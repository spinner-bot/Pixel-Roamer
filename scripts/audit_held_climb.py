"""Compare pre-held climb input at real ladder contact, with application events."""
import argparse
from collections import defaultdict
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
from pixel_roamer.application import GameApp, PAGE_WORLD
from pixel_roamer.world_session import WorldSession
from teleport import can_place
from world import World


def make_session(start_x=3, session_class=WorldSession):
    world = World(0, 'held climb', 12, 24, gravity=-6.5, spawn_points=(start_x, 1.9))
    for x in range(12):
        world.set_tile(x, 0, 2)
    for y in range(1, 13):
        world.set_tile(5, y, 9)
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    with patch('pixel_roamer.application.get_map', return_value=world):
        app.launch_world(0)
    app.focused, app.help_open, app.page = True, False, PAGE_WORLD
    app._stamina_flash_duration = .6
    return session_class(app)


def run(fps, side, arrows, session_class=WorldSession):
    session = make_session(3 if side == 'left' else 8, session_class)
    app, player = session.app, session.app.player1
    up = pygame.K_UP if arrows else pygame.K_w
    left = pygame.K_LEFT if arrows else pygame.K_a
    right = pygame.K_RIGHT if arrows else pygame.K_d
    keys = defaultdict(bool, {up: True})
    climbed = False
    with patch('pygame.key.get_pressed', return_value=keys):
        for frame in range(fps * 6):
            desired = max(-4, min(4, (5.5 - player._x) * 3))
            error = desired - player.v_x
            keys[right] = error > .3 and not player.is_climbing
            keys[left] = error < -.3 and not player.is_climbing
            # Exactly one up keydown occurs before reaching the ladder.
            events = [pygame.event.Event(pygame.KEYDOWN, key=up)] if frame == 0 else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            climbed |= player.is_climbing
            if not can_place(player, app._current_map, *player.get_center()):
                raise AssertionError('held climb entered solid terrain')
    return {'fps': fps, 'side': side, 'keys': 'arrows' if arrows else 'wasd',
            'climbed': climbed, 'position': player.get_center(), 'can_climb': player.can_climb,
            'stamina': player.stamina, 'hp': player.hp}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_held_climb_session')
    module.__file__ = str(ROOT / 'pixel_roamer/world_session.py')
    source = subprocess.check_output(['git', 'show', '29ba738:pixel_roamer/world_session.py'],
                                     cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy_revision': '29ba738', 'scope': 'isolated held input approach, actual application/session; no device acceptance'}
    for label, session_class in (('before', module.WorldSession), ('after', WorldSession)):
        report[label] = [run(fps, side, arrows, session_class) for fps in (30, 60, 144)
                         for side in ('left', 'right') for arrows in (False, True)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({label: sum(run['climbed'] for run in report[label]) for label in ('before', 'after')}))


if __name__ == '__main__':
    main()
