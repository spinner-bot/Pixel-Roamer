import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from creature import Player
from world import World


class EnvironmentColumnTests(unittest.TestCase):
    def test_deep_contact_tracks_the_end_of_its_connected_column(self):
        for kind, attribute in ((7, '_swim_top_y'), (9, '_climb_top_y')):
            world = World(0, 'column', 10, 30)
            for y in range(1, 20):
                world.set_tile(5, y, kind)
            world.set_tile(5, 22, kind)
            world.set_tile(6, 25, kind)
            player = Player(0, 'column', 5.5, 10, {})
            player.collide_with_world(world, 0)
            self.assertEqual(getattr(player, attribute), 20)

    def test_endless_vertical_default_column_has_no_false_surface(self):
        for kind, attribute in ((7, '_swim_top_y'), (9, '_climb_top_y')):
            world = World(0, 'endless', 1, 1, loop_x=True, loop_y=True, default_block_id=kind)
            player = Player(0, 'endless', .5, .5, {})
            player.collide_with_world(world, 0)
            self.assertIsNone(getattr(player, attribute))

    def test_bank_with_wall_above_surface_is_not_a_clear_shore(self):
        from scripts.audit_swimming import make_session
        session = make_session()
        world, player = session.app._current_map, session.app.player1
        world.set_tile(0, 20, 2)
        player.collide_with_world(world, 0)
        self.assertFalse(player._near_shore)
