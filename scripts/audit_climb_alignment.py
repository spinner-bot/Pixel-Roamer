"""Measure event-time and fixed-step ladder capture motion separately."""
from collections import defaultdict
from contextlib import nullcontext
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from world import World
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, side, mode, width, height, offset, player_class=None):
    dx, dy = offset
    target = 5.5 + dx
    start_x = target + side * (width / 2 + .49)
    world = World(0, 'climb alignment', 20, 20, gravity=0, loop_x=True, loop_y=True,
                  spawn_points=(start_x, 10 + dy))
    world.player_config = {'w': width, 'h': height}
    for y in range(1, 19):
        world.set_tile(5, y, 9)
    override = patch('player_factory.Player', player_class) if player_class else nullcontext()
    with override:
        session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    player.collide_with_world(app._current_map, 0)
    keys = defaultdict(bool, {pygame.K_w: True})
    max_event_dx, max_step_dx, max_frame_dx = 0, 0, 0
    failures = []
    original_step = session._advance_step

    def observe_step(dt, held):
        nonlocal max_step_dx
        before_x = player._x
        original_step(dt, held)
        max_step_dx = max(max_step_dx, abs(player._x - before_x))
        failures.extend(errors_for(session))

    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(session, '_advance_step', side_effect=observe_step):
        for frame in range(fps):
            frame_x = player._x
            events = ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)]
                      if frame == 0 and mode == 'keydown' else [])
            with patch('pygame.event.get', return_value=events):
                before_x = player._x
                app._handle_events()
                max_event_dx = max(max_event_dx, abs(player._x - before_x))
            session.advance(1 / fps)
            max_frame_dx = max(max_frame_dx, abs(player._x - frame_x))
    return {'fps': fps, 'side': side, 'mode': mode, 'body': [width, height], 'offset': offset,
            'start_x': start_x, 'target_x': target, 'position': player.get_center(),
            'max_event_dx': max_event_dx, 'max_fixed_step_dx': max_step_dx,
            'max_frame_dx': max_frame_dx, 'stamina': player.stamina, 'hp': player.hp,
            'is_climbing': player.is_climbing, 'errors': failures,
            'aligned_final': abs(player._x - target) <= 1e-8,
            'continuous_capture': max_event_dx <= 1e-8 and max_step_dx <= 6 / 120 + 1e-8}


def cases(player_class=None):
    return [run(fps, side, mode, width, height, offset, player_class)
            for fps in (30, 60, 144) for side in (-1, 1) for mode in ('keydown', 'held')
            for width, height in ((.8, 1.8), (2, 1.8), (.8, 2.8), (2, 2.8))
            for offset in ((0, 0), (-20, -20), (20, 20))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--current-only', action='store_true')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'legacy_revision': '2b2a739',
              'scope': 'synthetic legal ladder contacts with actual events/session; four valid bodies, mirror, loop translations and three FPS; no physical device claim'}
    if not args.current_only:
        old = ModuleType('legacy_climb_alignment_creature')
        old.__file__ = str(ROOT / 'creature.py')
        source = subprocess.check_output(['git', 'show', '2b2a739:creature.py'], cwd=ROOT, text=True)
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        report['before'] = cases(old.Player)
    report['after'] = cases()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: {'cases': len(report[name]),
                            'continuous': sum(r['continuous_capture'] for r in report[name]),
                            'aligned': sum(r['aligned_final'] for r in report[name]),
                            'max_jump': max(max(r['max_event_dx'], r['max_fixed_step_dx']) for r in report[name])}
                      for name in ('before', 'after') if name in report}))


if __name__ == '__main__':
    main()
