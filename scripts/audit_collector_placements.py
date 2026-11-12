"""Compare authored feature placement against both background air kinds."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map, list_maps
from maps.placement import is_air_cell, load_feature_plan
from player_factory import create_world_player
from scripts.control_session import available_score
from teleport import can_place
PLAN = ROOT / 'maps' / list_maps()[9] / 'features.json'


def inspect_world(world):
    points, reserved = load_feature_plan(world, PLAN)
    missed, placed, occupied = [], [], []
    for x, y, expected in points:
        actual = world.get_tile(x, y).type_id
        entry = {'x': x, 'y': y, 'expected': expected, 'actual': actual}
        if actual == expected:
            placed.append(entry)
        elif is_air_cell(world, x, y):
            missed.append(entry)
        else:
            occupied.append(entry)
    player = create_world_player(world, {}, position=(13.5, 18.9))
    return {'default_tile': world.default_tile.type_id, 'missed_on_air': missed,
            'placed': placed, 'occupied_preserved': occupied,
            'crystal_count': sum(tile.type_id in (200, 201, 204, 206) for tile in world.grid.values()),
            'available_score': available_score(world),
            'reserved_solid_cells': [[x, y] for x, y in sorted(reserved) if world.get_block_type(x, y).is_solid],
            'entrance_body_clear': can_place(player, world, *player.get_center())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_collector_placements')
    module.__file__ = str(ROOT / 'maps/collector/map.py')
    source = subprocess.check_output(['git', 'show', '6b0908f:maps/collector/map.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy_revision': '6b0908f', 'scope': 'feature placement and local entrance clearance; full control route tested separately',
              'before': inspect_world(module.world), 'after': inspect_world(get_map(9))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: {'missed': len(report[name]['missed_on_air']),
                           'crystals': report[name]['crystal_count'],
                           'score': report[name]['available_score']} for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
