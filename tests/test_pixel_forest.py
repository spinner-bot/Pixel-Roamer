"""Normal large-map forest departure, portal and destination island landing."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PixelForestTests(unittest.TestCase):
    def test_normal_spawn_to_t5_and_actual_island_landing_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pixel-forest.json'
            result = subprocess.run([sys.executable, 'scripts/audit_pixel_forest.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=25)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_T5_sky_destination'])
                self.assertTrue(run['landed_on_original_sky_island'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 80)
                self.assertEqual(len(run['portal_hops']), 1)
                hop = run['portal_hops'][0]
                self.assertLess(abs(hop['from'][0] - 70.5), 1)
                self.assertLess(abs(hop['to'][0] - 185), .1)
                self.assertLess(abs(hop['to'][1] - 70), .1)
                self.assertAlmostEqual(run['position'][1], 61.9)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
