"""Original forest spawn to tower-top checkpoint in one continuous real session."""
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
from scripts.control_session import create_control_session
from scripts.audit_pixel_sky import run as sky_run
from scripts.audit_endless_climb import run as route_run

ROUTES = ('pixel_sky_to_tower_base.json', 'pixel_tower_local.json')


def measure(fps, routes=None, session=None):
    if session is None:
        session = create_control_session(3)
    player = session.app.player1
    spawn = player.get_center()
    if routes is None:
        routes = [json.loads((ROOT / 'scripts/routes' / name).read_text()) for name in ROUTES]
    segments = []
    with patch.object(player, 'reset', wraps=player.reset) as reset:
        prefix = sky_run(fps, stop_at_upper_cloud=True, session=session)
        segments.append(prefix)
        completed = prefix['stopped_on_upper_cloud'] and prefix['failure'] is None
        if completed:
            for route in routes:
                segment = route_run(fps, route, duration=240, draw_every=5, session=session)
                segments.append(segment)
                if not segment['completed_route']:
                    completed = False
                    break
        respawns = reset.call_count
    return {'fps': fps, 'completed': completed, 'original_spawn': spawn,
            'position': player.get_center(), 'saved_checkpoint': player.spawn_pos,
            'timer': session.app._game_timer, 'respawns': respawns,
            'min_hp': min(s['min_hp'] for s in segments),
            'min_stamina': min(s['min_stamina'] for s in segments),
            'final_hp': player.hp, 'final_stamina': player.stamina,
            'segments': segments}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    args = parser.parse_args()
    sources = ['scripts/audit_pixel_normal_tower.py', 'scripts/audit_pixel_sky.py',
               'scripts/audit_endless_climb.py'] + ['scripts/routes/' + name for name in ROUTES]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
              'scope': 'original forest spawn; continuous same WorldSession through sky/ice/pyramid and tower, no local spawn or state transfer',
              'runs': [measure(fps) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'completed', 'timer', 'position', 'min_hp', 'min_stamina', 'respawns')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
