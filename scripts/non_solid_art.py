"""Transparent art for existing background flora, web and pickup state pairs."""
import pygame
from scripts.decorative_art import decoration
from scripts.pickup_art import pickup, BACKGROUND

FLORA_ALIASES = {126: 50, 127: 51, 128: 52, 129: 53, 130: 54}
SPRITE_IDS = tuple(FLORA_ALIASES) + (299,) + tuple(range(310, 330))
COMPARISON_REF = 'a8d3e8e'


def transparent_sprite(tile_id):
    if tile_id in FLORA_ALIASES:
        return decoration(FLORA_ALIASES[tile_id])
    image = pygame.Surface((16, 16), pygame.SRCALPHA)
    image.fill((0, 0, 0, 0))
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
