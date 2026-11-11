"""Actual access to the three original rooms, recovery alcove and checkpoint."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PyramidRoomTests(unittest.TestCase):
    def check_route(self, normal_spawn):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'rooms.json'
            command = [sys.executable, 'scripts/audit_pyramid_rooms.py', '--output', str(output)]
            if normal_spawn:
                command.append('--normal-spawn')
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertIsNone(report['candidate_layout'])
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps'], normal_spawn=normal_spawn):
                self.assertTrue(run['completed'] if normal_spawn else run['completed_route'])
                self.assertEqual(run['normal_spawn'], normal_spawn)
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 90 if normal_spawn else 149)
                self.assertGreater(run['min_stamina'], 5 if normal_spawn else 30)
                self.assertTrue(all(r['legal'] and r['connected'] for r in run['topology']['rooms'].values()))
                self.assertTrue(run['checkpoint_valid'])
                self.assertEqual(run['saved_checkpoint'][1], 48.9)
                self.assertEqual(run['position'][1], 80.9)
                room = run['segments'][-1] if normal_spawn else run
                self.assertIsNone(room['failure'])
                arrivals = {arrival['name']: arrival for arrival in room['arrivals']}
                for name, height in (('first_checkpoint', 48.9), ('second_room', 55.9),
                                     ('treasure_room', 62.9), ('rest_alcove', 72.9), ('original_roof', 80.9)):
                    self.assertEqual(arrivals[name]['position'][1], height)
                    self.assertGreaterEqual(arrivals[name]['stamina'], 95)
                self.assertEqual(arrivals['treasure_room']['stand_pool'], 80)
                self.assertGreater(room['min_stamina'], 30)
                death = run['after_deliberate_death']
                self.assertTrue(death['alive'] and death['clear'])
                self.assertEqual(death['respawns'], 1)
                for actual, saved in zip(death['position'], run['saved_checkpoint']):
                    self.assertAlmostEqual(actual, saved)
                if normal_spawn:
                    self.assertEqual(run['original_spawn'], [15.5, 54.9])
                    self.assertEqual(len(run['segments'][0]['hops']), 1)

    def test_local_roof_three_rooms_and_legal_checkpoint_respawn(self):
        self.check_route(False)

    def test_original_forest_to_three_rooms_and_roof_return(self):
        self.check_route(True)
