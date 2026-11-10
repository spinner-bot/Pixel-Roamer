import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from maps import list_maps
from pixel_roamer.ui.map_selector import MapSelector


class MapSelectorTests(unittest.TestCase):
    def make_selector(self):
        app = SimpleNamespace(_dev_selected_id=sorted(list_maps())[0], scale=0.5,
                              draw_offset_x=40, draw_offset_y=20,
                              logic_surface=pygame.Surface((1600, 900)), set_page=Mock(),
                              map_browser=SimpleNamespace(handle_dev_input=Mock()))
        return MapSelector(app), app

    def test_drawing_and_selection_never_generate_worlds(self):
        selector, app = self.make_selector()
        with patch("maps._load_map", side_effect=AssertionError("picker generated a world")):
            selector.draw(1 / 60)
            selector.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END))
            self.assertEqual(app._dev_selected_id, max(list_maps()))
            selector.draw(1 / 60)
            selector.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME))
            self.assertEqual(app._dev_selected_id, min(list_maps()))

    def test_scaled_row_pointer_hit_and_double_click_target(self):
        selector, app = self.make_selector()
        _, rows = selector._rows()
        map_id, rect = rows[1]
        point = (rect.centerx * app.scale + app.draw_offset_x,
                 rect.centery * app.scale + app.draw_offset_y)
        selector.handle_input(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point, clicks=2))
        self.assertEqual(app._dev_selected_id, map_id)
        app.set_page.assert_called_once_with(3, map_id=map_id)

    def test_preview_cache_is_bounded_when_browsing_all_maps(self):
        selector, app = self.make_selector()
        for map_id in list_maps():
            selector._preview(map_id)
        self.assertLessEqual(len(selector.previews), 8)


if __name__ == "__main__":
    unittest.main()
