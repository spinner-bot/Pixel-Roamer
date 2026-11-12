import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from creature import Player
from world import World


class WorldMutationTests(unittest.TestCase):
    def test_same_type_metadata_update_changes_actual_portal_destination(self):
        world = World(0, 'metadata', 40, 30, gravity=0)
        world.set_tile(5, 5, 300, {'tp_x': 12, 'tp_y': 10})
        world._render_chunk((0, 0))
        raster = world._chunk_surfaces[(0, 0)]
        world.set_tile(5, 5, 300, {'tp_x': 22, 'tp_y': 20})
        player = Player(0, 'metadata', 5.5, 5.5, {})
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), (22, 20))
        self.assertIs(world._chunk_surfaces[(0, 0)], raster)
        self.assertNotIn((0, 0), world._dirty_chunks)
        self.assertNotIn((5, 5), world._solid_index)

    def test_same_type_metadata_overwrite_and_clear_match_bulk_loading(self):
        for bulk in (False, True):
            world = World(0, 'metadata', 40, 30)
            if bulk:
                world.begin_bulk_load()
            world.set_tile(5, 5, 2, {'label': 'old'})
            world.set_tile(5, 5, 2, {'label': 'new'})
            self.assertEqual(world.get_tile(5, 5).meta, {'label': 'new'})
            world.set_tile(5, 5, 2)
            self.assertIsNone(world.get_tile(5, 5).meta)
            if bulk:
                world.end_bulk_load()
            self.assertIn((5, 5), world._solid_index)
