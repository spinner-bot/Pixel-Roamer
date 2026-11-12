"""Contact geometry invariants: positions must not jump when touching a face."""
import math
import os
import random
from itertools import permutations
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from creature import Player
from world import World


def flat_world(top, tile_id=4):
    world = World(0, "precision", 100, 160, gravity=-6.5, edge_behavior="void")
    for x in range(2, 40):
        world.set_tile(x, top - 1, tile_id)
    return world


class CollisionPrecisionTests(unittest.TestCase):
    def test_nearest_collision_is_independent_of_candidate_order(self):
        from block_type import BlockType
        from collision import sweep_axis
        from game_rect import GameRect
        for horizontal in (False, True):
            for direction in (-1, 1):
                obstacles = []
                for edge in (5, 7, 9):
                    block = GameRect(edge, 0, 1, 20) if horizontal else GameRect(0, edge, 20, 1)
                    obstacles.append((block, BlockType(1)))
                results = set()
                for ordered in permutations(obstacles):
                    rect = GameRect(1 if direction > 0 else 12, 4, 0.8, 1.8)
                    if not horizontal:
                        rect.x, rect.y = rect.y, rect.x
                    self.assertTrue(sweep_axis(rect, direction * 15, ordered, horizontal))
                    results.add((rect.x, rect.y))
                self.assertEqual(len(results), 1, results)
                coordinate = next(iter(results))[0 if horizontal else 1]
                self.assertAlmostEqual(coordinate, (5 - (0.8 if horizontal else 1.8))
                                       if direction > 0 else 10)

    def test_seeded_obstacle_motion_stays_bounded_and_nonpenetrating(self):
        rng = random.Random(20261111)
        cases = 0
        for _ in range(20):
            world = World(0, "random", 40, 40, gravity=0, edge_behavior="void")
            world.begin_bulk_load()
            for x in range(2, 38):
                for y in range(2, 38):
                    if rng.random() < 0.12:
                        world.set_tile(x, y, 2)
            world.end_bulk_load()
            accepted = 0
            while accepted < 100:
                player = Player(0, "random", rng.uniform(5, 35), rng.uniform(5, 35), {},
                                w=rng.choice((0.6, 0.8, 1.2)), h=rng.choice((1.5, 1.8, 2.0)))
                rect = player.get_game_rect()
                if any(rect.collides(block) for block, _ in world.get_nearby_solid_blocks_game(rect)):
                    continue
                player.v_x, player.v_y = rng.uniform(-50, 50), rng.uniform(-50, 50)
                dt = rng.choice((1 / 30, 1 / 60, 1 / 144, 0.2))
                x, y = player.get_center()
                vx, vy = player.v_x, player.v_y
                player.collide_with_world(world, dt)
                self.assertLessEqual(abs(player._x - x), abs(vx) * dt + 1e-7)
                self.assertLessEqual(abs(player._y - y), abs(vy) * dt + 1e-7)
                rect = player.get_game_rect()
                for block, _ in world.get_nearby_solid_blocks_game(rect):
                    overlap_x = min(rect.x + rect.w, block.x + block.w) - max(rect.x, block.x)
                    overlap_y = min(rect.y + rect.h, block.y + block.h) - max(rect.y, block.y)
                    self.assertFalse(overlap_x > 1e-7 and overlap_y > 1e-7,
                                     (x, y, vx, vy, dt, player.get_center()))
                accepted += 1
                cases += 1
        self.assertEqual(cases, 2000)

    def test_passive_ice_friction_never_generates_speed(self):
        for tile_id in (3, 75, 86):
            with self.subTest(tile_id=tile_id):
                world = flat_world(5, tile_id)
                player = Player(0, "ice", 10, 5.9, {})
                player.v_x = 2
                player.collide_with_world(world, 0)
                for _ in range(60):
                    before = abs(player.v_x)
                    player.update_physics(1 / 60, world)
                    player.collide_with_world(world, 1 / 60)
                    self.assertLessEqual(abs(player.v_x), before + 1e-8)

    def test_friction_buffs_do_not_erase_liquid_drag(self):
        for buff_id in (42, 43, 51):
            velocities = []
            for in_water in (False, True):
                world = World(0, "drag", 30, 30, gravity=0, edge_behavior="void")
                if in_water:
                    world.set_tile(5, 5, 7)
                player = Player(0, "drag", 5.5, 5.5, {})
                player.v_x = 2
                player.apply_buff(buff_id, (), 10)
                player.collide_with_world(world, 1 / 60)
                velocities.append(player.v_x)
            self.assertLess(velocities[1], velocities[0], (buff_id, velocities))

    def test_mirrored_geometry_has_no_left_or_right_bias(self):
        rng = random.Random(3817)
        worlds = [World(0, "mirror", 80, 80, gravity=0, edge_behavior="void") for _ in range(2)]
        for x in range(5, 65):
            for y in (4, 20):
                worlds[0].set_tile(x, y, 4)
                worlds[1].set_tile(79 - x, y, 4)
        for y in range(5, 14):
            worlds[0].set_tile(25, y, 4)
            worlds[1].set_tile(54, y, 4)
        accepted = 0
        while accepted < 500:
            x, y = rng.uniform(8, 72), rng.uniform(6, 28)
            players = [Player(0, "mirror", x, y, {}), Player(0, "mirror", 80 - x, y, {})]
            if any(any(p.get_game_rect().collides(b) for b, _ in w.get_nearby_solid_blocks_game(p.get_game_rect()))
                   for p, w in zip(players, worlds)):
                continue
            vx, vy = rng.uniform(-35, 35), rng.uniform(-35, 35)
            dt = rng.choice((1 / 30, 1 / 60, 1 / 144, 0.1))
            for p, w, direction in zip(players, worlds, (1, -1)):
                p.v_x, p.v_y = vx * direction, vy
                p.collide_with_world(w, dt)
            self.assertAlmostEqual(players[0]._x + players[1]._x, 80, places=7)
            self.assertAlmostEqual(players[0]._y, players[1]._y, places=7)
            accepted += 1

    def test_translated_surface_keeps_same_motion_at_large_coordinates(self):
        players, worlds = [], []
        for offset in (0, 100000):
            world = World(0, "translated", 200000, 200000, gravity=-6.5, edge_behavior="void")
            for x in range(2, 40):
                world.set_tile(x + offset, 15 + offset, 4)
            player = Player(0, "translated", 15.7 + offset,
                            math.nextafter(16.9 + offset, -math.inf), {})
            player.v_x = 2
            players.append(player)
            worlds.append(world)
        for _ in range(120):
            for player, world in zip(players, worlds):
                player.update_physics(1 / 60, world)
                player.collide_with_world(world, 1 / 60)
            self.assertAlmostEqual(players[1]._x - 100000, players[0]._x, places=7)
            self.assertAlmostEqual(players[1]._y - 100000, players[0]._y, places=7)

    def test_landing_roundoff_does_not_become_a_side_collision(self):
        for top in (5, 8, 16, 32, 64, 128):
            for direction in (-1, 1):
                for offset in (0, -1e-15, -1e-12, -1e-9):
                    with self.subTest(top=top, direction=direction, offset=offset):
                        world = flat_world(top)
                        player = Player(0, "precision", 6, top + 0.9 + offset, {})
                        player.v_x = direction * 2
                        player.v_y = -0.1
                        before = player.get_center()
                        player.collide_with_world(world, 1 / 60)
                        dx = player._x - before[0]
                        self.assertGreaterEqual(dx * direction, -1e-8)
                        self.assertLessEqual(abs(dx), 2 / 60 + 1e-8)
                        self.assertAlmostEqual(player.get_game_rect().y, top, places=8)
                        self.assertFalse(player.on_wall_left)
                        self.assertFalse(player.on_wall_right)

    def test_roundoff_at_ceiling_does_not_push_player_sideways(self):
        for direction in (-1, 1):
            world = flat_world(17)
            player = Player(0, "ceiling", 6, 16 - 0.9 + 1e-12, {})
            player.v_x, player.v_y = direction * 2, 0.1
            old_x = player._x
            player.collide_with_world(world, 1 / 60)
            self.assertGreaterEqual((player._x - old_x) * direction, -1e-8)
            self.assertLessEqual(abs(player._x - old_x), 2 / 60 + 1e-8)
            self.assertTrue(player.on_ceiling)

    def test_vertical_slide_along_wall_does_not_become_a_floor_collision(self):
        for direction in (-1, 1):
            world = World(0, "wall", 30, 30, gravity=0, edge_behavior="void")
            for y in range(2, 25):
                world.set_tile(10, y, 4)
            player = Player(0, "wall", 9.6 + 1e-12, 12, {})
            player.v_x, player.v_y = 0, direction * 2
            before_y = player._y
            player.collide_with_world(world, 1 / 60)
            self.assertGreater((player._y - before_y) * direction, 0)
            self.assertLessEqual(abs(player._y - before_y), 2 / 60 + 1e-8)
            self.assertFalse(player.on_ground)
            self.assertFalse(player.on_ceiling)

    def test_actual_clay_platform_jump_and_landing_preserves_horizontal_motion(self):
        # This is the test_world clay platform height (tiles y=15, top y=16).
        for fps in (30, 60, 144):
            for direction in (-1, 1):
                world = flat_world(16)
                player = Player(0, "jump", 20, 16.9, {}, v_jump=9)
                player.collide_with_world(world, 0)
                self.assertTrue(player.on_ground)
                self.assertTrue(player.jump())
                landed = False
                for frame in range(fps * 5):
                    player.move(direction * 0.1)
                    player.update_physics(1 / fps, world)
                    previous_x = player._x
                    speed = abs(player.v_x)
                    player.collide_with_world(world, 1 / fps)
                    self.assertLessEqual(abs(player._x - previous_x), speed / fps + 1e-8)
                    if frame > 1 and player.on_ground:
                        landed = True
                        # Keep walking over tile seams after the landing.
                        for _ in range(fps):
                            player.move(direction * 0.1)
                            player.update_physics(1 / fps, world)
                            previous_x, speed = player._x, abs(player.v_x)
                            player.collide_with_world(world, 1 / fps)
                            self.assertGreaterEqual((player._x - previous_x) * direction, -1e-8)
                            self.assertLessEqual(abs(player._x - previous_x), speed / fps + 1e-8)
                        break
                self.assertTrue(landed, (fps, direction, player.get_center()))


if __name__ == "__main__":
    unittest.main()
