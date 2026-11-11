"""Generic reaction metadata and exposure lifecycle, isolated from map imports."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from buff_reactions import (BuffReaction, apply_contact_reactions, clear_contact_reactions,
                            load_reactions)
from buff_system import BUFF_TYPES, BuffType, CAT_NEGATIVE
from creature import Player


def document():
    return {'schema_version': 1, 'kind': 'buff_reactions', 'entries': [
        {'id': 'fixture_cold_water', 'required_buffs': [51], 'contact': 'water',
         'result_buff': 5000, 'base_duration': 2, 'duration_multiplier': 2,
         'rearm_without': [15]}]}


RULES = {'fixture_cold_water': BuffReaction((51,), 'water', 5000, 2, 2, (15,))}


class BuffReactionTests(unittest.TestCase):
    def setUp(self):
        self.definition = patch.dict(BUFF_TYPES, {
            5000: BuffType(5000, 'fixture_frozen', category=CAT_NEGATIVE, cleanup_by=(40,))})
        self.definition.start()
        self.addCleanup(self.definition.stop)

    def actor(self):
        actor = Player(0, 'reaction fixture', 0, 0, {})
        actor.apply_buff(51, (), None)
        actor.apply_buff(15, (), None)
        return actor

    def test_loader_rejects_bad_references_types_duplicates_and_numeric_products(self):
        mutations = {
            'duplicate': lambda d: d['entries'].append(deepcopy(d['entries'][0])),
            'id_type': lambda d: d['entries'][0].update(id=1),
            'id_empty': lambda d: d['entries'][0].update(id=' '),
            'unknown_required': lambda d: d['entries'][0].update(required_buffs=[9999]),
            'duplicate_required': lambda d: d['entries'][0].update(required_buffs=[51, 51]),
            'bool_required': lambda d: d['entries'][0].update(required_buffs=[True]),
            'empty_required': lambda d: d['entries'][0].update(required_buffs=[]),
            'unknown_result': lambda d: d['entries'][0].update(result_buff=9999),
            'bool_result': lambda d: d['entries'][0].update(result_buff=True),
            'unknown_rearm': lambda d: d['entries'][0].update(rearm_without=[9999]),
            'contact_unknown': lambda d: d['entries'][0].update(contact='lava'),
            'contact_list': lambda d: d['entries'][0].update(contact=[]),
            'zero_duration': lambda d: d['entries'][0].update(base_duration=0),
            'bool_duration': lambda d: d['entries'][0].update(base_duration=True),
            'nan_duration': lambda d: d['entries'][0].update(base_duration=math.nan),
            'negative_multiplier': lambda d: d['entries'][0].update(duration_multiplier=-2),
            'huge_integer': lambda d: d['entries'][0].update(base_duration=10 ** 400),
            'overflow_product': lambda d: d['entries'][0].update(base_duration=1e308, duration_multiplier=2),
            'underflow_product': lambda d: d['entries'][0].update(base_duration=1e-300, duration_multiplier=1e-300),
            'extra_field': lambda d: d['entries'][0].update(source_block=373),
            'bool_version': lambda d: d.update(schema_version=True),
            'header': lambda d: d.update(kind='buffs'),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rules.json'
            for name, mutate in mutations.items():
                with self.subTest(name=name):
                    changed = document()
                    mutate(changed)
                    path.write_text(json.dumps(changed))
                    with self.assertRaises(ValueError):
                        load_reactions(path, known_ids={51, 15, 5000})
            path.write_text(json.dumps(document()))
            loaded = load_reactions(path, known_ids={51, 15, 5000})
            self.assertEqual(loaded['fixture_cold_water'].duration, 4)
            with self.assertRaises(TypeError):
                loaded['other'] = loaded['fixture_cold_water']
            with self.assertRaises(FrozenInstanceError):
                loaded['fixture_cold_water'].base_duration = 10

    def test_contact_jitter_does_not_refresh_or_rearm_until_completely_dry(self):
        actor, world = self.actor(), object()
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        effect = next(b for b in actor.buffs if b.buff_id == 5000)
        effect.duration = 1.5
        for contacts in (set(), {'water'}, set(), {'water'}):
            apply_contact_reactions(actor, world, contacts, rules=RULES)
            self.assertEqual(effect.duration, 1.5)
        actor.remove_buff(5000)
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertFalse(actor.has_buff(5000))
        actor.remove_buff(15)
        apply_contact_reactions(actor, world, set(), rules=RULES)
        actor.apply_buff(15, (), None)
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertTrue(actor.has_buff(5000))

    def test_immune_rejection_consumes_exposure_and_world_reset_rearms(self):
        actor, world = self.actor(), object()
        actor.apply_buff(40, (), None)
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertFalse(actor.has_buff(5000))
        actor.remove_buff(40)
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertFalse(actor.has_buff(5000))
        apply_contact_reactions(actor, object(), {'water'}, rules=RULES)
        self.assertTrue(actor.has_buff(5000))
        actor.remove_buff(5000)
        clear_contact_reactions(actor)
        self.assertEqual(actor._buff_reaction_latches, set())
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertTrue(actor.has_buff(5000))

    def test_no_contact_or_required_buff_no_reaction_and_longer_effect_not_shortened(self):
        for duration in (None, 10, 1):
            actor, world = self.actor(), object()
            actor.apply_buff(5000, (), duration)
            apply_contact_reactions(actor, world, {'water'}, rules=RULES)
            effect = next(b for b in actor.buffs if b.buff_id == 5000)
            self.assertEqual(effect.duration, 4 if duration == 1 else duration)
        actor, world = self.actor(), object()
        apply_contact_reactions(actor, world, set(), rules=RULES)
        self.assertFalse(actor.has_buff(5000))
        actor.remove_buff(51)
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertFalse(actor.has_buff(5000))
        actor.apply_buff(51, (), None)
        actor.alive = False
        apply_contact_reactions(actor, world, {'water'}, rules=RULES)
        self.assertFalse(actor.has_buff(5000))
