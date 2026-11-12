"""Normal forest departure and the original T5 connection to the sky islands."""
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
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps):
    session = create_control_session(3)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    trace, hops = [], []
    reached, landed, failure = False, False, None
    min_hp, min_stamina = player.hp, player.stamina
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(60 * fps):
            target_x = 185.5 if reached else 70.5
            error = max(-7, min(7, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            jump = not reached and player.on_ground and (player.on_wall_right or player._x > 60)
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            before = player.get_center()
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if abs(player._x - before[0]) > 90:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
                reached = abs(player._x - 185) < 1 and abs(player._y - 70) < 1
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina,
                              'ground': player.on_ground, 'wall_right': player.on_wall_right})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if reached and player.on_ground and 185 <= player._x <= 188 and abs(player._y - 61.9) < .01:
                landed = True
                break
        respawns = reset.call_count
    if not landed and failure is None:
        failure = 'sky destination landing not reached before input budget'
    return {'fps': fps, 'reached_T5_sky_destination': reached, 'landed_on_original_sky_island': landed,
            'failure': failure,
            'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'portal_hops': hops, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal forest spawn to original T5 sky destination, production controls/config; not whole-map traversal',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'reached_T5_sky_destination', 'failure', 'timer', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
