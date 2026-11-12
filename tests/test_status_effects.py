import math
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
from creature import Player


def player(**kwargs):
    return Player(0, "status", 5, 5, {}, **kwargs)


class BuffTimeTests(unittest.TestCase):
    def test_environment_timers_expire_without_any_collision_updates(self):
        for flying in (False, True):
            actor = player()
            actor.fly_mode = flying
            actor.apply_buff(28, (), 2)
            actor._confused = actor._phantom_active = True
            actor._confusion_timer = actor._phantom_timer = 0.5
            actor._special_cooldowns = {"phantom": 0.5}
            actor.tick_buffs(1)
            self.assertFalse(actor._confused)
            self.assertFalse(actor._phantom_active)
            self.assertEqual(actor._special_cooldowns, {})

    def test_periodic_cleanse_uses_instance_time_and_does_not_leak_after_reapply(self):
        actor = player()
        actor.apply_buff(12, (1,), 10)
        actor.apply_buff(22, (10,), 10)
        actor.tick_buffs(0.6)
        actor.remove_buff(12)
        actor.apply_buff(12, (1,), 10)
        actor.tick_buffs(0.4)
        self.assertTrue(actor.has_buff(22))
        actor.tick_buffs(0.6)
        self.assertFalse(actor.has_buff(22))

    def test_damage_matches_active_duration_for_short_and_long_frames(self):
        for steps in ([1], [0.1] * 10, [1 / 60] * 60):
            with self.subTest(steps=len(steps)):
                actor = player()
                actor.apply_buff(16, (8,), 1)
                for dt in steps:
                    actor.tick_buffs(dt)
                self.assertAlmostEqual(actor.hp, 92, places=7)
                self.assertFalse(actor.has_buff(16))
        actor = player()
        actor.apply_buff(16, (10,), 0.1)
        actor.tick_buffs(1)
        self.assertAlmostEqual(actor.hp, 99)

    def test_expiring_immunity_only_protects_its_active_interval(self):
        for reverse in (False, True):
            actor = player()
            buffs = [(16, (10,), 1), (36, (), 0.1)]
            for args in reversed(buffs) if reverse else buffs:
                actor.apply_buff(*args)
            actor.tick_buffs(1)
            self.assertAlmostEqual(actor.hp, 91)

    def test_regeneration_and_shield_gain_respect_elapsed_time(self):
        actor = player()
        actor.hp = 50
        actor.apply_buff(1, (8,), 1)
        actor.apply_buff(2, (4,), 1)
        actor.tick_buffs(1)
        self.assertAlmostEqual(actor.hp, 58)
        self.assertAlmostEqual(actor.shield, 4)

    def test_bleeding_is_independent_of_frame_partition(self):
        health = []
        for steps in ([1], [0.1] * 10, [1 / 60] * 60):
            actor = player()
            actor.apply_buff(17, (10,), 1)
            for dt in steps:
                actor.tick_buffs(dt)
            health.append(actor.hp)
        self.assertAlmostEqual(max(health), min(health), places=7)
        self.assertAlmostEqual(health[0], 100 * math.exp(-0.1), places=7)

    def test_stacks_affect_continuous_damage_and_stat_modifiers(self):
        actor = player()
        for _ in range(2):
            actor.apply_buff(16, (5,), 2)
            actor.apply_buff(3, (20,), 2)
        actor.tick_buffs(1)
        self.assertAlmostEqual(actor.hp, 90)
        self.assertAlmostEqual(actor.get_buff_stat("v_max", 10), 14)

    def test_invalid_time_steps_are_rejected(self):
        for dt in (-1, math.inf, math.nan):
            actor = player()
            with self.assertRaises(ValueError):
                actor.tick_buffs(dt)

    def test_reducing_stats_cannot_invert_healing_cost_or_gravity(self):
        for buff_id, stat in ((6, "stamina_cost"), (7, "damage_taken"),
                              (13, "gravity"), (19, "stamina_recovery"),
                              (20, "healing_received"), (22, "v_max")):
            actor = player()
            actor.apply_buff(buff_id, (150,), 2)
            self.assertGreaterEqual(actor.get_buff_stat(stat, 1), 0, (buff_id, stat))


class DamageTests(unittest.TestCase):
    def test_fire_resistance_blocks_actual_lava_contact(self):
        from world import World
        world = World(0, "lava", 30, 30)
        world.set_tile(5, 5, 6)
        actor = player()
        actor.apply_buff(9, (), 2)
        actor.collide_with_world(world, 1 / 60)
        self.assertEqual(actor.hp, 100)

    def test_lifesteal_and_thorns_use_actual_damage_not_requested_overkill(self):
        source = player()
        source.hp = 50
        source.apply_buff(11, (50,), 2)
        target = player(hp_max=10)
        target.apply_buff(10, (50,), 2)
        self.assertEqual(target.take_damage(1000, 0, source=source), 10)
        self.assertEqual(source.hp, 50)  # 5 reflected, then 5 healed.

    def test_damage_return_value_counts_shield_and_caps_overkill(self):
        actor = player(hp_max=10, shield=3)
        self.assertEqual(actor.take_raw_damage(5), 5)
        self.assertEqual(actor.hp, 8)
        self.assertEqual(actor.take_raw_damage(100), 8)
        self.assertFalse(actor.alive)

    def test_armor_break_is_a_victim_debuff(self):
        actor = player(phys_res=100, dr=0.5)
        actor.apply_buff(26, (), 2)
        self.assertAlmostEqual(actor.take_damage(10, 0), 10)
        source = player()
        source.apply_buff(26, (), 2)
        target = player()
        self.assertAlmostEqual(target.take_damage(10, 0, source=source), 10)

    def test_fire_resistance_blocks_burning_and_direct_fire(self):
        actor = player()
        actor.apply_buff(9, (), 2)
        actor.apply_buff(16, (10,), 1)
        actor.tick_buffs(0.5)
        self.assertEqual(actor.take_raw_damage(10, damage_type="fire"), 0)
        self.assertEqual(actor.take_damage(0, 10, damage_type="fire"), 0)
        self.assertEqual(actor.hp, 100)

    def test_capped_shield_regeneration_does_not_remove_existing_shield(self):
        actor = player(shield=100)
        self.assertEqual(actor.add_shield(2, max_shield=50), 0)
        self.assertEqual(actor.shield, 100)


if __name__ == "__main__":
    unittest.main()
