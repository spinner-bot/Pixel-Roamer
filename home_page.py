"""Pixel home menu with one shared layout for rendering and hit testing."""
from __future__ import annotations
import math
import random
import pygame
import game_text as gt
from pixel_roamer.ui.theme import PALETTE as P, panel, key_hint
from resource_catalog import load_home_menu

MENU_START, MENU_SETTINGS, MENU_DEV, MENU_QUIT = range(4)
_MENU_ITEMS = load_home_menu()
_selected_index = 0
_elapsed = 0.0
_quit_requested = False
_stars = []


def init_home_page(logic_w, logic_h):
    global _selected_index, _elapsed, _quit_requested, _stars
    _selected_index, _elapsed, _quit_requested = 0, 0.0, False
    rng = random.Random(42)
    _stars = [(rng.randrange(176), rng.randrange(12, 68), rng.random() * 6) for _ in range(28)]


def menu_layout(logic_w, logic_h):
    x, y = int(logic_w * 0.05), int(logic_h * 0.345)
    width, height, gap = int(logic_w * 0.35), int(logic_h * 0.092), 12
    return [pygame.Rect(x, y + index * (height + gap), width, height) for index in range(len(_MENU_ITEMS))]


def get_selected_action():
    return _MENU_ITEMS[_selected_index]['id']


def set_selected_index(index):
    global _selected_index
    _selected_index = index % len(_MENU_ITEMS)


def move_selection(delta):
    set_selected_index(_selected_index + delta)


def is_quit_requested():
    return _quit_requested


def _draw_vista():
    canvas = pygame.Surface((176, 112))
    canvas.fill((20, 39, 59))
    for y, color in ((24, (28, 53, 71)), (48, (37, 69, 81)), (70, (54, 85, 89))):
        pygame.draw.rect(canvas, color, (0, y, 176, 112 - y))
    for x, y, phase in _stars:
        brightness = 135 + int(55 * math.sin(_elapsed * 0.8 + phase))
        canvas.set_at((x, y), (brightness, brightness + 12, min(255, brightness + 25)))
    pygame.draw.rect(canvas, (239, 218, 158), (139, 15, 10, 10))
    pygame.draw.rect(canvas, (20, 39, 59), (135, 12, 10, 10))
    pygame.draw.polygon(canvas, (28, 57, 69), [(0, 72), (0, 60), (24, 37), (55, 69), (88, 40), (127, 75), (176, 45), (176, 112), (0, 112)])
    pygame.draw.polygon(canvas, (35, 74, 78), [(0, 78), (33, 58), (60, 83), (108, 57), (151, 79), (176, 67), (176, 112), (0, 112)])
    # Cliff, grass, water and a small floating ledge use a native pixel grid.
    pygame.draw.rect(canvas, (57, 48, 47), (9, 79, 158, 33))
    pygame.draw.rect(canvas, (100, 72, 50), (9, 79, 158, 8))
    pygame.draw.rect(canvas, (83, 139, 93), (9, 76, 158, 4))
    pygame.draw.rect(canvas, (141, 182, 103), (9, 75, 158, 2))
    for x in range(14, 165, 13):
        pygame.draw.rect(canvas, (78, 60, 48), (x, 93 + x % 7, 5, 3))
    pygame.draw.rect(canvas, (40, 103, 127), (111, 81, 29, 31))
    for row in range(84, 112, 7):
        shift = int(_elapsed * 3 + row) % 9
        pygame.draw.rect(canvas, (89, 167, 173), (114 + shift, row, 9, 1))
    pygame.draw.rect(canvas, (60, 52, 48), (49, 49, 26, 7))
    pygame.draw.rect(canvas, (113, 166, 101), (47, 46, 30, 4))
    for tx, ty, height in ((27, 75, 21), (151, 75, 27), (59, 46, 14)):
        pygame.draw.rect(canvas, (72, 53, 40), (tx, ty - height, 3, height))
        pygame.draw.rect(canvas, (33, 76, 62), (tx - 7, ty - height - 8, 18, 14))
        pygame.draw.rect(canvas, (67, 119, 76), (tx - 8, ty - height - 6, 18, 10))
        pygame.draw.rect(canvas, (111, 160, 91), (tx - 4, ty - height - 9, 10, 6))
    pygame.draw.rect(canvas, (94, 64, 41), (86, 73, 9, 3))
    flame = int(_elapsed * 6) % 2
    pygame.draw.rect(canvas, (213, 113, 55), (88, 66 - flame, 5, 8 + flame))
    pygame.draw.rect(canvas, (247, 205, 99), (89, 68 - flame, 2, 5))
    from costumes import COSTUMES, DEFAULT_COSTUME_ID
    hero = COSTUMES[DEFAULT_COSTUME_ID]['src_frames']['idle'][0]
    canvas.blit(pygame.transform.scale(hero, (8, 16)), (101, 63))
    return canvas


def run_home_page(surf, dt, logic_w, logic_h):
    global _elapsed
    _elapsed += dt
    surf.fill(P['background'])
    left = int(logic_w * 0.05)
    gt.draw(surf, 'P I X E L   R O A M E R', left, 54, 18, P['mint'])
    gt.draw(surf, '像素漫游者', left - 2, 98, 60, P['text'], 'sans')
    gt.draw(surf, '走过每一格，发现新的风景。', left, 192, 24, P['muted'], 'sans')
    for index, (item, rect) in enumerate(zip(_MENU_ITEMS, menu_layout(logic_w, logic_h))):
        selected = index == _selected_index
        panel(surf, rect, selected)
        number_color = P['accent'] if selected else P['muted']
        gt.draw(surf, f'0{index + 1}', rect.x + 22, rect.y + 25, 24, number_color)
        gt.draw(surf, item['label'], rect.x + 82, rect.y + 11, 30, P['text'], 'sans')
        gt.draw(surf, item['description'], rect.x + 83, rect.y + 48, 18, P['muted'], 'sans')
        if selected:
            pygame.draw.polygon(surf, P['accent'], [(rect.right - 28, rect.centery - 5),
                                                   (rect.right - 22, rect.centery),
                                                   (rect.right - 28, rect.centery + 5)])
    scene_rect = pygame.Rect(int(logic_w * .475), 220, 760, 496)
    gt.draw(surf, '探索，从一格开始', scene_rect.x, 158, 30, P['accent'], 'sans')
    panel(surf, scene_rect)
    surf.blit(pygame.transform.scale(_draw_vista(), (704, 448)), (scene_rect.x + 28, scene_rect.y + 24))
    gt.draw(surf, '跳跃 · 攀爬 · 收集 · 自由探索', scene_rect.x + scene_rect.w // 2, 738, 21, P['muted'], 'sans', center_x=True)
    pygame.draw.line(surf, P['border'], (left, 802), (logic_w - left, 802))
    x = key_hint(surf, '↑ ↓', '选择', left, 830)
    x = key_hint(surf, 'Enter', '确认', x, 830)
    key_hint(surf, 'Esc', '地图列表', x, 830)
    gt.draw(surf, '像素世界，慢慢走。', logic_w - left, 836, 18, P['muted'], 'sans', right_x=True)


def handle_home_input(event):
    global _quit_requested
    if event.type != pygame.KEYDOWN:
        return None
    if event.key in (pygame.K_UP, pygame.K_w):
        move_selection(-1)
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        move_selection(1)
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
        action = get_selected_action()
        _quit_requested = action == MENU_QUIT
        return action
    elif pygame.K_1 <= event.key <= pygame.K_4:
        set_selected_index(event.key - pygame.K_1)
        action = get_selected_action()
        _quit_requested = action == MENU_QUIT
        return action
    return None


def handle_home_mouse(pos, logic_w, logic_h, scale, draw_offset_x, draw_offset_y):
    if scale <= 0:
        return None
    point = ((pos[0] - draw_offset_x) / scale, (pos[1] - draw_offset_y) / scale)
    for index, rect in enumerate(menu_layout(logic_w, logic_h)):
        if rect.collidepoint(point):
            set_selected_index(index)
            return get_selected_action()
    return None
