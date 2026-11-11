"""The south region needs normal access and a rested, valid route back out."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeSouthRouteTests(unittest.TestCase):
    def test_south_portal_and_full_shaft_return_with_real_controls(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'maze-south.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_south_route.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        changes = {tuple(c['position']): c for c in report['tile_changes']}
        for y in range(1, 23):
            self.assertEqual(changes[(20, y)]['after'], 31)
        reviews = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        reviewed = {tuple(c['position']): c for c in reviews['maps']['4']}
        for pos, change in changes.items():
            self.assertIn(pos, reviewed)
            self.assertEqual(change['after'], reviewed[pos]['after'])
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after, returned in zip(report['before'], report['after'], report['return_runs']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['reached_T2_destination'])
                self.assertEqual(before['phase'], 'descent')
                self.assertTrue(after['reached_T2_destination'])
                self.assertEqual(after['position'], [2.5, 8.9])
                self.assertEqual(len(after['portal_hops']), 1)
                self.assertGreater(after['climb_input_seconds'], 1.5)
                self.assertTrue(returned['returned_to_west_corridor'])
                self.assertGreater(returned['climb_input_seconds'], 6)
                self.assertLess(returned['position'][0], 20)
                self.assertAlmostEqual(returned['position'][1], 22.9)
                for run in (after, returned):
                    self.assertIsNone(run['failure'])
                    self.assertEqual(run['respawns'], 0)
                    self.assertEqual(run['min_hp'], 150)
                    self.assertGreater(run['min_stamina'], 80)
                    elapsed = run['control_frames'] / run['fps']
                    self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                    self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
