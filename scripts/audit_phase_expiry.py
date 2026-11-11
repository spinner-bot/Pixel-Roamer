"""Compare solid placement on the first tick after existing phase effects expire."""
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
from creature import Player
from scripts.control_session import create_control_session
from teleport import can_place
from world import World


def measure(player_class, source, direction, fps, wall='single_layer'):
    spawn = 3.5 if direction == 1 else 60.5
    if source == 'phantom_gate':
        # Start beside the solid gate, touching its face, rather than inside it.
        spawn = 4.4 if direction == 1 else 59.6
    world = World(0, 'phase expiry fixture', 64, 16, gravity=0, spawn_points=(spawn, 5.5))
    wall_x = 8 if source == 'ghost_buff' else 31
    if direction == -1:
        wall_x = 63 - wall_x
    columns = range(5, 59) if wall == 'thick' else (wall_x,)
    for x in columns:
        for y in range(2, 10):
            world.set_tile(x, y, 19)
    if source == 'phantom_gate':
        world.set_tile(int(spawn) - direction, 5, 349)
    with patch('player_factory.Player', player_class):
        session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    if source == 'ghost_buff':
        player.apply_buff(48, (), 1)
    keys = defaultdict(bool, {pygame.K_d if direction == 1 else pygame.K_a: True})
    seen_phase, entered_wall, first_expired, last_clear = False, False, None, player.get_center()
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        # Observe every fixed tick, even when a presentation frame contains several.
        original = session._advance_step
        def observe(dt, held):
            nonlocal seen_phase, entered_wall, first_expired, last_clear
            original(dt, held)
            phased = player.has_buff(48) or getattr(player, '_phantom_active', False)
            clear = can_place(player, world, *player.get_center())
            if phased:
                seen_phase = True
                entered_wall |= not clear
                if clear:
                    last_clear = player.get_center()
            elif seen_phase and first_expired is None:
                first_expired = {'time': app._game_timer, 'position': player.get_center(),
                                 'clear': clear, 'last_clear': last_clear,
                                 'velocity': [player.v_x, player.v_y],
                                 'hp': player.hp, 'stamina': player.stamina}
        session._advance_step = observe
        for _ in range(4 * fps):
            session.advance(1 / fps)
        respawns = reset.call_count
    return {'source': source, 'direction': direction, 'fps': fps, 'wall': wall, 'entered_wall': entered_wall,
            'first_expired': first_expired, 'final_clear': can_place(player, world, *player.get_center()),
            'final_position': player.get_center(), 'respawns': respawns}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_phase_player')
    module.__file__ = str(ROOT / 'creature.py')
    source = subprocess.check_output(['git', 'show', '1db6cd2:creature.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    cases = [(source, direction, fps, wall) for source in ('ghost_buff', 'phantom_gate')
             for direction in (-1, 1) for fps in (30, 60, 144) for wall in ('single_layer', 'thick')]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '1db6cd2',
              'scope': 'isolated ability fixture with production controls; phantom uses actual tile; ghost buff granted only in fixture',
              'before': [measure(module.Player, *case) for case in cases],
              'after': [measure(Player, *case) for case in cases]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: sum(bool(r['first_expired'] and r['first_expired']['clear'])
                               for r in report[name]) for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
