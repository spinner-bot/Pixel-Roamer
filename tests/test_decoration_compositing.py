"""Explicit RGBA canvases compose without treating opaque black as empty."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from scripts.audit_decoration_compositing import rgba_case, scene
from block_types_data import BLOCK_TYPES
from world import World


class DecorationCompositingTests(unittest.TestCase):
    def test_rgba_canvas_matches_reference_for_direct_and_chunk_paths(self):
        for background in (0, 11, 12):
            for alpha in (0, 128):
                with self.subTest(background=background, alpha=alpha):
                    result = rgba_case(background, alpha)
                    self.assertTrue(result['direct_matches'], result)
                    self.assertTrue(result['chunk_matches'], result)
                    self.assertTrue(result['opaque_motif_preserved'])

    def test_opaque_black_and_stone_keep_their_opaque_rendering(self):
        for background in (0, 11, 12):
            with self.subTest(background=background):
                self.assertTrue(scene(background)['opaque_black_preserved'])
                world = World(0, 'opaque texture', 2, 2, default_block_id=background)
                for block_id in (2, 12):
                    texture = world._terrain_texture(BLOCK_TYPES[block_id])
                    self.assertEqual(texture.get_at((0, 0)).a, 255)
