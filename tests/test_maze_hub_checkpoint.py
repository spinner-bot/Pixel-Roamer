"""The hub anchor must be activated by normal play, not merely exist under walls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MazeHubCheckpointTests(unittest.TestCase):
    def test_normal_spawn_activates_checkpoint_and_respawns_at_its_valid_pose(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'hub-checkpoint.json'
            result = subprocess.run([sys.executable, 'scripts/audit_maze_hub_checkpoint.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        changes = {tuple(c['position']): c for c in report['tile_changes']}
        self.assertEqual(changes[(22, 15)], {'position': [22, 15], 'before': 19, 'after': 302})
        self.assertEqual(changes[(24, 15)], {'position': [24, 15], 'before': 302, 'after': 19})
        reviews = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        reviewed = {tuple(c['position']): c for c in reviews['maps']['4']}
        for position, change in changes.items():
            self.assertIn(position, reviewed)
            self.assertEqual(change['after'], reviewed[position]['after'])
        self.assertIsNone(report['before_contact_pose'])
        self.assertIsNotNone(report['after_contact_pose'])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['activation']['checkpoint_seen'])
                self.assertEqual(before['activation']['record_calls'], 0)
                self.assertTrue(after['activation']['checkpoint_seen'])
                self.assertGreater(after['activation']['record_calls'], 0)
                self.assertTrue(after['activation']['valid'])
                self.assertEqual(after['activation']['saved_spawn'], [22.5, 16.9])
                self.assertEqual(after['after_deliberate_death']['respawns'], 1)
                self.assertTrue(after['after_deliberate_death']['valid'])
                self.assertTrue(after['after_deliberate_death']['alive'])
                self.assertEqual(after['after_deliberate_death']['position'], [22.5, 16.9])
