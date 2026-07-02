from __future__ import annotations

import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
from camera import Camera
from creature import Player
from maps import get_map, list_maps, load_map_config, save_map_config, get_map_folder_name, rename_map
from costumes import COSTUMES, DEFAULT_COSTUME_ID, list_costumes, render_costume_direct
import sfx
import game_text as gt

# ===================== 游戏元信息 =====================
GAME_NAME_CN = "像素漫游者"
GAME_NAME_EN = "Pixel Roamer"
GAME_DEV = "浪兮"

# ===================== 初始化 =====================
pygame.mixer.pre_init(22050, -16, 1, 512)  # 音频预初始化
pygame.init()

# 禁用IME中文输入法，避免字母键轮询失效
pygame.key.stop_text_input()
pygame.key.set_repeat(0, 0)

win_surface = pygame.display.set_mode((INIT_WIN_W, INIT_WIN_H), pygame.RESIZABLE)
pygame.display.set_caption(f"{GAME_NAME_CN}  {GAME_NAME_EN}")
clock = pygame.time.Clock()
logic_surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))

win_w, win_h = INIT_WIN_W, INIT_WIN_H
scale = 1.0
draw_offset_x = 0
draw_offset_y = 0
current_fps = DEFAULT_FPS


def update_scale_param():
    global scale, draw_offset_x, draw_offset_y
    scale_w = win_w / LOGIC_WIDTH
    scale_h = win_h / LOGIC_HEIGHT
    scale = min(scale_w, scale_h)
    real_draw_w = LOGIC_WIDTH * scale
    real_draw_h = LOGIC_HEIGHT * scale
    draw_offset_x = (win_w - real_draw_w) / 2
    draw_offset_y = (win_h - real_draw_h) / 2


update_scale_param()

# ===================== 字体尺寸常量 =====================
FONT56 = 56
FONT40 = 40
FONT34 = 34
FONT28 = 28
FONT24 = 24
FONT20 = 20

# ===================== 页面管理 =====================
PAGE_DEV = 0
PAGE_INIT = 1
PAGE_HOME = 2
PAGE_WORLD = 3
PAGE_INFINITE_WORLD = 4
PAGE_SETTING = 5

page = PAGE_DEV  # 默认进入开发者界面
_page_need_launch = True
_page_launch_kwargs = {}

_world_initialized = False  # 跟踪世界是否已初始化（从设置返回时跳过重新初始化）


def set_page(page_id: int, **kwargs):
    """设置当前页面，立即执行对应启动器。"""
    global page, _page_need_launch, _page_launch_kwargs
    # 离开世界页面时停止音乐
    if page == PAGE_WORLD and page_id != PAGE_WORLD:
        pygame.mixer.music.stop()
    page = page_id
    _page_launch_kwargs = kwargs
    _page_need_launch = False
    _dispatch_launcher()


def set_page_no_launch(page_id: int):
    """切换页面但不触发启动器（用于返回暂停状态）。"""
    global page, _page_need_launch
    page = page_id
    _page_need_launch = False


def set_page_by_name(name: str, **kwargs):
    """按名称设置页面（兼容旧接口）。"""
    ids = {"dev": 0, "init": 1, "home": 2, "world": 3, "infinite_world": 4, "setting": 5}
    set_page(ids[name], **kwargs)


# ===================== 页面启动器 =====================
_current_map = None
camera = None
player1 = None
p1_keys = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_SPACE,
    "up": pygame.K_w,
    "down": pygame.K_s,
    "fly": pygame.K_f,
}
_dev_selected_id = None
_dev_edit_mode = False        # 开发者地图编辑模式
_dev_edit_field_idx = 0       # 当前编辑字段索引
_dev_edit_dirty = False       # 是否有未保存的修改
_dev_edit_config = {}         # 当前编辑中的配置
_dev_renaming = False         # 是否正在重命名地图

# 游戏状态
_game_over = False
_game_win = False
_game_timer = 0.0             # 累计游戏时间（秒）
_player_lives_left = 0        # 剩余复活次数


def _init_dev_selection():
    global _dev_selected_id
    maps_dict = list_maps()
    if not maps_dict:
        _dev_selected_id = None
        return
    ids = sorted(maps_dict.keys())
    if _dev_selected_id not in ids:
        _dev_selected_id = ids[0]


def launch_dev():
    """启动器：开发者界面。"""
    global _dev_selected_id
    _init_dev_selection()
    # [log removed]


def launch_world(map_id: int):
    """启动器：游戏世界。传入地图ID，加载地图、创建相机和玩家。"""
    global _current_map, camera, player1, _world_initialized
    _current_map = get_map(map_id)
    camera = Camera(LOGIC_WIDTH, LOGIC_HEIGHT, _current_map)
    sp_x, sp_y = _current_map.spawn_points

    # 读取玩家配置（若有），全部传入 Player 构造函数
    cfg = getattr(_current_map, 'player_config', {})
    player1 = Player(
        player_id=0, player_name="玩家1",
        spawn_x=float(sp_x), spawn_y=float(sp_y),
        key_bind=p1_keys,
        hp_max=cfg.get("hp_max", 150),
        shield=cfg.get("shield", 0),
        w=cfg.get("w", 0.8),
        h=cfg.get("h", 1.8),
        v_max=cfg.get("v_max", 36.5),
        v_jump=cfg.get("v_jump", 11.5),
        f_x=cfg.get("f_x", 0.985),
        f_y=cfg.get("f_y", 1.0),
        phys_atk=cfg.get("phys_atk", 10),
        magic_atk=cfg.get("magic_atk", 0),
        phys_res=cfg.get("phys_res", 0),
        magic_res=cfg.get("magic_res", 0),
        phys_pen=cfg.get("phys_pen", 0),
        magic_pen=cfg.get("magic_pen", 0),
        k_res=cfg.get("k_res", 150),
        dr=cfg.get("dr", 0),
        stamina_max=cfg.get("stamina_max", 200),
    )
    # 加载时装
    player1.costume_id = cfg.get("costume_id", DEFAULT_COSTUME_ID)

    # 初始化游戏状态
    global _game_over, _game_win, _game_timer, _player_lives_left
    _game_over = False
    _game_win = False
    _game_timer = 0.0
    _player_lives_left = getattr(_current_map, 'lives', 0)

    # 播放地图专属音乐
    _play_world_music(_current_map)

    _world_initialized = True


def _play_world_music(world):
    """根据地图配置播放背景音乐。"""
    import os
    music_name = getattr(world, 'music', '')
    if music_name:
        music_path = os.path.join(os.path.dirname(__file__), 'music', music_name)
        if os.path.isfile(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(sfx.get_music_volume())
                pygame.mixer.music.play(-1)  # 循环播放
            except pygame.error:
                pass  # 文件无效则跳过
    else:
        pygame.mixer.music.stop()


def launch_setting(from_page: int = PAGE_WORLD):
    """启动器：设置页面。保存来源页面，以便返回。"""
    # from_page 存储在 kwargs 中，由调用方传入
    pass


def launch_default(page_id: int):
    """占位启动器。"""
    pass


# ===================== 绘图辅助 =====================
def draw_text_center(surf, font_size, text, y, color=(255,255,255), shadow=False):
    """居中绘制（game_text），返回下一行的 y 坐标。"""
    _, h = gt.draw(surf, text, LOGIC_WIDTH // 2, y, font_size, color,
                   "sans", center_x=True, shadow=shadow)
    return y + h + 4


def draw_text_left(surf, font_size, text, x, y, color=(255,255,255), shadow=False):
    """左对齐绘制，返回下一行的 y 坐标。"""
    _, h = gt.draw(surf, text, x, y, font_size, color, "sans", shadow=shadow)
    return y + h + 4


def draw_text_right(surf, font_size, text, x_right, y, color=(255,255,255), shadow=False):
    """右对齐绘制，x_right 为文字右边缘的 x 坐标。"""
    _, h = gt.draw(surf, text, x_right, y, font_size, color, "sans",
                   right_x=True, shadow=shadow)
    return y + h + 4


# ===================== HP / 体力条 / 坐标 绘制 =====================
_damage_flash_timer = 0.0       # 受伤黄色闪烁计时器
_damage_flash_duration = 0.3    # 闪烁持续时间（秒）
_stamina_flash_timer = 0.0      # 体力不足闪烁计时器
_stamina_flash_duration = 1.0   # 体力闪烁持续1秒
_prev_hp = None                 # 上一帧血量（用于检测受伤）
_prev_score = 0                 # 上一帧积分（检测拾取）
_prev_alive = True              # 上一帧存活状态（检测死亡）
_win_played = False             # 通关音效是否已播放
_death_played = False           # 死亡音效是否已播放

BAR_X, BAR_Y = 24, 16
BAR_W, BAR_H = 280, 32
BAR_TEXT_H = 22                  # 文字高度（用于垂直居中）
BORDER_R = 6
PAD = 4
BAR_GAP = 5                     # 血条与体力条间距


def _draw_single_bar(surf, x, y, w, h, pad, border_r,
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


def draw_hp_bar(surf, player, dt: float):
    """绘制血条（固定宽度，含护盾按比例压缩）。"""
    global _damage_flash_timer, _prev_hp

    # 检测受伤
    if _prev_hp is not None and player.hp < _prev_hp - 0.5:
        _damage_flash_timer = _damage_flash_duration
        sfx.play_hurt()
    _prev_hp = player.hp

    # 衰减闪烁计时器
    if _damage_flash_timer > 0:
        _damage_flash_timer -= dt

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

    _draw_single_bar(surf, BAR_X, BAR_Y, BAR_W, BAR_H, PAD, BORDER_R,
                     hp_ratio, shield_ratio, hp_color, shield_color,
                     _damage_flash_timer, _damage_flash_duration)

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


def draw_stamina_bar(surf, player, dt: float):
    """在血条下方绘制体力条。体力不足时闪烁。"""
    global _stamina_flash_timer
    stam_y = BAR_Y + BAR_H + BAR_GAP
    stamina = getattr(player, 'stamina', 100.0)
    stamina_max = max(1, getattr(player, 'stamina_max', 100.0))
    ratio = max(0.0, min(1.0, stamina / stamina_max))

    # 衰减闪烁计时器
    if _stamina_flash_timer > 0:
        _stamina_flash_timer -= dt

    # 体力颜色：低体力红 → 橙 → 蓝
    if ratio < 0.25:
        stam_color = (200, 60, 40)
    elif ratio < 0.5:
        t = (ratio - 0.25) / 0.25
        stam_color = (int(200 - 40 * t), int(60 + 100 * t), int(40 + 80 * t))
    else:
        stam_color = (60, 140, 220)

    _draw_single_bar(surf, BAR_X, stam_y, BAR_W, BAR_H, PAD, BORDER_R,
                     ratio, 0.0, stam_color, None, 0.0, 0.0)

    # 体力不足时边框闪3次（16Hz，均匀间隔，仅亮帧覆盖）
    if _stamina_flash_timer > 0:
        tick = int(_stamina_flash_timer * 16)
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


def draw_player_info(surf, player, dt: float):
    """在体力条下方绘制复活次数（命数）。"""
    global _player_lives_left
    if _player_lives_left > 0:
        stam_y = BAR_Y + BAR_H + BAR_GAP
        info_y = stam_y + BAR_H + 6
        if _player_lives_left <= 5:
            heart_text = "H " * _player_lives_left
        else:
            heart_text = f"H x{_player_lives_left}"
        gt.draw(surf, heart_text.strip(), BAR_X + BAR_W + 10, info_y, 20, (255, 60, 60), "mono", shadow=True)


# ===================== Buff 状态显示区 =====================
# Buff 图标位置缓存（用于鼠标悬浮检测）
_buff_icon_rects = []  # [(ix, iy, p, buff_instance), ...]

def _format_time(seconds: float) -> str:
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


def draw_buff_status(surf, player, dt: float):
    """在屏幕左下方绘制当前活跃 buff 的状态图标（含进度扇形和层数）。"""
    global _buff_icon_rects
    _buff_icon_rects = []

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
        _buff_icon_rects.append((ix, iy, p, b))

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
    logic_mx = (mx - draw_offset_x) / scale
    logic_my = (my - draw_offset_y) / scale

    for ix, iy, p, b in _buff_icon_rects:
        if ix <= logic_mx <= ix + p and iy <= logic_my <= iy + p:
            btype = b.buff_type
            if btype is None:
                continue
            name_text = btype.name2 or btype.name
            if b.duration is not None:
                time_text = _format_time(max(0, b.duration))
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


# ===================== 濒死滤镜 =====================
def draw_near_death_vignette(surf, player):
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


# ===================== 设置页面 =====================
_FPS_OPTIONS = [30, 60, 90, 120, 150, 180, 210, 240]
_setting_selected_row = 0
_setting_selected_fps_idx = 1
_setting_from_page = PAGE_DEV
_setting_fps_just_autodetected = False
_SETTING_ROWS = 4  # 0:FPS  1:自动检测  2:音效音量  3:音乐音量


def _run_fps_benchmark() -> int:
    """快速测试设备帧率能力，返回推荐的 fps 上限（30 的整数倍）。"""
    test_surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    test_clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    frames = 0
    while pygame.time.get_ticks() - start < 800:
        test_surface.fill((0, 0, 0))
        for i in range(50):
            pygame.draw.rect(test_surface, (i * 5 % 255, i * 3 % 255, i * 7 % 255),
                             (i * 20 % LOGIC_WIDTH, i * 15 % LOGIC_HEIGHT, 80, 60))
        test_clock.tick(1000)
        frames += 1
    measured = frames / 0.8 * 0.9
    best = 30
    for opt in _FPS_OPTIONS:
        if opt <= measured:
            best = opt
    return best


def _draw_volume_bar(surf, x, y, w, h, value, is_active):
    """绘制音量条：value 0~1。"""
    bg = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surf, (20, 20, 35), bg, border_radius=4)
    if is_active:
        pygame.draw.rect(surf, (100, 180, 255), bg, 2, border_radius=4)
    fill_w = int((w - 4) * value)
    if fill_w > 0:
        fill_color = (80, 200, 120) if is_active else (60, 150, 90)
        pygame.draw.rect(surf, fill_color, (x + 2, y + 2, fill_w, h - 4), border_radius=2)


def run_setting_page(dt: float):
    """设置页面渲染。"""
    global _setting_selected_row, _setting_selected_fps_idx, _setting_fps_just_autodetected

    sfx_vol = sfx.get_sfx_volume()
    mus_vol = sfx.get_music_volume()

    logic_surface.fill((20, 20, 40))

    y = 60
    y = draw_text_center(logic_surface, FONT40, "设置 (SETTING)", y, (100, 200, 255)) + 24

    # 辅助：绘制一行
    def _row(label, value_text, row_idx, hint="← → 调整"):
        nonlocal y
        is_active = (_setting_selected_row == row_idx)
        row_h = 46
        bg = pygame.Rect(200, y - 2, LOGIC_WIDTH - 400, row_h)
        pygame.draw.rect(logic_surface, (40, 40, 70) if is_active else (25, 25, 45), bg, border_radius=4)
        if is_active:
            pygame.draw.rect(logic_surface, (100, 180, 255), bg, 2, border_radius=4)
        draw_text_left(logic_surface, FONT28, label, 240, y + 7, (255, 255, 255))
        draw_text_right(logic_surface, FONT24, value_text, LOGIC_WIDTH - 270, y + 9, (220, 220, 220))
        draw_text_right(logic_surface, FONT20, hint, LOGIC_WIDTH - 240, y + 9, (140, 140, 160))
        y += row_h + 6

    # 0: FPS
    fps_label = "自动" if _setting_fps_just_autodetected else str(_FPS_OPTIONS[_setting_selected_fps_idx])
    _row(f"帧率上限", f"{fps_label} FPS", 0)

    # 1: 自动检测
    _row("自动检测设备最佳帧率", "Enter 执行", 1, "Enter")

    # 2: 音效音量
    _row("音效音量", f"{int(sfx_vol * 100)}%", 2)
    _draw_volume_bar(logic_surface, 340, y - 48, LOGIC_WIDTH - 680, 16, sfx_vol, _setting_selected_row == 2)

    # 3: 音乐音量（预留）
    _row("音乐音量", f"{int(mus_vol * 100)}%", 3)
    _draw_volume_bar(logic_surface, 340, y - 48, LOGIC_WIDTH - 680, 16, mus_vol, _setting_selected_row == 3)

    if _setting_fps_just_autodetected:
        draw_text_center(logic_surface, FONT20, f"检测结果：{fps_label} FPS 已自动设定", LOGIC_HEIGHT - 86, (100, 255, 100))

    draw_text_center(logic_surface, FONT20, "↑ ↓ 选择    ← → 调整    Enter 确认    Esc 返回", LOGIC_HEIGHT - 58, (140, 140, 180))


def handle_setting_input(event):
    """处理设置页面的键盘事件。"""
    global _setting_selected_row, _setting_selected_fps_idx, current_fps
    global _setting_fps_just_autodetected, _setting_from_page

    if event.type != pygame.KEYDOWN:
        return

    from sfx import play_click

    if event.key == pygame.K_UP:
        _setting_selected_row = (_setting_selected_row - 1) % _SETTING_ROWS
        _setting_fps_just_autodetected = False
        play_click()
    elif event.key == pygame.K_DOWN:
        _setting_selected_row = (_setting_selected_row + 1) % _SETTING_ROWS
        _setting_fps_just_autodetected = False
        play_click()
    elif event.key == pygame.K_LEFT:
        if _setting_selected_row == 0:
            _setting_selected_fps_idx = (_setting_selected_fps_idx - 1) % len(_FPS_OPTIONS)
            _setting_fps_just_autodetected = False
            current_fps = _FPS_OPTIONS[_setting_selected_fps_idx]
            play_click()
        elif _setting_selected_row == 2:
            sfx.set_sfx_volume(sfx.get_sfx_volume() - 0.05)
            play_click()
        elif _setting_selected_row == 3:
            sfx.set_music_volume(sfx.get_music_volume() - 0.05)
            pygame.mixer.music.set_volume(sfx.get_music_volume())
            play_click()
    elif event.key == pygame.K_RIGHT:
        if _setting_selected_row == 0:
            _setting_selected_fps_idx = (_setting_selected_fps_idx + 1) % len(_FPS_OPTIONS)
            _setting_fps_just_autodetected = False
            current_fps = _FPS_OPTIONS[_setting_selected_fps_idx]
            play_click()
        elif _setting_selected_row == 2:
            sfx.set_sfx_volume(sfx.get_sfx_volume() + 0.05)
            play_click()
        elif _setting_selected_row == 3:
            sfx.set_music_volume(sfx.get_music_volume() + 0.05)
            pygame.mixer.music.set_volume(sfx.get_music_volume())
            play_click()
    elif event.key == pygame.K_RETURN:
        if _setting_selected_row == 1:
            detected = _run_fps_benchmark()
            try:
                _setting_selected_fps_idx = _FPS_OPTIONS.index(detected)
            except ValueError:
                _setting_selected_fps_idx = 1
            _setting_fps_just_autodetected = True
            current_fps = detected
    elif event.key == pygame.K_ESCAPE:
        set_page_no_launch(_setting_from_page)


# ===================== Dev 页面 =====================
# 可编辑字段定义：(属性路径, 显示名, 类型, 默认值, 步进/选项)
# type: "float" | "int" | "bool" | "str"
# 对于 str 类型，步进字段为选项列表
_EDITABLE_FIELDS = [
    # ---- World 属性 ----
    ("world.gravity",        "重力",               "float", -6.5,    0.5),
    ("world.mode",           "游戏模式",           "str",   "free",    ["free", "explore", "score_timed", "score_target"]),
    ("world.lives",          "复活次数(0=无限)",    "int",   0,        1),
    ("world.score_goal",     "积分目标",           "int",   100,      50),
    ("world.time_limit",     "时间限制(秒,0=无限)",  "float", 0.0,      30.0),
    ("world.music",          "背景音乐(文件名)",     "str",   "",       None),
    ("world.loop_x",         "X轴循环",            "bool",  False,    None),
    ("world.loop_y",         "Y轴循环",            "bool",  False,    None),
    ("world.edge_behavior",  "边界行为",           "str",   "solid",  ["solid", "void"]),
    ("world.view_blocks_h",  "视野(格高)",         "float", 15.0,     1.0),
    ("world.void_limit",     "虚空边界距离",       "int",   20,       5),
    ("world.fill_color",     "背景填充色(R,G,B)",   "str",  "30,30,30", None),
    ("world.default_block_id","默认方块ID",        "int",   0,        1),
    # ---- Player 属性 ----
    ("player.hp_max",        "最大血量",           "float", 150.0,    10.0),
    ("player.v_max",         "最大速度",           "float", 36.5,     1.0),
    ("player.v_jump",        "跳跃速度",           "float", 11.5,     1.0),
    ("player.stamina_max",   "最大体力",           "float", 200.0,    10.0),
    ("player.phys_atk",      "物理攻击",           "float", 10.0,     5.0),
    ("player.magic_atk",     "魔法攻击",           "float", 0.0,      5.0),
    ("player.phys_res",      "物理抗性",           "float", 0.0,      5.0),
    ("player.magic_res",     "魔法抗性",           "float", 0.0,      5.0),
    ("player.phys_pen",      "物理穿透",           "float", 0.0,      5.0),
    ("player.magic_pen",     "魔法穿透",           "float", 0.0,      5.0),
    ("player.k_res",         "抗性系数",           "float", 150.0,    10.0),
    ("player.dr",            "减伤率",             "float", 0.0,      0.05),
    ("player.f_x",           "X轴摩擦系数",        "float", 0.985,    0.005),
    ("player.f_y",           "Y轴摩擦系数",        "float", 1.0,      0.005),
    ("player.shield",        "初始护盾",           "float", 0.0,      5.0),
    ("player.w",             "玩家宽度",           "float", 0.8,      0.1),
    ("player.h",             "玩家高度",           "float", 1.8,      0.1),
    ("player.costume_id",    "时  装",            "int",   1,        1),
]

# 精确输入状态
_dev_inputting = False       # 是否处于精确输入模式
_dev_input_text = ""         # 输入缓冲区

# ===================== 方块/ Buff 预览器状态 =====================
_dev_block_browser = False        # 是否处于方块预览模式
_dev_block_browser_mode = "grid"
_dev_block_browser_cursor = 0
_dev_block_browser_scroll = 0
_dev_block_browser_show_name2 = False
_dev_block_detail_id = None
_dev_block_page_offset = 0

_dev_buff_browser = False         # 是否处于 Buff 预览模式
_dev_buff_browser_mode = "grid"
_dev_buff_browser_cursor = 0
_dev_buff_browser_scroll = 0
_dev_buff_browser_show_name2 = False
_dev_buff_detail_id = None


# ---- 方块亮点选择器（算法自动匹配，非预存）----
def _get_block_highlights(bt) -> list:
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


def _draw_block_preview(surf, bt, x, y, size):
    """绘制单个方块的预览缩略图。"""
    from pattern import render_block_pattern
    preview = pygame.Surface((size, size))
    preview.fill(bt.color)
    if bt.pattern is not None:
        render_block_pattern(preview, bt, 0, 0, size, size)
    surf.blit(preview, (x, y))
    # 边框
    pygame.draw.rect(surf, (100, 100, 120), (x, y, size, size), 1)


def _run_block_browser(logic_surface, dt):
    """方块浏览器渲染（网格/列表模式）。"""
    global _dev_block_browser_cursor, _dev_block_browser_scroll
    from block_types_data import BLOCK_TYPES
    all_ids = sorted(BLOCK_TYPES.keys())
    if not all_ids:
        return

    # 详情页
    if _dev_block_detail_id is not None:
        _run_block_detail(logic_surface, dt)
        return

    # 标题 (5%-15% 区域)
    TITLE_Y = int(LOGIC_HEIGHT * 0.06) - 18  # 标题中心在6%
    HINT_Y = int(LOGIC_HEIGHT * 0.975)
    title = f"方块预览器 [{_dev_block_browser_mode.upper()}]"
    gt.draw(logic_surface, title, LOGIC_WIDTH // 2, TITLE_Y, 36,
                        (255, 255, 200), "sans", shadow=True, center_x=True)
    mode_hint = "Tab:切换视图  N:名称切换  Enter:详情  B/Esc:返回"
    gt.draw(logic_surface, mode_hint, LOGIC_WIDTH // 2, HINT_Y, 18,
                        (140, 160, 200), "sans", shadow=True, center_x=True)

    name_key = "name2" if _dev_block_browser_show_name2 else "name"
    cursor = _dev_block_browser_cursor
    CONTENT_TOP2 = int(LOGIC_HEIGHT * 0.12)
    CONTENT_H = int(LOGIC_HEIGHT * 0.85)  # 12%-97%

    if _dev_block_browser_mode == "grid":
        COLS = 8
        cell_w = 170
        cell_h = CONTENT_H // 4  # 每页4排
        preview_size = 80
        start_x = (LOGIC_WIDTH - COLS * cell_w) // 2
        start_y = CONTENT_TOP2
        rows = (len(all_ids) + COLS - 1) // COLS

        visible_rows = 4
        cursor_row = cursor // COLS
        if cursor_row < _dev_block_browser_scroll:
            _dev_block_browser_scroll = cursor_row
        if cursor_row >= _dev_block_browser_scroll + visible_rows:
            _dev_block_browser_scroll = max(0, cursor_row - visible_rows + 1)
        _dev_block_browser_scroll = max(0, min(_dev_block_browser_scroll, max(0, rows - visible_rows)))

        for row in range(_dev_block_browser_scroll, min(_dev_block_browser_scroll + visible_rows, rows)):
            for col in range(COLS):
                idx = row * COLS + col
                if idx >= len(all_ids):
                    break
                bid = all_ids[idx]
                bt = BLOCK_TYPES[bid]
                cx = start_x + col * cell_w
                cy = start_y + (row - _dev_block_browser_scroll) * cell_h

                if idx == cursor:
                    pygame.draw.rect(logic_surface, (80, 140, 255),
                                    (cx - 3, cy - 3, cell_w - 4, cell_h - 4), 2, border_radius=4)

                # 预览图
                px = cx + (cell_w - preview_size) // 2
                _draw_block_preview(logic_surface, bt, px, cy + 4, preview_size)

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

        if cursor < _dev_block_browser_scroll:
            _dev_block_browser_scroll = cursor
        if cursor >= _dev_block_browser_scroll + visible_rows:
            _dev_block_browser_scroll = max(0, cursor - visible_rows + 1)
        _dev_block_browser_scroll = max(0, min(_dev_block_browser_scroll, max(0, len(all_ids) - visible_rows)))

        for i in range(_dev_block_browser_scroll,
                       min(_dev_block_browser_scroll + visible_rows, len(all_ids))):
            idx = i
            bid = all_ids[idx]
            bt = BLOCK_TYPES[bid]
            cy = start_y + (i - _dev_block_browser_scroll) * row_h

            if idx == cursor:
                pygame.draw.rect(logic_surface, (60, 60, 100), (40, cy, LOGIC_WIDTH - 80, row_h))
                pygame.draw.rect(logic_surface, (100, 200, 255), (40, cy, LOGIC_WIDTH - 80, row_h), 2)

            # 左侧预览
            _draw_block_preview(logic_surface, bt, 56, cy + (row_h - preview_size) // 2, preview_size)

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
            highlights = _get_block_highlights(bt)
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


def _run_block_detail(logic_surface, dt):
    """方块详情页：上中下3区 — 标题 | 左中右3栏 | 操作指引。5%边距。"""
    from block_types_data import BLOCK_TYPES
    bid = _dev_block_detail_id
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
    _draw_block_preview(logic_surface, bt, col1_x + (cw - preview_size) // 2, CONTENT_TOP + 10, preview_size)

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
                # 少量指令：每条一行，中号字体
                VFS = 16; VLH = 19
                max_chars = (cw - 14) // 8
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
                    if len(text) > max_chars:
                        text = text[:max_chars-2] + ".."
                    gt.draw(logic_surface, text, col3_x + 6, cy2, VFS, (150, 170, 210), "sans")
            else:
                # 大量指令：与位图相同的紧凑换行模式
                flat = "[" + ", ".join(
                    f"fill({c[1][0]},{c[1][1]},{c[1][2]})" if c[0] == "fill"
                    else f"rect({c[1]},{c[2]},{c[3]},{c[4]},({c[5][0]},{c[5][1]},{c[5][2]}))" if c[0] == "rect"
                    else f"circle({c[1]},{c[2]},{c[3]},({c[4][0]},{c[4][1]},{c[4][2]}))" if c[0] == "circle"
                    else str(c)
                    for c in cmds[:24]
                ) + (", ..." if len(cmds) > 24 else "") + "]"
                chars_per_line = (cw - 20) // 7
                bj = 0
                while bj < len(flat):
                    chunk = flat[bj:bj + chars_per_line]
                    if ry + 28 + (bj // chars_per_line) * 15 > CONTENT_BOT - 10: break
                    gt.draw(logic_surface, chunk, col3_x + 6, ry + 28 + (bj // chars_per_line) * 15, 13, (150, 170, 210), "sans")
                    bj += chars_per_line
    else:
        gt.draw(logic_surface, f"编码: 无  底色: {bt.color}",
                            col3_x + 6, ry, 19, (160, 180, 200), "sans")

    # ==== 下区：操作指引 (92%-95%) ====
    gt.draw(logic_surface, "B / Esc  返回列表", LOGIC_WIDTH // 2, HINT_TOP + 4, 18,
                        (140, 160, 200), "sans", shadow=True, center_x=True)

def _handle_block_browser_input(event):
    """处理方块浏览器的键盘事件。"""
    global _dev_block_browser, _dev_block_browser_mode, _dev_block_browser_cursor
    global _dev_block_browser_scroll, _dev_block_browser_show_name2
    global _dev_block_detail_id, _dev_block_page_offset
    from block_types_data import BLOCK_TYPES

    if event.type != pygame.KEYDOWN:
        return

    all_ids = sorted(BLOCK_TYPES.keys())
    if not all_ids:
        return

    # 详情页内
    if _dev_block_detail_id is not None:
        if event.key in (pygame.K_ESCAPE, pygame.K_b):
            _dev_block_detail_id = None
        return

    if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
        _dev_block_browser = False
        _dev_block_browser_cursor = 0
        _dev_block_browser_scroll = 0
        return

    if event.key == pygame.K_TAB:
        _dev_block_browser_mode = "list" if _dev_block_browser_mode == "grid" else "grid"
        _dev_block_browser_scroll = 0

    elif event.key == pygame.K_n:
        _dev_block_browser_show_name2 = not _dev_block_browser_show_name2

    elif event.key == pygame.K_RETURN:
        bid = all_ids[_dev_block_browser_cursor]
        _dev_block_detail_id = bid

    elif event.key == pygame.K_UP:
        if _dev_block_browser_mode == "grid":
            COLS = 8
            _dev_block_browser_cursor = max(0, _dev_block_browser_cursor - COLS)
        else:
            _dev_block_browser_cursor = max(0, _dev_block_browser_cursor - 1)

    elif event.key == pygame.K_DOWN:
        if _dev_block_browser_mode == "grid":
            COLS = 8
            _dev_block_browser_cursor = min(len(all_ids) - 1, _dev_block_browser_cursor + COLS)
        else:
            _dev_block_browser_cursor = min(len(all_ids) - 1, _dev_block_browser_cursor + 1)

    elif event.key == pygame.K_LEFT:
        if _dev_block_browser_mode == "grid":
            _dev_block_browser_cursor = max(0, _dev_block_browser_cursor - 1)
        else:
            # 列表模式左键快速翻页
            visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
            _dev_block_browser_cursor = max(0, _dev_block_browser_cursor - visible_rows)
            _dev_block_browser_scroll = max(0, _dev_block_browser_scroll - visible_rows)

    elif event.key == pygame.K_RIGHT:
        if _dev_block_browser_mode == "grid":
            _dev_block_browser_cursor = min(len(all_ids) - 1, _dev_block_browser_cursor + 1)
        else:
            visible_rows = max(1, (LOGIC_HEIGHT - 56 - 50) // 64)
            _dev_block_browser_cursor = min(len(all_ids) - 1, _dev_block_browser_cursor + visible_rows)
            _dev_block_browser_scroll = min(
                max(0, len(all_ids) - visible_rows),
                _dev_block_browser_scroll + visible_rows)


# ===================== Buff 预览器 =====================
def _run_buff_browser(logic_surface, dt):
    """Buff 预览器渲染。"""
    global _dev_buff_browser_scroll
    import buff_data
    from buff_system import BUFF_TYPES
    all_ids = sorted(BUFF_TYPES.keys())
    if not all_ids:
        return

    if _dev_buff_detail_id is not None:
        _run_buff_detail(logic_surface, dt)
        return

    TITLE_Y = int(LOGIC_HEIGHT * 0.06) - 18  # 标题中心在6%
    HINT_Y = int(LOGIC_HEIGHT * 0.975)
    CONTENT_TOP2 = int(LOGIC_HEIGHT * 0.12)
    CONTENT_H = int(LOGIC_HEIGHT * 0.85)

    title = f"Buff 预览器 [{_dev_buff_browser_mode.upper()}]"
    gt.draw(logic_surface, title, LOGIC_WIDTH // 2, TITLE_Y, 36,
                        (255, 255, 200), "sans", shadow=True, center_x=True)
    mode_hint = "Tab:切换视图  N:名称切换  Enter:详情  U/Esc:返回"
    gt.draw(logic_surface, mode_hint, LOGIC_WIDTH // 2, HINT_Y, 18,
                        (140, 160, 200), "sans", shadow=True, center_x=True)

    name_key = "name2" if _dev_buff_browser_show_name2 else "name"
    cursor = _dev_buff_browser_cursor

    if _dev_buff_browser_mode == "grid":
        COLS = 8
        cell_w = 170
        cell_h = CONTENT_H // 4
        preview_size = 80
        start_x = (LOGIC_WIDTH - COLS * cell_w) // 2
        start_y = CONTENT_TOP2
        rows = (len(all_ids) + COLS - 1) // COLS
        visible_rows = 4

        cursor_row = cursor // COLS
        if cursor_row < _dev_buff_browser_scroll:
            _dev_buff_browser_scroll = cursor_row
        if cursor_row >= _dev_buff_browser_scroll + visible_rows:
            _dev_buff_browser_scroll = max(0, cursor_row - visible_rows + 1)
        _dev_buff_browser_scroll = max(0, min(_dev_buff_browser_scroll, max(0, rows - visible_rows)))

        for row in range(_dev_buff_browser_scroll, min(_dev_buff_browser_scroll + visible_rows, rows)):
            for col in range(COLS):
                idx = row * COLS + col
                if idx >= len(all_ids): break
                bid = all_ids[idx]
                bt = BUFF_TYPES[bid]
                cx = start_x + col * cell_w
                cy = start_y + (row - _dev_buff_browser_scroll) * cell_h
                if idx == cursor:
                    pygame.draw.rect(logic_surface, (80, 140, 255),
                                    (cx - 3, cy - 3, cell_w - 4, cell_h - 4), 2, border_radius=4)
                px = cx + (cell_w - preview_size) // 2
                _draw_buff_icon(logic_surface, bt, px, cy + 4, preview_size)
                label = f"{bid}.{getattr(bt, name_key, bt.name)}"
                gt.draw(logic_surface, label, cx + cell_w // 2, cy + preview_size + 22, 20,
                                    (220, 220, 220), "sans", shadow=True, center_x=True)
    else:
        row_h = CONTENT_H // 8; preview_size = 60; start_y = CONTENT_TOP2
        visible_rows = 8
        cat_names = {"positive": "有益", "neutral": "中性", "negative": "有害"}

        if cursor < _dev_buff_browser_scroll:
            _dev_buff_browser_scroll = cursor
        if cursor >= _dev_buff_browser_scroll + visible_rows:
            _dev_buff_browser_scroll = max(0, cursor - visible_rows + 1)
        _dev_buff_browser_scroll = max(0, min(_dev_buff_browser_scroll, max(0, len(all_ids) - visible_rows)))

        for i in range(_dev_buff_browser_scroll, min(_dev_buff_browser_scroll + visible_rows, len(all_ids))):
            bid = all_ids[i]
            bt = BUFF_TYPES[bid]
            cy = start_y + (i - _dev_buff_browser_scroll) * row_h
            if i == cursor:
                pygame.draw.rect(logic_surface, (60, 60, 100), (40, cy, LOGIC_WIDTH - 80, row_h))
                pygame.draw.rect(logic_surface, (100, 200, 255), (40, cy, LOGIC_WIDTH - 80, row_h), 2)
            _draw_buff_icon(logic_surface, bt, 56, cy + (row_h - preview_size) // 2, preview_size)
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


def _run_buff_detail(logic_surface, dt):
    """Buff 详情页：3栏布局，参照方块详情。"""
    import buff_data
    from buff_system import BUFF_TYPES
    bid = _dev_buff_detail_id
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
    _draw_buff_icon(logic_surface, bt, col1_x + (cw - preview_size) // 2, CONTENT_TOP + 10, preview_size)

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
            gt.draw(logic_surface, f"编码: 矢量  画布: {vw}x{vh}", col3_x + 6, ry, 28, (200, 210, 240), "sans")
            for j, cmd in enumerate(cmds):
                cy2 = ry + 30 + j * 26
                if cy2 > CONTENT_BOT - 16: break
                ctype = cmd[0]
                if ctype == "fill": c1 = cmd[1]; text = f"fill({c1[0]},{c1[1]},{c1[2]})"
                elif ctype == "rect": text = f"rect({cmd[1]},{cmd[2]},{cmd[3]},{cmd[4]},{cmd[5]})"
                elif ctype == "circle": text = f"circle({cmd[1]},{cmd[2]},{cmd[3]},{cmd[4]})"
                else: text = str(cmd)
                gt.draw(logic_surface, text, col3_x + 6, cy2, 21, (150, 170, 210), "sans")
    else:
        gt.draw(logic_surface, f"编码: 无  纯色图标", col3_x + 6, ry, 19, (160, 180, 200), "sans")

    # ==== 下区 ====
    gt.draw(logic_surface, "U / Esc  返回列表", LOGIC_WIDTH // 2, HINT_TOP + 4, 18,
                        (140, 160, 200), "sans", shadow=True, center_x=True)



def _draw_buff_icon(surf, bt, x, y, size):
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


def _handle_buff_browser_input(event):
    """处理 Buff 预览器的键盘事件。"""
    global _dev_buff_browser, _dev_buff_browser_mode, _dev_buff_browser_cursor
    global _dev_buff_browser_scroll, _dev_buff_browser_show_name2, _dev_buff_detail_id
    import buff_data
    from buff_system import BUFF_TYPES

    if event.type != pygame.KEYDOWN: return
    all_ids = sorted(BUFF_TYPES.keys())
    if not all_ids: return

    if _dev_buff_detail_id is not None:
        if event.key in (pygame.K_ESCAPE, pygame.K_u):
            _dev_buff_detail_id = None
        return

    if event.key in (pygame.K_ESCAPE, pygame.K_u):
        _dev_buff_browser = False
        _dev_buff_browser_cursor = 0
        return

    if event.key == pygame.K_TAB:
        _dev_buff_browser_mode = "list" if _dev_buff_browser_mode == "grid" else "grid"
    elif event.key == pygame.K_n:
        _dev_buff_browser_show_name2 = not _dev_buff_browser_show_name2
    elif event.key == pygame.K_RETURN:
        _dev_buff_detail_id = all_ids[_dev_buff_browser_cursor]
    elif event.key == pygame.K_UP:
        _dev_buff_browser_cursor = max(0, _dev_buff_browser_cursor - (8 if _dev_buff_browser_mode == "grid" else 1))
    elif event.key == pygame.K_DOWN:
        _dev_buff_browser_cursor = min(len(all_ids) - 1, _dev_buff_browser_cursor + (8 if _dev_buff_browser_mode == "grid" else 1))
    elif event.key == pygame.K_LEFT:
        _dev_buff_browser_cursor = max(0, _dev_buff_browser_cursor - 1)
    elif event.key == pygame.K_RIGHT:
        _dev_buff_browser_cursor = min(len(all_ids) - 1, _dev_buff_browser_cursor + 1)


def _get_edit_config(map_id: int) -> dict:
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
    defaults = {
        "hp_max": 150.0, "v_max": 36.5, "v_jump": 11.5, "stamina_max": 200.0,
        "phys_atk": 10.0, "magic_atk": 0.0, "phys_res": 0.0, "magic_res": 0.0,
        "phys_pen": 0.0, "magic_pen": 0.0, "k_res": 150.0, "dr": 0.0,
        "f_x": 0.985, "f_y": 0.9965, "shield": 0.0, "w": 0.8, "h": 1.8,
        "costume_id": 1,
    }
    saved_player = saved.get("player", {})
    for key, default_val in defaults.items():
        config["player"][key] = saved_player.get(key, default_val)

    # 已保存的 world 配置覆盖
    saved_world = saved.get("world", {})
    config["world"].update(saved_world)
    return config


def _get_field_value(config: dict, field_path: str):
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


def _set_field_value(config: dict, field_path: str, value):
    """设置配置字典中的字段值。"""
    parts = field_path.split(".")
    obj = config
    for p in parts[:-1]:
        if p not in obj:
            obj[p] = {}
        obj = obj[p]
    obj[parts[-1]] = value


def _get_map_type_label(m) -> str:
    """获取地图类型标签。"""
    if m.loop_x and m.loop_y:
        return "循环XY"
    elif m.loop_x:
        return "循环X"
    elif m.loop_y:
        return "循环Y"
    else:
        return "有限"


def run_dev_page(dt: float):
    """开发者界面：查询地图、选择地图、编辑属性、启动游戏、预览器。"""
    global _dev_edit_mode, _dev_edit_field_idx, _dev_edit_dirty, _dev_edit_config
    global _dev_inputting, _dev_input_text
    global _dev_block_browser, _dev_buff_browser

    # 方块/ Buff 预览器模式
    if _dev_block_browser:
        logic_surface.fill((20, 20, 40))
        _run_block_browser(logic_surface, dt)
        return
    if _dev_buff_browser:
        logic_surface.fill((20, 20, 40))
        _run_buff_browser(logic_surface, dt)
        return

    logic_surface.fill((20, 20, 40))

    maps_dict = list_maps()
    map_ids = sorted(maps_dict.keys())

    # 标题
    y = 30
    y = draw_text_center(logic_surface, FONT56, f"{GAME_NAME_CN}", y, (255, 220, 100)) + 4
    y = draw_text_center(logic_surface, FONT28, f"{GAME_NAME_EN}", y, (200, 180, 100)) + 8
    y = draw_text_center(logic_surface, FONT20, f"开发者：{GAME_DEV}", y, (140, 140, 160)) + 16

    if _dev_edit_mode and _dev_selected_id is not None:
        # ========== 编辑模式 ==========
        global _dev_renaming
        y = draw_text_center(logic_surface, FONT34, f"编辑地图属性 — ID={_dev_selected_id}", y, (100, 255, 150)) + 4

        # ---- 重命名行 ----
        map_name = maps_dict.get(_dev_selected_id, "?")
        if _dev_renaming:
            rename_hint = f"新名称: {_dev_input_text}▌  (Enter确认 Esc取消)"
            y = draw_text_center(logic_surface, FONT24, rename_hint, y, (255, 220, 100)) + 4
        else:
            rename_line = f"地图名: {map_name}  [按 R 重命名]"
            y = draw_text_center(logic_surface, FONT24, rename_line, y, (200, 200, 220)) + 4

        if _dev_inputting and not _dev_renaming:
            hint = "输入数值后 Enter 确认  Esc 取消"
        elif not _dev_renaming:
            hint = "↑↓ 选择  ← → 快速调整  Enter 精确输入  S 保存  R 改名  Esc 返回"
        else:
            hint = ""
        if hint:
            y = draw_text_center(logic_surface, FONT20, hint, y, (180, 180, 180)) + 12

        # 可见行数
        visible_start = max(0, _dev_edit_field_idx - 8)
        visible_end = min(len(_EDITABLE_FIELDS), visible_start + 18)
        # 确保当前选中在可见范围内
        if _dev_edit_field_idx < visible_start:
            visible_start = _dev_edit_field_idx
            visible_end = min(len(_EDITABLE_FIELDS), visible_start + 18)
        elif _dev_edit_field_idx >= visible_end:
            visible_end = min(len(_EDITABLE_FIELDS), _dev_edit_field_idx + 1)
            visible_start = max(0, visible_end - 18)

        # 滚动指示
        if visible_start > 0:
            draw_text_center(logic_surface, FONT20, "▲ 更多 ↑", y - 6, (100, 100, 120))

        for i in range(visible_start, visible_end):
            field_path, label, ftype, default, step = _EDITABLE_FIELDS[i]
            val = _get_field_value(_dev_edit_config, field_path)
            is_sel = (i == _dev_edit_field_idx)

            row_h = 36
            row_y = y
            # 行背景
            if is_sel:
                highlight_color = (100, 200, 255) if not _dev_inputting else (255, 200, 50)
                pygame.draw.rect(logic_surface, (50, 50, 90), (200, row_y - 1, LOGIC_WIDTH - 400, row_h))
                pygame.draw.rect(logic_surface, highlight_color, (200, row_y - 1, LOGIC_WIDTH - 400, row_h), 2)

            # 字段名和类型标签
            type_tag = {"float": "F", "int": "I", "bool": "B", "str": "S"}.get(ftype, "?")
            type_color = {"float": (150,200,255), "int": (255,200,150), "bool": (200,255,150), "str": (255,200,255)}.get(ftype, (150,150,150))
            label_text = f"{label}"
            draw_text_left(logic_surface, FONT24 if is_sel else FONT20,
                           label_text, 220, row_y + 6,
                           (255, 255, 180) if is_sel else (200, 200, 200))
            # 类型小标签
            gt.draw(logic_surface, type_tag, 540, row_y + 8, FONT20, type_color, "sans")

            # 值显示
            if is_sel and _dev_inputting:
                # 精确输入模式：显示光标
                display_text = _dev_input_text + "▌"
                val_color = (255, 255, 100)
            else:
                if ftype == "bool":
                    display_text = "是" if val else "否"
                elif ftype == "float":
                    display_text = f"{val:.3f}".rstrip("0").rstrip(".")
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

            draw_text_right(logic_surface, FONT24 if is_sel else FONT20,
                            display_text, LOGIC_WIDTH - 220, row_y + 6, val_color)
            y += row_h + 2

        if visible_end < len(_EDITABLE_FIELDS):
            draw_text_center(logic_surface, FONT20, "▼ 更多 ↓", y + 4, (100, 100, 120))

        y = LOGIC_HEIGHT - 70
        status_color = (100, 255, 100) if _dev_edit_dirty else (150, 150, 150)
        draw_text_center(logic_surface, FONT20,
                         "已修改，按 S 保存" if _dev_edit_dirty else "无修改",
                         y, status_color)
    else:
        # ========== 地图列表模式 ==========
        y = draw_text_center(logic_surface, FONT34, "开发者界面 (DEV)", y, (100, 200, 255)) + 12
        y = draw_text_center(logic_surface, FONT24, "↑↓ 选择  Enter 启动  E 编辑属性  R 刷新", y, (180, 180, 180)) + 30

        # 表头
        col_x_id = 80
        col_x_name = 160
        col_x_mode = 400
        col_x_type = 580
        col_x_size = 730
        header_y = y
        pygame.draw.rect(logic_surface, (30, 30, 55), (40, y - 2, LOGIC_WIDTH - 80, 30))
        draw_text_left(logic_surface, FONT20, "ID", col_x_id, y + 2, (150, 150, 150))
        draw_text_left(logic_surface, FONT20, "地图名称", col_x_name, y + 2, (150, 150, 150))
        draw_text_left(logic_surface, FONT20, "游戏模式", col_x_mode, y + 2, (150, 150, 150))
        draw_text_left(logic_surface, FONT20, "循环", col_x_type, y + 2, (150, 150, 150))
        draw_text_left(logic_surface, FONT20, "尺寸", col_x_size, y + 2, (150, 150, 150))
        y = header_y + 34

        for mid in map_ids:
            name = maps_dict[mid]
            try:
                m = get_map(mid)
                info_size = f"{m.width}×{m.height}"
                info_type = _get_map_type_label(m)
                info_mode = m.mode
            except Exception:
                info_size = "?"
                info_type = "?"
                info_mode = "?"

            is_selected = (mid == _dev_selected_id)
            row_h = 36
            if is_selected:
                pygame.draw.rect(logic_surface, (50, 50, 90), (40, y - 1, LOGIC_WIDTH - 80, row_h))
                pygame.draw.rect(logic_surface, (100, 200, 255), (40, y - 1, LOGIC_WIDTH - 80, row_h), 2)

            font = FONT28 if is_selected else FONT24
            sel_color = (255, 255, 180)
            norm_color = (200, 200, 200)
            c = lambda b: sel_color if b and is_selected else norm_color

            draw_text_left(logic_surface, font, str(mid), col_x_id, y + 3, c(True))
            draw_text_left(logic_surface, font, name, col_x_name, y + 3, c(True))
            # 游戏模式用颜色标注
            mode_color_map = {"free": (180,200,220), "explore": (255,200,150),
                              "score_timed": (255,150,150), "score_target": (150,255,150)}
            mc = mode_color_map.get(info_mode, (200,200,200))
            if not is_selected: mc = tuple(int(c*0.75) for c in mc)
            draw_text_left(logic_surface, font, info_mode, col_x_mode, y + 3, mc)
            # 循环类型
            type_color_map = {"有限": (180, 200, 220), "循环X": (150, 255, 200),
                              "循环Y": (150, 200, 255), "循环XY": (255, 200, 150)}
            tc = type_color_map.get(info_type, (200, 200, 200))
            if not is_selected: tc = tuple(int(c*0.75) for c in tc)
            draw_text_left(logic_surface, font, info_type, col_x_type, y + 3, tc)
            draw_text_left(logic_surface, font, info_size, col_x_size, y + 3, c(False))
            y += row_h

    # 底部
    if _dev_selected_id is not None:
        if _dev_edit_mode:
            draw_text_center(logic_surface, FONT20,
                             "S: 保存到硬盘  |  Enter: 精确输入当前字段  |  Esc: 返回列表",
                             LOGIC_HEIGHT - 24, (140, 180, 255))
        else:
            draw_text_center(logic_surface, FONT24,
                             f"当前选中: ID={_dev_selected_id}  |  Enter启动 E编辑 B方块预览 UBuff预览",
                             LOGIC_HEIGHT - 50, (140, 180, 255))


def _parse_input_value(text: str, ftype: str):
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


def handle_dev_input(event):
    """处理 dev 页面的键盘事件。"""
    global _dev_selected_id, _dev_edit_mode, _dev_edit_field_idx
    global _dev_edit_dirty, _dev_edit_config
    global _dev_inputting, _dev_input_text
    global _dev_block_browser, _dev_buff_browser

    if event.type != pygame.KEYDOWN:
        return

    if _dev_block_browser:
        _handle_block_browser_input(event)
        return
    if _dev_buff_browser:
        _handle_buff_browser_input(event)
        return

    maps_dict = list_maps()
    ids = sorted(maps_dict.keys())
    if not ids:
        return

    # ========== B键方块预览器 / U键Buff预览器 ==========
    if event.key == pygame.K_b and not _dev_edit_mode and not _dev_inputting:
        _dev_block_browser = True
        return
    if event.key == pygame.K_u and not _dev_edit_mode and not _dev_inputting:
        _dev_buff_browser = True
        return

    # ========== 编辑模式按键 ==========
    global _dev_renaming
    if _dev_edit_mode and _dev_selected_id is not None:
        # ---- 重命名模式（优先级最高）----
        if _dev_renaming:
            if event.key == pygame.K_ESCAPE:
                _dev_renaming = False
                _dev_input_text = ""
            elif event.key == pygame.K_RETURN:
                new_name = _dev_input_text.strip()
                if new_name:
                    ok = rename_map(_dev_selected_id, new_name)
                    if ok:
                        _init_dev_selection()
                        _dev_edit_config = _get_edit_config(_dev_selected_id)
                _dev_renaming = False
                _dev_input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                _dev_input_text = _dev_input_text[:-1]
            elif event.unicode and len(event.unicode) > 0:
                ch = event.unicode
                if ch.isprintable() and ord(ch) >= 32 and ch not in '/\\:*?\"<>|':
                    _dev_input_text += ch
            return

        field_path, label, ftype, default, step = _EDITABLE_FIELDS[_dev_edit_field_idx]

        # ---- 精确输入模式 ----
        if _dev_inputting:
            if event.key == pygame.K_ESCAPE:
                # 取消输入
                _dev_inputting = False
                _dev_input_text = ""
            elif event.key == pygame.K_RETURN:
                # 确认输入
                val = _parse_input_value(_dev_input_text, ftype)
                if val is not None:
                    # 对 str 类型校验选项
                    if ftype == "str" and isinstance(step, list) and val not in step:
                        pass  # 无效选项，忽略
                    else:
                        _set_field_value(_dev_edit_config, field_path, val)
                        _dev_edit_dirty = True
                _dev_inputting = False
                _dev_input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                _dev_input_text = _dev_input_text[:-1]
            elif event.key == pygame.K_DELETE:
                _dev_input_text = ""
            # ==== 小键盘支持 ====
            elif event.key == pygame.K_KP0:
                _dev_input_text += "0"
            elif event.key == pygame.K_KP1:
                _dev_input_text += "1"
            elif event.key == pygame.K_KP2:
                _dev_input_text += "2"
            elif event.key == pygame.K_KP3:
                _dev_input_text += "3"
            elif event.key == pygame.K_KP4:
                _dev_input_text += "4"
            elif event.key == pygame.K_KP5:
                _dev_input_text += "5"
            elif event.key == pygame.K_KP6:
                _dev_input_text += "6"
            elif event.key == pygame.K_KP7:
                _dev_input_text += "7"
            elif event.key == pygame.K_KP8:
                _dev_input_text += "8"
            elif event.key == pygame.K_KP9:
                _dev_input_text += "9"
            elif event.key == pygame.K_KP_PERIOD:
                if ftype in ("float", "int"):
                    _dev_input_text += "."
            elif event.key == pygame.K_KP_MINUS:
                if ftype in ("float", "int"):
                    _dev_input_text += "-"
            elif event.unicode and len(event.unicode) > 0:
                # 过滤控制字符
                ch = event.unicode
                if ch.isprintable() and ord(ch) >= 32:
                    # bool 类型特殊处理：允许输入 true/false/是/否 等
                    if ftype == "bool":
                        if ch.isalpha():
                            _dev_input_text += ch
                    elif ftype == "str":
                        _dev_input_text += ch
                    else:
                        # 数字类型：允许数字、负号、小数点
                        if ch.isdigit() or ch in ".-":
                            _dev_input_text += ch
            return

        # ---- 常规编辑模式按键 ----
        if event.key == pygame.K_ESCAPE:
            _dev_edit_mode = False
            _dev_edit_dirty = False
        elif event.key == pygame.K_r:
            # 启动重命名
            _dev_renaming = True
            _dev_input_text = maps_dict.get(_dev_selected_id, "")
            _dev_inputting = False
        elif event.key == pygame.K_UP:
            _dev_edit_field_idx = (_dev_edit_field_idx - 1) % len(_EDITABLE_FIELDS)
        elif event.key == pygame.K_DOWN:
            _dev_edit_field_idx = (_dev_edit_field_idx + 1) % len(_EDITABLE_FIELDS)
        elif event.key == pygame.K_RETURN:
            # 进入精确输入模式
            val = _get_field_value(_dev_edit_config, field_path)
            if ftype == "bool":
                _dev_input_text = "true" if val else "false"
            elif ftype == "str":
                _dev_input_text = str(val)
            elif ftype == "int":
                _dev_input_text = str(int(val))
            else:
                _dev_input_text = f"{val:.3f}".rstrip("0").rstrip(".")
            _dev_inputting = True
        elif event.key == pygame.K_LEFT:
            try:
                if ftype == "bool":
                    _set_field_value(_dev_edit_config, field_path, False)
                elif ftype == "str":
                    cur = _get_field_value(_dev_edit_config, field_path)
                    if isinstance(step, list) and step:
                        try:
                            idx = step.index(cur)
                        except ValueError:
                            idx = 0
                        idx = (idx - 1) % len(step)
                        _set_field_value(_dev_edit_config, field_path, step[idx])
                    # str 无有效选项列表时不操作
                elif ftype == "float":
                    val = _get_field_value(_dev_edit_config, field_path)
                    if val is not None and isinstance(step, (int, float)):
                        val = float(val) - float(step)
                        _set_field_value(_dev_edit_config, field_path, val)
                elif ftype == "int":
                    val = _get_field_value(_dev_edit_config, field_path)
                    if val is not None and isinstance(step, (int, float)):
                        val = int(val) - int(step)
                        _set_field_value(_dev_edit_config, field_path, val)
                _dev_edit_dirty = True
            except Exception:
                pass
        elif event.key == pygame.K_RIGHT:
            try:
                if ftype == "bool":
                    _set_field_value(_dev_edit_config, field_path, True)
                elif ftype == "str":
                    cur = _get_field_value(_dev_edit_config, field_path)
                    if isinstance(step, list) and step:
                        try:
                            idx = step.index(cur)
                        except ValueError:
                            idx = -1
                        idx = (idx + 1) % len(step)
                        _set_field_value(_dev_edit_config, field_path, step[idx])
                    # str 无有效选项列表时不操作
                elif ftype == "float":
                    val = _get_field_value(_dev_edit_config, field_path)
                    if val is not None and isinstance(step, (int, float)):
                        val = float(val) + float(step)
                        _set_field_value(_dev_edit_config, field_path, val)
                elif ftype == "int":
                    val = _get_field_value(_dev_edit_config, field_path)
                    if val is not None and isinstance(step, (int, float)):
                        val = int(val) + int(step)
                        _set_field_value(_dev_edit_config, field_path, val)
                _dev_edit_dirty = True
            except Exception:
                pass
        elif event.key == pygame.K_s:
            # 保存到硬盘
            save_map_config(_dev_selected_id, _dev_edit_config)
            _dev_edit_dirty = False
            # [log removed]
        elif event.key == pygame.K_RETURN:
            # 在编辑模式中 Enter 也保存并启动
            if _dev_edit_dirty:
                save_map_config(_dev_selected_id, _dev_edit_config)
                _dev_edit_dirty = False
                # [log removed]
            _dev_edit_mode = False
            set_page(PAGE_WORLD, map_id=_dev_selected_id)
        return

    # ========== 列表模式按键 ==========
    if event.key == pygame.K_RETURN:
        if _dev_selected_id is not None:
            set_page(PAGE_WORLD, map_id=_dev_selected_id)
    elif event.key == pygame.K_e:
        if _dev_selected_id is not None:
            _dev_edit_mode = True
            _dev_edit_field_idx = 0
            _dev_edit_dirty = False
            _dev_edit_config = _get_edit_config(_dev_selected_id)
            # [log removed]
    elif event.key == pygame.K_UP:
        idx = ids.index(_dev_selected_id) if _dev_selected_id in ids else 0
        idx = (idx - 1) % len(ids)
        _dev_selected_id = ids[idx]
    elif event.key == pygame.K_DOWN:
        idx = ids.index(_dev_selected_id) if _dev_selected_id in ids else 0
        idx = (idx + 1) % len(ids)
        _dev_selected_id = ids[idx]
    elif event.key == pygame.K_r:
        _init_dev_selection()
        # [log removed]


# ===================== 页面启动器注册表 =====================
_LAUNCHERS = {
    PAGE_DEV: launch_dev,
    PAGE_INIT: launch_default,
    PAGE_HOME: launch_default,
    PAGE_WORLD: launch_world,
    PAGE_INFINITE_WORLD: launch_default,
    PAGE_SETTING: launch_setting,
}


def _dispatch_launcher():
    """根据当前 page 和 _page_launch_kwargs 调用对应启动器。"""
    launcher = _LAUNCHERS.get(page, launch_default)
    launcher(**_page_launch_kwargs)


# 初始化：启动 dev 页面
_page_launch_kwargs = {}
_dispatch_launcher()

# ===================== 主循环 =====================
running = True
jump_pressed = False
f = 0

while running:
    dt = clock.tick(current_fps) / 1000.0

    # ----- 事件处理 -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            win_w, win_h = event.w, event.h
            win_surface = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
            update_scale_param()
            if _current_map is not None:
                _current_map.invalidate_chunks()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                current_fps = min(current_fps + 10, MAX_FPS)
                # [log removed]
            if event.key == pygame.K_F2:
                current_fps = max(current_fps - 10, MIN_FPS)
                # [log removed]

        # 页面分发
        if page == PAGE_DEV:
            handle_dev_input(event)
        elif page == PAGE_WORLD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_page(PAGE_DEV)
                elif event.key == pygame.K_BACKSPACE:
                    _setting_from_page = PAGE_WORLD
                    try:
                        _setting_selected_fps_idx = _FPS_OPTIONS.index(current_fps)
                    except ValueError:
                        _setting_selected_fps_idx = 1
                    _setting_fps_just_autodetected = False
                    _setting_selected_row = 0
                    set_page(PAGE_SETTING)
                elif event.key == player1.key_bind["jump"]:
                    jump_pressed = True
                elif event.key == pygame.K_c:
                    # 切换时装
                    cids = sorted(COSTUMES.keys())
                    try:
                        idx = cids.index(player1.costume_id)
                        idx = (idx + 1) % len(cids)
                    except ValueError:
                        idx = 0
                    player1.costume_id = cids[idx]
                    # [log removed]
                elif event.key == player1.key_bind["fly"]:
                    # 切换飞行模式
                    player1.fly_mode = not player1.fly_mode
                    player1.v_x = 0.0
                    player1.v_y = 0.0
                    player1.is_climbing = False
                    jump_pressed = False
                    # [log removed]
                elif event.key == pygame.K_F5:
                    # 调试：随机获得1-3个未生效的buff
                    import random as _rnd
                    from buff_system import BUFF_TYPES
                    active_ids = {b.buff_id for b in player1.buffs}
                    available = [bid for bid in BUFF_TYPES if bid not in active_ids]
                    if available:
                        n = _rnd.randint(1, min(3, len(available)))
                        chosen = _rnd.sample(available, n)
                        for bid in chosen:
                            bt = BUFF_TYPES[bid]
                            dur = _rnd.uniform(3.0, 15.0)  # 必定有时限，最多15s
                            p0 = _rnd.uniform(1, 30) if _rnd.random() < 0.6 else 0
                            p1 = _rnd.uniform(1, 50) if _rnd.random() < 0.4 else 0
                            player1.apply_buff(bid, (p0, p1), dur)
                elif event.key == player1.key_bind["up"] or event.key == pygame.K_UP:
                    # W/↑键：可攀爬时进入攀爬，攀爬中向上
                    if not player1.fly_mode:
                        if not player1.is_climbing and player1.can_climb:
                            if player1.stamina >= 1.0:
                                player1.try_start_climbing(_current_map)
                            else:
                                _stamina_flash_timer = _stamina_flash_duration
                        elif player1.is_climbing:
                            if player1.stamina >= 1.0:
                                player1.climb_move(1.0)
                            else:
                                player1.stop_climbing()
                                _stamina_flash_timer = _stamina_flash_duration
                elif event.key == player1.key_bind["down"] or event.key == pygame.K_DOWN:
                    # S/↓键：攀爬中则解除
                    if not player1.fly_mode and player1.is_climbing:
                        player1.stop_climbing()
        elif page == PAGE_SETTING:
            handle_setting_input(event)
        else:
            # 占位页面：Enter 返回 dev
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                set_page(PAGE_DEV)

    # ----- 页面逻辑 & 渲染 -----
    if page == PAGE_DEV:
        run_dev_page(dt)

    elif page == PAGE_WORLD:
        keys = pygame.key.get_pressed()

        # ---- 游戏状态检查 ----

        # 计时器
        wmode = _current_map.mode if _current_map else "free"
        if not _game_over and not _game_win:
            _game_timer += dt
            # 限时模式：时间到则失败
            time_limit = getattr(_current_map, 'time_limit', 0.0)
            if wmode == "score_timed" and time_limit > 0 and _game_timer >= time_limit:
                _game_over = True

            # 积分目标模式：达到目标则胜利
            score_goal = getattr(_current_map, 'score_goal', 0)
            if wmode == "score_target" and score_goal > 0 and player1.score >= score_goal:
                _game_win = True

            # 探索模式：触碰终点则胜利
            if wmode == "explore" and player1._reached_end:
                _game_win = True

        # 死亡处理（限复活次数）
        if not player1.alive and not _game_over and not _game_win:
            if _player_lives_left > 0:
                _player_lives_left -= 1
                if _player_lives_left <= 0:
                    _game_over = True
                else:
                    player1.alive = True
                    player1.hp = player1.hp_max
            # lives==0 表示无限复活，on_death 已经重置了

        # ---- Buff 系统 tick ----
        player1.tick_buffs(dt)
        # buff 属性修正
        buf_v_max = player1.get_buff_stat("v_max", player1._base_v_max)
        buf_v_jump = player1.get_buff_stat("v_jump", player1._base_v_jump)
        # 体力恢复速度（动态公式，三层结构）
        stamina_ratio = player1.stamina / max(1, player1.stamina_max)
        hp_ratio = player1.hp / max(1, player1.hp_max)
        stamina_missing = player1.stamina_max - player1.stamina
        base_stam_rec = (
            (1.15 + 5.5 * (1 - stamina_ratio) + 0.85 * hp_ratio) * (0.85 + 0.25 * hp_ratio)
            + 0.035 * stamina_missing
            + 0.15 * ((1 - stamina_ratio) ** 2)
            + 0.35 * ((1 - stamina_ratio) ** 3)
            + 0.65 * ((1 - stamina_ratio) ** 4)
        )
        buf_stam_rec = player1.get_buff_stat("stamina_recovery", base_stam_rec)
        buf_stam_cost = player1.get_buff_stat("stamina_cost", 1.0)
        player1.v_max = buf_v_max
        player1.v_jump = buf_v_jump
        # 控制效果检查（铁意 buff 40 免疫定身/晕眩/压制/反向）
        iron_will = player1.has_buff(40)
        rooted = player1.has_buff(21) and not iron_will
        stunned = player1.has_buff(28) and not iron_will
        grounded = player1.has_buff(27) and not iron_will
        hopping = player1.has_buff(33)
        reversed_ctrl = player1.has_buff(23) and not player1.has_buff(8) and not iron_will

        # ---- 移动物理（游戏结束/胜利时冻结）----
        if not _game_over and not _game_win and not stunned:
            if player1.fly_mode:
                # ---- 飞行模式 ----
                fly_dx, fly_dy = 0.0, 0.0
                if keys[player1.key_bind["left"]] or keys[pygame.K_LEFT]:
                    fly_dx -= 1.0
                if keys[player1.key_bind["right"]] or keys[pygame.K_RIGHT]:
                    fly_dx += 1.0
                if keys[player1.key_bind["up"]] or keys[pygame.K_UP]:
                    fly_dy += 1.0
                if keys[player1.key_bind["down"]] or keys[pygame.K_DOWN]:
                    fly_dy -= 1.0
                # 直接操作坐标
                player1._x += fly_dx * player1.fly_speed * dt
                player1._y += fly_dy * player1.fly_speed * dt
                player1.v_x = 0.0
                player1.v_y = 0.0
                # 钳制在地图边界内（循环世界不钳制）
                if not _current_map.loop_x:
                    player1._x = max(0.5, min(player1._x, _current_map.width - 0.5))
                if not _current_map.loop_y:
                    player1._y = max(0.5, min(player1._y, _current_map.height - 0.5))
                # 更新接触池（用于绘制等）
                grect = player1.get_game_rect()
                player1.contact_pool = set()
                player1.stand_pool = None
            else:
                # ---- 正常模式 ----
                dir_x = 0.0
                if not rooted and not hopping:
                    left_key = keys[player1.key_bind["left"]] or keys[pygame.K_LEFT]
                    right_key = keys[player1.key_bind["right"]] or keys[pygame.K_RIGHT]
                    if reversed_ctrl:
                        left_key, right_key = right_key, left_key
                    if left_key:
                        dir_x -= 0.35
                    if right_key:
                        dir_x += 0.35
                player1.move(dir_x)

                # ---- 攀爬: W/↑向上 ----
                sm = getattr(player1, '_stamina_mult', 1.0)
                silenced = getattr(player1, '_silenced', False)
                climb_up_cost = 14.0 * sm * buf_stam_cost * dt + 0.01
                climb_idle_cost = 3.52 * sm * buf_stam_cost * dt + 0.01
                # 攀爬上边界：人物中心到达梯子顶端（半腰位置），消耗挂住体力
                climb_bound = getattr(player1, '_climb_top_y', None)
                at_climb_bound = False
                if climb_bound is not None and player1.is_climbing:
                    # 仅当靠近边界时吸附（防止远处瞬移）
                    if player1._y >= climb_bound - 0.05 and player1._y <= climb_bound + 2.0:
                        player1._y = climb_bound  # 中心与方块上边界齐平（半腰）
                        player1.v_y = 0.0
                        at_climb_bound = True
                if player1.is_climbing and (keys[player1.key_bind["up"]] or keys[pygame.K_UP]):
                    if at_climb_bound:
                        # 已到顶端，消耗挂住体力
                        if player1.stamina >= climb_idle_cost:
                            if not silenced: player1.consume_stamina(3.52 * sm * buf_stam_cost * dt)
                        else:
                            player1.stop_climbing()
                            _stamina_flash_timer = _stamina_flash_duration
                    elif player1.stamina >= climb_up_cost:
                        player1.climb_move(1.0)
                        if not silenced: player1.consume_stamina(14.0 * sm * buf_stam_cost * dt)
                    else:
                        player1.stop_climbing()
                        _stamina_flash_timer = _stamina_flash_duration
                elif player1.is_climbing:
                    player1.v_y = 0.0
                    if player1.stamina >= climb_idle_cost:
                        if not silenced: player1.consume_stamina(3.52 * sm * buf_stam_cost * dt)
                    else:
                        player1.stop_climbing()
                        _stamina_flash_timer = _stamina_flash_duration

                # ---- 游泳: W/↑向上，攀爬优先 ----
                swimming_now = False
                up_held = keys[player1.key_bind["up"]] or keys[pygame.K_UP]
                if not player1.is_climbing and player1.can_swim and not player1.has_buff(58):
                    if up_held:
                        swim_cost = 21.0 * sm * buf_stam_cost * dt + 0.01
                        if player1.stamina >= swim_cost:
                            # 游泳上边界仅在主动游泳且体力足够时生效
                            swim_bound = getattr(player1, '_swim_top_y', None)
                            at_swim_bound = False
                            if swim_bound is not None:
                                if player1._y >= swim_bound - 0.05 and player1._y <= swim_bound + 2.0:
                                    player1._y = swim_bound  # 中心与水面齐平（半腰）
                                    player1.v_y = 0.0
                                    at_swim_bound = True
                            if at_swim_bound:
                                if not silenced: player1.consume_stamina(21.0 * sm * buf_stam_cost * dt)
                                swimming_now = True
                            else:
                                swim_v = player1._swim_force
                                player1.v_y = swim_v  # 匀速上游
                                if not silenced: player1.consume_stamina(21.0 * sm * buf_stam_cost * dt)
                                swimming_now = True
                        else:
                            # 体力耗尽：不吸附、不游泳，自然下沉
                            _stamina_flash_timer = _stamina_flash_duration

                # ---- 体力恢复（攀爬中/水中按↑时不恢复，防止耗尽-恢复循环） ----
                can_recover = (not player1.is_climbing
                               and not swimming_now
                               and not (player1.can_swim and up_held)
                               and not (player1.can_climb and up_held and not player1.is_climbing))
                if can_recover and player1.stamina < player1.stamina_max:
                    player1.recover_stamina(buf_stam_rec * dt)

                # ---- 上岸：水面上 + 近岸 + 跳跃键 ----
                shore_exit_done = False
                if (jump_pressed and not grounded
                    and player1.can_swim and swimming_now
                    and getattr(player1, '_near_shore', False)
                    and player1.stamina >= 25):
                    _shore_pending = getattr(player1, '_shore_exit_pending', False)
                    if not _shore_pending:
                        # 高速上岸 + 临时空气墙：极速完成，不受液体阻力影响
                        player1.v_y = 22.0  # 高速向上
                        player1.v_x = 0.0
                        if not silenced: player1.consume_stamina(25)
                        player1.apply_buff(58, (), 2.0)
                        player1._shore_exit_pending = 'rise'  # 上升阶段
                        player1._shore_exit_dir = player1._shore_dir
                        player1._shore_exit_bound = getattr(player1, '_swim_top_y', None)
                        sfx.play_jump()
                        shore_exit_done = True
                        jump_pressed = False
                # 上岸后续：空气墙逻辑（到达高度→竖直停，再水平推→到位停）
                _shore_state = getattr(player1, '_shore_exit_pending', False)
                if _shore_state and not shore_exit_done:
                    exit_dir = player1._shore_exit_dir
                    swim_bound = getattr(player1, '_shore_exit_bound', None)
                    feet_y = player1._y - player1._h / 2
                    if _shore_state == 'rise':
                        if swim_bound is not None and feet_y >= swim_bound:
                            # 竖直空气墙：到达水面高度，锁 v_y
                            player1.v_y = 0.0
                            player1.v_x = exit_dir * 10.0  # 高速水平推出
                            player1._shore_exit_pending = 'slide'
                    elif _shore_state == 'slide':
                        if not player1.can_swim:
                            # 水平空气墙：脚下方块不再是水，已到岸上，锁 v_x
                            player1.v_x = 0.0
                            player1._shore_exit_pending = False
                        elif not player1.has_buff(58):
                            player1._shore_exit_pending = False
                    # buff 过期兜底
                    if player1._shore_exit_pending and not player1.has_buff(58):
                        player1._shore_exit_pending = False

                # ---- 正常跳跃 ----
                if jump_pressed and not grounded and not shore_exit_done:
                    can_actually_jump = player1.on_ground or player1.is_climbing
                    jump_cost = 15.0 * sm * buf_stam_cost + 0.01
                    if player1.stamina >= jump_cost:
                        if player1.jump():
                            if not silenced: player1.consume_stamina(15.0 * sm * buf_stam_cost)
                            sfx.play_jump()
                    elif can_actually_jump:
                        _stamina_flash_timer = _stamina_flash_duration
                    jump_pressed = False

                player1.update_physics(dt, _current_map)
                player1.collide_with_world(_current_map, dt)

                # 攀爬中着陆或离开可攀爬方块：自动解除
                if player1.is_climbing and (player1.on_ground or not player1.can_climb):
                    player1.is_climbing = False
                # 上岸后着陆或离开水面：清除上岸待处理状态
                if getattr(player1, '_shore_exit_pending', False):
                    if player1.on_ground or not player1.can_swim:
                        player1._shore_exit_pending = False

        px, py = player1.get_center()
        camera.follow(px, py)

        # 渲染世界
        fill_color = getattr(_current_map, 'fill_color', (30, 30, 30))
        logic_surface.fill(fill_color)
        _current_map.draw(logic_surface, camera)

        # 绘制玩家（时装系统）
        grect = player1.get_game_rect()
        # 时装位图底部有透明行，向下偏移使脚部对齐碰撞箱底部
        shift = grect.h * 0.22
        cam_scale = camera.scale
        sx = (grect.x - camera.x) * cam_scale + camera.logic_width / 2
        sy_top = camera.logic_height / 2 - (grect.y + grect.h - shift - camera.y) * cam_scale
        sw = grect.w * cam_scale
        sh = grect.h * cam_scale
        player_screen_rect = pygame.Rect(sx, sy_top, sw, sh)
        render_costume_direct(logic_surface, player1.costume_id, player_screen_rect)

        # ---- Buff 视线效果（只影响世界/生物，不影响 UI） ----
        # Buff: 发光 (50) 自身发光照亮周围
        if player1.has_buff(50):
            px, py = player1.get_center()
            cam_scale = camera.scale
            sx = (px - camera.x) * cam_scale + camera.logic_width / 2
            sy = camera.logic_height / 2 - (py - camera.y) * cam_scale
            glow_radius = 120
            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                alpha = 30 - i * 3
                r = glow_radius * i / 8
                pygame.draw.circle(glow, (255, 240, 180, max(0, alpha)),
                                   (glow_radius, glow_radius), int(r))
            logic_surface.blit(glow, (sx - glow_radius, sy - glow_radius), special_flags=pygame.BLEND_ADD)

        # Buff: 失明 (24) 屏幕变亮黄色（清明 buff 8 免疫）
        if player1.has_buff(24) and not player1.has_buff(8):
            blind_overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            blind_overlay.fill((255, 240, 80, 140))
            logic_surface.blit(blind_overlay, (0, 0))

        # Buff: 视野受限 (25) 缩小视野半径（清明 buff 8 免疫）
        if player1.has_buff(25) and not player1.has_buff(8):
            vision_radius = 5.0  # 默认半径（格）
            for b in player1.buffs:
                if b.buff_id == 25 and b.params:
                    vision_radius = float(b.params[0])
            px, py = player1.get_center()
            cam_scale = camera.scale
            sx = (px - camera.x) * cam_scale + camera.logic_width / 2
            sy = camera.logic_height / 2 - (py - camera.y) * cam_scale
            vision_radius_px = int(vision_radius * 24 * cam_scale)
            dark = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 220))
            if vision_radius_px > 0:
                pygame.draw.circle(dark, (0, 0, 0, 0), (int(sx), int(sy)), vision_radius_px)
            logic_surface.blit(dark, (0, 0))

        # ---- HP 血条 ----
        # ---- 音效检测 ----
        if _prev_score < player1.score:
            sfx.play_pickup()
        _prev_score = player1.score

        if _prev_alive and not player1.alive and not _death_played:
            sfx.play_death()
            _death_played = True
        if not player1.alive:
            _prev_alive = player1.alive
        else:
            _prev_alive = True
            _death_played = False

        if _game_win and not _win_played:
            sfx.play_win()
            _win_played = True

        draw_hp_bar(logic_surface, player1, dt)
        draw_stamina_bar(logic_surface, player1, dt)
        draw_player_info(logic_surface, player1, dt)

        # ---- 濒死滤镜 ----
        draw_near_death_vignette(logic_surface, player1)
        draw_buff_status(logic_surface, player1, dt)

        # ---- 积分显示（顶部居中）----
        score_text = f"* {player1.score}"
        gt.draw(logic_surface, score_text,
                           LOGIC_WIDTH // 2, 16, 22,
                           (255, 220, 80), "mono", shadow=True, center_x=True)

        # ---- 计时器（积分限时模式）----
        wmode = _current_map.mode if _current_map else "free"
        time_limit = getattr(_current_map, 'time_limit', 0.0)
        if wmode == "score_timed" and time_limit > 0:
            remaining = max(0, time_limit - _game_timer)
            timer_text = f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"
            timer_color = (255, 80, 80) if remaining < 30 else (255, 255, 255)
            gt.draw(logic_surface, timer_text,
                               LOGIC_WIDTH // 2, 42, 20,
                               timer_color, "mono", shadow=True, center_x=True)

        # ---- 积分目标进度（积分目标模式）----
        score_goal = getattr(_current_map, 'score_goal', 0)
        if wmode == "score_target" and score_goal > 0:
            goal_text = f"Goal: {score_goal} ({int(player1.score / max(1, score_goal) * 100)}%)"
            gt.draw(logic_surface, goal_text,
                               LOGIC_WIDTH // 2, 42, 15,
                               (200, 220, 255), "mono", shadow=True, center_x=True)

        # ---- 命数已移至体力条下方 (draw_player_info) ----

        # ---- 游戏结束/胜利叠加层 ----
        if _game_over:
            overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            logic_surface.blit(overlay, (0, 0))
            y = LOGIC_HEIGHT // 2 - 80
            y = draw_text_center(logic_surface, FONT56, "游 戏 失 败", y, (255, 80, 60)) + 16
            if wmode == "score_timed":
                y = draw_text_center(logic_surface, FONT28, f"最终得分: {player1.score}", y, (255, 220, 80)) + 8
            draw_text_center(logic_surface, FONT24, "按 ESC 返回", y + 16, (180, 180, 180))

        elif _game_win:
            overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            logic_surface.blit(overlay, (0, 0))
            y = LOGIC_HEIGHT // 2 - 80
            y = draw_text_center(logic_surface, FONT56, "通 关！", y, (100, 255, 100)) + 16
            y = draw_text_center(logic_surface, FONT28, f"最终得分: {player1.score}", y, (255, 220, 80)) + 8
            draw_text_center(logic_surface, FONT24, "按 ESC 返回", y + 16, (180, 180, 180))

        # 右上角 FPS
        fps_text = f"FPS {int(clock.get_fps())}"
        gt.draw(logic_surface, fps_text,
                           LOGIC_WIDTH - 16, 8, 18,
                           (255, 255, 255), "mono", shadow=True, right_x=True)
        # 坐标（FPS 下方）
        px, py = player1.get_center()
        coord_text = f"({px:.1f}, {py:.1f})"
        gt.draw(logic_surface, coord_text,
                           LOGIC_WIDTH - 16, 30, 16,
                           (200, 210, 230), "mono", shadow=True, right_x=True)

        # 飞行模式指示
        if player1.fly_mode:
            gt.draw(logic_surface, "[FLY]",
                               LOGIC_WIDTH // 2, LOGIC_HEIGHT - 36, 15,
                               (100, 255, 200), "mono", shadow=True, center_x=True)

        f += 1
        state_str = ("飞行" if player1.fly_mode
                     else ("攀爬中" if player1.is_climbing
                           else ("可攀爬" if player1.can_climb
                                 else ("地面" if player1.on_ground else "浮空"))))
        # [log removed]
        costume_name = COSTUMES.get(player1.costume_id, {}).get("name", "?")
        # [log removed]


    elif page == PAGE_SETTING:
        run_setting_page(dt)

    else:
        # 占位页面
        logic_surface.fill((20, 20, 40))
        page_names = {0: "dev", 1: "init", 2: "home", 3: "world", 4: "infinite_world", 5: "setting"}
        draw_text_center(logic_surface, FONT40,
                         f"=== {page_names.get(page, '?')} 页面 ===", 400, (150, 150, 150))
        draw_text_center(logic_surface, FONT24,
                         "（尚未实现，按 Enter 返回开发者界面）", 460, (120, 120, 140))

    # ----- 最终输出 -----
    win_surface.fill((0, 0, 0))
    scaled_surf = pygame.transform.scale(logic_surface, (int(LOGIC_WIDTH * scale), int(LOGIC_HEIGHT * scale)))
    win_surface.blit(scaled_surf, (draw_offset_x, draw_offset_y))
    pygame.display.flip()

pygame.quit()
