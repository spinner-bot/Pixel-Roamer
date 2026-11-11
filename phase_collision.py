"""Restore solid placement when existing phase or free flight ends inside terrain."""
from collision import spans_overlap
from teleport import can_place


def _embedded(actor, world):
    rect = actor.get_game_rect()
    return any(not kind.one_way
               and spans_overlap(rect.x, rect.w, block.x, block.w)
               and spans_overlap(rect.y, rect.h, block.y, block.h)
               for block, kind in world.get_nearby_solid_blocks_game(rect))


def prepare_phase_collision(actor, world):
    active = (actor.has_buff(48) or getattr(actor, '_phantom_active', False)
              or getattr(actor, 'fly_mode', False))
    previous = getattr(actor, '_phase_active', False)
    same_world = getattr(actor, '_phase_world', None) is world
    if active and (not previous or not same_world):
        actor._phase_anchor = None
        actor._phase_world = world
    if not active and previous and same_world and _embedded(actor, world):
        candidates = (getattr(actor, '_phase_anchor', None), getattr(actor, 'spawn_pos', None))
        target = next((point for point in candidates
                       if point is not None and can_place(actor, world, *point)), None)
        if target is not None:
            from shore_exit import cancel_shore_exit
            cancel_shore_exit(actor)
            actor.is_climbing = False
            actor._x, actor._y = target
            actor.reset_motion()
            actor.clear_environment_contacts(world)
    actor._phase_active = active
    if active:
        remember_phase_position(actor, world)
    else:
        actor._phase_anchor = None
        actor._phase_world = None
    return active


def remember_phase_position(actor, world):
    if can_place(actor, world, *actor.get_center()):
        actor._phase_anchor = actor.get_center()


def ghost_wall_blocks(world, rect, blocks, horizontal):
    """Buff48 passes isolated wall columns, while keeping support/ceilings.

    Query actual neighbors through the world so looping seams and defaults
    obey the same thickness rule. Vertical movement ignores a wall column
    only while the body is already traversing it, never a supporting tile.
    """
    def full_solid(x, y):
        kind = world.get_block_type(x, y)
        return kind.is_solid and not kind.one_way

    def thin(block, kind):
        return (not kind.one_way
                and not full_solid(block.x - .5, block.y + .5)
                and not full_solid(block.x + 1.5, block.y + .5))

    eligible = {(block.x, block.y) for block, kind in blocks if thin(block, kind)}
    if horizontal:
        return [(block, kind) for block, kind in blocks if (block.x, block.y) not in eligible]
    traversing = {block.x for block, kind in blocks
                  if (block.x, block.y) in eligible
                  and spans_overlap(rect.x, rect.w, block.x, block.w)
                  and spans_overlap(rect.y, rect.h, block.y, block.h)}
    return [(block, kind) for block, kind in blocks
            if block.x not in traversing or (block.x, block.y) not in eligible]
