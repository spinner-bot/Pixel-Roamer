"""World-only status overlays with explicit world-to-pixel units."""
from collections import OrderedDict
import math
import pygame


class WorldEffects:
    def __init__(self):
        self._glows = OrderedDict()
        self._mask = None

    def _glow(self, radius):
        if radius not in self._glows:
            glow = pygame.Surface((radius * 2, radius * 2))
            glow.fill((0, 0, 0))
            for layer in range(8, 0, -1):
                alpha = 30 - layer * 3
                color = tuple(round(channel * alpha / 255) for channel in (255, 240, 180))
                pygame.draw.circle(glow, color, (radius, radius), max(1, round(radius * layer / 8)))
            self._glows[radius] = glow
            while len(self._glows) > 4:
                self._glows.popitem(last=False)
        self._glows.move_to_end(radius)
        return self._glows[radius]

    def _draw_pickup_flights(self, surface, player, camera, world):
        if world is None:
            return
        target_x, target_y = player.get_center()
        for flight in getattr(player, '_pickup_flights', ()):
            age = player._buff_game_time - flight.started_at
            if not 0 <= age < flight.duration:
                continue
            progress = age / flight.duration
            easing = 1 - (1 - progress) ** 2
            x = flight.origin[0] + (target_x - flight.origin[0]) * easing
            y = flight.origin[1] + (target_y - flight.origin[1]) * easing
            sx, sy = camera.world_to_screen(x, y)
            kind = world.block_types.get(flight.tile_id)
            if kind is None:
                continue
            # Flight icons stay pixel-sized even at extreme map zoom.
            size = max(4, min(32, round(camera.scale * (1 - .65 * progress))))
            if (sx + size / 2 < 0 or sy + size / 2 < 0
                    or sx - size / 2 >= surface.get_width()
                    or sy - size / 2 >= surface.get_height()):
                continue
            image = pygame.transform.scale(world._terrain_texture(kind), (size, size))
            surface.blit(image, (round(sx - size / 2), round(sy - size / 2)))

    def draw(self, surface, player, camera, world=None):
        self._draw_pickup_flights(surface, player, camera, world)
        center = tuple(round(value) for value in camera.world_to_screen(*player.get_center()))
        if player.has_buff(50):
            radius = max(4, min(256, round(3 * camera.scale)))
            surface.blit(self._glow(radius), (center[0] - radius, center[1] - radius),
                         special_flags=pygame.BLEND_RGB_ADD)
        if player.has_buff(8):
            return
        if not player.has_buff(24) and not player.has_buff(25):
            return
        if self._mask is None or self._mask.get_size() != surface.get_size():
            self._mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if player.has_buff(24):
            self._mask.fill((255, 240, 80, 140))
            surface.blit(self._mask, (0, 0))
        if player.has_buff(25):
            radius_blocks = max(0, player._get_buff_param(25, 0, 5))
            # Camera scale is already pixels per tile; there is no second *24.
            radius_pixels = radius_blocks * camera.scale
            farthest = max(math.hypot(x - center[0], y - center[1])
                           for x in (0, surface.get_width()) for y in (0, surface.get_height()))
            if radius_pixels >= farthest:
                return
            self._mask.fill((0, 0, 0, 220))
            if radius_pixels > 0:
                pygame.draw.circle(self._mask, (0, 0, 0, 0), center, max(1, round(radius_pixels)))
            surface.blit(self._mask, (0, 0))
