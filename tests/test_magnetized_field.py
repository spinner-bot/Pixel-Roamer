"""Magnetized49 must act nearby, remain escapable and stop with its lifetime."""
from collections import defaultdict
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from block_types_data import BLOCK_TYPES
from environment_forces import apply_magnetism
from scripts.control_session import create_control_session
from world import World


def fixture(distance=3.5, duration=2):
    ore = replace(BLOCK_TYPES[338], id=5000, special_data=8)
    world = World(0, 'magnetized lifecycle', 40, 16, gravity=0,
                  spawn_points=(20.5 - distance, 5.5), block_types={**BLOCK_TYPES, 5000: ore})
    world.set_tile(20, 5, 5000)
    session = create_control_session(0, world=world)
    session.app.player1.apply_buff(49, (), duration)
    return session, world


class MagnetizedFieldTests(unittest.TestCase):
    def test_range_polarities_immunities_real_source_retreat_and_loop_deduplication(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'field.json'
            process = subprocess.run([sys.executable, 'scripts/audit_magnetized_field.py', '--output', str(output)],
                                     cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 96)
        for row in report['runs']:
            with self.subTest(row=row):
                if row['distance'] in (1.5, 3.5) and row['active']:
                    self.assertGreater(row['dx'] * row['side'] * row['polarity'], 0)
                elif row['distance'] >= 1.5:
                    self.assertEqual(row['dx'], 0)
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['hp'], 150)
        self.assertEqual(len(report['immune']), 36)
        self.assertTrue(all(row['dx'] == 0 for row in report['immune']))
        self.assertEqual(len(report['escape']), 18)
        self.assertTrue(all(row['escaped'] and row['hp'] == 150 and row['lives_left'] == 3 for row in report['escape']))
        self.assertEqual(len(report['loop']), 18)
        self.assertLess(max(row['error'] for row in report['loop']), 1e-10)
        for row in report['reversed_source']:
            self.assertEqual(row['obtained'], {'23': 411, '49': 411})
            self.assertGreater(row['retreat'], 1)
            self.assertEqual(row['hp'], 150)
            self.assertEqual(row['respawns'], 0)
            self.assertAlmostEqual(row['min_foot_y'], 5)
            self.assertTrue(row['remaining49'] and row['remaining23'])

    def test_field_strength_decays_to_zero_without_extending_ordinary_contact_range(self):
        speeds = []
        for distance in (.9, 1., 1.5, 2.5, 3.5, 3.99, 4., 4.01, 5.):
            session, world = fixture(distance)
            actor = session.app.player1
            apply_magnetism(actor, world, [], 1 / 120)
            speeds.append(actor.v_x)
            self.assertEqual(actor.v_y, 0)
        self.assertAlmostEqual(speeds[0], 200 / 120)
        self.assertTrue(all(a > b for a, b in zip(speeds[:6], speeds[1:7])))
        self.assertEqual(speeds[6:], [0, 0, 0])
        session, world = fixture(1.5)
        actor = session.app.player1
        actor.remove_buff(49)
        apply_magnetism(actor, world, [], .1)
        self.assertEqual((actor.v_x, actor.v_y), (0, 0))

    def test_pause_focus_removal_clear_expiry_and_real_respawn_leave_no_residual_field(self):
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            for mode in ('remove', 'clear', 'expire'):
                session, _ = fixture(duration=.1 if mode == 'expire' else 2)
                actor = session.app.player1
                for _ in range(12 if mode == 'expire' else 6):
                    session.advance(1 / 120)
                self.assertGreater(actor.v_x, 0)
                if mode == 'remove':
                    actor.remove_buff(49)
                elif mode == 'clear':
                    actor.clear_buffs()
                self.assertFalse(actor.has_buff(49))
                speed = actor.v_x
                session.advance(1 / 120)
                self.assertAlmostEqual(actor.v_x, speed * actor.f_x ** .5)
            session, _ = fixture()
            actor = session.app.player1
            session.advance(.05)
            for flag, frozen in (('help_open', True), ('focused', False)):
                before = actor.get_center(), actor.v_x, actor.buffs[0].duration, session.app._game_timer
                setattr(session.app, flag, frozen)
                session.advance(1)
                self.assertEqual((actor.get_center(), actor.v_x, actor.buffs[0].duration, session.app._game_timer), before)
                setattr(session.app, flag, not frozen)
            actor.take_raw_damage(10000, bypass_shield=True)
            session.advance(1 / 120)
            self.assertTrue(actor.alive)
            self.assertFalse(actor.has_buff(49))
            self.assertEqual((actor.v_x, actor.v_y), (0, 0))

    def test_multiple_nearby_sources_are_limited_after_summing(self):
        session, world = fixture()
        world.set_tile(20, 6, 5000)
        actor = session.app.player1
        actor.a_x = -8
        apply_magnetism(actor, world, [], .25)
        self.assertEqual(actor.v_x, 1.5)  # Aggregate magnetic increment <= 6 * dt.
        session, world = fixture()
        world.set_tile(13, 5, 5000)
        actor = session.app.player1
        apply_magnetism(actor, world, [], .25)
        self.assertAlmostEqual(actor.v_x, 0)
        self.assertEqual(actor.v_y, 0)
