"""Collision restoration is a lifecycle rule, including stunned and flying players."""
from collections import defaultdict
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
from scripts.control_session import create_control_session
from teleport import can_place
from world import World
from collision import CONTACT_EPSILON


def session_fixture():
    world = World(0, 'noclip guards', 20, 20, gravity=0, spawn_points=(3.5, 5.5))
    world.set_tile(5, 5, 19)
    return create_control_session(0, world=world)


def toggle_flight(app):
    with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)]):
        app._handle_events()


class NoclipLifecycleTests(unittest.TestCase):
    def test_flight_and_stunned_expiry_are_safe_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'noclip.json'
            result = subprocess.run([sys.executable, 'scripts/audit_noclip_lifecycle.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['after']), 15)
        self.assertEqual(sum(r['final_clear'] for r in report['before']), 3)
        for run in report['after']:
            with self.subTest(case=run['case'], fps=run['fps']):
                self.assertTrue(run['first_after_change']['clear'])
                self.assertTrue(run['final_clear'])
                self.assertEqual(run['hp'], 150)
                self.assertEqual(run['stamina'], 200)
                self.assertEqual(run['respawns'], 0)
                self.assertFalse(run['ghost'])
                self.assertFalse(run['flight'])
                self.assertEqual(run['stunned'], run['case'].endswith('stunned'))
                if run['case'] == 'flight_clear':
                    self.assertLess(abs(run['first_after_change']['position'][0] - run['before_change']['position'][0]), .05)

    def test_stunned_rollback_clears_stale_environment_without_waiting_for_stun_to_end(self):
        session = session_fixture()
        player, world = session.app.player1, session.app._current_map
        player.apply_buff(48, (), 1)
        player.collide_with_world(world, 0)
        player._x = 5.5
        player._silenced, player._berserk_active = True, True
        player.phys_atk = player._base_phys_atk * 2.5
        player.apply_buff(28, (), 2)
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.advance(1.1)
        self.assertTrue(player.has_buff(28))
        self.assertFalse(player.has_buff(48))
        self.assertEqual(player.get_center(), world.spawn_points)
        self.assertFalse(player._silenced)
        self.assertFalse(player._berserk_active)
        self.assertEqual(player.phys_atk, player._base_phys_atk)
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_pause_and_terminal_guards_do_not_relocate_a_frozen_world(self):
        for guard in ('help_open', '_game_win', '_game_over'):
            with self.subTest(guard=guard):
                session = session_fixture()
                player, world = session.app.player1, session.app._current_map
                player.apply_buff(48, (), 5)
                player.collide_with_world(world, 0)
                player._x = 5.5
                player.remove_buff(48)
                setattr(session.app, guard, True)
                before = player.get_center(), player.hp, player.stamina, session.app._game_timer
                with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
                    session.advance(2)
                self.assertEqual((player.get_center(), player.hp, player.stamina, session.app._game_timer), before)

    def test_flight_exit_rechecks_anchor_before_falling_back_to_spawn(self):
        session = session_fixture()
        player, world = session.app.player1, session.app._current_map
        keys = defaultdict(bool, {pygame.K_d: True})
        with patch('pygame.key.get_pressed', return_value=keys):
            toggle_flight(session.app)
            for _ in range(15):
                session.advance(1 / 60)
            world.set_tile(4, 5, 19)
            toggle_flight(session.app)
            keys.clear()
            session.advance(1 / 60)
        self.assertEqual(player.get_center(), world.spawn_points)
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_flight_exit_respects_solid_boundaries_and_preserves_loop_coordinates(self):
        for loop_y in (False, True):
            with self.subTest(loop_y=loop_y):
                world = World(0, 'flight bounds', 10, 10, gravity=0, loop_y=loop_y, spawn_points=(5.5, 5.5))
                session = create_control_session(0, world=world)
                player = session.app.player1
                keys = defaultdict(bool, {pygame.K_s: True})
                with patch('pygame.key.get_pressed', return_value=keys):
                    toggle_flight(session.app)
                    for _ in range(60):
                        session.advance(1 / 60)
                    toggle_flight(session.app)
                    session.advance(1 / 60)
                self.assertTrue(can_place(player, world, *player.get_center()))
                if loop_y:
                    self.assertLess(player._y, 0)
                else:
                    self.assertGreaterEqual(player._y, player._h / 2 - CONTACT_EPSILON)
