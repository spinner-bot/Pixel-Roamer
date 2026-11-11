"""Spawn screening must detect the real old trap without treating portals as proof."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.audit_spawn_connectivity import screen
from world import World


class SpawnConnectivityTests(unittest.TestCase):
    def test_current_map_pack_has_local_geometry_paths_and_old_maze_is_flagged(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'spawns.json'
            result = subprocess.run([sys.executable, 'scripts/audit_spawn_connectivity.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['maps']), 15)
        self.assertTrue(report['known_closed_maze']['unexplained_closed_spawn'])
        self.assertFalse(report['known_closed_maze']['local_boundary_reached'])
        self.assertEqual(report['suspect_maps'], [])
        for entry in report['maps']:
            with self.subTest(map_id=entry['map_id']):
                self.assertTrue(entry['local_boundary_reached'])
                self.assertFalse(entry['needs_control_audit'])
                self.assertEqual(entry['actual_spawn'], entry['authored_spawn'])

    def test_contact_with_an_unverified_portal_does_not_waive_control_verification(self):
        world = World(0, 'closed portal fixture', 12, 12, spawn_points=(5.5, 5.9), default_block_id=19)
        for x in range(4, 8):
            for y in range(4, 7):
                world.set_tile(x, y, 0)
        without = screen(world)
        self.assertTrue(without['needs_control_audit'])
        self.assertTrue(without['unexplained_closed_spawn'])
        world.set_tile(6, 4, 300, {'tp_x': 10.5, 'tp_y': 10.9})
        with_portal = screen(world)
        self.assertFalse(with_portal['local_boundary_reached'])
        self.assertTrue(with_portal['needs_control_audit'])
        self.assertFalse(with_portal['unexplained_closed_spawn'])
        self.assertIn(300, [p['block_id'] for p in with_portal['potential_nonlocal_exits']])
