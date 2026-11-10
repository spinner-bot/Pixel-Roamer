"""New-game isolation and map replay regressions."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


class MapSessionTests(unittest.TestCase):
    def test_test_world_clay_platform_jump_and_walk_has_no_snap(self):
        from maps import get_map
        from creature import Player
        for direction in (-1, 1):
            world = get_map(1)
            self.assertEqual(world.get_tile(13, 15).type_id, 4)
            player = Player(0, "clay route", 13, 16.9, {}, v_jump=3)
            player.collide_with_world(world, 0)
            self.assertTrue(player.jump())
            landed = False
            for frame in range(120):
                player.move(0.05 * direction)
                player.update_physics(1 / 60, world)
                before, speed = player._x, abs(player.v_x)
                player.collide_with_world(world, 1 / 60)
                self.assertLessEqual(abs(player._x - before), speed / 60 + 1e-8)
                self.assertGreaterEqual((player._x - before) * direction, -1e-8)
                if frame > 1 and player.on_ground:
                    landed = True
            self.assertTrue(landed)
            self.assertEqual(world.get_tile(player._x, player._y - player._h / 2 - 0.001).type_id, 4)

    def test_all_map_spawns_have_clear_character_space(self):
        from maps import get_map, list_maps
        from creature import Player
        for map_id in list_maps():
            with self.subTest(map_id=map_id):
                world = get_map(map_id)
                config = world.player_config
                player = Player(0, "spawn", *world.spawn_points, {},
                                w=config.get("w", 0.8), h=config.get("h", 1.8))
                rect = player.get_game_rect()
                self.assertFalse(any(rect.collides(block)
                                     for block, _ in world.get_nearby_solid_blocks_game(rect)))

    def test_temple_existing_corridor_reaches_portal_and_end(self):
        from maps import get_map
        from creature import Player
        world = get_map(7)
        player = Player(0, "route", *world.spawn_points, {})
        teleported = False
        for _ in range(1200):
            if player.on_ground and (player.on_wall_left or player.on_wall_right):
                player.jump()
            player.move(-0.35 if teleported else 0.35)
            player.update_physics(1 / 60, world)
            player.collide_with_world(world, 1 / 60)
            if player._x > 40 and player._y > 35:
                teleported = True
            if player._reached_end:
                break
        self.assertTrue(player.alive)
        self.assertTrue(teleported, f"Blocked before temple portal: {player.get_center()}")
        self.assertTrue(player._reached_end, f"Blocked before end: {player.get_center()}")

    def test_new_game_restores_collected_score_blocks(self):
        from maps import get_map
        world = get_map(7)
        coord, tile_id = next(
            (coord, tile.type_id) for coord, tile in world.grid.items()
            if world.block_types[tile.type_id].special == "score")
        world.set_tile(*coord, 0)
        replay = get_map(7)
        self.assertIsNot(replay, world)
        self.assertEqual(replay.get_tile(*coord).type_id, tile_id)

    def test_sessions_do_not_share_grid_indexes_or_render_caches(self):
        from maps import get_map
        first, second = get_map(1), get_map(1)
        self.assertIsNot(first.grid, second.grid)
        self.assertIsNot(first._solid_index, second._solid_index)
        self.assertIsNot(first._chunk_surfaces, second._chunk_surfaces)
        self.assertIsNot(first._scaled_chunk_cache, second._scaled_chunk_cache)
        first.set_tile(10, 15, 1)
        self.assertNotEqual(first.get_tile(10, 15).type_id,
                            second.get_tile(10, 15).type_id)

    def test_world_settings_do_not_leak_into_next_game(self):
        from maps import get_map
        world = get_map(7)
        original = world.gravity
        world.gravity = -12345
        self.assertEqual(get_map(7).gravity, original)


if __name__ == "__main__":
    unittest.main()
