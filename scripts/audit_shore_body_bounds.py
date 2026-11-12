"""Sweep representative legal body-size bounds at the exact shore margin."""
from collections import defaultdict
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
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
from teleport import can_place


def run(width, height, side, fps):
    x = 20 + width / 2 + .2 if side == -1 else 60 - width / 2 - .2
    world = World(0, 'shore legal body bounds', 80, 60, gravity=-6.5, spawn_points=(x, 30))
    world.player_config = {'w': width, 'h': height}
    world.begin_bulk_load()
    for gx in range(80):
        for gy in range(30):
            world.set_tile(gx, gy, 7 if 20 <= gx < 60 else 2)
    world.end_bulk_load()
    session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    player.collide_with_world(app._current_map, 0)
    initial = player.get_center()
    if (any(abs(a - b) > 1e-12 for a, b in zip(initial, (x, 30)))
            or not can_place(player, app._current_map, *initial)):
        raise AssertionError('body-boundary fixture was illegal or repositioned')
    errors = []
    step = session._advance_step

    def observe(dt, keys):
        step(dt, keys)
        issues = errors_for(session)
        if issues and not errors:
            errors.append({'time': app._game_timer, 'errors': issues})

    completed = False
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool, {pygame.K_w: True})), \
            patch.object(session, '_advance_step', side_effect=observe), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(2 * fps):
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if frame == 0 else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if (player.on_ground and not getattr(player, '_shore_exit_pending', False)
                    and abs(player._y - height / 2 - 30) < .02):
                completed = True
                break
            if errors:
                break
        respawns = reset.call_count
    return dict(width=width, height=height, side=side, fps=fps, initial=initial,
                completed=completed, final=player.get_center(), elapsed=app._game_timer,
                stamina=player.stamina, errors=errors, respawns=respawns,
                chosen=getattr(player, '_shore_exit_dir', None))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': '294 legal fixture combinations sampled through allowed 0.1..10 dimensions, exact 0.2 shore margin; not every real size/map/buff',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    ('scripts/audit_shore_body_bounds.py', 'shore_detection.py',
                     'shore_exit.py', 'pixel_roamer/world_session.py', 'creature.py')},
        'runs': [run(w, h, side, fps) for w in (.1, .6, .8, 1.8, 2.6, 5, 10)
                 for h in (.1, .6, .8, 1.8, 2.6, 5, 10)
                 for side in (-1, 1) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cases': len(report['runs']), 'completed': sum(r['completed'] for r in report['runs']),
                      'clear': sum(not r['errors'] for r in report['runs']),
                      'respawns': sum(r['respawns'] for r in report['runs'])}))
