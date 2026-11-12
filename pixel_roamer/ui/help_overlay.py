"""Readable controls with a paused world while the overlay is open."""
import json
from pathlib import Path
import pygame
import game_text as gt
from pixel_roamer.ui.theme import PALETTE as P, panel, key_hint


class HelpOverlay:
    def __init__(self):
        path = Path(__file__).resolve().parents[2] / "data/controls.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("unsupported control help version")
        self.controls = data["controls"]

    def draw(self, surface):
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((3, 8, 15, 205))
        surface.blit(shade, (0, 0))
        panel(surface, (348, 144, 904, 620), True)
        gt.draw(surface, "操作指南", 396, 180, 36, P["text"], "sans")
        gt.draw(surface, "世界已暂停，可以慢慢查看。", 398, 238, 21, P["muted"], "sans")
        for index, row in enumerate(self.controls):
            y = 294 + index * 43
            gt.draw(surface, row["keys"], 398, y, 21, P["accent"])
            gt.draw(surface, row["action"], 624, y, 21, P["text"], "sans")
        key_hint(surface, "H / Esc", "关闭指南并继续", 398, 704)
