"""A local top-deck checkpoint fixture, not a forest-to-tower route proof."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TowerCheckpointTests(unittest.TestCase):
    def test_local_walk_activates_exposed_checkpoint_and_respawns_legally(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'tower-checkpoint.json'
            result = subprocess.run([sys.executable, 'scripts/audit_tower_checkpoint.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertIsNone(report['before_contact_pose'])
        self.assertIsNotNone(report['after_contact_pose'])
        self.assertIn('NOT forest-to-tower', report['scope'])
        reviewed = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        expected = [{key: c[key] for key in ('position', 'before', 'after')}
                    for c in reviewed['maps']['3']]
        expected.sort(key=lambda c: tuple(c['position']))
        self.assertEqual(report['tile_changes'], expected)
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['activation']['checkpoint_seen'])
                self.assertEqual(before['activation']['record_calls'], 0)
                self.assertEqual(before['activation']['saved_spawn'], before['fixture_spawn'])
                self.assertTrue(after['activation']['checkpoint_seen'])
                self.assertGreater(after['activation']['record_calls'], 0)
                self.assertTrue(after['activation']['valid'])
                self.assertLess(abs(after['activation']['position'][0] - 447.5), .1)
                self.assertEqual(after['activation']['saved_spawn'], after['activation']['position'])
                self.assertIsNone(after['failure'])
                self.assertEqual(after['min_hp'], 150)
                self.assertEqual(after['normal_respawns'], 0)
                death = after['after_deliberate_death']
                self.assertTrue(death['alive'] and death['valid'])
                self.assertEqual(death['respawns'], 1)
                for actual, saved in zip(death['position'], after['activation']['saved_spawn']):
                    self.assertAlmostEqual(actual, saved)
