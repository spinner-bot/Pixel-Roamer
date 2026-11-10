"""Contact behavior should be invariant under whole-world translations."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from creature import Player
from world import World


class ContactEdgeTests(unittest.TestCase):
    def test_mirrored_shores_survive_negative_and_large_loop_translations(self):
        for x, shore, direction in ((1.45, 0, -1), (8.55, 9, 1)):
            world = World(0, 'shore', 10, 20, loop_x=True, loop_y=True, gravity=0)
            for gx in range(1, 9):
                for gy in range(1, 6):
                    world.set_tile(gx, gy, 7)
            for gy in range(1, 6):
                world.set_tile(shore, gy, 2)
            for dx in (0, -10, 10, -100000, 100000):
                for dy in (0, -20, 20):
                    with self.subTest(shore=shore, dx=dx, dy=dy):
                        player = Player(0, 'shore', x + dx, 5.7 + dy, {})
                        player.collide_with_world(world, 0)
                        self.assertTrue(player.can_swim)
                        self.assertTrue(player._near_shore)
                        self.assertEqual(player._shore_dir, direction)
                        self.assertEqual(player._swim_top_y, 6 + dy)

    def test_nearby_upper_segment_does_not_change_bounds_under_translation(self):
        for tile_id, attribute in ((7, '_swim_top_y'), (9, '_climb_top_y')):
            world = World(0, 'segments', 10, 20, loop_x=True, loop_y=True, gravity=0)
            world.set_tile(5, 5, tile_id)
            world.set_tile(5, 8, tile_id)
            for dx in (0, -10, 10):
                for dy in (0, -20, 20):
                    player = Player(0, 'segments', 5.5 + dx, 5.7 + dy, {})
                    player.collide_with_world(world, 0)
                    self.assertEqual(getattr(player, attribute), 6 + dy)
