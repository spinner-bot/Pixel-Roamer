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
    from shore_exit import cancel_shore_exit
    cancel_shore_exit(actor)
    actor.is_climbing = False
    actor._x, actor._y = normalized_target(world, x, y)
    actor.reset_motion()
    actor._teleport_latched = True
    actor.collide_with_world(world, 0)
    return True


def random_teleport(actor, world, ranges, rng=None):
    """Try at most 32 bounded offsets; an impossible destination is a no-op."""
    if not isinstance(ranges, (tuple, list)) or len(ranges) != 2:
        return False
    if any(type(value) not in (int, float) for value in ranges):
        return False
    try:
        rx, ry = map(float, ranges)
    except OverflowError:
        return False
    if any(not math.isfinite(value) or value < 0 for value in (rx, ry)):
        return False
    if rng is None:
        import random
        rng = random
    for _ in range(32):
        x = actor._x + rng.uniform(-rx, rx)
        y = actor._y + rng.uniform(-ry, ry)
        if teleport_to(actor, world, x, y):
            return True
    return False
