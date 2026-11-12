"""Original large-map seven-region route and data-defined sky connection."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class LargeThemeRouteTests(unittest.TestCase):
    def test_normal_cross_region_route_reaches_original_sky_island(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'large-theme.json'
            result = subprocess.run([sys.executable, 'scripts/audit_large_theme_route.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=100)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        reviews = json.loads((root / 'tests/fixtures/reviewed_map_changes.json').read_text())
        expected = [{key: c[key] for key in ('position', 'before', 'after')}
                    for c in reviews['maps']['2']]
        expected.sort(key=lambda c: tuple(c['position']))
        self.assertEqual(report['tile_changes'], expected)
        self.assertEqual({tuple(c['position']) for c in expected}, {(599, y) for y in range(10, 24)})
        self.assertEqual([r['fps'] for r in report['after']], [30, 60, 144])
        for before, after in zip(report['before'], report['after']):
            with self.subTest(fps=after['fps']):
                self.assertFalse(before['reached_original_sky_island'])
                self.assertEqual(before['phase'], 'sky_climb')
                self.assertTrue(after['reached_original_sky_island'])
                self.assertIsNone(after['failure'])
                self.assertEqual(after['respawns'], 0)
                self.assertGreater(after['min_hp'], 149)
                self.assertGreater(after['min_stamina'], 15)
                self.assertAlmostEqual(after['position'][1], 42.9)
                self.assertLess(abs(after['position'][0] - 605.5), .15)
                self.assertEqual([r['boundary_x'] for r in after['regions']], [100, 200, 300, 400, 500, 600])
                self.assertLess(after['max_frame_dx'], 1)
                self.assertGreaterEqual(after['terrain_draws'], 30)
                self.assertIn('sky_base_rest', [r['to'] for r in after['transitions']])
                self.assertIn('sky_climb', [r['to'] for r in after['transitions']])
                self.assertEqual(after['production_options'], before['production_options'])
                self.assertEqual(after['production_options']['stamina_max'], 100)
                self.assertEqual(after['production_options']['v_jump'], 29.5)
                self.assertEqual(after['production_options']['gravity'], -16.5)
                elapsed = after['control_frames'] / after['fps']
                self.assertGreaterEqual(elapsed + 1e-7, after['timer'])
                self.assertLessEqual(elapsed - after['timer'], 1 / 120 + 1e-7)
