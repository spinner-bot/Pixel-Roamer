"""
像素卡通字体系统 —— 用线段拼接字符，替代原生字体渲染。
所有字符定义为关键点坐标，通过绘制粗线段连接成字形。
"""
from __future__ import annotations
import pygame
from typing import List, Tuple, Dict

# ===================== 字体配置 =====================
# 基础设计网格 (宽 x 高)，用于定义字符形状
GRID_W = 10
GRID_H = 14
LINE_WIDTH_BASE = 2.8  # 基础线宽（粗线条，卡通风格）
CHAR_SPACING = 0.85    # 字符间距系数（越大越宽松）

# ===================== 字符关键点数据 =====================
# 每个字符定义为一组线段: [(x1, y1, x2, y2), ...]
# 坐标基于 GRID_W x GRID_H 网格
# 空白字符用空列表

_CHAR_SEGMENTS: Dict[str, List[Tuple[float, float, float, float]]] = {}

# ---- 数字 ----
_CHAR_SEGMENTS['0'] = [
    (2, 2, 8, 2), (8, 2, 8, 12), (8, 12, 2, 12), (2, 12, 2, 2),  # 外框
]
_CHAR_SEGMENTS['1'] = [
    (5, 2, 5, 12), (3, 5, 5, 2),  # 竖 + 顶部短横
]
_CHAR_SEGMENTS['2'] = [
    (2, 2, 8, 2), (8, 2, 8, 6), (8, 6, 2, 6), (2, 6, 2, 12), (2, 12, 8, 12),  # 锯齿形
]
_CHAR_SEGMENTS['3'] = [
    (2, 2, 8, 2), (8, 2, 8, 12), (8, 12, 2, 12), (2, 6, 8, 6),  # E形
]
_CHAR_SEGMENTS['4'] = [
    (2, 2, 2, 7), (2, 7, 8, 7), (7, 2, 7, 12),  # 4形
]
_CHAR_SEGMENTS['5'] = [
    (8, 2, 2, 2), (2, 2, 2, 6), (2, 6, 8, 6), (8, 6, 8, 12), (8, 12, 2, 12),
]
_CHAR_SEGMENTS['6'] = [
    (8, 2, 2, 2), (2, 2, 2, 12), (2, 12, 8, 12), (8, 12, 8, 6), (8, 6, 2, 6),
]
_CHAR_SEGMENTS['7'] = [
    (2, 2, 8, 2), (8, 2, 5, 12),
]
_CHAR_SEGMENTS['8'] = [
    (2, 2, 8, 2), (8, 2, 8, 12), (8, 12, 2, 12), (2, 12, 2, 2),  # 外框
    (2, 6, 8, 6),  # 中间横线
]
_CHAR_SEGMENTS['9'] = [
    (2, 12, 8, 12), (8, 12, 8, 2), (8, 2, 2, 2), (2, 2, 2, 6), (2, 6, 8, 6),
]

# ---- 大写字母 ----
_CHAR_SEGMENTS['A'] = [
    (2, 12, 2, 2), (2, 2, 8, 2), (8, 2, 8, 12), (2, 6, 8, 6),
]
_CHAR_SEGMENTS['B'] = [
    (2, 2, 2, 12), (2, 2, 7, 2), (7, 2, 7, 6), (7, 6, 2, 6),
    (2, 6, 7, 6), (7, 6, 7, 12), (7, 12, 2, 12),
]
_CHAR_SEGMENTS['C'] = [
    (8, 2, 2, 2), (2, 2, 2, 12), (2, 12, 8, 12),
]
_CHAR_SEGMENTS['D'] = [
    (2, 2, 2, 12), (2, 2, 6, 2), (6, 2, 7, 4), (7, 4, 7, 10),
    (7, 10, 6, 12), (6, 12, 2, 12),
]
_CHAR_SEGMENTS['E'] = [
    (2, 2, 8, 2), (2, 2, 2, 12), (2, 12, 8, 12), (2, 6, 6, 6),
]
_CHAR_SEGMENTS['F'] = [
    (2, 2, 8, 2), (2, 2, 2, 12), (2, 6, 6, 6),
]
_CHAR_SEGMENTS['G'] = [
    (8, 2, 2, 2), (2, 2, 2, 12), (2, 12, 8, 12), (8, 12, 8, 8), (8, 8, 5, 8),
]
_CHAR_SEGMENTS['H'] = [
    (2, 2, 2, 12), (8, 2, 8, 12), (2, 6, 8, 6),
]
_CHAR_SEGMENTS['I'] = [
    (3, 2, 7, 2), (5, 2, 5, 12), (3, 12, 7, 12),
]
_CHAR_SEGMENTS['J'] = [
    (7, 2, 7, 10), (7, 10, 4, 12), (4, 12, 2, 10),
]
_CHAR_SEGMENTS['K'] = [
    (2, 2, 2, 12), (2, 6, 8, 2), (2, 6, 8, 12),
]
_CHAR_SEGMENTS['L'] = [
    (2, 2, 2, 12), (2, 12, 8, 12),
]
_CHAR_SEGMENTS['M'] = [
    (2, 12, 2, 2), (2, 2, 5, 6), (5, 6, 8, 2), (8, 2, 8, 12),
]
_CHAR_SEGMENTS['N'] = [
    (2, 12, 2, 2), (2, 2, 8, 12), (8, 2, 8, 12),
]
_CHAR_SEGMENTS['O'] = [
    (2, 2, 8, 2), (8, 2, 8, 12), (8, 12, 2, 12), (2, 12, 2, 2),
]
_CHAR_SEGMENTS['P'] = [
    (2, 2, 2, 12), (2, 2, 8, 2), (8, 2, 8, 6), (8, 6, 2, 6),
]
_CHAR_SEGMENTS['Q'] = [
    (2, 2, 8, 2), (8, 2, 8, 12), (8, 12, 2, 12), (2, 12, 2, 2),
    (5, 9, 8, 12),  # 小尾巴
]
_CHAR_SEGMENTS['R'] = [
    (2, 2, 2, 12), (2, 2, 8, 2), (8, 2, 8, 6), (8, 6, 2, 6),
    (5, 6, 8, 12),
]
_CHAR_SEGMENTS['S'] = [
    (8, 2, 2, 2), (2, 2, 2, 6), (2, 6, 8, 6), (8, 6, 8, 12), (8, 12, 2, 12),
]
_CHAR_SEGMENTS['T'] = [
    (2, 2, 8, 2), (5, 2, 5, 12),
]
_CHAR_SEGMENTS['U'] = [
    (2, 2, 2, 10), (2, 10, 8, 10), (8, 10, 8, 2),
]
_CHAR_SEGMENTS['V'] = [
    (2, 2, 5, 12), (5, 12, 8, 2),
]
_CHAR_SEGMENTS['W'] = [
    (2, 2, 2, 12), (2, 12, 5, 8), (5, 8, 8, 12), (8, 12, 8, 2),
]
_CHAR_SEGMENTS['X'] = [
    (2, 2, 8, 12), (8, 2, 2, 12),
]
_CHAR_SEGMENTS['Y'] = [
    (2, 2, 5, 6), (8, 2, 5, 6), (5, 6, 5, 12),
]
_CHAR_SEGMENTS['Z'] = [
    (2, 2, 8, 2), (8, 2, 2, 12), (2, 12, 8, 12),
]

# ---- 小写字母 ----
_CHAR_SEGMENTS['a'] = _CHAR_SEGMENTS['A']  # fallback
_CHAR_SEGMENTS['b'] = _CHAR_SEGMENTS['B']
_CHAR_SEGMENTS['c'] = [
    (7, 3, 3, 3), (3, 3, 3, 11), (3, 11, 7, 11),
]
_CHAR_SEGMENTS['d'] = _CHAR_SEGMENTS['D']
_CHAR_SEGMENTS['e'] = [
    (7, 3, 3, 3), (3, 3, 3, 11), (3, 11, 7, 11), (3, 7, 6, 7),
]
_CHAR_SEGMENTS['f'] = _CHAR_SEGMENTS['F']
_CHAR_SEGMENTS['g'] = _CHAR_SEGMENTS['G']
_CHAR_SEGMENTS['h'] = _CHAR_SEGMENTS['H']
_CHAR_SEGMENTS['i'] = [(5, 3, 5, 11), (5, 2, 5, 2)]  # 简化的i
_CHAR_SEGMENTS['j'] = _CHAR_SEGMENTS['J']
_CHAR_SEGMENTS['k'] = _CHAR_SEGMENTS['K']
_CHAR_SEGMENTS['l'] = [(5, 2, 5, 12), (3, 12, 7, 12)]
_CHAR_SEGMENTS['m'] = _CHAR_SEGMENTS['M']
_CHAR_SEGMENTS['n'] = _CHAR_SEGMENTS['N']
_CHAR_SEGMENTS['o'] = _CHAR_SEGMENTS['O']
_CHAR_SEGMENTS['p'] = _CHAR_SEGMENTS['P']
_CHAR_SEGMENTS['q'] = _CHAR_SEGMENTS['Q']
_CHAR_SEGMENTS['r'] = _CHAR_SEGMENTS['R']
_CHAR_SEGMENTS['s'] = _CHAR_SEGMENTS['S']
_CHAR_SEGMENTS['t'] = _CHAR_SEGMENTS['T']
_CHAR_SEGMENTS['u'] = _CHAR_SEGMENTS['U']
_CHAR_SEGMENTS['v'] = _CHAR_SEGMENTS['V']
_CHAR_SEGMENTS['w'] = _CHAR_SEGMENTS['W']
_CHAR_SEGMENTS['x'] = _CHAR_SEGMENTS['X']
_CHAR_SEGMENTS['y'] = _CHAR_SEGMENTS['Y']
_CHAR_SEGMENTS['z'] = _CHAR_SEGMENTS['Z']

# ---- 符号 ----
_CHAR_SEGMENTS['.'] = [(4, 11, 5, 11), (5, 11, 5, 12), (5, 12, 4, 12), (4, 12, 4, 11)]
_CHAR_SEGMENTS[','] = [(4, 11, 5, 12), (3, 12, 5, 11)]
_CHAR_SEGMENTS[':'] = [(4, 4, 5, 4), (4, 4, 4, 5), (5, 4, 5, 5),
                        (4, 9, 5, 9), (4, 9, 4, 10), (5, 9, 5, 10)]
_CHAR_SEGMENTS[';'] = [(4, 4, 5, 5), (4, 10, 5, 12)]
_CHAR_SEGMENTS['!'] = [(5, 2, 5, 8), (4, 10, 5, 12), (5, 12, 6, 10)]
_CHAR_SEGMENTS['?'] = [(2, 2, 8, 2), (8, 2, 8, 5), (8, 5, 5, 7), (5, 7, 5, 8),
                        (5, 11, 5, 12)]
_CHAR_SEGMENTS['-'] = [(3, 7, 7, 7)]
_CHAR_SEGMENTS['+'] = [(5, 3, 5, 11), (2, 7, 8, 7)]
_CHAR_SEGMENTS['='] = [(2, 5, 8, 5), (2, 9, 8, 9)]
_CHAR_SEGMENTS['/'] = [(8, 2, 2, 12)]
_CHAR_SEGMENTS['\\'] = [(2, 2, 8, 12)]
_CHAR_SEGMENTS['('] = [(7, 2, 4, 5), (4, 5, 4, 9), (4, 9, 7, 12)]
_CHAR_SEGMENTS[')'] = [(3, 2, 6, 5), (6, 5, 6, 9), (6, 9, 3, 12)]
_CHAR_SEGMENTS['['] = [(7, 2, 3, 2), (3, 2, 3, 12), (3, 12, 7, 12)]
_CHAR_SEGMENTS[']'] = [(3, 2, 7, 2), (7, 2, 7, 12), (7, 12, 3, 12)]
_CHAR_SEGMENTS['_'] = [(2, 12, 8, 12)]
_CHAR_SEGMENTS["'"] = [(5, 2, 5, 5)]
_CHAR_SEGMENTS['"'] = [(3, 2, 3, 5), (7, 2, 7, 5)]
_CHAR_SEGMENTS['*'] = [(5, 2, 5, 12), (2, 5, 8, 9), (8, 5, 2, 9)]
_CHAR_SEGMENTS['#'] = [(3, 2, 3, 12), (7, 2, 7, 12), (2, 5, 8, 5), (2, 9, 8, 9)]
_CHAR_SEGMENTS['%'] = [(2, 2, 4, 2), (4, 2, 4, 4), (4, 4, 2, 4), (2, 4, 2, 2),
                        (8, 10, 6, 10), (6, 10, 6, 12), (6, 12, 8, 12), (8, 12, 8, 10),
                        (8, 2, 2, 12)]
_CHAR_SEGMENTS[' '] = []

# 特殊组合字符
_CHAR_SEGMENTS['♥'] = [
    (5, 2, 3, 5), (3, 5, 3, 7), (3, 7, 5, 10),
    (5, 10, 7, 7), (7, 7, 7, 5), (7, 5, 5, 2),
]
_CHAR_SEGMENTS['★'] = [
    (5, 1, 6, 4), (6, 4, 9, 4), (9, 4, 7, 6),
    (7, 6, 8, 9), (8, 9, 5, 7), (5, 7, 2, 9),
    (2, 9, 3, 6), (3, 6, 1, 4), (1, 4, 4, 4), (4, 4, 5, 1),
]


def get_char_width(target_h: float) -> float:
    """返回给定高度下单个字符的宽度。"""
    return target_h * GRID_W / GRID_H * CHAR_SPACING


def text_width(text: str, target_h: float) -> float:
    """计算文本渲染后的总宽度。"""
    if not text:
        return 0
    cw = get_char_width(target_h)
    return len(text) * cw


def draw_pixel_text(
    surf: pygame.Surface,
    text: str,
    x: float,
    y: float,
    target_h: float,
    color: Tuple[int, int, int] = (255, 255, 255),
    shadow: bool = False,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    center_x: bool = False,
    right_x: bool = False,
):
    """
    在表面上绘制像素卡通文字。

    参数:
        surf: 目标表面
        text: 要绘制的文本
        x, y: 起始位置（左上角）
        target_h: 目标字符高度（像素）
        color: 文字颜色
        shadow: 是否绘制阴影
        shadow_color: 阴影颜色
        center_x: True 时 x 为水平中心
        right_x: True 时 x 为右边缘
    """
    if not text:
        return

    cw = get_char_width(target_h)
    scale = target_h / GRID_H
    lw = max(1.5, LINE_WIDTH_BASE * scale)

    total_w = len(text) * cw

    # 计算起始 x
    if center_x:
        start_x = x - total_w / 2
    elif right_x:
        start_x = x - total_w
    else:
        start_x = x

    def draw_char(ch: str, cx: float, cy: float, col: Tuple[int, int, int]):
        segments = _CHAR_SEGMENTS.get(ch)
        if not segments:
            return
        for sx1, sy1, sx2, sy2 in segments:
            px1 = cx + sx1 * scale
            py1 = cy + sy1 * scale
            px2 = cx + sx2 * scale
            py2 = cy + sy2 * scale
            if abs(px2 - px1) < 0.5 and abs(py2 - py1) < 0.5:
                # 点
                pygame.draw.circle(surf, col, (int(px1), int(py1)), max(1, int(lw / 2)))
            else:
                pygame.draw.line(surf, col, (px1, py1), (px2, py2), max(1, int(lw)))

    for i, ch in enumerate(text):
        cx = start_x + i * cw
        if shadow:
            draw_char(ch, cx + 2, y + 2, shadow_color)
        draw_char(ch, cx, y, color)


def draw_pixel_text_multiline(
    surf: pygame.Surface,
    lines: List[str],
    x: float,
    y: float,
    target_h: float,
    line_spacing: float = 1.3,
    color: Tuple[int, int, int] = (255, 255, 255),
    shadow: bool = False,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    center_x: bool = False,
):
    """绘制多行像素文字，返回结束 y 坐标。"""
    cy = y
    for line in lines:
        draw_pixel_text(surf, line, x, cy, target_h, color, shadow, shadow_color, center_x=center_x)
        cy += target_h * line_spacing
    return cy
