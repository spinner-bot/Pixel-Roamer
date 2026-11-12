import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
import pygame
from block_type import BlockType
import pattern
from world import World, MAX_TERRAIN_TEXTURES


class RenderCacheTests(unittest.TestCase):
    def setUp(self):
        pattern.clear_pattern_cache()

    def tearDown(self):
        pattern.clear_pattern_cache()

    def test_pattern_lru_respects_bytes_and_preserves_reused_raster(self):
        blocks = [BlockType(i, pattern=('vector', (16, 16), (('fill', color),)))
                  for i, color in enumerate(((255, 0, 0), (0, 255, 0), (0, 0, 255)))]
        surface = pygame.Surface((32, 32))
        with patch('pattern.MAX_PATTERN_CACHE_BYTES', 8192):
            for index in (0, 1, 0, 2):
                pattern.render_block_pattern(surface, blocks[index], 0, 0, 32, 32, False)
                self.assertEqual(surface.get_at((16, 16))[:3], blocks[index].pattern[2][0][1])
            self.assertEqual(len(pattern._pattern_cache), 2)
            self.assertLessEqual(pattern._pattern_cache_bytes, 8192)
            self.assertEqual({s.get_at((0, 0))[:3] for s in pattern._pattern_cache.values()},
                             {(255, 0, 0), (0, 0, 255)})
        pattern.clear_pattern_cache()
        with patch('pattern.MAX_PATTERN_CACHE_BYTES', 100):
            pattern.render_block_pattern(surface, blocks[0], 0, 0, 32, 32, False)
            self.assertEqual(surface.get_at((0, 0))[:3], (255, 0, 0))
            self.assertEqual(pattern._pattern_cache_bytes, 0)
            self.assertFalse(pattern._pattern_cache)

    def test_chunk_rasterizes_each_definition_once_and_detects_appearance_changes(self):
        world = World(0, 'raster', 64, 32)
        world.begin_bulk_load()
        for x in range(64):
            for y in range(32):
                world.set_tile(x, y, 4)
        world.end_bulk_load()
        with patch('world.render_block_pattern', wraps=pattern.render_block_pattern) as render:
            world._render_chunk((0, 0))
            world._render_chunk((1, 0))
            self.assertEqual(render.call_count, 1)
        block = BlockType(9000, color=(10, 20, 30))
        self.assertEqual(world._terrain_texture(block).get_at((0, 0))[:3], block.color)
        block.color = (30, 20, 10)
        self.assertEqual(world._terrain_texture(block).get_at((0, 0))[:3], block.color)
        session = world.create_session()
        self.assertFalse(session._terrain_textures)
        self.assertIsNot(session._terrain_textures, world._terrain_textures)

    def test_terrain_cache_is_bounded_across_many_definitions(self):
        world = World(0, 'bounded', 1, 1)
        for i in range(MAX_TERRAIN_TEXTURES + 100):
            world._terrain_texture(BlockType(9000 + i, color=(i % 255, 30, 50)))
        self.assertEqual(len(world._terrain_textures), MAX_TERRAIN_TEXTURES)
