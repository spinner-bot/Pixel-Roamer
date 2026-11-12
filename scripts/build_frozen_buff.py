"""Build the user-authorized cold-water outcome and its separate ID manifest."""
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
from buff_system import BuffType, CAT_NEGATIVE
from pattern import _draw_vector
from resource_catalog import load_buffs
from scripts.format_catalogs import formatted
from scripts.refine_pixel_art import digest, vector


def image():
    surface = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (29, 58, 89), [(4, 1), (11, 1), (14, 5), (14, 12),
                                             (11, 15), (4, 15), (1, 12), (1, 5)])
    pygame.draw.polygon(surface, (78, 150, 195), [(4, 2), (11, 2), (13, 5), (13, 12),
                                              (10, 14), (5, 14), (2, 11), (2, 5)])
    pygame.draw.polygon(surface, (146, 221, 238), [(4, 2), (11, 2), (8, 7), (2, 5)])
    pygame.draw.polygon(surface, (54, 116, 172), [(8, 8), (13, 5), (13, 12), (10, 14)])
    pygame.draw.line(surface, (219, 250, 251), (8, 4), (8, 12))
    pygame.draw.line(surface, (219, 250, 251), (4, 8), (12, 8))
    for end in ((5, 5), (11, 5), (5, 11), (11, 11)):
        pygame.draw.line(surface, (219, 250, 251), (8, 8), end)
    pygame.draw.rect(surface, (255, 255, 255), (7, 7, 3, 3))
    pygame.draw.line(surface, (190, 241, 249), (4, 3), (6, 3))
    return surface


def main():
    effect = BuffType(59, 'frozen', name2='冻结', category=CAT_NEGATIVE,
                      icon=vector(image(), alpha=True),
                      desc='无法主动移动、跳跃、攀爬或游泳，持续 {0} 秒',
                      cleanup_by=(40,), tick='frozen', on_apply='halt_motion')
    package = ROOT / 'data/catalogs/extensions/buffs_frozen.json'
    package.write_text(formatted({'schema_version': 1, 'kind': 'buffs', 'entries': [asdict(effect)]}) + '\n')
    loaded = load_buffs()[59]
    definition = asdict(loaded)
    non_art = dict(definition)
    non_art.pop('icon')
    surface = _draw_vector(loaded.icon, 32, 32)
    path = ROOT / 'tests/fixtures/catalog_extensions.json'
    manifest = json.loads(path.read_text())
    manifest['buffs']['59'] = {
        'stage': 'A91', 'source': str(package.relative_to(ROOT)),
        'reason': 'User-authorized finite cold-water outcome for existing51; legacy58 untouched',
        'definition': digest(definition),
        'rgba32': hashlib.sha256(pygame.image.tobytes(surface, 'RGBA')).hexdigest(),
        'non_art': digest(non_art)}
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    destination = ROOT / 'docs/进展报告/evidence/art/A91_frozen_buff.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(pygame.transform.scale(surface, (256, 256)), str(destination))


if __name__ == '__main__':
    main()
