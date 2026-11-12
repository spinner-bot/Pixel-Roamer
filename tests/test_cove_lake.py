"""The authored lake return vine must actually reach its upper reward platform."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CoveLakeTests(unittest.TestCase):
    def test_normal_spawn_lake_island_and_return_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'lake.json'
            result = subprocess.run([sys.executable, 'scripts/audit_cove_lake.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(report['tile_changes'], [
            {'position': [66, 58], 'before': 0, 'after': 10},
            {'position': [66, 59], 'before': 0, 'after': 10},
            {'position': [66, 60], 'before': 17, 'after': 10},
            {'position': [66, 61], 'before': 17, 'after': 10}])
        self.assertEqual(report['lake_fix_reference'],'dd277a4')
        plan=json.loads((root/'maps/adventure_cove/frost_pool.json').read_text())
        later=[{'position':[x,y],'before':0,'after':bid} for x,y,bid in sorted(plan['points'])]
        self.assertEqual(len(later),17)
        self.assertEqual(report['later_map_changes'],later)
        self.assertEqual(report['all_map_changes'],sorted(report['tile_changes']+later,
                                                         key=lambda row:row['position']))
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['branch_goal_reached'])
                self.assertEqual(before['arrivals'][-1]['climb_bound'], 58)
                self.assertAlmostEqual(before['max_exit_y'], 59.1)
                self.assertTrue(after['branch_goal_reached'])
                self.assertIsNone(after['failure'])
                self.assertEqual([p['leg'] for p in after['arrivals']], ['island', 'vine', 'return_platform'])
                self.assertEqual(after['arrivals'][1]['climb_bound'], 62)
                self.assertEqual(after['diamonds_remaining'], [False, False])
                self.assertEqual(after['score'], 130)
                self.assertTrue(after['score_balance'])
                self.assertEqual(after['respawns'], 0)
                self.assertGreater(after['min_hp'], 100)
                self.assertGreater(after['min_stamina'], 120)
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / after['fps'] + 1 / 120 + 1e-7)
