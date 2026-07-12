"""
游戏主页模块 —— 主菜单界面，含动画背景、菜单按钮、Logo 等。
"""
from __future__ import annotations
import math, random, time
import pygame
import game_text as gt

# ===================== 常量 =====================
MENU_START = 0
MENU_SETTINGS = 1
MENU_DEV = 2
MENU_QUIT = 3

_MENU_ITEMS = [
    (MENU_START,    "开始游戏",    "▶  进入地图选择"),
    (MENU_SETTINGS, "设  置",     "⚙  音效 / 帧率 / 音量"),
    (MENU_DEV,      "开发者界面",  "🛠  地图管理 & 属性编辑"),
    (MENU_QUIT,     "退出游戏",    "✕  返回桌面"),
]

# ===================== 状态变量 =====================
_selected_index = 0
_stars = []
_particles = []
_elapsed = 0.0
_logo_bounce_t = 0.0
_menu_anim_t = 0.0
_entered = False               # 是否已从加载过渡进入
_entry_alpha = 0.0             # 入场过渡 alpha
_quit_requested = False


def init_home_page(logic_w: int, logic_h: int):
    """初始化主页（粒子、星空、入场动画等）。"""
    global _selected_index, _stars, _particles, _elapsed
    global _logo_bounce_t, _menu_anim_t, _entered, _entry_alpha, _quit_requested

    _selected_index = 0
    _elapsed = 0.0
    _logo_bounce_t = 0.0
    _menu_anim_t = 0.0
    _entered = False
    _entry_alpha = 0.0
    _quit_requested = False

    # 背景粒子
    _particles = []
    for _ in range(35):
        _particles.append({
            'x': random.uniform(0, logic_w),
            'y': random.uniform(0, logic_h),
            'vx': random.uniform(-5, 5),
            'vy': random.uniform(-12, -3),
            'size': random.uniform(1.0, 3.5),
            'alpha': random.randint(30, 140),
            'color': random.choice([
                (255, 200, 80), (80, 150, 255), (100, 230, 140),
                (255, 130, 160), (180, 140, 255), (220, 220, 255),
            ]),
            'phase': random.uniform(0, math.pi * 2),
        })

    # 星空
    _stars = []
    for _ in range(120):
        _stars.append({
            'x': random.uniform(0, logic_w),
            'y': random.uniform(0, logic_h),
            'size': random.uniform(0.3, 2.2),
            'twinkle_speed': random.uniform(1.5, 5.0),
            'twinkle_phase': random.uniform(0, math.pi * 2),
        })


def get_selected_action() -> int:
    """返回当前选中的菜单项 ID。"""
    return _MENU_ITEMS[_selected_index][0]


def set_selected_index(index: int):
    global _selected_index
    _selected_index = index % len(_MENU_ITEMS)


def move_selection(delta: int):
    global _selected_index
    _selected_index = (_selected_index + delta) % len(_MENU_ITEMS)


def is_quit_requested() -> bool:
    return _quit_requested


def run_home_page(surf: pygame.Surface, dt: float, logic_w: int, logic_h: int):
    """渲染一帧主页。"""
    global _elapsed, _logo_bounce_t, _menu_anim_t, _entry_alpha, _entered, _quit_requested

    _elapsed += dt
    _entry_alpha = min(255, _entry_alpha + dt * 200)
    _logo_bounce_t += dt
    _menu_anim_t += dt

    # ---- 背景 ----
    bg = pygame.Surface((logic_w, logic_h))
    for y in range(0, logic_h, 3):
        t = y / logic_h
        r = int(10 + t * 18)
        g = int(8 + t * 12)
        b = int(25 + t * 40)
        pygame.draw.rect(bg, (r, g, b), (0, y, logic_w, 3))
    surf.blit(bg, (0, 0))

    # ---- 星空 ----
    for star in _stars:
        twinkle = (math.sin(_elapsed * star['twinkle_speed'] + star['twinkle_phase']) + 1) / 2
        alpha = int(50 + twinkle * 190)
        sx, sy = int(star['x']), int(star['y'])
        ss = int(star['size'] * (0.7 + twinkle * 0.5))
        if 0 <= sx < logic_w and 0 <= sy < logic_h:
            star_surf = pygame.Surface((ss * 2 + 2, ss * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (200, 210, 255, alpha), (ss + 1, ss + 1), ss)
            surf.blit(star_surf, (sx - ss, sy - ss))

    # ---- 背景粒子 ----
    for p in _particles:
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        if p['y'] < -20:
            p['y'] = logic_h + 20
            p['x'] = random.uniform(0, logic_w)
        if p['x'] < -20:
            p['x'] = logic_w + 20
        if p['x'] > logic_w + 20:
            p['x'] = -20

        wave = math.sin(_elapsed * 2.0 + p['phase']) * 0.25
        alpha = int(p['alpha'] * (0.6 + wave))
        px, py = int(p['x']), int(p['y'])
        if 0 <= px < logic_w and 0 <= py < logic_h:
            ps = int(p['size'])
            p_surf = pygame.Surface((ps * 2 + 2, ps * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], max(0, min(255, alpha))),
                              (ps + 1, ps + 1), max(1, ps))
            surf.blit(p_surf, (px - ps, py - ps))

    # ---- Logo 区域 ----
    logo_bounce = math.sin(_logo_bounce_t * 2.0) * 5
    logo_center_y = int(logic_h * 0.18) + logo_bounce

    # Logo 光晕
    glow_a = int(40 + math.sin(_elapsed * 1.5) * 20)
    glow_s = pygame.Surface((520, 130), pygame.SRCALPHA)
    for i in range(5):
        r = 250 - i * 40
        a = glow_a - i * 10
        pygame.draw.rect(glow_s, (220, 180, 60, max(0, a)),
                        (10 - i * 4, 5 - i * 4, 500 + i * 8, 120 + i * 8),
                        border_radius=12 + i * 2)
    surf.blit(glow_s, (logic_w // 2 - 260, logo_center_y - 65))

    # 标题
    gt.draw(surf, "像素漫游者", logic_w // 2, logo_center_y - 38, 64,
            (255, 225, 90), "sans", center_x=True, shadow=True,
            shadow_color=(40, 25, 5))
    gt.draw(surf, "Pixel Roamer", logic_w // 2, logo_center_y + 30, 26,
            (170, 190, 210), "mono", center_x=True, shadow=True)

    # 装饰分隔线
    line_y = logo_center_y + 60
    line_w = 300
    line_alpha = int(80 + math.sin(_elapsed * 3.0) * 30)
    line_surf = pygame.Surface((line_w, 2), pygame.SRCALPHA)
    for i in range(line_w):
        t = abs(i - line_w / 2) / (line_w / 2)
        a = int(line_alpha * (1.0 - t ** 2))
        line_surf.set_at((i, 0), (180, 200, 240, a))
    surf.blit(line_surf, (logic_w // 2 - line_w // 2, line_y))

    # ---- 菜单项 ----
    menu_start_y = int(logic_h * 0.42)
    item_h = 62
    item_w = 420
    item_gap = 10

    for i, (action_id, label, desc) in enumerate(_MENU_ITEMS):
        is_sel = (i == _selected_index)
        item_x = logic_w // 2 - item_w // 2
        item_y = menu_start_y + i * (item_h + item_gap)

        # 入场动画延迟
        delay_offset = i * 0.12
        item_alpha = max(0.0, min(1.0, (_entry_alpha / 255) - delay_offset))

        if item_alpha > 0.01:
            # 选中光晕
            if is_sel:
                pulse = math.sin(_menu_anim_t * 3.5) * 0.3 + 0.7
                glow_w = item_w + 30
                glow_h = item_h + 16
                glow_rect = pygame.Rect(item_x - 15, item_y - 8, glow_w, glow_h)
                glow_s = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                for j in range(4):
                    a = int((50 - j * 12) * pulse * item_alpha)
                    pygame.draw.rect(glow_s, (100, 180, 255, max(0, a)),
                                    (j * 3, j * 3, glow_w - j * 6, glow_h - j * 6),
                                    border_radius=12 + j)
                surf.blit(glow_s, (item_x - 15, item_y - 8))

            # 按钮背景
            bg_alpha = int(220 * item_alpha) if is_sel else int(140 * item_alpha)
            bg_color = (35, 40, 70, bg_alpha) if is_sel else (22, 25, 45, bg_alpha)
            btn_bg = pygame.Surface((item_w, item_h), pygame.SRCALPHA)
            btn_bg.fill(bg_color)
            surf.blit(btn_bg, (item_x, item_y))

            # 按钮边框
            border_color = (120, 200, 255, int(230 * item_alpha)) if is_sel else (50, 55, 80, int(180 * item_alpha))
            border_w = 2 if is_sel else 1
            pygame.draw.rect(surf, border_color, (item_x, item_y, item_w, item_h),
                           border_w, border_radius=8)

            # 选中标记
            if is_sel:
                marker_x = item_x + 16
                marker_y = item_y + item_h // 2
                marker_size = 8
                marker_pts = [
                    (marker_x - marker_size, marker_y - marker_size // 2),
                    (marker_x + marker_size // 2, marker_y),
                    (marker_x - marker_size, marker_y + marker_size // 2),
                ]
                marker_color = (100, 220, 255)
                pygame.draw.polygon(surf, marker_color, marker_pts)

            # 标签
            label_color = (255, 255, 240) if is_sel else (190, 195, 210)
            label_alpha_final = int(255 * item_alpha)
            gt.draw(surf, label, item_x + 40, item_y + 7, 28,
                    (*label_color, label_alpha_final), "sans", shadow=is_sel)

            # 描述
            desc_color = (160, 200, 230) if is_sel else (120, 125, 140)
            gt.draw(surf, desc, item_x + 44, item_y + 36, 15,
                    (*desc_color, int(200 * item_alpha)), "sans")

            # 右侧箭头
            if is_sel:
                arrow_alpha = int(200 * (0.6 + math.sin(_menu_anim_t * 4.0) * 0.4))
                arrow_x = item_x + item_w - 30
                arrow_y = item_y + item_h // 2
                arrow_pts = [
                    (arrow_x - 5, arrow_y - 7),
                    (arrow_x + 7, arrow_y),
                    (arrow_x - 5, arrow_y + 7),
                ]
                pygame.draw.polygon(surf, (100, 200, 255, arrow_alpha), arrow_pts)

    # ---- 底部信息 ----
    bottom_y = logic_h - 60
    gt.draw(surf, "↑ ↓ / 1-4 选择   Enter 确认   Esc 开发者界面", logic_w // 2, bottom_y, 18,
            (130, 140, 170), "mono", center_x=True)
    gt.draw(surf, f"v1.0 — 开发者：浪兮", logic_w // 2, bottom_y + 24, 14,
            (90, 95, 115), "mono", center_x=True)

    # 装饰底部光点
    for i in range(5):
        x = logic_w // 2 + (i - 2) * 60
        pulse = math.sin(_elapsed * 3.0 + i * 1.2) * 0.5 + 0.5
        a = int(30 + pulse * 40)
        pygame.draw.circle(surf, (150, 170, 200, a), (int(x), bottom_y - 8), 3)


def handle_home_input(event) -> int | None:
    """
    处理主页键盘事件。
    返回: MENU_START / MENU_SETTINGS / MENU_DEV / MENU_QUIT 表示确认选择。
           None 表示未确认。
    """
    global _selected_index, _quit_requested

    if event.type != pygame.KEYDOWN:
        return None

    if event.key == pygame.K_UP or event.key == pygame.K_w:
        _selected_index = (_selected_index - 1) % len(_MENU_ITEMS)
        return None
    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
        _selected_index = (_selected_index + 1) % len(_MENU_ITEMS)
        return None
    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
        action = _MENU_ITEMS[_selected_index][0]
        if action == MENU_QUIT:
            _quit_requested = True
        return action
    elif event.key == pygame.K_ESCAPE:
        return None  # 主页不响应 Esc（由调用方处理）
    # 数字快捷键 1-4
    elif event.key == pygame.K_1:
        return _MENU_ITEMS[0][0]
    elif event.key == pygame.K_2:
        return _MENU_ITEMS[1][0]
    elif event.key == pygame.K_3:
        return _MENU_ITEMS[2][0]
    elif event.key == pygame.K_4:
        action = _MENU_ITEMS[3][0]
        if action == MENU_QUIT:
            _quit_requested = True
        return action

    return None


def handle_home_mouse(pos: tuple, logic_w: int, logic_h: int, scale: float,
                      draw_offset_x: float, draw_offset_y: float) -> int | None:
    """
    处理鼠标移动（高亮）和点击（确认）。
    pos: 窗口鼠标坐标 (mx, my)
    返回: 若点击了菜单项则返回对应 action ID，否则 None。
    """
    global _selected_index

    mx, my = pos
    logic_mx = (mx - draw_offset_x) / scale
    logic_my = (my - draw_offset_y) / scale

    item_h = 62
    item_gap = 10
    item_w = 420
    menu_start_y = int(logic_h * 0.42)
    item_x = logic_w // 2 - item_w // 2

    for i in range(len(_MENU_ITEMS)):
        item_y = menu_start_y + i * (item_h + item_gap)
        if item_x <= logic_mx <= item_x + item_w and item_y <= logic_my <= item_y + item_h:
            _selected_index = i
            return None

    return None
