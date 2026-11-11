"""A local tower-base fixture using production parameters and normal controls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PixelTowerTests(unittest.TestCase):
    def test_local_tower_base_to_top_checkpoint_with_layer_recovery(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'tower.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_pixel_tower.py', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertIsNone(report['candidate_layout'])
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['completed_route'], run['failure'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 10)
                self.assertGreaterEqual(run['native_draws'], 26)
                self.assertLess(run['max_frame_dx'], .25)
                self.assertLess(run['max_frame_dy'], 1)
                self.assertTrue(run['checkpoint_seen'])
                self.assertTrue(run['checkpoint_recorded'])
                self.assertEqual(run['saved_checkpoint'], run['position'])
                self.assertEqual(run['position'][1], 202.9)
                self.assertEqual(run['local_fixture_spawn'], [433.5, 11.9])
                self.assertEqual(run['original_forest_spawn'], [15.5, 54.9])
                self.assertEqual(run['production_configuration'],
                                 dict(v_jump=27., v_max=38., f_y=.98, stamina_max=100., gravity=-6.2))
                self.assertEqual([a['name'] for a in run['arrivals']],
                                 [w['name'] for w in report['route']['waypoints']])
                rests = [a for a in run['arrivals'] if a['name'].endswith('_floor') and a['name'] != 'first_floor']
                self.assertEqual([a['position'][1] for a in rests], [41.9, 66.9, 91.9, 123.9, 141.9, 166.9])
                self.assertTrue(all(a['stamina'] >= 95 for a in rests))
