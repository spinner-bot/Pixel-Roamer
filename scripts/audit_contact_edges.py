"""Coordinate translation, ladder placement and same-type metadata probes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from world import World
from creature import Player
from teleport import can_place


def audit():
    shores = []
    for side, x, shore_x, direction in [('left', 1.45, 0, -1), ('right', 8.55, 9, 1)]:
        world = World(0, 'shore', 10, 20, loop_x=True, loop_y=True, gravity=0)
        for gx in range(1, 9):
            for gy in range(1, 6):
                world.set_tile(gx, gy, 7)
        for gy in range(1, 6):
            world.set_tile(shore_x, gy, 2)
        for dx in (0, -10, 10, -100000, 100000):
            for dy in (0, -20, 20):
                player = Player(0, 'shore', x + dx, 5.7 + dy, {})
                player.collide_with_world(world, 0)
                passed = player.can_swim and player._near_shore and player._shore_dir == direction
                shores.append({'side': side, 'shift': [dx, dy], 'near_shore': player._near_shore,
                               'direction': player._shore_dir, 'passed': passed})
    world = World(0, 'ladder', 20, 20, gravity=0)
    world.set_tile(5, 5, 9)
    world.set_tile(5, 6, 2)
    player = Player(0, 'ladder', 6.4, 5.7, {})
    player.collide_with_world(world, 0)
    before = player.get_center()
    started = player.try_start_climbing(world)
    climb = {'before': before, 'after': player.get_center(), 'started': started,
             'embedded': not can_place(player, world, *player.get_center())}
    world = World(0, 'metadata', 30, 30)
    world.set_tile(5, 5, 300, {'tp_x': 12, 'tp_y': 10})
    world.set_tile(5, 5, 300, {'tp_x': 22, 'tp_y': 20})
    metadata = {'expected': {'tp_x': 22, 'tp_y': 20}, 'actual': world.get_tile(5, 5).meta}
    return {'shores': shores, 'shore_failures': sum(not case['passed'] for case in shores),
            'climb': climb, 'metadata': metadata}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(), **audit()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('shore_failures', 'climb', 'metadata')}))


if __name__ == '__main__':
    main()
