"""Full existing Cove challenge route through production application controls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CoveRouteTests(unittest.TestCase):
    def test_spawn_to_formal_victory_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'route.json'
            result = subprocess.run([sys.executable, 'scripts/audit_cove_route.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([run['fps'] for run in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['game_win'])
                self.assertTrue(run['reached_end'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['lives_left'], 3)
                self.assertGreater(run['min_hp'], 130)  # Existing thorny vine causes limited damage.
                self.assertGreater(run['min_stamina'], 100)
                self.assertGreaterEqual(run['score'], 400)
                arrivals = [point['name'] for point in run['arrivals']]
                self.assertEqual(len(arrivals), 22)
                for waypoint in ('rift_launch', 'valley_launch', 'vine', 'surefooted',
                                 'exit_ladder', 'temple_pillar_358', 'temple_pillar_403'):
                    self.assertIn(waypoint, arrivals)
                self.assertIn(387, run['touched_types'])
