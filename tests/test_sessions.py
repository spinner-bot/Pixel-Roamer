"""New-game isolation and map replay regressions."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


class MapSessionTests(unittest.TestCase):
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
