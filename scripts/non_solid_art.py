"""Transparent art for existing background flora, web and pickup state pairs."""
import pygame
from scripts.decorative_art import decoration
from scripts.pickup_art import pickup, BACKGROUND

FLORA_ALIASES = {126: 50, 127: 51, 128: 52, 129: 53, 130: 54}
SPRITE_IDS = (31, 96) + tuple(FLORA_ALIASES) + (299,) + tuple(range(310, 330))
COMPARISON_REF = 'a8d3e8e'


def transparent_sprite(tile_id):
    if tile_id in FLORA_ALIASES:
        return decoration(FLORA_ALIASES[tile_id])
    image = pygame.Surface((16, 16), pygame.SRCALPHA)
    image.fill((0, 0, 0, 0))
    if tile_id == 31:
        pygame.draw.rect(image, (65, 49, 40), (6, 0, 4, 16))
        pygame.draw.rect(image, (151, 104, 60), (7, 0, 2, 16))
        for y in range(0, 16, 2):
            image.set_at((7, y), (221, 176, 107))
            image.set_at((8, y + 1), (193, 140, 80))
        for y in (2, 7, 12):
            pygame.draw.rect(image, (65, 49, 40), (5, y, 6, 3))
            pygame.draw.rect(image, (181, 131, 75), (6, y, 4, 2))
            pygame.draw.line(image, (235, 190, 119), (6, y), (9, y))
        return image
    if tile_id == 96:
        pygame.draw.rect(image, (184, 213, 226, 48), (4, 1, 8, 12))
        pygame.draw.rect(image, (85, 122, 143), (6, 1, 4, 12))
        pygame.draw.rect(image, (194, 230, 232), (7, 2, 2, 10))
        pygame.draw.line(image, (255, 255, 225), (7, 2), (7, 10))
        pygame.draw.rect(image, (255, 252, 217), (6, 0, 4, 3))
        pygame.draw.rect(image, (94, 67, 111), (4, 13, 8, 3))
        pygame.draw.rect(image, (159, 121, 161), (5, 12, 6, 2))
        pygame.draw.line(image, (217, 177, 190), (5, 12), (10, 12))
        image.set_at((8, 1), (255, 255, 255))
        return image
    if tile_id == 299:
        spokes = [((2, 2), (13, 13)), ((13, 2), (2, 13)),
                  ((1, 7), (14, 7)), ((7, 1), (7, 14))]
        rings = [[(3, 3), (7, 2), (12, 3), (13, 7), (12, 12), (7, 13), (3, 12), (2, 7)],
                 [(5, 5), (7, 4), (10, 5), (11, 7), (10, 10), (7, 11), (5, 10), (4, 7)]]
        for color, width in (((65, 91, 110), 2), ((205, 220, 220), 1)):
            for points in spokes:
                pygame.draw.lines(image, color, False, points, width)
            for points in rings:
                pygame.draw.lines(image, color, True, points, width)
        image.set_at((6, 6), (247, 244, 218))
        return image
    if not 310 <= tile_id < 330:
        raise ValueError(f'Unknown non-solid sprite: {tile_id}')
    used = tile_id >= 320
    source = pickup(tile_id - 10 if used else tile_id)
    for y in range(16):
        for x in range(16):
            color = tuple(source.get_at((x, y)))[:3]
            if color == BACKGROUND:
                continue
            if used:
                color = (32 + round(color[0] * .32), 40 + round(color[1] * .30),
                         50 + round(color[2] * .28))
            image.set_at((x, y), color)
    return image
