"""Center a captured climber gradually, using full-body placement checks."""
import math
from collision import CONTACT_EPSILON
from teleport import can_place

ALIGN_SPEED = 6.0


def _cancel(actor):
    actor._climb_align_target = None
    actor.is_climbing = False
    actor.v_x = actor.v_y = 0.0


def advance_climb_alignment(actor, world, dt):
    target = getattr(actor, '_climb_align_target', None)
    if target is None:
        return
    if not actor.is_climbing:
        actor._climb_align_target = None
        return
    if not math.isfinite(target) or not math.isfinite(actor._x):
        _cancel(actor)
        return
    if not math.isfinite(dt) or dt <= 0:
        return
    delta = target - actor._x
    if abs(delta) > actor._w / 2 + .51 + CONTACT_EPSILON:
        _cancel(actor)
        return
    distance = min(abs(delta), ALIGN_SPEED * dt)
    next_x = target if distance == abs(delta) else actor._x + math.copysign(distance, delta)
    if abs(target - next_x) <= CONTACT_EPSILON:
        next_x = target
    if not can_place(actor, world, next_x, actor._y):
        # A changed wall may invalidate an already selected destination.
        _cancel(actor)
        return
    actor._x = next_x
    if abs(target - next_x) <= CONTACT_EPSILON:
        actor._climb_align_target = None


def hold_climb_top(actor, world, dt):
    """Settle near the finite ladder cap without snapping or entering a ledge.

    Return True while holding/settling at the top so upward input does not
    compete with the alignment. Pending horizontal alignment may need to
    finish before lowering a tall body beside a ledge.
    """
    bound = getattr(actor, '_climb_top_y', None)
    if bound is None or not actor.is_climbing:
        return False
    if not math.isfinite(bound) or not math.isfinite(actor._y):
        actor.stop_climbing()
        return False
    if not bound - .05 <= actor._y <= bound + 2.0:
        return False
    if not math.isfinite(dt) or dt <= 0:
        return False
    pending_x = getattr(actor, '_climb_align_target', None)
    endpoint_x = actor._x if pending_x is None else pending_x
    if not can_place(actor, world, endpoint_x, bound):
        actor.stop_climbing()
        return False
    delta = bound - actor._y
    distance = min(abs(delta), ALIGN_SPEED * dt)
    next_y = bound if distance == abs(delta) else actor._y + math.copysign(distance, delta)
    if abs(bound - next_y) <= CONTACT_EPSILON:
        next_y = bound
    actor.v_y = 0.0
    if can_place(actor, world, actor._x, next_y):
        actor._y = next_y
    elif pending_x is None:
        actor.stop_climbing()
        return False
    return True
