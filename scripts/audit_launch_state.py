"""Compare a real jump request immediately after launcher contact, before/after fix."""
from collections import defaultdict
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from camera import Camera
from creature import Player
from player_factory import create_world_player
from pixel_roamer.world_session import WorldSession
from world import World


def measure(player_class, fps):
    world = World(0, 'catapult', 12, 30, gravity=-6.5)
    world.set_tile(5, 1, 433)
    bindings = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                    down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    with patch('player_factory.Player', player_class):
        player = create_world_player(world, bindings, position=(5.5, 2.9))
    player.collide_with_world(world, 0)
    contact = {'ground': player.on_ground, 'vy': player.v_y}
    app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                          jump_pressed=True, _game_over=False, _game_win=False,
                          _game_timer=0, _player_lives_left=3, _infinite_lives=False,
                          camera=Camera(640, 360, world), _stamina_flash_timer=0,
                          _stamina_flash_duration=.6)
    session = WorldSession(app)
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), patch('sfx.play_jump'):
        for _ in range(3):
            session.advance(1 / fps)
    return {'fps': fps, 'after_contact': contact, 'after_jump_request':
            {'vy': player.v_y, 'stamina': player.stamina, 'position': player.get_center()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_launch_creature')
    module.__file__ = str(ROOT / 'creature.py')
    source = subprocess.check_output(['git', 'show', '956158f:creature.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy_revision': '956158f', 'scope': 'isolated launch contact and production session jump input',
              'before': [measure(module.Player, fps) for fps in (30, 60, 144)],
              'after': [measure(Player, fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
