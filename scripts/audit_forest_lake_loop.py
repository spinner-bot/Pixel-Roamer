"""Normal forest controls into the lake, island rest and physical x-wrap."""
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
from shore_exit import begin_shore_exit
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps):
    session = create_control_session(6)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    trace, transitions, hops = [], [], []
    shore_exits, terrain_draws = [], 0
    surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    phase, phase_start = 'east_island', 0
    reached, crossed_x, failure = False, False, None
    min_hp, min_stamina = player.hp, player.stamina

    def observe_shore_exit(actor, **kwargs):
        stamina_before = actor.stamina
        result = begin_shore_exit(actor, **kwargs)
        if result:
            shore_exits.append({'time': app._game_timer, 'position': actor.get_center(),
                                'stamina_before': stamina_before, 'stamina_after': actor.stamina})
        return result

    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch('pixel_roamer.world_session.begin_shore_exit', side_effect=observe_shore_exit), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(100 * fps):
            previous_phase = phase
            target_x = 76.5 if phase == 'east_island' else 83.5
            if phase == 'east_island' and player.on_ground and abs(player._x - 76.5) < .15 :
                if player.stamina >= 195:
                    phase, target_x = 'across_lake_seam', 83.5
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': player.get_center(), 'stamina': player.stamina})
                phase_start = frame
            error = max(-5, min(5, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            keys[pygame.K_w] = player.can_swim and not player.on_ground
            jump = player.on_ground and player.on_wall_right
            if (player.can_swim and getattr(player, '_near_shore', False)
                    and getattr(player, '_swim_top_y', None) is not None
                    and abs(player._y - player._swim_top_y) <= .1):
                jump = True
            before = player.get_center()
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            crossed_x |= before[0] < 80 <= player._x
            if abs(player._x - before[0]) > 10:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                app._current_map.draw(surface, app.camera)
                terrain_draws += 1
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'swimming': player.can_swim,
                              'on_ground': player.on_ground, 'wall_right': player.on_wall_right})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode or hops:
                failure = issues or 'death respawn flight or unexpected portal'
                break
            if phase == 'across_lake_seam' and player.on_ground and abs(player._x - 83.5) < .15 :
                app._current_map.draw(surface, app.camera)
                terrain_draws += 1
                reached = True
                break
            if frame - phase_start > 40 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'reached_wrapped_west_island': reached, 'crossed_x_seam_physically': crossed_x,
            'failure': failure, 'phase': phase, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'transitions': transitions, 'portal_hops': hops,
            'shore_exits': shore_exits, 'terrain_draws': terrain_draws,
            'shore_pending_at_finish': getattr(player, '_shore_exit_pending', False),
            'saved_checkpoint': player.spawn_pos, 'landing_block': player.stand_pool, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal forest spawn, eastern lakeside canopy/rest then physical x seam to existing west lakeside canopy, no portal shortcut',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'reached_wrapped_west_island', 'phase', 'failure', 'position')}
                      for r in report['runs']]))


if __name__ == '__main__':
    main()
