"""An environmental launch must survive a jump keydown before the next sweep."""
from collections import defaultdict
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import pygame
from camera import Camera
from player_factory import create_world_player
from pixel_roamer.world_session import WorldSession
from world import World


class LaunchStateTests(unittest.TestCase):
    def make_session(self):
        world = World(0, 'catapult', 12, 30, gravity=-6.5)
        world.set_tile(5, 1, 433)
        player = create_world_player(world, dict(left=pygame.K_a, right=pygame.K_d,
                                     up=pygame.K_w, down=pygame.K_s,
                                     jump=pygame.K_SPACE, fly=pygame.K_f), position=(5.5, 2.9))
        app = SimpleNamespace(_current_map=world, player1=player, help_open=False,
                              jump_pressed=False, _game_over=False, _game_win=False,
                              _game_timer=0, _player_lives_left=3, _infinite_lives=False,
                              camera=Camera(640, 360, world), _stamina_flash_timer=0,
                              _stamina_flash_duration=.6)
        return WorldSession(app)

    def test_catapult_clears_ground_and_climbing_before_next_input(self):
        session = self.make_session()
        player = session.app.player1
        session.app._current_map.set_tile(6, 2, 9)
        player._x = 5.6  # Touch both ladder and launcher in this isolated fixture.
        player.is_climbing = True
        player.collide_with_world(session.app._current_map, 0)
        self.assertGreater(player.v_y, 30)
        self.assertFalse(player.on_ground)
        self.assertFalse(player.is_climbing)
        self.assertFalse(player.jump())

    def test_same_input_cannot_replace_launch_or_charge_jump_stamina(self):
        for fps in (30, 60, 144):
            with self.subTest(fps=fps):
                session = self.make_session()
                player = session.app.player1
                player.collide_with_world(session.app._current_map, 0)
                session.app.jump_pressed = True
                with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), patch('sfx.play_jump'):
                    for _ in range(3):
                        session.advance(1 / fps)
                self.assertGreater(player.v_y, 30)
                self.assertEqual(player.stamina, player.stamina_max)
