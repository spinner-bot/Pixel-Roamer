"""Capture current renderer with optional reversal of the reviewed A66 tiles."""
import argparse
import json
import os
from pathlib import Path
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from camera import Camera
from maps import get_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    world = get_map(3).create_session()
    if args.before:
        reviews = json.loads((ROOT / 'tests/fixtures/reviewed_map_changes.json').read_text())
        for change in reviews['maps']['3']:
            if change['stage'] == 'A66':
                world.set_tile(*change['position'], change['before'])
    surface = pygame.Surface((640, 900))
    camera = Camera(640, 900, world)
    camera.scale = 4
    camera.follow(450, 110)
    world.draw(surface, camera)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(args.output))


if __name__ == '__main__':
    main()
