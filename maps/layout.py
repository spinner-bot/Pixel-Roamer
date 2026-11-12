"""Validated, ordered rectangle layouts for authored compact maps."""
import json
from dataclasses import replace
from pathlib import Path


def apply_layout(world, path):
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    if set(document) != {'schema_version', 'rectangles', 'palette'} or document['schema_version'] != 1:
        raise ValueError('unsupported map layout schema')
    palette = document['palette']
    if not isinstance(palette, dict):
        raise ValueError('palette must be an object')
    for key, color in palette.items():
        if (not key.isdecimal() or int(key) not in world.block_types
                or not isinstance(color, list) or len(color) != 3
                or any(type(c) is not int or not 0 <= c <= 255 for c in color)):
            raise ValueError('invalid local block color')
    rectangles = document['rectangles']
    if not isinstance(rectangles, list):
        raise ValueError('rectangles must be a list')
    # Validate the entire document before changing the supplied world.
    for rectangle in rectangles:
        if (not isinstance(rectangle, list) or len(rectangle) != 5
                or any(type(value) is not int for value in rectangle)):
            raise ValueError('rectangle must be [x0, y0, x1, y1, block_id]')
        x0, y0, x1, y1, tile_id = rectangle
        if not (0 <= x0 <= x1 < world.width and 0 <= y0 <= y1 < world.height):
            raise ValueError('rectangle outside world')
        if tile_id not in world.block_types:
            raise ValueError('unknown block id')
    # Local appearance only: never mutate shared definitions or behavior.
    world.block_types = dict(world.block_types)
    for key, color in palette.items():
        block_id = int(key)
        world.block_types[block_id] = replace(world.block_types[block_id],
                                              color=tuple(color), pattern=None)
        world._bt_fast[block_id] = world.block_types[block_id]
    world._default_bt = world.block_types[world.default_tile.type_id]
    world.fill_color = world._default_bt.color
    world.begin_bulk_load()
    try:
        for x0, y0, x1, y1, tile_id in rectangles:
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    world.set_tile(x, y, tile_id)
    finally:
        world.end_bulk_load()
