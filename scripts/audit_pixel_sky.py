"""Normal forest/T5 route, original sky jump boosters and the T2 return."""
from collections import defaultdict
import argparse
import hashlib
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


def run(fps, stop_at_upper_cloud=False, session=None):
    if session is None:
        session = create_control_session(3)
    app, actor, world = session.app, session.app.player1, session.app._current_map
    keys = defaultdict(bool)
    phase, phase_start = 'forest', 0
    hops, launches, transitions, trace = [], [], [], []
    reached, failure, draws = False, None, 0
    min_hp, min_stamina = actor.hp, actor.stamina
    surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for frame in range(100 * fps):
            previous_phase = phase
            target_x, jump = 70.5, False
            if phase == 'forest':
                jump = actor.on_ground and (actor.on_wall_right or actor._x > 60)
                if hops:
                    phase, target_x = 'sky_landing', 185.5
            elif phase == 'sky_landing':
                target_x = 185.5
                if actor.on_ground and abs(actor._y - 61.9) < .02:
                    phase, target_x = 'first_booster', 185.62
            elif phase in ('first_booster', 'second_booster'):
                target_x = 185.62 if phase == 'first_booster' else 190.62
                if actor.on_ground and actor.v_jump > 40 and (298 in actor.contact_pool or actor.stand_pool == 298):
                    launches.append({'phase': phase, 'time': app._game_timer,
                                     'position': actor.get_center(), 'jump_velocity': actor.v_jump,
                                     'stamina': actor.stamina})
                    phase, target_x = ('first_island', 190.5) if phase == 'first_booster' else ('lower_cloud', 196.5)
                    jump = True
            elif phase == 'first_island':
                target_x = 190.5
                if actor.on_ground and abs(actor._y - 78.9) < .02:
                    phase, target_x = 'second_booster', 190.62
            elif phase == 'lower_cloud':
                target_x = 196.5
                if actor.on_ground and abs(actor._y - 106.9) < .02:
                    phase, target_x = 'cloud_edge', 204 + actor._w / 2 + .25
            elif phase == 'cloud_edge':
                target_x = 204 + actor._w / 2 + .25
                if actor.on_ground and abs(actor._x - target_x) < .15:
                    phase, target_x, jump = 'upper_cloud', 217.5, True
            elif phase == 'upper_cloud':
                target_x = 217.5
                if actor.on_ground and abs(actor._y - 111.9) < .02:
                    if stop_at_upper_cloud:
                        reached = True
                        break
                    phase, target_x = 'sky_portal', 220.5
            elif phase == 'sky_portal':
                target_x = 220.5
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': actor.get_center(), 'stamina': actor.stamina})
                phase_start = frame
            desired = max(-6, min(6, (target_x - actor._x) * 3))
            if phase in ('first_booster', 'second_booster'):
                desired = 6  # Push against the original booster, without a feedback dead zone.
            error = desired - actor.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            before = actor.get_center()
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if abs(actor._x - before[0]) > 50:
                hops.append({'phase': phase, 'time': app._game_timer, 'from': before, 'to': actor.get_center()})
            min_hp, min_stamina = min(min_hp, actor.hp), min(min_stamina, actor.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': actor.get_center(),
                              'hp': actor.hp, 'stamina': actor.stamina,
                              'jump_velocity': actor.v_jump, 'on_ground': actor.on_ground})
            if frame % (5 * fps) == 0:
                world.draw(surface, app.camera)
                draws += 1
            issues = errors_for(session)
            if issues or reset.call_count or not actor.alive or actor.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if len(hops) == 2 and abs(actor._x - 130) < 1 and abs(actor._y - 40) < 1:
                reached = True
                break
            if frame - phase_start > 25 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'returned_to_ruins_via_original_T2': reached and not stop_at_upper_cloud,
            'stopped_on_upper_cloud': reached and stop_at_upper_cloud, 'failure': failure,
            'phase': phase, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': actor.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'body': [actor._w, actor._h],
            'production_options': {'gravity': world.gravity, 'v_jump': actor._base_v_jump,
                                   'stamina_max': actor.stamina_max, 'f_y': actor.f_y},
            'respawns': respawns, 'hops': hops, 'boosted_launches': launches,
            'transitions': transitions, 'terrain_draws': draws, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'normal forest spawn, T5, existing jump boosters and original sky T2 to ruins; no debug flight/positions or buff injection',
              'runs': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'returned_to_ruins_via_original_T2', 'phase', 'failure', 'position')}
                      for r in report['runs']]))
    if not all(r['returned_to_ruins_via_original_T2'] and r['failure'] is None for r in report['runs']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
