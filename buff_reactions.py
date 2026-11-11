"""Validated Buff/contact reactions with one attempt per complete exposure."""
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
from types import MappingProxyType

REACTION_PATH = Path(__file__).resolve().parent / 'data/rules/buff_reactions.json'
CONTACTS = frozenset({'water'})


@dataclass(frozen=True)
class BuffReaction:
    required_buffs: tuple
    contact: str
    result_buff: int
    base_duration: float
    duration_multiplier: float
    rearm_without: tuple

    @property
    def duration(self):
        return self.base_duration * self.duration_multiplier


def load_reactions(path=REACTION_PATH, *, known_ids=None):
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    if (not isinstance(document, dict) or set(document) != {'schema_version', 'kind', 'entries'}
            or type(document['schema_version']) is not int or document['schema_version'] != 1
            or document['kind'] != 'buff_reactions' or not isinstance(document['entries'], list)):
        raise ValueError('invalid Buff reaction header')
    if known_ids is None:
        from resource_catalog import load_buffs
        known_ids = load_buffs().keys()
    result = {}
    fields = {'id', 'required_buffs', 'contact', 'result_buff', 'base_duration',
              'duration_multiplier', 'rearm_without'}
    for entry in document['entries']:
        if (not isinstance(entry, dict) or set(entry) != fields
                or not isinstance(entry['id'], str) or not entry['id'].strip()
                or entry['id'] in result or entry['contact'] not in CONTACTS
                or type(entry['result_buff']) is not int or entry['result_buff'] not in known_ids):
            raise ValueError('invalid or duplicate Buff reaction')
        for field in ('required_buffs', 'rearm_without'):
            values = entry[field]
            if (not isinstance(values, list) or not values
                    or any(type(value) is not int or value not in known_ids for value in values)
                    or len(set(values)) != len(values)):
                raise ValueError('invalid reaction Buff references')
        for field in ('base_duration', 'duration_multiplier'):
            value = entry[field]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('reaction durations must be finite and positive')
        rule = BuffReaction(tuple(entry['required_buffs']), entry['contact'], entry['result_buff'],
                            float(entry['base_duration']), float(entry['duration_multiplier']),
                            tuple(entry['rearm_without']))
        if not math.isfinite(rule.duration):
            raise ValueError('reaction duration product must be finite')
        result[entry['id']] = rule
    return MappingProxyType(result)


@lru_cache(maxsize=1)
def contact_reactions():
    return load_reactions()


def clear_contact_reactions(actor):
    actor._buff_reaction_world = None
    actor._buff_reaction_latches = set()


def apply_contact_reactions(actor, world, contacts, *, rules=None):
    rules = contact_reactions() if rules is None else rules
    if getattr(actor, '_buff_reaction_world', None) is not world:
        clear_contact_reactions(actor)
        actor._buff_reaction_world = world
    latches = actor._buff_reaction_latches
    latches.intersection_update(rules)
    if not actor.alive:
        return
    for key, rule in rules.items():
        contact = rule.contact in contacts
        if not contact and not any(actor.has_buff(buff_id) for buff_id in rule.rearm_without):
            latches.discard(key)
        if key in latches or not contact or not all(actor.has_buff(i) for i in rule.required_buffs):
            continue
        # An immune/rejected acquisition consumes this exposure too. Losing
        # immunity while still immersed must not cause a delayed surprise lock.
        latches.add(key)
        existing = next((b for b in actor.buffs if b.buff_id == rule.result_buff), None)
        if existing is not None and (existing.duration is None or existing.duration >= rule.duration):
            continue
        actor.apply_buff(rule.result_buff, (), rule.duration, source=f'reaction:{key}')
