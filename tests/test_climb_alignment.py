"""Centering must be continuous and stop when its original capture ends."""
import json
from collections import defaultdict
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import pygame
from creature import Player
from world import World
from teleport import can_place, teleport_to
from scripts.audit_held_climb import make_session


def captured():
    world = World(0, 'alignment lifecycle', 20, 20, gravity=0)
    for y in range(1, 16):
        world.set_tile(5, y, 9)
    actor = Player(0, 'alignment', 6.4, 10, {})
    actor.collide_with_world(world, 0)
    assert actor.try_start_climbing(world)
    return actor, world


class ClimbAlignmentTests(unittest.TestCase):
    def test_mirrors_bodies_input_modes_and_loop_translations(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'alignment.json'
            result = subprocess.run([sys.executable, 'scripts/audit_climb_alignment.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=40)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 144)
        self.assertTrue(all(not r['continuous_capture'] for r in report['before']))
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps'], body=after['body'], side=after['side'], mode=after['mode'], offset=after['offset']):
                self.assertTrue(after['continuous_capture'])
                self.assertTrue(after['aligned_final'] and after['is_climbing'])
                self.assertEqual(after['errors'], [])
                self.assertLessEqual(after['max_event_dx'], 1e-8)
                self.assertLessEqual(after['max_fixed_step_dx'], .05 + 1e-8)
                self.assertEqual(after['hp'], 150)
                self.assertAlmostEqual(after['position'][0], before['position'][0])
                self.assertAlmostEqual(after['position'][1], before['position'][1])
                self.assertAlmostEqual(after['stamina'], before['stamina'])

    def test_releasing_and_jumping_cancel_incomplete_alignment(self):
        for action in ('release', 'jump'):
            actor, world = captured()
            self.assertEqual(actor._x, 6.4)
            if action == 'release':
                actor.stop_climbing()
            else:
                self.assertTrue(actor.jump())
            self.assertIsNone(actor._climb_align_target)
            actor.update_physics(.05, world)
            actor.collide_with_world(world, .05)
            self.assertEqual(actor._x, 6.4)
            self.assertFalse(actor.is_climbing)

    def test_new_wall_cancels_alignment_before_entering_it(self):
        actor, world = captured()
        world.set_tile(5, 10, 2)
        self.assertTrue(can_place(actor, world, *actor.get_center()))
        actor.update_physics(1 / 120, world)
        actor.collide_with_world(world, 1 / 120)
        self.assertEqual(actor._x, 6.4)
        self.assertFalse(actor.is_climbing)
        self.assertIsNone(actor._climb_align_target)
        self.assertTrue(can_place(actor, world, *actor.get_center()))

    def test_respawn_portal_and_spawn_callback_drop_old_destination(self):
        for action in ('reset', 'portal', 'callback'):
            actor, world = captured()
            if action == 'reset':
                actor.reset(10.5, 10)
            elif action == 'portal':
                self.assertTrue(teleport_to(actor, world, 10.5, 10))
            else:
                actor.spawn_pos = (10.5, 10)
                actor._dispatch_buff_callback('teleport_spawn')
            self.assertIsNone(actor._climb_align_target)
            actor.update_physics(.05, world)
            actor.collide_with_world(world, .05)
            self.assertEqual(actor.get_center(), (10.5, 10))

    def test_out_of_band_relocation_cannot_be_pulled_back_to_old_ladder(self):
        actor, world = captured()
        actor._x = 15.5
        actor.update_physics(1 / 120, world)
        self.assertEqual(actor._x, 15.5)
        self.assertFalse(actor.is_climbing)
        self.assertIsNone(actor._climb_align_target)

    def test_pause_focus_and_terminal_guards_freeze_pending_alignment(self):
        session = make_session(4.61)
        app, actor = session.app, session.app.player1
        actor.collide_with_world(app._current_map, 0)
        self.assertTrue(actor.try_start_climbing(app._current_map))
        keys = defaultdict(bool, {pygame.K_w: True})
        with patch('pygame.key.get_pressed', return_value=keys):
            for field, value in (('help_open', True), ('focused', False), ('_game_win', True), ('_game_over', True)):
                old = getattr(app, field)
                before = actor.get_center(), actor._climb_align_target
                setattr(app, field, value)
                session.advance(.25)
                self.assertEqual((actor.get_center(), actor._climb_align_target), before)
                setattr(app, field, old)
            session.advance(.2)
        self.assertEqual(actor._x, 5.5)
        self.assertIsNone(actor._climb_align_target)

    def test_stun_freezes_alignment_and_iron_will_resumes_it(self):
        session = make_session(4.61)
        actor = session.app.player1
        actor.collide_with_world(session.app._current_map, 0)
        self.assertTrue(actor.try_start_climbing(session.app._current_map))
        actor.apply_buff(28, (), 10)
        before = actor.get_center(), actor._climb_align_target
        keys = defaultdict(bool, {pygame.K_w: True})
        with patch('pygame.key.get_pressed', return_value=keys):
            session.advance(.1)
            self.assertEqual((actor.get_center(), actor._climb_align_target), before)
            actor.apply_buff(40, (), 10)
            session.advance(.2)
        self.assertEqual(actor._x, 5.5)
        self.assertIsNone(actor._climb_align_target)
