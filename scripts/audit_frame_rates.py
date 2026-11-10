"""Measure acceleration and passive drag under identical simulated time."""
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
from creature import Player
from world import World
from simulation import FixedStepClock, SIMULATION_HZ


def measure(tile_id, fps):
    world = World(0, 'framerate', 2000, 50, gravity=-6.5)
    world.begin_bulk_load()
    for x in range(2000):
        world.set_tile(x, 8, tile_id)
    world.end_bulk_load()
    player = Player(0, 'framerate', 10.5, 9.9, {})
    player.collide_with_world(world, 0)
    clock = FixedStepClock()
    def step(dt):
        player.move(1)
        player.update_physics(dt, world)
        player.collide_with_world(world, dt)
    for _ in range(5 * fps):
        clock.advance(1 / fps, step)
    return {'tile': tile_id, 'fps': fps, 'seconds': 5,
            'distance': player._x - 10.5, 'speed': player.v_x}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = [measure(tile, fps) for tile in (2, 3, 4, 5, 23)
               for fps in (30, 60, 144)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
               cwd=ROOT, text=True).strip(), 'simulation_hz': SIMULATION_HZ, 'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
