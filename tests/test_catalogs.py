from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from resource_catalog import load_blocks, load_buffs, load_costumes, load_interface

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "tests/fixtures/catalog_baseline.json").read_text())
ART = json.loads((ROOT / "tests/fixtures/catalog_art_overrides.json").read_text())
NON_ART = json.loads((ROOT / "tests/fixtures/catalog_non_art_baseline.json").read_text())
EXTENSIONS = json.loads((ROOT / "tests/fixtures/catalog_extensions.json").read_text())


def expected(kind, entry_id):
    key = str(entry_id)
    if key in EXTENSIONS[kind]:
        if key in BASELINE[kind]:
            raise AssertionError(f'extension overrides legacy {kind} id {key}')
        return EXTENSIONS[kind][key]
    return {**BASELINE[kind][str(entry_id)], **ART[kind].get(str(entry_id), {})}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


class CatalogTests(unittest.TestCase):
    def test_interface_fields_have_valid_defaults_and_unique_paths(self):
        from map_config import validate_config
        options, fields = load_interface()
        self.assertEqual(options, sorted(set(options)))
        config = {"world": {}, "player": {}}
        paths = []
        for path, label, kind, default, step in fields:
            section, name = path.split(".", 1)
            config[section][name] = default
            paths.append(path)
        self.assertEqual(len(paths), len(set(paths)))
        validate_config(config)

    def test_all_block_definitions_and_pixels_match_pre_migration(self):
        from pattern import render_block_pattern
        blocks = load_blocks()
        self.assertEqual(set(map(str, blocks)), set(BASELINE["blocks"]) | set(EXTENSIONS['blocks']))
        for block_id, block in blocks.items():
            with self.subTest(block_id=block_id):
                self.assertEqual(digest(asdict(block)), expected("blocks", block_id)["definition"])
                surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                render_block_pattern(surface, block, 0, 0, 32, 32, overdraw=False)
                self.assertEqual(hashlib.sha256(pygame.image.tobytes(surface, "RGBA")).hexdigest(),
                                 expected("blocks", block_id)["rgba32"])

    def test_all_buff_definitions_and_icons_match_pre_migration(self):
        from pattern import _draw_vector
        buffs = load_buffs()
        self.assertEqual(set(map(str, buffs)), set(BASELINE["buffs"]) | set(EXTENSIONS['buffs']))
        for buff_id, buff in buffs.items():
            with self.subTest(buff_id=buff_id):
                self.assertEqual(digest(asdict(buff)), expected("buffs", buff_id)["definition"])
                surface = _draw_vector(buff.icon, 32, 32)
                self.assertEqual(hashlib.sha256(pygame.image.tobytes(surface, "RGBA")).hexdigest(),
                                 expected("buffs", buff_id)["rgba32"])

    def test_art_refinement_preserves_every_gameplay_field(self):
        for kind, entries, art_field in (("blocks", load_blocks(), "pattern"),
                                         ("buffs", load_buffs(), "icon")):
            for entry_id, entry in entries.items():
                definition = asdict(entry)
                definition.pop(art_field)
                with self.subTest(kind=kind, entry_id=entry_id):
                    key = str(entry_id)
                    baseline = (NON_ART[kind][key] if key in NON_ART[kind]
                                else EXTENSIONS[kind][key]['non_art'])
                    self.assertEqual(digest(definition), baseline)

    def test_costume_frames_match_pre_migration_pixels(self):
        from costumes import _pixels_to_surface
        costumes, default_id = load_costumes()
        self.assertEqual(default_id, 1)
        self.assertEqual(set(map(str, costumes)), set(BASELINE["costumes"]))
        for costume_id, costume in costumes.items():
            expected = BASELINE["costumes"][str(costume_id)]
            definition = {key: value for key, value in costume.items() if key != "pixels"}
            self.assertEqual(digest(definition), expected["normalized_definition"])
            for state, frames in costume["frames"].items():
                actual = [hashlib.sha256(pygame.image.tobytes(
                    _pixels_to_surface(frame, costume["w"], costume["h"]), "RGBA")).hexdigest()
                    for frame in frames]
                self.assertEqual(actual, expected["frames"][state])

    def test_block_status_references_exist(self):
        buffs = load_buffs()
        for block in load_blocks().values():
            self.assertTrue(set(block.buff_ids) <= set(buffs), block.id)

    def test_rejects_duplicates_unknown_fields_versions_and_invalid_art(self):
        valid = {"schema_version": 1, "kind": "blocks",
                 "entries": [{"id": 0, "name": "air", "is_solid": False}]}
        invalid = [
            {**valid, "schema_version": 2},
            {**valid, "entries": valid["entries"] * 2},
            {**valid, "entries": [{"id": True, "name": "air"}]},
            {**valid, "entries": [{"id": 0, "name": "air", "typo": 1}]},
            {**valid, "entries": [{"id": 0, "name": "air", "surface_f": -1}]},
            {**valid, "entries": [{"id": 0, "name": "air", "color": [999, 0, 0]}]},
            {**valid, "entries": [{"id": 0, "name": "air", "pattern": ["bitmap", 2, []]}]},
        ]
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "blocks.json"
            for document in invalid:
                filename.write_text(json.dumps(document))
                with self.subTest(document=document), self.assertRaises(ValueError):
                    load_blocks(filename)


if __name__ == "__main__":
    unittest.main()
