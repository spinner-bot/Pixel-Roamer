"""Buff-only source works through authored spawn and actual movement input."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MagneticSourceRouteTests(unittest.TestCase):
    def test_normal_spawn_contact_reward_expiry_and_fresh_session(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'source.json'
            completed = subprocess.run(
                [sys.executable, 'scripts/audit_magnetic_source_route.py', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            runs = json.loads(output.read_text())['runs']
        self.assertEqual([r['fps'] for r in runs], [30, 60, 144])
        for run in runs:
            with self.subTest(fps=run['fps']):
                self.assertEqual(run['initial'], {'position': [4.5, 25.9], 'buff14': False, 'score': 0})
                self.assertTrue(run['completed'])
                self.assertEqual(run['applied']['source'], 439)
                self.assertEqual(run['applied']['params'], [4.0])
                self.assertEqual(run['applied']['remaining'], 8.0)
                self.assertIn(439, run['applied']['contacts'])
                self.assertEqual(run['source_definition'], {
                    'buff_ids': [14], 'params': [[4.0]], 'durations': [8.0], 'special': None})
                self.assertEqual(run['final_score'], run['expected_score'])
                self.assertGreater(run['final_score'], 0)
                self.assertEqual(run['reward']['flights'], 2)
                self.assertEqual(run['tiles'], {'3,25': 439, '1,26': 320, '0,25': 324})
                self.assertEqual(run['fresh_tiles'], {'3,25': 439, '1,26': 310, '0,25': 314})
                self.assertFalse(run['buff14_at_finish'])
                self.assertEqual(run['flights_at_finish'], 0)
                self.assertGreaterEqual(run['elapsed'] - run['applied']['time'], 8)
                self.assertLess(run['elapsed'], 11)
                self.assertEqual(run['min_hp'], 150)
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['errors'], [])
