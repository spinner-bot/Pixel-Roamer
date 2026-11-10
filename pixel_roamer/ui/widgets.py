"""Shared text layout helpers."""
from __future__ import annotations
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
import game_text as gt

def draw_text_center(surf, font_size, text, y, color=(255,255,255), shadow=False):
    """居中绘制（game_text），返回下一行的 y 坐标。"""
    _, h = gt.draw(surf, text, LOGIC_WIDTH // 2, y, font_size, color,
                   "sans", center_x=True, shadow=shadow)
    return y + h + 4

def draw_text_left(surf, font_size, text, x, y, color=(255,255,255), shadow=False):
    """左对齐绘制，返回下一行的 y 坐标。"""
    _, h = gt.draw(surf, text, x, y, font_size, color, "sans", shadow=shadow)
    return y + h + 4

def draw_text_right(surf, font_size, text, x_right, y, color=(255,255,255), shadow=False):
    """右对齐绘制，x_right 为文字右边缘的 x 坐标。"""
    _, h = gt.draw(surf, text, x_right, y, font_size, color, "sans",
                   right_x=True, shadow=shadow)
    return y + h + 4
