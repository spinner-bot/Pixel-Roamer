"""Existing small objective maps using actual application events and world rules."""
import argparse
from collections import defaultdict
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
from teleport import can_place


def run(map_id, fps):
    session = create_control_session(map_id)
    app, player = session.app, session.app.player1
    world = app._current_map
    available_score = sum(world.block_types[tile.type_id].special_data
                          for tile in world.grid.values()
                          if world.block_types[tile.type_id].special == 'score')
    keys = defaultdict(bool)
    teleported = False
    direction = 1
    release_up_until = 0
    min_x = max_x = player._x
    min_y = max_y = player._y
    min_hp, min_stamina = player.hp, player.stamina
    trace = []
    limit = world.time_limit + 1 if map_id == 8 else 30
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(int(limit * fps)):
            if map_id == 7:
                direction = -1 if teleported else 1
                jump = player.on_ground and (player.on_wall_left or player.on_wall_right)
            else:
                if player._x >= world.width - 1.5:
                    direction = -1
                elif player._x <= 1.5:
                    direction = 1
                bound = getattr(player, '_climb_top_y', None)
                jump = ((player.on_ground and (frame % fps == 0 or player.on_wall_left or player.on_wall_right))
                        or (player.is_climbing and bound is not None and player._y >= bound - .05))
            keys[pygame.K_d], keys[pygame.K_a] = direction > 0, direction < 0
            events = []
            if map_id == 8:
                keys[pygame.K_w] = frame >= release_up_until
                if keys[pygame.K_w] and player.can_climb and not player.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
            if jump:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                release_up_until = frame + int(.75 * fps)
                keys[pygame.K_w] = False
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            min_x, max_x = min(min_x, player._x), max(max_x, player._x)
            min_y, max_y = min(min_y, player._y), max(max_y, player._y)
            if not can_place(player, world, *player.get_center()):
                raise AssertionError(f'{map_id}/{fps}: invalid or overlapping position')
            if player._x > 40 and player._y > 35:
                teleported = True
            if frame % fps == 0:
                trace.append({'t': frame / fps, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'score': player.score})
            if app._game_win or app._game_over:
                break
        def snapshot():
            return {'timer': app._game_timer, 'position': player.get_center(),
                    'velocity': (player.v_x, player.v_y), 'score': player.score,
                    'hp': player.hp, 'stamina': player.stamina, 'shield': player.shield,
                    'buffs': [(buff.buff_id, buff.duration, buff.stacks) for buff in player.buffs]}

        final = snapshot()
        frozen = None
        if app._game_over or app._game_win:
            for _ in range(2 * fps):
                session.advance(1 / fps)
            frozen = final == snapshot()
        respawns = reset.call_count
    remaining_score = sum(world.block_types[tile.type_id].special_data
                          for tile in world.grid.values()
                          if world.block_types[tile.type_id].special == 'score')
    return {'available_score': available_score, 'remaining_score': remaining_score, 'map': map_id, 'fps': fps, 'game_win': app._game_win, 'game_over': app._game_over,
            'timer': app._game_timer, 'time_limit': world.time_limit, 'score': player.score,
            'position': player.get_center(), 'reached_end': player._reached_end,
            'teleported': teleported, 'respawns': respawns, 'lives_left': app._player_lives_left,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'terminal_state_frozen': frozen,
            'x_range': [min_x, max_x], 'y_range': [min_y, max_y], 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--map-id', action='append', choices=(7, 8), type=int)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runs = [run(mid, fps) for mid in (args.map_id or (7, 8)) for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'scope': 'production application/session controls to terminal state; synthetic inputs; no device acceptance',
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k != 'trace'} for run in runs]))
    if not all(run['terminal_state_frozen'] and
               (run['game_win'] if run['map'] == 7 else run['game_over'] and run['score'] > 0)
               for run in runs):
        sys.exit(1)


if __name__ == '__main__':
    main()
