"""Normal original spawn, cold source, thaw/shore return and exact map scope."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CoveFrostPoolTests(unittest.TestCase):
    def test_three_actual_dry_return_and_reentry_cycles_then_formal_victory_at_three_rates(self):
        report = self.probe('scripts/audit_cove_frost_round_trips.py')
        self.assertEqual(report['requested_loops'],3)
        self.assertEqual([r['fps'] for r in report['runs']],[30,60,144])
        for row in report['runs']:
            with self.subTest(fps=row['fps']):
                self.assertIsNone(row['failure'])
                self.assertTrue(row['game_win'])
                self.assertEqual(row['lives_left'],3)
                self.assertLess(row['seconds'],160)
                repeated=row['ice_extension']
                self.assertEqual(len(repeated['loops']),3)
                self.assertEqual(len(repeated['dry_returns']),2)
                self.assertEqual(repeated['min_hp'],150)
                for route in repeated['loops']:
                    self.assertEqual(route['phase'],'complete')
                    self.assertIsNone(route['failure'])
                    self.assertTrue(route['cold_source373'] and route['freeze_seen'] and route['thawed'])
                    self.assertAlmostEqual(route['transitions'][1]['time']-route['transitions'][0]['time'],4,places=8)
                for route in repeated['dry_returns']:
                    self.assertIsNone(route['failure'])
                    self.assertTrue(route['arrived_dry'] and route['jump_input'])
                    self.assertFalse(route['wet'] or route['frozen'])
                    self.assertAlmostEqual(route['position'][1],63.9)

    def probe(self, script):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            result = subprocess.run([sys.executable, script, '--output', str(path)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(path.read_text())

    def test_normal_spawn_original_cold_source_freezes_thaws_and_returns_to_formal_victory(self):
        report = self.probe('scripts/audit_cove_frost_pool.py')
        self.assertFalse(report['candidate_geometry'])
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for row in report['runs']:
            with self.subTest(fps=row['fps']):
                self.assertIsNone(row['failure'])
                self.assertTrue(row['game_win'])
                self.assertTrue(row['reached_end'])
                self.assertEqual(row['lives_left'], 3)
                self.assertGreater(row['min_hp'], 140)
                self.assertGreater(row['min_stamina'], 100)
                self.assertLess(row['seconds'], 110)
                detour = row['ice_extension']
                self.assertIsNone(detour['failure'])
                self.assertEqual(detour['phase'], 'complete')
                for key in ('cold_source373', 'freeze_seen', 'thawed', 'shore_event'):
                    self.assertTrue(detour[key], key)
                self.assertEqual(detour['min_hp'], 150)
                self.assertEqual([s['to'] for s in detour['transitions']],
                                 ['frozen', 'swim', 'shore', 'return', 'complete'])
                self.assertAlmostEqual(detour['transitions'][1]['time']
                                       - detour['transitions'][0]['time'], 4, places=8)
                self.assertTrue({7,373}.issubset(detour['touched_types']))
                frozen = [s for s in detour['trace'] if s['phase'] == 'frozen']
                self.assertTrue(frozen)
                self.assertTrue(all(abs(s['velocity'][0]) < 1e-10 for s in frozen))
                self.assertTrue(any(b['id']==51 and b['source']==373
                                    for s in frozen for b in s['buffs']))

    def test_only_seventeen_original_air_cells_change_and_every_original_pickup_is_preserved(self):
        report = self.probe('scripts/audit_cove_frost_layout.py')
        self.assertTrue(all(report['checks'].values()), report['checks'])
        self.assertEqual(report['planned_cells'], 17)
        self.assertEqual(report['changed_cells'], 17)
        self.assertEqual(report['outside_plan'], [])
        self.assertGreater(report['pickup_count'], 50)
        self.assertTrue(all(row['before']==0 and row['after'] in (3,7)
                            for row in report['differences']))
