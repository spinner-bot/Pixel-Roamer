"""Held input should grab ladders without cancelling jumps or overriding release."""
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import pygame
from scripts.audit_held_climb import make_session


class HeldClimbTests(unittest.TestCase):
    def advance(self, session, keys, dt=.25):
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool, keys)), patch('sfx.play_jump'):
            session.advance(dt)

    def keydown(self, session, key):
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=key)]):
            session.app._handle_events()

    def test_preheld_w_and_arrow_inputs_grab_from_both_sides_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'held.json'
            result = subprocess.run([sys.executable, 'scripts/audit_held_climb.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 12)
        self.assertTrue(all(not run['climbed'] for run in report['before']))
        for run in report['after']:
            with self.subTest(fps=run['fps'], side=run['side'], keys=run['keys']):
                self.assertTrue(run['climbed'])
                self.assertEqual(run['position'], [5.5, 13])
                self.assertEqual(run['hp'], 150)
                self.assertGreater(run['stamina'], 100)
                self.assertLess(run['stamina'], 200)

    def test_down_release_dominates_held_up_and_new_up_keydown(self):
        session = make_session(5.5)
        session.app.player1.collide_with_world(session.app._current_map, 0)
        self.advance(session, {pygame.K_w: True})
        self.assertTrue(session.app.player1.is_climbing)
        self.keydown(session, pygame.K_s)
        for _ in range(3):
            self.keydown(session, pygame.K_w)
            self.advance(session, {pygame.K_w: True, pygame.K_s: True}, .1)
            self.assertFalse(session.app.player1.is_climbing)

    def test_ground_jump_with_up_held_remains_airborne_during_ascent(self):
        session = make_session(5.5)
        player = session.app.player1
        player.collide_with_world(session.app._current_map, 0)
        self.keydown(session, pygame.K_SPACE)
        self.advance(session, {pygame.K_w: True}, .2)
        self.assertFalse(player.is_climbing)
        self.assertGreater(player.v_y, 9)
        self.assertGreater(player._y, 3)
        self.assertGreater(player.stamina, 180)

    def test_jump_from_climb_is_not_immediately_reattached(self):
        session = make_session(5.5)
        player = session.app.player1
        player.collide_with_world(session.app._current_map, 0)
        self.advance(session, {pygame.K_w: True}, .2)
        self.assertTrue(player.is_climbing)
        self.keydown(session, pygame.K_SPACE)
        self.advance(session, {pygame.K_w: True}, .2)
        self.assertFalse(player.is_climbing)
        self.assertGreater(player.v_y, 9)

    def test_stun_blocks_held_capture_and_iron_will_still_overrides_stun(self):
        session = make_session(5.5)
        player = session.app.player1
        player.collide_with_world(session.app._current_map, 0)
        player.apply_buff(28, (), 1)
        self.advance(session, {pygame.K_w: True})
        self.assertFalse(player.is_climbing)
        player.apply_buff(40, (), 10)
        self.advance(session, {pygame.K_w: True})
        self.assertTrue(player.is_climbing)
        self.assertGreater(player._y, 1.9)

    def test_up_without_contact_never_snaps_toward_ladder(self):
        session = make_session(3)
        self.advance(session, {pygame.K_w: True})
        self.assertFalse(session.app.player1.is_climbing)
        self.assertEqual(session.app.player1.get_center(), (3, 1.9))

    def test_insufficient_stamina_does_not_capture_and_flashes_existing_feedback(self):
        session = make_session(5.5)
        player = session.app.player1
        player.collide_with_world(session.app._current_map, 0)
        player.stamina = .5
        self.advance(session, {pygame.K_w: True}, 1 / 120)
        self.assertFalse(player.is_climbing)
        self.assertEqual(player.stamina, .5)
        self.assertGreater(session.app._stamina_flash_timer, 0)

    def test_held_up_can_catch_ladder_while_falling(self):
        session = make_session(5.5)
        player = session.app.player1
        player._y = 5.5
        player.v_y = -2
        player.collide_with_world(session.app._current_map, 0)
        self.advance(session, {pygame.K_w: True}, 1 / 120)
        self.assertTrue(player.is_climbing)
        self.assertGreater(player._y, 5.5)
