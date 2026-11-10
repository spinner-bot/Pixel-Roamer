"""Real WorldSession swimming input sequences on mirrored shores."""
import argparse
from collections import defaultdict
import json
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
import pygame
from camera import Camera
from creature import Player
from world import World
from pixel_roamer.world_session import WorldSession


def make_session(side='left', start_y=20, width=.8, height=1.8):
    world = World(0, 'swimming', 10, 30, gravity=-6.5)
    for x in range(10):
        world.set_tile(x, 0, 2)
    for x in range(1, 9):
        for y in range(1, 20):
            world.set_tile(x, y, 7)
    for y in range(20):
        world.set_tile(0 if side == 'left' else 9, y, 2)
    keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    x = 1 + width / 2 + .05 if side == 'left' else 9 - width / 2 - .05
    player = Player(0, 'swimming', x, start_y, keys, w=width, h=height)
    player.collide_with_world(world, 0)
    app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                          jump_pressed=False, _game_over=False, _game_win=False,
                          _game_timer=0, _player_lives_left=3, _infinite_lives=False,
                          camera=Camera(640, 360, world),
                          _stamina_flash_timer=0, _stamina_flash_duration=.6)
    return WorldSession(app)


def exercise(side, fps, start_y):
    session = make_session(side, start_y)
    player = session.app.player1
    surface = player._swim_top_y
    session.app.jump_pressed = start_y <= 20
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool, {pygame.K_w: True})), patch('sfx.play_jump'):
        session.advance(1 / fps)
        first = {'position': player.get_center(), 'pending': getattr(player, '_shore_exit_pending', False),
                 'exit_buff': player.has_buff(58), 'stamina': player.stamina}
        for _ in range(fps - 1):
            session.advance(1 / fps)
    return {'side': side, 'fps': fps, 'start_y': start_y, 'initial_surface': surface,
            'first_frame': first, 'after_one_second': player.get_center(),
            'on_ground': player.on_ground, 'pending': getattr(player, '_shore_exit_pending', False),
            'hp': player.hp, 'stamina': player.stamina}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = [exercise(side, fps, y) for side in ('left', 'right')
               for fps in (30, 60, 144) for y in (10, 20, 20.7)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(), 'scope': 'actual session controls, synthetic held keys; no physical device acceptance',
              'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
