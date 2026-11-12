import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import random
import unittest
from creature import Player
from world import World
from scripts.audit_environment_cycles import run_cycle


class EnvironmentCycleTests(unittest.TestCase):
    def test_altar_entry_leave_respawn_and_teleports_preserve_fractional_stats(self):
        for base in (1.25, 10, .1):
            run = run_cycle(base)
            self.assertEqual(run['failures'], 0, run)

    def test_repeated_contact_and_flight_cleanup_do_not_accumulate_or_disable_multiplier(self):
        world = World(0, 'altar', 30, 30, gravity=0)
        world.set_tile(5, 5, 348)
        player = Player(0, 'altar', 5.5, 6.9, {}, phys_atk=1.25)
        for _ in range(100):
            player.collide_with_world(world, 0)
            self.assertEqual(player.phys_atk, 3.125)
            player.clear_environment_contacts(world)
            self.assertEqual(player.phys_atk, 1.25)

    def test_fractional_base_attacks_keep_numeric_precision(self):
        rng = random.Random(20261111)
        for _ in range(100):
            base = rng.uniform(.001, 50)
            run = run_cycle(base)
            self.assertEqual(run['failures'], 0, run)
