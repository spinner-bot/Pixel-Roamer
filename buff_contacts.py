"""Apply source Buffs once per continuous kind exposure, refreshing while touched."""


def clear_contact_buffs(actor):
    actor._buff_contact_world=None
    actor._buff_contact_kinds=frozenset()


def apply_contact_buffs(actor,world,types):
    current=frozenset(kind.id for kind in types if kind.buff_ids)
    previous=(getattr(actor,'_buff_contact_kinds',frozenset())
              if getattr(actor,'_buff_contact_world',None) is world else frozenset())
    entered=current-previous
    # Record before callbacks; each kind is one continuous exposure even
    # across adjacent cells and the canonical seam of a looping world.
    actor._buff_contact_world=world
    actor._buff_contact_kinds=current
    for kind in types:
        for index,buff_id in enumerate(kind.buff_ids):
            params=kind.buff_params_list[index] if index<len(kind.buff_params_list) else ()
            duration=kind.buff_durations[index] if index<len(kind.buff_durations) else None
            actor.apply_buff(buff_id,params,duration,source=kind.id,add_stack=kind.id in entered)
