"""Upright native pixel decorations on explicit transparent canvases."""
import pygame

DECORATION_IDS = (43, 50, 51, 52, 53, 54)


def decoration(tile_id):
    image = pygame.Surface((16, 16), pygame.SRCALPHA)
    image.fill((0, 0, 0, 0))
    if tile_id == 43:
        pygame.draw.rect(image, (76, 47, 35), (6, 7, 4, 9))
        pygame.draw.rect(image, (168, 107, 56), (7, 8, 2, 7))
        pygame.draw.rect(image, (221, 161, 85), (7, 9, 1, 5))
        pygame.draw.rect(image, (96, 88, 81), (5, 7, 6, 2))
        pygame.draw.polygon(image, (192, 67, 36), [(8, 0), (9, 3), (11, 2), (12, 6), (10, 9), (5, 9), (3, 6), (5, 2), (6, 5)])
        pygame.draw.polygon(image, (245, 151, 48), [(8, 2), (9, 5), (10, 4), (10, 7), (8, 9), (5, 7), (6, 5), (7, 6)])
        pygame.draw.rect(image, (255, 232, 141), (7, 6, 2, 2))
    elif tile_id in (50, 51):
        pygame.draw.rect(image, (35, 87, 56), (7, 7, 2, 9))
        pygame.draw.line(image, (113, 171, 78), (7, 8), (7, 15))
        pygame.draw.polygon(image, (53, 124, 66), [(7, 13), (3, 12), (2, 9), (5, 10)])
        pygame.draw.polygon(image, (85, 151, 70), [(8, 11), (12, 8), (13, 8), (12, 11)])
        dark, base, light = (((130, 37, 62), (218, 70, 91), (255, 151, 151))
                             if tile_id == 50 else ((182, 105, 37), (244, 194, 62), (255, 235, 142)))
        pygame.draw.rect(image, dark, (5, 1, 5, 7))
        pygame.draw.rect(image, dark, (3, 3, 9, 3))
        pygame.draw.rect(image, base, (5, 2, 5, 5))
        pygame.draw.rect(image, base, (4, 3, 7, 3))
        pygame.draw.rect(image, light, (5, 2, 2, 2))
        pygame.draw.rect(image, (255, 222, 117), (7, 4, 2, 2))
    elif tile_id in (52, 53):
        pygame.draw.rect(image, (117, 87, 64), (6, 8, 4, 8))
        pygame.draw.rect(image, (220, 195, 151), (7, 9, 2, 6))
        pygame.draw.rect(image, (255, 224, 176), (7, 10, 1, 4))
        dark, base, light = (((119, 40, 55), (211, 67, 76), (255, 157, 142))
                             if tile_id == 52 else ((85, 57, 48), (150, 99, 65), (212, 158, 102)))
        pygame.draw.rect(image, dark, (2, 6, 12, 4))
        pygame.draw.rect(image, dark, (4, 4, 8, 3))
        pygame.draw.rect(image, base, (3, 6, 10, 2))
        pygame.draw.rect(image, base, (5, 4, 6, 4))
        pygame.draw.rect(image, light, (5, 4, 4, 1))
        pygame.draw.rect(image, (244, 220, 174), (4, 6, 2, 1))
        pygame.draw.rect(image, (244, 220, 174), (9, 5, 2, 2))
        pygame.draw.line(image, (190, 157, 119), (4, 9), (11, 9))
    elif tile_id == 54:
        shadow, wood, light = (91, 62, 48), (158, 112, 67), (205, 155, 93)
        branches = [[(7, 15), (7, 9), (9, 6), (9, 2)],
                    [(7, 12), (3, 9), (2, 5)], [(7, 10), (12, 7), (13, 4)],
                    [(4, 10), (2, 10)], [(9, 7), (6, 4), (6, 2)],
                    [(11, 8), (14, 8)]]
        for points in branches:
            pygame.draw.lines(image, shadow, False, points, 2)
            pygame.draw.lines(image, wood, False, points)
        pygame.draw.line(image, light, (7, 12), (7, 15))
        image.set_at((9, 2), light)
        image.set_at((2, 5), light)
    else:
        raise ValueError(f'Unknown decoration: {tile_id}')
    return image
