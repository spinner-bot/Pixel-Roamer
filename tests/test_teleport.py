import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from creature import Player
from world import World
from teleport import can_place, teleport_to


def portal_world():
    world = World(0, 'portals', 40, 30, gravity=-6.5)
    for x in range(40):
        world.set_tile(x, 8, 2)
    world.set_tile(5, 9, 300, {'tp_x': 20.5, 'tp_y': 9.9})
    world.set_tile(20, 9, 300, {'tp_x': 5.5, 'tp_y': 9.9})
    return world


class TeleportTests(unittest.TestCase):
    def test_reciprocal_portals_stay_stable_until_player_leaves_and_returns(self):
        world = portal_world()
        player = Player(0, 'portal', 5.5, 9.9, {})
        player.collide_with_world(world, 0)
        self.assertEqual(player.get_center(), (20.5, 9.9))
        for _ in range(240):
            player.update_physics(1 / 120, world)
            player.collide_with_world(world, 1 / 120)
        self.assertEqual(player.get_center(), (20.5, 9.9))
        for _ in range(150):
            player.move(.35)
            player.update_physics(1 / 120, world)
            player.collide_with_world(world, 1 / 120)
        self.assertGreater(player._x, 21.5)
        for _ in range(1200):
            player.move(-.35)
            player.update_physics(1 / 120, world)
            player.collide_with_world(world, 1 / 120)
            if player._x < 10:
                break
        self.assertLess(player._x, 10)
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_unsafe_nonfinite_and_malformed_targets_do_not_move_or_crash(self):
        world = portal_world()
        player = Player(0, 'target', 10, 15, {})
        for tx, ty in ((2, 8), (0, 0), (-10, 10), (math.nan, 10), (10, math.inf),
                       ('10', 10), (True, 10), (10**1000, 10)):
            with self.subTest(target=(str(tx)[:30], ty)):
                self.assertFalse(teleport_to(player, world, tx, ty))
                self.assertEqual(player.get_center(), (10, 15))
        self.assertTrue(teleport_to(player, world, 10.5, 9.9))
        self.assertEqual(player.get_center(), (10.5, 9.9))

    def test_loop_target_is_normalized_before_testing_collision(self):
        world = World(0, 'loop', 40, 30, loop_x=True, loop_y=True)
        player = Player(0, 'loop', 1, 2, {})
        self.assertTrue(teleport_to(player, world, 85.5, -20.1))
        self.assertAlmostEqual(player._x, 5.5)
        self.assertAlmostEqual(player._y, 9.9)
        player._teleport_latched = True
        player.reset(1, 2)
        self.assertFalse(player._teleport_latched)

    def test_all_map_portals_have_clear_targets_and_survive_real_activation(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'portals.json'
            result = subprocess.run([sys.executable, 'scripts/audit_portals.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            portals = json.loads(output.read_text())['portals']
        self.assertEqual(len(portals), 22)
        self.assertTrue(any(p['map'] == 6 for p in portals), 'forest portal must not be overwritten')
        self.assertTrue(all(p['reached_end'] for p in portals if p['map'] == 21))

    def test_hidden_room_arrivals_have_physical_exits(self):
        from maps import get_map
        for map_id, portal_coord, exit_x in ((4, (26, 15), 0), (3, (375, 80), 274.5)):
            world = get_map(map_id)
            tile = world.grid[portal_coord]
            player = Player(0, 'exit', 10, 20, {})
            self.assertTrue(teleport_to(player, world, tile.meta['tp_x'], tile.meta['tp_y']))
            for _ in range(2400):
                if player.on_ground and player.on_wall_left:
                    player.jump()
                player.move(-.35)
                player.tick_buffs(1 / 120)
                player.update_physics(1 / 120, world)
                player.collide_with_world(world, 1 / 120)
                self.assertTrue(player.alive)
                self.assertTrue(can_place(player, world, *player.get_center()))
                if player._x < exit_x:
                    break
            self.assertLess(player._x, exit_x, (map_id, player.get_center()))
