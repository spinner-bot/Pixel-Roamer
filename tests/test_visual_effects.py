import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
from camera import Camera
from creature import Player
from world import World
from pixel_roamer.visual_effects import WorldEffects


class WorldEffectsTests(unittest.TestCase):
    def scene(self):
        world = World(0, "vision", 100, 100, loop_x=True, loop_y=True, view_blocks_h=30)
        player = Player(0, "vision", 50, 50, {})
        camera = Camera(400, 300, world)
        camera.follow(*player.get_center())
        surface = pygame.Surface((400, 300))
        surface.fill((40, 40, 40))
        return player, camera, surface

    def test_vision_radius_uses_tiles_once_at_multiple_zoom_levels(self):
        for scale in (10, 20, 40):
            player, camera, surface = self.scene()
            camera.scale = scale
            player.apply_buff(25, (2,), 10)
            WorldEffects().draw(surface, player, camera)
            self.assertEqual(surface.get_at((200, 150))[:3], (40, 40, 40))
            self.assertLess(surface.get_at((200 + 2 * scale + 5, 150))[0], 10)

    def test_clarity_suppresses_blindness_and_vision_mask(self):
        player, camera, surface = self.scene()
        player.apply_buff(24, (), 10)
        player.apply_buff(25, (1,), 10)
        player.apply_buff(8, (), 10)
        WorldEffects().draw(surface, player, camera)
        self.assertEqual(surface.get_at((10, 10))[:3], (40, 40, 40))

    def test_glow_adds_subtle_premultiplied_light_without_white_disk(self):
        player, camera, surface = self.scene()
        player.apply_buff(50, (), 10)
        WorldEffects().draw(surface, player, camera)
        self.assertGreater(surface.get_at((200, 150))[0], 40)
        self.assertLessEqual(surface.get_at((200, 150))[0], 70)
        self.assertEqual(surface.get_at((10, 10))[:3], (40, 40, 40))

    def test_large_vision_radius_is_full_vision_without_huge_allocation(self):
        player, camera, surface = self.scene()
        player.apply_buff(25, (1e9,), 10)
        effects = WorldEffects()
        effects.draw(surface, player, camera)
        self.assertEqual(surface.get_at((10, 10))[:3], (40, 40, 40))


if __name__ == "__main__":
    unittest.main()
