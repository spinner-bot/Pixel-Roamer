"""Seeded random-portal placement geometry; finite numbers alone are insufficient."""
import argparse
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from creature import Player
from world import World
from teleport import can_place


def run_cases(count=1000):
    results = []
    for kind in (301, 358):
        world = World(0, 'random portal', 30, 30, gravity=0)
        for x in range(30):
            world.set_tile(x, 8, 2)
        world.set_tile(15, 9, kind)
        failures, outside_range, moved = [], [], 0
        rx, ry = world.block_types[kind].special_data
        for seed in range(count):
            player = Player(0, 'random portal', 15.5, 10.9, {})
            rng = Random(seed)
            with patch('random.uniform', side_effect=rng.uniform):
                player.collide_with_world(world, 0)
            if not can_place(player, world, *player.get_center()):
                failures.append({'seed': seed, 'position': player.get_center()})
            if abs(player._x - 15.5) > rx + 1e-8 or abs(player._y - 10.9) > ry + 1e-8:
                outside_range.append(seed)
            moved += abs(player._x - 15.5) + abs(player._y - 10.9) > 1e-8
        results.append({'kind': kind, 'cases': count, 'unsafe_count': len(failures),
                        'unsafe_samples': failures[:20], 'range_violations': outside_range,
                        'moved_count': moved})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(), 'runs': run_cases()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({r['kind']: r['unsafe_count'] for r in report['runs']}))


if __name__ == '__main__':
    main()
