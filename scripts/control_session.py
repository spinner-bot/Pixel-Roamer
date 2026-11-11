"""Nonvisual application shell for real world-control audits (no UI acceptance)."""
from contextlib import nullcontext
from unittest.mock import patch
import pygame
from pixel_roamer.application import GameApp, PAGE_WORLD
from pixel_roamer.world_session import WorldSession


def create_control_session(map_id, *, world=None):
    app = GameApp.__new__(GameApp)
    app.p1_keys = dict(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                       down=pygame.K_s, jump=pygame.K_SPACE, fly=pygame.K_f)
    app._play_world_music = lambda world: None
    override = patch('pixel_roamer.application.get_map', return_value=world) if world is not None else nullcontext()
    with override:
        app.launch_world(map_id)
    app.focused, app.help_open, app.page = True, False, PAGE_WORLD
    app._stamina_flash_duration = .6
    return WorldSession(app)
