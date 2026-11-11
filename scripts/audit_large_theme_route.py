"""Normal controls across original large-map regions toward the sky islands."""
from collections import defaultdict
import argparse
import json
import math
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
    session = create_control_session(2)
    app, player, world = session.app, session.app.player1, session.app._current_map
    keys = defaultdict(bool)
    trace, regions = [], []
    phase, phase_start = 'cross_regions', 0
    canopy_index = 0
    volcano_index = 0
    reached, failure = False, None
    min_hp, min_stamina = player.hp, player.stamina
    furthest, last_progress = player._x, 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(220 * fps):
            target_x, jump, speed_limit = 599.5, False, 6
            keys[pygame.K_w], keys[pygame.K_s] = False, False
            if phase == 'cross_regions':
                feet = player._y - player._h / 2
                ahead = math.floor(player._x + player._w / 2 + 1)
                danger = any(world.get_block_type(ahead, y).damage_ps > 0
                             for y in range(math.floor(feet) - 1, math.floor(player._y + player._h / 2) + 1))
                jump = player.on_ground and (player.on_wall_right or danger)
                keys[pygame.K_w] = player.can_swim and not player.on_ground and player.stamina > 60
                # This authored platform stands above the waterline. The
                # existing surface-only shore move deliberately rejects it;
                # dive below its underside instead of changing that rule.
                if 300 <= player._x <= 400:
                    keys[pygame.K_w] = False
                swim_top = getattr(player, '_swim_top_y', None)
                if player.can_swim and getattr(player, '_near_shore', False) and swim_top is not None:
                    jump |= abs(player._y - swim_top) <= .1
                # Jump from the last dry ledge before the original forest lake;
                # the far tree is taller than the surface-only shore maneuver.
                if ((13.5 <= player._x < 15.3 and player._y > 50)
                        or 26.2 <= player._x < 27) and player.on_ground:
                    phase, phase_start, target_x, jump = 'forest_lake_jump', frame, 40.5, True
                if player._x >= 504:
                    phase, phase_start, target_x = 'volcano_runup', frame, 507.5
            elif phase == 'forest_lake_jump':
                target_x = 40.5
                if player.on_ground and abs(player._x - 40.5) < .15 and player._y > 18:
                    phase, phase_start, target_x, jump = 'forest_canopy_jump', frame, 55.5, True
            elif phase == 'forest_canopy_jump':
                target_x = (55.5, 70.5, 85.5)[canopy_index]
                if player.on_ground and abs(player._x - target_x) < .15 and player._y > 18:
                    canopy_index += 1
                    phase_start, jump = frame, True
                    if canopy_index == 3:
                        phase, target_x = 'forest_finish', 102.5
                    else:
                        target_x = (55.5, 70.5, 85.5)[canopy_index]
            elif phase == 'forest_finish':
                target_x = 102.5
                if player.on_ground and abs(player._x - target_x) < .15:
                    phase, phase_start = 'cross_regions', frame
            elif phase == 'volcano_runup':
                target_x = 507.5
                if player.on_ground and abs(player._x - target_x) < .15 and player.stamina >= 95:
                    phase, phase_start, target_x, jump = 'volcano_platforms', frame, 525.5, True
            elif phase == 'volcano_platforms':
                target_x = (525.5, 541.5, 561.5, 579.4)[volcano_index]
                speed_limit = 8
                if player.on_ground and abs(player._x - target_x) < .15:
                    volcano_index += 1
                    phase_start, jump = frame, True
                    if volcano_index == 4:
                        phase, target_x, speed_limit = 'sky_landing', 605.5, 20
                    else:
                        target_x = (525.5, 541.5, 561.5, 579.4)[volcano_index]
            elif phase == 'sky_landing':
                target_x = 605.5
                speed_limit = 20
            error = max(-speed_limit, min(speed_limit, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            while len(regions) < 6 and player._x >= (len(regions) + 1) * 100:
                regions.append({'boundary_x': (len(regions) + 1) * 100,
                                'time': app._game_timer, 'position': player.get_center(),
                                'hp': player.hp, 'stamina': player.stamina})
            if frame % (2 * fps) == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'on_ground': player.on_ground,
                              'wall_right': player.on_wall_right, 'swimming': player.can_swim})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if phase == 'sky_landing' and player.on_ground and abs(player._x - 605.5) < .15 and abs(player._y - 42.9) < .02:
                reached = True
                break
            if player._x > furthest + .2:
                furthest, last_progress = player._x, frame
            if phase == 'cross_regions' and frame - last_progress > 20 * fps:
                failure = 'no forward progress for 20 seconds'
                break
            if phase != 'cross_regions' and frame - phase_start > 20 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'reached_original_sky_island': reached, 'failure': failure, 'phase': phase,
            'timer': app._game_timer, 'control_frames': frame + 1, 'position': player.get_center(),
            'min_hp': min_hp, 'min_stamina': min_stamina, 'respawns': respawns,
            'regions': regions, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal spawn across large-map regions to original sky island, real controls and production config; controller failure alone is not global inaccessibility',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'reached_original_sky_island', 'phase', 'failure', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
