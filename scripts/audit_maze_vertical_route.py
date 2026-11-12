"""Normal-input two-axis loop, original hidden-room contacts and return."""
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
from teleport import can_place


def run(fps, world=None):
    session = create_control_session(4, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    phase, phase_start, departure = 'west_exit', 0, 0
    trace, transitions, hops, crossings, contacts = [], [], [], [], []
    reached, failure, climb_frames = False, None, 0
    current_contacts = set()
    healing_probe, respawn_probe = None, None
    environmental_hp_loss = 0
    min_hp, min_stamina = player.hp, player.stamina
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(120 * fps):
            previous_phase = phase
            target_x, jump = 20.5, False
            keys[pygame.K_w], keys[pygame.K_s] = False, False
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
                if hops:
                    phase, target_x = 'southwest_entry', 14.5
            elif phase == 'southwest_entry':
                target_x = 14.5
                if player.on_ground and player._y < 0 and (14, 34) in current_contacts:
                    phase, target_x, jump = 'southwest_exit', 9.5, True
            elif phase == 'southwest_exit':
                target_x = 9.5
                if player.on_ground and player._y > 1 and player._x < 12:
                    phase, target_x = 'southeast_entry', -2.5
            elif phase == 'southeast_entry':
                target_x = -2.5
                if player.on_ground and player._y < 0 and (45, 34) in current_contacts:
                    healing_probe = {'time': app._game_timer, 'hp_before_test_hit': player.hp,
                                     'initial_position': player.get_center()}
                    player.take_raw_damage(50)
                    healing_probe['hp_after_test_hit'] = player.hp
                    phase, target_x = 'southeast_heal', -3.5
            elif phase == 'southeast_heal':
                target_x = -3.5
                if (44, 34) in current_contacts and player.hp >= player.hp_max:
                    healing_probe.update({'healed_time': app._game_timer, 'final_hp': player.hp,
                                          'heal_contact': [44, 34], 'healed_position': player.get_center()})
                    phase, target_x, jump = 'southeast_exit', -7.5, True
            elif phase == 'southeast_exit':
                target_x = -7.5
                if player.on_ground and player._y > 1 and player._x < -6.4:
                    phase, target_x = 'shaft_return', -27.5
            elif phase == 'shaft_return':
                target_x = -27.5
                keys[pygame.K_w] = True
                if player.is_climbing and player._y >= 22.98:
                    phase, target_x = 'west_return', -28.5
                    keys[pygame.K_w], keys[pygame.K_s] = False, True
            elif phase == 'west_return':
                target_x = -28.5
                keys[pygame.K_s] = True
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
            hp_before_advance = player.hp
            session.advance(1 / fps)
            environmental_hp_loss += max(0, hp_before_advance - player.hp)
            current_contacts = {coord for _, _, coord, _ in player._contact_tile_instances(app._current_map)}
            for coordinate in sorted(current_contacts & {(14, 34), (45, 34), (44, 34)}):
                if not any(c['coordinate'] == coordinate for c in contacts):
                    contacts.append({'time': app._game_timer, 'coordinate': coordinate,
                                     'position': player.get_center()})
            climb_frames += player.is_climbing
            if abs(player._x - before[0]) > 10:
                hops.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            elif (before[1] >= 0) != (player._y >= 0):
                crossings.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'climbing': player.is_climbing})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if phase == 'west_return' and player.on_ground and player._x < -28 and abs(player._y - 22.9) < .1:
                reached = True
                break
            if frame - phase_start > 25 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
        route_timer, route_position = app._game_timer, player.get_center()
        if reached:
            saved = tuple(player.spawn_pos)
            route_final = player.get_center()
            keys.clear()
            player.take_raw_damage(1e9)
            for _ in range(3):
                session.advance(1 / fps)
                if player.alive:
                    break
            respawn_probe = {'deliberate_lethal_test_hit': True, 'route_final_position': route_final,
                             'saved_spawn': saved, 'position': player.get_center(),
                             'alive': player.alive, 'respawns': reset.call_count - respawns,
                             'valid': can_place(player, app._current_map, *player.get_center())}
    return {'fps': fps, 'returned_after_both_rooms': reached, 'failure': failure,
            'phase': phase, 'timer': route_timer, 'control_frames': frame + 1,
            'position': route_position, 'min_hp': min_hp, 'min_stamina': min_stamina,
            'climb_input_seconds': climb_frames / fps, 'respawns': respawns,
            'environmental_hp_loss': environmental_hp_loss, 'healing_probe': healing_probe,
            'negative_checkpoint_respawn_probe': respawn_probe,
            'transitions': transitions, 'portal_hops': hops, 'vertical_crossings': crossings,
            'contacts': contacts, 'saved_checkpoint': player.spawn_pos, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--current-only', action='store_true')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '90a106a',
              'scope': 'normal spawn, T2, physical downward y-wrap to both original hidden checkpoints, jump out and shaft return; explicit 50HP test hit for heal and lethal test hit after route for negative-coordinate respawn, no position edits'}
    if not args.current_only:
        old = ModuleType('legacy_maze_vertical')
        old.__file__ = str(ROOT / 'maps/loop_maze/map.py')
        source = subprocess.check_output(['git', 'show', '90a106a:maps/loop_maze/map.py'], cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        _apply_config(old.world, 'loop_maze')
        current = get_map(4)
        report['tile_changes'] = [
            {'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
             'after': current.get_tile(x, y).type_id}
            for x, y in sorted(set(old.world.grid) | set(current.grid))
            if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
        report['before'] = [run(fps, old.world.create_session()) for fps in (30, 60, 144)]
    report['after'] = [run(fps) for fps in (30, 60, 144)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [{k: r[k] for k in ('fps', 'returned_after_both_rooms', 'phase', 'failure', 'timer', 'position')} for r in report[name]] for name in ('before', 'after') if name in report}))


if __name__ == '__main__':
    main()
