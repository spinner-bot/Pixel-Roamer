import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from creature import Player
from world import World


def at_ladder():
    world = World(0, 'controls', 20, 20, gravity=0)
    world.set_tile(5, 5, 9)
    player = Player(0, 'controls', 6.1, 5.7, {})
    player.collide_with_world(world, 0)
    return player, world


class ControlActionTests(unittest.TestCase):
    def test_stunned_jump_and_ladder_capture_leave_motion_unchanged(self):
        player, world = at_ladder()
        player.on_ground = True
        player.apply_buff(28, (), 5)
        before = player.get_center(), player.v_x, player.v_y
        self.assertFalse(player.jump())
        self.assertFalse(player.jump(not_on_ground_ok=True))
        self.assertFalse(player.try_start_climbing(world))
        self.assertEqual((player.get_center(), player.v_x, player.v_y), before)

    def test_jump_suppression_still_allows_climbing(self):
        player, world = at_ladder()
        player.on_ground = True
        player.apply_buff(27, (), 5)
        self.assertFalse(player.jump())
        self.assertTrue(player.try_start_climbing(world))
        self.assertFalse(player.jump())

    def test_iron_will_preserves_immunity_for_actions(self):
        player, world = at_ladder()
        player.apply_buff(28, (), 5)
        player.apply_buff(27, (), 5)
        player.apply_buff(40, (), 5)
        self.assertTrue(player.try_start_climbing(world))
        self.assertTrue(player.jump())

    def test_stun_cannot_change_an_existing_climb_velocity(self):
        player, world = at_ladder()
        self.assertTrue(player.try_start_climbing(world))
        player.apply_buff(28, (), 5)
        player.climb_move(1)
        self.assertEqual(player.v_y, 0)
        player.tick_buffs(5)
        player.climb_move(1)
        self.assertEqual(player.v_y, 3)
