"""Body-sized y-loop openings must support their original rooms and return."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeVerticalRouteTests(unittest.TestCase):
    def test_both_hidden_rooms_heal_negative_checkpoint_and_safe_return(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'maze-vertical.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_vertical_route.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=40)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        expected = {(x, y) for lo, hi in ((13, 17), (43, 46))
                    for x in range(lo, hi + 1) for y in (0, 35)}
        changes = {tuple(c['position']): c for c in report['tile_changes']}
        self.assertTrue(expected <= changes.keys())
        reviewed = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        reviewed = {tuple(c['position']): c for c in reviewed['maps']['4']}
        for coordinate, change in changes.items():
            self.assertIn(coordinate, reviewed)
            self.assertEqual(change['after'], reviewed[coordinate]['after'])
        for coordinate in expected:
            self.assertEqual(changes[coordinate]['after'], 11)
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['returned_after_both_rooms'])
                self.assertEqual(before['phase'], 'southwest_entry')
                self.assertTrue(after['returned_after_both_rooms'])
                self.assertIsNone(after['failure'])
                self.assertEqual(after['respawns'], 0)
                self.assertEqual(after['environmental_hp_loss'], 0)
                self.assertGreater(after['min_stamina'], 80)
                self.assertEqual(after['min_hp'], 100)
                self.assertLess(after['position'][0], -28)
                self.assertAlmostEqual(after['position'][1], 22.9)
                self.assertEqual(len(after['portal_hops']), 1)
                down = [c for c in after['vertical_crossings'] if c['from'][1] >= 0 > c['to'][1]]
                self.assertEqual(len(down), 2)
                self.assertEqual({tuple(c['coordinate']) for c in after['contacts']},
                                 {(14, 34), (45, 34), (44, 34)})
                heal = after['healing_probe']
                self.assertEqual(heal['hp_before_test_hit'], 150)
                self.assertEqual(heal['hp_after_test_hit'], 100)
                self.assertEqual(heal['final_hp'], 150)
                self.assertGreater(heal['healed_time'] - heal['time'], 3)
                probe = after['negative_checkpoint_respawn_probe']
                self.assertTrue(probe['alive'] and probe['valid'])
                self.assertEqual(probe['respawns'], 1)
                self.assertLess(probe['saved_spawn'][0], 0)
                self.assertLess(probe['saved_spawn'][1], 0)
                for actual, saved in zip(probe['position'], probe['saved_spawn']):
                    self.assertAlmostEqual(actual, saved)
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / 120 + 1e-7)
