"""One canonical score-pickup transaction for contact and Buff-driven collection."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PickupFlight:
    tile_id: int
    origin: tuple
    started_at: float
    duration: float


def collect_score_pickup(actor, world, gx, gy):
    coord = world._wrap_grid_coord(gx, gy)
    if coord is None:
        return None
    tile = world.get_tile(*coord)
    kind = world.block_types.get(tile.type_id)
    if kind is None or kind.special != 'score' or kind.special_data is None:
        return None
    consumed = kind.consumed_type_id
    if consumed is None:
        consumed = world.default_tile.type_id
    # Consume the current tile before publishing its reward; a later contact
    # or a second collector must observe the consumed state.
    world.set_tile(*coord, consumed)
    points = int(kind.special_data)
    actor.score += points
    return {'tile_id': kind.id, 'points': points, 'coord': coord, 'consumed': consumed}


def prune_pickup_flights(actor):
    now = actor._buff_game_time
    actor._pickup_flights = [flight for flight in getattr(actor, '_pickup_flights', ())
                             if now - flight.started_at < flight.duration]
