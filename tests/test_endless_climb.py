"""Actual normal-spawn multi-floor route and stamina recovery on authored map."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class EndlessClimbTests(unittest.TestCase):
    def test_original_platform_side_route_reaches_and_rests_at_checkpoint(self):
        root = Path(__file__).resolve().parents[1]
        route = json.loads((root / 'scripts/routes/endless_climb.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'endless-climb.json'
            result = subprocess.run([sys.executable, 'scripts/audit_endless_climb.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_and_rested'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 95)
                self.assertGreater(run['min_stamina'], 150)
                self.assertGreaterEqual(run['final_stamina'], 195)
                self.assertTrue(run['checkpoint_seen'])
                self.assertEqual(run['saved_checkpoint'], run['position'])
                self.assertEqual([a['name'] for a in run['arrivals']],
                                 [w['name'] for w in route['waypoints']])
                for arrival, waypoint in zip(run['arrivals'], route['waypoints']):
                    self.assertLess(abs(arrival['position'][0] - waypoint['x']), .18)
                    if waypoint['kind'] != 'climb':
                        self.assertAlmostEqual(arrival['position'][1], waypoint['y'])
                self.assertGreater(run['arrivals'][-1]['stamina'], run['arrivals'][-2]['stamina'] + 20)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
