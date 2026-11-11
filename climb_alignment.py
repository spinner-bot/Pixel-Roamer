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
    if not can_place(actor, world, next_x, actor._y):
        # A changed wall may invalidate an already selected destination.
        _cancel(actor)
        return
    actor._x = next_x
    if abs(target - next_x) <= CONTACT_EPSILON:
        actor._climb_align_target = None
