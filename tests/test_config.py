import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
from map_config import validate_config


class ConfigTests(unittest.TestCase):
    def test_rename_preserves_display_name_and_rejects_invalid_folders(self):
        import maps
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "fixture"
            folder.mkdir()
            (folder / "map.py").write_text(
                'MAP_ID = 1\nworld = World(map_id=1, name="原名称", w=20, h=20)\n',
                encoding="utf-8")
            with patch.object(maps, "__file__", str(root / "__init__.py")):
                self.assertEqual(maps.get_map_summary(1)["name"], "原名称")
                for invalid in ("../outside", "_hidden", "", " name", "..", "bad/name"):
                    self.assertFalse(maps.rename_map(1, invalid))
                self.assertTrue(maps.rename_map(1, "新名称"))
                self.assertTrue((root / "新名称/map.py").is_file())
                self.assertEqual(maps.get_map_summary(1)["name"], "新名称")
                self.assertEqual(maps.load_map_config(1)["world"]["name"], "新名称")

    def test_rejects_unbounded_physics_and_invalid_types(self):
        for config in (
            {"world": {"gravity": 2 ** 40}}, {"world": {"gravity": 10 ** 1000}},
            {"world": {"view_blocks_h": 0}}, {"player": {"costume_id": 99999}},
            {"player": {"f_x": 1.5}}, {"player": {"v_max": float("inf")}},
            {"player": {"hp_max": float("nan")}}, {"player": {"w": -1}},
            {"world": {"loop_x": "false"}}, {"world": {"lives": True}},
            {"world": {"default_block_id": -1}}, {"world": {"grid": {}}},
            {"player": []}, [], {"world": {"fill_color": "256,0,0"}},
        ):
            with self.subTest(config=config), self.assertRaises(ValueError):
                validate_config(config)

    def test_color_input_normalizes_without_changing_original(self):
        original = {"world": {"fill_color": "20, 30, 40"}}
        self.assertEqual(validate_config(original)["world"]["fill_color"], [20, 30, 40])
        self.assertIsInstance(original["world"]["fill_color"], str)

    def test_all_shipped_configs_are_valid(self):
        for path in (Path(__file__).resolve().parents[1] / "maps").glob("*/config.json"):
            with self.subTest(path=path):
                validate_config(json.loads(path.read_text()))

    def test_save_load_invalid_file_fallback_and_default_tile_application(self):
        import maps
        from world import World
        with tempfile.TemporaryDirectory() as directory:
            fake_module = Path(directory) / "__init__.py"
            folder = Path(directory) / "fixture"
            folder.mkdir()
            with patch.object(maps, "__file__", str(fake_module)), patch.object(
                    maps, "_map_registry", return_value={1: "fixture"}):
                config = {"world": {"gravity": -4, "default_block_id": 9,
                                    "fill_color": "1,2,3"}}
                maps.save_map_config(1, config)
                self.assertEqual(maps.load_map_config(1)["world"]["fill_color"], [1, 2, 3])
                world = World(1, "fixture", 10, 10)
                maps._apply_config(world, "fixture")
                self.assertEqual(world.get_block_type(5, 5).id, 9)
                self.assertEqual(world.fill_color, (1, 2, 3))
                self.assertEqual(world.gravity, -4)
                before = (folder / "config.json").read_bytes()
                with self.assertRaises(ValueError):
                    maps.save_map_config(1, {"player": {"f_y": 1.5}})
                self.assertEqual((folder / "config.json").read_bytes(), before)
                (folder / "config.json").write_text("{broken")
                with self.assertWarns(RuntimeWarning):
                    self.assertEqual(maps.load_map_config(1), {})


if __name__ == "__main__":
    unittest.main()
