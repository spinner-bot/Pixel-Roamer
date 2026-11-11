"""A clear spawn rectangle is insufficient if the hub cannot be left normally."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeSpawnExitTests(unittest.TestCase):
    def test_west_exit_connects_to_corridor_with_only_two_reviewed_cells_changed(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'maze-exit.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_spawn_exit.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(report['tile_changes'], [
            {'position': [21, 21], 'before': 254, 'after': 0},
            {'position': [21, 22], 'before': 19, 'after': 0}])
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
