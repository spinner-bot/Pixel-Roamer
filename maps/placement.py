"""Validated optional map features and air checks that preserve invisible walls."""
import json
from pathlib import Path

# 13/14/15 look like air but are solid boundary blocks, not empty space.
_AIR_IDS = frozenset((0, 11, 12))


def is_air_cell(world, x, y):
    kind = world.get_block_type(x, y)
    return kind is not None and kind.id in _AIR_IDS and not kind.is_solid


def load_feature_plan(world, path):
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    if (not isinstance(document, dict)
            or document.keys() != {'schema_version', 'map_id', 'points', 'reserved_rectangles'}
            or type(document['schema_version']) is not int or document['schema_version'] != 1
            or type(document['map_id']) is not int or document['map_id'] != world.map_id):
        raise ValueError('invalid feature plan header')
    if not isinstance(document['points'], list) or not isinstance(document['reserved_rectangles'], list):
        raise ValueError('feature points and reserved rectangles must be lists')
    points, seen, reserved = [], set(), set()
    for point in document['points']:
        if not isinstance(point, list) or len(point) != 3 or any(type(v) is not int for v in point):
            raise ValueError('feature point must be [x, y, block_id]')
        x, y, tile_id = point
        if not (0 <= x < world.width and 0 <= y < world.height) or tile_id not in world.block_types:
            raise ValueError('feature point outside world or unknown block')
        if (x, y) in seen:
            raise ValueError('duplicate feature point')
        seen.add((x, y))
        points.append((x, y, tile_id))
    for rectangle in document['reserved_rectangles']:
        if not isinstance(rectangle, list) or len(rectangle) != 4 or any(type(v) is not int for v in rectangle):
            raise ValueError('reserved rectangle must be [x0, y0, x1, y1]')
        x0, y0, x1, y1 = rectangle
        if not (0 <= x0 <= x1 < world.width and 0 <= y0 <= y1 < world.height):
            raise ValueError('reserved rectangle outside world')
        reserved.update((x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
    # Only return after validating the whole document; never mutate the map here.
    return tuple(points), frozenset(reserved)
