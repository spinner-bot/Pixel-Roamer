"""Measure finite-world background leakage and redundant wide-view chunks."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import ModuleType
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from camera import Camera
from world import World
LEGACY_REF = 'dfb1ed9'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    world_class = World
    if args.legacy:
        source = subprocess.check_output(['git', 'show', f'{LEGACY_REF}:world.py'], cwd=ROOT, text=True, encoding='utf-8')
        module = ModuleType('legacy_background_world_audit')
        sys.modules[module.__name__] = module
        exec(compile(source, f'git:{LEGACY_REF}:world.py', 'exec'), module.__dict__)
        world_class = module.World
    rows = []
    for loop_x, loop_y in ((False, False), (True, False), (False, True), (True, True)):
        world = world_class(0, 'small', 2, 2, loop_x=loop_x, loop_y=loop_y, view_blocks_h=4)
        world.fill_color = (4, 8, 12)
        camera = Camera(80, 80, world)
        camera.follow(1, 1)
        surface = pygame.Surface((80, 80))
        surface.fill(world.fill_color)
        world.draw(surface, camera)
        rows.append({'loop_x': loop_x, 'loop_y': loop_y, 'fill_color': world.fill_color,
                     'pixels': {f'{x},{y}': tuple(surface.get_at((x, y))[:3])
                                for x, y in ((0, 0), (40, 0), (0, 40), (40, 40))}})
    world = world_class(0, 'wide', 64, 36, view_blocks_h=200)
    camera = Camera(1600, 900, world)
    camera.follow(4.5, 25.9)
    surface = pygame.Surface((1600, 900))
    start = time.perf_counter()
    with patch.object(world, '_render_chunk', wraps=world._render_chunk) as render:
        world.draw(surface, camera)
        wide = {'draw_ms': (time.perf_counter() - start) * 1000,
                'rendered_chunks': render.call_count, 'retained_chunks': len(world._chunk_surfaces)}
    report = {'world_revision': LEGACY_REF if args.legacy else subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'corners': rows, 'wide_view': wide}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
