"""Normal descent through the authored y-loop and return via existing platforms."""
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
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from maps import get_map, _apply_config
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, world=None):
    session = create_control_session(5, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    phase, phase_start = 'bottom_descent', 0
    trace, transitions, crossings = [], [], []
    reached, failure = False, None
    draws = 0
    surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    min_hp, min_stamina = player.hp, player.stamina
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(90 * fps):
            previous_phase = phase
            target_x, jump = 3.5, False
            keys[pygame.K_w], keys[pygame.K_s] = False, True
            if phase == 'bottom_descent':
                if player.on_ground and abs(player._y + 10.1) < .02:
                    phase, target_x, jump = 'upper_platform', 5.5, True
            elif phase == 'upper_platform':
                target_x = 5.5
                if player.on_ground and abs(player._y + 5.1) < .02 and abs(player._x - 5.5) < .15:
                    phase, target_x, jump = 'upward_seam', 3.5, True
            elif phase == 'upward_seam':
                if player._y >= 2.98:
                    phase, target_x = 'positive_base', 5.5
            elif phase == 'positive_base':
                target_x = 5.5
                if player.on_ground and abs(player._y - 2.9) < .02:
                    phase, target_x, jump = 'spawn_return', 10, True
            elif phase == 'spawn_return':
                target_x = 10
            if phase != previous_phase:
                transitions.append({'time': app._game_timer, 'from': previous_phase, 'to': phase,
                                    'position': player.get_center(), 'stamina': player.stamina})
                phase_start = frame
            error = max(-4, min(4, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            before = player.get_center()
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            if (before[1] >= 0) != (player._y >= 0):
                crossings.append({'time': app._game_timer, 'from': before, 'to': player.get_center()})
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                app._current_map.draw(surface, app.camera)
                draws += 1
                trace.append({'time': app._game_timer, 'phase': phase, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'on_ground': player.on_ground})
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive or player.fly_mode:
                failure = issues or 'death respawn or flight'
                break
            if phase == 'spawn_return' and player.on_ground and abs(player._x - 10) < .15 and abs(player._y - 5.9) < .02:
                reached = True
                break
            if frame - phase_start > 20 * fps:
                failure = f'{phase} timed out'
                break
        respawns = reset.call_count
    return {'fps': fps, 'returned_after_vertical_loop': reached, 'failure': failure,
            'phase': phase, 'timer': app._game_timer, 'control_frames': frame + 1,
            'position': player.get_center(), 'min_hp': min_hp, 'min_stamina': min_stamina,
            'respawns': respawns, 'transitions': transitions, 'vertical_crossings': crossings,
            'terrain_draws': draws, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--current-only', action='store_true')
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '363054d',
              'scope': 'normal spawn downward y-loop to original upper platform, upward loop and return to starting checkpoint; not full tower ascent'}
    if not args.current_only:
        old = ModuleType('legacy_climb_loop')
        old.__file__ = str(ROOT / 'maps/endless_climb/map.py')
        source = subprocess.check_output(['git', 'show', '363054d:maps/endless_climb/map.py'], cwd=ROOT, text=True, encoding='utf-8')
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        _apply_config(old.world, 'endless_climb')
        current = get_map(5)
        report['tile_changes'] = [
            {'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
             'after': current.get_tile(x, y).type_id}
            for x, y in sorted(set(old.world.grid) | set(current.grid))
            if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
        report['before'] = [run(fps, old.world.create_session()) for fps in (30, 60, 144)]
    report['after'] = [run(fps) for fps in (30, 60, 144)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [{k: r[k] for k in ('fps', 'returned_after_vertical_loop', 'phase', 'failure', 'position')}
                            for r in report[name]] for name in ('before', 'after') if name in report}))


if __name__ == '__main__':
    main()
