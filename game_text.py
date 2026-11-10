"""
统一文本渲染模块 —— 基于 pygame.freetype 的高质量抗锯齿文字。
支持中英文混排，统一替代像素字体和原生字体渲染。
"""
from __future__ import annotations
import pygame
import pygame.freetype
from typing import Tuple, Optional

# The bundled OFL pixel font keeps CJK and Latin labels readable on a clean OS.
from pathlib import Path

_fonts: dict = {}
_BUNDLED_FONT = Path(__file__).resolve().parent / "assets/fonts/fusion-pixel-12px-zh_hans.otf"
_FALLBACK = {
    "mono": ["consolas", "courier", "dejavusansmono"],
    "sans": ["noto sans cjk sc", "microsoftyahei", "simhei", "dejavusans"],
}


def _resolve_chain(chain):
    for name in chain:
        try:
            path = pygame.font.match_font(name)
        except (OSError, pygame.error):
            continue
        if path is not None:
            return path
    return None


def _get_font(name: str, size: int) -> pygame.freetype.Font:
    key = name, max(1, int(size))
    if key not in _fonts:
        if _BUNDLED_FONT.is_file():
            font = pygame.freetype.Font(str(_BUNDLED_FONT), key[1])
            font.antialiased = False
        else:
            path = _resolve_chain(_FALLBACK.get(name, [name]))
            font = pygame.freetype.Font(path, key[1])
            font.antialiased = True
        font.pad = True
        _fonts[key] = font
    return _fonts[key]


# ===================== 预加载常用字体 =====================
try:
    pygame.freetype.init()
except Exception:
    pass  # 静默失败，后续 _get_font 会回退


def draw(
    surf: pygame.Surface,
    text: str,
    x: float,
    y: float,
    size: int,
    color: Tuple[int, int, int] = (255, 255, 255),
    font_family: str = "mono",
    center_x: bool = False,
    right_x: bool = False,
    shadow: bool = False,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
) -> Tuple[int, int]:
    """
    在表面上绘制高质量抗锯齿文字。

    参数:
        surf: 目标 Surface
        text: 文本内容
        x, y: 左上角位置
        size: 字号
        color: 文字颜色
        font_family: "mono" (等宽) 或 "sans" (黑体/无衬线)
        center_x: True 时 x 为水平中心
        right_x: True 时 x 为右边缘
        shadow: 是否绘制投影
        shadow_color: 投影颜色
    返回:
        (width, height) 实际渲染尺寸
    """
    if not text:
        return (0, 0)

    font = _get_font(font_family, size)
    rect = font.get_rect(text)
    w, h = rect.width, rect.height

    # 计算起始位置
    if center_x:
        sx = x - w // 2
    elif right_x:
        sx = x - w
    else:
        sx = x

    # Match shadow opacity to animated text; a transparent label must not
    # leave a fully opaque shadow behind.
    if len(color) == 4 and color[3] == 0:
        return w, h
    if shadow:
        sr = pygame.Rect(sx + 2, y + 2, w, h)
        shade = (*shadow_color[:3], color[3]) if len(color) == 4 else shadow_color
        font.render_to(surf, sr, text, fgcolor=shade)

    # 正文
    tr = pygame.Rect(sx, y, w, h)
    font.render_to(surf, tr, text, fgcolor=color)
    return (w, h)


def draw_multiline(
    surf: pygame.Surface,
    lines: list,
    x: float,
    y: float,
    size: int,
    line_spacing: float = 1.35,
    color: Tuple[int, int, int] = (255, 255, 255),
    font_family: str = "sans",
    shadow: bool = False,
    center_x: bool = False,
) -> float:
    """绘制多行文字，返回结束 y 坐标。"""
    cy = y
    for line in lines:
        _, h = draw(surf, line, x, cy, size, color, font_family,
                    center_x=center_x, shadow=shadow)
        cy += h * line_spacing
    return cy


# ===================== 兼容旧版辅助函数 =====================
def draw_center(surf, text, size, y, color=(255, 255, 255),
                font_family="sans", shadow=False):
    """居中绘制（兼容 draw_text_center 的签名）。"""
    return draw(surf, text, surf.get_width() // 2, y, size, color,
                font_family, center_x=True, shadow=shadow)


def draw_left(surf, text, size, x, y, color=(255, 255, 255),
              font_family="sans", shadow=False):
    """左对齐绘制（兼容 draw_text_left 的签名）。"""
    return draw(surf, text, x, y, size, color, font_family, shadow=shadow)


def draw_right(surf, text, size, x_right, y, color=(255, 255, 255),
               font_family="sans", shadow=False):
    """右对齐绘制（兼容 draw_text_right 的签名）。"""
    return draw(surf, text, x_right, y, size, color, font_family,
                right_x=True, shadow=shadow)
