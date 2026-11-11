"""Actual lake entry, dry chamber, real checkpoint and exit after its respawn."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class UndergroundLakeTests(unittest.TestCase):
    def check_route(self, normal_spawn):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'lake.json'
            command = [sys.executable, 'scripts/audit_underground_lake.py', '--output', str(output)]
            if normal_spawn:
                command.append('--normal-spawn')
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertIsNone(report['candidate_layout'])
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps'], normal_spawn=normal_spawn):
                self.assertTrue(run['success'])
                self.assertEqual(run['initial_position'], [15.5, 54.9] if normal_spawn else [261.5, 38.9])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 135 if normal_spawn else 149)
                self.assertGreater(run['min_stamina'], 30)
                self.assertTrue(all(t['legal'] and t['connected']
                                    for t in run['topology']['targets'].values()))
                self.assertTrue(run['lake_checkpoint_recorded'])
                self.assertGreater(run['observation']['swimming_steps'], 2000)
                self.assertGreater(run['observation']['air_chamber_dry_steps'], 30)
                room = run['segments'][-1] if normal_spawn else run
                self.assertTrue(room['completed_route'])
                self.assertIsNone(room['failure'])
                self.assertLess(room['max_frame_dx'], .25)
                self.assertLess(room['max_frame_dy'], 1)
                arrivals = {a['name']: a for a in room['arrivals']}
                for name, stand in [('air_chamber_rest', 2), ('original_snow_step', 23)]:
                    self.assertEqual(arrivals[name]['stand_pool'], stand)
                    self.assertGreaterEqual(arrivals[name]['stamina'], 95)
                self.assertIn(302, arrivals['lake_checkpoint']['contacts'])
                death = run['after_deliberate_death']
                self.assertTrue(death['alive'] and death['clear'])
                self.assertEqual(death['respawns'], 1)
                self.assertEqual(death['position'][1], 20.9)
                returned = run['post_respawn_return']
                self.assertTrue(returned['completed_route'])
                self.assertIsNone(returned['failure'])
                self.assertEqual(returned['respawns'], 0)
                self.assertGreater(returned['min_stamina'], 33)
                self.assertEqual(returned['position'][1], 38.9)
                self.assertGreaterEqual(returned['final_stamina'], 95)

    def test_local_lake_chamber_checkpoint_and_respawn_return(self):
        self.check_route(False)

    def test_original_forest_to_lake_and_actual_respawn_return_same_session(self):
        self.check_route(True)
