"""Shared pixel panels, palette and keyboard hints."""
import json
from pathlib import Path
import pygame
import game_text as gt

_DATA = json.loads((Path(__file__).resolve().parents[2] / "data/theme.json").read_text())
if _DATA.get("schema_version") != 1:
    raise ValueError("unsupported interface theme version")
PALETTE = {}
for _name, _color in _DATA["palette"].items():
    if len(_color) != 3 or any(type(c) is not int or not 0 <= c <= 255 for c in _color):
        raise ValueError(f"invalid theme color {_name}")
    PALETTE[_name] = tuple(_color)


def panel(surface, rect, selected=False, accent=None):
    rect = pygame.Rect(rect)
    accent = accent or PALETTE["accent"]
    cut = 6
    points = [(rect.left + cut, rect.top), (rect.right - cut, rect.top),
              (rect.right, rect.top + cut), (rect.right, rect.bottom - cut),
              (rect.right - cut, rect.bottom), (rect.left + cut, rect.bottom),
              (rect.left, rect.bottom - cut), (rect.left, rect.top + cut)]
    pygame.draw.polygon(surface, (6, 11, 18), [(x, y + 4) for x, y in points])
    pygame.draw.polygon(surface, PALETTE["raised"] if selected else PALETTE["panel"], points)
    pygame.draw.polygon(surface, accent if selected else PALETTE["border"], points, 2)


def key_hint(surface, key, label, x, y):
    width = max(36, gt._get_font("mono", 18).get_rect(key).width + 16)
    pygame.draw.rect(surface, PALETTE["raised"], (x, y, width, 30))
    pygame.draw.rect(surface, PALETTE["border"], (x, y, width, 30), 1)
    gt.draw(surface, key, x + width // 2, y + 4, 18, PALETTE["text"], center_x=True)
    gt.draw(surface, label, x + width + 10, y + 4, 18, PALETTE["muted"], "sans")
    return x + width + 10 + gt._get_font("sans", 18).get_rect(label).width + 28
