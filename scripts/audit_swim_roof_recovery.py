"""Cycle existing swimming/release recovery under the low-roof geometry."""
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


def run(height, seconds=120):
    world = World(0, 'swim roof recovery', 20, 20, gravity=-6.5,
                  spawn_points=(5.5, min(9.97, 11 - height / 2 - .001)))
    world.player_config = {'h': height}
    for x in range(20):
        world.set_tile(x, 0, 2)
        world.set_tile(x, 11, 2)
        for y in range(1, 10):
            world.set_tile(x, y, 7)
    session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    elapsed, frames, next_sample = 0., 0, 0.
    trace, transitions, errors = [], [], []
    observed = {'steps': 0, 'ceiling_steps': 0, 'floor_steps': 0,
                'exhausted_up_steps': 0, 'min_stamina': player.stamina,
                'min_hp': player.hp, 'max_release_recovery': 0., 'max_step_dy': 0.}
    step = session._advance_step

    def observe(dt, keys):
        before_y = player._y
        step(dt, keys)
        observed['steps'] += 1
        observed['ceiling_steps'] += bool(player.on_ceiling)
        observed['floor_steps'] += bool(player.on_ground)
        observed['exhausted_up_steps'] += bool(keys[pygame.K_w] and player.stamina < .2)
        observed['min_stamina'] = min(observed['min_stamina'], player.stamina)
        observed['min_hp'] = min(observed['min_hp'], player.hp)
        observed['max_step_dy'] = max(observed['max_step_dy'], abs(player._y - before_y))
        issues = errors_for(session)
        if issues and not errors:
            errors.append({'time': app._game_timer, 'errors': issues,
                           'position': player.get_center()})

    previous_up = None
    release_start = None
    keys = defaultdict(bool)
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        while elapsed < seconds - 1e-8 and not errors:
            fps = (30, 60, 144)[int(elapsed // 10) % 3]
            dt = min(1 / fps, seconds - elapsed)
            up = elapsed % 28 < 12  # 12 seconds up, then 16 seconds released.
            if up != previous_up:
                transitions.append({'input_time': elapsed, 'up': up,
                    'position': player.get_center(), 'stamina': player.stamina})
                if not up:
                    release_start = player.stamina
                previous_up = up
            keys[pygame.K_w] = up
            session.advance(dt)
            if not up:
                observed['max_release_recovery'] = max(observed['max_release_recovery'],
                                                       player.stamina - release_start)
            elapsed += dt
            frames += 1
            if elapsed >= next_sample - 1e-8:
                trace.append({'input_time': elapsed, 'position': player.get_center(),
                    'stamina': player.stamina, 'up': up, 'on_ceiling': player.on_ceiling,
                    'on_ground': player.on_ground})
                next_sample += 10
        respawns = reset.call_count
    return dict(height=height, requested_seconds=seconds, input_seconds=elapsed,
                frames=frames, respawns=respawns, errors=errors,
                final_position=player.get_center(), final_stamina=player.stamina,
                transitions=transitions, trace=trace, **observed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'four explicit low-roof fixtures with a floor, actual held/release input; not map traversal or device acceptance',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    ('scripts/audit_swim_roof_recovery.py', 'pixel_roamer/world_session.py', 'creature.py')},
        'runs': [run(height) for height in (1.8, 2.02, 2.08, 2.12)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{key: r[key] for key in ('height', 'input_seconds', 'errors', 'respawns',
                      'exhausted_up_steps', 'max_release_recovery')} for r in report['runs']]))
    raise SystemExit(1 if any(r['errors'] or r['respawns'] for r in report['runs']) else 0)
