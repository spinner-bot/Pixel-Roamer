import math
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
from creature import Player
from world import World
from teleport import can_place, random_teleport
from scripts.audit_random_portals import run_cases


class RandomTeleportTests(unittest.TestCase):
    def test_two_thousand_seeded_activations_never_embed_or_leave_range(self):
        for run in run_cases():
            with self.subTest(kind=run['kind']):
                self.assertEqual(run['unsafe_count'], 0)
                self.assertEqual(run['range_violations'], [])
                self.assertGreater(run['moved_count'], 900)

    def test_impossible_offsets_are_bounded_and_do_not_retry_while_still_touching(self):
        world = World(0, 'sealed', 30, 30, gravity=0, default_block_id=2)
        world.set_tile(15, 9, 301)
        world.set_tile(15, 10, 0)
        world.set_tile(15, 11, 0)
        player = Player(0, 'sealed', 15.5, 10.9, {})
        self.assertTrue(can_place(player, world, *player.get_center()))
        with patch('random.uniform', side_effect=lambda a, b: b) as uniform:
            player.collide_with_world(world, 0)
            self.assertEqual(uniform.call_count, 64)
            for _ in range(120):
                player.collide_with_world(world, 0)
            self.assertEqual(uniform.call_count, 64)
        self.assertEqual(player.get_center(), (15.5, 10.9))
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_zero_offset_arrival_on_same_rune_does_not_recurse_or_repeat(self):
        world = World(0, 'contact', 30, 30, gravity=0)
        world.set_tile(15, 9, 358)
        player = Player(0, 'contact', 15.5, 10.9, {})
        with patch('random.uniform', return_value=0) as uniform:
            player.collide_with_world(world, 0)
            player.collide_with_world(world, 0)
            self.assertEqual(uniform.call_count, 2)
        self.assertTrue(player._teleport_latched)
        world.set_tile(15, 9, 0)
        player.collide_with_world(world, 0)
        self.assertFalse(player._teleport_latched)

    def test_malformed_or_nonfinite_ranges_never_move(self):
        world = World(0, 'invalid', 30, 30)
        player = Player(0, 'invalid', 15.5, 10.9, {})
        for ranges in (None, '8,8', [8], (-1, 2), (math.nan, 1), (math.inf, 1),
                       (10**1000, 1), (True, 1)):
            self.assertFalse(random_teleport(player, world, ranges))
            self.assertEqual(player.get_center(), (15.5, 10.9))
