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


if __name__ == "__main__":
    unittest.main()
