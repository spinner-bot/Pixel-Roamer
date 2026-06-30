"""
统一文本渲染模块 —— 基于 pygame.freetype 的高质量抗锯齿文字。
支持中英文混排，统一替代像素字体和原生字体渲染。
"""
from __future__ import annotations
import pygame
import pygame.freetype
from typing import Tuple, Optional

# ===================== 字体缓存 =====================
_fonts: dict = {}

# 字体优先级链（从左到右尝试，直到找到可用字体）
_FALLBACK = {
    "mono": ["consolas", "cour", "courier", "monospace", "dejavusansmono", None],
    "sans": ["simhei", "msyh", "microsoftyahei", "arial", "dejavusans", None],
}


def _resolve_chain(chain: list) -> str:
    """尝试链中的字体名，返回第一个可用的。"""
    for name in chain:
        try:
            if name is None:
                return None
            f = pygame.freetype.SysFont(name, 20)
            return name
        except (TypeError, ValueError, OSError, Exception):
            continue
    return None


def _get_font(name: str, size: int) -> pygame.freetype.Font:
    """加载字体（带缓存和回退，处理系统字体扫描异常）。"""
    key = (name, size)
    if key in _fonts:
        return _fonts[key]

    chain = _FALLBACK.get(name, [name])
    resolved = _resolve_chain(chain)

    # 尝试创建字体，处理 pygame 内部字体扫描异常
    font = None
    for attempt_name in [resolved, None]:
        try:
            font = pygame.freetype.SysFont(attempt_name, size, bold=True)
            break
        except (TypeError, ValueError, OSError, Exception):
            continue

    if font is None:
        # 终极回退：直接用已知字体文件，绕过 SysFont 的系统扫描
        for fallback_file in ["C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/consola.ttf"]:
            try:
                font = pygame.freetype.Font(fallback_file, size)
                font.antialiased = True
                font.pad = True
                break
            except Exception:
                continue
        if font is None:
            font = pygame.freetype.Font(None, size)

    font.antialiased = True
    font.pad = True
    _fonts[key] = font
    return font


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

    # 投影
    if shadow:
        sr = pygame.Rect(sx + 2, y + 2, w, h)
        font.render_to(surf, sr, text, fgcolor=shadow_color)

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
