import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parents[1]
pygame.init()


class LoadingScreenTests(unittest.TestCase):
    def test_loading_status_renders_across_multiple_frames(self):
        import loading_screen

        loading_screen.init_loading_screen(800, 450)
        loading_screen.set_progress(1.0)
        loading_screen.mark_loading_complete()
        surface = pygame.Surface((800, 450))

        for _ in range(30):
            loading_screen.run_loading_screen(surface, 1 / 30, 800, 450)

        self.assertTrue(loading_screen.is_loading_complete())
        self.assertEqual(loading_screen._status_index,
                         len(loading_screen.LOADING_STATUSES) - 1)


class PlayerDeathTests(unittest.TestCase):
    def make_player(self):
        from creature import Player

        keys = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_SPACE,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fly": pygame.K_f,
        }
        return Player(0, "test", 4, 8, keys, hp_max=10, stamina_max=25)

    def test_finite_respawns_decrement_then_game_over(self):
        from game_state import resolve_player_death

        player = self.make_player()
        player.score = 42
        player.take_raw_damage(20)
        self.assertFalse(player.alive)

        lives_left, game_over = resolve_player_death(player, 1, False)
        self.assertEqual(lives_left, 0)
        self.assertFalse(game_over)
        self.assertTrue(player.alive)
        self.assertEqual(player.score, 42)
        self.assertEqual(player.stamina, player.stamina_max)
        self.assertTrue(player.has_buff(36))

        player.clear_buffs()
        player.take_raw_damage(20)
        lives_left, game_over = resolve_player_death(player, lives_left, False)
        self.assertEqual(lives_left, 0)
        self.assertTrue(game_over)
        self.assertFalse(player.alive)

    def test_zero_lives_means_unlimited_respawns(self):
        from game_state import resolve_player_death

        player = self.make_player()
        player.take_raw_damage(20)
        lives_left, game_over = resolve_player_death(player, 0, True)

        self.assertEqual(lives_left, 0)
        self.assertFalse(game_over)
        self.assertTrue(player.alive)


class MapSmokeTests(unittest.TestCase):
    def test_all_maps_load_have_valid_spawn_and_render(self):
        from camera import Camera
        from maps import get_map, list_maps

        maps = list_maps()
        self.assertEqual(len(maps), 12)
        surface = pygame.Surface((640, 360))
        for map_id in sorted(maps):
            world = get_map(map_id)
            spawn_x, spawn_y = world.spawn_points
            self.assertGreater(world.width, 0, maps[map_id])
            self.assertGreater(world.height, 0, maps[map_id])
            self.assertGreaterEqual(spawn_x, 0, maps[map_id])
            self.assertLess(spawn_x, world.width, maps[map_id])
            self.assertGreaterEqual(spawn_y, 0, maps[map_id])
            self.assertLess(spawn_y, world.height, maps[map_id])
            camera = Camera(640, 360, world)
            camera.follow(spawn_x, spawn_y)
            world.draw(surface, camera)


class ApplicationStartupTests(unittest.TestCase):
    def test_application_survives_loading_and_enters_main_loop(self):
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "main.py")],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            time.sleep(4.0)
            output = process.stdout.read() if process.poll() is not None else ""
            self.assertIsNone(process.poll(), output)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            if process.stdout:
                process.stdout.close()


if __name__ == "__main__":
    unittest.main()
