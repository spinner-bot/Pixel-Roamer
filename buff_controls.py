"""Query active Buff control rules without encoding source or outcome IDs."""
from buff_behavior import behavior_for


def action_blocked(actor, action):
    return any(action in behavior_for(effect.buff_id).control_locks for effect in actor.buffs)
