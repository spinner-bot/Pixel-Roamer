import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from pixel_roamer.ui.references import ReferenceBrowser


class ReferenceBrowserTests(unittest.TestCase):
    def make_browser(self):
        fields = {"scale": 0.5, "draw_offset_x": 40, "draw_offset_y": 20}
        for kind in ("block", "buff"):
            fields[f"_dev_{kind}_browser"] = kind == "block"
            fields[f"_dev_{kind}_detail_id"] = None
            for key, value in {"cursor": 0, "scroll": 0, "mode": "grid", "show_name2": True}.items():
                fields[f"_dev_{kind}_browser_{key}"] = value
        app = SimpleNamespace(**fields)
        return ReferenceBrowser(app), app

    def test_pointer_details_and_back_match_scaled_card_positions(self):
        browser, app = self.make_browser()
        index, block_id, rect = browser._layout("block")[1][1]
        pos = (rect.centerx * .5 + 40, rect.centery * .5 + 20)
        browser._handle_block_browser_input(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        self.assertEqual(app._dev_block_detail_id, block_id)
        browser._handle_block_browser_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertIsNone(app._dev_block_detail_id)
        self.assertTrue(app._dev_block_browser)

    def test_catalog_switch_scroll_and_end_navigation(self):
        browser, app = self.make_browser()
        browser._handle_block_browser_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_u))
        self.assertTrue(app._dev_buff_browser)
        self.assertFalse(app._dev_block_browser)
        browser._handle_buff_browser_input(pygame.event.Event(pygame.MOUSEWHEEL, y=-1))
        self.assertEqual(app._dev_buff_browser_cursor, 8)
        browser._handle_buff_browser_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END))
        self.assertEqual(app._dev_buff_browser_cursor, len(browser._catalog("buff")) - 1)

    def test_all_preview_sizes_stay_within_memory_budget(self):
        browser, _ = self.make_browser()
        for kind in ("block", "buff"):
            for item in browser._catalog(kind).values():
                browser._image(kind, item, 320)
                self.assertLessEqual(browser._image_bytes, browser.CACHE_BYTES)
        surface = pygame.Surface((1600, 900))
        browser._draw("block", surface, 0)


if __name__ == "__main__":
    unittest.main()
