"""Restoring night-background healing must not overwrite unrelated map tiles."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class NightAirFeatureTests(unittest.TestCase):
    def test_healing_and_registered_map_changes_are_the_only_differences(self):
        root = Path(__file__).resolve().parents[1]
        reviews = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'night-air.json'
            result = subprocess.run([sys.executable, 'scripts/audit_night_air_features.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual({entry['map_id'] for entry in report['maps']}, {4, 7})
        self.assertEqual(report['legacy_revision'], reviews['baseline_ref'])
        for entry in report['maps']:
            with self.subTest(map_id=entry['map_id']):
                self.assertEqual(entry['before'], 11)
                self.assertEqual(entry['after'], 290)
                self.assertFalse(entry['healing_is_solid'])
                expected = [{key: change[key] for key in ('position', 'before', 'after')}
                            for change in reviews['maps'][str(entry['map_id'])]]
                expected.sort(key=lambda change: tuple(change['position']))
                self.assertEqual(entry['changes'], expected)
