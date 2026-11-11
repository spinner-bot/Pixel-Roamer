"""Normal authored-map clay landings, ice/stone transition and climbing return."""
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
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, rounds=1):
    route = json.loads((ROOT / 'scripts/routes/test_world_surfaces.json').read_text())
    waypoints = route['approach'] + route['circuit'] * rounds + route['finish']
    session = create_control_session(route['map_id'])
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    trace, arrivals, clay_entries = [], [], []
    stage, stage_start = 0, 0
    reached, failure, was_on_clay = False, None, False
    min_hp, min_stamina, max_dx = player.hp, player.stamina, 0
    max_dx_event, max_clay_dx = None, 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range((60 + rounds * 30) * fps):
            waypoint = waypoints[stage]
            arrived = abs(player._x - waypoint['x']) < .18
            if waypoint['kind'] == 'climb':
                arrived &= player.is_climbing and player._y >= waypoint['y']
            else:
                arrived &= player.on_ground and abs(player._y - waypoint['y']) < .02
                if waypoint['kind'] == 'rest':
                    arrived &= player.stamina >= 195
            jump = False
            if arrived:
                arrivals.append({'name': waypoint['name'], 'time': app._game_timer,
                                 'position': player.get_center(), 'stamina': player.stamina,
                                 'standing_block': player.stand_pool})
                stage += 1
                stage_start = frame
                if stage == len(waypoints):
                    reached = True
                    break
                waypoint = waypoints[stage]
                jump = waypoint['jump']
            keys[pygame.K_w] = waypoint['kind'] == 'climb' and player._y <= waypoint['y'] + .1
            keys[pygame.K_s] = waypoint['kind'] != 'climb' and not jump
            error = max(-5, min(5, (waypoint['x'] - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            if not jump and player.on_ground and player._y < waypoint['y'] - .1:
                jump = True
            before, vx_before = player.get_center(), player.v_x
            was_climbing, previous_stand = player.is_climbing, player.stand_pool
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            dx = player._x - before[0]
            if abs(dx) > max_dx:
                max_dx = abs(dx)
                max_dx_event = {'time': app._game_timer, 'phase': waypoint['name'],
                                'from': before, 'to': player.get_center(), 'dx': dx,
                                'was_climbing': was_climbing, 'is_climbing': player.is_climbing,
                                'standing_before': previous_stand, 'standing_after': player.stand_pool}
            if previous_stand == 4 or player.stand_pool == 4:
                max_clay_dx = max(max_clay_dx, abs(dx))
            on_clay = player.on_ground and player.stand_pool == 4
            if on_clay and not was_on_clay:
                clay_entries.append({'time': app._game_timer, 'phase': waypoint['name'],
                                     'from': before, 'to': player.get_center(),
                                     'vx_before': vx_before, 'vx_after': player.v_x,
                                     'dx': player._x - before[0], 'speed_bound': player.v_max / fps})
            was_on_clay = on_clay
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': waypoint['name'],
                              'position': player.get_center(), 'hp': player.hp,
                              'stamina': player.stamina, 'climbing': player.is_climbing})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if frame - stage_start > 20 * fps:
                failure = f"{waypoint['name']} timed out"
                break
        respawns = reset.call_count
    return {'fps': fps, 'rounds': rounds, 'returned_after_surface_route': reached, 'failure': failure,
            'timer': app._game_timer, 'control_frames': frame if reached else frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'max_frame_dx': max_dx, 'respawns': respawns,
            'max_frame_dx_event': max_dx_event, 'max_clay_frame_dx': max_clay_dx,
            'production_options': {'gravity': app._current_map.gravity, 'v_max': player._base_v_max,
                                   'v_jump': player.v_jump, 'stamina_max': player.stamina_max,
                                   'f_y': player.f_y},
            'arrivals': arrivals, 'clay_entries': clay_entries, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rounds', type=int, default=1)
    args = parser.parse_args()
    if not 1 <= args.rounds <= 100:
        parser.error('--rounds must be between 1 and 100')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'route_sha256': hashlib.sha256((ROOT / 'scripts/routes/test_world_surfaces.json').read_bytes()).hexdigest(),
              'scope': 'normal map1 spawn, original clay drop and jump landing, ice/stone transitions, vine and return; not all areas or device acceptance',
              'runs': [run(fps, args.rounds) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'returned_after_surface_route', 'failure', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
