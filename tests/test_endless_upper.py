"""Normal spawn through original upper tower, real hazards and narrow roofs."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class EndlessUpperTests(unittest.TestCase):
    def test_normal_upper_route_and_web_escape_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        route_path = root / 'scripts/routes/endless_upper.json'
        route = json.loads(route_path.read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'upper.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_endless_climb.py', '--route', str(route_path),
                 '--duration', '180', '--draw-every', '5', '--output', str(output)],
                cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['completed_route'], run['failure'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 95)
                self.assertGreater(run['min_stamina'], 140)
                self.assertGreaterEqual(run['native_draws'], 15)
                self.assertLess(run['max_frame_dx'], 6 * math.ceil(120 / run['fps']) / 120 + .01)
                self.assertEqual([a['name'] for a in run['arrivals']],
                                 [w['name'] for w in route['waypoints']])
                for arrival, waypoint in zip(run['arrivals'], route['waypoints']):
                    if waypoint['kind'] in ('ground', 'rest'):
                        self.assertAlmostEqual(arrival['position'][1], waypoint['y'])
                by_name = {a['name']: a for a in run['arrivals']}
                self.assertIn(299, by_name['web_platform']['contacts'])
                self.assertNotIn(299, by_name['web_return_shield']['contacts'])
                self.assertGreater(by_name['shield_platform']['shield'], 0)
                self.assertEqual(run['position'][1], 114.9)
