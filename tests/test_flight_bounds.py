"""Flight keeps the complete edited body in finite worlds without exit jumps."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class FlightBoundsTests(unittest.TestCase):
    def test_dimensions_edges_loop_axes_and_collision_reentry(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'flight.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_flight_bounds.py', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 192)
        for run in report['runs']:
            with self.subTest(fps=run['fps'], size=run['size'], direction=run['direction'], loops=run['loops']):
                self.assertTrue(run['flight_body_in_bounds'], run)
                self.assertTrue(run['edge_matches_body'], run)
                self.assertTrue(run['loop_crossed'], run)
                self.assertTrue(run['exit_immediate_clear'], run)
                self.assertTrue(run['exit_clear'], run)
                self.assertLess(run['exit_shift'], 1e-8, run)
                self.assertTrue(run['alive'])
                self.assertEqual(run['hp'], 150)
                self.assertEqual(run['stamina'], 200)
