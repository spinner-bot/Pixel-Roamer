"""Single-layer wall traversal must retain gravity support and ceiling collision."""
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
from world import World


class GhostWallContractTests(unittest.TestCase):
    def test_mirrors_thickness_loop_seams_fractional_bodies_and_supporting_posts(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'ghost.json'
            result = subprocess.run([sys.executable, 'scripts/audit_ghost_wall_contract.py', '--extended', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['walls']), 72)
        self.assertEqual(len(report['extended_walls']), 216)
        self.assertEqual(len(report['extended_floors']), 54)
        for row in report['walls'] + report['extended_walls']:
            with self.subTest(row=row):
                expected = row['mode'] == 'phantom' or (row['mode'] != 'none' and row['thickness'] == 1)
                self.assertEqual(row['crossed'], expected)
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['hp'], 150)
                if row['mode'] == 'source':
                    self.assertEqual(row['applied']['source'], 384)
        for row in report['floors'] + report['extended_floors']:
            with self.subTest(floor=row):
                self.assertFalse(row['dropped_through_floor'])
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['hp'], 150)
                self.assertAlmostEqual(row['min_center_y'], 5 + row['size'][1] / 2)

    def test_jumping_into_full_or_isolated_ceilings_stays_solid(self):
        for width, height in ((.6, 1.5), (.8, 1.8), (1.4, 2.1)):
            for isolated in (False, True):
                for source in (False, True):
                    world = World(0, 'ghost ceiling', 24, 16, gravity=-9.8,
                                  spawn_points=(10.5, 5 + height / 2))
                    world.player_config = {'w': width, 'h': height}
                    for x in range(2, 22):
                        world.set_tile(x, 4, 2)
                    for x in ((10,) if isolated else range(2, 22)):
                        world.set_tile(x, 8, 384 if source else 2)
                    session = create_control_session(0, world=world)
                    actor = session.app.player1
                    if not source:
                        actor.apply_buff(48, (), 4)
                    touched = False
                    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
                        for _ in range(6):
                            session.advance(1 / 120)
                        self.assertTrue(actor.jump())
                        for _ in range(180):
                            session.advance(1 / 120)
                            self.assertLessEqual(actor._y + actor._h / 2, 8 + 1e-8)
                            self.assertGreaterEqual(actor._y - actor._h / 2, 5 - 1e-8)
                            touched |= actor.on_ceiling
                    self.assertTrue(touched)
                    self.assertTrue(actor.has_buff(48))

    def test_wall_traversal_under_gravity_keeps_floor_contact(self):
        for width, height in ((.6, 1.5), (.8, 1.8), (1.4, 2.1)):
            for direction in (-1, 1):
                for fps in (30, 60, 144):
                    for source in (False, True):
                        world = World(0, 'ghost wall and floor', 30, 16, gravity=-9.8,
                                      spawn_points=(6.5 if direction == 1 else 14.5, 5 + height / 2))
                        world.player_config = {'w': width, 'h': height}
                        for x in range(2, 28):
                            world.set_tile(x, 4, 2)
                        for y in range(5, 10):
                            world.set_tile(10, y, 384 if source else 19)
                        session = create_control_session(0, world=world)
                        actor = session.app.player1
                        if not source:
                            actor.apply_buff(48, (), 4)
                        keys = defaultdict(bool, {pygame.K_d if direction == 1 else pygame.K_a: True})
                        crossed = False
                        with patch('pygame.key.get_pressed', return_value=keys):
                            for _ in range(3 * fps):
                                session.advance(1 / fps)
                                self.assertAlmostEqual(actor._y - actor._h / 2, 5)
                                if (direction == 1 and actor._x - width / 2 >= 11
                                        or direction == -1 and actor._x + width / 2 <= 10):
                                    crossed = True
                                    break
                        self.assertTrue(crossed)
                        self.assertEqual(actor.hp, 150)
