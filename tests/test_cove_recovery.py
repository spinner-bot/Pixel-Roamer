"""Exercise an actual accidental fall and the complete stamina-limited return."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CoveRecoveryTests(unittest.TestCase):
    def test_bottom_recovery_returns_to_beach_with_real_controls(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'recovery.json'
            result = subprocess.run([sys.executable, 'scripts/audit_cove_recovery.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['recovered'])
                self.assertEqual(run['rest_stops'], 3)
                self.assertEqual(run['min_hp'], 150)
                self.assertEqual(run['lives_left'], 3)
                self.assertGreater(run['min_stamina'], 100)
                self.assertTrue(any(point['position'][1] < 12 for point in run['trace']))
                self.assertGreater(run['position'][1], 68)
