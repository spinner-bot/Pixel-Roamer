"""Magnetic attraction that permits deliberate retreat from solid faces."""
import math


def opposed_force(force, input_acceleration):
    # Keep some resistance, but leave a net acceleration in the requested
    # direction. Limit the sum, rather than each face independently.
    if force * input_acceleration < 0:
        return math.copysign(min(abs(force), abs(input_acceleration) * .75), force)
    return force


def apply_magnetism(actor, world, types, dt):
    if world is not None and actor.has_buff(49):
        from magnetized_field import apply_field
        apply_field(actor, world, dt)
        return
    magnetic = {kind.id: kind for kind in types if kind.special == 'magnetic'
                and kind.special_data is not None}
    if not magnetic or dt <= 0:
        return
    ax = ay = 0.0
    multiplier = 2.5 if actor.has_buff(49) else 1.0
    for gx, gy, _, tile in actor._contact_tile_instances(world):
        kind = magnetic.get(tile.type_id)
        if kind is None:
            continue
        dx, dy = gx + .5 - actor._x, gy + .5 - actor._y
        distance = max(.1, math.hypot(dx, dy))
        force = float(kind.special_data) * multiplier * 10
        ax += dx / distance * force
        ay += dy / distance * force
    actor.v_x += opposed_force(ax, actor.a_x) * dt
    actor.v_y += ay * dt
