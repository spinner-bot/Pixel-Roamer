"""Measure deliberate retreat from solid magnetic faces using production controls."""
import argparse
from collections import defaultdict
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
from teleport import can_place
from world import World


def run(kind, side, fps, player_class=Player):
    world = World(0, 'magnetic escape', 24, 24, gravity=-6.5)
    for x in range(24):
        world.set_tile(x, 0, 2)
    for y in (10, 11):
        world.set_tile(10, y, kind)
    # The mixed case verifies that limits apply to combined magnetic sources.
    if kind == 386:
        world.set_tile(10, 11, 403)
    x = 9.6 if side == 'left' else 11.4
    bindings = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                    down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    with patch('player_factory.Player', player_class):
        player = create_world_player(world, bindings, position=(x, 11))
    app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                          jump_pressed=False, _game_over=False, _game_win=False,
                          _game_timer=0, _player_lives_left=3, _infinite_lives=False,
                          camera=Camera(640, 360, world), _stamina_flash_timer=0,
                          _stamina_flash_duration=.6)
    session = WorldSession(app)
    away = pygame.K_a if side == 'left' else pygame.K_d
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool, {away: True})):
        for _ in range(4 * fps):
            session.advance(1 / fps)
            if not can_place(player, world, *player.get_center()):
                raise AssertionError('escape entered a solid block')
    retreat = (x - player._x) if side == 'left' else (player._x - x)
    return {'kind': kind, 'side': side, 'fps': fps, 'start': [x, 11],
            'after_four_seconds': player.get_center(), 'retreat': retreat,
            'escaped': retreat > 1, 'hp': player.hp, 'lives_left': app._player_lives_left}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    player_class = Player
    if args.legacy:
        module = ModuleType('legacy_magnetic_creature')
        module.__file__ = str(ROOT / 'creature.py')
        source = subprocess.check_output(['git', 'show', '783bd52:creature.py'], cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        player_class = module.Player
    runs = [run(kind, side, fps, player_class) for kind in (338, 386, 403)
            for side in ('left', 'right') for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy': args.legacy, 'scope': 'isolated magnetic faces; synthetic production session input',
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'runs': len(runs), 'escaped': sum(run['escaped'] for run in runs)}))


if __name__ == '__main__':
    main()
