"""Fixed-tick invariant audit of existing status/environment combinations."""
from collections import defaultdict, deque
import argparse
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from block_types_data import BLOCK_TYPES
from buff_system import BUFF_TYPES
from scripts.control_session import create_control_session, terminal_snapshot
from scripts.audit_session_soak import errors_for
from world import World

SURFACES = (2, 3, 4, 6, 7, 9, 10, 32, 33, 330, 338, 339, 340, 346,
            348, 349, 353, 370, 373, 375, 379, 397, 427, 438)


class CaseFailure(Exception):
    pass


def run(block_id, buff_id, seconds):
    seed = block_id * 1000 + buff_id
    random.seed(seed)
    solid = BLOCK_TYPES[block_id].is_solid
    world = World(0, 'status/environment matrix', 24, 64, gravity=-6.5,
                  spawn_points=(12.5, 2.9 if solid else 1.9))
    world.begin_bulk_load()
    for x in range(24):
        world.set_tile(x, 0, 2)
    for x in range(8, 17):
        world.set_tile(x, 1, block_id)
    world.end_bulk_load()
    session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    player.apply_buff(buff_id, (), min(5., seconds * .75))
    keys = defaultdict(bool)
    history, failures = deque(maxlen=8), []
    elapsed, ticks, frames, next_jump, next_sample = 0., 0, 0, .75, 0.
    min_hp, min_stamina = player.hp, player.stamina
    observed = set()
    original = session._advance_step

    def observe(dt, held):
        nonlocal ticks, min_hp, min_stamina, next_sample
        original(dt, held)
        ticks += 1
        min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
        observed.update(buff.buff_id for buff in player.buffs)
        issues = errors_for(session)
        if app._game_timer >= next_sample - 1e-8 or issues:
            history.append({'tick': ticks, 'state': terminal_snapshot(session)})
            next_sample += .25
        if issues:
            failures.append({'tick': ticks, 'errors': issues, 'history': list(history)})
            raise CaseFailure

    session._advance_step = observe
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        while elapsed < seconds - 1e-8:
            fps = (30, 60, 144)[min(2, int((elapsed + 1e-8) * 3 / seconds))]
            dt = min(1 / fps, seconds - elapsed)
            target = 12.5 + (3 if int(elapsed // 1.5) % 2 == 0 else -3)
            error = max(-6, min(6, (target - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .3, error < -.3
            keys[pygame.K_w] = .5 <= elapsed < 4
            keys[pygame.K_s] = elapsed >= 4
            events = []
            if elapsed >= next_jump - 1e-8:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                next_jump += 3
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            frames += 1
            try:
                session.advance(dt)
            except CaseFailure:
                break
            elapsed += dt
        respawns = reset.call_count
    return {'block_id': block_id, 'buff_id': buff_id, 'seed': seed, 'ticks': ticks,
            'input_seconds': elapsed, 'control_frames': frames, 'respawns': respawns,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'observed_buffs': sorted(observed),
            'errors': failures, 'final_state': terminal_snapshot(session)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blocks', type=int, nargs='+', default=SURFACES)
    parser.add_argument('--buffs', type=int, nargs='+')
    parser.add_argument('--seconds', type=float, default=8)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    buffs = args.buffs or sorted(BUFF_TYPES)
    if (not math.isfinite(args.seconds) or args.seconds <= 0
            or set(args.blocks) - set(BLOCK_TYPES) or set(buffs) - set(BUFF_TYPES)):
        parser.error('unknown block/buff or invalid duration')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'isolated existing buff/surface fixtures; production session controls and fixed-tick invariants; not every semantic effect, frame partition or map path',
              'python': platform.python_version(), 'pygame': pygame.version.ver,
              'requested_seconds': args.seconds, 'expected_cases': len(args.blocks) * len(buffs),
              'complete': False, 'cases': []}
    started = time.perf_counter()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for block_id in args.blocks:
        for buff_id in buffs:
            report['cases'].append(run(block_id, buff_id, args.seconds))
        report['wall_seconds'] = time.perf_counter() - started
        report['complete'] = len(report['cases']) == report['expected_cases']
        temporary = args.output.with_suffix('.tmp.json')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(args.output)
        print(json.dumps({'block_id': block_id, 'cases': len(report['cases']),
                          'failed': sum(bool(c['errors']) for c in report['cases'])}), flush=True)
    if any(case['errors'] for case in report['cases']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
