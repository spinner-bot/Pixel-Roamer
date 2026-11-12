"""Surface-only rise/slide sequence with explicit completion and cancellation."""
from collision import CONTACT_EPSILON
from teleport import can_place
from buff_controls import action_blocked


def cancel_shore_exit(actor):
    state = getattr(actor, '_shore_exit_pending', False)
    if state:
        actor.v_x = 0.0
        if state == 'rise':
            actor.v_y = min(0.0, actor.v_y)
    actor._shore_exit_pending = False


def begin_shore_exit(actor, suppress_cost=False, preferred_direction=0):
    if action_blocked(actor, 'jump') or action_blocked(actor, 'swim'):
        return False
    surface = getattr(actor, '_swim_top_y', None)
    if (not actor.can_swim or actor.is_climbing or surface is None
            or not getattr(actor, '_near_shore', False)
            or abs(actor._y - surface) > .1
            or getattr(actor, '_shore_exit_pending', False)
            or actor.stamina < 25):
        return False
    actor.v_y = 32.0
    actor.v_x = 0.0
    if not suppress_cost:
        actor.consume_stamina(25)
    actor.apply_buff(58, (), .3)
    actor._shore_exit_pending = 'rise'
    directions = getattr(actor, '_shore_directions', ())
    actor._shore_exit_dir = (preferred_direction if preferred_direction in directions
                            else actor._shore_dir)
    actor._shore_exit_bound = surface
    return True


def advance_shore_exit(actor, world=None):
    state = getattr(actor, '_shore_exit_pending', False)
    if not state:
        return
    if action_blocked(actor, 'jump') or action_blocked(actor, 'swim'):
        cancel_shore_exit(actor)
        return
    if not actor.has_buff(58):
        cancel_shore_exit(actor)
        return
    if state == 'rise':
        surface = actor._shore_exit_bound
        if actor._y - actor._h / 2 >= surface - CONTACT_EPSILON:
            target_y = surface + actor._h / 2
            if world is not None and not can_place(actor, world, actor._x, target_y):
                cancel_shore_exit(actor)
                return
            actor._y = target_y
            actor.v_y = 0.0
            actor.v_x = actor._shore_exit_dir * 16.0
            actor._shore_slide_start_x = actor._x
            actor._shore_exit_pending = 'slide'
    elif state == 'slide':
        distance = actor._w / 2 + .25
        if abs(actor._x - actor._shore_slide_start_x) >= distance - CONTACT_EPSILON:
            cancel_shore_exit(actor)
        elif world is not None:
            # Hold the feet at the lip until horizontal motion reaches support.
            # A fractional fall here turns the next horizontal sweep into a wall.
            target_y = actor._shore_exit_bound + actor._h / 2
            if not can_place(actor, world, actor._x, target_y):
                cancel_shore_exit(actor)
                return
            actor._y = target_y
            actor.v_y = 0.0


def after_shore_physics(actor, world=None):
    state = getattr(actor, '_shore_exit_pending', False)
    if state == 'rise' and (actor.on_ceiling or actor.on_ground):
        cancel_shore_exit(actor)
    else:
        advance_shore_exit(actor, world)
