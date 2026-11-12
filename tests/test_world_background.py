import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
import pygame
from block_type import BlockType
from camera import Camera
from world import World


class WorldBackgroundTests(unittest.TestCase):
    def test_background_only_fills_nonlooping_axes_outside_world(self):
        background, sky = (4, 8, 12), (135, 255, 255)
        points = ((0, 0), (40, 0), (0, 40), (40, 40))
        cases = [((False, False), (background, background, background, sky)),
                 ((True, False), (background, background, sky, sky)),
                 ((False, True), (background, sky, background, sky)),
                 ((True, True), (sky, sky, sky, sky))]
        for loops, expected in cases:
            world = World(0, 'small', 2, 2, loop_x=loops[0], loop_y=loops[1], view_blocks_h=4)
            world.fill_color = background
            camera = Camera(80, 80, world)
            camera.follow(1, 1)
            surface = pygame.Surface((80, 80))
            world.draw(surface, camera)
            self.assertEqual(tuple(surface.get_at(point)[:3] for point in points), expected)

    def test_partial_chunks_do_not_bleed_sky_into_world_or_over_background(self):
        types = {0: BlockType(0, is_solid=False, color=(100, 150, 200)),
                 2: BlockType(2, color=(150, 80, 40))}
        world = World(0, 'partial', 5, 3, block_types=types)
        world.fill_color = (4, 8, 12)
        for x in range(5):
            for y in range(3):
                world.set_tile(x, y, 2)
        camera = Camera(80, 80, world)
        camera.scale = 13.3
        camera.follow(2.5, 1.5)
        surface = pygame.Surface((80, 80))
        world.draw(surface, camera)
        left = round(camera.world_to_screen(0, 0)[0])
        right = round(camera.world_to_screen(5, 0)[0])
        top = round(camera.world_to_screen(0, 3)[1])
        bottom = round(camera.world_to_screen(0, 0)[1])
        for x in range(80):
            for y in range(80):
                expected = types[2].color if left <= x < right and top <= y < bottom else world.fill_color
                self.assertEqual(surface.get_at((x, y))[:3], expected, (x, y))

    def test_caller_clip_is_preserved_and_pixels_outside_it_are_untouched(self):
        world = World(0, 'clip', 2, 2, view_blocks_h=4)
        world.fill_color = (4, 8, 12)
        camera = Camera(80, 80, world)
        camera.follow(1, 1)
        surface = pygame.Surface((80, 80))
        surface.fill((250, 0, 250))
        clip = pygame.Rect(5, 6, 40, 40)
        surface.set_clip(clip)
        world.draw(surface, camera)
        self.assertEqual(surface.get_clip(), clip)
        self.assertEqual(surface.get_at((0, 0))[:3], (250, 0, 250))
        self.assertEqual(surface.get_at((5, 6))[:3], world.fill_color)
        self.assertEqual(surface.get_at((40, 40))[:3], world.block_types[0].color)

    def test_wide_view_does_not_create_chunks_beyond_finite_map(self):
        world = World(0, 'wide', 64, 36, view_blocks_h=200)
        camera = Camera(1600, 900, world)
        camera.follow(4.5, 25.9)
        world.draw(pygame.Surface((1600, 900)), camera)
        self.assertLessEqual(len(world._chunk_surfaces), 4)
        self.assertTrue(all(0 <= x <= 1 and 0 <= y <= 1 for x, y in world._chunk_surfaces))
