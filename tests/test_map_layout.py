import json
from pathlib import Path
import tempfile
import unittest
from maps.layout import apply_layout
from block_types_data import BLOCK_TYPES
from world import World


class LayoutTests(unittest.TestCase):
    def apply_document(self, world, document):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'layout.json'
            path.write_text(json.dumps(document))
            apply_layout(world, path)

    def test_local_palette_preserves_shared_definitions_and_gameplay(self):
        world = World(0, 'layout', 10, 10)
        original = BLOCK_TYPES[0]
        self.apply_document(world, {'schema_version': 1, 'palette': {'0': [1, 2, 3]},
                                   'rectangles': [[2, 3, 4, 3, 19]]})
        self.assertEqual(world.get_block_type_by_coord(0, 0).color, (1, 2, 3))
        self.assertIs(BLOCK_TYPES[0], original)
        self.assertNotEqual(original.color, (1, 2, 3))
        self.assertFalse(world.get_block_type_by_coord(0, 0).is_solid)
        self.assertEqual(world.get_tile(4, 3).type_id, 19)
        self.assertEqual(len(world.grid), 3)

    def test_bad_document_never_partially_changes_world(self):
        invalid = [
            {'schema_version': 2, 'palette': {}, 'rectangles': []},
            {'schema_version': 1, 'palette': {'0': [999, 2, 3]}, 'rectangles': []},
            {'schema_version': 1, 'palette': {}, 'rectangles': [[1, 1, 2, 1, 2], [9, 9, 10, 10, 2]]},
            {'schema_version': 1, 'palette': {}, 'rectangles': [[1, 1, 2, 1, 99999]]},
            {'schema_version': 1, 'palette': {}, 'rectangles': [[True, 1, 2, 1, 2]]},
        ]
        for document in invalid:
            world = World(0, 'bad', 10, 10)
            with self.subTest(document=document), self.assertRaises(ValueError):
                self.apply_document(world, document)
            self.assertEqual(world.grid, {})
            self.assertIs(world.block_types, BLOCK_TYPES)
