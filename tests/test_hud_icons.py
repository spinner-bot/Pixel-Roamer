"""The HUD reuses icon rasters and bounds memory across sizes."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
from pixel_roamer.ui.hud import HudRenderer
from resource_catalog import load_buffs
import pattern


class HudIconTests(unittest.TestCase):
    def test_rasterization_is_reused_and_variants_are_bounded(self):
        renderer = HudRenderer(None)
        buff = load_buffs()[1]
        with patch('pattern._draw_vector', wraps=pattern._draw_vector) as draw:
            first = renderer._buff_icon(buff, 24)
            for _ in range(120):
                self.assertIs(renderer._buff_icon(buff, 24), first)
            self.assertEqual(draw.call_count, 1)
        for size in range(1, 150):
            renderer._buff_icon(buff, size)
        self.assertLessEqual(len(renderer._icons), 128)
