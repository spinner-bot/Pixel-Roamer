"""Honor declared cleanup relations when their counter effect is accepted."""


def clear_countered_buffs(actor,counter_id):
    for effect in tuple(actor.buffs):
        kind=effect.buff_type
        if effect in actor.buffs and kind is not None and counter_id in kind.cleanup_by:
            actor.remove_buff(effect.buff_id)
