"""Capture reviewed tower/pyramid regions with optional stage tile reversal."""
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
    parser.add_argument('--region', choices=('tower', 'pyramid', 'pyramid_bottom', 'ice_lower', 'lake'), default='tower')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    stage, scale, center = {
        'tower': ('A66', 4, (450, 110)),
        'pyramid': ('A69', 16, (375, 60)),
        'pyramid_bottom': ('A70', 12, (375, 50)),
        'ice_lower': ('A71', 16, (288, 54)),
        'lake': ('A73', 16, (282, 27)),
    }[args.region]
    world = get_map(3).create_session()
    if args.before:
        reviews = json.loads((ROOT / 'tests/fixtures/reviewed_map_changes.json').read_text())
        for change in reviews['maps']['3']:
            if change['stage'] == stage:
                world.set_tile(*change['position'], change['before'])
    size = (800, 900) if args.region in ('ice_lower', 'lake') else (640, 900)
    surface = pygame.Surface(size)
    camera = Camera(*size, world)
    camera.scale = scale
    camera.follow(*center)
    world.draw(surface, camera)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(args.output))


if __name__ == '__main__':
    main()
