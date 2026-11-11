"""Lower ice palace controls, real checkpoint contact and narrow-ceiling respawn."""
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
from scripts.audit_feature_clearance import contact_pose
from teleport import can_place


def topology(world, player):
    free = {(x, y) for x in range(265, 316) for y in range(32, 81)
            if can_place(player, world, x + .5, y + .9)}
    seen, queue = {(275, 76)}, deque([(275, 76)])
    while queue:
        x, y = queue.popleft()
        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if point in free and point not in seen:
                seen.add(point)
                queue.append(point)
    return {'scope': 'bounded static body candidates, not gravity/control proof',
            'bounds': [265, 315, 32, 80], 'lower_connected': (291, 40) in seen,
            'upper_connected': (289, 63) in seen,
            'checkpoint_contact_candidate': contact_pose(world, player, (290, 40))}


def measure(fps, route, layout=None, normal_spawn=False):
    world = get_map(3).create_session()
    authored_spawn = world.spawn_points
    if layout:
        fill_color = world.fill_color
        apply_layout(world, layout)
        world.fill_color = fill_color
    if not normal_spawn:
        world.spawn_points = (269.5, 39.9)
    session = create_control_session(3, world=world)
    player = session.app.player1
    initial_position = player.get_center()
    connectivity = topology(session.app._current_map, player)
    jumps = []
    original_jump = player.jump

    def observe_jump(*args, **kwargs):
        sample = {'time': session.app._game_timer, 'position': player.get_center(),
                  'stamina_before_cost': player.stamina, 'jump_velocity': player.v_jump}
        succeeded = original_jump(*args, **kwargs)
        if succeeded:
            jumps.append(sample)
        return succeeded

    with patch.object(player, 'jump', side_effect=observe_jump):
        if normal_spawn:
            approach = json.loads((ROOT / 'scripts/routes/pixel_sky_to_ice_lower.json').read_text())
            result = normal_measure(fps, routes=[approach, route], session=session)
            room = result['segments'][-1]
            complete = result['completed']
        else:
            result = room = route_run(fps, route, duration=240, draw_every=5, session=session)
            complete = result['completed_route']
    recorded = (302 in room['contacts_seen'] and abs(player.spawn_pos[1] - 40.9) < 1e-7
                and abs(player.spawn_pos[0] - 289.6) < .02)
    checkpoint_clear = can_place(player, session.app._current_map, *player.spawn_pos)
    arrivals = {a['name']: a for a in room['arrivals']}
    clearance_jumps = []
    if 'return_gap' in arrivals and 'pillar_clearance' in arrivals:
        low, high = arrivals['return_gap']['time'], arrivals['pillar_clearance']['time']
        clearance_jumps = [jump for jump in jumps if low < jump['time'] <= high + 1e-7]
    result.update(success=complete and recorded and checkpoint_clear,
                  normal_spawn=normal_spawn, initial_position=initial_position,
                  original_forest_spawn=authored_spawn, topology=connectivity,
                  checkpoint_recorded=recorded, checkpoint_clear=checkpoint_clear,
                  jumps=jumps, clearance_jump_count=len(clearance_jumps))
    if result['success']:
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
    parser.add_argument('--route', type=Path, default=ROOT / 'scripts/routes/pixel_ice_lower.json')
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    args = parser.parse_args()
    route = json.loads(args.route.read_text())
    sources = ('scripts/audit_ice_lower.py', 'scripts/audit_endless_climb.py',
               'scripts/audit_pixel_normal_tower.py', 'scripts/audit_pixel_sky.py',
               'scripts/audit_feature_clearance.py', 'scripts/routes/pixel_sky_to_ice_lower.json')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
              'route_sha256': hashlib.sha256(args.route.read_bytes()).hexdigest(), 'route': route,
              'scope': 'original forest same-session controls' if args.normal_spawn else 'explicit legal outside-door fixture',
              'candidate_layout': json.loads(args.layout.read_text()) if args.layout else None,
              'runs': [measure(fps, route, args.layout, args.normal_spawn) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{key: run[key] for key in ('fps', 'success', 'timer', 'position', 'min_hp', 'min_stamina', 'respawns', 'checkpoint_recorded', 'clearance_jump_count')}
                      for run in report['runs']]))


if __name__ == '__main__':
    main()
