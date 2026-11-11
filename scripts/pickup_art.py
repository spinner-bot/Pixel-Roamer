"""Native 16px silhouettes for the ten existing score pickups."""
import pygame

PICKUP_IDS = tuple(range(310, 320))
BACKGROUND = (9, 15, 24)
INK = (24, 34, 49)


def pickup(tile_id):
    image = pygame.Surface((16, 16))
    image.fill(BACKGROUND)
    if tile_id in (310, 311):
        dark, base, light = (((137, 82, 32), (227, 173, 62), (255, 234, 151))
                             if tile_id == 310 else ((75, 100, 124), (164, 193, 207), (236, 250, 250)))
        outline = [(5, 2), (10, 2), (13, 5), (13, 10), (10, 13), (5, 13), (2, 10), (2, 5)]
        pygame.draw.polygon(image, INK, outline)
        pygame.draw.polygon(image, dark, [(5, 3), (10, 3), (12, 5), (12, 10), (10, 12), (5, 12), (3, 10), (3, 5)])
        pygame.draw.rect(image, base, (5, 4, 6, 7))
        pygame.draw.rect(image, base, (4, 5, 8, 5))
        pygame.draw.line(image, light, (5, 4), (9, 4))
        pygame.draw.line(image, light, (4, 5), (4, 8))
        pygame.draw.line(image, dark, (7, 6), (7, 9))
        pygame.draw.line(image, light, (8, 6), (8, 9))
        if tile_id == 311:
            pygame.draw.rect(image, light, (11, 2, 1, 3))
            pygame.draw.rect(image, light, (10, 3, 3, 1))
    elif tile_id in (312, 313, 314, 315):
        palettes = {312: ((107, 30, 57), (208, 57, 81), (255, 155, 160)),
                    313: ((36, 56, 119), (67, 124, 211), (156, 216, 255)),
                    314: ((50, 108, 147), (102, 197, 218), (219, 255, 250)),
                    315: ((27, 89, 77), (54, 176, 120), (161, 248, 177))}
        dark, base, light = palettes[tile_id]
        shapes = {312: [(8, 1), (13, 6), (11, 11), (8, 14), (3, 9), (3, 6)],
                  313: [(4, 3), (11, 3), (14, 7), (11, 12), (4, 12), (1, 7)],
                  314: [(4, 3), (11, 3), (14, 6), (8, 14), (1, 6)],
                  315: [(5, 1), (10, 1), (12, 4), (12, 11), (10, 14), (5, 14), (3, 11), (3, 4)]}
        pygame.draw.polygon(image, dark, shapes[tile_id])
        if tile_id == 312:
            pygame.draw.polygon(image, base, [(8, 3), (11, 6), (8, 12), (5, 8)])
            pygame.draw.polygon(image, light, [(8, 3), (8, 7), (5, 8), (5, 6)])
        elif tile_id == 313:
            pygame.draw.polygon(image, base, [(5, 4), (10, 4), (12, 7), (10, 10), (5, 10), (3, 7)])
            pygame.draw.polygon(image, light, [(5, 4), (10, 4), (8, 7), (3, 7)])
        elif tile_id == 314:
            pygame.draw.polygon(image, base, [(5, 4), (10, 4), (12, 6), (8, 11), (3, 6)])
            pygame.draw.polygon(image, light, [(5, 4), (10, 4), (12, 6), (3, 6)])
            pygame.draw.line(image, light, (7, 7), (8, 11))
        else:
            pygame.draw.rect(image, base, (5, 3, 6, 9))
            pygame.draw.rect(image, light, (5, 3, 2, 8))
            pygame.draw.line(image, dark, (9, 4), (9, 10))
        pygame.draw.rect(image, (244, 255, 245), (6, 4, 1, 1))
    elif tile_id == 316:
        points = [(8, 1), (10, 5), (14, 6), (11, 9), (12, 14), (8, 11), (3, 14), (4, 9), (1, 6), (6, 5)]
        pygame.draw.polygon(image, (151, 111, 48), points)
        pygame.draw.polygon(image, (247, 211, 96), [(8, 3), (9, 6), (12, 7), (9, 9), (10, 11), (8, 10), (5, 11), (6, 8), (4, 7), (7, 6)])
        pygame.draw.rect(image, (255, 248, 195), (7, 5, 2, 3))
    elif tile_id == 317:
        pygame.draw.ellipse(image, (100, 64, 152), (1, 4, 14, 8), 1)
        pygame.draw.circle(image, (58, 37, 92), (8, 7), 5)
        pygame.draw.circle(image, (139, 86, 193), (8, 7), 4)
        pygame.draw.circle(image, (27, 24, 53), (9, 8), 3)
        pygame.draw.rect(image, (224, 188, 255), (5, 4, 3, 1))
        pygame.draw.rect(image, (179, 125, 221), (4, 5, 1, 2))
        pygame.draw.line(image, (188, 144, 238), (2, 10), (5, 11))
    elif tile_id == 318:
        for rect in ((7, 1, 2, 2), (7, 13, 2, 2), (1, 7, 2, 2), (13, 7, 2, 2),
                     (3, 3, 2, 2), (11, 3, 2, 2), (3, 11, 2, 2), (11, 11, 2, 2)):
            pygame.draw.rect(image, (224, 147, 57), rect)
        pygame.draw.circle(image, (149, 80, 38), (8, 8), 5)
        pygame.draw.circle(image, (250, 194, 75), (8, 8), 4)
        pygame.draw.rect(image, (255, 238, 156), (6, 5, 3, 2))
        pygame.draw.line(image, (255, 219, 117), (5, 7), (5, 9))
    elif tile_id == 319:
        pygame.draw.circle(image, (81, 115, 157), (7, 8), 6)
        pygame.draw.circle(image, (200, 223, 236), (7, 8), 5)
        pygame.draw.circle(image, BACKGROUND, (10, 5), 5)
        pygame.draw.line(image, (245, 255, 250), (3, 8), (3, 10))
        pygame.draw.rect(image, (163, 202, 244), (12, 8, 1, 4))
        pygame.draw.rect(image, (163, 202, 244), (11, 9, 3, 1))
    else:
        raise ValueError('unknown score pickup')
    return image
