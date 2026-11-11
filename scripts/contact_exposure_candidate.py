"""Unconnected research control: continuous same-kind contact refreshes one exposure."""
from contextlib import contextmanager
from unittest.mock import patch
from creature import Creature
import status_effects


@contextmanager
def exposure_candidate(entry_buffs=(), compound_slow=False):
    original_effects=Creature._apply_tile_effects
    original_apply=Creature.apply_buff
    original_reset=Creature.reset
    original_stat=status_effects.modified_stat
    entry_buffs=frozenset(entry_buffs)

    def contact_effects(actor,world,dt):
        ids=set(actor.contact_pool)
        if actor.stand_pool is not None:
            ids.add(actor.stand_pool)
        current={i for i in ids if i in world.block_types and world.block_types[i].buff_ids}
        previous=(getattr(actor,'_research_contact_kinds',set())
                  if getattr(actor,'_research_contact_world',None) is world else set())
        actor._research_new_kinds=current-previous
        actor._research_contact_kinds=current
        actor._research_contact_world=world
        actor._research_in_contact=True
        try:
            return original_effects(actor,world,dt)
        finally:
            actor._research_in_contact=False

    def contact_apply(actor,buff_id,params=(),duration=None,source=None,*,add_stack=True):
        old=next((b for b in actor.buffs if b.buff_id==buff_id),None)
        previous_stacks=old.stacks if old else 0
        if (buff_id in entry_buffs and getattr(actor,'_research_in_contact',False)
                and source in getattr(actor,'_research_contact_kinds',())
                and (source not in getattr(actor,'_research_new_kinds',()) or old is not None)):
            return
        result=original_apply(actor,buff_id,params,duration,source,add_stack=add_stack)
        if (old is not None and old in actor.buffs and getattr(actor,'_research_in_contact',False)
                and source in getattr(actor,'_research_contact_kinds',())
                and source not in getattr(actor,'_research_new_kinds',())):
            old.stacks=previous_stacks
        return result

    def reset(actor,*args,**kwargs):
        result=original_reset(actor,*args,**kwargs)
        actor._research_contact_kinds=set()
        actor._research_contact_world=None
        actor._research_in_contact=False
        return result

    def stat(actor,name,base):
        if not compound_slow or name != 'v_max':
            return original_stat(actor,name,base)
        saved=[]
        multiplier=1.
        try:
            for buff in actor.buffs:
                if buff.buff_type and buff.buff_type.tick in ('slowed','chilled'):
                    saved.append((buff,buff.stacks))
                    value=buff.params[0] if buff.params else 40 if buff.buff_id==51 else 50
                    multiplier*=max(0.,1-value/100)**max(0,buff.stacks-1)
                    buff.stacks=1
            return original_stat(actor,name,base)*multiplier
        finally:
            for buff,stacks in saved:
                buff.stacks=stacks

    with patch.object(status_effects,'modified_stat',stat),patch.object(Creature,'_apply_tile_effects',contact_effects), \
         patch.object(Creature,'apply_buff',contact_apply),patch.object(Creature,'reset',reset):
        yield
