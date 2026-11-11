"""Normal maze spawn, west departure, horizontal wrap, east door and hidden portal."""
from collections import defaultdict
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for
from scripts.maze_controls import west_departure


def run(fps):
    session = create_control_session(4)
    app, player, world = session.app, session.app.player1, session.app._current_map
    keys = defaultdict(bool)
    surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    phase, phase_start = 0, 0
    departure_stage = 0
    arrivals, hops, trace = [], [], []
    crossed_seam, reached = False, False
    failure, draws = None, 0
    min_hp, min_stamina = player.hp, player.stamina
    targets = (('west_corridor', 19.5, 22.9), ('east_landing', -19.5, 18.9), ('portal', -21.5, None))
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(90 * fps):
            name, tx, ty = targets[phase]
            departure_jump = False
            if phase == 0:
                departure_stage, tx, departure_jump, arrived = west_departure(player, departure_stage)
            elif phase == 1:
                arrived = player.on_ground and abs(player._y - ty) < .1 and abs(player._x - tx) < .15
            if phase < 2:
                if arrived:
                    arrivals.append({'phase': name, 'time': app._game_timer, 'position': player.get_center()})
                    phase += 1
                    phase_start = frame
                    name, tx, ty = targets[phase]
            error = max(-6, min(6, (tx - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            jump = departure_jump if phase == 0 else (player.on_ground and (player.on_wall_left or player.on_wall_right))
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            before = player.get_center()
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            crossed_seam |= before[0] >= 0 > player._x
            if abs(player._x - before[0]) > 10:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                world.draw(surface, app.camera)
                draws += 1
                trace.append({'time': app._game_timer, 'phase': name, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina})
            issues = errors_for(session)
            if issues:
                failure = issues
                break
            if reset.call_count or not player.alive or player.fly_mode:
                failure = 'death respawn or flight'
                break
            if hops and abs(player._x - 4.5) < .01 and abs(player._y - 29.9) < .01:
                reached = True
                world.draw(surface, app.camera)
                draws += 1
                break
            if frame - phase_start > 30 * fps:
                failure = f'{name} timed out'
                break
        respawns = reset.call_count
    if not reached and failure is None:
        failure = 'route time budget exceeded'
    return {'fps': fps, 'reached_hidden_room': reached, 'failure': failure,
            'crossed_horizontal_seam': crossed_seam, 'portal_hops': hops,
            'arrivals': arrivals, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'terrain_draws': draws, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal-spawn horizontal wrap and existing T1 portal entry; terrain draws at negative camera coordinates; vertical wrap and other rooms separate',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'reached_hidden_room', 'timer', 'failure')} for r in report['runs']]))


if __name__ == '__main__':
    main()
