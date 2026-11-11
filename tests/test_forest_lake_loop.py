"""Normal lake traversal must physically cross the seam and finish shore exit."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ForestLakeLoopTests(unittest.TestCase):
    def test_normal_lake_rest_wrap_and_shore_exit_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'forest-lake.json'
            result = subprocess.run([sys.executable, 'scripts/audit_forest_lake_loop.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=35)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        self.assertTrue(any(run['shore_exits'] for run in report['runs']))
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_wrapped_west_island'])
                self.assertTrue(run['crossed_x_seam_physically'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['portal_hops'], [])
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 130)
                self.assertEqual(run['landing_block'], 17)
                self.assertAlmostEqual(run['position'][1], 15.9)
                self.assertGreater(run['position'][0], 80)
                self.assertGreaterEqual(run['transitions'][0]['stamina'], 195)
                self.assertGreaterEqual(run['terrain_draws'], 20)
                self.assertFalse(run['shore_pending_at_finish'])
                for event in run['shore_exits']:
                    self.assertAlmostEqual(event['stamina_before'] - event['stamina_after'], 25)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
