"""The surface limiter must respect the complete body under low ceilings."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class SwimSurfaceRoofTests(unittest.TestCase):
    def audit(self, script):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'water.json'
            result = subprocess.run([sys.executable, script, '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(output.read_text())

    def test_252_legal_surface_contacts_stop_before_roofs_without_changing_open_water(self):
        report = self.audit('scripts/audit_swim_surface_roof.py')
        self.assertEqual(len(report['current']), 252)
        for row in report['current']:
            with self.subTest(fps=row['fps'], height=row['height'], roof=row['roof'],
                              mode=row['mode'], offset=row['offset']):
                self.assertEqual(row['errors_total'], 0)
                self.assertTrue(row['final_clear'] and row['can_swim'])
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['max_event_dy'], 0)
                self.assertEqual(row['max_step_dx'], 0)
                self.assertLess(row['max_step_dy'], .05 + 1e-8)
                self.assertGreater(row['stamina'], 178)
                self.assertLess(row['stamina'], 180)
                dx, dy = row['offset']
                self.assertAlmostEqual(row['final'][0], 5.5 + dx)
                if row['roof'] and row['height'] > 2:
                    self.assertTrue(row['on_ceiling'])
                    self.assertAlmostEqual(row['final'][1] + row['height'] / 2, 11 + dy)
                else:
                    self.assertAlmostEqual(row['final'][1], 10 + dy, delta=.001)

    def test_repeated_roof_contact_exhaustion_release_and_recovery_stay_legal(self):
        report = self.audit('scripts/audit_swim_roof_recovery.py')
        self.assertEqual([r['height'] for r in report['runs']], [1.8, 2.02, 2.08, 2.12])
        for row in report['runs']:
            with self.subTest(height=row['height']):
                self.assertAlmostEqual(row['input_seconds'], 120)
                self.assertGreaterEqual(row['steps'], 14399)
                self.assertEqual(row['errors'], [])
                self.assertEqual(row['respawns'], 0)
                self.assertEqual(row['min_hp'], 150)
                self.assertLess(row['min_stamina'], .2)
                self.assertGreater(row['exhausted_up_steps'], 2000)
                self.assertGreater(row['floor_steps'], 8000)
                self.assertGreater(row['max_release_recovery'], 150)
                self.assertEqual(len(row['transitions']), 9)
                if row['height'] > 2:
                    self.assertGreater(row['ceiling_steps'], 3000)
