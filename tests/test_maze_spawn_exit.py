"""A clear spawn rectangle is insufficient if the hub cannot be left normally."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeSpawnExitTests(unittest.TestCase):
    def test_west_exit_keeps_its_repair_and_all_map_changes_are_reviewed(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'maze-exit.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_spawn_exit.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        changes = {tuple(change['position']): change for change in report['tile_changes']}
        self.assertEqual(changes[(21, 21)], {'position': [21, 21], 'before': 254, 'after': 0})
        self.assertEqual(changes[(21, 22)], {'position': [21, 22], 'before': 19, 'after': 0})
        review_data = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        reviewed = {tuple(change['position']): change for change in review_data['maps']['4']}
        for position, change in changes.items():
            self.assertIn(position, reviewed)
            self.assertEqual(change['after'], reviewed[position]['after'])
        self.assertFalse(report['before_component']['west_boundary_reached'])
        self.assertTrue(report['after_component']['west_boundary_reached'])
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['escaped_to_west_corridor'])
                self.assertTrue(after['escaped_to_west_corridor'])
                self.assertIsNone(after['failure'])
                self.assertLess(after['position'][0], 20.4)
                self.assertAlmostEqual(after['position'][1], 22.9)
                self.assertEqual(after['min_hp'], 150)
                self.assertGreater(after['min_stamina'], 160)
                self.assertEqual(after['respawns'], 0)
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / 120 + 1e-7)
