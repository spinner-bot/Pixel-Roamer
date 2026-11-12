"""Cold/warm rendering measurements with pixel digests and cache accounting."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from camera import Camera
from maps import get_map
import pattern


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pygame.init()
    results = []
    for map_id in (3, 6, 19, 20, 1001, 1002, 1003):
        pattern._pattern_cache.clear()
        if hasattr(pattern, '_pattern_cache_bytes'):
            pattern._pattern_cache_bytes = 0
        world = get_map(map_id)
        camera = Camera(640, 360, world)
        camera.follow(*world.spawn_points)
        surface = pygame.Surface((640, 360))
        times = []
        for _ in range(21):
            start = time.perf_counter()
            world.draw(surface, camera)
            times.append((time.perf_counter() - start) * 1000)
        results.append({'id': map_id, 'cold_ms': times[0],
                        'warm_mean_ms': statistics.mean(times[1:]),
                        'rgb_sha256': hashlib.sha256(pygame.image.tobytes(surface, 'RGB')).hexdigest(),
                        'pattern_entries': len(pattern._pattern_cache),
                        'pattern_bytes': sum(s.get_pitch() * s.get_height()
                                             for s in pattern._pattern_cache.values())})
    report = {'code_revision': subprocess.check_output(['git','rev-parse','HEAD'],
               cwd=ROOT, text=True).strip(), 'driver': pygame.display.get_driver(), 'runs': results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    pygame.quit()


if __name__ == '__main__':
    main()
