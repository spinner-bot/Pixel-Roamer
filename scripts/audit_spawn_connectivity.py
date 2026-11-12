"""Screen local spawn geometry; every flagged pocket still needs real controls."""
from collections import deque
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map, list_maps, _apply_config
from player_factory import create_world_player
from teleport import can_place


def screen(world):
    actor = create_world_player(world, {})
    start = (round(actor._x * 10), round(actor._y * 10))
    low_x, high_x, low_y, high_y = start[0] - 50, start[0] + 50, start[1] - 50, start[1] + 50
    queue, seen = deque([start]), {start}
    boundary = False
    while queue and not boundary:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = (x + dx, y + dy)
            if point in seen or not (low_x <= point[0] <= high_x and low_y <= point[1] <= high_y):
                continue
            if can_place(actor, world, point[0] / 10, point[1] / 10):
                seen.add(point)
                queue.append(point)
                if point[0] in (low_x, high_x) or point[1] in (low_y, high_y):
                    boundary = True
                    break
    specials = {}
    if not boundary:
        for px, py in seen:
            x, y = px / 10, py / 10
            for gx in range(math.floor(x - actor._w / 2 - .01), math.floor(x + actor._w / 2 + .01 - 1e-9) + 1):
                for gy in range(math.floor(y - actor._h / 2 - .01), math.floor(y + actor._h / 2 + .01 - 1e-9) + 1):
                    coord = world._wrap_grid_coord(gx, gy)
                    if coord is None:
                        continue
                    kind = world.get_block_type_by_coord(*coord)
                    if (kind.special in ('teleport', 'ender', 'phantom') or 48 in kind.buff_ids
                            or (kind.special == 'end_point' and world.mode == 'explore')):
                        specials[coord] = {'position': coord, 'block_id': kind.id, 'special': kind.special}
    small_finite_world = ((not world.loop_x and world.width < 10 + actor._w)
                          or (not world.loop_y and world.height < 10 + actor._h))
    return {'map_id': world.map_id, 'authored_spawn': world.spawn_points, 'actual_spawn': actor.get_center(),
            'body': [actor._w, actor._h], 'samples_seen': len(seen), 'local_boundary_reached': boundary,
            'search_stopped_on_boundary': boundary, 'potential_nonlocal_exits': list(specials.values()),
            'small_finite_world': small_finite_world,
            'needs_control_audit': not boundary and not small_finite_world,
            'unexplained_closed_spawn': not boundary and not specials and not small_finite_world}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = ModuleType('known_closed_maze')
    old.__file__ = str(ROOT / 'maps/loop_maze/map.py')
    source = subprocess.check_output(['git', 'show', 'b1e1fb9:maps/loop_maze/map.py'], cwd=ROOT, text=True)
    exec(compile(source, old.__file__, 'exec'), old.__dict__)
    _apply_config(old.world, 'loop_maze')
    results = [screen(get_map(map_id)) for map_id in sorted(list_maps())]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': '0.1-cell local free-body screening within five cells, stops at first boundary; no gravity/jump/stamina proof; nonlocal exit contact is only potential',
              'legacy_maze_revision': 'b1e1fb9', 'known_closed_maze': screen(old.world),
              'maps': results, 'suspect_maps': [r['map_id'] for r in results if r['unexplained_closed_spawn']],
              'closed_with_potential_exit': [r['map_id'] for r in results
                                           if r['needs_control_audit'] and r['potential_nonlocal_exits']]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'maps': len(results), 'suspect_maps': report['suspect_maps'],
                      'known_closed_maze_detected': report['known_closed_maze']['needs_control_audit']}))


if __name__ == '__main__':
    main()
