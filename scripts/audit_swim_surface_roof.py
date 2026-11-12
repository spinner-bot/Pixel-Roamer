"""Full-body placement at water-surface caps under a low ceiling."""
from collections import defaultdict
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
from teleport import can_place


def run(fps, height, roof, mode, offset, session_class=None):
    dx, dy = offset
    y = min(9.97, 11 - height / 2 - .001) if roof else 9.97
    expected = (5.5 + dx, y + dy)
    world = World(0, 'swim surface ceiling', 20, 20, gravity=-6.5,
                  spawn_points=expected, loop_x=True, loop_y=True)
    world.player_config = {'h': height}
    for x in range(1, 19):
        for gy in range(1, 10):
            world.set_tile(x, gy, 7)
        if roof:
            world.set_tile(x, 11, 2)
    session = create_control_session(0, world=world)
    if session_class is not None:
        session = session_class(session.app)
    app, player = session.app, session.app.player1
    player.collide_with_world(app._current_map, 0)
    initial = player.get_center()
    if (any(abs(actual - requested) > 1e-12 for actual, requested in zip(initial, expected))
            or not can_place(player, app._current_map, *initial)):
        raise AssertionError(f'illegal/repositioned swimming fixture: {initial} != {expected}')
    observations = {'steps': 0, 'errors_total': 0, 'first_errors': [],
                    'max_step_dx': 0, 'max_step_dy': 0, 'max_event_dy': 0}
    step = session._advance_step

    def observe(dt, keys):
        before = player.get_center()
        step(dt, keys)
        observations['steps'] += 1
        observations['max_step_dx'] = max(observations['max_step_dx'], abs(player._x - before[0]))
        observations['max_step_dy'] = max(observations['max_step_dy'], abs(player._y - before[1]))
        errors = errors_for(session)
        observations['errors_total'] += len(errors)
        if errors and not observations['first_errors']:
            observations['first_errors'] = errors

    key = pygame.K_w if mode == 'held_w' else pygame.K_UP
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool, {key: True})), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(fps):
            events = ([pygame.event.Event(pygame.KEYDOWN, key=key)]
                      if frame == 0 and mode == 'keydown_arrow' else [])
            before_y = player._y
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            observations['max_event_dy'] = max(observations['max_event_dy'], abs(player._y - before_y))
            session.advance(1 / fps)
        observations['respawns'] = reset.call_count
    return dict(fps=fps, height=height, roof=roof, mode=mode, offset=offset,
                initial=initial, final=player.get_center(), surface=player._swim_top_y,
                can_swim=player.can_swim, stamina=player.stamina,
                on_ceiling=player.on_ceiling,
                final_clear=can_place(player, app._current_map, *player.get_center()), **observations)


def cases(session_class=None):
    return [run(fps, height, roof, mode, offset, session_class)
            for fps in (30, 60, 144) for height in (1.8, 2., 2.02, 2.04, 2.08, 2.1, 2.12)
            for roof in (False, True) for mode in ('held_w', 'keydown_arrow')
            for offset in ((-20, -20), (0, 0), (20, 20))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy-ref')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': '252 legal low-roof/open-water fixtures, actual held/keydown session; not all shore exits or device acceptance',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    ('scripts/audit_swim_surface_roof.py', 'pixel_roamer/world_session.py', 'creature.py')},
        'current': cases()}
    if args.legacy_ref:
        old = ModuleType('legacy_swim_surface_session')
        old.__file__ = str(ROOT / 'pixel_roamer/world_session.py')
        source = subprocess.check_output(['git', 'show', args.legacy_ref + ':pixel_roamer/world_session.py'],
                                         cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        report.update(legacy_revision=args.legacy_ref, legacy=cases(old.WorldSession))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: {'cases': len(report[name]),
        'clear_all_steps': sum(r['errors_total'] == 0 for r in report[name]),
        'max_step_dy': max(r['max_step_dy'] for r in report[name])}
        for name in ('current', 'legacy') if name in report}))


if __name__ == '__main__':
    main()
