"""Production WorldSession routes with held keys, stamina and formal win checks."""
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map
from player_factory import create_world_player
import pygame
from camera import Camera
from pixel_roamer.world_session import WorldSession
from simulation import SIMULATION_HZ


def run_route(map_id, fps, upper=False):
    world = get_map(map_id)
    bindings = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                    down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    player = create_world_player(world, bindings, player_name='route')
    app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                          jump_pressed=False, _game_over=False, _game_win=False,
                          _game_timer=0, _player_lives_left=world.lives,
                          _infinite_lives=world.lives == 0,
                          camera=Camera(640, 360, world),
                          _stamina_flash_timer=0, _stamina_flash_duration=.6)
    session = WorldSession(app)
    keys = defaultdict(bool)
    targets = [(90, 9 + player._h / 2)]
    if upper:
        targets = [(24.5, 13 + player._h / 2), (38.5, 16 + player._h / 2),
                   (55.5, 13 + player._h / 2), (90, 9 + player._h / 2)]
    frames = jumps = 0
    min_hp = player.hp
    visited = []
    rewards = []
    jump_requests = 0
    min_stamina = player.stamina
    original_jump = player.jump

    def counted_jump(*args, **kwargs):
        nonlocal jumps
        success = original_jump(*args, **kwargs)
        jumps += int(success)
        return success

    with patch('pygame.key.get_pressed', return_value=keys), \
            patch('sfx.play_jump'), patch.object(player, 'jump', side_effect=counted_jump):
        for leg, (tx, ty) in enumerate(targets):
          previous_score = player.score
          for _ in range(fps * 200):
              desired_v = max(-6, min(6, (tx - player._x) * 3))
              error = desired_v - player.v_x
              keys[pygame.K_d] = error > .6
              keys[pygame.K_a] = error < -.6
              if ty > player._y + 1 and player.on_ground:
                  if abs(tx - player._x) < 8 or player._y > 12:
                      app.jump_pressed = True
                      jump_requests += 1
              session.advance(1 / fps)
              frames += 1
              min_stamina = min(min_stamina, player.stamina)
              min_hp = min(min_hp, player.hp)
              if app._player_lives_left != world.lives or app._game_over:
                  raise AssertionError(f'{map_id}/{fps}: death or respawn')
              if not player.alive or not all(math.isfinite(v) for v in
                      (player._x, player._y, player.v_x, player.v_y)):
                  raise AssertionError(f'{map_id}/{fps}: dead or nonfinite')
              rect = player.get_game_rect()
              for obstacle, kind in world.get_nearby_solid_blocks_game(rect):
                  dx = min(rect.x + rect.w, obstacle.x + obstacle.w) - max(rect.x, obstacle.x)
                  dy = min(rect.y + rect.h, obstacle.y + obstacle.h) - max(rect.y, obstacle.y)
                  if dx > 1e-7 and dy > 1e-7:
                      raise AssertionError(f'{map_id}/{fps}: overlap {kind.id}')
              if app._game_win:
                  visited.append([round(player._x, 3), round(player._y, 3)])
                  break
              if leg < len(targets) - 1 and abs(player._x - tx) < 0.5 and abs(player._y - ty) < 0.15 and player.on_ground:
                  visited.append([round(player._x, 3), round(player._y, 3)])
                  break
          else:
              raise AssertionError(f'{map_id}/{fps}: stuck at {(player._x, player._y)} target {(tx, ty)}')
          rewards.append(player.score - previous_score)
    if not app._game_win:
        raise AssertionError(f'{map_id}/{fps}: no finish')
    if min_hp < player.hp_max:
        raise AssertionError(f'{map_id}/{fps}: safe route caused damage: {min_hp}')
    if upper and any(value <= 0 for value in rewards[:3]):
        raise AssertionError(f'{map_id}/{fps}: missing upper platform rewards: {rewards}')
    return {'id': map_id, 'fps': fps, 'route': 'upper' if upper else 'main',
            'frames': frames, 'seconds': round(frames / fps, 3), 'jumps': jumps,
            'score': player.score, 'waypoint_rewards': rewards, 'min_hp': min_hp, 'max_hp': player.hp_max, 'vertical_drag': player.f_y, 'waypoints': visited,
            'reached_end': player._reached_end, 'game_win': app._game_win,
            'lives_left': app._player_lives_left, 'initial_lives': world.lives,
            'min_stamina': min_stamina, 'jump_requests': jump_requests}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    results = [run_route(mid, fps, upper) for mid in (1001, 1002, 1003)
               for fps in (30, 60, 144) for upper in (False, True)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(),
              'scope': 'production WorldSession controls and presets, synthetic keys; no physical device acceptance',
              'simulation_hz': SIMULATION_HZ, 'runs': results}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
