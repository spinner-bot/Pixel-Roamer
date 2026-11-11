"""Sample the periodic full-body free space without assuming gravity controls."""
from collections import deque
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from maps import get_map
from player_factory import create_world_player
from teleport import can_place


def inspect_world(world, image_path=None):
    player = create_world_player(world, {})
    width, height = world.width * 10, world.height * 10
    legal = {(x, y) for x in range(width) for y in range(height)
             if can_place(player, world, x / 10, y / 10)}
    start = (round(player._x * 10) % width, round(player._y * 10) % height)
    seen, queue = {start}, deque([start])
    crossed_x, crossed_y = False, False
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = ((x + dx) % width if world.loop_x else x + dx,
                     (y + dy) % height if world.loop_y else y + dy)
            if point in legal:
                crossed_x |= not 0 <= x + dx < width
                crossed_y |= not 0 <= y + dy < height
                if point not in seen:
                    seen.add(point)
                    queue.append(point)
    targets = {'south_portal_contact': (235, 89), 'southwest_anchor_top': (145, 359),
               'southeast_anchor_top': (455, 359)}
    if image_path:
        surface = pygame.Surface((width, height))
        surface.fill((12, 18, 29))
        for x, y in legal:
            surface.set_at((x, height - 1 - y), (60, 78, 92))
        for x, y in seen:
            surface.set_at((x, height - 1 - y), (91, 191, 146))
        pygame.draw.circle(surface, (255, 225, 150), (start[0], height - 1 - start[1]), 3)
        for point in targets.values():
            pygame.draw.circle(surface, (235, 119, 117), (point[0], height - 1 - point[1]), 2)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(surface, str(image_path))
    return {'legal_samples': len(legal), 'spawn_component_samples': len(seen),
            'solid_base_cells': sum(world.get_block_type(x, 0).is_solid for x in range(world.width)),
            'horizontal_seam_in_component': crossed_x, 'vertical_seam_in_component': crossed_y,
            'targets': {name: {'position': [point[0] / 10, point[1] / 10],
                               'legal': point in legal, 'connected': point in seen}
                        for name, point in targets.items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--image', type=Path)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': '0.1-cell periodic free-body geometry only; teleport/gravity/stamina/phase effects not modeled; real controls required separately',
              'map_id': 4, 'result': inspect_world(get_map(4), args.image)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['result']))


if __name__ == '__main__':
    main()
