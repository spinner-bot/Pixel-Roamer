from __future__ import annotations
import pygame
from decimal import Decimal
from resource_catalog import player_defaults
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from maps import get_map, list_maps, load_map_config, save_map_config, get_map_summary, rename_map
from costumes import COSTUMES
import game_text as gt
from pixel_roamer.ui.config import FONT20, FONT24, FONT28, FONT34, FONT56, GAME_DEV, GAME_NAME_CN, GAME_NAME_EN, PAGE_HOME, PAGE_WORLD, _EDITABLE_FIELDS
from pixel_roamer.ui.widgets import draw_text_center, draw_text_left, draw_text_right
from pixel_roamer.ui.editor_input import EditorTextInput

class MapBrowser:
    """Map Browser behavior; shared session and viewport come from app."""

    def __init__(self, app):
        self.app = app
        self.text_input = EditorTextInput(self)

    def _get_edit_config(self, map_id: int) -> dict:
        """获取地图的当前配置（合并 World 实例默认值与已保存配置）。"""
        saved = load_map_config(map_id)
        config = {"world": {}, "player": {}}

        # 从 World 实例读取所有可编辑属性的当前值作为默认
        try:
            m = get_map(map_id)
            config["world"]["gravity"] = m.gravity
            config["world"]["mode"] = m.mode
            config["world"]["loop_x"] = m.loop_x
            config["world"]["loop_y"] = m.loop_y
            config["world"]["edge_behavior"] = m.edge_behavior
            config["world"]["view_blocks_h"] = m.view_blocks_h
            config["world"]["void_limit"] = m.void_limit
            config["world"]["default_block_id"] = m.default_tile.type_id
            config["world"]["fill_color"] = ",".join(str(c) for c in m.fill_color)
            config["world"]["lives"] = getattr(m, 'lives', 0)
            config["world"]["score_goal"] = getattr(m, 'score_goal', 100)
            config["world"]["time_limit"] = getattr(m, 'time_limit', 0.0)
            config["world"]["music"] = getattr(m, 'music', "")
        except Exception:
            config["world"]["gravity"] = -6.5
            config["world"]["mode"] = "adventure"
            config["world"]["loop_x"] = False
            config["world"]["loop_y"] = False
            config["world"]["edge_behavior"] = "solid"
            config["world"]["view_blocks_h"] = 15.0
            config["world"]["void_limit"] = 20
            config["world"]["default_block_id"] = 0

        # Player 默认值
        defaults = player_defaults()
        saved_player = saved.get("player", {})
        for key, default_val in defaults.items():
            config["player"][key] = saved_player.get(key, default_val)

        # 已保存的 world 配置覆盖
        saved_world = saved.get("world", {})
        config["world"].update(saved_world)
        color = config["world"].get("fill_color", (30, 30, 30))
        if isinstance(color, (list, tuple)):
            color = ",".join(str(component) for component in color)
        config["world"]["fill_color"] = color
        return config

    def _get_field_value(self, config: dict, field_path: str):
        """从配置字典中读取字段值。field_path 如 'player.hp_max'"""
        parts = field_path.split(".")
        val = config
        for p in parts:
            if not isinstance(val, dict):
                return None
            val = val.get(p)
            if val is None:
                return None
        return val

    def _set_field_value(self, config: dict, field_path: str, value):
        """设置配置字典中的字段值。"""
        parts = field_path.split(".")
        obj = config
        for p in parts[:-1]:
            if p not in obj:
                obj[p] = {}
            obj = obj[p]
        obj[parts[-1]] = value

    def _get_map_type_label(self, loop_x: bool, loop_y: bool) -> str:
        """获取地图类型标签。"""
        if loop_x and loop_y:
            return "循环XY"
        elif loop_x:
            return "循环X"
        elif loop_y:
            return "循环Y"
        else:
            return "有限"

    def run_dev_page(self, dt: float):
        """开发者界面：查询地图、选择地图、编辑属性、启动游戏、预览器。"""

        # 方块/ Buff 预览器模式
        if self.app._dev_block_browser:
            self.app.logic_surface.fill((20, 20, 40))
            self.app.references._run_block_browser(self.app.logic_surface, dt)
            return
        if self.app._dev_buff_browser:
            self.app.logic_surface.fill((20, 20, 40))
            self.app.references._run_buff_browser(self.app.logic_surface, dt)
            return

        self.app.logic_surface.fill((20, 20, 40))

        if not self.app._dev_edit_mode:
            self.app.map_selector.draw(dt)
            if self.app._dev_error:
                pygame.draw.rect(self.app.logic_surface, (20, 20, 40),
                                 (0, LOGIC_HEIGHT - 38, LOGIC_WIDTH, 38))
                draw_text_center(self.app.logic_surface, FONT20,
                                 gt.elide(self.app._dev_error, LOGIC_WIDTH - 80, FONT20),
                                 LOGIC_HEIGHT - 28, (255, 130, 110))
            return

        maps_dict = list_maps()
        map_ids = sorted(maps_dict.keys())

        # 标题
        y = 30
        y = draw_text_center(self.app.logic_surface, FONT56, f"{GAME_NAME_CN}", y, (255, 220, 100)) + 4
        y = draw_text_center(self.app.logic_surface, FONT28, f"{GAME_NAME_EN}", y, (200, 180, 100)) + 8
        y = draw_text_center(self.app.logic_surface, FONT20, f"开发者：{GAME_DEV}", y, (140, 140, 160)) + 16

        if self.app._dev_edit_mode and self.app._dev_selected_id is not None:
            # ========== 编辑模式 ==========
            y = draw_text_center(self.app.logic_surface, FONT34, f"编辑地图属性 — ID={self.app._dev_selected_id}", y, (100, 255, 150)) + 4

            # ---- 重命名行 ----
            map_name = maps_dict.get(self.app._dev_selected_id, "?")
            if self.app._dev_renaming:
                rename_hint = '新名称: ' + self.text_input.display() + '  (Enter确认 Esc取消)'
                rename_hint = gt.elide(rename_hint, LOGIC_WIDTH - 120, FONT24)
                self.text_input.set_rect((200, y, 1200, 36))
                y = draw_text_center(self.app.logic_surface, FONT24, rename_hint, y, (255, 220, 100)) + 4
            else:
                rename_line = f"地图名: {map_name}  [按 R 重命名]"
                y = draw_text_center(self.app.logic_surface, FONT24, rename_line, y, (200, 200, 220)) + 4

            if self.app._dev_inputting and not self.app._dev_renaming:
                hint = "直接输入替换原值  Ctrl+A 全选  Enter 确认  Esc 取消"
            elif not self.app._dev_renaming:
                hint = "↑↓ 选择  ← → 快速调整  Enter 精确输入  S 保存  R 改名  Esc 返回"
            else:
                hint = ""
            if hint:
                y = draw_text_center(self.app.logic_surface, FONT20, hint, y, (180, 180, 180)) + 12

            # 可见行数
            visible_start = max(0, self.app._dev_edit_field_idx - 8)
            visible_end = min(len(_EDITABLE_FIELDS), visible_start + 18)
            # 确保当前选中在可见范围内
            if self.app._dev_edit_field_idx < visible_start:
                visible_start = self.app._dev_edit_field_idx
                visible_end = min(len(_EDITABLE_FIELDS), visible_start + 18)
            elif self.app._dev_edit_field_idx >= visible_end:
                visible_end = min(len(_EDITABLE_FIELDS), self.app._dev_edit_field_idx + 1)
                visible_start = max(0, visible_end - 18)

            # 滚动指示
            if visible_start > 0:
                draw_text_center(self.app.logic_surface, FONT20, "▲ 更多 ↑", y - 6, (100, 100, 120))

            for i in range(visible_start, visible_end):
                field_path, label, ftype, default, step = _EDITABLE_FIELDS[i]
                val = self._get_field_value(self.app._dev_edit_config, field_path)
                is_sel = (i == self.app._dev_edit_field_idx)

                row_h = 36
                row_y = y
                # 行背景
                if is_sel:
                    highlight_color = (100, 200, 255) if not self.app._dev_inputting else (255, 200, 50)
                    pygame.draw.rect(self.app.logic_surface, (50, 50, 90), (200, row_y - 1, LOGIC_WIDTH - 400, row_h))
                    pygame.draw.rect(self.app.logic_surface, highlight_color, (200, row_y - 1, LOGIC_WIDTH - 400, row_h), 2)

                # 字段名和类型标签
                type_tag = {"float": "F", "int": "I", "bool": "B", "str": "S"}.get(ftype, "?")
                type_color = {"float": (150,200,255), "int": (255,200,150), "bool": (200,255,150), "str": (255,200,255)}.get(ftype, (150,150,150))
                label_text = f"{label}"
                draw_text_left(self.app.logic_surface, FONT24 if is_sel else FONT20,
                               label_text, 220, row_y + 6,
                               (255, 255, 180) if is_sel else (200, 200, 200))
                # 类型小标签
                gt.draw(self.app.logic_surface, type_tag, 540, row_y + 8, FONT20, type_color, "sans")

                # 值显示
                if is_sel and self.app._dev_inputting:
                    # 精确输入模式：显示光标
                    display_text = self.text_input.display()
                    self.text_input.set_rect((600, row_y, 780, 36))
                    val_color = (255, 255, 100)
                else:
                    if ftype == "bool":
                        display_text = "是" if val else "否"
                    elif ftype == "float":
                        display_text = str(val)
                    elif ftype == "int":
                        display_text = str(int(val))
                        # 时装字段：同时显示名称
                        if field_path == "player.costume_id":
                            cname = COSTUMES.get(int(val), {}).get("name", "")
                            if cname:
                                display_text = f"{int(val)} · {cname}"
                    else:
                        display_text = str(val)
                    val_color = (100, 255, 150) if is_sel else (150, 220, 150)

                text_size = FONT24 if is_sel else FONT20
                display_text = gt.elide(display_text[::-1], 760, text_size)[::-1]
                if is_sel and self.app._dev_inputting and self.text_input.selected:
                    pygame.draw.rect(self.app.logic_surface, (40, 75, 80), (600, row_y + 2, 780, row_h - 4))
                draw_text_right(self.app.logic_surface, text_size,
                                display_text, LOGIC_WIDTH - 220, row_y + 6, val_color)
                y += row_h + 2

            if visible_end < len(_EDITABLE_FIELDS):
                draw_text_center(self.app.logic_surface, FONT20, "▼ 更多 ↓", y + 4, (100, 100, 120))

            y = LOGIC_HEIGHT - 70
            status_color = (100, 255, 100) if self.app._dev_edit_dirty else (150, 150, 150)
            draw_text_center(self.app.logic_surface, FONT20,
                             "已修改，按 S 保存" if self.app._dev_edit_dirty else "无修改",
                             y, status_color)
        if self.app._dev_selected_id is not None:
            draw_text_center(self.app.logic_surface, FONT20,
                             self.app._dev_error or "S: 保存到硬盘 | Enter: 精确输入 | Esc: 返回列表",
                             LOGIC_HEIGHT - 24, (255, 100, 80) if self.app._dev_error else (140, 180, 255))

    def _parse_input_value(self, text: str, ftype: str):
        """解析输入文本为对应类型的值，失败返回 None。"""
        try:
            if ftype == "float":
                return float(text)
            elif ftype == "int":
                return int(text)
            elif ftype == "bool":
                t = text.strip().lower()
                if t in ("true", "1", "是", "yes", "y"):
                    return True
                elif t in ("false", "0", "否", "no", "n"):
                    return False
                return None
            elif ftype == "str":
                return text.strip()
        except (ValueError, TypeError):
            return None
        return None

    def handle_dev_input(self, event):
        """处理 dev 页面的键盘事件。"""

        if (not self.app._dev_edit_mode and not self.app._dev_block_browser
                and not self.app._dev_buff_browser and self.app.map_selector.handle_input(event)):
            return

        if self.app._dev_block_browser:
            self.app.references._handle_block_browser_input(event)
            return
        if self.app._dev_buff_browser:
            self.app.references._handle_buff_browser_input(event)
            return
        if self.text_input.handle(event):
            return
        if event.type != pygame.KEYDOWN:
            return

        maps_dict = list_maps()
        ids = sorted(maps_dict.keys())
        if not ids:
            return

        # ========== B键方块预览器 / U键Buff预览器 ==========
        if event.key == pygame.K_b and not self.app._dev_edit_mode and not self.app._dev_inputting:
            self.app._dev_block_browser = True
            return
        if event.key == pygame.K_u and not self.app._dev_edit_mode and not self.app._dev_inputting:
            self.app._dev_buff_browser = True
            return

        # ========== 编辑模式按键 ==========
        if self.app._dev_edit_mode and self.app._dev_selected_id is not None:
            field_path, label, ftype, default, step = _EDITABLE_FIELDS[self.app._dev_edit_field_idx]

            # ---- 常规编辑模式按键 ----
            if event.key == pygame.K_ESCAPE:
                self.app._dev_edit_mode = False
                self.app._dev_edit_dirty = False
            elif event.key == pygame.K_r:
                self.text_input.begin(rename=True)
            elif event.key == pygame.K_UP:
                self.app._dev_edit_field_idx = (self.app._dev_edit_field_idx - 1) % len(_EDITABLE_FIELDS)
            elif event.key == pygame.K_DOWN:
                self.app._dev_edit_field_idx = (self.app._dev_edit_field_idx + 1) % len(_EDITABLE_FIELDS)
            elif event.key == pygame.K_RETURN:
                self.text_input.begin()
            elif event.key == pygame.K_LEFT:
                try:
                    if ftype == "bool":
                        self._set_field_value(self.app._dev_edit_config, field_path, False)
                    elif ftype == "str":
                        cur = self._get_field_value(self.app._dev_edit_config, field_path)
                        if isinstance(step, list) and step:
                            try:
                                idx = step.index(cur)
                            except ValueError:
                                idx = 0
                            idx = (idx - 1) % len(step)
                            self._set_field_value(self.app._dev_edit_config, field_path, step[idx])
                        # str 无有效选项列表时不操作
                    elif ftype == "float":
                        val = self._get_field_value(self.app._dev_edit_config, field_path)
                        if val is not None and isinstance(step, (int, float)):
                            val = float(Decimal(str(val)) - Decimal(str(step)))
                            self._set_field_value(self.app._dev_edit_config, field_path, val)
                    elif ftype == "int":
                        val = self._get_field_value(self.app._dev_edit_config, field_path)
                        if val is not None and isinstance(step, (int, float)):
                            val = int(val) - int(step)
                            self._set_field_value(self.app._dev_edit_config, field_path, val)
                    self.app._dev_edit_dirty = True
                except Exception:
                    pass
            elif event.key == pygame.K_RIGHT:
                try:
                    if ftype == "bool":
                        self._set_field_value(self.app._dev_edit_config, field_path, True)
                    elif ftype == "str":
                        cur = self._get_field_value(self.app._dev_edit_config, field_path)
                        if isinstance(step, list) and step:
                            try:
                                idx = step.index(cur)
                            except ValueError:
                                idx = -1
                            idx = (idx + 1) % len(step)
                            self._set_field_value(self.app._dev_edit_config, field_path, step[idx])
                        # str 无有效选项列表时不操作
                    elif ftype == "float":
                        val = self._get_field_value(self.app._dev_edit_config, field_path)
                        if val is not None and isinstance(step, (int, float)):
                            val = float(Decimal(str(val)) + Decimal(str(step)))
                            self._set_field_value(self.app._dev_edit_config, field_path, val)
                    elif ftype == "int":
                        val = self._get_field_value(self.app._dev_edit_config, field_path)
                        if val is not None and isinstance(step, (int, float)):
                            val = int(val) + int(step)
                            self._set_field_value(self.app._dev_edit_config, field_path, val)
                    self.app._dev_edit_dirty = True
                except Exception:
                    pass
            elif event.key == pygame.K_s:
                # 保存到硬盘
                try:
                    save_map_config(self.app._dev_selected_id, self.app._dev_edit_config)
                except (ValueError, OSError) as error:
                    self.app._dev_error = str(error)
                else:
                    self.app._dev_edit_dirty = False
                    self.app._dev_error = ""
            return

        # ========== 列表模式按键 ==========
        if event.key == pygame.K_RETURN:
            if self.app._dev_selected_id is not None:
                self.app.set_page(PAGE_WORLD, map_id=self.app._dev_selected_id)
        elif event.key == pygame.K_e:
            if self.app._dev_selected_id is not None:
                self.app._dev_edit_mode = True
                self.app._dev_edit_field_idx = 0
                self.app._dev_edit_dirty = False
                self.app._dev_edit_config = self._get_edit_config(self.app._dev_selected_id)
        elif event.key == pygame.K_UP:
            idx = ids.index(self.app._dev_selected_id) if self.app._dev_selected_id in ids else 0
            idx = (idx - 1) % len(ids)
            self.app._dev_selected_id = ids[idx]
        elif event.key == pygame.K_DOWN:
            idx = ids.index(self.app._dev_selected_id) if self.app._dev_selected_id in ids else 0
            idx = (idx + 1) % len(ids)
            self.app._dev_selected_id = ids[idx]
        elif event.key == pygame.K_r:
            self.app._init_dev_selection()
        elif event.key == pygame.K_ESCAPE:
            # 返回主页
            self.app.set_page(PAGE_HOME)
