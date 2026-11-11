"""Jump input preserves existing upward launches without disabling weak boosts."""
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
from creature import Player
from scripts.control_session import create_control_session
from world import World


class LaunchJumpOverrideTests(unittest.TestCase):
    def test_all_existing_launch_sources_preserve_height_after_space(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'launch.json'
            process = subprocess.run([sys.executable, 'scripts/audit_launch_jump_override.py', '--output', str(output)],
                                     cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            rows = json.loads(output.read_text())['pairs']
        self.assertEqual(len(rows), 36)
        self.assertEqual({row['block_id'] for row in rows}, {71, 293, 294, 295, 296, 330, 331, 332, 389, 396, 415, 433})
        for row in rows:
            with self.subTest(source=row['block_id'], fps=row['fps']):
                self.assertLessEqual(row['height_lost_by_pressing'], 1e-7)
                for mode in ('automatic', 'pressed'):
                    self.assertTrue(row[mode]['cycle_complete'])
                    self.assertEqual(row[mode]['respawns'], 0)
                    self.assertEqual(row[mode]['hp'], 150)
                if row['block_id'] in (71, 295, 296):
                    self.assertGreater(row['pressed']['height'], row['automatic']['height'])
                else:
                    self.assertAlmostEqual(row['pressed']['height'], row['automatic']['height'])

    def test_jump_preserves_velocity_and_existing_ground_air_and_status_gates(self):
        for velocity in (-40, 0, 5, 12, 30, 100):
            actor = Player(0, 'velocity', 0, 0, {}, v_y=velocity)
            actor.on_ground = True
            self.assertTrue(actor.jump())
            self.assertEqual(actor.v_y, max(velocity, actor.v_jump))
        for blocked in ('air', 'grounded', 'stunned', 'exhausted', 'dead'):
            actor = Player(0, 'blocked', 0, 0, {}, v_y=30)
            actor.on_ground = blocked != 'air'
            if blocked in ('grounded', 'stunned'):
                actor.apply_buff(27 if blocked == 'grounded' else 28, (), 5)
            elif blocked == 'exhausted':
                actor.stamina = 0
            elif blocked == 'dead':
                actor.alive = False
            self.assertFalse(actor.jump())
            self.assertEqual(actor.v_y, 30)
            self.assertFalse(actor._jump_escape_active)
        actor = Player(0, 'air charge', 0, 0, {}, v_y=30)
        actor.apply_buff(37, (), 5)
        self.assertTrue(actor.jump())
        self.assertEqual(actor.v_y, 30)
        self.assertEqual(actor._air_jumps_used, 1)
        self.assertFalse(actor.jump())

    def test_source_launches_escape_magnetic_fields_and_immunity_still_blocks_launches(self):
        for kind, velocity in ((415, 22), (330, 30), (433, 35)):
            for immunity in (None, 39, 41, 54):
                with self.subTest(source=kind, immunity=immunity):
                    world = World(0, 'launch field interaction', 40, 256, gravity=-6.5,
                                  spawn_points=(20.5, 5.9))
                    for x in range(40):
                        world.set_tile(x, 4, kind if x == 20 else 2)
                    world.set_tile(20, 3, 338)
                    session = create_control_session(0, world=world)
                    actor = session.app.player1
                    actor.apply_buff(49, (), 5)
                    if immunity:
                        actor.apply_buff(immunity, (), 5)
                    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
                        session.advance(1 / 120)
                    if immunity:
                        self.assertEqual(actor.v_y, 0)
                        self.assertFalse(actor._jump_escape_active)
                    else:
                        self.assertGreater(actor.v_y, velocity * .99)
                        self.assertTrue(actor._jump_escape_active)
                    actor.reset_motion()
                    self.assertFalse(actor._jump_escape_active)
        for impulse in ((5, 0), (0, -5)):
            actor = Player(0, 'non-upward impulse', 0, 0, {})
            actor.apply_impulse(*impulse)
            self.assertFalse(actor._jump_escape_active)
