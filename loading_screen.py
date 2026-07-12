"""
加载界面模块 —— 启动时的过渡动画，展示 Logo 和加载进度。
包含粒子背景、进度条、旋转提示等效果。
"""
from __future__ import annotations
import math, random, time
import pygame
import game_text as gt

# ===================== 状态变量 =====================
_start_time = 0.0
_progress = 0.0                # 0.0 ~ 1.0
_loading_complete = False
_tip_index = 0
_tip_alpha = 0.0               # 提示文字透明度（0~255）
_tip_transition = 0.0           # 切换计时器
_particles = []                 # 背景粒子
_stars = []                     # 星空背景
_logo_scale = 1.0
_logo_bounce_t = 0.0
_dots = 0                      # 加载动画点数
_dot_timer = 0.0

# 提示文字列表
TIPS = [
    "提示：使用 A/D 或 ← → 移动角色",
    "提示：空格键跳跃，W/↑ 攀爬或游泳",
    "提示：F 键切换飞行模式（需地图支持）",
    "提示：按 C 键切换角色时装",
    "提示：按 Backspace 打开设置",
    "提示：收集积分可解锁特殊奖励",
    "提示：注意体力条，耗尽后无法攀爬和跳跃",
    "提示：低血量时屏幕边缘会出现红色警告",
    "提示：不同方块有不同的物理属性",
    "提示：按 F1/F2 调整帧率上限",
    "提示：探索地图边界，发现隐藏区域",
    "提示：游泳时按空格键可快速上岸",
]

# 粒子颜色
PARTICLE_COLORS = [
    (255, 200, 80), (80, 180, 255), (100, 255, 150),
    (255, 120, 150), (200, 150, 255), (255, 255, 200),
    (100, 220, 220), (255, 180, 100),
]


def init_loading_screen(logic_w: int, logic_h: int):
    """初始化加载界面（粒子、星空等）。"""
    global _start_time, _progress, _loading_complete
    global _tip_index, _tip_alpha, _tip_transition
    global _particles, _stars, _logo_scale, _logo_bounce_t, _dots, _dot_timer

    _start_time = time.time()
    _progress = 0.0
    _loading_complete = False
    _tip_index = random.randint(0, len(TIPS) - 1)
    _tip_alpha = 0.0
    _tip_transition = 0.0
    _logo_scale = 1.0
    _logo_bounce_t = 0.0
    _dots = 0
    _dot_timer = 0.0

    # 生成背景粒子（缓慢上升的光点）
    _particles = []
    for _ in range(40):
        _particles.append({
            'x': random.uniform(0, logic_w),
            'y': random.uniform(0, logic_h),
            'vx': random.uniform(-8, 8),
            'vy': random.uniform(-18, -5),
            'size': random.uniform(1.5, 4.5),
            'alpha': random.randint(40, 180),
            'color': random.choice(PARTICLE_COLORS),
            'phase': random.uniform(0, math.pi * 2),
        })

    # 生成星空背景（小闪烁点）
    _stars = []
    for _ in range(100):
        _stars.append({
            'x': random.uniform(0, logic_w),
            'y': random.uniform(0, logic_h),
            'size': random.uniform(0.5, 2.0),
            'twinkle_speed': random.uniform(2.0, 6.0),
            'twinkle_phase': random.uniform(0, math.pi * 2),
        })


def set_progress(value: float):
    """设置加载进度 0.0~1.0。"""
    global _progress
    _progress = max(0.0, min(1.0, value))


def mark_loading_complete():
    """标记加载完成。"""
    global _loading_complete, _progress
    _progress = 1.0
    _loading_complete = True


def is_loading_complete() -> bool:
    return _loading_complete


def run_loading_screen(surf: pygame.Surface, dt: float, logic_w: int, logic_h: int):
    """渲染一帧加载界面。返回 True 表示加载完成可以切换页面。"""
    global _tip_alpha, _tip_transition, _tip_index
    global _logo_bounce_t, _dots, _dot_timer

    elapsed = time.time() - _start_time

    # 背景渐变（深空蓝紫）
    bg = pygame.Surface((logic_w, logic_h))
    for y in range(0, logic_h, 2):
        t = y / logic_h
        r = int(8 + t * 15)
        g = int(6 + t * 10)
        b = int(20 + t * 35)
        pygame.draw.rect(bg, (r, g, b), (0, y, logic_w, 2))
    surf.blit(bg, (0, 0))

    # ---- 星空闪烁 ----
    for star in _stars:
        twinkle = (math.sin(elapsed * star['twinkle_speed'] + star['twinkle_phase']) + 1) / 2
        alpha = int(60 + twinkle * 180)
        sx = int(star['x'])
        sy = int(star['y'])
        ss = int(star['size'] * (0.8 + twinkle * 0.4))
        if 0 <= sx < logic_w and 0 <= sy < logic_h:
            star_surf = pygame.Surface((ss * 2 + 2, ss * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surf, (200, 210, 255, alpha), (ss + 1, ss + 1), ss)
            surf.blit(star_surf, (sx - ss, sy - ss))

    # ---- 背景粒子 ----
    for p in _particles:
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        # 循环：超出屏幕后重置
        if p['y'] < -20:
            p['y'] = logic_h + 20
            p['x'] = random.uniform(0, logic_w)
        if p['x'] < -20:
            p['x'] = logic_w + 20
        if p['x'] > logic_w + 20:
            p['x'] = -20

        # 缓慢波动
        wave = math.sin(elapsed * 2.5 + p['phase']) * 0.3
        alpha = int(p['alpha'] * (0.6 + wave))
        px, py = int(p['x']), int(p['y'])
        if 0 <= px < logic_w and 0 <= py < logic_h:
            p_surf = pygame.Surface((int(p['size'] * 2 + 2), int(p['size'] * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], max(0, min(255, alpha))),
                              (int(p['size'] + 1), int(p['size'] + 1)), max(1, int(p['size'])))
            surf.blit(p_surf, (px - int(p['size']), py - int(p['size'])))

    # ---- 游戏 Logo ----
    _logo_bounce_t += dt
    logo_bounce = math.sin(_logo_bounce_t * 2.5) * 6
    logo_y = int(logic_h * 0.22) + logo_bounce

    # Logo 光晕
    glow_alpha = int(60 + math.sin(elapsed * 1.8) * 25)
    glow_surf = pygame.Surface((500, 160), pygame.SRCALPHA)
    for i in range(6):
        r = 240 - i * 30
        alpha = glow_alpha - i * 12
        color = (220, 180, 60, max(0, alpha))
        pygame.draw.rect(glow_surf, color,
                        (30 - i * 5, 10 - i * 5, 440 + i * 10, 140 + i * 10),
                        border_radius=15 + i * 3)
    surf.blit(glow_surf, (logic_w // 2 - 250, logo_y - 80))

    # 中文标题
    gt.draw(surf, "像素漫游者", logic_w // 2, logo_y - 42, 60,
            (255, 220, 80), "sans", center_x=True, shadow=True,
            shadow_color=(40, 30, 10))
    # 英文副标题
    gt.draw(surf, "Pixel Roamer", logic_w // 2, logo_y + 24, 28,
            (180, 200, 220), "mono", center_x=True, shadow=True)

    # ---- 加载进度条 ----
    bar_w = 500
    bar_h = 18
    bar_x = (logic_w - bar_w) // 2
    bar_y = int(logic_h * 0.58)
    border_r = 9

    # 进度条背景
    pygame.draw.rect(surf, (15, 15, 38), (bar_x, bar_y, bar_w, bar_h), border_radius=border_r)
    pygame.draw.rect(surf, (50, 50, 80), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=border_r)

    # 进度条填充
    fill_w = int((bar_w - 4) * _progress)
    if fill_w > 0:
        # 渐变色：进度低时蓝，进度高时金
        r = int(60 + _progress * 180)
        g = int(140 + _progress * 80)
        b = int(220 - _progress * 120)
        fill_color = (min(255, r), min(255, g), min(255, b))
        fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4)
        pygame.draw.rect(surf, fill_color, fill_rect, border_radius=border_r - 2)

        # 填充高光
        if fill_w > 10:
            hl_h = (bar_h - 4) // 2
            hl_rect = pygame.Rect(bar_x + 6, bar_y + 3, fill_w - 12, max(1, hl_h))
            hl_surf = pygame.Surface((max(1, fill_w - 12), max(1, hl_h)), pygame.SRCALPHA)
            hl_surf.fill((255, 255, 255, 50))
            surf.blit(hl_surf, hl_rect)

    # 进度条流动光点
    if _progress < 1.0:
        glow_x = bar_x + fill_w
        glow_surf_bar = pygame.Surface((60, bar_h), pygame.SRCALPHA)
        for i in range(15):
            a = int(100 - i * 6.5)
            r = 8 - i * 0.5
            pygame.draw.circle(glow_surf_bar, (255, 255, 255, max(0, a)),
                             (30, bar_h // 2), max(1, int(r)))
        surf.blit(glow_surf_bar, (glow_x - 30, bar_y))

    # 百分比文字
    pct_text = f"{int(_progress * 100)}%"
    gt.draw(surf, pct_text, logic_w // 2, bar_y + bar_h + 8, 24,
            (200, 200, 220), "mono", center_x=True, shadow=True)

    # ---- 加载动画点 ----
    _dot_timer += dt
    if _dot_timer > 0.4:
        _dot_timer = 0.0
        _dots = (_dots + 1) % 4
    dots_text = "加载中" + "." * _dots
    gt.draw(surf, dots_text, logic_w // 2, bar_y + bar_h + 36, 18,
            (150, 150, 180), "sans", center_x=True)

    # ---- 提示文字（淡入淡出） ----
    _tip_transition += dt
    if _tip_transition > 4.5:
        # 切换提示
        _tip_transition = 0.0
        _tip_index = (_tip_index + 1) % len(TIPS)
        # 避免连续相同
        if len(TIPS) > 1:
            while _tip_index == (_tip_index - 1) % len(TIPS):
                _tip_index = random.randint(0, len(TIPS) - 1)

    # 淡入淡出曲线
    fade_progress = _tip_transition / 4.5
    if fade_progress < 0.15:
        _tip_alpha = fade_progress / 0.15 * 200
    elif fade_progress > 0.85:
        _tip_alpha = (1.0 - fade_progress) / 0.15 * 200
    else:
        _tip_alpha = 200
    _tip_alpha = max(0, min(200, _tip_alpha))

    tip_text = TIPS[_tip_index]
    gt.draw(surf, tip_text, logic_w // 2, logic_h - 75, 18,
            (180, 200, 230, int(_tip_alpha)), "sans", center_x=True, shadow=True)

    # ---- 底部信息 ----
    gt.draw(surf, f"v1.0  |  开发者：浪兮", logic_w // 2, logic_h - 38, 15,
            (100, 100, 130), "mono", center_x=True)

    # ---- 加载完成提示 ----
    if _loading_complete and elapsed > 0.5:
        complete_alpha = min(255, int((elapsed - 0.5) * 400))
        pulse = math.sin(elapsed * 4.0) * 0.3 + 0.7
        r = int(100 * pulse)
        g = int(255 * pulse)
        b = int(140 * pulse)
        gt.draw(surf, "按 Enter 或 点击 开始游戏",
                logic_w // 2, bar_y + bar_h + 60, 22,
                (r, g, b), "sans", center_x=True, shadow=True)

    return _loading_complete
