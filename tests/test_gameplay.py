"""Deterministic gameplay regressions using small, isolated worlds."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from block_type import BlockType
from creature import Player
from world import World


def make_world(**kwargs):
    return World(0, "regression", 40, 30, gravity=0,
                 edge_behavior="void", **kwargs)


def make_player(x=5.5, y=5.5):
    return Player(0, "regression", x, y, {})


class EnvironmentTests(unittest.TestCase):
    def test_leaving_water_and_ladder_clears_contact_state(self):
        for tile_id, state in ((7, "can_swim"), (9, "can_climb")):
            with self.subTest(tile_id=tile_id):
                world = make_world()
                world.set_tile(5, 5, tile_id)
                player = make_player()
                player.collide_with_world(world, 0)
                self.assertTrue(getattr(player, state))
                player._x = 20
                player.collide_with_world(world, 1 / 60)
                self.assertFalse(getattr(player, state))
                self.assertEqual(player._swim_force, 0)
                self.assertIsNone(player._climb_top_y)
                self.assertIsNone(player._swim_top_y)

    def test_temporary_effects_expire_in_empty_air(self):
        for tile_id, state in ((349, "_phantom_active"), (353, "_confused")):
            with self.subTest(tile_id=tile_id):
                world = make_world()
                world.set_tile(5, 5, tile_id)
                player = make_player()
                player.collide_with_world(world, 0)
                self.assertTrue(getattr(player, state))
                player._x = 20
                for _ in range(601):
                    player.collide_with_world(world, 1 / 60)
                self.assertFalse(getattr(player, state))
                self.assertEqual(player._special_cooldowns, {})

    def test_environment_modifiers_restore_after_leaving(self):
        tile = BlockType(5000, is_solid=False, special="berserk", special_data=2.5)
        from block_types_data import BLOCK_TYPES
        world = make_world(block_types={**BLOCK_TYPES, tile.id: tile})
        world.set_tile(5, 5, tile.id)
        player = make_player()
        original_attack = player.phys_atk
        player.collide_with_world(world, 0)
        self.assertEqual(player.phys_atk, original_attack * 2.5)
        player._x = 20
        player.collide_with_world(world, 1 / 60)
        self.assertEqual(player.phys_atk, original_attack)

    def test_default_ladder_world_has_climbable_contacts(self):
        world = make_world(default_block_id=9)
        player = make_player()
        player.collide_with_world(world, 0)
        self.assertTrue(player.can_climb)

    def test_respawn_clears_environment_timers_and_modifiers(self):
        player = make_player()
        player.can_swim = True
        player._confused = True
        player._confusion_timer = 2
        player._phantom_active = True
        player._phantom_timer = 3
        player._special_cooldowns = {"phantom": 5}
        player._air_jumps_used = 1
        player._shore_exit_pending = "rise"
        player.reset(2, 3)
        self.assertFalse(player.can_swim)
        self.assertFalse(player._confused)
        self.assertFalse(player._phantom_active)
        self.assertFalse(player._shore_exit_pending)
        self.assertEqual(player._special_cooldowns, {})
        self.assertEqual(player._air_jumps_used, 0)


class PickupTests(unittest.TestCase):
    def test_only_touched_coin_is_consumed(self):
        world = make_world()
        world.set_tile(5, 5, 310)
        world.set_tile(6, 5, 310)
        player = make_player()
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 10)
        self.assertEqual(world.get_tile(5, 5).type_id, 320)
        self.assertEqual(world.get_tile(6, 5).type_id, 310)
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 10)

    def test_each_touched_coin_scores_once(self):
        world = make_world()
        for y in (5, 6):
            world.set_tile(5, y, 310)
        player = make_player(y=6)
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 20)
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 20)

    def test_coin_across_negative_loop_seam_is_consumed_once(self):
        world = make_world(loop_x=True)
        world.set_tile(39, 5, 310)
        player = make_player(x=-0.5)
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 10)
        self.assertEqual(world.get_tile(39, 5).type_id, 320)

    def test_score_block_without_consumed_variant_restores_default(self):
        world = make_world(default_block_id=11)
        world.set_tile(5, 5, 398)
        player = make_player()
        player.collide_with_world(world, 0)
        self.assertEqual(player.score, 200)
        self.assertEqual(world.get_tile(5, 5).type_id, 11)

    def test_teleport_uses_touched_portal_metadata(self):
        from block_types_data import BLOCK_TYPES
        tile_id = next(b.id for b in BLOCK_TYPES.values() if b.special == "teleport")
        world = make_world()
        world.set_tile(5, 5, tile_id, {"tp_x": 12, "tp_y": 10})
        world.set_tile(6, 5, tile_id, {"tp_x": 22, "tp_y": 20})
        player = make_player()
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), (12, 10))


class PoisonTests(unittest.TestCase):
    def test_poison_bypasses_half_shield_and_respects_immunity(self):
        world = make_world()
        world.set_tile(5, 5, 346)
        player = make_player()
        player.shield = 100
        player.collide_with_world(world, 1)
        self.assertEqual(player.hp, 90)
        self.assertEqual(player.shield, 90)
        player.apply_buff(36, (), 3)
        player.collide_with_world(world, 1)
        self.assertEqual(player.hp, 90)
        self.assertEqual(player.shield, 90)

    def test_poison_lethal_second_half_marks_player_dead(self):
        world = make_world()
        world.set_tile(5, 5, 346)
        player = make_player()
        player.hp = 15
        player.collide_with_world(world, 1)
        self.assertEqual(player.hp, 0)
        self.assertFalse(player.alive)


if __name__ == "__main__":
    unittest.main()
