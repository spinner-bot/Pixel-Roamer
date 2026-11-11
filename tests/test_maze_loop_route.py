"""Normal horizontal wrap must lead back to the real portal and hidden room."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeLoopRouteTests(unittest.TestCase):
    def test_spawn_wrap_east_door_and_portal_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'maze-loop.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_loop_route.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['reached_hidden_room'])
                self.assertIsNone(run['failure'])
                self.assertTrue(run['crossed_horizontal_seam'])
                self.assertTrue(any(p['position'][0] < 0 for p in run['trace']))
                self.assertEqual([p['phase'] for p in run['arrivals']], ['west_corridor', 'east_landing'])
                self.assertEqual(len(run['portal_hops']), 1)
                self.assertAlmostEqual(run['portal_hops'][0]['from'][0], -21.5, delta=.1)
                self.assertEqual(run['portal_hops'][0]['to'], [4.5, 29.9])
                self.assertEqual(run['position'], [4.5, 29.9])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['min_hp'], 150)
                self.assertGreater(run['min_stamina'], 160)
                self.assertGreaterEqual(run['terrain_draws'], 10)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
