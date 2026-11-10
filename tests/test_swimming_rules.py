from collections import defaultdict
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
import pygame
from scripts.audit_swimming import exercise, make_session
from shore_exit import begin_shore_exit
from teleport import can_place, teleport_to


class SwimmingRuleTests(unittest.TestCase):
    def test_surface_exit_finishes_on_mirrored_banks_at_three_frame_rates(self):
        results = {}
        for side in ('left', 'right'):
            for fps in (30, 60, 144):
                with self.subTest(side=side, fps=fps):
                    run = exercise(side, fps, 20)
                    self.assertTrue(run['on_ground'])
                    self.assertFalse(run['pending'])
                    self.assertEqual(run['hp'], 100)
                    x, y = run['after_one_second']
                    self.assertLess(x, 1) if side == 'left' else self.assertGreater(x, 9)
                    self.assertAlmostEqual(y, 20.9)
                    results[side, fps] = x
        for fps in (30, 60, 144):
            self.assertAlmostEqual(results['left', fps] + results['right', fps], 10)
            self.assertAlmostEqual(results['left', fps], results['left', 60])

    def test_deep_water_never_starts_or_charges_surface_exit(self):
        for side in ('left', 'right'):
            for fps in (30, 60, 144):
                run = exercise(side, fps, 10)
                self.assertEqual(run['initial_surface'], 20)
                self.assertFalse(run['first_frame']['exit_buff'])
                self.assertFalse(run['first_frame']['pending'])
                self.assertGreater(run['first_frame']['stamina'], 199)
                self.assertFalse(run['on_ground'])

    def test_up_input_above_surface_does_not_snap_character_down(self):
        for side in ('left', 'right'):
            run = exercise(side, 60, 20.7)
            self.assertGreater(run['first_frame']['position'][1], 20.65)

    def test_exit_handles_character_dimensions_without_embedding(self):
        keys = defaultdict(bool, {pygame.K_w: True})
        with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
            for width, height in ((.6, 1.5), (.8, 1.8), (1.2, 2.6)):
                for side in ('left', 'right'):
                    session = make_session(side, 20, width, height)
                    player, world = session.app.player1, session.app._current_map
                    session.app.jump_pressed = True
                    for _ in range(120):
                        session.advance(1 / 120)
                        self.assertTrue(can_place(player, world, *player.get_center()))
                    self.assertTrue(player.on_ground, (width, height, side, player.get_center()))
                    self.assertFalse(getattr(player, '_shore_exit_pending', False))
                    self.assertAlmostEqual(player._y - height / 2, 20)

    def test_expiring_rise_clears_boost_velocity(self):
        session = make_session()
        player = session.app.player1
        self.assertTrue(begin_shore_exit(player))
        player.tick_buffs(.31)
        self.assertFalse(player._shore_exit_pending)
        self.assertLessEqual(player.v_y, 0)

    def test_teleport_cancels_shore_motion_instead_of_clamping_to_old_surface(self):
        session = make_session()
        player, world = session.app.player1, session.app._current_map
        self.assertTrue(begin_shore_exit(player))
        self.assertTrue(teleport_to(player, world, 5.5, 25))
        self.assertFalse(getattr(player, '_shore_exit_pending', False))
        self.assertFalse(player.can_swim)
        self.assertIsNone(player._swim_top_y)
