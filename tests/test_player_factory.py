from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from player_factory import create_world_player, world_player_options
from resource_catalog import player_defaults
from world import World


class PlayerFactoryTests(unittest.TestCase):
    def test_production_application_editor_and_factory_share_every_default(self):
        from pixel_roamer.application import GameApp
        from pixel_roamer.ui.map_browser import MapBrowser
        world = World(0, 'defaults', 30, 30, spawn_points=(5.5, 5.5))
        app = GameApp.__new__(GameApp)
        app.p1_keys = {}
        app._play_world_music = Mock()
        with patch('pixel_roamer.application.get_map', return_value=world):
            app.launch_world(0)
        with patch('pixel_roamer.ui.map_browser.get_map', return_value=world), \
             patch('pixel_roamer.ui.map_browser.load_map_config', return_value={}):
            editor = MapBrowser(SimpleNamespace())._get_edit_config(0)['player']
        self.assertEqual(editor, player_defaults())
        for key, value in editor.items():
            attribute = {'w': '_w', 'h': '_h'}.get(key, key)
            self.assertEqual(getattr(app.player1, attribute), value, key)
        self.assertEqual(app.player1.hp_max, 150)
        self.assertEqual(app.player1.f_y, 1)

    def test_map_overrides_are_applied_without_mutating_shared_presets(self):
        world = World(0, 'overrides', 30, 30, spawn_points=(5.5, 5.5))
        world.player_config = {'hp_max': 240, 'f_y': .97, 'w': .7, 'costume_id': 2}
        before = dict(world.player_config)
        player = create_world_player(world, {}, player_name='audit', position=(10.5, 12.5))
        self.assertEqual(player.get_center(), (10.5, 12.5))
        self.assertEqual((player.hp_max, player.f_y, player._w, player.costume_id), (240, .97, .7, 2))
        self.assertEqual(world.player_config, before)
        self.assertEqual(player_defaults()['hp_max'], 150)
        self.assertEqual(player_defaults()['f_y'], 1)

    def test_returned_presets_are_independent_and_invalid_programmatic_values_fail(self):
        defaults = player_defaults()
        defaults['hp_max'] = 0
        self.assertEqual(player_defaults()['hp_max'], 150)
        world = World(0, 'invalid', 30, 30, spawn_points=(5.5, 5.5))
        world.player_config = {'f_y': float('nan')}
        with self.assertRaises(ValueError):
            world_player_options(world)
