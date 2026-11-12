"""World-aware magnetic Buff behavior for existing collectible score tiles."""
import math
from pickup_effects import PickupFlight, collect_score_pickup

DEFAULT_RADIUS = 4.0
MAX_RADIUS = 16.0
SCAN_INTERVAL = .1
MAX_FLIGHTS = 64


def _short_delta(delta, period, looping):
    return (delta + period / 2) % period - period / 2 if looping else delta


def _clear_path(world, start, delta):
    def blocked(gx, gy):
        coord = world._wrap_grid_coord(gx, gy)
        return coord is None or world.get_block_type_by_coord(*coord).is_solid

    x, y = start
    dx, dy = delta
    gx, gy = math.floor(x), math.floor(y)
    end_x, end_y = math.floor(x + dx), math.floor(y + dy)
    sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
    step_x = 1 / abs(dx) if dx else math.inf
    step_y = 1 / abs(dy) if dy else math.inf
    next_x = ((gx + 1 - x) / dx if dx > 0 else (x - gx) / -dx) if dx else math.inf
    next_y = ((gy + 1 - y) / dy if dy > 0 else (y - gy) / -dy) if dy else math.inf
    # Traverse every crossed grid cell, including both sides of a corner;
    # fixed-distance sampling can miss a thin diagonal intersection.
    for _ in range(abs(end_x - gx) + abs(end_y - gy) + 3):
        if blocked(gx, gy):
            return False
        if (gx, gy) == (end_x, end_y):
            return True
        if abs(next_x - next_y) <= 1e-12:
            if blocked(gx + sx, gy) or blocked(gx, gy + sy):
                return False
            gx, gy = gx + sx, gy + sy
            next_x, next_y = next_x + step_x, next_y + step_y
        elif next_x < next_y:
            gx, next_x = gx + sx, next_x + step_x
        else:
            gy, next_y = gy + sy, next_y + step_y
    return False


def attract_pickups(actor, buff, elapsed, world):
    if world is None or not actor.alive:
        return
    buff.tick_elapsed -= elapsed
    if buff.tick_elapsed > 1e-12:
        return
    buff.tick_elapsed = SCAN_INTERVAL
    radius = float(buff.params[0]) if buff.params else DEFAULT_RADIUS
    if not math.isfinite(radius):
        return
    radius = max(0., min(MAX_RADIUS, radius))
    x, y = actor.get_center()
    seen, candidates = set(), []
    for gx in range(math.floor(x - radius), math.floor(x + radius) + 1):
        for gy in range(math.floor(y - radius), math.floor(y + radius) + 1):
            coord = world._wrap_grid_coord(gx, gy)
            if coord is None or coord in seen:
                continue
            seen.add(coord)
            kind = world.get_block_type_by_coord(*coord)
            if kind.is_solid or kind.special != 'score' or kind.special_data is None:
                continue
            consumed = kind.consumed_type_id
            if consumed is None:
                consumed = world.default_tile.type_id
            if consumed == kind.id:
                continue  # No consumable state: never repeatedly harvest a default tile.
            delta = (_short_delta(coord[0] + .5 - x, world.width, world.loop_x),
                     _short_delta(coord[1] + .5 - y, world.height, world.loop_y))
            distance = math.hypot(*delta)
            if distance <= radius + 1e-8 and _clear_path(world, (x, y), delta):
                candidates.append((distance, coord, delta))
    for distance, coord, delta in sorted(candidates):
        receipt = collect_score_pickup(actor, world, *coord)
        if receipt is None:
            continue
        flight = PickupFlight(receipt['tile_id'], (x + delta[0], y + delta[1]),
                              actor._buff_game_time, max(.08, min(.5, distance / 8)))
        actor._pickup_flights.append(flight)
    if len(actor._pickup_flights) > MAX_FLIGHTS:
        actor._pickup_flights = actor._pickup_flights[-MAX_FLIGHTS:]
