"""Explicit local tower-base fixture; never claims a normal forest-to-tower route."""
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
from maps import get_map
from maps.layout import apply_layout
from scripts.audit_endless_climb import run
from scripts.control_session import create_control_session


def measure(fps, route, layout=None):
    world = get_map(3).create_session()
    authored_spawn = world.spawn_points
    if layout is not None:
        fill_color = world.fill_color
        apply_layout(world, layout)
        world.fill_color = fill_color
    world.spawn_points = (433.5, 11.9)
    session = create_control_session(3, world=world)
    player = session.app.player1
    configuration = {key: getattr(player, key) for key in ('v_jump', 'v_max', 'f_y', 'stamina_max')}
    configuration['gravity'] = world.gravity
    with patch('scripts.audit_endless_climb.create_control_session', return_value=session):
        result = run(fps, route, duration=240, draw_every=5)
    result.update(local_fixture_spawn=world.spawn_points, original_forest_spawn=authored_spawn,
                  production_configuration=configuration, checkpoint_recorded=player.spawn_pos[1] > 200)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--route', type=Path, default=ROOT / 'scripts/routes/pixel_tower_local.json')
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    args = parser.parse_args()
    route = json.loads(args.route.read_text())
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'shared_controller_sha256': hashlib.sha256((ROOT / 'scripts/audit_endless_climb.py').read_bytes()).hexdigest(),
              'route_sha256': hashlib.sha256(args.route.read_bytes()).hexdigest(),
              'candidate_layout': json.loads(args.layout.read_text()) if args.layout else None,
              'scope': route['scope'], 'route': route,
              'runs': [measure(fps, route, args.layout) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'completed_route', 'failure', 'timer', 'position', 'min_hp', 'min_stamina')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
