"""Check every authored portal target and trigger it from clear contact space."""
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
from maps import get_map, list_maps
from teleport import can_place
from simulation import SIMULATION_STEP


def audit():
    results = []
    for map_id in sorted(list_maps()):
        template = get_map(map_id)
        portals = [(coord, tile) for coord, tile in template.grid.items()
                   if template.block_types[tile.type_id].special == 'teleport']
        for (x, y), tile in portals:
            world = template.create_session()
            kind = world.block_types[tile.type_id]
            tx, ty = kind.special_data
            if isinstance(tile.meta, dict):
                tx, ty = tile.meta.get('tp_x', tx), tile.meta.get('tp_y', ty)
            player = None
            for px, py in ((x + .5, y + .9), (x + .5, y + 1.9),
                           (x - .4, y + .5), (x + 1.4, y + .5), (x + .5, y - .9)):
                candidate = Player(0, 'portal', px, py, {})
                if (can_place(candidate, world, px, py)
                        and any(coord == (x, y) for _, _, coord, _ in
                                candidate._contact_tile_instances(world))):
                    player = candidate
                    break
            if player is None:
                raise AssertionError(f'{map_id}/{x,y}: no clear contact position')
            if not can_place(player, world, tx, ty):
                raise AssertionError(f'{map_id}/{x,y}: obstructed target {(tx,ty)}')
            player.collide_with_world(world, 0)
            if abs(player._x - tx) > 1e-8 or abs(player._y - ty) > 1e-8:
                raise AssertionError(f'{map_id}/{x,y}: failed actual teleport {player.get_center()}')
            for _ in range(120):
                player.tick_buffs(SIMULATION_STEP)
                player.update_physics(SIMULATION_STEP, world)
                player.collide_with_world(world, SIMULATION_STEP)
                if not player.alive or not can_place(player, world, *player.get_center()):
                    raise AssertionError(f'{map_id}/{x,y}: unsafe after arrival {player.get_center()}')
            results.append({'map': map_id, 'source': [x, y, tile.type_id], 'target': [tx, ty],
                            'after_one_second': player.get_center(), 'hp': player.hp,
                            'reached_end': player._reached_end})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = audit()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
               cwd=ROOT, text=True).strip(), 'scope': 'clear targets, real triggers and one second survival; not full map routes',
              'portals': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'portals_checked': len(results), 'passed': True}))


if __name__ == '__main__':
    main()
