import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import home_page


class HomeMenuTests(unittest.TestCase):
    def test_every_button_hit_matches_its_drawn_rect_after_window_scaling(self):
        for scale, offset in ((1, (0, 0)), (0.5, (40, 90)), (0.8, (0, 0))):
            for index, rect in enumerate(home_page.menu_layout(1600, 900)):
                point = (rect.centerx * scale + offset[0], rect.centery * scale + offset[1])
                action = home_page.handle_home_mouse(point, 1600, 900, scale, *offset)
                self.assertEqual(action, index)
                self.assertEqual(home_page.get_selected_action(), action)
            self.assertIsNone(home_page.handle_home_mouse((0, 0), 1600, 900, scale, *offset))

    def test_menu_randomness_does_not_change_map_random_state(self):
        random.seed(937)
        before = random.getstate()
        home_page.init_home_page(1600, 900)
        self.assertEqual(random.getstate(), before)


if __name__ == "__main__":
    unittest.main()
