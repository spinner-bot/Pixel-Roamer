"""Actual shallow-water collection and rested return must remain possible."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CovePoolTests(unittest.TestCase):
    def test_normal_dive_collects_both_diamonds_and_returns_without_death(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pool.json'
            result = subprocess.run([sys.executable, 'scripts/audit_cove_pool.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['returned_to_beach'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['water_diamonds_remaining'], [False, False])
                self.assertEqual(run['score'], 150)
                self.assertTrue(run['score_balance'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 50)
                self.assertGreater(run['swim_input_seconds'], 2)
                recovery = next(t for t in run['transitions'] if t['from'] == 'recover')
                self.assertGreaterEqual(recovery['stamina'], 195)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
