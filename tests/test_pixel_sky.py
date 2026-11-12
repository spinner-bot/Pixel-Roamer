"""Normal sky traversal must use the authored boosts and return portal."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PixelSkyRouteTests(unittest.TestCase):
    def test_forest_boosters_clouds_and_original_sky_portal(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pixel-sky.json'
            result = subprocess.run([sys.executable, 'scripts/audit_pixel_sky.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=35)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['returned_to_ruins_via_original_T2'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 75)
                self.assertEqual(len(run['hops']), 2)
                for hop, target in zip(run['hops'], ((185, 70), (130, 40))):
                    self.assertAlmostEqual(hop['to'][0], target[0], delta=.01)
                    self.assertAlmostEqual(hop['to'][1], target[1], delta=.01)
                self.assertEqual([b['phase'] for b in run['boosted_launches']], ['first_booster', 'second_booster'])
                for boost in run['boosted_launches']:
                    self.assertAlmostEqual(boost['jump_velocity'], 48.6)
                takeoff = next(t for t in run['transitions'] if t['to'] == 'upper_cloud')
                self.assertGreaterEqual(takeoff['position'][0] - run['body'][0] / 2, 204)
                self.assertEqual(run['production_options']['v_jump'], 27)
                self.assertEqual(run['production_options']['f_y'], .98)
                self.assertGreaterEqual(run['terrain_draws'], 6)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
