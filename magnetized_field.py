"""Bounded world-aware ore fields for active magnetized49.

Keep contact strength and opposing-input retreat. Callers retain existing
immunity checks; physical sources use their nearest loop image exactly once.
"""
import math
from environment_forces import opposed_force

RADIUS = 4.


def _delta(value, period, looping):
    return (value + period / 2) % period - period / 2 if looping else value


def apply_field(actor, world, dt):
    if dt <= 0:
        return
    x, y = actor.get_center()
    sources = {}

    def consider(coord, contact):
        if coord is None or coord in sources:
            return
        kind = world.get_block_type_by_coord(*coord)
        if kind.special != 'magnetic' or kind.special_data is None:
            return
        dx = _delta(coord[0] + .5 - x, world.width, world.loop_x)
        dy = _delta(coord[1] + .5 - y, world.height, world.loop_y)
        distance = math.hypot(dx, dy)
        if contact or distance <= RADIUS:
            sources[coord] = (kind, dx, dy, distance, contact)

    # Canonical coordinates deduplicate physical sources across loop images.
    for _, _, coord, _ in actor._contact_tile_instances(world):
        consider(coord, True)
    for gx in range(math.floor(x - RADIUS), math.floor(x + RADIUS) + 1):
        for gy in range(math.floor(y - RADIUS), math.floor(y + RADIUS) + 1):
            consider(world._wrap_grid_coord(gx, gy), False)

    ax = ay = 0.
    for kind, dx, dy, distance, contact in sources.values():
        if not distance:
            continue
        attenuation = 1.
        if not contact:
            nx, ny = abs(dx) / distance, abs(dy) / distance
            contact_distance = min((actor._w / 2 + .5) / nx if nx else math.inf,
                                   (actor._h / 2 + .5) / ny if ny else math.inf)
            # Continuous from the actor/ore contact envelope to zero at R.
            gap = max(0., distance - contact_distance)
            attenuation = max(0., 1 - gap / max(1e-8, RADIUS - contact_distance)) ** 2
        strength = float(kind.special_data) * 2.5 * 10 * attenuation
        ax += dx / max(.1, distance) * strength
        ay += dy / max(.1, distance) * strength
    actor.v_x += opposed_force(ax, actor.a_x) * dt
    if getattr(actor, '_jump_escape_active', False) and actor.v_y > 0 and ay < 0:
        # An indefinitely refreshed field must not pin a deliberate jump to
        # its source. Keep modest downward resistance during that ascent;
        # passive attraction and falling retain their ordinary field force.
        gravity = abs(world.gravity * actor.get_buff_stat('gravity', 1.))
        ay = max(ay, -.25 * gravity)
    actor.v_y += ay * dt
