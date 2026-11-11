"""Forest spawn and every regional/tower segment share one actual world session."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PixelNormalTowerTests(unittest.TestCase):
    def test_original_spawn_reaches_tower_checkpoint_without_state_transfer(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'normal-tower.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_pixel_normal_tower.py', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['completed'])
                self.assertEqual(run['original_spawn'], [15.5, 54.9])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 90)
                self.assertGreater(run['min_stamina'], 5)
                self.assertEqual(run['saved_checkpoint'], run['position'])
                self.assertEqual(run['position'][1], 202.9)
                self.assertEqual(len(run['segments']), 3)
                sky, cross, tower = run['segments']
                self.assertTrue(sky['stopped_on_upper_cloud'])
                self.assertFalse(sky['returned_to_ruins_via_original_T2'])
                self.assertEqual(len(sky['hops']), 1)
                self.assertEqual(len(sky['boosted_launches']), 2)
                self.assertTrue(cross['completed_route'] and tower['completed_route'])
                for segment in (cross, tower):
                    self.assertIsNone(segment['failure'])
                    self.assertEqual(segment['respawns'], 0)
                    self.assertLess(segment['max_frame_dx'], .5)
                    self.assertLess(segment['max_frame_dy'], 1)
                self.assertEqual(cross['arrivals'][-1]['name'], 'tower_base')
                self.assertEqual(cross['position'][1], 11.9)
                self.assertAlmostEqual(run['timer'], sky['timer'] + cross['elapsed_timer'] + tower['elapsed_timer'])
                rests = [a for a in tower['arrivals'] if a['name'].endswith('_floor') and a['name'] != 'first_floor']
                self.assertEqual([a['position'][1] for a in rests], [41.9, 66.9, 91.9, 123.9, 141.9, 166.9])
                self.assertTrue(all(a['stamina'] >= 95 for a in rests))
