"""Teleport placement checks: invalid targets never embed a character."""
import math
from collision import CONTACT_EPSILON, spans_overlap
from game_rect import GameRect


def normalized_target(world, x, y):
    if any(type(value) not in (int, float) for value in (x, y)):
        return None
    try:
        x, y = float(x), float(y)
    except OverflowError:
        return None
    if not math.isfinite(x) or not math.isfinite(y):
        return None
    return (x % world.width if world.loop_x else x,
            y % world.height if world.loop_y else y)


def can_place(actor, world, x, y):
    target = normalized_target(world, x, y)
    if target is None:
        return False
    x, y = target
    rect = GameRect(x - actor._w / 2, y - actor._h / 2, actor._w, actor._h)
    if not world.loop_x and not (-CONTACT_EPSILON <= rect.x
                                and rect.x + rect.w <= world.width + CONTACT_EPSILON):
        return False
    if not world.loop_y and not (-CONTACT_EPSILON <= rect.y
                                and rect.y + rect.h <= world.height + CONTACT_EPSILON):
        return False
    for obstacle, _ in world.get_nearby_solid_blocks_game(rect):
        if (spans_overlap(rect.x, rect.w, obstacle.x, obstacle.w)
                and spans_overlap(rect.y, rect.h, obstacle.y, obstacle.h)):
            return False
    return True


def teleport_to(actor, world, x, y):
    if not can_place(actor, world, x, y):
        return False
    actor._x, actor._y = normalized_target(world, x, y)
    actor.reset_motion()
    return True
