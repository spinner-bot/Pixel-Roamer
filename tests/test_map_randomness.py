"""Map authoring must be independent of process RNG, hash salt and load order."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MapRandomnessTests(unittest.TestCase):
    def test_geometry_is_stable_and_generation_preserves_global_rng(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'randomness.json'
            result = subprocess.run([sys.executable, 'scripts/audit_map_randomness.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(report['changed_maps'], [])
        self.assertEqual(report['polluted_global_rng'], [])
        self.assertEqual(report['changed_on_regeneration'], [])
        self.assertEqual(len(report['cases']), 3)
        for case in report['cases']:
            self.assertEqual(len(case['maps']), 15)
            for map_id, entry in case['maps'].items():
                with self.subTest(seed=case['seed'], reverse=case['reverse_order'], map=map_id):
                    self.assertTrue(entry['global_rng_unchanged'])
                    if 'regenerate_hash' in entry:
                        self.assertTrue(entry['regenerate_rng_unchanged'])
                        self.assertEqual(entry['hash'], entry['regenerate_hash'])
