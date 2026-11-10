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


class MusicTests(unittest.TestCase):
    def test_first_track_request_is_non_blocking_and_renders_on_demand(self):
        import music

        music.stop(fade_out_ms=0)
        music.invalidate_cache()
        start = time.perf_counter()
        music.play("home", fade_in_ms=0, loops=0)
        request_duration = time.perf_counter() - start

        self.assertLess(request_duration, 0.75)
        self.assertNotIn("adventure", music._music_cache)
        deadline = time.monotonic() + 10
        max_update_duration = 0.0
        while "home" not in music._music_cache and time.monotonic() < deadline:
            update_start = time.perf_counter()
            music.update()
            max_update_duration = max(max_update_duration,
                                      time.perf_counter() - update_start)
        music.update()
        self.assertIn("home", music._music_cache)
        self.assertLess(max_update_duration, 0.03)
        self.assertEqual(music.get_current_track(), "home")
        self.assertNotIn("adventure", music._music_cache)
        music.stop(fade_out_ms=0)
        music.invalidate_cache()


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
        from creature import Player
        from maps import get_map, get_map_summary, list_maps

        import sys
        registry_start = time.perf_counter()
        maps = list_maps()
        self.assertLess(time.perf_counter() - registry_start, 1.0)
        self.assertEqual(len(maps), 12)
        self.assertFalse(any(
            name.startswith("maps.") and name.endswith(".map")
            for name in sys.modules
        ), "listing maps must not execute map generation modules")
        summaries = {map_id: get_map_summary(map_id) for map_id in maps}
        self.assertFalse(any(
            name.startswith("maps.") and name.endswith(".map")
            for name in sys.modules
        ), "map summaries must not execute map generation modules")
        selected_load_start = time.perf_counter()
        selected_world = get_map(20)
        self.assertLess(time.perf_counter() - selected_load_start, 1.5,
                        "loading one map should not generate every map")
        loaded_map_modules = [
            name for name in sys.modules
            if name.startswith("maps.") and name.endswith(".map")
        ]
        self.assertEqual(loaded_map_modules, ["maps.grand_journey.map"])
        self.assertEqual(len(selected_world.grid), 140372)
        surface = pygame.Surface((640, 360))
        for map_id in sorted(maps):
            world = get_map(map_id)
            summary = summaries[map_id]
            self.assertEqual(summary["name"], world.name, maps[map_id])
            self.assertEqual(summary["width"], world.width, maps[map_id])
            self.assertEqual(summary["height"], world.height, maps[map_id])
            self.assertEqual(summary["mode"], world.mode, maps[map_id])
            self.assertEqual(summary["loop_x"], world.loop_x, maps[map_id])
            self.assertEqual(summary["loop_y"], world.loop_y, maps[map_id])
            spawn_x, spawn_y = world.spawn_points
            self.assertGreater(world.width, 0, maps[map_id])
            self.assertGreater(world.height, 0, maps[map_id])
            self.assertGreaterEqual(spawn_x, 0, maps[map_id])
            self.assertLess(spawn_x, world.width, maps[map_id])
            self.assertGreaterEqual(spawn_y, 0, maps[map_id])
            self.assertLess(spawn_y, world.height, maps[map_id])
            camera = Camera(640, 360, world)
            camera.follow(spawn_x, spawn_y)
            draw_start = time.perf_counter()
            world.draw(surface, camera)
            first_draw_seconds = time.perf_counter() - draw_start
            if map_id in (3, 19, 20):
                self.assertLess(first_draw_seconds, 1.0,
                                f"{maps[map_id]} first draw took {first_draw_seconds:.2f}s")
            self.assertLessEqual(world._scaled_chunk_cache_bytes, 64 * 1024 * 1024)

            if world.mode == "explore":
                endpoints = [
                    coord for coord, tile in world.grid.items()
                    if world.block_types.get(tile.type_id)
                    and world.block_types[tile.type_id].special == "end_point"
                ]
                self.assertTrue(endpoints, f"{maps[map_id]} has no end point")
                end_x, end_y = endpoints[0]
                keys = {
                    "left": pygame.K_a,
                    "right": pygame.K_d,
                    "jump": pygame.K_SPACE,
                    "up": pygame.K_w,
                    "down": pygame.K_s,
                    "fly": pygame.K_f,
                }
                player = Player(0, "test", end_x - 0.3, end_y + 0.5, keys)
                player.collide_with_world(world, 1 / 60)
                self.assertTrue(player._reached_end, f"{maps[map_id]} end point did not activate")

            if world.mode == "score_target":
                available_score = sum(
                    world.block_types[tile.type_id].special_data
                    for tile in world.grid.values()
                    if tile.type_id in world.block_types
                    and world.block_types[tile.type_id].special == "score"
                )
                self.assertGreaterEqual(available_score, world.score_goal,
                                        f"{maps[map_id]} cannot reach its score goal")


class PhysicsTests(unittest.TestCase):
    def test_movement_collision_and_jump_stay_active(self):
        from creature import Player
        from maps import get_map

        world = get_map(1)
        keys = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_SPACE,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fly": pygame.K_f,
        }
        player = Player(0, "physics", *world.spawn_points, keys)
        for _ in range(300):
            player.move(0.35)
            player.update_physics(1 / 60, world)
            player.collide_with_world(world, 1 / 60)

        self.assertTrue(player.alive)
        self.assertGreater(player._x, world.spawn_points[0])
        self.assertGreater(player._y, 0)
        # The route can leave the starting platform; wait for an actual landing
        # instead of assuming frame 300 must coincide with ground contact.
        for _ in range(300):
            if player.on_ground:
                break
            player.move(0)
            player.update_physics(1 / 60, world)
            player.collide_with_world(world, 1 / 60)
        self.assertTrue(player.on_ground)

        before_jump = player._y
        self.assertTrue(player.jump())
        player.update_physics(1 / 60, world)
        player.collide_with_world(world, 1 / 60)
        self.assertGreater(player._y, before_jump)


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
