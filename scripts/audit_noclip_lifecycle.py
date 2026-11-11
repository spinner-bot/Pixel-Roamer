"""Placement safety when collision resumes independently of voluntary movement."""
from collections import defaultdict
from contextlib import ExitStack
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
from pixel_roamer.world_session import WorldSession
from scripts.control_session import create_control_session
from teleport import can_place
from world import World

CASES = ('flight_embedded', 'flight_clear', 'ghost_stunned', 'ghost_dispelled_stunned', 'flight_stunned')


def measure(session_class, case, fps, legacy_phase=None):
    world = World(0, 'noclip lifecycle', 20, 20, gravity=0, spawn_points=(3.5, 5.5))
    for x in range(5, 9):
        for y in range(3, 9):
            world.set_tile(x, y, 19)
    keys = defaultdict(bool, {pygame.K_d: True})
    with ExitStack() as stack:
        stack.enter_context(patch('scripts.control_session.WorldSession', session_class))
        if legacy_phase:
            for name in ('prepare_phase_collision', 'remember_phase_position'):
                stack.enter_context(patch(f'phase_collision.{name}', getattr(legacy_phase, name)))
        session = create_control_session(0, world=world)
        app, player = session.app, session.app.player1
        stack.enter_context(patch('pygame.key.get_pressed', return_value=keys))
        reset = stack.enter_context(patch.object(player, 'reset', wraps=player.reset))
        if case.startswith('flight'):
            with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)]):
                app._handle_events()
        else:
            player.apply_buff(48, (), 1)
        changed, stunned, first_after_change, before_change = False, False, None, None
        original = session._advance_step
        def observe(dt, held):
            nonlocal first_after_change
            original(dt, held)
            if changed and first_after_change is None:
                first_after_change = {'time': app._game_timer, 'position': player.get_center(),
                                      'clear': can_place(player, world, *player.get_center())}
        session._advance_step = observe
        for frame in range(int(1.1 * fps) + 1):
            elapsed = frame / fps
            stun_at = .2 if case == 'flight_stunned' else .75
            if (case.endswith('stunned') and not stunned and elapsed >= stun_at - 1e-9):
                player.apply_buff(28, (), 2)
                stunned = True
            change_at = .125 if case == 'flight_clear' else (.25 if case.startswith('flight') else
                         (.8 if case == 'ghost_dispelled_stunned' else 1.))
            if not changed and elapsed >= change_at - 1e-9:
                before_change = {'position': player.get_center(), 'clear': can_place(player, world, *player.get_center())}
                if case.startswith('flight'):
                    with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)]):
                        app._handle_events()
                elif case == 'ghost_dispelled_stunned':
                    player.remove_buff(48)
                changed = True
            session.advance(1 / fps)
        result = {'case': case, 'fps': fps, 'before_change': before_change,
                  'first_after_change': first_after_change, 'final_position': player.get_center(),
                  'final_clear': can_place(player, world, *player.get_center()),
                  'stunned': player.has_buff(28), 'ghost': player.has_buff(48), 'flight': player.fly_mode,
                  'hp': player.hp, 'stamina': player.stamina, 'respawns': reset.call_count}
    return result


def legacy_module(filename, name):
    module = ModuleType(name)
    module.__file__ = str(ROOT / filename)
    source = subprocess.check_output(['git', 'show', f'913eb87:{filename}'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old_session = legacy_module('pixel_roamer/world_session.py', 'legacy_noclip_session')
    old_phase = legacy_module('phase_collision.py', 'legacy_noclip_phase')
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '913eb87',
              'scope': 'isolated legal-spawn lifecycle fixtures; real flight toggle/control; existing buffs deliberately granted in fixtures',
              'before': [measure(old_session.WorldSession, case, fps, old_phase) for case in CASES for fps in (30, 60, 144)],
              'after': [measure(WorldSession, case, fps) for case in CASES for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: sum(r['final_clear'] for r in report[name]) for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
