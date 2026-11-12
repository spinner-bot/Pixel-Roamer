"""Normal-spawn dive via the existing west rest platform and return to the beach."""
from collections import defaultdict
import argparse
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
from scripts.control_session import create_control_session, available_score
from teleport import can_place


def run(fps):
    session = create_control_session(21)
    app, player, world = session.app, session.app.player1, session.app._current_map
    initial_score = available_score(world)
    keys = defaultdict(bool)
    phase, rest_target = 'descend', None
    trace, transitions = [], []
    failure, swim_frames = None, 0
    min_hp, min_stamina = player.hp, player.stamina
    advanced_frames = 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(180 * fps):
            old_phase = phase
            events = []
            keys[pygame.K_w] = False
            target_x = 20.5
            if phase == 'descend':
                if abs(player._x - 20.5) < .1 and player._y <= 59.95 and player.can_climb:
                    events.extend([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w),
                                   pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)])
                    phase = 'entry_rest'
            elif phase == 'entry_rest':
                target_x = 23.5
                if player.on_ground and abs(player._y - 59.9) < .1 and abs(player._x - target_x) < .2:
                    phase = 'entry_edge'
            elif phase == 'entry_edge':
                target_x = 25.2
                if player.on_ground and player._x >= 25.1:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                    phase = 'west_diamond'
            elif phase in ('west_diamond', 'east_diamond'):
                keys[pygame.K_w] = True
                target_x = 35.5 if phase == 'west_diamond' else 42.5
                tile_x = 35 if phase == 'west_diamond' else 42
                if world.get_tile(tile_x, 63).type_id != 314:
                    phase = 'east_diamond' if phase == 'west_diamond' else 'return_ladder'
            elif phase == 'return_ladder':
                keys[pygame.K_w] = not player.can_swim
                if player.is_climbing:
                    rest_target = next((y for y in (27.9, 43.9, 59.9) if y > player._y + .2), None)
                    phase = 'rest_climb' if rest_target is not None else 'exit_climb'
            elif phase in ('rest_climb', 'exit_climb'):
                keys[pygame.K_w] = True
                target_y = rest_target if phase == 'rest_climb' else 68.95
                if player.is_climbing and player._y >= target_y:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                    phase = 'recover' if phase == 'rest_climb' else 'finish'
            elif phase == 'recover':
                target_x = 23.5
                if player.on_ground and abs(player._y - rest_target) < .1 and player.stamina >= 195:
                    phase = 'return_ladder'
            elif phase == 'finish':
                target_x = 23.5
                if player.on_ground and player._y >= 68.8:
                    break
            if phase != old_phase:
                transitions.append({'time': app._game_timer, 'from': old_phase, 'to': phase,
                                    'position': player.get_center(), 'stamina': player.stamina, 'score': player.score})
            desired = max(-8, min(8, (target_x - player._x) * 3))
            error = desired - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            advanced_frames += 1
            swim_frames += bool(player.can_swim and keys[pygame.K_w])
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if not can_place(player, world, *player.get_center()):
                failure = 'invalid physical placement'
                break
            if not player.alive or reset.call_count or player.fly_mode:
                failure = 'death respawn or flight'
                break
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'score': player.score,
                              'swimming_contact': player.can_swim, 'climbing': player.is_climbing})
        respawns = reset.call_count
    returned = phase == 'finish' and player.on_ground and player._y >= 68.8
    if not returned and failure is None:
        failure = 'route time budget exceeded'
    return {'fps': fps, 'returned_to_beach': returned, 'failure': failure, 'phase': phase,
            'control_frames': advanced_frames,
            'timer': app._game_timer, 'score': player.score, 'score_balance': player.score == initial_score - available_score(world),
            'water_diamonds_remaining': [world.get_tile(x, 63).type_id == 314 for x in (35, 42)],
            'position': player.get_center(), 'swim_input_seconds': swim_frames / fps,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'respawns': respawns,
            'transitions': transitions, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'existing shallow-pool water diamonds and west-ladder recovery, normal spawn and controls; not all water routes or device acceptance',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'returned_to_beach', 'phase', 'score', 'failure')} for r in report['runs']]))


if __name__ == '__main__':
    main()
