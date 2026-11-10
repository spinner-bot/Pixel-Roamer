"""Contact geometry invariants: positions must not jump when touching a face."""
import math
import os
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
