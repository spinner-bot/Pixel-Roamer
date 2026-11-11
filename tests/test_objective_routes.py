"""Existing objective modes must reach real terminal states using normal inputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ObjectiveRouteTests(unittest.TestCase):
    def audit(self, map_id):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'objective.json'
            result = subprocess.run([sys.executable, 'scripts/audit_objective_routes.py',
                                     '--map-id', str(map_id), '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            self.assertTrue(run['terminal_state_frozen'])
            self.assertEqual(run['score'], run['available_score'] - run['remaining_score'])
            self.assertEqual([point['score'] for point in run['trace']],
                             sorted(point['score'] for point in run['trace']))
        return report['runs']

    def test_temple_real_controls_trigger_formal_victory_without_respawn(self):
        for run in self.audit(7):
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['game_win'])
                self.assertFalse(run['game_over'])
                self.assertTrue(run['reached_end'])
                self.assertTrue(run['teleported'])
                self.assertEqual(run['respawns'], 0)
                self.assertEqual(run['lives_left'], 3)
                self.assertGreater(run['min_hp'], 140)
                self.assertGreater(run['min_stamina'], 150)

    def test_timed_route_collects_across_layers_then_freezes_at_time_limit(self):
        for run in self.audit(8):
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['game_over'])
                self.assertFalse(run['game_win'])
                self.assertGreater(run['score'], 0)
                self.assertGreaterEqual(run['timer'], run['time_limit'])
                self.assertLessEqual(run['timer'], run['time_limit'] + 1 / 120 + 1e-7)
                self.assertGreater(run['y_range'][1], 22)
                self.assertGreater(run['x_range'][1], 38)
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 0)
                self.assertGreater(run['min_stamina'], 0)
