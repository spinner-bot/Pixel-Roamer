import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import random
import unittest
from unittest.mock import patch
import pygame
from camera import Camera
import chunk_scaling
from chunk_scaling import blit_large_chunk, clear_axis_cache
from world import World


class ZoomRenderingTests(unittest.TestCase):
    def setUp(self):
        clear_axis_cache()

    def test_clipped_scaling_matches_full_pygame_transform_for_seeded_sizes(self):
        rng = random.Random(20261111)
        for _ in range(200):
            source = pygame.Surface((rng.randrange(1, 20), rng.randrange(1, 20)), depth=32)
            for x in range(source.get_width()):
                for y in range(source.get_height()):
                    source.set_at((x, y), tuple(rng.randrange(256) for _ in range(3)))
            size = rng.randrange(1, 200), rng.randrange(1, 150)
            rect = pygame.Rect(rng.randrange(-100, 40), rng.randrange(-75, 30), *size)
            expected = pygame.Surface((96, 64))
            expected.fill((21, 32, 43))
            actual = expected.copy()
            clip = pygame.Rect(5, 7, 80, 50)
            expected.set_clip(clip)
            actual.set_clip(clip)
            expected.blit(pygame.transform.scale(source, size), rect)
            blit_large_chunk(actual, source, rect)
            self.assertEqual(pygame.image.tobytes(expected, 'RGB'), pygame.image.tobytes(actual, 'RGB'))
            self.assertEqual(actual.get_clip(), clip)

    def test_valid_minimum_editor_view_never_allocates_an_oversized_surface(self):
        world = World(0, 'zoom', 64, 36, view_blocks_h=2)
        world.set_tile(4, 25, 4)
        surface = pygame.Surface((1600, 900))
        camera = Camera(1600, 900, world)
        camera.follow(4.5, 25.9)
        real_scale = pygame.transform.scale
        allocations = []
        def guarded(source, size, *args, **kwargs):
            estimated = size[0] * size[1] * source.get_bytesize()
            allocations.append(estimated)
            self.assertLessEqual(estimated, 64 * 1024 * 1024)
            return real_scale(source, size, *args, **kwargs)
        with patch('pygame.transform.scale', side_effect=guarded):
            world.draw(surface, camera)
        self.assertTrue(allocations)
        self.assertLessEqual(max(allocations), 57600)
        self.assertLessEqual(chunk_scaling._axis_cache_bytes, chunk_scaling.MAX_AXIS_CACHE_BYTES)

    def test_forced_clipped_world_draw_matches_normal_chunks_at_fractional_loop_phases(self):
        for loops in ((False, False), (True, False), (True, True)):
            world = World(0, 'phase', 5, 3, loop_x=loops[0], loop_y=loops[1])
            for x in range(5):
                for y in range(3):
                    world.set_tile(x, y, (2, 3, 4, 17)[(x + y) % 4])
            for scale in (3.17, 8, 16.37, 33.3):
                camera = Camera(96, 64, world)
                camera.scale = scale
                camera.follow(-3.27, 1.3)
                expected = pygame.Surface((96, 64))
                actual = expected.copy()
                world.draw(expected, camera)
                with patch('world.MAX_SCALED_CACHE_BYTES', 1024):
                    world.draw(actual, camera)
                self.assertEqual(pygame.image.tobytes(expected, 'RGB'), pygame.image.tobytes(actual, 'RGB'),
                                 (loops, scale))

    def test_axis_cache_has_byte_and_entry_bounds(self):
        target = pygame.Surface((8, 8))
        source = pygame.Surface((2, 2))
        for size in range(10, 110):
            blit_large_chunk(target, source, pygame.Rect(0, 0, size, size))
        self.assertLessEqual(len(chunk_scaling._axis_cache), chunk_scaling.MAX_AXIS_CACHE_ENTRIES)
        self.assertLessEqual(chunk_scaling._axis_cache_bytes, chunk_scaling.MAX_AXIS_CACHE_BYTES)
        self.assertEqual(chunk_scaling._axis_cache_bytes,
                         sum(s.get_pitch() * s.get_height() for s in chunk_scaling._axis_cache.values()))

    def test_programmatic_giant_scale_keeps_only_visible_axis_samples(self):
        source = pygame.Surface((2, 2))
        source.fill((40, 70, 90))
        target = pygame.Surface((8, 8))
        with patch('pygame.transform.scale', side_effect=AssertionError('giant allocation')):
            blit_large_chunk(target, source, pygame.Rect(-500000000, -500000000, 1000000000, 1000000000))
        self.assertEqual(target.get_at((4, 4))[:3], (40, 70, 90))
