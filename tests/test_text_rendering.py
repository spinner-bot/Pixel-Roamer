import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
import game_text


class TextRenderingTests(unittest.TestCase):
    def test_bundled_font_has_chinese_gameplay_glyphs_without_system_fonts(self):
        font = game_text._get_font("sans", 24)
        self.assertIn("Fusion Pixel", font.name)
        self.assertTrue(all(metric is not None for metric in font.get_metrics("像素漫游者黏土地图设置跳跃")))

    def test_transparent_animated_label_has_no_opaque_shadow(self):
        surface = pygame.Surface((320, 80))
        surface.fill((17, 34, 51))
        before = pygame.image.tobytes(surface, "RGB")
        width, height = game_text.draw(surface, "像素 Pixel", 10, 10, 24,
                                      (255, 255, 255, 0), "sans", shadow=True)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        self.assertEqual(before, pygame.image.tobytes(surface, "RGB"))


if __name__ == "__main__":
    unittest.main()
