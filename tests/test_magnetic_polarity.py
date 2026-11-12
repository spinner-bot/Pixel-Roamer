"""Signed Buff parameters, not source IDs or input reversal, determine polarity."""
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from buff_parameters import magnetic_response
from scripts.control_session import create_control_session
from world import World
import pygame


def fixture(params=()):
    world = World(0, 'response bounds', 40, 20, gravity=0, spawn_points=(17, 5.5))
    world.set_tile(20, 5, 338)
    session = create_control_session(0, world=world)
    session.app.player1.apply_buff(49, params, 2)
    return session


class MagneticPolarityTests(unittest.TestCase):
    def test_signed_parameters_and_original_source_effects_with_no_keyboard_input(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'polarity.json'
            process = subprocess.run([sys.executable, 'scripts/audit_magnetic_polarity.py', '--output', str(output)],
                                     cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['parameters']), 72)
        baseline = {(r['fps'], r['side'], r['ore_polarity']): r['first_tick_vx']
                    for r in report['parameters'] if r['response_parameter'] is None}
        for row in report['parameters']:
            with self.subTest(row=row):
                response = row['response_parameter'] if row['response_parameter'] is not None else 1
                base = baseline[row['fps'], row['side'], row['ore_polarity']]
                self.assertAlmostEqual(row['first_tick_vx'], base * response)
                if response:
                    self.assertGreater(row['dx'] * row['side'] * row['ore_polarity'] * response, 0)
                else:
                    self.assertEqual(row['dx'], 0)
                self.assertEqual(row['hp'], 150)
                self.assertEqual(row['respawns'], 0)
        self.assertEqual(len(report['sources']), 9)
        for row in report['sources']:
            response = -1 if row['source_block'] == 411 else 1
            self.assertEqual(row['actual_params'], [response])
            self.assertEqual(row['actual_source'], row['source_block'])
            self.assertGreater(row['first_tick_vx'] * response, 0)
            self.assertIn('反向' if response < 0 else '正向', row['description'])

    def test_effective_bounds_match_descriptions_and_nonfinite_values_stay_safe(self):
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            base = fixture()
            base.advance(1 / 120)
            ordinary = base.app.player1.v_x
            for value, effective in ((0, 0), (.5, .5), (-.5, -.5), (2, 2), (-2, -2),
                                     (1e100, 4), (-1e100, -4), (math.nan, 0), (math.inf, 0), (-math.inf, 0)):
                with self.subTest(value=value):
                    session = fixture((value,))
                    actor = session.app.player1
                    session.advance(1 / 120)
                    self.assertEqual(magnetic_response((value,)), effective)
                    self.assertAlmostEqual(actor.v_x, ordinary * effective)
                    self.assertTrue(math.isfinite(actor.v_x))
                    text = actor.buffs[0].format_desc()
                    self.assertIn('正向' if effective > 0 else '反向' if effective < 0 else '不受磁力', text)
                    if abs(effective) == 4:
                        self.assertIn('4倍', text)

    def test_refresh_changes_response_without_accumulating_or_leaving_old_force(self):
        session = fixture()
        actor = session.app.player1
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.advance(1 / 120)
            positive = actor.v_x
            actor.reset_motion()
            for _ in range(100):
                actor.apply_buff(49, (-1,), 2)
            self.assertEqual(len([b for b in actor.buffs if b.buff_id == 49]), 1)
            session.advance(1 / 120)
            self.assertAlmostEqual(actor.v_x, -positive)
            actor.reset_motion()
            actor.apply_buff(49, (0,), 2)
            session.advance(1 / 120)
            self.assertEqual(actor.v_x, 0)
            actor.apply_buff(49, (-1,), .05)
            session.advance(.05)
            self.assertFalse(actor.has_buff(49))
            speed = actor.v_x
            session.advance(1 / 120)
            self.assertAlmostEqual(actor.v_x, speed * actor.f_x ** .5)

    def test_neutral_contact_blocks_magnetism_while_ordinary_contact_keeps_original_force(self):
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            for params, expected in ((None, -80 / 120), ((0,), 0), ((1,), -200 / 120), ((-1,), 200 / 120)):
                world = World(0, 'contact polarity', 40, 20, gravity=0, spawn_points=(20.5, 5.9))
                world.set_tile(20, 4, 338)
                session = create_control_session(0, world=world)
                actor = session.app.player1
                if params is not None:
                    actor.apply_buff(49, params, 2)
                session.advance(1 / 120)
                self.assertAlmostEqual(actor.v_y, expected)

    def test_clarity_and_iron_will_change_controls_without_erasing_reverse_polarity(self):
        for immunity in (None, 8, 40, 41):
            with self.subTest(immunity=immunity):
                world = World(0, 'independent reversal and field', 40, 20, gravity=-9.8,
                              spawn_points=(10.5, 5.9))
                for x in range(40):
                    world.set_tile(x, 4, 411 if x == 10 else 2)
                world.set_tile(13, 5, 338)
                session = create_control_session(0, world=world)
                actor = session.app.player1
                if immunity:
                    actor.apply_buff(immunity, (), 5)
                keys = defaultdict(bool)
                with patch('pygame.key.get_pressed', return_value=keys):
                    session.advance(1 / 120)
                    if immunity == 41:
                        self.assertEqual(actor.v_x, 0)
                    else:
                        self.assertLess(actor.v_x, 0)
                    actor.reset_motion()
                    keys[pygame.K_d] = True
                    session.advance(.25)
                buff = next(b for b in actor.buffs if b.buff_id == 49)
                self.assertEqual(buff.params, (-1,))
                self.assertEqual(buff.source, 411)
                if immunity in (8, 40):
                    self.assertGreater(actor._x, 10.5)
                else:
                    self.assertLess(actor._x, 10.5)
