"""Capture production WorldView feedback in an explicit Buff14 fixture."""
from collections import defaultdict
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from world import World
from pixel_roamer.application import GameApp
from pixel_roamer.ui.config import PAGE_WORLD


def capture(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    world = World(0, 'magnetic feedback fixture', 30, 15, gravity=0, spawn_points=(10.5, 7.5))
    world.fill_color = (25, 41, 55)
    world.set_tile(13, 7, 310)
    app = GameApp()
    with patch('pixel_roamer.application.get_map', return_value=world.create_session()):
        app.set_page(PAGE_WORLD, map_id=0)
    frames = []
    try:
        with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
            for ticks, label in ((0, 'before'), (1, 'start'), (14, 'flying'),
                                 (45, 'near_end'), (60, 'settled')):
                while round(app._game_timer * 120) < ticks:
                    app._draw_current_page(1 / 120)
                app._draw_current_page(0)
                image_path = output.with_name(output.stem + '_' + label + '.png')
                pygame.image.save(app.logic_surface, str(image_path))
                frames.append({'time': app._game_timer, 'image': image_path.name,
                    'score': app.player1.score, 'pickup_tile': app._current_map.get_tile(13, 7).type_id,
                    'flights': len(app.player1._pickup_flights)})
                if ticks == 0:
                    app.player1.apply_buff(14, (), 5)
    finally:
        pygame.quit()
    return {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'actual GameApp draw/current WorldSession and WorldView in SDL dummy fixture; direct Buff injection, not native desktop or normal source route',
            'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                        ('scripts/capture_magnetic_pickups.py', 'pixel_roamer/world_view.py',
                         'pixel_roamer/visual_effects.py', 'magnetic_pickups.py')}, 'frames': frames}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = capture(args.output)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['frames']))
