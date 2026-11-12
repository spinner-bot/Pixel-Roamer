"""Intercept huge scale requests before allocation; measure valid editor zooms."""
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
from chunk_scaling import clear_axis_cache
LEGACY_REF = 'e1ec7ec'
BUDGET = 64 * 1024 * 1024


class AllocationIntercepted(Exception):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy', action='store_true')
    args = parser.parse_args()
    world_class = World
    if args.legacy:
        source = subprocess.check_output(['git', 'show', f'{LEGACY_REF}:world.py'], cwd=ROOT, text=True, encoding='utf-8')
        module = ModuleType('legacy_zoom_world_audit')
        sys.modules[module.__name__] = module
        exec(compile(source, f'git:{LEGACY_REF}:world.py', 'exec'), module.__dict__)
        world_class = module.World
    results = []
    real_scale = pygame.transform.scale
    for view in (2, 4, 14, 200):
        clear_axis_cache()
        world = world_class(0, 'zoom', 64, 36, view_blocks_h=view)
        world.set_tile(4, 25, 4)
        surface = pygame.Surface((1600, 900))
        camera = Camera(1600, 900, world)
        camera.follow(4.5, 25.9)
        requests = []
        def guarded(source, size, *a, **kw):
            estimate = size[0] * size[1] * source.get_bytesize()
            requests.append({'size': size, 'requested_bytes': estimate})
            if estimate > BUDGET:
                raise AllocationIntercepted()
            return real_scale(source, size, *a, **kw)
        completed = True
        start = time.perf_counter()
        try:
            with patch('pygame.transform.scale', side_effect=guarded):
                world.draw(surface, camera)
        except AllocationIntercepted:
            completed = False
        results.append({'view_blocks_h': view, 'completed': completed,
                        'draw_ms': (time.perf_counter() - start) * 1000,
                        'max_requested_bytes': max((r['requested_bytes'] for r in requests), default=0),
                        'requests': requests})
    report = {'world_revision': LEGACY_REF if args.legacy else subprocess.check_output(
              ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'actual transform allocation requests intercepted above 64 MiB; not peak RSS', 'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps([{k: row[k] for k in ('view_blocks_h', 'completed', 'max_requested_bytes', 'draw_ms')}
                      for row in results]))


if __name__ == '__main__':
    main()
