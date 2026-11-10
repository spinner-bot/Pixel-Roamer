"""Surface-only rise/slide sequence with explicit completion and cancellation."""
from collision import CONTACT_EPSILON


def cancel_shore_exit(actor):
    state = getattr(actor, '_shore_exit_pending', False)
    if state:
        actor.v_x = 0.0
        if state == 'rise':
            actor.v_y = min(0.0, actor.v_y)
    actor._shore_exit_pending = False


def begin_shore_exit(actor, suppress_cost=False):
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
    actor._shore_exit_dir = actor._shore_dir
    actor._shore_exit_bound = surface
    return True


def advance_shore_exit(actor):
    state = getattr(actor, '_shore_exit_pending', False)
    if not state:
        return
    if not actor.has_buff(58):
        cancel_shore_exit(actor)
        return
    if state == 'rise':
        surface = actor._shore_exit_bound
        if actor._y - actor._h / 2 >= surface - CONTACT_EPSILON:
            actor._y = surface + actor._h / 2
            actor.v_y = 0.0
            actor.v_x = actor._shore_exit_dir * 16.0
            actor._shore_slide_start_x = actor._x
            actor._shore_exit_pending = 'slide'
    elif state == 'slide':
        distance = actor._w / 2 + .25
        if abs(actor._x - actor._shore_slide_start_x) >= distance - CONTACT_EPSILON:
            cancel_shore_exit(actor)


def after_shore_physics(actor):
    state = getattr(actor, '_shore_exit_pending', False)
    if state == 'rise' and (actor.on_ceiling or actor.on_ground):
        cancel_shore_exit(actor)
    else:
        advance_shore_exit(actor)
