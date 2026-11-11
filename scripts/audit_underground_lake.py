"""Lake entry/air chamber/checkpoint/return with explicit local or forest scope."""
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
    free = {(x, y) for x in range(250, 323) for y in range(9, 43)
            if can_place(player, world, x + .5, y + .9)}
    seen, queue = {(261, 38)}, deque([(261, 38)])
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point in free and point not in seen:
                seen.add(point)
                queue.append(point)
    return {'scope': 'bounded static full-body candidates, not gravity/input proof',
            'bounds': [250, 322, 9, 42], 'free_count': len(free),
            'connected_count': len(seen), 'targets': {
                name: {'legal': point in free, 'connected': point in seen}
                for name, point in [('lake', (264, 22)), ('air_chamber', (284, 15)),
                                    ('checkpoint_roof', (287, 20))]}}


def measure(fps, route, layout=None, normal_spawn=False):
    world = get_map(3).create_session()
    original_spawn = world.spawn_points
    if layout:
        fill_color = world.fill_color
        apply_layout(world, layout)
        world.fill_color = fill_color
    if not normal_spawn:
        world.spawn_points = (261.5, 38.9)
    session = create_control_session(3, world=world)
    app, player = session.app, session.app.player1
    initial_position = player.get_center()
    connectivity = topology(app._current_map, player)
    observed = {'swimming_steps': 0, 'climbing_steps': 0, 'air_chamber_dry_steps': 0,
                'max_step_dx': 0, 'max_step_dy': 0}
    advance_step = session._advance_step

    def observe(dt, keys):
        before = player.get_center()
        advance_step(dt, keys)
        x, y = player.get_center()
        observed['swimming_steps'] += bool(player.can_swim)
        observed['climbing_steps'] += bool(player.is_climbing)
        observed['air_chamber_dry_steps'] += bool(
            281 < x < 294 and 15.8 < y < 18.2 and not player.can_swim and player.on_ground)
        observed['max_step_dx'] = max(observed['max_step_dx'], abs(x - before[0]))
        observed['max_step_dy'] = max(observed['max_step_dy'], abs(y - before[1]))

    with patch.object(session, '_advance_step', side_effect=observe):
        if normal_spawn:
            approach = json.loads((ROOT / 'scripts/routes/pixel_sky_to_ice_lower.json').read_text())
            approach['waypoints'] = approach['waypoints'][:2] + [{
                'name': 'west_lake_surface', 'x': 261.5, 'y': 38.9,
                'kind': 'rest', 'stamina_min': 95}]
            result = normal_measure(fps, routes=[approach, route], session=session)
            room = result['segments'][-1]
            completed = result['completed']
        else:
            result = room = route_run(fps, route, duration=300, draw_every=5, session=session)
            completed = result['completed_route']
    saved = player.spawn_pos
    recorded = (302 in room['contacts_seen'] and abs(saved[1] - 20.9) < .02
                and abs(saved[0] - 287.5) < 1)
    result.update(normal_spawn=normal_spawn, initial_position=initial_position,
                  original_forest_spawn=original_spawn, topology=connectivity,
                  observation=observed, lake_checkpoint_recorded=recorded,
                  success=completed and recorded and observed['air_chamber_dry_steps'] > 0)
    if result['success']:
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
                patch.object(player, 'reset', wraps=player.reset) as reset:
            player.take_raw_damage(1000)
            session.advance(1 / 120)
            result['after_deliberate_death'] = {
                'alive': player.alive, 'position': player.get_center(), 'respawns': reset.call_count,
                'clear': can_place(player, app._current_map, *player.get_center())}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--normal-spawn', action='store_true')
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    args = parser.parse_args()
    route_path = ROOT / 'scripts/routes/pixel_underground_lake.json'
    route = json.loads(route_path.read_text())
    sources = ['scripts/audit_underground_lake.py', 'scripts/audit_endless_climb.py',
               'scripts/audit_pixel_normal_tower.py', 'scripts/audit_pixel_sky.py',
               'scripts/routes/pixel_underground_lake.json',
               'scripts/routes/pixel_sky_to_ice_lower.json', 'maps/pixel_journey/map.py']
    if (ROOT / 'maps/pixel_journey/lake_connections.json').exists():
        sources.append('maps/pixel_journey/lake_connections.json')
    report = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': route['scope'], 'normal_spawn': args.normal_spawn,
        'candidate_layout': (json.loads(args.layout.read_text()) if args.layout else None),
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
        'runs': [measure(fps, route, args.layout, args.normal_spawn) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'success', 'timer', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
