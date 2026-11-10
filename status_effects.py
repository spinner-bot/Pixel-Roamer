"""Time integration and numeric modifiers for the existing status catalog."""
import math
import random

from buff_system import BUFF_TYPES, CAT_NEGATIVE


def _tick_effect(actor, buff, elapsed):
    kind = buff.buff_type
    if kind is None:
        return
    params = buff.params
    value = float(params[0]) if params else None
    stacks = buff.stacks
    if kind.tick == "regen":
        actor.heal((value if value is not None else 3) * stacks * elapsed)
    elif kind.tick == "shield_regen":
        actor.add_shield((value if value is not None else 2) * stacks * elapsed)
    elif kind.tick in ("burning", "berserk", "parasitic"):
        default = 3 if kind.tick == "parasitic" else 5
        actor.take_raw_damage((value if value is not None else default) * stacks * elapsed,
                              damage_type="fire" if kind.tick == "burning" else "raw")
    elif kind.tick == "bleeding":
        rate = max(0, value if value is not None else 1) * stacks / 100
        actor.take_raw_damage(actor.hp * -math.expm1(-rate * elapsed))
    elif kind.tick == "electrified" and actor.can_swim:
        actor.take_raw_damage((value if value is not None else 8) * stacks * elapsed, damage_type="magic")
    elif kind.tick in ("cleansing", "drowsy"):
        interval = max(0.01, value if value is not None else (5 if kind.tick == "cleansing" else 4))
        buff.tick_elapsed += elapsed
        while buff.tick_elapsed + 1e-12 >= interval:
            buff.tick_elapsed = max(0, buff.tick_elapsed - interval)
            if kind.tick == "cleansing":
                negative = next((b for b in actor.buffs
                                 if b.buff_type and b.buff_type.category == CAT_NEGATIVE), None)
                if negative is not None:
                    actor.remove_buff(negative.buff_id)
            elif random.random() < 0.4:
                actor.apply_buff(28, (0.5,), 0.5)


def advance_buffs(actor, dt):
    """Integrate up to each expiry so immunity/damage ordering is deterministic."""
    if not math.isfinite(dt) or dt < 0:
        raise ValueError("buff dt must be finite and nonnegative")
    remaining = dt
    while remaining > 1e-12 and actor.buffs:
        snapshot = list(actor.buffs)
        finite_durations = [max(0, b.duration) for b in snapshot if b.duration is not None]
        step = min(remaining, min(finite_durations)) if finite_durations else remaining
        actor._buff_game_time += step
        for buff in snapshot:
            if buff in actor.buffs and actor.alive and step > 0:
                _tick_effect(actor, buff, step)
        expired = []
        for buff in snapshot:
            if buff in actor.buffs and buff.tick(step):
                expired.append(buff)
        for buff in expired:
            if buff not in actor.buffs:
                continue
            if buff.buff_type and buff.buff_type.tick == "lucky":
                negatives = [b for b in actor.buffs if b.buff_type and b.buff_type.category == CAT_NEGATIVE]
                if negatives:
                    actor.remove_buff(random.choice(negatives).buff_id)
            actor.remove_buff(buff.buff_id)
        remaining -= step
        if step == 0 and not expired:
            break
    actor._buff_game_time += remaining


_INCREASE = {
    "v_max": {"swiftness": 30}, "v_jump": {"leaping": 50},
    "stamina_recovery": {"vigor": 50}, "gravity": {"anchored": 100},
}
_DECREASE = {
    "v_max": {"slowed": 50, "chilled": 40},
    "stamina_recovery": {"fatigue": 50}, "stamina_cost": {"endurance": 30},
    "gravity": {"feather": 50}, "damage_taken": {"fortify": 30},
    "healing_received": {"grievous_wound": 50},
}


def modified_stat(actor, stat_name, base_value):
    result = base_value
    for buff in actor.buffs:
        kind = buff.buff_type
        if kind is None:
            continue
        for table, sign in ((_INCREASE, 1), (_DECREASE, -1)):
            default = table.get(stat_name, {}).get(kind.tick)
            if default is not None:
                value = float(buff.params[0]) if buff.params else default
                result *= max(0, 1 + sign * value * buff.stacks / 100)
        if stat_name == "v_max" and kind.tick == "stone_skin":
            result *= 0.4
        if stat_name == "stamina_cost" and kind.tick == "weakened":
            result *= max(0, float(buff.params[0]) if buff.params else 2)
    return result
