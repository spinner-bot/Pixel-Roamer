"""Check actual catalog-card compositing for explicitly transparent sprites."""
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
import game_text as gt
from block_types_data import BLOCK_TYPES
from pattern import pattern_has_alpha_canvas
from pixel_roamer.ui.references import ReferenceBrowser
from pixel_roamer.ui.theme import PALETTE as P


def measure(output):
    browser = ReferenceBrowser(None)
    ids = [i for i, block in BLOCK_TYPES.items() if pattern_has_alpha_canvas(block.pattern)]
    surface = pygame.Surface((960, 40 + ((len(ids) + 7) // 8) * 100))
    surface.fill(P['background'])
    results = []
    for index, tile_id in enumerate(ids):
        icon = browser._image('block', BLOCK_TYPES[tile_id], 64)
        card = pygame.Surface((64, 64))
        card.fill(P['panel'])
        card.blit(icon, (0, 0))
        alpha = icon.get_at((0, 0)).a
        corner = tuple(card.get_at((0, 0)))[:3]
        results.append({'block_id': tile_id, 'corner_alpha': alpha, 'card_corner': corner,
                        'composites': alpha == 0 and corner == tuple(P['panel'])})
        x, y = index % 8 * 120 + 28, 24 + index // 8 * 100
        surface.blit(card, (x, y))
        gt.draw(surface, str(tile_id), x, y + 68, 16, P['text'])
    image_path = output.with_suffix('.png')
    pygame.image.save(surface, str(image_path))
    opaque = browser._image('block', BLOCK_TYPES[12], 64)
    return {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'real ReferenceBrowser cached icons on the existing panel color, not device acceptance',
            'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                        ('pixel_roamer/ui/references.py', 'data/catalogs/blocks.json')},
            'entries': results, 'image': image_path.name,
            'opaque_black_preserved': tuple(opaque.get_at((0, 0))) == (0, 0, 0, 255)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = measure(args.output)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sprites': len(result['entries']),
                      'composites': sum(r['composites'] for r in result['entries']),
                      'opaque_black_preserved': result['opaque_black_preserved']}))
