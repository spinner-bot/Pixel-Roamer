"""Pyramid roof/room controls, with explicit local versus forest-spawn scope."""
from collections import defaultdict, deque
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
from maps import get_map
from maps.layout import apply_layout
from scripts.control_session import create_control_session
from scripts.audit_endless_climb import run as route_run
from scripts.audit_pixel_normal_tower import measure as normal_measure
from teleport import can_place


def topology(world, player):
    free = {(x, y) for x in range(325, 426) for y in range(20, 87)
            if can_place(player, world, x + .5, y + .9)}
    seen, queue = {(380, 80)}, deque([(380, 80)])
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point in free and point not in seen:
                seen.add(point)
                queue.append(point)
    return {'scope': 'bounded full-body static candidates; not gravity or input proof',
            'bounds': [325, 425, 20, 86], 'free_count': len(free), 'component_count': len(seen),
            'rooms': {name: {'legal': (x, y) in free, 'connected': (x, y) in seen}
                      for name, x, y in (('checkpoint', 375, 48), ('second_room', 376, 55), ('treasure', 376, 62))}}


def cross_prefix():
    route = json.loads((ROOT / 'scripts/routes/pixel_sky_to_tower_base.json').read_text())
    index = next(i for i, point in enumerate(route['waypoints']) if point['name'] == 'after_t3')
    route['waypoints'] = route['waypoints'][:index + 1]
    route['scope'] = 'original forest and sky/ice/pyramid controls through original T3 bypass'
    return route


def measure(fps, route, layout=None, normal_spawn=False):
    world = get_map(3).create_session()
    authored_spawn = world.spawn_points
    if layout:
        fill_color = world.fill_color
        apply_layout(world, layout)
        world.fill_color = fill_color
    if not normal_spawn:
        world.spawn_points = (380.5, 80.9)
    session = create_control_session(3, world=world)
    player = session.app.player1
    connectivity = topology(session.app._current_map, player)
    result = (normal_measure(fps, routes=[cross_prefix(), route], session=session) if normal_spawn
              else route_run(fps, route, duration=240, draw_every=5, session=session))
    result.update(topology=connectivity, original_forest_spawn=authored_spawn,
                  normal_spawn=normal_spawn, checkpoint_valid=can_place(player, session.app._current_map, *player.spawn_pos))
    complete = result['completed'] if normal_spawn else result['completed_route']
    if complete:
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
                patch.object(player, 'reset', wraps=player.reset) as reset:
            player.take_raw_damage(1000)
            session.advance(1 / 120)
            result['after_deliberate_death'] = {
                'alive': player.alive, 'position': player.get_center(), 'respawns': reset.call_count,
                'clear': can_place(player, session.app._current_map, *player.get_center())}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--normal-spawn', action='store_true')
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    args = parser.parse_args()
    route_path = ROOT / 'scripts/routes/pixel_pyramid_rooms.json'
    route = json.loads(route_path.read_text())
    sources = ('scripts/audit_pyramid_rooms.py', 'scripts/audit_pixel_normal_tower.py',
               'scripts/audit_pixel_sky.py', 'scripts/audit_endless_climb.py',
               'scripts/routes/pixel_pyramid_rooms.json', 'scripts/routes/pixel_sky_to_tower_base.json')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
              'scope': 'original forest continuous session' if args.normal_spawn else 'explicit local pyramid roof fixture',
              'candidate_layout': json.loads(args.layout.read_text()) if args.layout else None,
              'route': route, 'cross_prefix': cross_prefix() if args.normal_spawn else None,
              'runs': [measure(fps, route, args.layout, args.normal_spawn) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{key: run[key] for key in ('fps', 'timer', 'position', 'min_hp', 'min_stamina', 'respawns')}
                      | {'complete': run.get('completed', run.get('completed_route')), 'failure': run.get('failure')}
                      for run in report['runs']]))


if __name__ == '__main__':
    main()
