"""Continue the actual forest route after its explicit checkpoint respawn test."""
import argparse
import hashlib
import json
import math
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
from scripts import audit_ice_lower as ice_audit
from scripts import audit_session_soak as soak_audit
from scripts.control_session import create_control_session, terminal_snapshot


def measure(seconds, fps):
    sessions = []

    def observe_factory(*args, **kwargs):
        session = create_control_session(*args, **kwargs)
        sessions.append(session)
        return session

    route = json.loads((ROOT / 'scripts/routes/pixel_ice_lower.json').read_text())
    with patch.object(ice_audit, 'create_control_session', side_effect=observe_factory):
        route_result = ice_audit.measure(fps, route, normal_spawn=True)
    if not route_result['success'] or len(sessions) != 1:
        return {'route': route_result, 'error': 'continuous route did not provide one successful session'}
    session = sessions[0]
    start = terminal_snapshot(session)
    steps, roof_contacts, jump_count = 0, 0, 0
    max_dx, max_dy, large_movements = 0., 0., []
    original_step, original_jump = session._advance_step, session.app.player1.jump

    def observe_step(dt, held):
        nonlocal steps, roof_contacts, max_dx, max_dy
        player = session.app.player1
        before = {'position': player.get_center(), 'alive': player.alive,
                  'contacts': sorted(player.contact_pool)}
        original_step(dt, held)
        after = player.get_center()
        steps += 1
        dx, dy = abs(after[0] - before['position'][0]), abs(after[1] - before['position'][1])
        max_dx, max_dy = max(max_dx, dx), max(max_dy, dy)
        if 75 in player.contact_pool and abs(player._y + player._h / 2 - 42) < 1e-6:
            roof_contacts += 1
        if max(dx, dy) > 1:
            large_movements.append({'time': session.app._game_timer, 'before': before,
                                    'after': after, 'alive_after': player.alive,
                                    'contacts_after': sorted(player.contact_pool)})

    def observe_jump(*args, **kwargs):
        nonlocal jump_count
        accepted = original_jump(*args, **kwargs)
        jump_count += bool(accepted)
        return accepted

    session._advance_step = observe_step
    with patch.object(soak_audit, 'create_control_session', return_value=session) as factory, \
            patch.object(session.app.player1, 'jump', side_effect=observe_jump):
        soak = soak_audit.run(3, seconds)
        factory_calls = factory.call_count
    return {'route': route_result, 'start_after_deliberate_respawn': start,
            'soak': soak, 'final': terminal_snapshot(session), 'factory_calls': factory_calls,
            'physics_steps': steps, 'float_ice_roof_contact_steps': roof_contacts,
            'accepted_jumps': jump_count, 'max_step_dx': max_dx, 'max_step_dy': max_dy,
            'large_movements': large_movements}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--fps', type=int, choices=(30, 60, 144), default=60)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    pygame.init()
    sources = ('scripts/audit_ice_checkpoint_soak.py', 'scripts/audit_ice_lower.py',
               'scripts/audit_endless_climb.py', 'scripts/audit_pixel_normal_tower.py',
               'scripts/audit_pixel_sky.py', 'scripts/audit_session_soak.py',
               'scripts/routes/pixel_ice_lower.json', 'scripts/routes/pixel_sky_to_ice_lower.json')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
              'scope': 'same forest-route session after explicit deliberate checkpoint respawn; finite mixed-input stress may leave the initial room',
              'result': measure(args.seconds, args.fps)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    result = report['result']
    print(json.dumps({key: result.get(key) for key in ('error', 'physics_steps', 'float_ice_roof_contact_steps',
                                                     'accepted_jumps', 'max_step_dx', 'max_step_dy', 'large_movements')}))
    pygame.quit()
    if result.get('error') or result['soak']['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
