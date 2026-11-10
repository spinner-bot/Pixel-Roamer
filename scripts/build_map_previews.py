"""Build offline map previews without generating worlds in the map picker."""
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
from camera import Camera
from maps import get_map, list_maps


def main():
    pygame.init()
    destination = ROOT / "assets/maps"
    destination.mkdir(parents=True, exist_ok=True)
    for map_id in sorted(list_maps()):
        world = get_map(map_id)
        surface = pygame.Surface((640, 360))
        surface.fill(world.fill_color)
        camera = Camera(640, 360, world)
        camera.follow(*world.spawn_points)
        world.draw(surface, camera)
        pygame.image.save(surface, str(destination / f"{map_id}.png"))
    pygame.quit()


if __name__ == "__main__":
    main()
