"""Measure complete player bounds during actual flight and collision re-entry."""
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
from scripts.control_session import create_control_session
from teleport import can_place
from world import World

SIZES = ((.2, .2), (.8, 1.8), (2., 4.), (4., 4.))
DIRECTIONS = {'left': (pygame.K_a, 0, -1), 'right': (pygame.K_d, 0, 1),
              'down': (pygame.K_s, 1, -1), 'up': (pygame.K_w, 1, 1)}


def toggle(app):
    with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)]):
        app._handle_events()


def run(fps, size, direction, loops):
    world = World(0, 'flight body bounds', 10, 10, gravity=0,
                  loop_x=loops[0], loop_y=loops[1], spawn_points=(5., 5.))
    world.player_config = dict(w=size[0], h=size[1])
    session = create_control_session(0, world=world)
    player = session.app.player1
    key, axis, sign = DIRECTIONS[direction]
    keys = defaultdict(bool, {key: True})
    with patch('pygame.key.get_pressed', return_value=keys):
        toggle(session.app)
        for _ in range(2 * fps):
            session.advance(1 / fps)
        position = player.get_center()
        rect = player.get_game_rect()
        in_bounds = ((loops[0] or (rect.x >= -1e-8 and rect.x + rect.w <= 10 + 1e-8))
                     and (loops[1] or (rect.y >= -1e-8 and rect.y + rect.h <= 10 + 1e-8)))
        expected_edge = None if loops[axis] else (size[axis] / 2 if sign < 0 else 10 - size[axis] / 2)
        keys.clear()
        toggle(session.app)
        session.advance(1 / fps)
    return {'fps': fps, 'size': size, 'direction': direction, 'loops': loops,
            'flight_position': position, 'flight_body_in_bounds': in_bounds,
            'expected_edge': expected_edge,
            'edge_matches_body': expected_edge is None or abs(position[axis] - expected_edge) < 1e-8,
            'loop_crossed': not loops[axis] or (position[axis] < 0 if sign < 0 else position[axis] > 10),
            'after_exit': player.get_center(),
            'exit_shift': max(abs(a - b) for a, b in zip(position, player.get_center())),
            'exit_clear': can_place(player, world, *player.get_center()),
            'hp': player.hp, 'stamina': player.stamina, 'alive': player.alive}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = [run(fps, size, direction, loops) for fps in (30, 60, 144) for size in SIZES
             for direction in DIRECTIONS for loops in ((False, False), (True, False), (False, True), (True, True))]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'actual flight keys and F exit, synthetic empty 10x10 worlds; not all real maps/device acceptance',
              'runs': cases}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cases': len(cases), 'body_in_bounds': sum(c['flight_body_in_bounds'] for c in cases),
                      'edge_matches': sum(c['edge_matches_body'] for c in cases),
                      'exit_no_shift': sum(c['exit_shift'] < 1e-8 for c in cases),
                      'exit_clear': sum(c['exit_clear'] for c in cases)}))


if __name__ == '__main__':
    main()
