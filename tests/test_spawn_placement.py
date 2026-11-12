"""Legal editor sizes must not launch embedded or crash when no space exists."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from game_state import resolve_player_death
from pixel_roamer.application import GameApp, PAGE_DEV, PAGE_WORLD
from player_factory import create_world_player
from spawn_placement import SpawnPlacementError
from teleport import can_place
from world import World


class SpawnPlacementTests(unittest.TestCase):
    def test_all_maps_launch_clear_at_four_legal_editor_dimensions(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dimensions.json'
            result = subprocess.run([sys.executable, 'scripts/audit_spawn_dimensions.py', '--output', str(output)],
                                    cwd=root, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
        self.assertEqual(len(report['runs']), 60)
        for run in report['runs']:
            with self.subTest(map_id=run['map_id'], width=run['width'], height=run['height']):
                self.assertTrue(run['initial']['clear'])
                self.assertTrue(run['after_one_second']['clear'])
                if (run['width'], run['height']) == (.8, 1.8):
                    self.assertEqual(run['initial']['position'], run['authored_spawn'])

    def test_taller_character_keeps_authored_feet_and_respawns_clear(self):
        world = World(0, 'tall floor', 20, 20, spawn_points=(5.5, 1.9))
        for x in range(20):
            world.set_tile(x, 0, 19)
        world.player_config = {'h': 4.}
        player = create_world_player(world, {})
        self.assertEqual(player.get_center(), (5.5, 3.))
        self.assertEqual(player.spawn_pos, (5.5, 3.))
        player.take_raw_damage(1000)
        resolve_player_death(player, 0, True)
        self.assertTrue(player.alive)
        self.assertTrue(can_place(player, world, *player.get_center()))
        self.assertEqual(player.get_center(), player.spawn_pos)

    def test_width_adjustment_searches_nearby_without_moving_valid_default(self):
        world = World(0, 'near wall', 20, 20, spawn_points=(4.5, 5.5))
        world.set_tile(5, 5, 19)
        default = create_world_player(world, {})
        self.assertEqual(default.get_center(), world.spawn_points)
        world.player_config = {'w': 2.}
        wide = create_world_player(world, {})
        self.assertEqual(wide.get_center(), (4., 5.5))
        self.assertTrue(can_place(wide, world, *wide.get_center()))

    def test_explicit_fixture_position_is_not_silently_relocated(self):
        world = World(0, 'explicit', 10, 10, default_block_id=19)
        player = create_world_player(world, {}, position=(5.5, 5.5))
        self.assertEqual(player.get_center(), (5.5, 5.5))
        self.assertFalse(can_place(player, world, *player.get_center()))
        with self.assertRaises(SpawnPlacementError):
            create_world_player(world, {})

    def test_impossible_launch_returns_to_selector_and_can_retry(self):
        blocked = World(0, 'blocked', 6, 6, spawn_points=(3., 3.), default_block_id=19)
        app = GameApp.__new__(GameApp)
        app.p1_keys = {}
        app._play_world_music = Mock()
        app.page = PAGE_WORLD
        with patch('pixel_roamer.application.get_map', return_value=blocked), patch('music.stop'):
            self.assertFalse(app.launch_world(0))
        self.assertEqual(app.page, PAGE_DEV)
        self.assertIn('无法容纳', app._dev_error)
        self.assertFalse(app._world_initialized)
        self.assertFalse(app._dev_edit_mode)
        app._play_world_music.assert_not_called()
        open_world = World(0, 'fixed', 6, 6, spawn_points=(3., 3.))
        app.page = PAGE_WORLD
        with patch('pixel_roamer.application.get_map', return_value=open_world):
            app.launch_world(0)
        self.assertTrue(app._world_initialized)
        self.assertEqual(app._dev_error, '')
        self.assertTrue(can_place(app.player1, open_world, *app.player1.get_center()))

    def test_loop_spawn_does_not_get_clamped_to_finite_map_bounds(self):
        world = World(0, 'loop', 1, 1, loop_x=True, loop_y=True, spawn_points=(0, 0))
        world.player_config = {'w': 2., 'h': 4.}
        player = create_world_player(world, {})
        self.assertEqual(player.get_center(), (0., 0.))
        self.assertTrue(can_place(player, world, *player.get_center()))

    def test_selector_displays_placement_error(self):
        from types import SimpleNamespace
        import pygame
        from pixel_roamer.ui.map_browser import MapBrowser
        error = '出生点附近无法容纳角色，请调整玩家尺寸。'
        app = SimpleNamespace(_dev_block_browser=False, _dev_buff_browser=False, _dev_edit_mode=False,
                              _dev_error=error, logic_surface=pygame.Surface((1600, 900)), map_selector=Mock())
        with patch('pixel_roamer.ui.map_browser.draw_text_center') as draw:
            MapBrowser(app).run_dev_page(1 / 60)
        app.map_selector.draw.assert_called_once()
        self.assertEqual(draw.call_args.args[2], error)
