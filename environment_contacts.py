"""Bound connected ladder/liquid columns from actual contact cells."""
import math


def _column_top(world, gx, gy, attribute):
    # One complete vertical period is enough to detect an endless loop column.
    for _ in range(world.height):
        coord = world._wrap_grid_coord(gx, gy + 1)
        if coord is None or not getattr(world.get_block_type_by_coord(*coord), attribute):
            return float(gy + 1)
        gy += 1
    return None


def connected_contact_tops(actor, world):
    rect = actor.get_game_rect()
    columns = {'climbable': {}, 'swim_f': {}}
    for gx in range(math.floor(rect.x - .01), math.floor(rect.x + rect.w + .01 - 1e-9) + 1):
        for gy in range(math.floor(rect.y - .01), math.floor(rect.y + rect.h + .01 - 1e-9) + 1):
            coord = world._wrap_grid_coord(gx, gy)
            if coord is None:
                continue
            kind = world.get_block_type_by_coord(*coord)
            for attribute, cells in columns.items():
                if getattr(kind, attribute):
                    cells[gx] = max(cells.get(gx, gy), gy)
    result = []
    for attribute, cells in columns.items():
        tops = [_column_top(world, gx, gy, attribute) for gx, gy in cells.items()]
        result.append(max(tops) if tops and None not in tops else None)
    return tuple(result)
