"""Normal input must expose both pole effects and allow a safe, cleared return."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GrandPolarityGalleryTests(unittest.TestCase):
    def probe(self, script):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'report.json'
            result = subprocess.run([sys.executable,script,'--output',str(output)],cwd=ROOT,
                                    capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(output.read_text())

    def test_original_spawn_both_source_effects_and_cleared_return_at_three_rates(self):
        report = self.probe('scripts/audit_grand_polarity_gallery.py')
        self.assertEqual([r['fps'] for r in report['runs']],[30,60,144])
        for row in report['runs']:
            with self.subTest(fps=row['fps']):
                self.assertIsNone(row['failure'])
                self.assertTrue(row['reached_hall'])
                self.assertEqual([round(s['position'][1],1) for s in row['rest_stops']],[45.9,56.9,71.9])
                result = row['hall_extension']
                self.assertEqual(result['errors'],[])
                self.assertTrue(result['returned'])
                self.assertTrue(result['reverse_seen'])
                self.assertTrue(result['positive_seen'])
                self.assertLess(result['seconds'],35)
                self.assertEqual(result['min_hp'],150)
                self.assertGreater(result['min_stamina'],45)
                self.assertEqual(set(result['source_calls']),{'403','411'})
                self.assertTrue(result['force_samples'])
                self.assertTrue(result['positive_force_samples'])
                for sample in result['force_samples']:
                    self.assertEqual(sample['source'],411)
                    self.assertEqual(sample['params'],[-1])
                    self.assertGreater(sample['delta_vx'] * (sample['position'][0]-2980.5),0)
                for sample in result['positive_force_samples']:
                    self.assertEqual(sample['source'],403)
                    self.assertEqual(sample['params'],[1])
                    self.assertGreater(sample['delta_vx'] * (2980.5-sample['position'][0]),0)
                self.assertAlmostEqual(result['position'][1],76.9)
                self.assertLess(abs(result['position'][0]-3002.5),.4)
                self.assertEqual(result['trace'][-1]['buffs'],{})

    def test_plan_changes_only_reviewed_cells_and_preserves_original_features(self):
        report = self.probe('scripts/audit_grand_gallery_layout.py')
        self.assertTrue(all(report['checks'].values()),report['checks'])
        self.assertEqual(report['outside_plan'],[])
        self.assertEqual(report['changed_cells'],57)
        self.assertEqual(report['planned_cells'],120)
        for row in report['differences']:
            self.assertIsNone(row['before_meta'])
            self.assertIsNone(row['after_meta'])
