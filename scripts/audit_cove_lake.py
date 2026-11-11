"""Normal-spawn lake-island treasure and existing vine return branch."""
from collections import defaultdict
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from maps import _apply_config, get_map
from scripts.control_session import create_control_session, available_score
from teleport import can_place


def run(fps, world=None):
    session = create_control_session(21, world=world)
    app, player = session.app, session.app.player1
    initial_score = available_score(app._current_map)
    keys = defaultdict(bool)
    leg, leg_start, jumped = 0, 0, False
    arrivals, trace = [], []
    failure = None
    min_hp, min_stamina, max_exit_y = player.hp, player.stamina, None
    targets = (('island', 55.5, 51.9), ('vine', 66.5, None), ('return_platform', 68.5, 62.9))
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(90 * fps):
            name, tx, ty = targets[leg]
            speed = 6 if leg == 0 else 4
            error = max(-speed, min(speed, (tx - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            keys[pygame.K_w] = leg == 1
            events = []
            jump = False
            if leg == 0:
                jump = player._x > 47 and player.on_ground and not jumped
            elif leg == 1:
                jump = player.on_ground and not jumped
            elif leg == 2:
                jump = player.is_climbing and not jumped
            if jump:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                jumped = True
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if leg == 2:
                max_exit_y = max(player._y, max_exit_y or player._y)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'leg': name, 'position': player.get_center(),
                              'score': player.score, 'hp': player.hp, 'stamina': player.stamina,
                              'climbing': player.is_climbing, 'bound': getattr(player, '_climb_top_y', None)})
            if not can_place(player, app._current_map, *player.get_center()):
                failure = 'invalid physical placement'
                break
            if reset.call_count or not player.alive:
                failure = 'death or respawn'
                break
            if leg == 1:
                bound = getattr(player, '_climb_top_y', None)
                arrived = player.is_climbing and bound is not None and player._y >= bound - .02
            else:
                arrived = abs(player._x - tx) < .2 and abs(player._y - ty) < .1 and player.on_ground
            if arrived:
                arrivals.append({'leg': name, 'time': app._game_timer, 'position': player.get_center(),
                                 'score': player.score, 'climb_bound': getattr(player, '_climb_top_y', None)})
                if leg == 2:
                    break
                leg += 1
                leg_start, jumped = frame, False
            if frame - leg_start > 20 * fps:
                failure = 'branch waypoint timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'branch_goal_reached': len(arrivals) == 3, 'arrivals': arrivals,
            'leg': targets[leg][0], 'failure': failure, 'timer': app._game_timer,
            'control_frames': frame + 1,
            'score': player.score, 'position': player.get_center(), 'max_exit_y': max_exit_y,
            'score_balance': player.score == initial_score - available_score(app._current_map),
            'diamonds_remaining': [app._current_map.get_tile(x, y).type_id == 314
                                   for x, y in ((55, 51), (66, 62))],
            'min_hp': min_hp, 'min_stamina': min_stamina, 'respawns': respawns, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_lake_cove')
    module.__file__ = str(ROOT / 'maps/adventure_cove/map.py')
    source = subprocess.check_output(['git', 'show', 'e3ba6ec:maps/adventure_cove/map.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    _apply_config(module.world, 'adventure_cove')
    current = get_map(21)
    changes = [{'position': [x, y], 'before': module.world.get_tile(x, y).type_id,
                'after': current.get_tile(x, y).type_id}
               for x, y in sorted(set(module.world.grid) | set(current.grid))
               if module.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': 'e3ba6ec',
              'tile_changes': changes,
              'scope': 'normal spawn to optional lake island and existing return platform; not formal victory or whole underground coverage',
              'before': [run(fps, module.world.create_session()) for fps in (30, 60, 144)],
              'after': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [{'fps': r['fps'], 'goal': r['branch_goal_reached'], 'leg': r['leg'],
                             'score': r['score'], 'failure': r['failure']} for r in report[name]] for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
