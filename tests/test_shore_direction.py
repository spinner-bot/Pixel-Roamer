"""Shore choice, inclusive contact distance and supported slide completion."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ShoreDirectionTests(unittest.TestCase):
    def test_261_shore_choices_land_safely_with_intent_fallback_and_reverse_input(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'shores.json'
            result = subprocess.run([sys.executable, 'scripts/audit_shore_direction.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 243)
        self.assertEqual(len(report['reversed_runs']), 18)
        for row in report['runs'] + report['reversed_runs']:
            with self.subTest(fps=row['fps'], body=row['body'], intent=row['intent'],
                              banks=row['valid_banks'], offset=row['offset'], reversed=row['reversed_input']):
                self.assertTrue(row['matched'] and row['completed'])
                self.assertEqual(set(row['detected']), set(row['valid_banks']))
                self.assertEqual(len(row['choices']), 1)
                self.assertEqual(row['errors'], [])
                self.assertEqual(row['respawns'], 0)
                self.assertLess(row['elapsed'], .3)
                self.assertGreater((row['final'][0] - row['initial'][0]) * row['chosen'], .1)
                self.assertAlmostEqual(row['final'][1] - row['body'][1] / 2, 20 + row['offset'][1])
                self.assertLess(row['final_stamina'], 180)
                self.assertGreater(row['final_stamina'], 150)

    def test_exact_contact_margin_is_mirrored_and_outside_margin_does_not_start_exit(self):
        root = Path(__file__).resolve().parents[1]
        code = '''from collections import defaultdict
from unittest.mock import patch
import pygame
from world import World
from scripts.control_session import create_control_session
from teleport import can_place
for width in (.6,.8):
 for side in (-1,1):
  for margin in (.2,.20001):
   x=1+width/2+margin if side==-1 else 9-width/2-margin
   w=World(0,'shore margin',10,30,gravity=-6.5,spawn_points=(x,20))
   w.player_config={'w':width,'h':1.5 if width==.6 else 1.8}
   for gx in range(10):
    for gy in range(20): w.set_tile(gx,gy,2 if gx in (0,9) else 7)
   s=create_control_session(0,world=w);p=s.app.player1
   p.collide_with_world(s.app._current_map,0)
   assert p._shore_directions==((side,) if margin==.2 else ()), (width,side,margin,p._shore_directions)
   with patch('pygame.key.get_pressed',return_value=defaultdict(bool,{pygame.K_w:True})),patch('sfx.play_jump'),patch('pygame.event.get',return_value=[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]):
    s.app._handle_events();s.advance(1/120)
   assert bool(getattr(p,'_shore_exit_pending',False))==(margin==.2)
   assert can_place(p,s.app._current_map,*p.get_center())
'''
        env = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
        result = subprocess.run([sys.executable, '-c', code], cwd=root, env=env,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
