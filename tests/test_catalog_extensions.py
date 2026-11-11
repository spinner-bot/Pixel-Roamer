"""Data packages are ordered, cannot shadow IDs and preserve explicit-file isolation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from resource_catalog import catalog_document, load_blocks


def write(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'schema_version': 1, 'kind': 'blocks', 'entries': entries}))


class CatalogExtensionTests(unittest.TestCase):
    def test_package_order_and_rejection_of_collisions_with_core_or_other_packages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / 'blocks.json', [{'id': 0, 'name': 'core'}])
            write(root / 'extensions/blocks_b.json', [{'id': 2, 'name': 'second'}])
            write(root / 'extensions/blocks_a.json', [{'id': 1, 'name': 'first'}])
            self.assertEqual([e['id'] for e in catalog_document('blocks', directory=root)['entries']], [0, 1, 2])
            for duplicate in (0, 1):
                write(root / 'extensions/blocks_b.json', [{'id': duplicate, 'name': 'collision'}])
                with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                    catalog_document('blocks', directory=root)

    def test_cross_package_consumed_reference_is_resolved_but_explicit_files_stay_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root / 'blocks.json', [{'id': 0, 'name': 'air', 'is_solid': False}])
            coin = root / 'extensions/blocks_coin.json'
            write(coin, [{'id': 1, 'name': 'coin', 'consumed_type_id': 2}])
            write(root / 'extensions/blocks_marker.json', [{'id': 2, 'name': 'marker'}])
            with patch('resource_catalog.CATALOG_DIR', root):
                self.assertEqual(load_blocks()[1].consumed_type_id, 2)
                with self.assertRaises(ValueError):
                    load_blocks(coin)
