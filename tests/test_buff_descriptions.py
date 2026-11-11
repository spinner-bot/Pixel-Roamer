"""HUD/source descriptions must match numerical defaults and real lifetimes."""
import re
import unittest
import buff_data
from buff_system import BuffInstance
from creature import Player
from scripts.audit_buff_descriptions import run


class BuffDescriptionTests(unittest.TestCase):
    def test_every_source_uses_registered_nonempty_resolved_descriptions(self):
        result = run()
        self.assertEqual(result['buff_definitions'], 59)
        self.assertGreaterEqual(len(result['rows']), 135)
        self.assertEqual(result['issues'], [])

    def test_default_and_explicit_zero_stat_descriptions_match_effects(self):
        for buff_id, stat, sign in ((3, 'v_max', 1), (4, 'jump_height', 1),
                                    (5, 'stamina_recovery', 1), (6, 'stamina_cost', -1),
                                    (7, 'damage_taken', -1), (13, 'gravity', -1),
                                    (19, 'stamina_recovery', -1), (20, 'healing_received', -1),
                                    (22, 'v_max', -1)):
            for params in ((), (0,), (12.5,)):
                with self.subTest(buff=buff_id, params=params):
                    actor = Player(0, 'description', 0, 0, {})
                    actor.apply_buff(buff_id, params, 10)
                    instance = actor.buffs[0]
                    text = instance.format_desc()
                    value = float(re.search(r'([\d.]+)%', text).group(1))
                    self.assertAlmostEqual(actor.get_buff_stat(stat, 100), 100 + sign * value)
                    self.assertEqual(instance.params, params)

    def test_lifetime_descriptions_follow_refresh_and_do_not_claim_zero_seconds(self):
        for buff_id in (38, 48):
            for placeholder in ((), (0,), (99,)):
                buff = BuffInstance(buff_id, placeholder, 7.5)
                self.assertIn('持续 7.5 秒', buff.format_desc())
                buff.tick(3)
                self.assertIn('持续 7.5 秒', buff.format_desc())
                buff.refresh(placeholder, 12)
                self.assertIn('持续 12 秒', buff.format_desc())
                self.assertEqual(buff.params, placeholder)
            infinite = BuffInstance(buff_id, (0,), None)
            self.assertIn('持续至状态移除', infinite.format_desc())
            self.assertNotIn('{', infinite.format_desc())
