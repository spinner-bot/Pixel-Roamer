"""Presentation timing must not change world physics or resource costs."""
from collections import defaultdict
import math
import os
import random
from types import SimpleNamespace
import unittest
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import pygame
from camera import Camera
from creature import Player
from world import World
from simulation import FixedStepClock, SIMULATION_STEP
from pixel_roamer.world_session import WorldSession


def session_on(tile_id=23):
    world = World(0, 'timing', 2000, 100, gravity=-6.5)
    world.begin_bulk_load()
    for x in range(2000):
        world.set_tile(x, 8, tile_id)
    world.end_bulk_load()
    bindings = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                    down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    player = Player(0, 'clock', 10.5, 9.9, bindings)
    player.stamina = 100
    player.collide_with_world(world, 0)
    app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                          jump_pressed=False, _game_over=False, _game_win=False,
                          _game_timer=0, _player_lives_left=3, _infinite_lives=False,
                          camera=Camera(640, 360, world),
                          _stamina_flash_timer=0, _stamina_flash_duration=0.6)
    return WorldSession(app)


def state(session):
    p = session.app.player1
    return (p._x, p._y, p.v_x, p.v_y, p.hp, p.stamina, session.app._game_timer)


class SimulationTests(unittest.TestCase):
    def setUp(self):
        sound = patch("sfx.play_jump")
        sound.start()
        self.addCleanup(sound.stop)

    def test_constant_input_matches_on_five_surfaces_at_three_frame_rates(self):
        keys = defaultdict(bool, {pygame.K_d: True})
        with patch('pygame.key.get_pressed', return_value=keys):
            for tile in (2, 3, 4, 5, 23):
                results = []
                for fps in (30, 60, 144):
                    session = session_on(tile)
                    for frame in range(fps * 5):
                        if frame == fps:
                            session.app.jump_pressed = True
                        session.advance(1 / fps)
                    results.append(state(session))
                for actual in results[1:]:
                    with self.subTest(tile=tile):
                        for a, b in zip(actual, results[0]):
                            self.assertAlmostEqual(a, b, places=9)

    def test_jitter_partition_matches_uniform_input_and_elapsed_time(self):
        keys = defaultdict(bool, {pygame.K_d: True})
        rng = random.Random(20261111)
        times = [rng.uniform(0.001, 0.04) for _ in range(200)]
        times = [dt * 5 / sum(times) for dt in times]
        times[-1] += 5 - sum(times)
        with patch('pygame.key.get_pressed', return_value=keys):
            uniform, jitter = session_on(), session_on()
            for _ in range(300):
                uniform.advance(1 / 60)
            for dt in times:
                jitter.advance(dt)
        for a, b in zip(state(uniform), state(jitter)):
            self.assertAlmostEqual(a, b, places=9)

    def test_subtick_jump_is_consumed_once_and_help_advances_no_time(self):
        session = session_on()
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            session.app.jump_pressed = True
            session.advance(SIMULATION_STEP / 2)
            self.assertTrue(session.app.jump_pressed)
            session.advance(SIMULATION_STEP / 2)
            self.assertFalse(session.app.jump_pressed)
            self.assertGreater(session.app.player1.v_y, 0)
            self.assertGreaterEqual(session.app.player1.stamina, 85)
            self.assertLess(session.app.player1.stamina, 86)
            after_jump = session.app.player1.stamina
            session.advance(SIMULATION_STEP)
            self.assertGreater(session.app.player1.stamina, after_jump)
            session.app.help_open = True
            before = state(session)
            session.advance(20)
            self.assertEqual(before, state(session))

    def test_invalid_elapsed_is_rejected_without_poisoning_clock(self):
        clock = FixedStepClock()
        for dt in (-1, math.nan, math.inf):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                clock.advance(dt, lambda _: None)
            self.assertEqual(clock.remainder, 0)
        steps = []
        self.assertEqual(clock.advance(0.2, steps.append), 24)
        self.assertTrue(all(dt == SIMULATION_STEP for dt in steps))
