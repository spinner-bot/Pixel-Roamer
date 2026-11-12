"""Deterministic gameplay regressions using small, isolated worlds."""
import os
import time
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
                    player.tick_buffs(1 / 60)
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


class CollisionTests(unittest.TestCase):
    def test_extreme_runtime_velocity_cannot_hang_collision_loop(self):
        world = make_world(loop_x=True, loop_y=True)
        player = make_player()
        player.v_y = 1e12
        start = time.perf_counter()
        player.collide_with_world(world, 1 / 60)
        self.assertLess(time.perf_counter() - start, 1)
        player.v_y = float("inf")
        player.collide_with_world(world, 1 / 60)
        self.assertEqual(player.v_y, 0)

    def test_fast_movement_does_not_cross_a_one_tile_wall(self):
        for direction in (-1, 1):
            with self.subTest(direction=direction):
                world = make_world()
                world.set_tile(5, 5, 1)
                player = make_player(2 if direction > 0 else 9, 5.5)
                player.v_x = direction * 36.5
                player.collide_with_world(world, 0.2)
                self.assertEqual(player.v_x, 0)
                if direction > 0:
                    self.assertAlmostEqual(player._x, 4.6)
                else:
                    self.assertAlmostEqual(player._x, 6.4)

    def test_fast_fall_lands_without_crossing_floor(self):
        world = make_world()
        world.set_tile(5, 5, 1)
        player = make_player(y=15)
        player.v_y = -100
        player.collide_with_world(world, 0.2)
        self.assertTrue(player.on_ground)
        self.assertAlmostEqual(player._y, 6.9)

    def test_one_way_platform_stays_solid_at_exact_rest(self):
        from block_types_data import BLOCK_TYPES
        platform = BlockType(5000, is_solid=True, one_way=True)
        world = make_world(block_types={**BLOCK_TYPES, platform.id: platform})
        world.gravity = -10
        world.set_tile(5, 5, platform.id)
        player = make_player(y=6.9)
        for _ in range(120):
            player.update_physics(1 / 60, world)
            player.collide_with_world(world, 1 / 60)
        self.assertTrue(player.on_ground)
        self.assertAlmostEqual(player._y, 6.9)

    def test_one_way_platform_allows_jumping_from_below(self):
        from block_types_data import BLOCK_TYPES
        platform = BlockType(5000, is_solid=True, one_way=True)
        world = make_world(block_types={**BLOCK_TYPES, platform.id: platform})
        world.set_tile(5, 5, platform.id)
        player = make_player(y=2)
        player.v_y = 30
        player.collide_with_world(world, 0.2)
        self.assertGreater(player._y - player._h / 2, 6)

    def test_solid_default_tile_collides(self):
        world = make_world(default_block_id=1)
        world.set_tile(5, 6, 0)
        world.set_tile(5, 7, 0)
        player = make_player(y=7)
        player.v_y = -10
        player.collide_with_world(world, 0.2)
        self.assertTrue(player.on_ground)
        self.assertAlmostEqual(player._y, 6.9)

    def test_negative_fractional_coordinates_use_floor(self):
        world = make_world()
        world.set_tile(0, 5, 310)
        self.assertEqual(world.get_tile(-0.2, 5).type_id, 0)
        looping = make_world(loop_x=True)
        looping.set_tile(39, 5, 310)
        self.assertEqual(looping.get_tile(-0.2, 5).type_id, 310)

    def test_single_loop_axis_does_not_disable_void_on_other_axis(self):
        world = make_world(loop_x=True)
        self.assertFalse(world.is_out_of_bounds(-1000, 10))
        self.assertTrue(world.is_out_of_bounds(10, -21))
        player = make_player(10, -21)
        player.collide_with_world(world, 1 / 60)
        self.assertFalse(player.alive)


class FrameRateTests(unittest.TestCase):
    def test_friction_buffs_damp_without_inverting_or_amplifying_motion(self):
        speeds = {}
        for buff_id in (None, 42, 43, 51):
            world = make_world()
            player = make_player()
            player.v_x = 10
            if buff_id is not None:
                player.apply_buff(buff_id, (), 10)
            player.collide_with_world(world, 1)
            speeds[buff_id] = player.v_x
            self.assertGreater(player.v_x, 0)
            self.assertLessEqual(player.v_x, 10)
        self.assertGreater(speeds[42], speeds[None])  # Slippery: less damping.
        self.assertGreater(speeds[51], speeds[None])  # Icy: less damping.
        self.assertLess(speeds[43], speeds[None])     # Sticky: more damping.

    def test_speed_and_jump_tiles_combine_with_buffs_and_restore(self):
        from block_types_data import BLOCK_TYPES
        speed = BlockType(5000, is_solid=False, special="speed", special_data=1.8)
        jump = BlockType(5001, is_solid=False, special="jump", special_data=1.5)
        world = make_world(block_types={**BLOCK_TYPES, speed.id: speed, jump.id: jump})
        world.set_tile(5, 5, speed.id)
        world.set_tile(5, 6, jump.id)
        player = make_player(y=6)
        player.apply_buff(3, (30,), 10)
        player.apply_buff(4, (50,), 10)
        player.collide_with_world(world, 0)
        player.refresh_movement_stats()  # Same refresh as the next main-loop frame.
        self.assertAlmostEqual(player.v_max, player._base_v_max * 1.8 * 1.3)
        self.assertAlmostEqual(player.v_jump, player._base_v_jump * 1.5 * 1.5)
        player._x = 20
        player.collide_with_world(world, 0)
        self.assertAlmostEqual(player.v_max, player._base_v_max * 1.3)
        self.assertAlmostEqual(player.v_jump, player._base_v_jump * 1.5)
        player.clear_buffs()
        player.refresh_movement_stats()
        self.assertEqual(player.v_max, player._base_v_max)
        self.assertEqual(player.v_jump, player._base_v_jump)

    def test_horizontal_movement_matches_across_frame_rates(self):
        positions = []
        for fps in (30, 60, 144):
            world = World(0, "frame rate", 1000, 50, gravity=0, edge_behavior="void")
            player = make_player(5, 20)
            for _ in range(fps * 5):
                player.move(0.35)
                player.update_physics(1 / fps, world)
                player.collide_with_world(world, 1 / fps)
            positions.append(player._x)
        self.assertLess(max(positions) - min(positions), 2.5, positions)


if __name__ == "__main__":
    unittest.main()
