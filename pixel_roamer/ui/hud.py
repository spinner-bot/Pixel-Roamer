from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
import sfx
import game_text as gt
import home_page as hp
from pixel_roamer.ui.config import BAR_GAP, BAR_H, BAR_TEXT_H, BAR_W, BAR_X, BAR_Y, BORDER_R, PAD

class HudRenderer:
    """Hud behavior; shared session and viewport come from app."""

    def __init__(self, app):
        self.app = app

    def _draw_single_bar(self, surf, x, y, w, h, pad, border_r,
                         fill_ratio: float, fill_ratio2: float,
                         color1, color2, flash_t: float, flash_dur: float):
        """
        绘制单个状态条（血条或体力条），支持副填充（护盾等）。
        fill_ratio: 主填充比例 (0~1)
        fill_ratio2: 副填充比例 (0~1)，在主填充右侧
        总宽度固定为 w，当 fill_ratio + fill_ratio2 > 1 时按比例压缩。
        """
        fill_w_total = w - pad * 2
        total_ratio = fill_ratio + fill_ratio2

        if total_ratio > 1.0:
            # 按比例压缩到 fill_w_total
            main_w = int(fill_w_total * fill_ratio / total_ratio)
            sub_w = int(fill_w_total * fill_ratio2 / total_ratio)
            # 确保加起来不超过 total
            if main_w + sub_w > fill_w_total:
                sub_w = fill_w_total - main_w
        else:
            main_w = int(fill_w_total * fill_ratio)
            sub_w = int(fill_w_total * fill_ratio2)

        main_w = max(0, min(main_w, fill_w_total))
        sub_w = max(0, min(sub_w, fill_w_total - main_w))

        # 阴影
        shadow_rect = pygame.Rect(x + 2, y + 2, w, h)
        pygame.draw.rect(surf, (0, 0, 0, 160), shadow_rect, border_radius=border_r)

        # 背景
        bg_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, (22, 22, 32), bg_rect, border_radius=border_r)

        # 主填充
        if main_w > 0:
            fill_rect = pygame.Rect(x + pad, y + pad, main_w, h - pad * 2)
            if flash_t > 0:
                flash_a = flash_t / flash_dur
                r = int(color1[0] * (1 - flash_a) + 255 * flash_a)
                g = int(color1[1] * (1 - flash_a) + 220 * flash_a)
                b = int(color1[2] * (1 - flash_a) + 60 * flash_a)
                bar_c = (min(255, r), min(255, g), min(255, b))
            else:
                bar_c = color1
            # 圆角矩形
            if border_r > 2:
                pygame.draw.rect(surf, bar_c, fill_rect, border_radius=border_r - 2)
            else:
                pygame.draw.rect(surf, bar_c, fill_rect)

            # 高光
            if main_w > 10 and h - pad * 2 > 6:
                hl_y = y + pad + 1
                hl_h = (h - pad * 2) // 2 - 1
                hl_rect = pygame.Rect(x + pad + 2, hl_y, main_w - 4, max(1, hl_h))
                hl_surf = pygame.Surface((max(1, main_w - 4), max(1, hl_h)), pygame.SRCALPHA)
                hl_surf.fill((255, 255, 255, 40))
                surf.blit(hl_surf, hl_rect)

        # 副填充（在右侧，与主填充无缝衔接）
        if sub_w > 0 and color2 is not None:
            sub_x = x + pad + main_w
            sub_rect = pygame.Rect(sub_x, y + pad, sub_w, h - pad * 2)
            if border_r > 2:
                pygame.draw.rect(surf, color2, sub_rect, border_radius=border_r - 2)
            else:
                pygame.draw.rect(surf, color2, sub_rect)
            # 高光
            if sub_w > 10 and h - pad * 2 > 6:
                hl_y = y + pad + 1
                hl_h = (h - pad * 2) // 2 - 1
                sh_hl_rect = pygame.Rect(sub_x + 2, hl_y, sub_w - 4, max(1, hl_h))
                sh_hl_surf = pygame.Surface((max(1, sub_w - 4), max(1, hl_h)), pygame.SRCALPHA)
                sh_hl_surf.fill((255, 255, 255, 50))
                surf.blit(sh_hl_surf, sh_hl_rect)

        # 边框
        pygame.draw.rect(surf, (70, 70, 90), bg_rect, 2, border_radius=border_r)

    def draw_hp_bar(self, surf, player, dt: float):
        """绘制血条（固定宽度，含护盾按比例压缩）。"""

        # 检测受伤
        if self.app._prev_hp is not None and player.hp < self.app._prev_hp - 0.5:
            self.app._damage_flash_timer = self.app._damage_flash_duration
            sfx.play_hurt()
        self.app._prev_hp = player.hp

        # 衰减闪烁计时器
        if self.app._damage_flash_timer > 0:
            self.app._damage_flash_timer -= dt

        hp = player.hp
        hp_max = max(1, player.hp_max)
        shield = getattr(player, 'shield', 0.0)

        hp_ratio = max(0.0, min(1.0, hp / hp_max))
        shield_ratio = shield / hp_max if shield > 0 else 0.0

        # HP 颜色：低血量红 → 渐变 → 高血量绿
        if hp_ratio < 0.3:
            hp_color = (220, 50, 40)
        elif hp_ratio < 0.6:
            t = (hp_ratio - 0.3) / 0.3
            hp_color = (int(220 - 60 * t), int(50 + 140 * t), 40)
        else:
            hp_color = (80, 200, 60)

        shield_color = (180, 210, 255) if shield > 0 else None

        self._draw_single_bar(surf, BAR_X, BAR_Y, BAR_W, BAR_H, PAD, BORDER_R,
                         hp_ratio, shield_ratio, hp_color, shield_color,
                         self.app._damage_flash_timer, self.app._damage_flash_duration)

        # 像素文字
        if shield > 0:
            txt = f"{int(hp)}/{int(hp_max)} +{int(shield)}"
        else:
            txt = f"{int(hp)}/{int(hp_max)}"
        gt.draw(surf, txt, BAR_X + BAR_W // 2, BAR_Y + BAR_H // 2 - BAR_TEXT_H // 2,
                             BAR_TEXT_H, (255, 255, 255), "mono", shadow=True, center_x=True)

        # 右侧心形图标（与条等高，留空隙）
        hx = BAR_X + BAR_W + BAR_H // 2 + 6
        hy = BAR_Y + BAR_H // 2
        hs = BAR_H // 2 - 2
        heart_color = (255, 50, 40) if hp_ratio < 0.3 else (255, 110, 90)
        heart_pts = [
            (hx, hy + hs),                    # 底尖
            (hx + hs*3//10, hy + hs*6//10),   # 右下内
            (hx + hs*7//10, hy + hs*3//10),   # 右下外
            (hx + hs*9//10, hy - hs//10),     # 右外
            (hx + hs*7//10, hy - hs//2),      # 右上
            (hx + hs*35//100, hy - hs*85//100), # 右瓣顶
            (hx + hs//10, hy - hs*65//100),   # 右瓣内
            (hx, hy - hs*3//10),              # 中心凹
            (hx - hs//10, hy - hs*65//100),   # 左瓣内
            (hx - hs*35//100, hy - hs*85//100), # 左瓣顶
            (hx - hs*7//10, hy - hs//2),      # 左上
            (hx - hs*9//10, hy - hs//10),     # 左外
            (hx - hs*7//10, hy + hs*3//10),   # 左下外
            (hx - hs*3//10, hy + hs*6//10),   # 左下内
        ]
        pygame.draw.polygon(surf, heart_color, heart_pts)
        pygame.draw.polygon(surf, (160, 25, 15), heart_pts, 1)

    def draw_stamina_bar(self, surf, player, dt: float):
        """在血条下方绘制体力条。体力不足时闪烁。"""
        stam_y = BAR_Y + BAR_H + BAR_GAP
        stamina = getattr(player, 'stamina', 100.0)
        stamina_max = max(1, getattr(player, 'stamina_max', 100.0))
        ratio = max(0.0, min(1.0, stamina / stamina_max))

        # 衰减闪烁计时器
        if self.app._stamina_flash_timer > 0:
            self.app._stamina_flash_timer -= dt

        # 体力颜色：低体力红 → 橙 → 蓝
        if ratio < 0.25:
            stam_color = (200, 60, 40)
        elif ratio < 0.5:
            t = (ratio - 0.25) / 0.25
            stam_color = (int(200 - 40 * t), int(60 + 100 * t), int(40 + 80 * t))
        else:
            stam_color = (60, 140, 220)

        self._draw_single_bar(surf, BAR_X, stam_y, BAR_W, BAR_H, PAD, BORDER_R,
                         ratio, 0.0, stam_color, None, 0.0, 0.0)

        # 体力不足时边框闪3次（16Hz，均匀间隔，仅亮帧覆盖）
        if self.app._stamina_flash_timer > 0:
            tick = int(self.app._stamina_flash_timer * 16)
            if tick in (0, 5, 10):  # 闪3下
                flash_rect = pygame.Rect(BAR_X, stam_y, BAR_W, BAR_H)
                pygame.draw.rect(surf, (255, 255, 255), flash_rect, 3, border_radius=BORDER_R)

        # 像素文字
        txt = f"{int(stamina)}/{int(stamina_max)}"
        gt.draw(surf, txt, BAR_X + BAR_W // 2, stam_y + BAR_H // 2 - BAR_TEXT_H // 2,
                             BAR_TEXT_H, (255, 255, 255), "mono", shadow=True, center_x=True)

        # 右侧闪电图标（蓝色填充+深色边框，7点精确数据）
        ox = BAR_X + BAR_W + 8
        oy = stam_y + 1
        s = BAR_H - 2  # 正方形画布边长
        bolt_fill = (80, 180, 255)
        bolt_border = (20, 60, 140)
        # 7关键点（百分比坐标，原点左上）
        bolt_pts = [
            (ox + 0.350*s, oy + 0.135*s),
            (ox + 0.600*s, oy + 0.135*s),
            (ox + 0.465*s, oy + 0.425*s),
            (ox + 0.720*s, oy + 0.425*s),
            (ox + 0.465*s, oy + 0.900*s),
            (ox + 0.510*s, oy + 0.510*s),
            (ox + 0.245*s, oy + 0.515*s),
        ]
        # 边框（外扩1px）
        cx = ox + s/2; cy = oy + s/2
        bd_pts = [(x + (1.5 if x >= cx else -1.5), y + (1.5 if y >= cy else -1.5)) for x, y in bolt_pts]
        pygame.draw.polygon(surf, bolt_border, bd_pts)
        pygame.draw.polygon(surf, bolt_fill, bolt_pts)

    def _draw_heart(self, surf, cx, cy, size, color, border_color):
        """绘制一颗爱心（同HP条图标的矢量风格）。"""
        hs = size / 2
        hx, hy = cx, cy
        pts = [
            (hx, hy + hs),
            (hx + hs*3//10, hy + hs*6//10),
            (hx + hs*7//10, hy + hs*3//10),
            (hx + hs*9//10, hy - hs//10),
            (hx + hs*7//10, hy - hs//2),
            (hx + hs*35//100, hy - hs*85//100),
            (hx + hs//10, hy - hs*65//100),
            (hx, hy - hs*3//10),
            (hx - hs//10, hy - hs*65//100),
            (hx - hs*35//100, hy - hs*85//100),
            (hx - hs*7//10, hy - hs//2),
            (hx - hs*9//10, hy - hs//10),
            (hx - hs*7//10, hy + hs*3//10),
            (hx - hs*3//10, hy + hs*6//10),
        ]
        # 边框外扩
        bd_pts = [(x + (1.2 if x >= hx else -1.2), y + (1.2 if y >= hy else -1.2)) for x, y in pts]
        pygame.draw.polygon(surf, border_color, bd_pts)
        pygame.draw.polygon(surf, color, pts)

    def draw_player_info(self, surf, player, dt: float):
        """在体力条正下方绘制复活次数（精致心形图标）。"""
        if self.app._player_lives_left > 0 and self.app._player_lives_left <= 99:
            stam_y = BAR_Y + BAR_H + BAR_GAP
            # 条正下方居中
            cx_center = BAR_X + BAR_W // 2
            cy_base = stam_y + BAR_H + 14
            heart_size = 16
            heart_gap = 20
            total_w = self.app._player_lives_left * heart_gap - (heart_gap - heart_size)
            start_x = int(cx_center - total_w / 2)
            for i in range(self.app._player_lives_left):
                hx = start_x + i * heart_gap
                self._draw_heart(surf, hx, cy_base, heart_size, (255, 55, 45), (140, 20, 10))

    def _format_time(self, seconds: float) -> str:
        """将秒数格式化为可读时间字符串。"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            m = int(seconds // 60)
            s = seconds - m * 60
            return f"{m}min{s:.1f}s"
        else:
            h = int(seconds // 3600)
            r = seconds - h * 3600
            m = int(r // 60)
            s = r - m * 60
            return f"{h}h{m}min{s:.1f}s"

    def draw_buff_status(self, surf, player, dt: float):
        """在屏幕左下方绘制当前活跃 buff 的状态图标（含进度扇形和层数）。"""
        self.app._buff_icon_rects = []

        if not player.buffs:
            return

        import math
        import buff_data
        from buff_system import BUFF_TYPES
        from pattern import _draw_vector, _draw_bitmap

        p = BAR_H                     # 图标边长（与血条等高）
        gap = int(p * 0.2)            # 间隙
        step = p + gap                # 步进 1.2p
        cols = 5                      # 每行最多5个
        base_x = BAR_X                # 左对齐血条
        base_y = int(LOGIC_HEIGHT * 0.875)  # 底边 87.5%

        for k, b in enumerate(player.buffs):
            btype = BUFF_TYPES.get(b.buff_id)
            if btype is None or btype.icon is None:
                continue

            col = k % cols
            row = k // cols
            ix = base_x + col * step
            iy = base_y - p - row * step  # 从底向上堆叠

            # 记录位置供悬浮检测
            self.app._buff_icon_rects.append((ix, iy, p, b))

            # ---- 绘制图标 ----
            icon_surf = pygame.Surface((p, p))
            try:
                icon = btype.icon
                fmt = icon[0]
                if fmt == "vector":
                    psurf = _draw_vector(icon, p, p)
                elif fmt == "bitmap":
                    psurf = _draw_bitmap(icon, p, p)
                else:
                    psurf = None
                if psurf is not None:
                    icon_surf.blit(psurf, (0, 0))
                else:
                    icon_surf.fill((60, 60, 80))
            except Exception:
                icon_surf.fill((60, 60, 80))
            surf.blit(icon_surf, (ix, iy))
            pygame.draw.rect(surf, (100, 100, 130), (ix, iy, p, p), 1)

            # ---- 进度扇形覆盖（非永久buff） ----
            if b.duration is not None and b.initial_duration and b.initial_duration > 0:
                progress = 1.0 - (b.duration / b.initial_duration)
                progress = max(0.0, min(1.0, progress))
                if progress > 0.01:
                    overlay = pygame.Surface((p, p), pygame.SRCALPHA)
                    cx_p, cy_p = p / 2, p / 2
                    r = p * 0.75  # 覆盖四角（对角线半长≈p*0.707）
                    start_angle = -math.pi / 2  # 正上方
                    end_angle = start_angle + progress * 2 * math.pi
                    n_seg = max(3, int(progress * 36))
                    pie_pts = [(cx_p, cy_p)]
                    for seg in range(n_seg + 1):
                        a = start_angle + seg * (end_angle - start_angle) / n_seg
                        pie_pts.append((cx_p + r * math.cos(a), cy_p + r * math.sin(a)))
                    pygame.draw.polygon(overlay, (255, 255, 255, 175), pie_pts)
                    surf.blit(overlay, (ix, iy))

            # ---- 层数（右下角） ----
            if b.stacks > 1:
                stack_text = str(b.stacks)
                gt.draw(surf, stack_text, ix + p - 3, iy + p - 1, 12,
                                   (255, 255, 255), "mono", shadow=True, right_x=True)

        # ---- 鼠标悬浮浮窗 ----
        mx, my = pygame.mouse.get_pos()
        logic_mx = (mx - self.app.draw_offset_x) / self.app.scale
        logic_my = (my - self.app.draw_offset_y) / self.app.scale

        for ix, iy, p, b in self.app._buff_icon_rects:
            if ix <= logic_mx <= ix + p and iy <= logic_my <= iy + p:
                btype = b.buff_type
                if btype is None:
                    continue
                name_text = btype.name2 or btype.name
                if b.duration is not None:
                    time_text = self._format_time(max(0, b.duration))
                else:
                    time_text = "永久"
                # 名称按类别着色
                cat_colors = {"positive": (100, 255, 100), "neutral": (100, 200, 255), "negative": (255, 100, 100)}
                name_color = cat_colors.get(btype.category, (255, 255, 220))
                title = f"{name_text}  {time_text}"
                desc = b.format_desc() if b.format_desc() else ""

                TW = 18
                DW = 14
                PAD_X = 12
                PAD_Y = 8
                MIN_W = 160
                MAX_W = 280
                # 标题像素宽度（中文≈字号，ASCII≈字号/2）
                title_px = sum(TW if ord(c) > 127 else TW // 2 for c in title)
                popup_w = max(MIN_W, min(MAX_W, title_px + PAD_X * 2))

                # 描述像素级换行（中文≈DW，ASCII≈DW/2）
                avail_w = popup_w - PAD_X * 2
                desc_lines = []
                if desc:
                    line = ""
                    line_px = 0
                    for ch in desc:
                        ch_w = DW if ord(ch) > 127 else DW // 2
                        if line_px + ch_w > avail_w and line:
                            desc_lines.append(line)
                            line = ch
                            line_px = ch_w
                        else:
                            line += ch
                            line_px += ch_w
                    if line:
                        desc_lines.append(line)

                # 动态高度
                title_h = TW + 4
                desc_h = len(desc_lines) * (DW + 4) if desc_lines else 0
                popup_h = PAD_Y * 2 + title_h + desc_h + (4 if desc_lines else 0)

                # 定位
                popup_x = logic_mx + 16
                popup_y = logic_my - popup_h // 2
                if popup_x + popup_w > LOGIC_WIDTH:
                    popup_x = logic_mx - popup_w - 16
                if popup_y < 4:
                    popup_y = 4
                if popup_y + popup_h > LOGIC_HEIGHT - 4:
                    popup_y = LOGIC_HEIGHT - popup_h - 4

                # 背景
                popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
                pygame.draw.rect(surf, (15, 15, 35), popup_rect, border_radius=4)
                pygame.draw.rect(surf, (80, 80, 120), popup_rect, 1, border_radius=4)

                # 标题居中（名称类别色 + 时间中性色）
                name_px = sum(TW if ord(c) > 127 else TW // 2 for c in name_text)
                gap_px = TW  # "  " 约一个中文字宽
                time_px = sum(TW if ord(c) > 127 else TW // 2 for c in f"  {time_text}")
                total_title_px = name_px + time_px
                title_start_x = popup_x + (popup_w - total_title_px) // 2
                gt.draw(surf, name_text, title_start_x, popup_y + PAD_Y, TW,
                                   name_color, "sans", shadow=True)
                gt.draw(surf, f"  {time_text}", title_start_x + name_px, popup_y + PAD_Y, TW,
                                   (200, 200, 210), "sans", shadow=True)
                # 描述居中
                if desc_lines:
                    dy = popup_y + PAD_Y + title_h + 4
                    for dl in desc_lines:
                        gt.draw(surf, dl, popup_x + popup_w // 2, dy, DW,
                                           (200, 210, 230), "sans", shadow=True, center_x=True)
                        dy += DW + 4
                break

    def draw_near_death_vignette(self, surf, player):
        """当血量极低时，屏幕边缘绘制渐变红圈，确保覆盖四角。"""
        if not player.alive:
            return

        hp_ratio = player.hp / player.hp_max
        is_critical = hp_ratio < 0.10 or player.hp < 15

        if not is_critical:
            return

        # 计算透明度：血量越低越明显
        alpha = int(180 * (1.0 - hp_ratio / 0.10)) if hp_ratio < 0.10 else int(180 * (1.0 - player.hp / 15))
        alpha = max(60, min(alpha, 200))

        W, H = surf.get_width(), surf.get_height()
        cx, cy = W // 2, H // 2
        max_r = int((cx ** 2 + cy ** 2) ** 0.5) + 20  # 略微超出保证覆盖四角

        vignette = pygame.Surface((W, H), pygame.SRCALPHA)
        # 先填充整个表面为基础红色，确保四角不漏
        vignette.fill((200, 20, 20, alpha))

        # 从外向内绘制渐变透明圈，中心逐渐变淡
        inner_r = int(max_r * 0.40)  # 内部安全区半径
        steps = 50
        for i in range(steps):
            t = i / steps
            r = inner_r + (max_r - inner_r) * t
            # 越靠近中心的圈越"擦除"，形成渐变效果
            erase_a = int(alpha * (1.0 - t ** 1.5))
            if erase_a > 0:
                pygame.draw.circle(vignette, (200, 20, 20, max(1, alpha - erase_a)),
                                 (cx, cy), int(r), max(2, int((max_r - inner_r) / steps) + 1))

        # 中心安全区完全透明
        for rr in range(int(inner_r) - 2, int(inner_r) + 2):
            pygame.draw.circle(vignette, (0, 0, 0, 0), (cx, cy), rr)

        surf.blit(vignette, (0, 0))
