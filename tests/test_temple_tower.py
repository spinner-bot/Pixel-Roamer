"""The authored climbing route must collect its emerald and reach the beacon."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TempleTowerTests(unittest.TestCase):
    def test_normal_tower_route_without_shortcut_portal_at_three_frame_rates(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'temple-tower.json'
            result = subprocess.run([sys.executable, 'scripts/audit_temple_tower.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=35)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        expected = {(40, y): 10 for y in (22, 28, 35)}
        expected.update({(40, 37): 11, (41, 37): 11, (41, 38): 11})
        changes = {tuple(c['position']): c for c in report['tile_changes']}
        reviewed = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        reviewed = {tuple(c['position']): c for c in reviewed['maps']['7']}
        for coordinate, tile_id in expected.items():
            self.assertEqual(changes[coordinate]['after'], tile_id)
        for coordinate, change in changes.items():
            self.assertIn(coordinate, reviewed)
            self.assertEqual(change['after'], reviewed[coordinate]['after'])
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['original_emerald_collected'])
                self.assertFalse(before['game_win'])
                self.assertEqual(before['phase'], 'tower_climb')
                self.assertTrue(after['original_emerald_collected'])
                self.assertTrue(after['game_win'] and after['terminal_state_frozen'])
                self.assertIsNone(after['failure'])
                self.assertEqual(after['respawns'], 0)
                self.assertEqual(after['portal_hops'], [])
                self.assertGreater(after['min_hp'], 100)
                self.assertGreater(after['min_stamina'], 100)
                self.assertGreaterEqual(after['score'], 80)
                self.assertEqual(after['score'], after['consumed_score'])
                self.assertLess(after['emerald_collected_at'], after['timer'])
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / after['fps'] + 1 / 120 + 1e-7)
