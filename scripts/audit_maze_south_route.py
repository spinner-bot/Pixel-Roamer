"""Normal hub departure, south access shaft and the existing T2 portal."""
from collections import defaultdict
import argparse
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
from maps import get_map, _apply_config
from scripts.control_session import create_control_session
from scripts.maze_controls import west_departure
from scripts.audit_session_soak import errors_for


def run(fps, world=None):
    session = create_control_session(4, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    phase, phase_start, departure = 'west_exit', 0, 0
    trace, transitions, hops = [], [], []
    reached, failure, climb_frames = False, None, 0
    min_hp, min_stamina = player.hp, player.stamina
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(90 * fps):
            previous_phase = phase
            target_x, jump = 20.5, False
            keys[pygame.K_w] = False
            if phase == 'west_exit':
                departure, target_x, jump, done = west_departure(player, departure)
                if done:
                    phase = 'descent'
            elif phase == 'descent':
                if player.on_ground and abs(player._y - 1.9) < .1:
                    phase = 'south_climb'
            elif phase == 'south_climb':
                keys[pygame.K_w] = True
                if player.is_climbing and player._y >= 8:
                    phase, jump, target_x = 'south_portal', True, 23.5
                    keys[pygame.K_w] = False
            elif phase == 'south_portal':
                target_x = 23.5
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': player.get_center(), 'stamina': player.stamina})
                phase_start = frame
            error = max(-6, min(6, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            before = player.get_center()
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            climb_frames += player.is_climbing
            if abs(player._x - before[0]) > 10:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'climbing': player.is_climbing})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if phase == 'south_portal' and hops and abs(player._x - 2.5) < .01 and abs(player._y - 8.9) < .01:
                reached = True
                break
            if frame - phase_start > 20 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'reached_T2_destination': reached, 'failure': failure,
            'phase': phase, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'climb_input_seconds': climb_frames / fps, 'respawns': respawns,
            'transitions': transitions, 'portal_hops': hops, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = ModuleType('legacy_maze_south')
    old.__file__ = str(ROOT / 'maps/loop_maze/map.py')
    source = subprocess.check_output(['git', 'show', 'b745778:maps/loop_maze/map.py'], cwd=ROOT, text=True)
    exec(compile(source, old.__file__, 'exec'), old.__dict__)
    _apply_config(old.world, 'loop_maze')
    current = get_map(4)
    changes = [{'position': [x, y], 'before': old.world.get_tile(x, y).type_id, 'after': current.get_tile(x, y).type_id}
               for x, y in sorted(set(old.world.grid) | set(current.grid))
               if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': 'b745778',
              'scope': 'normal spawn to original south T2 destination via existing controls; vertical wrap and upper hidden rooms separate',
              'tile_changes': changes,
              'before': [run(fps, old.world.create_session()) for fps in (30, 60, 144)],
              'after': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [{'fps': r['fps'], 'goal': r['reached_T2_destination'], 'phase': r['phase']} for r in report[name]] for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
