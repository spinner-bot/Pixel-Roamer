"""Screen normal-body contact candidates, without asserting route reachability."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map, list_maps
from player_factory import create_world_player
from teleport import can_place

FEATURES = ('checkpoint', 'set_spawn', 'teleport', 'heal', 'shield', 'score', 'end_point')


def contact_pose(world, actor, coordinate):
    x, y = coordinate
    def axis(origin, half):
        low, high = origin - half - .01, origin + 1 + half + .01
        return sorted({q / 10 for q in range(math.ceil(low * 10), math.floor(high * 10) + 1)}
                      | {origin - half, origin + .5, origin + 1 + half})
    original = actor.get_center()
    try:
        for cx in axis(x, actor._w / 2):
            for cy in axis(y, actor._h / 2):
                actor._x, actor._y = cx, cy
                if (can_place(actor, world, cx, cy)
                        and any(coord == coordinate for _, _, coord, _ in actor._contact_tile_instances(world))):
                    return [cx, cy]
    finally:
        actor._x, actor._y = original
    return None


def inspect_world(world):
    actor = create_world_player(world, {})
    features, phase_sources = [], []
    for coordinate, tile in sorted(world.grid.items()):
        kind = world.block_types[tile.type_id]
        if kind.special == 'phantom' or 48 in kind.buff_ids:
            phase_sources.append({'position': coordinate, 'block_id': kind.id})
        if kind.special not in FEATURES:
            continue
        features.append({'position': coordinate, 'block_id': kind.id, 'special': kind.special,
                         'normal_contact_pose': contact_pose(world, actor, coordinate)})
    return {'map_id': world.map_id, 'body': [actor._w, actor._h], 'feature_count': len(features),
            'phase_sources': phase_sources, 'features': features,
            'no_normal_contact': [f for f in features if f['normal_contact_pose'] is None]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maps', type=int, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'sampled normal full-body placement plus real contact sampler; not controls/route proof; phase-enabled access not modeled',
              'maps': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for map_id in args.maps or sorted(list_maps()):
        result = inspect_world(get_map(map_id))
        report['maps'].append(result)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'map_id': map_id, 'features': result['feature_count'],
                          'no_normal_contact': len(result['no_normal_contact'])}), flush=True)


if __name__ == '__main__':
    main()
