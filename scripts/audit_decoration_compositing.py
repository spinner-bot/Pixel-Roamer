"""Measure decoration backgrounds and explicit RGBA vector composition."""
import argparse
import hashlib
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
from block_type import BlockType
from block_types_data import BLOCK_TYPES
from camera import Camera
from pattern import render_block_pattern
from world import World

DECORATIONS = (43, 50, 51, 52, 53, 54)


def scene(default_id, image_path=None, decorations=DECORATIONS):
    width = len(decorations) + 2
    world = World(0, 'decoration composition', width, 4, default_block_id=default_id,
                  view_blocks_h=4)
    for x, tile_id in enumerate(decorations, 1):
        world.set_tile(x, 1, tile_id)
    world.set_tile(0, 1, 12)
    world.set_tile(width - 1, 1, 2)
    surface = pygame.Surface((width * 16, 64))
    camera = Camera(width * 16, 64, world)
    camera.follow(width / 2, 2)
    world.draw(surface, camera)
    if image_path:
        image_path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(pygame.transform.scale(surface, (width * 64, 256)), str(image_path))
    background = tuple(world._default_bt.color)
    entries = []
    for x, tile_id in enumerate(decorations, 1):
        texture = world._terrain_texture(BLOCK_TYPES[tile_id])
        corner = tuple(surface.get_at((x * 16, 32)))[:3]
        alpha = texture.get_at((0, 0)).a
        entries.append({'block_id': tile_id, 'default_id': default_id,
                        'background': background, 'rendered_corner': corner,
                        'native_corner_alpha': alpha,
                        'composites_on_background': corner == background and alpha == 0})
    return {'default_id': default_id, 'decorations': entries,
            'opaque_black_corner': tuple(surface.get_at((0, 32)))[:3],
            'opaque_black_preserved': tuple(surface.get_at((0, 32)))[:3] == (0, 0, 0)}


def rgba_case(default_id, alpha):
    background = BLOCK_TYPES[default_id].color
    source_color = (90, 140, 180, alpha)
    block = BlockType(4500, 'explicit_rgba', is_solid=False, color=(200, 10, 20),
                      pattern=('vector', (16, 16), (('fill', source_color),
                                                    ('rect', 4, 4, 8, 8, (240, 80, 40)))))
    expected = pygame.Surface((16, 16))
    expected.fill(background)
    overlay = pygame.Surface((16, 16), pygame.SRCALPHA)
    overlay.fill(source_color)
    expected.blit(overlay, (0, 0))
    expected_corner = tuple(expected.get_at((0, 0)))[:3]
    direct = pygame.Surface((16, 16))
    direct.fill(background)
    render_block_pattern(direct, block, 0, 0, 16, 16, overdraw=False)
    catalog = dict(BLOCK_TYPES)
    catalog[block.id] = block
    world = World(0, 'rgba composition', 1, 1, block_types=catalog,
                  default_block_id=default_id, view_blocks_h=1)
    world.set_tile(0, 0, block.id)
    surface = pygame.Surface((16, 16))
    camera = Camera(16, 16, world)
    camera.follow(.5, .5)
    world.draw(surface, camera)
    direct_corner, chunk_corner = tuple(direct.get_at((0, 0)))[:3], tuple(surface.get_at((0, 0)))[:3]
    return {'default_id': default_id, 'alpha': alpha, 'expected_corner': expected_corner,
            'direct_corner': direct_corner, 'chunk_corner': chunk_corner,
            'direct_matches': direct_corner == expected_corner,
            'chunk_matches': chunk_corner == expected_corner,
            'opaque_motif_preserved': tuple(surface.get_at((8, 8)))[:3] == (240, 80, 40)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--images-dir', type=Path)
    parser.add_argument('--blocks', type=int, nargs='+', default=DECORATIONS)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'actual direct pattern and cached world rendering, day/night/black backgrounds; not gameplay or device acceptance',
              'scenes': [scene(i, args.images_dir / f'decorations_background_{i}.png' if args.images_dir else None, args.blocks)
                         for i in (0, 11, 12)],
              'rgba_cases': [rgba_case(i, alpha) for i in (0, 11, 12) for alpha in (0, 128)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'decorations_composited': sum(e['composites_on_background'] for s in report['scenes'] for e in s['decorations']),
                      'rgba_direct': sum(r['direct_matches'] for r in report['rgba_cases']),
                      'rgba_chunks': sum(r['chunk_matches'] for r in report['rgba_cases'])}))


if __name__ == '__main__':
    main()
