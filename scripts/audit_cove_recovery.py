"""Walk off the beach, then recover using real application key events and stamina."""
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
from teleport import can_place
from pixel_roamer.application import GameApp, PAGE_WORLD
from pixel_roamer.world_session import WorldSession


def run(fps=60, legacy=False):
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    if legacy:
        module = ModuleType('legacy_cove')
        module.__file__ = str(ROOT / 'maps/adventure_cove/map.py')
        source = subprocess.check_output(['git', 'show', '95b7e45:maps/adventure_cove/map.py'],
                                         cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        _apply_config(module.world, 'adventure_cove')
        with patch('pixel_roamer.application.get_map', return_value=module.world):
            app.launch_world(21)
    else:
        app.launch_world(21)
    app.focused = True
    app.help_open = False
    app.page = PAGE_WORLD
    app.running = True
    app._stamina_flash_duration = .6
    session = WorldSession(app)
    player = app.player1
    keys = defaultdict(bool)
    trace = []
    frame = 0
    phase = 'fall'
    rest_index = 0
    rest_heights = (27.9, 43.9, 59.9)
    min_hp, min_stamina = player.hp, player.stamina
    maximum_floor_jump = None
    jump_start = None
    crossed_beach_wall = False
    jump_peak = None
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for frame in range(fps * 240):
            events = []
            target_x = 60 if phase == 'fall' else 20.5
            if phase == 'fall' and player._x > 47 and player.on_ground and not crossed_beach_wall:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                crossed_beach_wall = True
            keys[pygame.K_w] = False
            if phase == 'fall' and player._x > 59 and player._y < 12 and player.on_ground:
                phase = 'return'
            if phase == 'return' and abs(player._x - 20.5) < .15 and abs(player.v_x) < .5:
                phase = 'climb'
            if phase in ('climb', 'exit'):
                keys[pygame.K_w] = True
                if player.can_climb and not player.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
                target_y = rest_heights[rest_index] if rest_index < 3 else 69
                if player.is_climbing and player._y >= target_y:
                    phase = 'rest' if rest_index < 3 else 'finish'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                elif legacy and phase == 'climb' and frame > fps * 35 and jump_start is None:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                    jump_start, jump_peak = player._y, player._y
            if phase in ('rest', 'finish'):
                target_x = 23.5
                keys[pygame.K_w] = False
                if phase == 'rest' and player.on_ground and player._y > rest_heights[rest_index] - .1 and player.stamina >= 195:
                    rest_index += 1
                    phase = 'exit' if rest_index == 3 else 'climb'
            desired = max(-6, min(6, (target_x - player._x) * 3))
            error = desired - player.v_x
            keys[pygame.K_d] = error > .3
            keys[pygame.K_a] = error < -.3
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if not can_place(player, app._current_map, *player.get_center()):
                raise AssertionError('recovery penetrated solid terrain')
            min_hp = min(min_hp, player.hp)
            min_stamina = min(min_stamina, player.stamina)
            if jump_start is not None:
                jump_peak = max(jump_peak, player._y)
                if player.on_ground and frame > fps * 36:
                    maximum_floor_jump = jump_peak - jump_start
                    break
            if frame % fps == 0:
                trace.append({'t': frame / fps, 'phase': phase, 'position': player.get_center(),
                              'stamina': player.stamina, 'hp': player.hp,
                              'climbing': player.is_climbing, 'ground': player.on_ground})
            if phase == 'finish' and player.on_ground and player._y > 68:
                break
            if app._game_over or app._player_lives_left != 3 or player.fly_mode:
                raise AssertionError('recovery used a death, respawn or flight')
    return {'fps': fps, 'legacy': legacy, 'seconds': (frame + 1) / fps,
            'recovered': phase == 'finish' and player.on_ground and player._y > 68,
            'phase': phase, 'position': player.get_center(), 'min_hp': min_hp,
            'min_stamina': min_stamina, 'lives_left': app._player_lives_left,
            'rest_stops': rest_index, 'floor_jump_rise': maximum_floor_jump, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = [run(fps, args.legacy) for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'scope': 'production application jump/climb events and session held keys; synthetic input only',
              'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k != 'trace'} for run in results]))


if __name__ == '__main__':
    main()
