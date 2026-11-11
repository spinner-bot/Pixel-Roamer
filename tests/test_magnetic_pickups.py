"""Behavioral acceptance for magnetic pickup collection and lifecycle."""
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
import pygame
from camera import Camera
from world import World
from scripts.control_session import create_control_session
from pixel_roamer.visual_effects import WorldEffects


def fixture(tiles, *, params=(), duration=5, position=(5.5, 4.5), loop=False):
    world = World(0, 'magnetic contract', 20, 12, gravity=0, spawn_points=position,
                  loop_x=loop, loop_y=loop)
    for x, y, tile_id in tiles:
        world.set_tile(x, y, tile_id)
    # Production get_map clones its template; the explicit fixture override
    # accepts a mutable world, so clone here before passing it to the app.
    session = create_control_session(0, world=world.create_session())
    session.app.player1.apply_buff(14, params, duration)
    return session, world


def advance(session, seconds):
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
        for _ in range(round(seconds * 120)):
            session.advance(1 / 120)


class MagneticPickupTests(unittest.TestCase):
    def test_all_pickup_kinds_mirrors_and_frame_rates_collect_once_with_buff(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'magnet.json'
            result = subprocess.run([sys.executable, 'scripts/audit_magnetic_pickups.py', '--output', str(path)],
                                    cwd=root, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rows = json.loads(path.read_text())['runs']
        self.assertEqual(len(rows), 120)
        for row in rows:
            with self.subTest(fps=row['fps'], kind=row['tile_id'], side=row['side'], active=row['buff_active']):
                self.assertEqual(row['score'], row['expected_score'])
                self.assertEqual(row['errors'], [])
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['position'], [5.5, 4.5])
                self.assertEqual(row['final_tile'], row['consumed_type_id'] if row['buff_active'] else row['tile_id'])
        session, _ = fixture([(8, 4, 310)])
        actor = session.app.player1
        advance(session, .1)
        score = actor.score
        actor.remove_buff(14)
        keys = defaultdict(bool)
        with patch('pygame.key.get_pressed', return_value=keys):
            for _ in range(360):
                error = max(-4, min(4, (8.5 - actor._x) * 3)) - actor.v_x
                keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
                session.advance(1 / 120)
        self.assertLess(abs(actor._x - 8.5), .1)
        self.assertEqual(actor.score, score)
        self.assertEqual(session.app._current_map.get_tile(8, 4).type_id, 320)

    def test_radius_parameters_and_solid_or_closed_corner_paths(self):
        cases = [([(9, 4, 310)], (), True), ([(10, 4, 310)], (), False),
                 ([(7, 4, 310)], (1,), False), ([(7, 4, 310)], (2,), True),
                 ([(6, 4, 310)], (-1,), False), ([(6, 4, 310)], (math.nan,), False),
                 ([(6, 4, 310)], (math.inf,), False),
                 ([(8, 4, 310), (6, 4, 2)], (), False),
                 ([(7, 6, 310), (6, 4, 2)], (), False),
                 ([(7, 6, 310)], (), True)]
        for tiles, params, expected in cases:
            with self.subTest(tiles=tiles, params=params):
                session, _ = fixture(tiles, params=params)
                advance(session, .2)
                self.assertEqual(session.app.player1.score > 0, expected)

    def test_looped_coordinates_are_deduplicated_and_sessions_do_not_share_consumption(self):
        for origin in ((19.5, 11.5), (-.5, -.5), (39.5, 23.5)):
            session, template = fixture([(1, 1, 314)], position=origin, loop=True)
            untouched = create_control_session(0, world=template.create_session())
            self.assertIsNot(session.app._current_map, untouched.app._current_map)
            self.assertIsNot(untouched.app._current_map, template)
            advance(session, .2)
            actor = session.app.player1
            self.assertEqual(actor.score, int(template.block_types[314].special_data))
            self.assertEqual(template.get_tile(1, 1).type_id, 314)
            self.assertEqual(untouched.app._current_map.get_tile(1, 1).type_id, 314)
            self.assertEqual(untouched.app.player1.score, 0)
            self.assertEqual(untouched.app.player1._pickup_flights, [])
            self.assertEqual(session.app._current_map.get_tile(1, 1).type_id, 324)

    def test_expiry_removal_pause_focus_stun_and_respawn_have_explicit_lifecycles(self):
        for action in ('expiry', 'remove', 'clear', 'reset'):
            session, _ = fixture([(6, 4, 310)], duration=.05 if action == 'expiry' else 5)
            actor, world = session.app.player1, session.app._current_map
            advance(session, .1)
            score = actor.score
            self.assertGreater(score, 0)
            if action == 'remove':
                actor.remove_buff(14)
            elif action == 'clear':
                actor.clear_buffs()
            elif action == 'reset':
                actor.take_raw_damage(1000)
                advance(session, 1 / 120)
                self.assertTrue(actor.alive)
                self.assertEqual(actor._pickup_flights, [])
            self.assertFalse(actor.has_buff(14))
            world.set_tile(7, 4, 310)
            advance(session, 1)
            self.assertEqual(actor.score, score)
            self.assertEqual(world.get_tile(7, 4).type_id, 310)
            self.assertEqual(actor._pickup_flights, [])
        session, _ = fixture([(6, 4, 310)])
        actor = session.app.player1
        for field in ('help_open', 'focused'):
            setattr(session.app, field, field == 'help_open')
            before = (actor.score, actor._buff_game_time, session.app._game_timer)
            session.advance(17)
            self.assertEqual((actor.score, actor._buff_game_time, session.app._game_timer), before)
            setattr(session.app, field, field != 'help_open')
        actor.apply_buff(28, (), .5)
        advance(session, .1)
        self.assertGreater(actor.score, 0)  # Magnetic attraction is a passive timed effect.

    def test_visible_flights_expire_and_extreme_radius_and_zoom_stay_bounded(self):
        session, _ = fixture([(8, 4, 310)])
        actor, world = session.app.player1, session.app._current_map
        advance(session, 1 / 120)
        self.assertEqual(len(actor._pickup_flights), 1)
        surface = pygame.Surface((400, 300))
        camera = Camera(400, 300, world)
        camera.follow(*actor.get_center())
        world.draw(surface, camera)
        before = pygame.image.tobytes(surface, 'RGBA')
        effects = WorldEffects()
        effects.draw(surface, actor, camera, world)
        self.assertNotEqual(pygame.image.tobytes(surface, 'RGBA'), before)
        camera.scale = 1e9
        effects.draw(surface, actor, camera, world)  # No huge surface or overflowing offscreen blit.
        advance(session, .6)
        self.assertEqual(actor._pickup_flights, [])
        dense, _ = fixture([(x, y, 310) for x in range(20) for y in range(12)], params=(1e9,))
        advance(dense, 1 / 120)
        self.assertGreater(dense.app.player1.score, 64)
        self.assertLessEqual(len(dense.app.player1._pickup_flights), 64)
