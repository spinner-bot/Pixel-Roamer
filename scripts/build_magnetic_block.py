"""Build the Buff-only magnetic flower data package and reviewed added-ID hashes."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from block_type import BlockType
from pattern import render_block_pattern
from resource_catalog import load_blocks
from scripts.format_catalogs import formatted
from scripts.refine_pixel_art import vector, digest


def image():
    art = pygame.Surface((16, 16), pygame.SRCALPHA)
    art.fill((0, 0, 0, 0))
    pygame.draw.rect(art, (44, 85, 69), (7, 8, 2, 8))
    pygame.draw.line(art, (123, 178, 110), (7, 9), (7, 15))
    pygame.draw.rect(art, (51, 113, 82), (3, 11, 5, 2))
    pygame.draw.rect(art, (94, 153, 107), (8, 12, 5, 2))
    pygame.draw.rect(art, (139, 192, 127), (9, 12, 3, 1))
    pygame.draw.rect(art, (62, 49, 78), (3, 2, 4, 5))
    pygame.draw.rect(art, (62, 49, 78), (9, 2, 4, 5))
    pygame.draw.rect(art, (62, 49, 78), (5, 6, 6, 3))
    pygame.draw.rect(art, (193, 77, 105), (4, 3, 2, 4))
    pygame.draw.rect(art, (74, 158, 185), (10, 3, 2, 4))
    pygame.draw.rect(art, (162, 119, 160), (6, 6, 4, 2))
    pygame.draw.rect(art, (245, 149, 154), (4, 1, 2, 2))
    pygame.draw.rect(art, (160, 231, 229), (10, 1, 2, 2))
    return art


def main():
    block = BlockType(439, 'magnetic_bloom', name2='磁引花', is_solid=False,
                      color=(85, 149, 152), pattern=vector(image(), alpha=True),
                      buff_ids=(14,), buff_params_list=((4.,),), buff_durations=(8.,))
    package = ROOT / 'data/catalogs/extensions/blocks_magnetic.json'
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text(formatted({'schema_version': 1, 'kind': 'blocks', 'entries': [asdict(block)]}) + '\n')
    # Hash the same normalized definition and rasterization the runtime loads.
    loaded = load_blocks()[439]
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    render_block_pattern(surface, loaded, 0, 0, 32, 32, overdraw=False)
    definition = asdict(loaded)
    non_art = dict(definition)
    non_art.pop('pattern')
    manifest_path = ROOT / 'tests/fixtures/catalog_extensions.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['blocks']['439'] = {
        'stage': 'A79', 'source': str(package.relative_to(ROOT)),
        'reason': 'User-authorized source block for existing magnetic Buff14, with no block special effect',
        'definition': digest(definition),
        'rgba32': hashlib.sha256(pygame.image.tobytes(surface, 'RGBA')).hexdigest(),
        'non_art': digest(non_art)}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    destination = ROOT / 'docs/进展报告/evidence/art/A79_magnetic_flower.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame.transform.scale(surface, (256, 256)), str(destination))


if __name__ == '__main__':
    main()
