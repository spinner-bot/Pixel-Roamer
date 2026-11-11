"""Reach the original temple tower from spawn without its shortcut portal."""
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
from scripts.control_session import create_control_session, available_score
from scripts.audit_session_soak import errors_for


def run(fps, world=None):
    session = create_control_session(7, world=world)
    app, player, world = session.app, session.app.player1, session.app._current_map
    keys = defaultdict(bool)
    phase, phase_start = 'hall_approach', 0
    trace, transitions, hops = [], [], []
    reached, failure = False, None
    min_hp, min_stamina = player.hp, player.stamina
    initial_score = available_score(world)
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(90 * fps):
            previous_phase = phase
            target_x, jump = 24.5, False
            keys[pygame.K_w], keys[pygame.K_s] = False, False
            if phase == 'hall_approach':
                jump = player.on_ground and (player.on_wall_left or player.on_wall_right)
                if abs(player._x - 24.5) < .2 and player.on_ground:
                    phase, target_x, jump = 'hall_platform', 31.5, True
            elif phase == 'hall_platform':
                target_x = 31.5
                if player.on_ground and player._y > 20:
                    phase, target_x = 'hall_drop', 33.8
            elif phase == 'hall_drop':
                target_x = 33.8
                if player.on_ground and player._y < 18:
                    phase, target_x = 'tower_approach', 40.5
            elif phase == 'tower_approach':
                target_x = 40.5
                jump = player.on_ground and (player.on_wall_left or player.on_wall_right)
                if abs(player._x - 40.5) < .2:
                    phase = 'tower_climb'
                    jump = player.on_ground
            elif phase == 'tower_climb':
                target_x = 40.5
                keys[pygame.K_w] = True
                if player.is_climbing and player._y >= 35:
                    phase, target_x, jump = 'emerald_landing', 41.5, True
                    keys[pygame.K_w] = False
            elif phase == 'emerald_landing':
                target_x = 41.5
                keys[pygame.K_s] = True
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': player.get_center(), 'stamina': player.stamina})
                phase_start = frame
            error = max(-6, min(6, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            before = player.get_center()
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if abs(player._x - before[0]) > 10 or abs(player._y - before[1]) > 10:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'climbing': player.is_climbing})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode or hops:
                failure = issues or 'death respawn flight or shortcut portal'
                break
            if world.get_tile(41, 36).type_id != 315:
                reached = True
                break
            if frame - phase_start > 20 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'original_emerald_collected': reached, 'failure': failure,
            'phase': phase, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'transitions': transitions, 'portal_hops': hops,
            'score': player.score, 'consumed_score': initial_score - available_score(world),
            'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal spawn to original tower emerald with real controls, no portal shortcut or position edits',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'original_emerald_collected', 'phase', 'failure', 'position')} for r in report['runs']]))


if __name__ == '__main__':
    main()
