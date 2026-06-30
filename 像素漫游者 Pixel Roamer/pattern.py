"""
# ===================================================================
# 方块图案编码规范 (Block Pattern Encoding Specification)
# ===================================================================
# pattern 属性为 None 时，方块仅使用 color 作为底色。
# 否则 pattern 必须为一个三元组： (format, sub_type, data)
#
# 各字段含义：
#   format : str   编码格式代号，支持 "bitmap"、"texture"、"vector" 等。
#   sub_type : Any 子分类，根据 format 不同而异（见下）。
#   data : Any     正式数据，根据 format 不同而异。
#
# -------------------------------------------------------------------
# 1. 位图格式 ( "bitmap" )
#    pattern = ("bitmap", size, pixels)
#      size  : int 正方形边长（像素）
#      pixels: list[list[tuple[int,int,int]]]  尺寸 size x size
#              每个元素为 (R, G, B) 颜色元组。
#    示例：
#      ("bitmap", 2, [[(255,0,0),(0,255,0)], [(0,0,255),(255,255,0)]])
#
# -------------------------------------------------------------------
# 2. 纹理预设格式 ( "texture" )
#    pattern = ("texture", code, params)
#      code  : str  纹理代码，如 "checkerboard", "gradient_h", "gradient_v"
#      params: dict 或 tuple  纹理参数，取决于 code：
#        - checkerboard: {"size": cell_size, "color1": c1, "color2": c2}
#                        或 (cell_size, c1, c2)
#        - gradient_h: (color_left, color_right)
#        - gradient_v: (color_top, color_bottom)
#    示例：
#      ("texture", "checkerboard", (8, (255,255,255), (0,0,0)))
#
# -------------------------------------------------------------------
# 3. 矢量指令格式 ( "vector" )
#    pattern = ("vector", (vw, vh), commands)
#      vw, vh : float  矢量画布宽高
#      commands: list[tuple]  绘图指令列表
#        每条指令为元组，第一个元素为指令名称字符串。
#        支持指令：
#          ("fill", color)                         填充整个画布
#          ("rect", x, y, w, h, color)             绘制实心矩形
#          ("circle", cx, cy, radius, color)       绘制实心圆
#        坐标基于矢量画布，最终会缩放至实际方块尺寸。
#    示例：
#      ("vector", (16, 16), [
#          ("fill", (255,255,255)),
#          ("rect", 2, 2, 12, 12, (0,0,0)),
#          ("circle", 8, 8, 4, (255,0,0))
#      ])
#
# -------------------------------------------------------------------
# 注意事项：
# - 所有颜色均为 (R, G, B) 整数元组，范围 0-255。
# - 解析器会先绘制底色 color，再叠加图案（图案通常不透明）。
# - 系统会自动缓存已渲染的图案 Surface，以提升性能。
# - 扩展新格式只需在解析器中增加分支。
# ===================================================================
"""

import pygame
from typing import Optional, Tuple
from block_type import BlockType


# 图案缓存：键为 (pattern, width, height)，值为 pygame.Surface
_pattern_cache = {}


def _make_hashable(obj):
    """递归地将列表/字典转换为元组，使对象可哈希"""
    if isinstance(obj, list):
        return tuple(_make_hashable(e) for e in obj)
    if isinstance(obj, tuple):
        return tuple(_make_hashable(e) for e in obj)
    if isinstance(obj, dict):
        return tuple(sorted((_make_hashable(k), _make_hashable(v)) for k, v in obj.items()))
    return obj


def render_block_pattern(surface: pygame.Surface, block_type: BlockType,
                         x: float, y: float, w: float, h: float):
    """
    在 surface 上的 (x, y, w, h) 矩形区域绘制方块图案。
    为保证无黑线，实际绘制尺寸向右下各扩展 1 像素。
    """
    # 目标绘制尺寸 +1 像素消除接缝
    draw_w = w + 1
    draw_h = h + 1
    base_rect = pygame.Rect(x, y, draw_w, draw_h)

    # 1. 填充底色
    pygame.draw.rect(surface, block_type.color, base_rect)

    # 2. 没有图案则直接返回
    if block_type.pattern is None:
        return

    # 使用缓存键：图案 + 扩大后的目标尺寸
    hashable_pattern = _make_hashable(block_type.pattern)
    cache_key = (hashable_pattern, int(draw_w), int(draw_h))
    if cache_key in _pattern_cache:
        pattern_surf = _pattern_cache[cache_key]
        surface.blit(pattern_surf, base_rect)
        return

    # 根据编码格式生成扩大尺寸的图案
    fmt = block_type.pattern[0]
    if fmt == "bitmap":
        pattern_surf = _draw_bitmap(block_type.pattern, draw_w, draw_h)
    elif fmt == "texture":
        pattern_surf = _draw_texture(block_type.pattern, draw_w, draw_h)
    elif fmt == "vector":
        pattern_surf = _draw_vector(block_type.pattern, draw_w, draw_h)
    else:
        return

    if pattern_surf is not None:
        _pattern_cache[cache_key] = pattern_surf
        surface.blit(pattern_surf, base_rect)


def _draw_bitmap(pattern: Tuple, w: float, h: float) -> Optional[pygame.Surface]:
    """
    位图格式：( "bitmap", size, pixels )
    size: int 正方形边长
    pixels: 二维列表，每个元素为 (R, G, B)
    """
    try:
        _, size, pixels = pattern
        src = pygame.Surface((size, size), pygame.SRCALPHA)
        for row in range(size):
            for col in range(size):
                color = pixels[row][col]
                src.set_at((col, row), color)
        return pygame.transform.scale(src, (int(w), int(h)))
    except Exception:
        return None


def _draw_texture(pattern: Tuple, w: float, h: float) -> Optional[pygame.Surface]:
    """
    纹理预设格式：( "texture", code, params )
    code: 纹理代码
    params: 参数（字典或元组）
    """
    try:
        _, code, params = pattern
        surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        if code == "checkerboard":
            if isinstance(params, dict):
                cell = params.get("size", 8)
                c1 = params.get("color1", (0,0,0))
                c2 = params.get("color2", (255,255,255))
            else:
                cell, c1, c2 = params
            for y in range(0, int(h), cell):
                for x in range(0, int(w), cell):
                    color = c1 if ((x // cell) + (y // cell)) % 2 == 0 else c2
                    rect = pygame.Rect(x, y, cell, cell)
                    pygame.draw.rect(surf, color, rect)
            return surf
        elif code == "gradient_h":
            c_left, c_right = params
            for x in range(int(w)):
                t = x / max(1, w - 1)
                r = int(c_left[0] * (1 - t) + c_right[0] * t)
                g = int(c_left[1] * (1 - t) + c_right[1] * t)
                b = int(c_left[2] * (1 - t) + c_right[2] * t)
                pygame.draw.line(surf, (r, g, b), (x, 0), (x, int(h)))
            return surf
        elif code == "gradient_v":
            c_top, c_bottom = params
            for y in range(int(h)):
                t = y / max(1, h - 1)
                r = int(c_top[0] * (1 - t) + c_bottom[0] * t)
                g = int(c_top[1] * (1 - t) + c_bottom[1] * t)
                b = int(c_top[2] * (1 - t) + c_bottom[2] * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (int(w), y))
            return surf
        else:
            return None
    except Exception:
        return None


def _draw_vector(pattern: Tuple, w: float, h: float) -> Optional[pygame.Surface]:
    """
    矢量格式：( "vector", (vw, vh), commands )
    (vw, vh) 为矢量画布尺寸，commands 为指令列表。
    """
    try:
        _, (vw, vh), commands = pattern
        src = pygame.Surface((int(vw), int(vh)), pygame.SRCALPHA)
        for cmd in commands:
            kind = cmd[0]
            if kind == "fill":
                src.fill(cmd[1])
            elif kind == "rect":
                _, rx, ry, rw, rh, color = cmd
                pygame.draw.rect(src, color, (rx, ry, rw, rh))
            elif kind == "circle":
                _, cx, cy, r, color = cmd
                pygame.draw.circle(src, color, (int(cx), int(cy)), int(r))
        return pygame.transform.scale(src, (int(w), int(h)))
    except Exception:
        return None
