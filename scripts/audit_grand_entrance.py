"""Production input route from Grand Journey altar to its first upper cave."""
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
from maps import _apply_config
from pixel_roamer.application import GameApp, PAGE_WORLD
from pixel_roamer.world_session import WorldSession
from teleport import can_place


def run(fps, legacy=False):
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    if legacy:
        module = ModuleType('legacy_grand_entrance')
        module.__file__ = str(ROOT / 'maps/grand_journey/map.py')
        source = subprocess.check_output(['git', 'show', 'c95354d:maps/grand_journey/map.py'],
                                         cwd=ROOT, text=True)
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        _apply_config(module.world, 'grand_journey')
        with patch('pixel_roamer.application.get_map', return_value=module.world):
            app.launch_world(20)
    else:
        app.launch_world(20)
    app.focused, app.help_open, app.page = True, False, PAGE_WORLD
    app._stamina_flash_duration = .6
    session = WorldSession(app)
    player = app.player1
    keys = defaultdict(bool)
    phase, rest = 'altar', 0
    heights = (45.9, 56.9)
    trace = []
    min_hp, min_stamina, peak = player.hp, player.stamina, player._y
    rest_stops = []
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for frame in range(150 * fps):
            events = []
            keys[pygame.K_w] = False
            tx = 3002.5 if phase == 'altar' else 3006.5
            if phase == 'altar' and player.on_ground and abs(player._x - tx) < .4 and player._y > 34:
                phase = 'climb'
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if phase == 'climb':
                keys[pygame.K_w] = True
                if player.can_climb and not player.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
                if player.is_climbing and player._y >= heights[rest]:
                    phase = 'rest'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if phase == 'rest':
                tx = 3010.5
                keys[pygame.K_w] = False
                if player.on_ground and abs(player._y - heights[rest]) < .1 and player.stamina >= 95:
                    rest_stops.append({'position': player.get_center(), 'stamina': player.stamina,
                                       'seconds': frame / fps})
                    rest += 1
                    if rest == 2:
                        break
                    phase = 'climb'
            desired = max(-6, min(6, (tx - player._x) * 3))
            error = desired - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .3, error < -.3
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            peak = max(peak, player._y)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if not can_place(player, app._current_map, *player.get_center()):
                raise AssertionError('entrance route penetrated terrain')
            if player.fly_mode or app._game_over or app._player_lives_left != 5:
                raise AssertionError('entrance route used flight, death or respawn')
            if frame % fps == 0:
                trace.append({'t': frame / fps, 'phase': phase, 'position': player.get_center(),
                              'stamina': player.stamina, 'hp': player.hp})
            if legacy and frame >= 30 * fps:
                break
    return {'fps': fps, 'reached_cave': rest == 2, 'seconds': frame / fps,
            'position': player.get_center(), 'peak': peak, 'rest_stops': rest_stops,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'lives_left': app._player_lives_left,
            'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runs = [run(fps, args.legacy) for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy_map': args.legacy, 'scope': 'spawn to first cave only, actual application/session synthetic inputs',
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k != 'trace'} for run in runs]))
    if not args.legacy and not all(run['reached_cave'] for run in runs):
        sys.exit(1)


if __name__ == '__main__':
    main()
