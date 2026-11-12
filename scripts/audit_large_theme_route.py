"""Normal controls across original large-map regions toward the sky islands."""
from collections import defaultdict
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from maps import get_map, _apply_config
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, world=None):
    started = time.perf_counter()
    session = create_control_session(2, world=world)
    app, player, world = session.app, session.app.player1, session.app._current_map
    keys = defaultdict(bool)
    trace, regions, transitions = [], [], []
    surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    terrain_draws, max_frame_dx = 0, 0
    phase, phase_start = 'cross_regions', 0
    canopy_index = 0
    volcano_index = 0
    reached, failure = False, None
    min_hp, min_stamina = player.hp, player.stamina
    furthest, last_progress = player._x, 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(220 * fps):
            previous_phase = phase
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
                        phase, target_x, speed_limit = 'sky_base_rest', 599.5, 8
                    else:
                        target_x = (525.5, 541.5, 561.5, 579.4)[volcano_index]
            elif phase == 'sky_base_rest':
                target_x = 599.5
                if player.on_ground and abs(player._x - target_x) < .15 and player.stamina >= 95:
                    phase, phase_start = 'sky_climb', frame
            elif phase == 'sky_climb':
                keys[pygame.K_w] = True
                if player.is_climbing and player._y >= 23.98:
                    phase, phase_start, target_x, jump = 'sky_landing', frame, 605.5, True
                    keys[pygame.K_w] = False
            elif phase == 'sky_landing':
                target_x = 605.5
                speed_limit = 8
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': player.get_center(), 'hp': player.hp,
                                    'stamina': player.stamina, 'velocity': [player.v_x, player.v_y]})
            error = max(-speed_limit, min(speed_limit, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            before_x = player._x
            session.advance(1 / fps)
            max_frame_dx = max(max_frame_dx, abs(player._x - before_x))
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            while len(regions) < 6 and player._x >= (len(regions) + 1) * 100:
                regions.append({'boundary_x': (len(regions) + 1) * 100,
                                'time': app._game_timer, 'position': player.get_center(),
                                'hp': player.hp, 'stamina': player.stamina})
            if frame % (2 * fps) == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'on_ground': player.on_ground,
                              'wall_right': player.on_wall_right, 'swimming': player.can_swim,
                              'velocity': [player.v_x, player.v_y]})
            if frame % (5 * fps) == 0:
                world.draw(surface, app.camera)
                terrain_draws += 1
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if phase == 'sky_landing' and player.on_ground and abs(player._x - 605.5) < .15 and abs(player._y - 42.9) < .02:
                world.draw(surface, app.camera)
                terrain_draws += 1
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
            'production_options': {'gravity': world.gravity, 'v_max': player._base_v_max,
                                   'v_jump': player.v_jump, 'stamina_max': player.stamina_max,
                                   'f_x': player.f_x, 'f_y': player.f_y},
            'max_frame_dx': max_frame_dx, 'terrain_draws': terrain_draws,
            'regions': regions, 'transitions': transitions, 'trace': trace,
            'wall_seconds': time.perf_counter() - started}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--current-only', action='store_true')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'legacy_revision': 'c6357d6',
              'scope': 'normal spawn across large-map regions to original sky island, real controls and production config; controller failure alone is not global inaccessibility',
              'after': []}
    if not args.current_only:
        old = ModuleType('legacy_large_theme')
        old.__file__ = str(ROOT / 'maps/test_world_2/map.py')
        source = subprocess.check_output(['git', 'show', 'c6357d6:maps/test_world_2/map.py'], cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        _apply_config(old.world, 'test_world_2')
        current = get_map(2)
        report['tile_changes'] = [
            {'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
             'after': current.get_tile(x, y).type_id}
            for x, y in sorted(set(old.world.grid) | set(current.grid))
            if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
        report['before'] = [run(fps, old.world.create_session()) for fps in (30, 60, 144)]
    report['after'] = [run(fps) for fps in (30, 60, 144)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [{k: r[k] for k in ('fps', 'reached_original_sky_island', 'phase', 'failure', 'position')}
                            for r in report[name]] for name in ('before', 'after') if name in report}))


if __name__ == '__main__':
    main()
