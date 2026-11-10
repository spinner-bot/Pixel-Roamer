"""Check the first Grand Journey vertical connection with production stamina."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class GrandEntranceTests(unittest.TestCase):
    def audit(self, *flags):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'entrance.json'
            result = subprocess.run([sys.executable, 'scripts/audit_grand_entrance.py',
                                     '--output', str(output), *flags], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        return report

    def test_spawn_to_first_cave_uses_real_ladder_and_rest_stops(self):
        report = self.audit()
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_cave'])
                self.assertEqual(run['min_hp'], 150)
                self.assertEqual(run['lives_left'], 5)
                self.assertGreater(run['min_stamina'], 20)
                self.assertEqual(len(run['rest_stops']), 2)
                self.assertTrue(all(stop['stamina'] >= 95 for stop in run['rest_stops']))
                self.assertAlmostEqual(run['position'][1], 56.9)

    def test_existing_hall_is_reached_without_increasing_stamina(self):
        report = self.audit('--upper')
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_cave'])
                self.assertTrue(run['reached_hall'])
                self.assertEqual(run['min_hp'], 150)
                self.assertEqual(run['lives_left'], 5)
                self.assertGreater(run['min_stamina'], 15)
                self.assertAlmostEqual(run['rest_stops'][2]['position'][1], 71.9)
                self.assertEqual(len(run['rest_stops']), 3)
                self.assertTrue(all(stop['stamina'] >= 95 for stop in run['rest_stops']))
                self.assertAlmostEqual(run['position'][1], 76.9)
                self.assertLess(abs(run['position'][0] - 3002.5), .4)
