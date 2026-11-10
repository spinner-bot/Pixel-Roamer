from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
import game_text as gt

class ReferenceBrowser:
    """References behavior; shared session and viewport come from app."""

    def __init__(self, app):
        self.app = app

    def _get_block_highlights(self, bt) -> list:
        """根据方块属性自动生成亮点描述列表。算法选择，不依赖预存数据。"""
        h = []
        if bt.climbable:
            h.append("可攀爬")
        if getattr(bt, 'swim_f', 0.0) > 0:
            h.append(f"浮力 {bt.swim_f:.1f}")
        if bt.damage_ps > 0:
            h.append(f"伤害 {bt.damage_ps:.0f}/s")
        if abs(bt.surface_f - 1.0) > 0.001:
            h.append(f"表面摩擦 x{bt.surface_f:.3f}")
        if abs(bt.space_f - 1.0) > 0.001:
            h.append(f"空间阻力 x{bt.space_f:.3f}")
        if bt.bounce != (0.0, 0.0) and (abs(bt.bounce[0]) > 0.01 or abs(bt.bounce[1]) > 0.01):
            h.append(f"弹跳 ({bt.bounce[0]:.0f},{bt.bounce[1]:.0f})")
        if bt.accel_k != (0.0, 0.0):
            h.append(f"加速系数 ({bt.accel_k[0]:.1f},{bt.accel_k[1]:.1f})")
        if bt.accel_b != (0.0, 0.0):
            h.append(f"基础加速 ({bt.accel_b[0]:.1f},{bt.accel_b[1]:.1f})")
        if bt.special is not None:
            special_names = {
                "teleport": "传送", "checkpoint": "检查点", "heal": "治疗",
                "shield": "护盾", "speed": "加速", "jump": "跳跃增强",
                "score": "积分", "end_point": "终点", "explosive": "爆炸",
                "ender": "随机传送",
            }
            sn = special_names.get(bt.special, bt.special)
            h.append(f"特效: {sn}")
        if bt.light_level > 0:
            h.append(f"光照 {bt.light_level}")
        if bt.break_level < 15:
            h.append(f"破坏等级 {bt.break_level}")
        if abs(bt.k_stamina - 1.0) > 0.001:
            h.append(f"体力消耗 x{bt.k_stamina:.1f}")
        if bt.break_special is not None:
            h.append(f"破坏特效: {bt.break_special}")
        if bt.drops_item_id is not None:
            h.append(f"掉落: {bt.drops_item_id}")
        if bt.one_way:
            h.append("单向平台")
        if not bt.is_solid:
            if bt.climbable:
                pass  # 已显示可攀爬
            elif getattr(bt, 'swim_f', 0.0) <= 0:
                h.append("非实体")
        # Buff 信息（方块的 gameplay 核心扩展）
        buff_ids = getattr(bt, 'buff_ids', ())
        if buff_ids:
            import buff_data
            from buff_system import BUFF_TYPES
            buff_names = []
            for bid in buff_ids[:3]:
                btype = BUFF_TYPES.get(bid)
                if btype:
                    buff_names.append(btype.name2 or btype.name)
                else:
                    buff_names.append(f"B{bid}")
            suffix = "…" if len(buff_ids) > 3 else ""
            h.append(f"增益: {','.join(buff_names)}{suffix}")
        return h

    def _draw_block_preview(self, surf, bt, x, y, size):
        """绘制单个方块的预览缩略图。"""
        from pattern import render_block_pattern
        preview = pygame.Surface((size, size))
        preview.fill(bt.color)
        if bt.pattern is not None:
            render_block_pattern(preview, bt, 0, 0, size, size)
        surf.blit(preview, (x, y))
        # 边框
        pygame.draw.rect(surf, (100, 100, 120), (x, y, size, size), 1)

    def _run_block_browser(self, logic_surface, dt):
        """方块浏览器渲染（网格/列表模式）。"""
        from block_types_data import BLOCK_TYPES
        all_ids = sorted(BLOCK_TYPES.keys())
        if not all_ids:
            return

        # 详情页
        if self.app._dev_block_detail_id is not None:
            self._run_block_detail(logic_surface, dt)
            return

        # 标题 (5%-15% 区域)
        TITLE_Y = int(LOGIC_HEIGHT * 0.06) - 18  # 标题中心在6%
        HINT_Y = int(LOGIC_HEIGHT * 0.975)
        title = f"方块预览器 [{self.app._dev_block_browser_mode.upper()}]"
        gt.draw(logic_surface, title, LOGIC_WIDTH // 2, TITLE_Y, 36,
                            (255, 255, 200), "sans", shadow=True, center_x=True)
        mode_hint = "Tab:切换视图  N:名称切换  Enter:详情  B/Esc:返回"
        gt.draw(logic_surface, mode_hint, LOGIC_WIDTH // 2, HINT_Y, 18,
                            (140, 160, 200), "sans", shadow=True, center_x=True)

        name_key = "name2" if self.app._dev_block_browser_show_name2 else "name"
        cursor = self.app._dev_block_browser_cursor
        CONTENT_TOP2 = int(LOGIC_HEIGHT * 0.12)
        CONTENT_H = int(LOGIC_HEIGHT * 0.85)  # 12%-97%

        if self.app._dev_block_browser_mode == "grid":
            COLS = 8
            cell_w = 170
            cell_h = CONTENT_H // 4  # 每页4排
            preview_size = 80
            start_x = (LOGIC_WIDTH - COLS * cell_w) // 2
            start_y = CONTENT_TOP2
            rows = (len(all_ids) + COLS - 1) // COLS

            visible_rows = 4
            cursor_row = cursor // COLS
            if cursor_row < self.app._dev_block_browser_scroll:
                self.app._dev_block_browser_scroll = cursor_row
            if cursor_row >= self.app._dev_block_browser_scroll + visible_rows:
                self.app._dev_block_browser_scroll = max(0, cursor_row - visible_rows + 1)
            self.app._dev_block_browser_scroll = max(0, min(self.app._dev_block_browser_scroll, max(0, rows - visible_rows)))

            for row in range(self.app._dev_block_browser_scroll, min(self.app._dev_block_browser_scroll + visible_rows, rows)):
                for col in range(COLS):
                    idx = row * COLS + col
                    if idx >= len(all_ids):
                        break
                    bid = all_ids[idx]
                    bt = BLOCK_TYPES[bid]
                    cx = start_x + col * cell_w
                    cy = start_y + (row - self.app._dev_block_browser_scroll) * cell_h

                    if idx == cursor:
                        pygame.draw.rect(logic_surface, (80, 140, 255),
                                        (cx - 3, cy - 3, cell_w - 4, cell_h - 4), 2, border_radius=4)

                    # 预览图
                    px = cx + (cell_w - preview_size) // 2
                    self._draw_block_preview(logic_surface, bt, px, cy + 4, preview_size)

                    # 名称（在两行预览图间隙中间靠上位置）
                    label = f"{bid}.{getattr(bt, name_key, bt.name)}"
                    gt.draw(logic_surface, label, cx + cell_w // 2,
                                        cy + preview_size + 22, 20, (220, 220, 220),
                                        "sans", shadow=True, center_x=True)

        else:
            # 列表模式 — 2行布局
            row_h = CONTENT_H // 8  # 每页8行
            preview_size = 60
            start_y = CONTENT_TOP2
            visible_rows = 8

            if cursor < self.app._dev_block_browser_scroll:
                self.app._dev_block_browser_scroll = cursor
            if cursor >= self.app._dev_block_browser_scroll + visible_rows:
                self.app._dev_block_browser_scroll = max(0, cursor - visible_rows + 1)
            self.app._dev_block_browser_scroll = max(0, min(self.app._dev_block_browser_scroll, max(0, len(all_ids) - visible_rows)))

            for i in range(self.app._dev_block_browser_scroll,
                           min(self.app._dev_block_browser_scroll + visible_rows, len(all_ids))):
                idx = i
                bid = all_ids[idx]
                bt = BLOCK_TYPES[bid]
                cy = start_y + (i - self.app._dev_block_browser_scroll) * row_h

                if idx == cursor:
                    pygame.draw.rect(logic_surface, (60, 60, 100), (40, cy, LOGIC_WIDTH - 80, row_h))
                    pygame.draw.rect(logic_surface, (100, 200, 255), (40, cy, LOGIC_WIDTH - 80, row_h), 2)

                # 左侧预览
                self._draw_block_preview(logic_surface, bt, 56, cy + (row_h - preview_size) // 2, preview_size)

                # 第1行：【ID】英文名 | 中文名  （大字，粗体感）
                line1 = f"[{bid}] {bt.name}  |  {bt.name2}"
                gt.draw(logic_surface, line1, 56 + preview_size + 16, cy + 10, 20,
                                    (255, 255, 210), "sans", shadow=True)

                # 第2行：标签 · 亮点（合并为一行），逐个绘制以支持分类着色
                line2_x = 56 + preview_size + 16
                line2_y = cy + 42
                FS2 = 17
                SEP = "  |  "
                DEFAULT_C2 = (170, 190, 220)

                # 构建带类型标记的条目列表: (text, type)
                # type: "tag" | "hl" | "buff_pos" | "buff_neu" | "buff_neg"
                items = []
                if bt.is_solid: items.append(("实体", "tag"))
                if bt.climbable: items.append(("攀爬", "tag"))
                if getattr(bt, 'swim_f', 0.0) > 0: items.append(("游泳", "tag"))
                if bt.damage_ps > 0: items.append((f"伤{bt.damage_ps:.0f}", "tag"))
                if bt.one_way: items.append(("单向", "tag"))

                # Buff 条目 — 每个 buff 单独着色
                buff_ids = getattr(bt, 'buff_ids', ())
                if buff_ids:
                    from buff_system import BUFF_TYPES
                    cat_colors_buff = {"positive": (100, 255, 100), "neutral": (100, 200, 255), "negative": (255, 100, 100)}
                    for bid in buff_ids:
                        btype = BUFF_TYPES.get(bid)
                        bname = f"{btype.name} {btype.name2}" if btype else f"Buff#{bid}"
                        cat = btype.category if btype else "neutral"
                        items.append((bname, f"buff_{cat}"))

                # 非buff亮点
                highlights = self._get_block_highlights(bt)
                non_buff_hl = [hl for hl in highlights if not hl.startswith("增益:")]
                for hl in non_buff_hl[:4]:
                    items.append((hl, "hl"))

                if not items:
                    gt.draw(logic_surface, "—", line2_x, line2_y, FS2, DEFAULT_C2, "sans", shadow=True)
                else:
                    cur_x = line2_x
                    for idx, (text, kind) in enumerate(items):
                        if idx > 0:
                            sep_w, _ = gt.draw(logic_surface, SEP, cur_x, line2_y, FS2, (100, 110, 140), "sans")
                            cur_x += sep_w
                        if kind == "tag":
                            c = DEFAULT_C2
                        elif kind == "hl":
                            c = (190, 200, 230)
                        elif kind == "buff_positive":
                            c = (100, 255, 100)
                        elif kind == "buff_neutral":
                            c = (100, 200, 255)
                        elif kind == "buff_negative":
                            c = (255, 100, 100)
                        else:
                            c = DEFAULT_C2
                        tw, _ = gt.draw(logic_surface, text, cur_x, line2_y, FS2, c, "sans", shadow=True)
                        cur_x += tw

    def _run_block_detail(self, logic_surface, dt):
        """方块详情页：上中下3区 — 标题 | 左中右3栏 | 操作指引。5%边距。"""
        from block_types_data import BLOCK_TYPES
        bid = self.app._dev_block_detail_id
        if bid is None: return
        bt = BLOCK_TYPES.get(bid)
        if bt is None:
            gt.draw(logic_surface, f"方块 {bid} 不存在", LOGIC_WIDTH // 2, 100, 24, (255,100,100), "sans", center_x=True)
            return

        M = 0.05
        ML = int(LOGIC_WIDTH * M)
        MR = int(LOGIC_WIDTH * (1-M))
        MT = int(LOGIC_HEIGHT * M)
        CONTENT_TOP = int(LOGIC_HEIGHT * 0.12)
        CONTENT_BOT = int(LOGIC_HEIGHT * 0.97)
        HINT_TOP = int(LOGIC_HEIGHT * 0.975)

        # ==== 标题 (5%-15%) ====
        title = f"[{bt.id}] {bt.name}  |  {bt.name2}"
        gt.draw(logic_surface, title, LOGIC_WIDTH // 2, MT + 20, 36,
                            (255, 255, 200), "sans", shadow=True, center_x=True)

        # ==== 中区：左中右3栏 (20%-88%) ====
        cw = (MR - ML) // 3
        col1_x = ML
        col2_x = ML + cw
        col3_x = ML + cw * 2

        for sep_x in [col2_x - 2, col3_x - 2]:
            pygame.draw.line(logic_surface, (80, 80, 120), (sep_x, CONTENT_TOP), (sep_x, CONTENT_BOT), 1)

        # -- 左栏：预览 + 基本信息 --
        preview_size = min(cw - 20, 280)
        self._draw_block_preview(logic_surface, bt, col1_x + (cw - preview_size) // 2, CONTENT_TOP + 10, preview_size)

        ly = CONTENT_TOP + preview_size + 20
        lh = 32
        FS = 22
        linfos = [
            f"ID: {bt.id}",
            f"实体: {bt.is_solid}",
            f"单向: {bt.one_way}",
            f"可攀爬: {bt.climbable}",
            f"浮力: {bt.swim_f:.2f}" if hasattr(bt, 'swim_f') else "浮力: -",
            f"颜色: {bt.color}",
        ]
        for i, inf in enumerate(linfos):
            if ly + i * lh > CONTENT_BOT - 10: break
            gt.draw(logic_surface, inf, col1_x + 6, ly + i * lh, FS, (210, 220, 250), "sans", shadow=True)

        # -- 中栏：物理/战斗属性 + Buff --
        my = CONTENT_TOP + 10
        mh = 28
        MFS = 20  # 中栏字体略小以容纳更多字段
        mid_attrs = [
            f"表面摩擦: {bt.surface_f:.3f}",
            f"空间阻力: {bt.space_f:.3f}",
            f"弹跳: {bt.bounce}",
            f"加速k: {bt.accel_k}",
            f"加速b: {bt.accel_b}",
            f"伤害/s: {bt.damage_ps}",
            f"体力倍率: {bt.k_stamina:.2f}",
            f"光照: {bt.light_level}",
            f"特殊: {bt.special}",
            f"特数: {str(bt.special_data)[:40]}",
            f"破坏等级: {bt.break_level}  血量: {bt.break_hp:.0f}",
            f"破坏特效: {bt.break_special}",
            f"掉落物: {bt.drops_item_id}",
        ]
        for i, attr in enumerate(mid_attrs):
            if my + i * mh > CONTENT_BOT - 10: break
            gt.draw(logic_surface, attr, col2_x + 6, my + i * mh, MFS, (210, 220, 250), "sans", shadow=True)

        # -- Buff 数据区（中栏下方，背景色与其他文字一致，buff名按类别着色） --
        buff_ids = getattr(bt, 'buff_ids', ())
        if buff_ids:
            by = my + len(mid_attrs) * mh + 6
            # 分隔线与标题使用与其他区域文字一致的颜色
            DIV_C = (180, 190, 210)
            pygame.draw.line(logic_surface, DIV_C, (col2_x, by), (col2_x + cw - 12, by), 1)
            by += 6
            gt.draw(logic_surface, "── Buff 绑定 ──", col2_x + cw // 2, by, 18,
                                DIV_C, "sans", shadow=True, center_x=True)
            by += 22
            from buff_system import BUFF_TYPES
            buff_params = getattr(bt, 'buff_params_list', ())
            buff_durs = getattr(bt, 'buff_durations', ())
            cat_colors = {"positive": (100, 255, 100), "neutral": (100, 200, 255), "negative": (255, 100, 100)}
            for j, bid in enumerate(buff_ids):
                if by > CONTENT_BOT - 16: break
                btype = BUFF_TYPES.get(bid)
                bname = f"{btype.name} {btype.name2}" if btype else f"Buff#{bid}"
                cat = btype.category if btype else "neutral"
                bc = cat_colors.get(cat, DIV_C)
                param = buff_params[j] if j < len(buff_params) else ()
                dur = buff_durs[j] if j < len(buff_durs) else None
                dur_str = f"{dur:.1f}s" if dur is not None else "永久"
                buf_line = f"#{bid} {bname}"
                gt.draw(logic_surface, buf_line, col2_x + 6, by, 17, bc, "sans", shadow=True)
                by += 20
                if param:
                    gt.draw(logic_surface, f"  参数: {param}  持续: {dur_str}", col2_x + 6, by, 15, DIV_C, "sans")
                    by += 18

        # -- 右栏：外观编码 --
        ry = CONTENT_TOP + 8
        sep_text = "======== 外观编码 ========"
        gt.draw(logic_surface, sep_text, col3_x + cw // 2, ry, 22,
                            (190, 200, 240), "sans", shadow=True, center_x=True)
        ry += 30

        if bt.pattern is not None:
            ptype = bt.pattern[0]
            if ptype == "bitmap":
                size = bt.pattern[1] if len(bt.pattern) > 1 else "?"
                pixels = bt.pattern[2] if len(bt.pattern) > 2 else []
                gt.draw(logic_surface, f"编码: 位图", col3_x + 6, ry, 19, (200, 210, 240), "sans")
                gt.draw(logic_surface, f"尺寸: {size}x{size}", col3_x + 6, ry + 26, 19, (180, 190, 220), "sans")
                # 字符宽度换行：按右栏宽度自动折行
                flat = "[" + ", ".join(str(row) for row in pixels[:16]) + (", ..." if len(pixels) > 16 else "") + "]"
                chars_per_line = (cw - 20) // 7  # 7px per char at 14px font
                bj = 0
                while bj < len(flat):
                    chunk = flat[bj:bj + chars_per_line]
                    if ry + 52 + (bj // chars_per_line) * 15 > CONTENT_BOT - 10: break
                    gt.draw(logic_surface, chunk, col3_x + 6, ry + 52 + (bj // chars_per_line) * 15, 13, (150, 170, 210), "sans")
                    bj += chars_per_line
            elif ptype == "texture":
                code = bt.pattern[1] if len(bt.pattern) > 1 else "?"
                params = bt.pattern[2] if len(bt.pattern) > 2 else {}
                preset_names = {"checkerboard": "棋盘格", "gradient_h": "水平渐变", "gradient_v": "垂直渐变",
                               "noise": "噪点", "brick": "砖墙", "wood": "木纹", "stone": "石纹"}
                gt.draw(logic_surface, f"编码: 预设图案", col3_x + 6, ry, 28, (200, 210, 240), "sans")
                gt.draw(logic_surface, f"代码: {code} ({preset_names.get(code, code)})",
                                    col3_x + 6, ry + 32, 27, (180, 190, 220), "sans")
                show_y = ry + 60
                if isinstance(params, dict):
                    for k, v in params.items():
                        if show_y > CONTENT_BOT - 16: break
                        gt.draw(logic_surface, f"{k}: {v}",
                                            col3_x + 6, show_y, 22, (150, 170, 200), "sans")
                        show_y += 28
                elif isinstance(params, (tuple, list)):
                    gt.draw(logic_surface, f"参数: {params}",
                                        col3_x + 6, show_y, 18, (150, 170, 200), "sans")
            elif ptype == "vector":
                vw, vh = bt.pattern[1]
                cmds = bt.pattern[2] if len(bt.pattern) > 2 else []
                n_cmds = len(cmds)
                gt.draw(logic_surface, f"编码: 矢量  画布: {vw}x{vh}  指令: {n_cmds}",
                                    col3_x + 6, ry, 19, (200, 210, 240), "sans")
                if n_cmds <= 35:
                    VFS = 16; VLH = 19
                    for j, cmd in enumerate(cmds):
                        cy2 = ry + 28 + j * VLH
                        if cy2 > CONTENT_BOT - 8: break
                        ctype = cmd[0]
                        if ctype == "fill":
                            c = cmd[1]
                            text = f"fill({c[0]},{c[1]},{c[2]})"
                        elif ctype == "rect":
                            c = cmd[5]
                            text = f"rect({cmd[1]},{cmd[2]},{cmd[3]},{cmd[4]},({c[0]},{c[1]},{c[2]}))"
                        elif ctype == "circle":
                            c = cmd[4]
                            text = f"circle({cmd[1]},{cmd[2]},{cmd[3]},({c[0]},{c[1]},{c[2]}))"
                        else:
                            text = str(cmd)
                        gt.draw(logic_surface, text, col3_x + 6, cy2, VFS, (150, 170, 210), "sans")
                else:
                    # 紧凑模式；条数>90触发绝对紧凑（10px/行距1px/去空格）
                    abs_compact = n_cmds > 105
                    avail_w = int(LOGIC_WIDTH * 0.965) - (col3_x + 6)
                    if abs_compact:
                        flat = "[" + ",".join(
                            f"fill({c[1][0]},{c[1][1]},{c[1][2]})" if c[0] == "fill"
                            else f"rect({c[1]},{c[2]},{c[3]},{c[4]},({c[5][0]},{c[5][1]},{c[5][2]}))" if c[0] == "rect"
                            else f"circle({c[1]},{c[2]},{c[3]},({c[4][0]},{c[4][1]},{c[4][2]}))" if c[0] == "circle"
                            else str(c).replace(" ", "")
                            for c in cmds
                        ) + "]"
                        CFS = 10; CLH = 11; cpch = max(1, avail_w // 5)
                    else:
                        flat = "[" + ", ".join(
                            f"fill({c[1][0]},{c[1][1]},{c[1][2]})" if c[0] == "fill"
                            else f"rect({c[1]},{c[2]},{c[3]},{c[4]},({c[5][0]},{c[5][1]},{c[5][2]}))" if c[0] == "rect"
                            else f"circle({c[1]},{c[2]},{c[3]},({c[4][0]},{c[4][1]},{c[4][2]}))" if c[0] == "circle"
                            else str(c)
                            for c in cmds
                        ) + "]"
                        CFS = 13; CLH = 15; cpch = max(1, avail_w // 7)
                    bj = 0
                    while bj < len(flat):
                        chunk = flat[bj:bj + cpch]
                        if ry + 28 + (bj // cpch) * CLH > CONTENT_BOT - 10: break
                        gt.draw(logic_surface, chunk, col3_x + 6, ry + 28 + (bj // cpch) * CLH, CFS, (150, 170, 210), "sans")
                        bj += cpch
        else:
            gt.draw(logic_surface, f"编码: 无  底色: {bt.color}",
                                col3_x + 6, ry, 19, (160, 180, 200), "sans")

        # ==== 下区：操作指引 (92%-95%) ====
        gt.draw(logic_surface, "B / Esc  返回列表", LOGIC_WIDTH // 2, HINT_TOP + 4, 18,
                            (140, 160, 200), "sans", shadow=True, center_x=True)

    def _handle_block_browser_input(self, event):
        """处理方块浏览器的键盘事件。"""
        from block_types_data import BLOCK_TYPES

        if event.type != pygame.KEYDOWN:
            return

        all_ids = sorted(BLOCK_TYPES.keys())
        if not all_ids:
            return

        # 详情页内
        if self.app._dev_block_detail_id is not None:
            if event.key in (pygame.K_ESCAPE, pygame.K_b):
                self.app._dev_block_detail_id = None
            return

        if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
            self.app._dev_block_browser = False
            self.app._dev_block_browser_cursor = 0
            self.app._dev_block_browser_scroll = 0
            return

        if event.key == pygame.K_TAB:
            self.app._dev_block_browser_mode = "list" if self.app._dev_block_browser_mode == "grid" else "grid"
            self.app._dev_block_browser_scroll = 0

        elif event.key == pygame.K_n:
            self.app._dev_block_browser_show_name2 = not self.app._dev_block_browser_show_name2

        elif event.key == pygame.K_RETURN:
            bid = all_ids[self.app._dev_block_browser_cursor]
            self.app._dev_block_detail_id = bid

        elif event.key == pygame.K_UP:
            if self.app._dev_block_browser_mode == "grid":
                COLS = 8
                self.app._dev_block_browser_cursor = max(0, self.app._dev_block_browser_cursor - COLS)
            else:
                self.app._dev_block_browser_cursor = max(0, self.app._dev_block_browser_cursor - 1)

        elif event.key == pygame.K_DOWN:
            if self.app._dev_block_browser_mode == "grid":
                COLS = 8
                self.app._dev_block_browser_cursor = min(len(all_ids) - 1, self.app._dev_block_browser_cursor + COLS)
            else:
                self.app._dev_block_browser_cursor = min(len(all_ids) - 1, self.app._dev_block_browser_cursor + 1)

        elif event.key == pygame.K_LEFT:
            if self.app._dev_block_browser_mode == "grid":
                self.app._dev_block_browser_cursor = max(0, self.app._dev_block_browser_cursor - 1)
            else:
                # 列表模式左键快速翻页
                visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
                self.app._dev_block_browser_cursor = max(0, self.app._dev_block_browser_cursor - visible_rows)
                self.app._dev_block_browser_scroll = max(0, self.app._dev_block_browser_scroll - visible_rows)

        elif event.key == pygame.K_RIGHT:
            if self.app._dev_block_browser_mode == "grid":
                self.app._dev_block_browser_cursor = min(len(all_ids) - 1, self.app._dev_block_browser_cursor + 1)
            else:
                visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
                self.app._dev_block_browser_cursor = min(len(all_ids) - 1, self.app._dev_block_browser_cursor + visible_rows)
                self.app._dev_block_browser_scroll = min(
                    max(0, len(all_ids) - visible_rows),
                    self.app._dev_block_browser_scroll + visible_rows)

    def _run_buff_browser(self, logic_surface, dt):
        """Buff 预览器渲染。"""
        import buff_data
        from buff_system import BUFF_TYPES
        all_ids = sorted(BUFF_TYPES.keys())
        if not all_ids:
            return

        if self.app._dev_buff_detail_id is not None:
            self._run_buff_detail(logic_surface, dt)
            return

        TITLE_Y = int(LOGIC_HEIGHT * 0.06) - 18  # 标题中心在6%
        HINT_Y = int(LOGIC_HEIGHT * 0.975)
        CONTENT_TOP2 = int(LOGIC_HEIGHT * 0.12)
        CONTENT_H = int(LOGIC_HEIGHT * 0.85)

        title = f"Buff 预览器 [{self.app._dev_buff_browser_mode.upper()}]"
        gt.draw(logic_surface, title, LOGIC_WIDTH // 2, TITLE_Y, 36,
                            (255, 255, 200), "sans", shadow=True, center_x=True)
        mode_hint = "Tab:切换视图  N:名称切换  Enter:详情  U/Esc:返回"
        gt.draw(logic_surface, mode_hint, LOGIC_WIDTH // 2, HINT_Y, 18,
                            (140, 160, 200), "sans", shadow=True, center_x=True)

        name_key = "name2" if self.app._dev_buff_browser_show_name2 else "name"
        cursor = self.app._dev_buff_browser_cursor

        if self.app._dev_buff_browser_mode == "grid":
            COLS = 8
            cell_w = 170
            cell_h = CONTENT_H // 4
            preview_size = 80
            start_x = (LOGIC_WIDTH - COLS * cell_w) // 2
            start_y = CONTENT_TOP2
            rows = (len(all_ids) + COLS - 1) // COLS
            visible_rows = 4

            cursor_row = cursor // COLS
            if cursor_row < self.app._dev_buff_browser_scroll:
                self.app._dev_buff_browser_scroll = cursor_row
            if cursor_row >= self.app._dev_buff_browser_scroll + visible_rows:
                self.app._dev_buff_browser_scroll = max(0, cursor_row - visible_rows + 1)
            self.app._dev_buff_browser_scroll = max(0, min(self.app._dev_buff_browser_scroll, max(0, rows - visible_rows)))

            for row in range(self.app._dev_buff_browser_scroll, min(self.app._dev_buff_browser_scroll + visible_rows, rows)):
                for col in range(COLS):
                    idx = row * COLS + col
                    if idx >= len(all_ids): break
                    bid = all_ids[idx]
                    bt = BUFF_TYPES[bid]
                    cx = start_x + col * cell_w
                    cy = start_y + (row - self.app._dev_buff_browser_scroll) * cell_h
                    if idx == cursor:
                        pygame.draw.rect(logic_surface, (80, 140, 255),
                                        (cx - 3, cy - 3, cell_w - 4, cell_h - 4), 2, border_radius=4)
                    px = cx + (cell_w - preview_size) // 2
                    self._draw_buff_icon(logic_surface, bt, px, cy + 4, preview_size)
                    label = f"{bid}.{getattr(bt, name_key, bt.name)}"
                    gt.draw(logic_surface, label, cx + cell_w // 2, cy + preview_size + 22, 20,
                                        (220, 220, 220), "sans", shadow=True, center_x=True)
        else:
            row_h = CONTENT_H // 8; preview_size = 60; start_y = CONTENT_TOP2
            visible_rows = 8
            cat_names = {"positive": "有益", "neutral": "中性", "negative": "有害"}

            if cursor < self.app._dev_buff_browser_scroll:
                self.app._dev_buff_browser_scroll = cursor
            if cursor >= self.app._dev_buff_browser_scroll + visible_rows:
                self.app._dev_buff_browser_scroll = max(0, cursor - visible_rows + 1)
            self.app._dev_buff_browser_scroll = max(0, min(self.app._dev_buff_browser_scroll, max(0, len(all_ids) - visible_rows)))

            for i in range(self.app._dev_buff_browser_scroll, min(self.app._dev_buff_browser_scroll + visible_rows, len(all_ids))):
                bid = all_ids[i]
                bt = BUFF_TYPES[bid]
                cy = start_y + (i - self.app._dev_buff_browser_scroll) * row_h
                if i == cursor:
                    pygame.draw.rect(logic_surface, (60, 60, 100), (40, cy, LOGIC_WIDTH - 80, row_h))
                    pygame.draw.rect(logic_surface, (100, 200, 255), (40, cy, LOGIC_WIDTH - 80, row_h), 2)
                self._draw_buff_icon(logic_surface, bt, 56, cy + (row_h - preview_size) // 2, preview_size)
                cat_str = cat_names.get(bt.category, bt.category)
                cat_colors = {"positive": (100, 220, 100), "neutral": (100, 180, 240), "negative": (240, 100, 100)}
                cat_color = cat_colors.get(bt.category, (170, 170, 170))
                line1 = f"[{bt.id}] {bt.name}  |  {bt.name2}"
                gt.draw(logic_surface, line1, 56 + preview_size + 16, cy + 10, 20,
                                    (255, 255, 210), "sans", shadow=True)
                label_w, _ = gt.draw(logic_surface, f"[{cat_str}] ", 56 + preview_size + 16, cy + 42, 17,
                                    cat_color, "sans", shadow=True)
                gt.draw(logic_surface, bt.desc, 56 + preview_size + 16 + label_w, cy + 42, 17,
                                    (170, 190, 220), "sans", shadow=True)

    def _run_buff_detail(self, logic_surface, dt):
        """Buff 详情页：3栏布局，参照方块详情。"""
        import buff_data
        from buff_system import BUFF_TYPES
        bid = self.app._dev_buff_detail_id
        if bid is None: return
        bt = BUFF_TYPES.get(bid)
        if bt is None:
            gt.draw(logic_surface, f"Buff {bid} 不存在", LOGIC_WIDTH // 2, 100, 24, (255,100,100), "sans", center_x=True)
            return

        M = 0.05
        ML = int(LOGIC_WIDTH * M)
        MR = int(LOGIC_WIDTH * (1-M))
        MT = int(LOGIC_HEIGHT * M)
        CONTENT_TOP = int(LOGIC_HEIGHT * 0.12)
        CONTENT_BOT = int(LOGIC_HEIGHT * 0.97)
        HINT_TOP = int(LOGIC_HEIGHT * 0.975)
        cat_names = {"positive": "有益", "neutral": "中性", "negative": "有害"}
        cat_colors = {"positive": (100, 220, 100), "neutral": (100, 180, 240), "negative": (240, 100, 100)}
        cat_str = cat_names.get(bt.category, bt.category)

        # ==== 标题 ====
        title = f"[{bt.id}] {bt.name}  |  {bt.name2}  [{cat_str}]"
        gt.draw(logic_surface, title, LOGIC_WIDTH // 2, MT + 20, 36,
                            cat_colors.get(bt.category, (255, 255, 200)), "sans", shadow=True, center_x=True)

        # ==== 中区：左中右3栏 ====
        cw = (MR - ML) // 3
        col1_x = ML
        col2_x = ML + cw
        col3_x = ML + cw * 2

        for sep_x in [col2_x - 2, col3_x - 2]:
            pygame.draw.line(logic_surface, (80, 80, 120), (sep_x, CONTENT_TOP), (sep_x, CONTENT_BOT), 1)

        # -- 左栏：大图标 + 基本信息 --
        preview_size = min(cw - 20, 200)
        self._draw_buff_icon(logic_surface, bt, col1_x + (cw - preview_size) // 2, CONTENT_TOP + 10, preview_size)

        FS = 22
        ly = CONTENT_TOP + preview_size + 20
        lh = 32
        linfos = [
            f"ID: {bt.id}",
            f"类别: {cat_str}",
            f"EN: {bt.name}",
            f"CN: {bt.name2}",
            f"最大叠层: {bt.max_stacks}",
        ]
        for i, inf in enumerate(linfos):
            if ly + i * lh > CONTENT_BOT - 10: break
            gt.draw(logic_surface, inf, col1_x + 6, ly + i * lh, FS, (210, 220, 250), "sans", shadow=True)

        # -- 中栏：效果描述 + 规则 --
        my = CONTENT_TOP + 10
        mh = 32
        mid_attrs = [
            f"描述: {bt.desc}",
            f"Tick: {bt.tick}",
            f"冲突: {bt.conflicts}",
            f"被清除: {bt.cleanup_by}",
            f"应用效果: {bt.on_apply}",
            f"移除效果: {bt.on_remove}",
        ]
        for i, attr in enumerate(mid_attrs):
            if my + i * mh > CONTENT_BOT - 10: break
            gt.draw(logic_surface, attr, col2_x + 6, my + i * mh, FS, (210, 220, 250), "sans", shadow=True)

        # -- 右栏：图标编码 --
        ry = CONTENT_TOP + 8
        sep_text = "======== 图标编码 ========"
        gt.draw(logic_surface, sep_text, col3_x + cw // 2, ry, 22,
                            (190, 200, 240), "sans", shadow=True, center_x=True)
        ry += 32

        if bt.icon is not None:
            ptype = bt.icon[0]
            if ptype == "bitmap":
                size = bt.icon[1] if len(bt.icon) > 1 else "?"
                pixels = bt.icon[2] if len(bt.icon) > 2 else []
                gt.draw(logic_surface, f"编码: 位图", col3_x + 6, ry, 19, (200, 210, 240), "sans")
                gt.draw(logic_surface, f"尺寸: {size}x{size}", col3_x + 6, ry + 26, 19, (180, 190, 220), "sans")
                flat = "[" + ", ".join(str(row) for row in pixels[:16]) + (", ..." if len(pixels) > 16 else "") + "]"
                chars_per_line = (cw - 20) // 7
                bj = 0
                while bj < len(flat):
                    chunk = flat[bj:bj + chars_per_line]
                    if ry + 52 + (bj // chars_per_line) * 15 > CONTENT_BOT - 10: break
                    gt.draw(logic_surface, chunk, col3_x + 6, ry + 52 + (bj // chars_per_line) * 15, 13, (150, 170, 210), "sans")
                    bj += chars_per_line
            elif ptype == "texture":
                code = bt.icon[1] if len(bt.icon) > 1 else "?"
                params = bt.icon[2] if len(bt.icon) > 2 else {}
                gt.draw(logic_surface, f"编码: 预设", col3_x + 6, ry, 28, (200, 210, 240), "sans")
                gt.draw(logic_surface, f"代码: {code}", col3_x + 6, ry + 32, 27, (180, 190, 220), "sans")
                show_y = ry + 60
                if isinstance(params, dict):
                    for k, v in params.items():
                        if show_y > CONTENT_BOT - 16: break
                        gt.draw(logic_surface, f"{k}: {v}", col3_x + 6, show_y, 22, (150, 170, 200), "sans")
                        show_y += 28
                elif isinstance(params, (tuple, list)):
                    gt.draw(logic_surface, f"参数: {params}",
                                        col3_x + 6, show_y, 18, (150, 170, 200), "sans")
            elif ptype == "vector":
                vw, vh = bt.icon[1]
                cmds = bt.icon[2] if len(bt.icon) > 2 else []
                n_cmds = len(cmds)
                gt.draw(logic_surface, f"编码: 矢量  画布: {vw}x{vh}  指令: {n_cmds}",
                                    col3_x + 6, ry, 19, (200, 210, 240), "sans")
                if n_cmds <= 35:
                    VFS = 16; VLH = 19
                    for j, cmd in enumerate(cmds):
                        cy2 = ry + 28 + j * VLH
                        if cy2 > CONTENT_BOT - 8: break
                        ctype = cmd[0]
                        if ctype == "fill":
                            c = cmd[1]
                            text = f"fill({c[0]},{c[1]},{c[2]})"
                        elif ctype == "rect":
                            c = cmd[5]
                            text = f"rect({cmd[1]},{cmd[2]},{cmd[3]},{cmd[4]},({c[0]},{c[1]},{c[2]}))"
                        elif ctype == "circle":
                            c = cmd[4]
                            text = f"circle({cmd[1]},{cmd[2]},{cmd[3]},({c[0]},{c[1]},{c[2]}))"
                        else:
                            text = str(cmd)
                        gt.draw(logic_surface, text, col3_x + 6, cy2, VFS, (150, 170, 210), "sans")
                else:
                    abs_compact = n_cmds > 105
                    avail_w = int(LOGIC_WIDTH * 0.965) - (col3_x + 6)
                    if abs_compact:
                        flat = "[" + ",".join(
                            f"fill({c[1][0]},{c[1][1]},{c[1][2]})" if c[0] == "fill"
                            else f"rect({c[1]},{c[2]},{c[3]},{c[4]},({c[5][0]},{c[5][1]},{c[5][2]}))" if c[0] == "rect"
                            else f"circle({c[1]},{c[2]},{c[3]},({c[4][0]},{c[4][1]},{c[4][2]}))" if c[0] == "circle"
                            else str(c).replace(" ", "")
                            for c in cmds
                        ) + "]"
                        CFS = 10; CLH = 11; cpch = max(1, avail_w // 5)
                    else:
                        flat = "[" + ", ".join(
                            f"fill({c[1][0]},{c[1][1]},{c[1][2]})" if c[0] == "fill"
                            else f"rect({c[1]},{c[2]},{c[3]},{c[4]},({c[5][0]},{c[5][1]},{c[5][2]}))" if c[0] == "rect"
                            else f"circle({c[1]},{c[2]},{c[3]},({c[4][0]},{c[4][1]},{c[4][2]}))" if c[0] == "circle"
                            else str(c)
                            for c in cmds
                        ) + "]"
                        CFS = 13; CLH = 15; cpch = max(1, avail_w // 7)
                    bj = 0
                    while bj < len(flat):
                        chunk = flat[bj:bj + cpch]
                        if ry + 28 + (bj // cpch) * CLH > CONTENT_BOT - 10: break
                        gt.draw(logic_surface, chunk, col3_x + 6, ry + 28 + (bj // cpch) * CLH, CFS, (150, 170, 210), "sans")
                        bj += cpch
        else:
            gt.draw(logic_surface, f"编码: 无  纯色图标", col3_x + 6, ry, 19, (160, 180, 200), "sans")

        # ==== 下区 ====
        gt.draw(logic_surface, "U / Esc  返回列表", LOGIC_WIDTH // 2, HINT_TOP + 4, 18,
                            (140, 160, 200), "sans", shadow=True, center_x=True)

    def _draw_buff_icon(self, surf, bt, x, y, size):
        """绘制 buff 图标。"""
        from pattern import _draw_vector, _draw_bitmap
        preview = pygame.Surface((size, size))
        if bt.icon is not None:
            try:
                icon = bt.icon
                fmt = icon[0]
                if fmt == "vector":
                    pattern_surf = _draw_vector(icon, size, size)
                    if pattern_surf is not None:
                        preview.blit(pattern_surf, (0, 0))
                    else:
                        preview.fill((80, 80, 100))
                elif fmt == "bitmap":
                    pattern_surf = _draw_bitmap(icon, size, size)
                    if pattern_surf is not None:
                        preview.blit(pattern_surf, (0, 0))
                    else:
                        preview.fill((80, 80, 100))
                else:
                    preview.fill((80, 80, 100))
            except Exception:
                preview.fill((80, 80, 100))
        else:
            preview.fill((80, 80, 100))
        surf.blit(preview, (x, y))
        pygame.draw.rect(surf, (100, 100, 120), (x, y, size, size), 1)

    def _handle_buff_browser_input(self, event):
        """处理 Buff 预览器的键盘事件。"""
        import buff_data
        from buff_system import BUFF_TYPES

        if event.type != pygame.KEYDOWN: return
        all_ids = sorted(BUFF_TYPES.keys())
        if not all_ids: return

        if self.app._dev_buff_detail_id is not None:
            if event.key in (pygame.K_ESCAPE, pygame.K_u):
                self.app._dev_buff_detail_id = None
            return

        if event.key in (pygame.K_ESCAPE, pygame.K_u):
            self.app._dev_buff_browser = False
            self.app._dev_buff_browser_cursor = 0
            return

        if event.key == pygame.K_TAB:
            self.app._dev_buff_browser_mode = "list" if self.app._dev_buff_browser_mode == "grid" else "grid"
            self.app._dev_buff_browser_scroll = 0
        elif event.key == pygame.K_n:
            self.app._dev_buff_browser_show_name2 = not self.app._dev_buff_browser_show_name2
        elif event.key == pygame.K_RETURN:
            self.app._dev_buff_detail_id = all_ids[self.app._dev_buff_browser_cursor]
        elif event.key == pygame.K_UP:
            self.app._dev_buff_browser_cursor = max(0, self.app._dev_buff_browser_cursor - (8 if self.app._dev_buff_browser_mode == "grid" else 1))
        elif event.key == pygame.K_DOWN:
            self.app._dev_buff_browser_cursor = min(len(all_ids) - 1, self.app._dev_buff_browser_cursor + (8 if self.app._dev_buff_browser_mode == "grid" else 1))
        elif event.key == pygame.K_LEFT:
            if self.app._dev_buff_browser_mode == "grid":
                self.app._dev_buff_browser_cursor = max(0, self.app._dev_buff_browser_cursor - 1)
            else:
                visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
                self.app._dev_buff_browser_cursor = max(0, self.app._dev_buff_browser_cursor - visible_rows)
                self.app._dev_buff_browser_scroll = max(0, self.app._dev_buff_browser_scroll - visible_rows)
        elif event.key == pygame.K_RIGHT:
            if self.app._dev_buff_browser_mode == "grid":
                self.app._dev_buff_browser_cursor = min(len(all_ids) - 1, self.app._dev_buff_browser_cursor + 1)
            else:
                visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
                self.app._dev_buff_browser_cursor = min(len(all_ids) - 1, self.app._dev_buff_browser_cursor + visible_rows)
                self.app._dev_buff_browser_scroll = min(
                    max(0, len(all_ids) - visible_rows),
                    self.app._dev_buff_browser_scroll + visible_rows)
