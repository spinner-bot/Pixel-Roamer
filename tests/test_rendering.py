import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from block_type import BlockType
from camera import Camera
from world import World


class LoopRenderingTests(unittest.TestCase):
    def test_fractional_camera_scale_does_not_leave_chunk_gaps(self):
        world = World(0, "seam", 5, 3, loop_x=True, loop_y=True,
                      block_types={0: BlockType(0, is_solid=False, color=(17, 34, 51))})
        camera = Camera(640, 360, world)
        camera.scale = 3.17
        camera.follow(0.27, 1.3)
        surface = pygame.Surface((640, 360))
        surface.fill((255, 0, 255))
        world.draw(surface, camera)
        expected = pygame.Surface(surface.get_size())
        expected.fill((17, 34, 51))
        self.assertEqual(pygame.image.tobytes(surface, "RGB"),
                         pygame.image.tobytes(expected, "RGB"))

    def make_world(self):
        types = {0: BlockType(0, is_solid=False, color=(0, 0, 0))}
        for tile_id in range(1, 16):
            types[tile_id] = BlockType(tile_id, is_solid=False,
                                       color=(tile_id * 15, tile_id * 10, tile_id * 5))
        world = World(0, "phase", 5, 3, loop_x=True, loop_y=True, block_types=types)
        for x in range(5):
            for y in range(3):
                world.set_tile(x, y, 1 + x + y * 5)
        return world

    def assert_visible_tiles_match_collision_world(self, world, camera):
        surface = pygame.Surface((96, 96))
        world.draw(surface, camera)
        for x in range(-5, 6):
            for y in range(-5, 6):
                wx, wy = camera.x + x + 0.5, camera.y + y + 0.5
                sx, sy = camera.world_to_screen(wx, wy)
                if 0 <= sx < 96 and 0 <= sy < 96:
                    self.assertEqual(surface.get_at((int(sx), int(sy)))[:3],
                                     world.get_block_type(wx, wy).color, (wx, wy))
        return pygame.image.tobytes(surface, "RGB")

    def test_non_chunk_sized_loops_render_at_actual_world_period(self):
        world = self.make_world()
        camera = Camera(96, 96, world)
        camera.scale = 8
        before = self.assert_visible_tiles_match_collision_world(world, camera)
        camera.follow(world.width, world.height)
        after = self.assert_visible_tiles_match_collision_world(world, camera)
        self.assertEqual(before, after)

    def test_edit_invalidates_all_visible_loop_copies(self):
        world = self.make_world()
        camera = Camera(96, 96, world)
        camera.scale = 8
        self.assert_visible_tiles_match_collision_world(world, camera)
        world.set_tile(2, 1, 15)
        self.assert_visible_tiles_match_collision_world(world, camera)
        camera.follow(-10, -6)
        self.assert_visible_tiles_match_collision_world(world, camera)


if __name__ == "__main__":
    unittest.main()
