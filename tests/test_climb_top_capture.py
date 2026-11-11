"""Ladder-top capture must be continuous, collision-safe and preserve failed actions."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ClimbTopCaptureTests(unittest.TestCase):
    def test_228_legal_contacts_and_pending_alignments_use_safe_physics_steps(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'top.json'
            result = subprocess.run([sys.executable, 'scripts/audit_climb_top_capture.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['current']), 216)
        self.assertEqual(len(report['current_pending']), 12)
        for row in report['current'] + report['current_pending']:
            with self.subTest(fps=row['fps'], body=row['body'], ledge=row['ledge'],
                              mode=row['mode'], offset=row['offset'], gap=row['gap']):
                self.assertTrue(row['continuous'] and row['final_clear'])
                self.assertEqual(row['errors_total'], 0)
                self.assertEqual(row['respawns'], 0)
                self.assertLessEqual(row['max_step_dx'], .05 + 1e-8)
                self.assertLessEqual(row['max_step_dy'], .05 + 1e-8)
                self.assertEqual(row['max_event_dy'], 0)
                if row['body'][0] == 2 and row['ledge']:
                    self.assertFalse(row['climbing'])
                    self.assertTrue(row['on_ground'])
                    self.assertAlmostEqual(row['final'][1], 10.2 + row['offset'][1])
                else:
                    self.assertTrue(row['climbing'])
                    self.assertAlmostEqual(row['final'][0], 5.5 + row['offset'][0])
                    self.assertAlmostEqual(row['final'][1], 10 + row['offset'][1])

    def test_rejected_capture_preserves_falling_velocity_and_air_jump_state(self):
        root = Path(__file__).resolve().parents[1]
        code = '''from world import World
from scripts.control_session import create_control_session
from teleport import can_place
import pygame
from unittest.mock import patch
w=World(0,'blocked cap',20,20,gravity=-6.5,spawn_points=(5.5,10.25))
w.player_config={'w':2.,'h':2.4}
for y in range(1,10): w.set_tile(5,y,9)
w.set_tile(4,8,2)
s=create_control_session(0,world=w)
p=s.app.player1
p.collide_with_world(s.app._current_map,0)
assert p.can_climb and can_place(p,s.app._current_map,*p.get_center())
# Explicit lifecycle fixture: the player has spent an air jump and is falling.
p.v_y=-2.;p._air_jumps_used=1
before=(p.get_center(),p.v_x,p.v_y,p._air_jumps_used,p.stamina)
with patch('pygame.event.get',return_value=[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_w)]):
 s.app._handle_events()
assert not p.is_climbing
assert (p.get_center(),p.v_x,p.v_y,p._air_jumps_used,p.stamina)==before
'''
        env = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
        result = subprocess.run([sys.executable, '-c', code], cwd=root, env=env,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
