"""The authored score target must be reachable without flight or duplicate pickups."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CollectorRouteTests(unittest.TestCase):
    def test_normal_route_reaches_score_goal_and_freezes_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'collector.json'
            result = subprocess.run([sys.executable, 'scripts/audit_collector_route.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertEqual(run['map_id'], 9)
                self.assertEqual(run['mode'], 'score_target')
                self.assertTrue(run['game_win'])
                self.assertFalse(run['game_over'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['score_goal'], 500)
                self.assertGreaterEqual(run['score'], run['score_goal'])
                self.assertEqual(run['score'], run['available_score'] - run['remaining_score'])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 80)
                self.assertGreater(run['min_stamina'], 100)
                self.assertTrue(run['terminal_state_frozen'])
                self.assertIn('exit_shaft', [point['action'] for point in run['arrivals']])
                scores = [point['score'] for point in run['trace']]
                self.assertEqual(scores, sorted(scores))
