"""Real cold sources, finite freeze, controls and full exposure lifecycle."""
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
from buff_controls import action_blocked
from scripts.control_session import create_control_session, terminal_snapshot
from shore_exit import begin_shore_exit
from world import World

ROOT = Path(__file__).resolve().parents[1]


class ChilledWaterTests(unittest.TestCase):
    def probe(self, *flags):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'water.json'
            result = subprocess.run([sys.executable, 'scripts/audit_chilled_water.py',
                                     '--output', str(path), *flags], cwd=ROOT,
                                    capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(path.read_text())

    def session(self, *, cold=True, water=True, spawn=(5.5, 5.9)):
        world = World(0, 'cold lifecycle fixture', 32, 32, gravity=-9.8, spawn_points=spawn)
        world.lives = 5
        for x in range(32):
            world.set_tile(x, 4, 373 if cold and x == 5 else 2)
        if water:
            for y in range(5, 12):
                world.set_tile(5, y, 7)
        session = create_control_session(0, world=world)
        return session, session.app._current_map

    def test_all_original_cold_sources_freeze_once_for_four_seconds_then_restore_controls(self):
        rows = self.probe()['rows']
        self.assertEqual(len(rows), 21)
        for row in rows:
            expected = row['liquid'] == 7 and row['source'] != 2
            with self.subTest(source=row['source'], liquid=row['liquid'], fps=row['fps']):
                self.assertEqual(len(row['freeze_applications']), int(expected))
                self.assertEqual(row['frozen_frames'], row['fps'] * 4 if expected else 0)
                if not expected:
                    continue
                self.assertIsNotNone(row['first_water'])
                self.assertIn({'id': 51, 'source': row['source']}, row['source_acquisition'])
                self.assertNotIn(21, [b['id'] for b in row['source_acquisition']])
                event = row['freeze_applications'][0]
                self.assertEqual(event['duration'], 4)
                self.assertEqual(event['source'], 'reaction:cold_water')
                frozen = [s for s in row['trace'] if s['frozen']]
                self.assertTrue(frozen)
                self.assertTrue(all(abs(s['velocity'][0]) < 1e-10 for s in frozen))
                self.assertTrue(all(s['velocity'][1] <= 1e-10 for s in frozen))
                last = frozen[-1]['time']
                self.assertTrue(any(s['time'] > last and not s['frozen']
                                    and s['velocity'][0] > .1 for s in row['trace']))
                self.assertTrue(all(s['hp'] == 150 for s in row['trace']))

    def test_original_sources_still_apply_cold_under_iron_will_without_freezing(self):
        rows = self.probe('--immune')['rows']
        self.assertEqual(len(rows), 21)
        for row in rows:
            with self.subTest(source=row['source'], liquid=row['liquid'], fps=row['fps']):
                self.assertTrue(row['immune_api40'])
                self.assertEqual(row['freeze_applications'], [])
                self.assertEqual(row['frozen_frames'], 0)
                if row['source'] != 2:
                    self.assertIn({'id': 51, 'source': row['source']}, row['source_acquisition'])

    def test_halt_cancels_climb_and_shore_but_gravity_and_recovery_continue(self):
        session, world = self.session(cold=False, water=False, spawn=(5.5, 9))
        actor, keys = session.app.player1, defaultdict(bool)
        for y in range(5, 16):
            world.set_tile(5, y, 10)
        with patch('pygame.key.get_pressed', return_value=keys):
            session.advance(1 / 120)
            self.assertTrue(actor.try_start_climbing(world))
            actor._shore_exit_pending = 'rise'  # API lifecycle isolation, not route evidence.
            actor.v_x, actor.v_y, actor.a_x = 3, 4, 2
            actor.apply_buff(59, (), .5)
            self.assertFalse(actor.is_climbing)
            self.assertFalse(actor._shore_exit_pending)
            self.assertIsNone(actor._climb_align_target)
            self.assertEqual((actor.v_x, actor.v_y, actor.a_x), (0, 0, 0))
            actor.move(1)
            self.assertEqual(actor.a_x, 0)
            self.assertFalse(actor.jump(not_on_ground_ok=True))
            self.assertFalse(actor.try_start_climbing(world))
            self.assertFalse(begin_shore_exit(actor))
            x, y, stamina = actor._x, actor._y, actor.stamina
            keys[pygame.K_d] = keys[pygame.K_w] = True
            session.app.jump_pressed = True
            session.advance(.2)
            self.assertAlmostEqual(actor._x, x)
            self.assertLess(actor._y, y - .05)
            self.assertLess(actor.v_y, 0)
            self.assertGreaterEqual(actor.stamina, stamina)
            self.assertFalse(session.app.jump_pressed)
            keys[pygame.K_d] = False
            session.advance(.4)
            self.assertFalse(actor.has_buff(59))
            self.assertTrue(actor.is_climbing)

    def test_pause_focus_and_terminal_state_preserve_frozen_lifetime_and_motion(self):
        session, _ = self.session()
        actor = session.app.player1
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.advance(1 / 120)
            self.assertTrue(actor.has_buff(59))
            for field in ('help_open', 'focused', '_game_win', '_game_over'):
                previous = getattr(session.app, field)
                setattr(session.app, field, False if field == 'focused' else True)
                before = terminal_snapshot(session)
                session.app.jump_pressed = True
                session.advance(17)
                self.assertEqual(terminal_snapshot(session), before)
                self.assertFalse(session.app.jump_pressed)
                setattr(session.app, field, previous)
            session.advance(.2)
            self.assertLess(next(b.duration for b in actor.buffs if b.buff_id == 59), 4)

    def test_continuous_contact_cleanse_immunity_and_complete_dry_reentry(self):
        session, world = self.session()
        actor = session.app.player1
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.advance(1 / 120)
            session.advance(4.1)
            self.assertFalse(actor.has_buff(59))
            self.assertTrue(actor.has_buff(51))
            self.assertTrue(actor.has_buff(15))
            session.advance(2)
            self.assertFalse(actor.has_buff(59))
            actor._x = 12.5  # Explicit API placements isolate dry/rewet, not normal travel.
            actor.collide_with_world(world, 0)
            session.advance(1.1)
            self.assertFalse(actor.has_buff(15))
            actor._x = 5.5
            actor.collide_with_world(world, 0)
            self.assertTrue(actor.has_buff(59))
            actor.apply_buff(12, (.01,), .1)
            session.advance(.03)
            self.assertFalse(actor.has_buff(59))
            self.assertFalse(action_blocked(actor, 'horizontal'))
            session.advance(.2)
            self.assertFalse(actor.has_buff(59))
            actor.apply_buff(40, (), .1)
            session.advance(.2)
            self.assertFalse(actor.has_buff(40))
            self.assertFalse(actor.has_buff(59))

    def test_actual_respawn_rearms_new_exposure_and_flight_clears_memory(self):
        session, world = self.session()
        actor = session.app.player1
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.advance(1 / 120)
            self.assertTrue(actor.has_buff(59))
            actor.apply_buff(40, (), 1)
            self.assertFalse(actor.has_buff(59))
            actor.take_damage(actor.hp_max * 10, 0)
            self.assertFalse(actor.alive)
            session.advance(1 / 120)
            self.assertEqual(session.app._player_lives_left, 4)
            self.assertTrue(actor.has_buff(36))
            self.assertFalse(actor.has_buff(40))
            self.assertTrue(actor.has_buff(59))
            self.assertEqual(actor._buff_reaction_latches, {'cold_water'})
            actor.fly_mode = True
            session.advance(1 / 120)
            self.assertEqual(actor._buff_reaction_latches, set())
            self.assertIsNone(actor._buff_reaction_world)

    def test_water_semantics_exclude_lava_and_damage_liquid_without_source_id_special_case(self):
        for liquid, expected in ((7, True), (8, False), (6, False), (5000, True), (5001, False)):
            session, world = self.session(water=False)
            world.block_types = dict(world.block_types)
            world.block_types[5000] = replace(BLOCK_TYPES[7], id=5000, name='fixture_other_water')
            world.block_types[5001] = replace(BLOCK_TYPES[7], id=5001, name='fixture_damage_water', damage_ps=1)
            world.set_tile(5, 5, liquid)
            actor = session.app.player1
            # dt0 isolates source/contact semantics from lava damage ticks.
            actor.collide_with_world(world, 0)
            with self.subTest(liquid=liquid):
                self.assertTrue(actor.has_buff(51))
                self.assertEqual(actor.has_buff(59), expected)
                self.assertEqual(actor.has_buff(15), expected)
