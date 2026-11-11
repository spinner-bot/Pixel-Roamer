"""Feature data must preserve walls, occupied loot and passable entrances."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from maps.placement import is_air_cell, load_feature_plan
from world import World


class MapPlacementTests(unittest.TestCase):
    def test_only_real_air_is_available_for_optional_features(self):
        world = World(9, 'placement fixture', 8, 8, default_block_id=11)
        self.assertTrue(is_air_cell(world, 2, 2))
        for tile_id in (0, 11, 12, 13, 14, 15, 7, 31, 310, 290, 19, 50):
            with self.subTest(tile_id=tile_id):
                world.set_tile(2, 2, tile_id)
                self.assertEqual(is_air_cell(world, 2, 2), tile_id in (0, 11, 12))

    def test_feature_plan_validates_entire_document_without_mutation(self):
        world = World(9, 'placement fixture', 8, 8, default_block_id=11)
        valid = {'schema_version': 1, 'map_id': 9,
                 'points': [[2, 3, 311]], 'reserved_rectangles': [[1, 2, 3, 4]]}
        invalid = []
        for key, values in {
            'schema_version': [True, 2], 'map_id': [True, 10],
            'points': [None, [[True, 3, 311]], [[8, 3, 311]], [[2, 3, -1]],
                       [[2, 3, 311], [2, 3, 290]]],
            'reserved_rectangles': [None, [[1, 2, 3]], [[True, 2, 3, 4]],
                                    [[3, 2, 1, 4]], [[1, 2, 3, 8]]],
        }.items():
            for value in values:
                document = copy.deepcopy(valid)
                document[key] = value
                invalid.append(document)
        invalid.extend([[], {**valid, 'unknown': 1}, {'schema_version': 1}])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'features.json'
            path.write_text(json.dumps(valid))
            points, reserved = load_feature_plan(world, path)
            self.assertEqual(points, ((2, 3, 311),))
            self.assertEqual(reserved, frozenset((x, y) for x in range(1, 4) for y in range(2, 5)))
            for document in invalid:
                with self.subTest(document=document):
                    path.write_text(json.dumps(document))
                    with self.assertRaises(ValueError):
                        load_feature_plan(world, path)
                    self.assertEqual(world.grid, {})

    def test_authored_features_load_without_overwriting_loot_or_blocking_passage(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'placement.json'
            result = subprocess.run([sys.executable, 'scripts/audit_collector_placements.py',
                                     '--output', str(output)], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        before, after = report['before'], report['after']
        self.assertEqual(len(before['missed_on_air']), 17)
        self.assertEqual(before['crystal_count'], 0)
        self.assertEqual(after['missed_on_air'], [])
        self.assertGreater(after['crystal_count'], 0)
        self.assertEqual(after['available_score'] - before['available_score'], 195)
        self.assertEqual(after['reserved_solid_cells'], [])
        self.assertTrue(after['entrance_body_clear'])
        placed = {(p['x'], p['y']): p['actual'] for p in after['placed']}
        self.assertEqual(placed[(27, 21)], 316)
        self.assertEqual(placed[(13, 18)], 290)
        occupied = {(p['x'], p['y']): p['actual'] for p in after['occupied_preserved']}
        self.assertEqual(occupied[(48, 8)], 315)
