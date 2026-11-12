"""Measure actual narrow-pool shore choice, completion and mirrored clearance."""
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
import pixel_roamer.world_session as session_module
from world import World
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for
from teleport import can_place


def run(fps, body, gap, intent, valid_banks, offset, reversed_input=False):
    width, height = body
    dx, dy = offset
    expected_start = (5 + gap / 2 + dx, 20 + dy)
    world = World(0, 'narrow shore choice', 20, 40, gravity=-6.5,
                  spawn_points=expected_start, loop_x=True, loop_y=True)
    world.player_config = {'w': width, 'h': height}
    for x in range(4, 6 + gap):
        for y in range(20):
            world.set_tile(x, y, 7 if 5 <= x < 5 + gap else 2)
    if -1 not in valid_banks:
        world.set_tile(4, 21, 2)
    if 1 not in valid_banks:
        world.set_tile(5 + gap, 21, 2)
    session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    if reversed_input:
        player.apply_buff(23, (), 5)
    player.collide_with_world(app._current_map, 0)
    initial = player.get_center()
    if (any(abs(a - b) > 1e-12 for a, b in zip(initial, expected_start))
            or not can_place(player, app._current_map, *initial)):
        raise AssertionError('shore fixture was invalid or relocated')
    detected = list(getattr(player, '_shore_directions', (player._shore_dir,)))
    fallback = 1 if 1 in valid_banks else -1
    effective_intent = -intent if reversed_input else intent
    expected_direction = effective_intent if effective_intent in valid_banks else fallback
    keys = defaultdict(bool, {pygame.K_w: True})
    choices, failures = [], []
    step = session._advance_step
    begin = session_module.begin_shore_exit

    def observe_begin(*args, **kwargs):
        succeeded = begin(*args, **kwargs)
        if succeeded:
            choices.append({'time': app._game_timer, 'direction': player._shore_exit_dir,
                            'position': player.get_center(), 'stamina': player.stamina})
        return succeeded

    def observe_step(dt, held):
        step(dt, held)
        issues = errors_for(session)
        if issues and not failures:
            failures.append({'time': app._game_timer, 'errors': issues})

    completed = False
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(session_module, 'begin_shore_exit', side_effect=observe_begin), \
            patch.object(session, '_advance_step', side_effect=observe_step), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(2 * fps):
            # A 144Hz render frame can contain no physics step. Retain the
            # directional hold until the queued Space is actually consumed.
            keys[pygame.K_a], keys[pygame.K_d] = not choices and intent < 0, not choices and intent > 0
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if frame == 0 else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if (player.on_ground and not getattr(player, '_shore_exit_pending', False)
                    and abs(player._y - (20 + dy + height / 2)) < .02):
                completed = True
                break
            if failures:
                break
        respawns = reset.call_count
    chosen = choices[0]['direction'] if choices else None
    return dict(fps=fps, body=body, gap=gap, intent=intent, valid_banks=valid_banks,
                offset=offset, initial=initial, detected=detected, expected_direction=expected_direction,
                reversed_input=reversed_input, effective_intent=effective_intent,
                choices=choices, chosen=chosen, matched=chosen == expected_direction,
                completed=completed, elapsed=app._game_timer, final=player.get_center(),
                final_stamina=player.stamina, errors=failures, respawns=respawns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = ['scripts/audit_shore_direction.py', 'creature.py',
               'pixel_roamer/world_session.py', 'shore_exit.py']
    if (ROOT / 'shore_detection.py').exists():
        sources.append('shore_detection.py')
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': '243 legal narrow-water fixtures with normal input and actual exit landing; not original map routes or device acceptance',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
        'runs': [run(fps, body, gap, intent, banks, offset)
                 for fps in (30, 60, 144)
                 for body, gap in (((.6, 1.5), 1), ((.8, 1.8), 1), ((1.8, 2.6), 2))
                 for intent in (-1, 0, 1) for banks in ((1, -1), (-1,), (1,))
                 for offset in ((-20, -40), (0, 0), (20, 40))],
        'reversed_runs': [run(fps, body, gap, intent, (1, -1), (0, 0), True)
                          for fps in (30, 60, 144)
                          for body, gap in (((.6, 1.5), 1), ((.8, 1.8), 1), ((1.8, 2.6), 2))
                          for intent in (-1, 1)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: {'cases': len(report[name]), 'matched': sum(r['matched'] for r in report[name]),
                      'completed': sum(r['completed'] for r in report[name]),
                      'clear': sum(not r['errors'] for r in report[name])}
                      for name in ('runs', 'reversed_runs')}))
