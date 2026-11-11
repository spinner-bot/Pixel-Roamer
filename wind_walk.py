"""Wind-walk acceleration follows effective intent, preserving passive momentum."""
from buff_parameters import DEFAULT_PARAMETERS


def advance_wind_walk(actor,dt):
    if actor.has_buff(53):
        moving=abs(actor.v_x)>0.1
        if moving:
            actor._wind_walk_timer=getattr(actor,'_wind_walk_timer',0.)+dt
            bonus=min(actor._wind_walk_timer*.5,actor._get_buff_param(53,0,DEFAULT_PARAMETERS['wind_walk'])*actor.v_max)
            direction_basis=actor.a_x if actor.a_x!=0 else actor.v_x
            direction=1. if direction_basis>0 else -1.
            actor.v_x+=direction*bonus*dt*3
        else:
            actor._wind_walk_timer=0.
    else:
        actor._wind_walk_timer=0.
