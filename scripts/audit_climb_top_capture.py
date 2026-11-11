"""Measure finite ladder-top capture across legal bodies, ledges and loop offsets."""
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


def run(fps, mode, body, ledge, offset, gap, session_class=None, horizontal_offset=0):
    dx, dy = offset
    expected = (5.5 + dx + horizontal_offset, 10 + dy + gap)
    world = World(0, 'finite climb top', 20, 20, gravity=-6.5,
                  spawn_points=expected, loop_x=True, loop_y=True)
    world.player_config = dict(zip(('w', 'h'), body))
    for y in range(1, 10):
        world.set_tile(5, y, 9)
    if ledge:
        world.set_tile(4 if ledge == 'left' else 6, 8, 2)
    session = create_control_session(0, world=world)
    if session_class is not None:
        session = session_class(session.app)
    app, player = session.app, session.app.player1
    player.collide_with_world(app._current_map, 0)
    initial = player.get_center()
    if initial != expected or not can_place(player, app._current_map, *initial):
        raise AssertionError(f'illegal/repositioned test fixture: {initial}, expected {expected}')
    observations = {'steps': 0, 'max_step_dx': 0, 'max_step_dy': 0,
                    'max_event_dy': 0, 'errors_total': 0, 'first_errors': []}
    original_step = session._advance_step

    def observe(dt, held):
        before = player.get_center()
        original_step(dt, held)
        observations['steps'] += 1
        observations['max_step_dx'] = max(observations['max_step_dx'], abs(player._x - before[0]))
        observations['max_step_dy'] = max(observations['max_step_dy'], abs(player._y - before[1]))
        errors = errors_for(session)
        observations['errors_total'] += len(errors)
        if errors and not observations['first_errors']:
            observations['first_errors'] = errors

    keys = defaultdict(bool, {pygame.K_w: True})
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(fps):
            events = ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)]
                      if frame == 0 and mode == 'keydown' else [])
            before_y = player._y
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            observations['max_event_dy'] = max(observations['max_event_dy'], abs(player._y - before_y))
            session.advance(1 / fps)
        observations['respawns'] = reset.call_count
    return dict(fps=fps, mode=mode, body=body, ledge=ledge, offset=offset, gap=gap,
                horizontal_offset=horizontal_offset,
                initial=initial, final=player.get_center(), climbing=player.is_climbing,
                on_ground=player.on_ground, stamina=player.stamina,
                final_clear=can_place(player, app._current_map, *player.get_center()),
                continuous=(observations['max_step_dy'] <= 6 / 120 + 1e-8
                            and observations['max_event_dy'] <= 1e-8), **observations)


def cases(session_class=None):
    return [run(fps, mode, body, ledge, offset, gap, session_class)
            for fps in (30, 60, 144) for mode in ('keydown', 'held')
            for body in ((.8, 1.8), (2., 2.4)) for ledge in (None, 'left', 'right')
            for offset in ((-20, -20), (0, 0), (20, 20)) for gap in (.25, .3)]


def pending_cases(session_class=None):
    return [run(fps, mode, (.8, 2.4), ledge, (0, 0), .25, session_class,
                horizontal_offset=-.5 if ledge == 'left' else .5)
            for fps in (30, 60, 144) for mode in ('keydown', 'held')
            for ledge in ('left', 'right')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy-ref')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': '216 legal initial fixtures plus 12 pending lateral alignments, actual event/held input and 120Hz session; not a normal map route or device acceptance',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    ('scripts/audit_climb_top_capture.py', 'pixel_roamer/world_session.py',
                     'creature.py', 'climb_alignment.py')}, 'current': cases(),
        'current_pending': pending_cases()}
    if args.legacy_ref:
        old = ModuleType('legacy_top_capture_session')
        old.__file__ = str(ROOT / 'pixel_roamer/world_session.py')
        source = subprocess.check_output(['git', 'show', args.legacy_ref + ':pixel_roamer/world_session.py'],
                                         cwd=ROOT, text=True)
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        # Both gameplay modules must match the legacy revision; otherwise new
        # capture admission would hide the old session's solid-overlap failures.
        old_actor = ModuleType('legacy_top_capture_creature')
        old_actor.__file__ = str(ROOT / 'creature.py')
        actor_source = subprocess.check_output(['git', 'show', args.legacy_ref + ':creature.py'],
                                               cwd=ROOT, text=True)
        exec(compile(actor_source, old_actor.__file__, 'exec'), old_actor.__dict__)
        with patch('player_factory.Player', old_actor.Player):
            report.update(legacy_revision=args.legacy_ref, legacy=cases(old.WorldSession),
                          legacy_pending=pending_cases(old.WorldSession))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: {'cases': len(report[name]),
        'continuous': sum(r['continuous'] for r in report[name]),
        'clear_all_steps': sum(r['errors_total'] == 0 for r in report[name]),
        'max_step_dy': max(r['max_step_dy'] for r in report[name])}
        for name in ('current', 'legacy', 'current_pending', 'legacy_pending') if name in report}))


if __name__ == '__main__':
    main()
