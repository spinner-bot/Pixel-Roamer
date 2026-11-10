"""Reproducibly refine pixel art from the pre-art catalog commit, preserving rules."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
import game_text as gt
from pattern import _draw_vector, _draw_bitmap, _draw_texture
from scripts.format_catalogs import formatted

BASELINE_REF = "e53ea03"
BLOCK_IDS = (2, 3, 4, 5, 7, 9, 16, 17, 18, 19, 20, 22)


def original(kind):
    return json.loads(subprocess.check_output(
        ["git", "show", f"{BASELINE_REF}:data/catalogs/{kind}.json"], cwd=ROOT, text=True))


def pattern_image(pattern, size):
    renderer = {"vector": _draw_vector, "bitmap": _draw_bitmap, "texture": _draw_texture}[pattern[0]]
    return renderer(pattern, size, size)


def vector(image):
    width, height = image.get_size()
    base = tuple(image.get_at((0, 0)))[:3]
    commands = [["fill", list(base)]]
    for y in range(height):
        x = 0
        while x < width:
            color = tuple(image.get_at((x, y)))[:3]
            end = x + 1
            while end < width and tuple(image.get_at((end, y)))[:3] == color:
                end += 1
            if color != base:
                commands.append(["rect", x, y, end - x, 1, list(color)])
            x = end
    return ["vector", [width, height], commands]


def terrain(tile_id):
    palettes = {2: ((105, 116, 124), (76, 88, 98), (146, 158, 163)),
                3: ((85, 174, 199), (50, 123, 162), (187, 235, 232)),
                4: ((143, 95, 70), (102, 65, 57), (190, 139, 93)),
                5: ((202, 168, 102), (165, 128, 76), (235, 208, 141)),
                7: ((39, 112, 143), (27, 83, 119), (108, 188, 193)),
                9: ((72, 60, 47), (47, 43, 39), (183, 137, 79)),
                16: ((113, 83, 57), (79, 61, 48), (150, 111, 70)),
                17: ((113, 83, 57), (79, 61, 48), (150, 111, 70)),
                18: ((121, 86, 54), (76, 57, 43), (172, 125, 71)),
                19: ((158, 118, 72), (108, 80, 51), (197, 158, 98)),
                20: ((147, 85, 65), (81, 63, 61), (188, 119, 84)),
                22: ((62, 113, 72), (35, 73, 55), (110, 155, 85))}
    base, shadow, highlight = palettes[tile_id]
    image = pygame.Surface((16, 16))
    image.fill(base)
    rng = random.Random(tile_id * 97)
    for _ in range(19):
        x, y = rng.randrange(1, 15), rng.randrange(1, 15)
        pygame.draw.rect(image, shadow if rng.random() < .6 else highlight, (x, y, 2, 1))
    if tile_id in (2, 4):
        for x, y in ((1, 5), (8, 10)):
            pygame.draw.lines(image, shadow, False, [(x, y), (x + 3, y), (x + 4, y + 1), (x + 6, y + 1)])
        pygame.draw.line(image, highlight, (0, 0), (15, 0))
        pygame.draw.line(image, shadow, (0, 15), (15, 15))
    elif tile_id == 3:
        for x, y in ((2, 4), (9, 11)):
            pygame.draw.line(image, highlight, (x, y), (x + 4, y - 2))
            image.set_at((x + 3, y - 2), (226, 249, 241))
    elif tile_id == 7:
        image.fill(base)
        for y in (1, 6, 11):
            pygame.draw.line(image, shadow, (0, y + 2), (15, y + 2))
            x = (y * 3) % 9
            pygame.draw.line(image, highlight, (x, y), (x + 5, y))
    elif tile_id == 9:
        image.fill(base)
        for x in (3, 11):
            pygame.draw.rect(image, shadow, (x, 0, 3, 16))
            pygame.draw.rect(image, highlight, (x, 0, 1, 16))
        for y in (2, 7, 12):
            pygame.draw.rect(image, (139, 99, 58), (3, y, 11, 3))
            pygame.draw.line(image, (213, 164, 96), (3, y), (13, y))
    elif tile_id == 17:
        pygame.draw.rect(image, (58, 108, 62), (0, 0, 16, 4))
        pygame.draw.rect(image, (116, 165, 84), (0, 0, 16, 1))
        for x in (1, 5, 9, 13):
            pygame.draw.rect(image, (73, 127, 66), (x, 3, 2, 2 + x % 3))
    elif tile_id == 18:
        for x in (1, 5, 11, 14):
            pygame.draw.line(image, shadow, (x, 0), (x, 15))
            pygame.draw.line(image, highlight, (x + 1, 1), (x + 1, 14))
        pygame.draw.rect(image, shadow, (7, 6, 3, 4))
        image.set_at((8, 7), highlight)
    elif tile_id == 19:
        for y in (0, 5, 10, 15):
            pygame.draw.line(image, shadow, (0, y), (15, y))
            if y < 15:
                pygame.draw.line(image, highlight, (0, y + 1), (15, y + 1))
        for x, y in ((4, 2), (12, 7), (7, 12)):
            image.set_at((x, y), shadow)
    elif tile_id == 20:
        for y in (0, 8):
            pygame.draw.line(image, shadow, (0, y), (15, y))
            pygame.draw.line(image, highlight, (0, y + 1), (15, y + 1))
        pygame.draw.line(image, shadow, (8, 1), (8, 7))
        pygame.draw.line(image, shadow, (0, 9), (0, 15))
    elif tile_id == 22:
        for x, y in ((1, 2), (8, 1), (4, 8), (11, 9)):
            pygame.draw.rect(image, shadow, (x, y + 1, 4, 3))
            pygame.draw.line(image, highlight, (x + 1, y), (x + 3, y))
    return image


def custom_symbol(buff_id, surface):
    dark = (12, 20, 28)
    if buff_id == 1:
        pygame.draw.polygon(surface, (211, 83, 109), [(12, 21), (3, 12), (3, 6), (6, 3), (10, 3), (12, 6), (14, 3), (18, 3), (21, 6), (21, 12)])
        pygame.draw.rect(surface, (255, 162, 162), (6, 5, 4, 2))
        pygame.draw.rect(surface, (255, 227, 211), (14, 11, 3, 7))
        pygame.draw.rect(surface, (255, 227, 211), (12, 13, 7, 3))
    elif buff_id in (2, 9, 34, 35, 36):
        color = {2: (94, 172, 214), 9: (204, 128, 65), 34: (155, 177, 192), 35: (159, 129, 209), 36: (226, 193, 107)}[buff_id]
        pygame.draw.polygon(surface, dark, [(12, 1), (22, 5), (21, 15), (17, 20), (12, 23), (7, 20), (3, 15), (2, 5)])
        pygame.draw.polygon(surface, color, [(12, 3), (20, 6), (19, 14), (15, 19), (12, 21), (9, 19), (5, 14), (4, 6)])
        pygame.draw.line(surface, (227, 238, 229), (6, 7), (6, 13), 2)
        pygame.draw.rect(surface, (244, 239, 211), (11, 7, 3, 10))
        pygame.draw.rect(surface, (244, 239, 211), (8, 10, 9, 3))
    elif buff_id == 3:
        pygame.draw.polygon(surface, dark, [(6, 3), (15, 3), (15, 13), (21, 13), (23, 17), (21, 22), (4, 22), (3, 17)])
        pygame.draw.polygon(surface, (119, 180, 207), [(7, 5), (13, 5), (13, 15), (20, 15), (21, 18), (19, 20), (5, 20), (5, 17)])
        pygame.draw.rect(surface, (215, 237, 232), (7, 5, 3, 7))
        pygame.draw.line(surface, (95, 210, 168), (0, 9), (4, 9), 2)
        pygame.draw.line(surface, (95, 210, 168), (1, 13), (3, 13), 2)
    elif buff_id in (4, 5):
        color = (135, 221, 150) if buff_id == 4 else (241, 203, 104)
        points = [(12, 2), (20, 10), (15, 10), (15, 21), (9, 21), (9, 10), (4, 10)] if buff_id == 4 else [(13, 1), (5, 13), (11, 13), (9, 23), (20, 9), (14, 9)]
        pygame.draw.polygon(surface, dark, points)
        pygame.draw.polygon(surface, color, points)
        pygame.draw.line(surface, (240, 245, 215), (12, 5), (10, 9), 2)
    elif buff_id == 16:
        pygame.draw.polygon(surface, (183, 75, 46), [(12, 1), (14, 8), (19, 4), (22, 15), (19, 21), (6, 21), (2, 15), (6, 7), (8, 13)])
        pygame.draw.polygon(surface, (240, 146, 64), [(12, 5), (14, 13), (18, 10), (19, 18), (15, 22), (8, 21), (5, 16), (9, 12)])
        pygame.draw.polygon(surface, (255, 217, 121), [(12, 12), (16, 18), (14, 22), (9, 21), (8, 18)])
    else:
        return False
    return True


def status_icon(entry):
    accent = {'positive': (107, 192, 151), 'neutral': (117, 171, 204), 'negative': (218, 124, 132)}[entry['category']]
    image = pygame.Surface((32, 32))
    image.fill((9, 16, 24))
    pygame.draw.rect(image, (24, 36, 48), (2, 2, 28, 28))
    pygame.draw.lines(image, accent, False, [(2, 3), (2, 1), (29, 1), (29, 3)])
    pygame.draw.line(image, tuple(round(c * .55) for c in accent), (2, 30), (29, 30))
    pygame.draw.rect(image, tuple(round(c * .72) for c in accent), (0, 4, 1, 24))
    pygame.draw.rect(image, tuple(round(c * .42) for c in accent), (31, 4, 1, 24))
    motif = pygame.Surface((24, 24))
    motif.fill((24, 36, 48))
    if not custom_symbol(entry['id'], motif):
        old = pattern_image(entry['icon'], 24)
        background = old.get_at((0, 0))[:3]
        for y in range(24):
            for x in range(24):
                color = old.get_at((x, y))[:3]
                if color != background:
                    motif.set_at((x, y), tuple(min(255, c + 9) for c in color))
    image.blit(motif, (4, 4))
    image.set_at((3, 3), (193, 221, 213))
    return image


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def gallery(kind, old, new, ids):
    cols, width, height = 6, 192, 120
    surface = pygame.Surface((cols * width, 60 + ((len(ids) + cols - 1) // cols) * height))
    surface.fill((11, 18, 29))
    gt.draw(surface, '像素素材精修  /  左：原图  右：新图', 24, 16, 24, (224, 235, 230), 'sans')
    field = 'pattern' if kind == 'blocks' else 'icon'
    for index, item_id in enumerate(ids):
        x, y = index % cols * width, 60 + index // cols * height
        for offset, catalog in ((8, old), (100, new)):
            image = pattern_image(catalog[item_id][field], 64)
            surface.blit(image, (x + offset, y + 4))
        gt.draw(surface, f"{item_id} {new[item_id]['name2']}", x + 8, y + 82, 18, (224, 235, 230), 'sans')
    directory = ROOT / 'docs/进展报告/evidence/art'
    directory.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, str(directory / f'{kind}_before_after.png'))


def main():
    overrides = {'schema_version': 1, 'baseline_ref': BASELINE_REF, 'blocks': {}, 'buffs': {}}
    for kind in ('blocks', 'buffs'):
        document = original(kind)
        before = {entry['id']: json.loads(json.dumps(entry)) for entry in document['entries']}
        chosen = BLOCK_IDS if kind == 'blocks' else tuple(before)
        for entry in document['entries']:
            if entry['id'] not in chosen:
                continue
            field = 'pattern' if kind == 'blocks' else 'icon'
            image = terrain(entry['id']) if kind == 'blocks' else status_icon(entry)
            entry[field] = vector(image)
            rgba = pattern_image(entry[field], 32)
            overrides[kind][str(entry['id'])] = {
                'definition': digest(entry), 'rgba32': hashlib.sha256(pygame.image.tobytes(rgba, 'RGBA')).hexdigest(),
                'reason': 'Reviewed pixel texture refinement' if kind == 'blocks' else 'Consistent category frame and refined status motif'}
        (ROOT / 'data/catalogs' / f'{kind}.json').write_text(formatted(document) + '\n')
        gallery(kind, before, {entry['id']: entry for entry in document['entries']}, chosen)
    (ROOT / 'tests/fixtures/catalog_art_overrides.json').write_text(json.dumps(overrides, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
