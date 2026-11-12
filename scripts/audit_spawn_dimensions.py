"""Measure legal editor dimensions against actual map spawn geometry."""
from collections import defaultdict
import argparse
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
from maps import get_map, list_maps
from scripts.control_session import create_control_session
from teleport import can_place


def measure(map_id, width, height):
    world = get_map(map_id)
    world.player_config = {**getattr(world, 'player_config', {}), 'w': width, 'h': height}
    session = create_control_session(map_id, world=world)
    player = session.app.player1
    initial = {'position': player.get_center(), 'clear': can_place(player, world, *player.get_center())}
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
        for _ in range(60):
            session.advance(1 / 60)
    return {'map_id': map_id, 'width': width, 'height': height,
            'authored_spawn': world.spawn_points, 'initial': initial,
            'after_one_second': {'position': player.get_center(), 'clear': can_place(player, world, *player.get_center()),
                                 'hp': player.hp, 'alive': player.alive}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'isolated in-memory editor dimension overrides and normal launch, no saved map changes',
              'runs': [measure(map_id, width, height) for map_id in sorted(list_maps())
                       for width, height in ((.8, 1.8), (.8, 2.8), (.8, 4.), (2., 1.8))]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'runs': len(report['runs']), 'invalid_initial':
                      [(r['map_id'], r['width'], r['height']) for r in report['runs'] if not r['initial']['clear']]}))


if __name__ == '__main__':
    main()
