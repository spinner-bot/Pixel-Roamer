"""Normal input score-target route; waypoint inputs are separate JSON test data."""
import argparse
from collections import defaultdict
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
from scripts.control_session import create_control_session, available_score, terminal_snapshot
from teleport import can_place
PLAN = ROOT / 'scripts/routes/collector.json'


def load_plan(world):
    document = json.loads(PLAN.read_text())
    if not isinstance(document, dict) or document.keys() != {'schema_version', 'map_id', 'waypoints'} or document['schema_version'] != 1 or document['map_id'] != world.map_id:
        raise ValueError('invalid audit plan header')
    if not isinstance(document['waypoints'], list):
        raise ValueError('audit waypoints must be a list')
    for point in document['waypoints']:
        if not isinstance(point, dict) or point.keys() != {'action', 'x', 'y'} or point['action'] not in ('collect', 'drop', 'ground', 'exit_shaft'):
            raise ValueError('invalid audit waypoint')
        if (any(type(point[key]) not in (int, float) or not math.isfinite(point[key]) for key in ('x', 'y'))
                or not 0 <= point['x'] < world.width or not 0 <= point['y'] < world.height):
            raise ValueError('audit waypoint outside world')
        if point['action'] == 'collect' and any(type(point[key]) is not int for key in ('x', 'y')):
            raise ValueError('collection target must be a grid cell')
    if not document['waypoints']:
        raise ValueError('empty audit plan')
    return document['waypoints']


def run(fps):
    session = create_control_session(9)
    app, player, world = session.app, session.app.player1, session.app._current_map
    plan = load_plan(world)
    initial_score = available_score(world)
    keys = defaultdict(bool)
    leg = leg_start = 0
    trace, arrivals, completed = [], [], set()
    min_hp, min_stamina = player.hp, player.stamina
    jump_started = False
    failure = None
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(300 * fps):
            point = plan[leg]
            action, x, y = point['action'], point['x'], point['y']
            tx = x + .5 if action == 'collect' else x
            error = max(-5, min(5, (tx - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .15, error < -.15
            keys[pygame.K_w] = False
            events = []
            done = False
            if action == 'collect':
                done = world.get_block_type(x, y).special != 'score'
                if not done and player.on_ground and (player._y + player._h / 2 < y + .05
                                                        or player.on_wall_left or player.on_wall_right):
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            elif action in ('ground', 'drop'):
                done = abs(player._x - tx) < .15 and abs(player._y - y) < .1 and player.on_ground
            elif action == 'exit_shaft':
                if not jump_started and player.on_ground and abs(player._x - tx) < .04 and abs(player.v_x) < .12:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                    jump_started = True
                if jump_started:
                    keys[pygame.K_d] = keys[pygame.K_a] = False
                done = jump_started and player._y >= y
            if done:
                if leg not in completed:
                    arrivals.append({'leg': leg, 'action': action, 'time': app._game_timer,
                                     'position': player.get_center(), 'score': player.score})
                    completed.add(leg)
                if leg < len(plan) - 1:
                    leg += 1
                    leg_start, jump_started = frame, False
                else:
                    keys[pygame.K_d] = keys[pygame.K_a] = False
                    if player.score < world.score_goal:
                        failure = 'plan exhausted below score goal'
                        break
            # Every rendered frame advances the real session, including waypoint changes.
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'leg': leg, 'position': player.get_center(),
                              'score': player.score, 'hp': player.hp, 'stamina': player.stamina})
            if not can_place(player, world, *player.get_center()):
                failure = 'invalid position or terrain overlap'
                break
            if player.fly_mode or reset.call_count:
                failure = 'flight or unexpected respawn'
                break
            if app._game_win or app._game_over:
                break
            if frame - leg_start > 30 * fps:
                failure = 'waypoint time budget exceeded'
                break
        final = terminal_snapshot(session)
        frozen = None
        if app._game_win or app._game_over:
            for _ in range(2 * fps):
                session.advance(1 / fps)
            frozen = final == terminal_snapshot(session)
        respawns = reset.call_count
    return {'map_id': world.map_id, 'mode': world.mode, 'fps': fps, 'game_win': app._game_win, 'game_over': app._game_over,
            'timer': app._game_timer, 'control_frames': frame + 1, 'score': player.score, 'score_goal': world.score_goal,
            'available_score': initial_score, 'remaining_score': available_score(world),
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'terminal_state_frozen': frozen, 'failure': failure,
            'leg': leg, 'arrivals': arrivals, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runs = [run(fps) for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'scope': 'normal spawn to score-target victory using production controls; optional loot excluded; no device acceptance',
              'plan': str(PLAN.relative_to(ROOT)), 'plan_sha256': hashlib.sha256(PLAN.read_bytes()).hexdigest(),
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k not in ('arrivals', 'trace')} for run in runs]))
    if not all(run['game_win'] and run['terminal_state_frozen'] and run['failure'] is None for run in runs):
        sys.exit(1)


if __name__ == '__main__':
    main()
