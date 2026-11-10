"""Production Grand Journey routes through existing mechanics to formal victory."""
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


def run(fps, legacy=False, upper=False, portal=False, finish=False):
    portal = portal or finish
    upper = upper or portal
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    if legacy:
        module = ModuleType('legacy_grand_entrance')
        module.__file__ = str(ROOT / 'maps/grand_journey/map.py')
        source = subprocess.check_output(['git', 'show', ('b93d820' if portal else ('43c16b4' if upper else 'c95354d')) + ':maps/grand_journey/map.py'],
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
    tops = (45, 56, 71) if upper else (45, 56)
    heights = tuple(top + player._h / 2 for top in tops)
    rest_goal = 100 if portal else 95
    reached_hall = False
    reached_portal = False
    hops = []
    failure = None
    north_climb_bound = None
    jump_targets = {'stone': (2997.5, 104 + player._h / 2),
                    'low_platform': (2991.5, 112 + player._h / 2),
                    'high_platform': (3000.5, 120 + player._h / 2),
                    'gate': (3018.5, 120 + player._h / 2)}
    distant_targets = {'library': (5005.5, 53 + player._h / 2),
                       'crystal': (5510.5, 52 + player._h / 2),
                       'final': (5940.5, 88 + player._h / 2)}
    trace = []
    min_hp, min_stamina, peak = player.hp, player.stamina, player._y
    rest_stops = []
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for frame in range(300 * fps):
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
                drop_to_rest = upper and rest == 2
                leave_height = 74 - player._h / 2 if drop_to_rest else heights[rest]
                if player.is_climbing and player._y >= leave_height:
                    phase = 'rest'
                    key = pygame.K_s if drop_to_rest else pygame.K_SPACE
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=key))
            if phase == 'rest':
                tx = 3010.5
                keys[pygame.K_w] = False
                if player.on_ground and player._y >= heights[rest] - .1 and player.stamina >= rest_goal:
                    rest_stops.append({'position': player.get_center(), 'stamina': player.stamina,
                                       'seconds': frame / fps})
                    rest += 1
                    if rest == len(heights):
                        if not upper:
                            break
                        phase = 'landing' if player._y >= 76.8 else 'ascend'
                    else:
                        phase = 'climb'
            if phase == 'ascend':
                keys[pygame.K_w] = True
                if player.can_climb and not player.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
                if player._y >= 82.95:
                    phase = 'landing'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
            if phase == 'landing':
                tx = 3002.5
                keys[pygame.K_w] = False
                if player.on_ground and (player.on_wall_left or player.on_wall_right) and abs(player._x - tx) > 1:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                if player.on_ground and abs(player._y - 76.9) < .1 and abs(player._x - tx) < .4:
                    reached_hall = True
                    if not portal:
                        break
                    phase = 'north_align'
            if phase == 'north_align':
                tx = 2996.5
                keys[pygame.K_w] = False
                if player.on_ground and abs(player._x - tx) < .15 and abs(player.v_x) < .5 and player.stamina >= 100:
                    phase = 'north_climb'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if phase == 'north_climb':
                tx = 2996.5
                keys[pygame.K_w] = True
                if player.can_climb and not player.is_climbing:
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
                if player.is_climbing and player._y >= 105:
                    phase = 'stone'
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
            if phase in jump_targets:
                tx, ty = jump_targets[phase]
                keys[pygame.K_w] = False
                if player.on_ground:
                    if abs(player._x - tx) < .4 and abs(player._y - ty) < .1:
                        if player.stamina >= 95 and phase != 'gate':
                            sequence = list(jump_targets)
                            phase = sequence[sequence.index(phase) + 1]
                    elif player.stamina >= 20 and (ty > player._y + 1 or abs(player._x - tx) > 4
                                                     or player.on_wall_left or player.on_wall_right):
                        events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if phase in distant_targets:
                tx, ty = distant_targets[phase]
                keys[pygame.K_w] = False
                if player.on_ground and ((abs(tx - player._x) < 7 and ty > player._y + 1)
                                         or ((player.on_wall_left or player.on_wall_right) and abs(tx - player._x) > 1)):
                    events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            desired = max(-6, min(6, (tx - player._x) * 3))
            error = desired - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .3, error < -.3
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            previous = player.get_center()
            session.advance(1 / fps)
            if abs(player._x - previous[0]) > 100:
                hops.append({'phase': phase, 'from': previous, 'to': player.get_center()})
            if phase == 'north_climb':
                bound = getattr(player, '_climb_top_y', None)
                if bound is not None:
                    north_climb_bound = max(north_climb_bound or bound, bound)
            peak = max(peak, player._y)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if not can_place(player, app._current_map, *player.get_center()):
                failure = {'position': player.get_center(), 'phase': phase, 'reason': 'terrain overlap or invalid coordinates'}
                break
            if player.fly_mode or app._game_over or app._player_lives_left != 5:
                failure = {'position': player.get_center(), 'phase': phase, 'lives': app._player_lives_left}
                break
            if portal and player._x > 4000 and not reached_portal:
                reached_portal = True
                if not finish:
                    break
                phase = 'library'
            if finish and phase == 'library' and player._x > 5400:
                phase = 'crystal'
            if finish and phase == 'crystal' and player._x > 5800:
                phase = 'final'
            if finish and app._game_win:
                break
            if frame % fps == 0:
                trace.append({'t': frame / fps, 'phase': phase, 'position': player.get_center(),
                              'stamina': player.stamina, 'hp': player.hp})
            if legacy and frame >= (150 if portal else (90 if upper else 30)) * fps:
                break
    reached_goal = app._game_win if finish else (reached_portal if portal else (reached_hall if upper else rest >= 2))
    if not reached_goal and failure is None:
        failure = {'reason': 'route time budget exceeded', 'phase': phase, 'position': player.get_center()}
    return {'game_win': app._game_win, 'reached_end': player._reached_end, 'hops': hops, 'fps': fps, 'simulation_seconds': session.app._game_timer, 'reached_cave': rest >= 2, 'reached_hall': reached_hall, 'reached_portal': reached_portal, 'north_climb_bound': north_climb_bound, 'failure': failure, 'phase': phase, 'seconds': frame / fps,
            'position': player.get_center(), 'peak': peak, 'rest_stops': rest_stops,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'lives_left': app._player_lives_left,
            'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--upper', action='store_true')
    parser.add_argument('--portal', action='store_true')
    parser.add_argument('--finish', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    goal = 'finish' if args.finish else ('portal' if args.portal else ('hall' if args.upper else 'cave'))
    runs = [run(fps, args.legacy, args.upper, args.portal, args.finish) for fps in (30, 60, 144)]
    revisions = {'cave': 'c95354d', 'hall': '43c16b4', 'portal': 'b93d820', 'finish': 'b93d820'}
    scopes = {'cave': 'spawn to first cave', 'hall': 'spawn to cross hall',
              'portal': 'spawn to first portal',
              'finish': 'spawn to formal victory via existing portals; optional regions excluded'}
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'goal': goal, 'legacy_map': args.legacy,
              'legacy_map_revision': revisions[goal] if args.legacy else None,
              'scope': scopes[goal] + '; actual application/session synthetic inputs; no device acceptance',
              'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in run.items() if k != 'trace'} for run in runs]))
    result_key = {'cave': 'reached_cave', 'hall': 'reached_hall',
                  'portal': 'reached_portal', 'finish': 'game_win'}[goal]
    if not args.legacy and not all(run[result_key] for run in runs):
        sys.exit(1)


if __name__ == '__main__':
    main()
