"""Normal platform/rope controls with route data and explicit air clearances."""
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


def run(fps, route=None, duration=120):
    if route is None:
        route = json.loads((ROOT / 'scripts/routes/endless_climb.json').read_text())
    session = create_control_session(route['map_id'])
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    trace, arrivals = [], []
    stage, stage_start = 0, 0
    reached, failure = False, None
    min_hp, min_stamina = player.hp, player.stamina
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(duration * fps):
            waypoint = route['waypoints'][stage]
            arrived = abs(player._x - waypoint['x']) < .18
            if waypoint['kind'] == 'air':
                arrived &= not player.on_ground and player._y >= waypoint['y']
            elif waypoint['kind'] == 'climb':
                arrived &= player.is_climbing and player._y >= waypoint['y']
            else:
                arrived &= player.on_ground and abs(player._y - waypoint['y']) < .02
                if waypoint['kind'] == 'rest':
                    arrived &= player.stamina >= 195
            jump = False
            if arrived:
                arrivals.append({'name': waypoint['name'], 'time': app._game_timer,
                                 'position': player.get_center(), 'stamina': player.stamina,
                                 'saved_spawn': player.spawn_pos})
                stage += 1
                stage_start = frame
                if stage == len(route['waypoints']):
                    reached = True
                    break
                waypoint = route['waypoints'][stage]
                jump = (player.on_ground or player.is_climbing) and waypoint['y'] > player._y + .2
            keys[pygame.K_w] = waypoint['kind'] == 'climb' and player._y <= waypoint['y'] + .1
            keys[pygame.K_s] = waypoint['kind'] != 'climb' and not jump and not app.jump_pressed
            error = max(-5, min(5, (waypoint['x'] - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            if not jump and player.on_ground and player._y < waypoint['y'] - .1:
                jump = True
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
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
    return {'fps': fps, 'completed_route': reached,
            'reached_and_rested': reached and route['waypoints'][-1]['kind'] == 'rest', 'failure': failure,
            'timer': app._game_timer, 'control_frames': frame if reached else frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'final_hp': player.hp, 'final_stamina': player.stamina,
            'checkpoint_seen': 302 in player.contact_pool or player.stand_pool == 302,
            'respawns': respawns, 'arrivals': arrivals, 'saved_checkpoint': player.spawn_pos,
            'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--route', type=Path, default=ROOT / 'scripts/routes/endless_climb.json')
    parser.add_argument('--fps', type=int, nargs='+', default=(30, 60, 144))
    parser.add_argument('--duration', type=int, default=120)
    args = parser.parse_args()
    route = json.loads(args.route.read_text())
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'route_sha256': hashlib.sha256(args.route.read_bytes()).hexdigest(),
              'route': route, 'scope': route['scope'],
              'runs': [run(fps, route, args.duration) for fps in args.fps]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'completed_route', 'failure', 'timer', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
