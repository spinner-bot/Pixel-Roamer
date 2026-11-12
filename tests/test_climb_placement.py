import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from creature import Player
from world import World
from teleport import can_place


class ClimbPlacementTests(unittest.TestCase):
    def test_ladder_capture_never_embeds_head_in_neighbor_wall(self):
        for ladder_x, player_x in ((5, 6.4), (14, 13.6)):
            world = World(0, 'blocked', 20, 20, loop_x=True, loop_y=True, gravity=0)
            world.set_tile(ladder_x, 5, 9)
            world.set_tile(ladder_x, 6, 2)
            for dx in (0, -20, 20):
                for dy in (0, -20, 20):
                    player = Player(0, 'blocked', player_x + dx, 5.7 + dy, {})
                    player.collide_with_world(world, 0)
                    self.assertTrue(player.can_climb)
                    before = player.get_center()
                    self.assertFalse(player.try_start_climbing(world))
                    self.assertEqual(player.get_center(), before)
                    self.assertFalse(player.is_climbing)
                    self.assertTrue(can_place(player, world, *player.get_center()))

    def test_capture_uses_touched_vertical_segment_instead_of_nearby_ladder(self):
        world = World(0, 'ladder', 20, 20, gravity=0)
        world.set_tile(5, 5, 9)
        world.set_tile(6, 7, 9)
        player = Player(0, 'ladder', 6.1, 5.7, {})
        player.collide_with_world(world, 0)
        self.assertTrue(player.try_start_climbing(world))
        self.assertEqual(player._x, 6.1, 'capture must not teleport before a physics step')
        for _ in range(3):
            player.update_physics(.05, world)
            player.collide_with_world(world, .05)
            self.assertTrue(can_place(player, world, *player.get_center()))
        self.assertEqual(player._x, 5.5)
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_default_ladder_loop_and_regular_ladder_still_capture(self):
        world = World(0, 'default', 10, 20, loop_x=True, loop_y=True, default_block_id=9)
        for dx, dy in ((0, 0), (-10, -20), (10, 20)):
            player = Player(0, 'default', 5.2 + dx, 5.7 + dy, {})
            player.collide_with_world(world, 0)
            self.assertTrue(player.try_start_climbing(world))
            self.assertEqual(player.get_center(), (5.2 + dx, 5.7 + dy))
            player.update_physics(.05, world)
            player.collide_with_world(world, .05)
            self.assertEqual(player.get_center(), (5.5 + dx, 5.7 + dy))
        world = World(0, 'regular', 20, 20, gravity=0)
        world.set_tile(5, 5, 9)
        player = Player(0, 'regular', 5.5, 6.5, {})
        player.collide_with_world(world, 0)
        self.assertFalse(player.try_start_climbing(world), 'feet touching is insufficient at this height')
