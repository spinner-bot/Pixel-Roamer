"""Climb from the authored spawn, physically wrap upward and rest at the start."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class EndlessFullLoopTests(unittest.TestCase):
    def test_normal_full_climb_wraps_upward_and_returns_to_start(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'loop.json'
            result = subprocess.run(
                [sys.executable, 'scripts/audit_endless_climb.py', '--route',
                 'scripts/routes/endless_full_loop.json', '--duration', '180',
                 '--draw-every', '5', '--output', str(output)],
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
                self.assertGreater(run['min_stamina'], 150)
                self.assertGreaterEqual(run['final_stamina'], 195)
                self.assertEqual(len(run['y_wraps']), 1)
                crossing = run['y_wraps'][0]
                self.assertEqual(crossing['direction'], 'up')
                self.assertEqual(crossing['phase'], 'upward_wrap_clearance')
                self.assertLess(crossing['from'][1], 120)
                self.assertGreaterEqual(crossing['to'][1], 120)
                self.assertLess(run['max_frame_dy'], 1)
                self.assertGreaterEqual(run['native_draws'], 18)
                self.assertEqual([d['waypoint'] for d in run['draw_trace'] if d['reason']=='waypoint'],
                                 [w['name'] for w in report['route']['waypoints']])
                self.assertEqual(run['draw_trace'][-1]['reason'], 'waypoint')
                self.assertEqual(run['draw_trace'][-1]['waypoint'], 'original_terrace_above_wrap')
                self.assertEqual(run['position'][1], 124.9)
                self.assertEqual([a['name'] for a in run['arrivals']],
                                 [w['name'] for w in report['route']['waypoints']])
