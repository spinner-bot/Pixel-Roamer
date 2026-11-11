"""Original clay landings must remain bounded through real-map surface changes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TestWorldSurfaceRouteTests(unittest.TestCase):
    def test_clay_ice_stone_vine_and_return_from_normal_spawn(self):
        root = Path(__file__).resolve().parents[1]
        route = json.loads((root / 'scripts/routes/test_world_surfaces.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'test-world-surfaces.json'
            result = subprocess.run([sys.executable, 'scripts/audit_test_world_surfaces.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual([r['fps'] for r in report['runs']], [30, 60, 144])
        for run in report['runs']:
            with self.subTest(fps=run['fps']):
                self.assertTrue(run['returned_after_surface_route'])
                self.assertIsNone(run['failure'])
                self.assertEqual(run['respawns'], 0)
                self.assertGreater(run['min_hp'], 125)
                self.assertGreater(run['min_stamina'], 130)
                names = [w['name'] for w in route['approach'] + route['circuit'] + route['finish']]
                self.assertEqual([a['name'] for a in run['arrivals']], names)
                self.assertEqual([e['phase'] for e in run['clay_entries']], ['clay_drop', 'clay_jump'])
                for entry in run['clay_entries']:
                    self.assertLessEqual(abs(entry['dx']), entry['speed_bound'] + .01)
                self.assertLessEqual(run['max_clay_frame_dx'], 21.5 / run['fps'] + .01)
                # The original grab centers the actor on its vine. Keep that
                # explicit event distinct from a collision-induced clay jump.
                event = run['max_frame_dx_event']
                self.assertEqual(event['phase'], 'vine_top')
                self.assertFalse(event['was_climbing'])
                self.assertTrue(event['is_climbing'])
                self.assertAlmostEqual(run['position'][1], 14.9)
                self.assertEqual(run['production_options']['v_jump'], 9)
                self.assertEqual(run['production_options']['f_y'], .995)
                elapsed = run['control_frames'] / run['fps']
                self.assertGreaterEqual(elapsed + 1e-7, run['timer'])
                self.assertLessEqual(elapsed - run['timer'], 1 / 120 + 1e-7)
