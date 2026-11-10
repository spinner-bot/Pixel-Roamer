"""Full Adventure Cove route: application events, production controls and no state cheats."""
import argparse
from collections import defaultdict
import json
import math
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


def run(fps=60, legacy=False):
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    if legacy:
        module = ModuleType('legacy_cove_route')
        module.__file__ = str(ROOT / 'maps/adventure_cove/map.py')
        source = subprocess.check_output(['git', 'show', '956158f:maps/adventure_cove/map.py'],
                                         cwd=ROOT, text=True)
        exec(compile(source, module.__file__, 'exec'), module.__dict__)
        _apply_config(module.world, 'adventure_cove')
        with patch('pixel_roamer.application.get_map', return_value=module.world):
            app.launch_world(21)
    else:
        app.launch_world(21)
    app.focused = True
    app.help_open = False
    app.page = PAGE_WORLD
    app._stamina_flash_duration = .6
    session = WorldSession(app)
    player = app.player1
    half_h = player._h / 2
    # Heights are support top faces, except actual climb bounds and end contact.
    targets = [('beach', 68.5, 62, 'land'), ('rift_launch', 92.5, 60, 'launch'),
               ('rift_landing', 137, 63, 'land'), ('rift_exit', 143, 69, 'land'), ('valley_launch', 195.5, 45, 'launch')]
    targets += [(f'ice_{x}', x + .5, 63, 'land') for x in (245, 251, 257, 263)]
    targets += [('vine', 278.5, 72, 'climb'), ('surefooted', 298.5, 64, 'land'),
                ('magnet_entry', 302.5, 62, 'land')]
    targets += [(f'magnet_jump_{x}', x + .5, 62, 'land') for x in (312, 322, 332)]
    targets += [('exit_ladder', 340.5, 72, 'climb'), ('temple_entry', 350, 74, 'land'),
                ('wind_entry', 354, 77, 'land')]
    targets += [(f'temple_pillar_{x}', x + .5, 88, 'land') for x in (358, 373, 388, 403)]
    targets += [('finish', 415.5, 79, 'end')]
    keys = defaultdict(bool)
    arrivals, trace, touched = [], [], set()
    leg = 0
    leg_start = jump_frame = 0
    jumped = set()
    min_hp, min_stamina = player.hp, player.stamina
    failure = None
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for frame in range(300 * fps):
            name, tx, top, mode = targets[leg]
            ty = top + half_h if mode in ('land', 'launch') else top
            speed = 6 if name in ('beach', 'rift_exit') else (7 if name == 'rift_launch' else 10)
            desired = max(-speed, min(speed, (tx - player._x) * 3))
            error = desired - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .5, error < -.5
            keys[pygame.K_w] = mode == 'climb'
            events = []
            if mode == 'climb' and player.can_climb and not player.is_climbing:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
            jump = False
            if name == 'beach':
                jump = player._x > 47 and player.on_ground and name not in jumped
            elif name == 'rift_launch':
                jump = player._x > 69.2 and player.on_ground and (name not in jumped or player._x > 89)
            elif mode == 'climb':
                jump = player.on_ground and ty > player._y + 1
            elif mode != 'launch':
                jump = (player.on_ground or player.is_climbing) and (ty > player._y + 1 or abs(tx - player._x) > 4)
            if jump:
                jump_frame = frame
                jumped.add(name)
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            # Delay horizontal movement so the jump passes beneath upper magnets.
            delay = .8 if name.startswith('magnet_jump_') else (.3 if name == 'rift_exit' else 0)
            if frame - jump_frame < delay * fps:
                keys[pygame.K_d] = keys[pygame.K_a] = False
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            touched.update(player.contact_pool)
            min_hp = min(min_hp, player.hp)
            min_stamina = min(min_stamina, player.stamina)
            if not all(math.isfinite(v) for v in (*player.get_center(), player.v_x, player.v_y)):
                raise AssertionError('nonfinite route state')
            if not can_place(player, app._current_map, *player.get_center()):
                raise AssertionError('route entered solid terrain')
            if player.fly_mode or app._game_over or app._player_lives_left != 3:
                failure = 'flight, death or respawn'
                break
            if frame % fps == 0:
                trace.append({'t': frame / fps, 'target': name, 'position': player.get_center(),
                              'velocity': [player.v_x, player.v_y], 'hp': player.hp,
                              'stamina': player.stamina})
            if app._game_win:
                break
            reached = False
            if mode == 'land':
                reached = abs(player._x - tx) < .5 and abs(player._y - ty) < .2 and player.on_ground
            elif mode == 'launch':
                reached = player.v_y > 25 and abs(player._x - tx) < 2
            elif mode == 'climb':
                reached = player.is_climbing and player._y > ty - .05
            if reached:
                arrivals.append({'name': name, 'seconds': frame / fps, 'position': player.get_center()})
                leg += 1
                leg_start = frame
            elif frame - leg_start >= 45 * fps:
                failure = 'waypoint time budget exceeded'
                break
    return {'fps': fps, 'seconds': (frame + 1) / fps, 'game_win': app._game_win,
            'reached_end': player._reached_end, 'failure': failure, 'target': targets[leg][0],
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'lives_left': app._player_lives_left, 'score': player.score,
            'touched_types': sorted(touched), 'arrivals': arrivals, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = [run(fps, args.legacy) for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'map_revision': '956158f' if args.legacy else 'current',
              'scope': 'full spawn to finish application/session route; synthetic controls; optional side rooms excluded',
              'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k not in ('trace', 'arrivals', 'touched_types')}
                      for run in results]))
    if not args.legacy and not all(run['game_win'] for run in results):
        sys.exit(1)


if __name__ == '__main__':
    main()
