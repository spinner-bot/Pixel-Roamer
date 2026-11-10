"""Authored portal clearances, applied after scenery and random placement."""


def prepare_portal_pad(world, x, y):
    tile = world.get_tile(x, y)
    kind = world.block_types[tile.type_id]
    floor_y = y if kind.is_solid else y - 1
    for gx in range(x - 1, x + 2):
        for gy in range(floor_y + 1, floor_y + 3):
            if (gx, gy) != (x, y):
                world.set_tile(gx, gy, world.default_tile.type_id)
        if (gx, floor_y) != (x, y):
            world.set_tile(gx, floor_y, 2)
    return x + 0.5, floor_y + 1.9
