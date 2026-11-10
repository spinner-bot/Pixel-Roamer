"""Run real physics routes in a child process to preserve lazy registry checks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ThemeRouteTests(unittest.TestCase):
    def test_both_routes_finish_unhurt_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'routes.json'
            result = subprocess.run([sys.executable, 'scripts/audit_theme_routes.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 18)
        for run in report['runs']:
            with self.subTest(id=run['id'], fps=run['fps'], route=run['route']):
                self.assertTrue(run['reached_end'])
                self.assertEqual(run['min_hp'], 100)
                if run['route'] == 'upper':
                    self.assertEqual(len(run['waypoints']), 4)
                    self.assertGreaterEqual(run['jumps'], 2)
                    self.assertTrue(all(value > 0 for value in run['waypoint_rewards'][:3]))
