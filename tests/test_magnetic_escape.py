"""Magnetic faces must resist movement without permanently trapping the player."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from environment_forces import apply_magnetism, opposed_force


class MagneticEscapeTests(unittest.TestCase):
    def test_only_deliberate_opposing_input_limits_horizontal_attraction(self):
        for force in (-150, -3, 3, 150):
            for direction in (-1, 0, 1):
                acceleration = direction * 12
                result = opposed_force(force, acceleration)
                if force * acceleration < 0:
                    self.assertLessEqual(abs(result), 9)
                    self.assertGreater((result + acceleration) * direction, 0)
                else:
                    self.assertEqual(result, force)

    def test_mixed_sources_are_limited_after_summing_not_per_face(self):
        kinds = [SimpleNamespace(id=i, special='magnetic', special_data=15) for i in (1, 2)]
        tiles = [(1, 0, None, SimpleNamespace(type_id=i)) for i in (1, 2)]
        actor = SimpleNamespace(_x=0, _y=.5, v_x=0, v_y=0, a_x=-8,
                                has_buff=lambda bid: bid == 49,
                                _contact_tile_instances=lambda world: tiles)
        apply_magnetism(actor, None, kinds, .25)
        self.assertEqual(actor.v_x, 1.5)  # Aggregate 6 * dt, leaving net retreat.
        self.assertEqual(actor.v_y, 0)

    def test_passive_and_vertical_attraction_keep_original_strength(self):
        kind = SimpleNamespace(id=1, special='magnetic', special_data=15)
        for magnetized in (False, True):
            actor = SimpleNamespace(_x=.5, _y=0, v_x=0, v_y=0, a_x=0,
                                    has_buff=lambda bid: magnetized,
                                    _contact_tile_instances=lambda world:
                                    [(0, 1, None, SimpleNamespace(type_id=1))])
            apply_magnetism(actor, None, [kind], .1)
            self.assertEqual(actor.v_x, 0)
            self.assertEqual(actor.v_y, 37.5 if magnetized else 15)
            apply_magnetism(actor, None, [kind], 0)
            self.assertEqual(actor.v_y, 37.5 if magnetized else 15)

    def test_force_immunity_still_blocks_magnetic_attraction(self):
        from creature import Player
        from world import World
        world = World(0, 'magnet', 24, 24, gravity=0)
        world.set_tile(10, 10, 386)
        for buff in (39, 41, 54):
            player = Player(0, 'magnet', 9.6, 10.5, {})
            player.apply_buff(buff, (), 10)
            player.collide_with_world(world, .1)
            self.assertEqual((player.v_x, player.v_y), (0, 0))

    def test_three_magnet_types_and_both_faces_allow_real_control_retreat(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'escape.json'
            result = subprocess.run([sys.executable, 'scripts/audit_magnetic_escape.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 18)
        for run in report['runs']:
            with self.subTest(kind=run['kind'], side=run['side'], fps=run['fps']):
                self.assertTrue(run['escaped'])
                self.assertEqual(run['hp'], 150)
                self.assertEqual(run['lives_left'], 3)
