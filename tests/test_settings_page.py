import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
import music
import sfx
from pixel_roamer.ui.settings import SettingsPage


class SettingsPageTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.volume = sfx.get_sfx_volume()
        self.app = SimpleNamespace(current_fps=70, _setting_selected_fps_idx=1,
                                   _setting_fps_just_autodetected=False, _setting_selected_row=0,
                                   _setting_from_page=3, scale=0.5, draw_offset_x=40,
                                   draw_offset_y=20, set_page_no_launch=Mock())
        self.page = SettingsPage(self.app)

    def tearDown(self):
        sfx.set_sfx_volume(self.volume)

    def event(self, kind, point):
        return pygame.event.Event(kind, button=1, pos=(point[0] * self.app.scale + 40,
                                                      point[1] * self.app.scale + 20))

    def test_fps_changes_relative_to_actual_value_and_clamps_at_limits(self):
        self.page._adjust_fps(-1)
        self.assertEqual(self.app.current_fps, 60)
        self.app.current_fps = 70
        self.page._adjust_fps(1)
        self.assertEqual(self.app.current_fps, 90)
        self.app.current_fps = 240
        self.page._adjust_fps(1)
        self.assertEqual(self.app.current_fps, 240)
        self.app.current_fps = 15
        self.page._adjust_fps(-1)
        self.assertEqual(self.app.current_fps, 15)

    def test_slider_click_drag_release_and_label_focus(self):
        sfx.set_sfx_volume(0.5)
        row = self.page.rows()[2]
        self.page.handle_setting_input(self.event(pygame.MOUSEBUTTONDOWN, (row.x + 20, row.centery)))
        self.assertEqual(sfx.get_sfx_volume(), 0.5)
        bar = self.page.slider(2)
        self.page.handle_setting_input(self.event(pygame.MOUSEBUTTONDOWN, (bar.x + bar.w * .75, bar.centery)))
        self.assertAlmostEqual(sfx.get_sfx_volume(), 0.75)
        self.page.handle_setting_input(self.event(pygame.MOUSEMOTION, (bar.right + 100, bar.centery)))
        self.assertEqual(sfx.get_sfx_volume(), 1)
        self.page.handle_setting_input(self.event(pygame.MOUSEBUTTONUP, (bar.right, bar.centery)))
        self.page.handle_setting_input(self.event(pygame.MOUSEMOTION, (bar.left, bar.centery)))
        self.assertEqual(sfx.get_sfx_volume(), 1)


if __name__ == "__main__":
    unittest.main()
