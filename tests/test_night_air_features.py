"""Restoring night-background healing must not overwrite unrelated map tiles."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class NightAirFeatureTests(unittest.TestCase):
    def test_temple_and_maze_restore_only_their_declared_empty_healing_point(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'night-air.json'
            result = subprocess.run([sys.executable, 'scripts/audit_night_air_features.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual({entry['map_id'] for entry in report['maps']}, {4, 7})
        for entry in report['maps']:
            with self.subTest(map_id=entry['map_id']):
                self.assertEqual(entry['before'], 11)
                self.assertEqual(entry['after'], 290)
                self.assertFalse(entry['healing_is_solid'])
                self.assertEqual(entry['changes'], [{'position': entry['point'], 'before': 11, 'after': 290}])
