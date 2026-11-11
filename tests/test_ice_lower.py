"""True lower checkpoint contact, low-ceiling respawn and fixed-input physics."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class IceLowerTests(unittest.TestCase):
    def check_route(self, normal_spawn):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'ice.json'
            command = [sys.executable, 'scripts/audit_ice_lower.py', '--output', str(output)]
            if normal_spawn:
                command.append('--normal-spawn')
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertIsNone(report['candidate_layout'])
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps'], normal_spawn=normal_spawn):
                self.assertTrue(run['success'])
                self.assertEqual(run['normal_spawn'], normal_spawn)
                self.assertEqual(run['initial_position'], [15.5, 54.9] if normal_spawn else [269.5, 39.9])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 115 if normal_spawn else 149)
                self.assertGreater(run['min_stamina'], 80 if normal_spawn else 84)
                self.assertTrue(run['topology']['lower_connected'])
                self.assertTrue(run['topology']['upper_connected'])
                self.assertTrue(run['checkpoint_recorded'] and run['checkpoint_clear'])
                self.assertEqual(run['saved_checkpoint'][1], 40.9)
                self.assertLess(abs(run['saved_checkpoint'][0] - 289.6), .02)
                self.assertEqual(run['clearance_jump_count'], 1)
                room = run['segments'][-1] if normal_spawn else run
                self.assertIsNone(room['failure'])
                self.assertLess(room['max_frame_dx'], .25)
                self.assertLess(room['max_frame_dy'], 1)
                arrivals = {a['name']: a for a in room['arrivals']}
                self.assertEqual(arrivals['lower_entry']['position'][1], 39.9)
                self.assertGreaterEqual(arrivals['lower_entry']['position'][0] - .4, 275)
                self.assertIn(302, arrivals['low_checkpoint']['contacts'])
                self.assertEqual(arrivals['low_checkpoint']['stand_pool'], 23)
                gap_x = arrivals['return_gap']['position'][0]
                self.assertGreaterEqual(gap_x - .4, 279 - 1e-7)
                self.assertLessEqual(gap_x + .4, 280 + 1e-7)
                self.assertGreaterEqual(arrivals['pillar_clearance']['position'][1], 51.2)
                death = run['after_deliberate_death']
                self.assertTrue(death['alive'] and death['clear'])
                self.assertEqual(death['respawns'], 1)
                for actual, saved in zip(death['position'], run['saved_checkpoint']):
                    self.assertAlmostEqual(actual, saved)

    def test_local_doorway_checkpoint_and_low_ceiling_return(self):
        self.check_route(False)

    def test_original_forest_to_lower_checkpoint_and_return(self):
        self.check_route(True)

    def test_identical_physics_tick_inputs_match_at_three_presentation_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'timing.json'
            result = subprocess.run([sys.executable, 'scripts/audit_ice_door_timing.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 9)
        hashes = {}
        for tick in (2, 3, 5):
            runs = [r for r in report['runs'] if r['jump_tick'] == tick]
            self.assertEqual([r['fps'] for r in runs], [30, 60, 144])
            self.assertTrue(all(r['entry'] is not None and not r['issues'] for r in runs))
            self.assertEqual(len({r['physics_trace_sha256'] for r in runs}), 1)
            hashes[tick] = runs[0]['physics_trace_sha256']
        self.assertNotEqual(hashes[2], hashes[5])
