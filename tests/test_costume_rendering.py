import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from costumes import COSTUMES, advance_costume_animation, render_costume_at_feet


class CostumeRenderingTests(unittest.TestCase):
    def test_all_costumes_align_visible_feet_and_center_after_scaling_and_flip(self):
        for costume_id in COSTUMES:
            for width, height in ((16, 32), (36, 81), (45, 101)):
                for flip in (False, True):
                    surface = pygame.Surface((200, 200), pygame.SRCALPHA)
                    rect = render_costume_at_feet(surface, costume_id, 100, 140, width, height, flip_h=flip)
                    actual = surface.get_bounding_rect()
                    self.assertEqual(actual, rect)
                    self.assertEqual(actual.bottom, 140)
                    self.assertLessEqual(abs(actual.centerx - 100), 1)

    def test_animation_time_partition_and_state_changes(self):
        frames = []
        with patch("costumes.get_costume_anim_info", return_value={"idle": 1, "walk": 4, "jump": 1}):
            for steps in ([0.75], [0.15] * 5, [0.01] * 75):
                player = SimpleNamespace(costume_id=1, _anim_timer=0, _anim_frame=0)
                for dt in steps:
                    advance_costume_animation(player, "walk", dt)
                frames.append(player._anim_frame)
                self.assertAlmostEqual(player._anim_timer, 0)
                advance_costume_animation(player, "idle", 0)
                self.assertEqual(player._anim_frame, 0)
            self.assertEqual(frames, [1, 1, 1])


if __name__ == "__main__":
    unittest.main()
