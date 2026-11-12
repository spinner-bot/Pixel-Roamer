"""Map selection uses static summaries and offline previews, never generation."""
from collections import OrderedDict
import json
from pathlib import Path
import pygame
import game_text as gt
from maps import list_maps, get_map_summary
from pixel_roamer.ui.config import PAGE_WORLD
from pixel_roamer.ui.theme import PALETTE as P, panel, key_hint

ROOT = Path(__file__).resolve().parents[2]
MODE_LABELS = {"free": "自由漫游", "adventure": "冒险探索", "explore": "寻找终点",
               "score_target": "积分挑战", "score_timed": "限时收集"}


class MapSelector:
    ROW_HEIGHT = 48
    VISIBLE_ROWS = 11

    def __init__(self, app):
        self.app = app
        self.previews = OrderedDict()
        self.descriptions = json.loads((ROOT / "data/map_descriptions.json").read_text())["maps"]

    def _rows(self):
        ids = sorted(list_maps())
        index = ids.index(self.app._dev_selected_id) if self.app._dev_selected_id in ids else 0
        first = max(0, min(index - self.VISIBLE_ROWS // 2, len(ids) - self.VISIBLE_ROWS))
        return ids, [(map_id, pygame.Rect(76, 190 + row * self.ROW_HEIGHT, 512, 44))
                     for row, map_id in enumerate(ids[first:first + self.VISIBLE_ROWS])]

    @staticmethod
    def buttons():
        return [("E", "编辑属性", pygame.Rect(64, 786, 166, 42)),
                ("B", "方块图鉴", pygame.Rect(242, 786, 166, 42)),
                ("U", "状态图鉴", pygame.Rect(420, 786, 166, 42)),
                ("Enter", "开始漫游", pygame.Rect(1284, 786, 252, 48))]

    def _preview(self, map_id):
        if map_id not in self.previews:
            path = ROOT / "assets/maps" / f"{map_id}.png"
            try:
                image = pygame.image.load(str(path))
            except (FileNotFoundError, pygame.error):
                image = pygame.Surface((640, 360))
                image.fill(P["background"])
                gt.draw(image, "暂无预览", 320, 162, 24, P["muted"], "sans", center_x=True)
            self.previews[map_id] = pygame.transform.scale(image, (640, 360))
            while len(self.previews) > 8:
                self.previews.popitem(last=False)
        self.previews.move_to_end(map_id)
        return self.previews[map_id]

    def draw(self, dt):
        surface = self.app.logic_surface
        surface.fill(P["background"])
        gt.draw(surface, "选择地图", 64, 56, 48, P["text"], "sans")
        gt.draw(surface, "选择一处风景，开始你的漫游。", 66, 124, 21, P["muted"], "sans")
        panel(surface, (64, 176, 536, 594))
        panel(surface, (632, 176, 904, 594))
        ids, rows = self._rows()
        if not ids:
            gt.draw(surface, "尚无可用地图", 90, 210, 24, P["muted"], "sans")
            return
        for map_id, rect in rows:
            summary = get_map_summary(map_id)
            selected = map_id == self.app._dev_selected_id
            if selected:
                panel(surface, rect, True)
            gt.draw(surface, f"{map_id:02d}", rect.x + 14, rect.y + 11, 21, P["accent"] if selected else P["muted"])
            gt.draw(surface, gt.elide(summary["name"], 300, 24), rect.x + 76, rect.y + 9, 24, P["text"], "sans")
            gt.draw(surface, MODE_LABELS.get(summary["mode"], summary["mode"]), rect.right - 14,
                    rect.y + 14, 15, P["mint"] if selected else P["muted"], "sans", right_x=True)
        selected_id = self.app._dev_selected_id if self.app._dev_selected_id in ids else ids[0]
        summary = get_map_summary(selected_id)
        gt.draw(surface, gt.elide(summary["name"], 840, 36), 660, 194, 36, P["text"], "sans")
        loops = "双向循环" if summary["loop_x"] and summary["loop_y"] else (
            "横向循环" if summary["loop_x"] else "纵向循环" if summary["loop_y"] else "有限世界")
        gt.draw(surface, f"{MODE_LABELS.get(summary['mode'], summary['mode'])}   /   {loops}",
                662, 246, 18, P["mint"], "sans")
        preview = self._preview(selected_id)
        surface.blit(preview, (764, 292))
        pygame.draw.rect(surface, P["border"], (762, 290, 644, 364), 2)
        description = self.descriptions.get(str(selected_id), "探索这张地图里的地形与通路。")
        gt.draw(surface, description, 660, 682, 21, P["text"], "sans")
        gt.draw(surface, f"尺寸 {summary['width']} × {summary['height']}  /  ID {selected_id}",
                660, 724, 18, P["muted"], "sans")
        gt.draw(surface, f"{len(ids)} 张地图   ·   ↑↓ 选择 / 滚轮翻阅", 84, 738, 15, P["muted"], "sans")
        for key, label, rect in self.buttons():
            panel(surface, rect, key == "Enter")
            gt.draw(surface, f"{label}  {key}", rect.centerx, rect.y + 9, 21,
                    P["accent"] if key == "Enter" else P["text"], "sans", center_x=True)
        x = key_hint(surface, "↑ ↓", "选择", 64, 850)
        x = key_hint(surface, "Enter", "开始", x, 850)
        key_hint(surface, "Esc", "主页", x, 850)

    def handle_input(self, event):
        ids, rows = self._rows()
        if not ids:
            return False
        index = ids.index(self.app._dev_selected_id) if self.app._dev_selected_id in ids else 0
        if event.type == pygame.MOUSEWHEEL:
            self.app._dev_selected_id = ids[max(0, min(len(ids) - 1, index - event.y))]
            return True
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            pos = event.pos if hasattr(event, "pos") else pygame.mouse.get_pos()
            point = ((pos[0] - self.app.draw_offset_x) / self.app.scale,
                     (pos[1] - self.app.draw_offset_y) / self.app.scale)
            for map_id, rect in rows:
                if rect.collidepoint(point):
                    self.app._dev_selected_id = map_id
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and getattr(event, "clicks", 1) >= 2:
                        self.app.set_page(PAGE_WORLD, map_id=map_id)
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, _, rect in self.buttons():
                    if rect.collidepoint(point):
                        code = pygame.K_RETURN if key == "Enter" else pygame.key.key_code(key.lower())
                        self.app.map_browser.handle_dev_input(pygame.event.Event(pygame.KEYDOWN, key=code, unicode=""))
                        return True
        if event.type == pygame.KEYDOWN:
            delta = {pygame.K_UP: -1, pygame.K_DOWN: 1, pygame.K_PAGEUP: -self.VISIBLE_ROWS,
                     pygame.K_PAGEDOWN: self.VISIBLE_ROWS}.get(event.key)
            if delta is not None:
                self.app._dev_selected_id = ids[max(0, min(len(ids) - 1, index + delta))]
                return True
            if event.key in (pygame.K_HOME, pygame.K_END):
                self.app._dev_selected_id = ids[0 if event.key == pygame.K_HOME else -1]
                return True
            if event.key == pygame.K_r:
                self.previews.clear()
        return False
