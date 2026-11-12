"""The original y-loop needs physical crossings and a normal way back out."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ClimbVerticalLoopTests(unittest.TestCase):
    def test_downward_loop_upper_platforms_and_upward_return_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'climb-loop.json'
            result = subprocess.run([sys.executable, 'scripts/audit_climb_vertical_loop.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=35)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        reviews = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        expected = [{key: c[key] for key in ('position', 'before', 'after')}
                    for c in reviews['maps']['5']]
        expected.sort(key=lambda c: tuple(c['position']))
        self.assertEqual(report['tile_changes'], expected)
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['returned_after_vertical_loop'])
                self.assertEqual(before['phase'], 'bottom_descent')
                self.assertAlmostEqual(before['position'][1], 2.9)
                self.assertTrue(after['returned_after_vertical_loop'])
                self.assertIsNone(after['failure'])
                self.assertEqual(after['respawns'], 0)
                self.assertEqual(after['min_hp'], 150)
                self.assertGreater(after['min_stamina'], 170)
                self.assertAlmostEqual(after['position'][1], 5.9)
                self.assertLess(abs(after['position'][0] - 10), .15)
                self.assertEqual([t['to'] for t in after['transitions']],
                                 ['upper_platform', 'upward_seam', 'positive_base', 'spawn_return'])
                self.assertAlmostEqual(after['transitions'][0]['position'][1], -10.1)
                self.assertAlmostEqual(after['transitions'][1]['position'][1], -5.1)
                self.assertEqual(len(after['vertical_crossings']), 2)
                down, up = after['vertical_crossings']
                self.assertGreaterEqual(down['from'][1], 0)
                self.assertLess(down['to'][1], 0)
                self.assertLess(up['from'][1], 0)
                self.assertGreaterEqual(up['to'][1], 0)
                for crossing in (down, up):
                    self.assertLess(abs(crossing['from'][1] - crossing['to'][1]), .5)
                self.assertGreaterEqual(after['terrain_draws'], 10)
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / 120 + 1e-7)
