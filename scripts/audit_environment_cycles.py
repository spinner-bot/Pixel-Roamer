"""Measure repeated altar entry, leave and respawn without integer truncation."""
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
from teleport import teleport_to


def run_cycle(base):
    world = World(0, 'altar', 30, 30, gravity=0)
    world.set_tile(5, 5, 348)
    player = Player(0, 'altar', 5.5, 6.9, {}, phys_atk=base)
    records = []
    def record(phase, boosted):
        player.collide_with_world(world, 0)
        records.append({'phase': phase, 'attack': player.phys_atk,
                        'expected': base * (2.5 if boosted else 1)})
    record('first_entry', True)
    for _ in range(10):
        player.collide_with_world(world, 0)
    record('continuous_contact', True)
    player._x = 15
    record('leave', False)
    player._x = 5.5
    record('reenter', True)
    player.reset(5.5, 6.9)
    record('after_respawn', True)
    teleport_to(player, world, 15, 6.9)
    record('teleport_out', False)
    teleport_to(player, world, 5.5, 6.9)
    record('teleport_back', True)
    return {'base_attack': base, 'records': records,
            'failures': sum(abs(row['attack'] - row['expected']) > 1e-9 for row in records)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(), 'runs': [run_cycle(base) for base in (1.25, 10, .1)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({row['base_attack']: row['failures'] for row in report['runs']}))


if __name__ == '__main__':
    main()
