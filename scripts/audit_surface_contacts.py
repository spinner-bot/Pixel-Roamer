"""Measure nearby disconnected cells incorrectly influencing surface bounds."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import types
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from world import World
from creature import Player
LEGACY_REF = '8400f34'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    actor_class = Player
    if args.legacy:
        source = subprocess.check_output(['git', 'show', f'{LEGACY_REF}:creature.py'], cwd=ROOT, text=True, encoding='utf-8')
        module = types.ModuleType('legacy_creature_surface_audit')
        sys.modules[module.__name__] = module
        exec(compile(source, f'git:{LEGACY_REF}:creature.py', 'exec'), module.__dict__)
        actor_class = module.Player
    results = []
    for kind in (7, 9):
        world = World(0, 'layers', 20, 20, gravity=0)
        for y in range(1, 6):
            world.set_tile(5, y, kind)
            world.set_tile(4, y, 2)
        world.set_tile(6, 7, kind)
        player = actor_class(0, 'layers', 5.5, 5.7, {})
        player.collide_with_world(world, 0)
        results.append({'kind': kind, 'expected_top': 6,
                        'actual_top': player._swim_top_y if kind == 7 else player._climb_top_y,
                        'near_shore': player._near_shore})
    report = {'actor_revision': LEGACY_REF if args.legacy else subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
