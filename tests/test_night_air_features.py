"""Restoring night-background healing must not overwrite unrelated map tiles."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class NightAirFeatureTests(unittest.TestCase):
    def test_healing_and_separately_reviewed_maze_exit_are_the_only_map_differences(self):
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
                expected = [{'position': entry['point'], 'before': 11, 'after': 290}]
                if entry['map_id'] == 4:
                    # A45 intentionally clears the two cells sealing the west spawn exit.
                    expected = [{'position': [21, 21], 'before': 254, 'after': 0},
                                {'position': [21, 22], 'before': 19, 'after': 0}] + expected
                self.assertEqual(entry['changes'], expected)
