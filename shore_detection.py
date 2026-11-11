"""Find every flush, full-body-clear bank within the existing shore margin."""
import math
from collision import CONTACT_EPSILON
from teleport import can_place


def shore_directions(actor, world):
    surface = getattr(actor, '_swim_top_y', None)
    if surface is None:
        return ()
    rect = actor.get_game_rect()
    result = []
    for direction in (1, -1):
        # Sample the outside of the inclusive contact boundary on both sides.
        edge = rect.x + rect.w if direction > 0 else rect.x
        gx = math.floor(edge + direction * (.2 + CONTACT_EPSILON))
        for gy in range(math.floor(surface - 1), math.floor(surface) + 1):
            coord = world._wrap_grid_coord(gx, gy)
            if coord is None:
                continue
            kind = world.get_block_type_by_coord(*coord)
            if kind.is_solid and abs(gy + 1 - surface) <= .1:
                target_x = actor._x + direction * (actor._w / 2 + .25)
                if can_place(actor, world, target_x, surface + actor._h / 2):
                    result.append(direction)
                    break
    return tuple(result)
