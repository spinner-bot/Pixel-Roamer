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
                                    capture_output=True, text=True, timeout=45)
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
                self.assertEqual([round(stop['position'][1], 1) for stop in run['rest_stops']], [45.9, 56.9])
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
                self.assertEqual([round(stop['position'][1], 1) for stop in run['rest_stops']], [45.9, 56.9, 71.9])
                self.assertTrue(all(stop['stamina'] >= 95 for stop in run['rest_stops']))
                self.assertAlmostEqual(run['position'][1], 76.9)
                self.assertLess(abs(run['position'][0] - 3002.5), .4)

    def test_north_shaft_and_existing_platforms_reach_first_portal(self):
        report = self.audit('--portal')
        self.assertEqual(len(report['runs']), 3)
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_cave'])
                self.assertTrue(run['reached_hall'])
                self.assertTrue(run['reached_portal'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['lives_left'], 5)
                self.assertGreater(run['min_hp'], 120)  # Original thorn vine remains active.
                self.assertGreater(run['min_stamina'], 10)
                self.assertEqual([round(stop['position'][1], 1) for stop in run['rest_stops']], [45.9, 56.9, 71.9])
                self.assertAlmostEqual(run['position'][0], 4800.5)
                self.assertAlmostEqual(run['position'][1], 60.9)

    def test_existing_portal_route_reaches_formal_victory_from_spawn(self):
        report = self.audit('--finish')
        self.assertEqual(report['goal'], 'finish')
        self.assertEqual(len(report['runs']), 3)
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['game_win'])
                self.assertTrue(run['reached_end'])
                self.assertTrue(run['reached_portal'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['lives_left'], 5)
                self.assertGreater(run['min_hp'], 120)
                self.assertGreater(run['min_stamina'], 10)
                self.assertEqual([round(stop['position'][1], 1) for stop in run['rest_stops']], [45.9, 56.9, 71.9])
                self.assertEqual([hop['phase'] for hop in run['hops']], ['gate', 'library', 'crystal'])
                for hop, expected in zip(run['hops'], [(4800.5, 60.9), (5500.5, 90.9), (5940.5, 85.9)]):
                    self.assertLess(abs(hop['to'][0] - expected[0]), .01)
                    self.assertLess(abs(hop['to'][1] - expected[1]), .01)
