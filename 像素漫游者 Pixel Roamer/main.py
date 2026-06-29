from __future__ import annotations

import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
from camera import Camera
from creature import Player
from maps import get_map, list_maps, load_map_config, save_map_config, get_map_folder_name, rename_map
from costumes import COSTUMES, DEFAULT_COSTUME_ID, list_costumes, render_costume_direct
import sfx

# ===================== 游戏元信息 =====================
GAME_NAME_CN = "像素漫游者"
GAME_NAME_EN = "Pixel Roamer"
GAME_DEV = "浪兮"

# ===================== 初始化 =====================
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

# ===================== 中文字体加载 =====================
def _load_cn_font(size: int):
    """加载中文字体，优先使用黑体（simhei.ttf）。"""
    try:
        return pygame.font.Font("C:/Windows/Fonts/simhei.ttf", size)
    except Exception:
        try:
            return pygame.font.Font("C:/Windows/Fonts/msyh.ttc", size)
        except Exception:
            return pygame.font.Font(None, size)


FONT56 = _load_cn_font(56)
FONT40 = _load_cn_font(40)
FONT34 = _load_cn_font(34)
FONT28 = _load_cn_font(28)
FONT24 = _load_cn_font(24)
FONT20 = _load_cn_font(20)

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
        v_jump=cfg.get("v_jump", 26.5),
        f_x=cfg.get("f_x", 0.985),
        f_y=cfg.get("f_y", 0.98),
        phys_atk=cfg.get("phys_atk", 10),
        magic_atk=cfg.get("magic_atk", 0),
        phys_res=cfg.get("phys_res", 0),
        magic_res=cfg.get("magic_res", 0),
        phys_pen=cfg.get("phys_pen", 0),
        magic_pen=cfg.get("magic_pen", 0),
        k_res=cfg.get("k_res", 150),
        dr=cfg.get("dr", 0),
        stamina_max=cfg.get("stamina_max", 100),
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
def draw_text_center(surf, font, text, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    x = (LOGIC_WIDTH - img.get_width()) // 2
    surf.blit(img, (x, y))
    return y + img.get_height()


def draw_text_left(surf, font, text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    surf.blit(img, (x, y))
    return y + img.get_height()


def draw_text_right(surf, font, text, x_right, y, color=(255, 255, 255)):
    """右对齐绘制，x_right 为文字右边缘的 x 坐标。"""
    img = font.render(text, True, color)
    x = x_right - img.get_width()
    surf.blit(img, (x, y))
    return y + img.get_height()


# ===================== HP 血条绘制 =====================
_damage_flash_timer = 0.0       # 受伤黄色闪烁计时器
_damage_flash_duration = 0.3    # 闪烁持续时间（秒）
_prev_hp = None                 # 上一帧血量（用于检测受伤）
_prev_score = 0                 # 上一帧积分（检测拾取）
_prev_alive = True              # 上一帧存活状态（检测死亡）
_win_played = False             # 通关音效是否已播放
_death_played = False           # 死亡音效是否已播放


def draw_hp_bar(surf, player, dt: float):
    """在逻辑画布左上角绘制精美血条（含护盾显示）。"""
    global _damage_flash_timer, _prev_hp

    # 检测受伤
    if _prev_hp is not None and player.hp < _prev_hp - 0.5:
        _damage_flash_timer = _damage_flash_duration
    _prev_hp = player.hp

    # 衰减闪烁计时器
    if _damage_flash_timer > 0:
        _damage_flash_timer -= dt

    BAR_X, BAR_Y = 24, 24
    BAR_W, BAR_H = 280, 34
    BORDER_R = 7
    PAD = 4  # 内边距

    hp = player.hp
    hp_max = player.hp_max
    shield = getattr(player, 'shield', 0.0)

    # 计算扩展宽度（护盾部分可能需要超出 BAR_W）
    has_shield = shield > 0
    total_effective = hp + shield
    if has_shield:
        total_bar_w = int(BAR_W * total_effective / hp_max)
        total_bar_w = max(BAR_W, total_bar_w)  # 至少保留基础宽度
        # 限制最大宽度，防止超出屏幕
        total_bar_w = min(total_bar_w, 700)
    else:
        total_bar_w = BAR_W

    # 背景阴影
    shadow_rect = pygame.Rect(BAR_X + 2, BAR_Y + 2, total_bar_w, BAR_H)
    pygame.draw.rect(surf, (0, 0, 0, 160), shadow_rect, border_radius=BORDER_R)

    # 主背景（深色）
    bg_rect = pygame.Rect(BAR_X, BAR_Y, total_bar_w, BAR_H)
    pygame.draw.rect(surf, (25, 25, 35), bg_rect, border_radius=BORDER_R)

    # ---- HP 填充 ----
    hp_ratio = max(0.0, min(1.0, hp / hp_max))
    # HP 填充宽度：若有护盾且超出上限，HP 按比例压缩
    if has_shield and total_effective > hp_max:
        hp_fill_w = int((total_bar_w - PAD * 2) * hp / total_effective)
    else:
        hp_fill_w = int((BAR_W - PAD * 2) * hp_ratio)
    hp_fill_w = max(0, min(hp_fill_w, total_bar_w - PAD * 2))

    if hp_fill_w > 0:
        fill_rect = pygame.Rect(BAR_X + PAD, BAR_Y + PAD, hp_fill_w, BAR_H - PAD * 2)

        # 受伤闪烁时用黄色覆盖
        if _damage_flash_timer > 0:
            flash_alpha = _damage_flash_timer / _damage_flash_duration
            r = int(220 - 120 * flash_alpha)
            g = int(60 + 140 * flash_alpha)
            b = int(50 + 100 * flash_alpha)
            bar_color = (r, g, b)
        else:
            # 正常渐变色：低血量红，高血量绿
            if hp_ratio < 0.3:
                bar_color = (220, 50, 40)
            elif hp_ratio < 0.6:
                t = (hp_ratio - 0.3) / 0.3
                bar_color = (int(220 - 60 * t), int(50 + 140 * t), int(40))
            else:
                bar_color = (80, 200, 60)

        pygame.draw.rect(surf, bar_color, fill_rect, border_radius=BORDER_R - 2)

        # 血量高光（顶部亮带）
        if hp_fill_w > 16:
            highlight_rect = pygame.Rect(BAR_X + PAD, BAR_Y + PAD, hp_fill_w, (BAR_H - PAD * 2) // 2)
            hl_surf = pygame.Surface((hp_fill_w, (BAR_H - PAD * 2) // 2), pygame.SRCALPHA)
            hl_surf.fill((255, 255, 255, 50))
            surf.blit(hl_surf, highlight_rect)

    # ---- 护盾填充（白色）----
    if has_shield:
        if total_effective <= hp_max:
            # 护盾在标准血条内，HP 右侧
            shield_fill_w = int((BAR_W - PAD * 2) * shield / hp_max)
        else:
            # 护盾部分超出标准血条
            shield_fill_w = int((total_bar_w - PAD * 2) * shield / total_effective)
        shield_fill_w = max(1, min(shield_fill_w, total_bar_w - PAD * 2 - hp_fill_w))

        shield_start_x = BAR_X + PAD + hp_fill_w
        shield_rect = pygame.Rect(shield_start_x, BAR_Y + PAD, shield_fill_w, BAR_H - PAD * 2)
        pygame.draw.rect(surf, (220, 230, 255), shield_rect, border_radius=BORDER_R - 2)

        # 护盾高光
        if shield_fill_w > 8:
            sh_hl = pygame.Rect(shield_start_x, BAR_Y + PAD, shield_fill_w, (BAR_H - PAD * 2) // 2)
            sh_hl_surf = pygame.Surface((shield_fill_w, (BAR_H - PAD * 2) // 2), pygame.SRCALPHA)
            sh_hl_surf.fill((255, 255, 255, 60))
            surf.blit(sh_hl_surf, sh_hl)

    # 边框
    pygame.draw.rect(surf, (80, 80, 100), bg_rect, 2, border_radius=BORDER_R)

    # 装饰：左侧小图标（心形用菱形替代）
    icon_x, icon_y = BAR_X - 2, BAR_Y + BAR_H // 2
    heart_color = (255, 60, 50) if hp_ratio < 0.3 else (255, 120, 100)
    pts = [
        (icon_x, icon_y),
        (icon_x - 6, icon_y - 5),
        (icon_x, icon_y - 10),
        (icon_x + 6, icon_y - 5),
    ]
    pygame.draw.polygon(surf, heart_color, pts)
    pygame.draw.polygon(surf, (180, 30, 20), pts, 1)

    # 文字：HP数值（含护盾）
    if has_shield:
        hp_text = f"{int(hp)} / {int(hp_max)} ({int(shield)})"
    else:
        hp_text = f"{int(hp)} / {int(hp_max)}"
    text_img = FONT20.render(hp_text, True, (255, 255, 255))
    text_x = BAR_X + BAR_W // 2 - text_img.get_width() // 2
    text_y = BAR_Y + BAR_H // 2 - text_img.get_height() // 2
    # 文字阴影
    shadow_img = FONT20.render(hp_text, True, (0, 0, 0))
    surf.blit(shadow_img, (text_x + 1, text_y + 1))
    surf.blit(text_img, (text_x, text_y))


# ===================== 坐标信息绘制 =====================
def draw_player_info(surf, player, dt: float):
    """在血条下方绘制玩家坐标（简洁大字）。"""
    px, py = player.get_center()
    # 格式：1位小数，小数后强制1位，前面不补零
    x_str = f"{px:.1f}"
    y_str = f"{py:.1f}"
    info = f"X {x_str}   Y {y_str}"
    text_img = FONT28.render(info, True, (220, 225, 240))
    surf.blit(text_img, (60, 66))


# ===================== 濒死滤镜 =====================
def draw_near_death_vignette(surf, player):
    """当血量极低时，屏幕边缘绘制渐变红圈。"""
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
    max_r = int((cx ** 2 + cy ** 2) ** 0.5)

    vignette = pygame.Surface((W, H), pygame.SRCALPHA)

    # 从外向内绘制渐变红圈
    inner_r = int(max_r * 0.45)  # 内部安全区半径
    steps = 40
    for i in range(steps):
        t = i / steps
        r = inner_r + (max_r - inner_r) * t
        a = int(alpha * (t ** 1.5))  # 越靠外越浓
        # 在环形区域绘制
        if a > 0:
            pygame.draw.circle(vignette, (200, 20, 20, a), (cx, cy), int(r), max(1, int((max_r - inner_r) / steps) + 1))

    # 中心安全区保持透明
    pygame.draw.circle(vignette, (0, 0, 0, 0), (cx, cy), int(inner_r))

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
    ("world.default_block_id","默认方块ID",        "int",   0,        1),
    # ---- Player 属性 ----
    ("player.hp_max",        "最大血量",           "float", 150.0,    10.0),
    ("player.v_max",         "最大速度",           "float", 36.5,     1.0),
    ("player.v_jump",        "跳跃速度",           "float", 26.5,     1.0),
    ("player.stamina_max",   "最大体力",           "float", 100.0,    10.0),
    ("player.phys_atk",      "物理攻击",           "float", 10.0,     5.0),
    ("player.magic_atk",     "魔法攻击",           "float", 0.0,      5.0),
    ("player.phys_res",      "物理抗性",           "float", 0.0,      5.0),
    ("player.magic_res",     "魔法抗性",           "float", 0.0,      5.0),
    ("player.phys_pen",      "物理穿透",           "float", 0.0,      5.0),
    ("player.magic_pen",     "魔法穿透",           "float", 0.0,      5.0),
    ("player.k_res",         "抗性系数",           "float", 150.0,    10.0),
    ("player.dr",            "减伤率",             "float", 0.0,      0.05),
    ("player.f_x",           "X轴摩擦系数",        "float", 0.985,    0.005),
    ("player.f_y",           "Y轴摩擦系数",        "float", 0.98,     0.005),
    ("player.shield",        "初始护盾",           "float", 0.0,      5.0),
    ("player.w",             "玩家宽度",           "float", 0.8,      0.1),
    ("player.h",             "玩家高度",           "float", 1.8,      0.1),
    ("player.costume_id",    "时  装",            "int",   1,        1),
]

# 精确输入状态
_dev_inputting = False       # 是否处于精确输入模式
_dev_input_text = ""         # 输入缓冲区


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
        "hp_max": 150.0, "v_max": 36.5, "v_jump": 26.5, "stamina_max": 100.0,
        "phys_atk": 10.0, "magic_atk": 0.0, "phys_res": 0.0, "magic_res": 0.0,
        "phys_pen": 0.0, "magic_pen": 0.0, "k_res": 150.0, "dr": 0.0,
        "f_x": 0.985, "f_y": 0.98, "shield": 0.0, "w": 0.8, "h": 1.8,
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
    """开发者界面：查询地图、选择地图、编辑属性、启动游戏。"""
    global _dev_edit_mode, _dev_edit_field_idx, _dev_edit_dirty, _dev_edit_config
    global _dev_inputting, _dev_input_text

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
            type_surf = FONT20.render(type_tag, True, type_color)
            logic_surface.blit(type_surf, (540, row_y + 8))

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
                             f"当前选中: ID={_dev_selected_id}  |  Enter 启动  E 编辑属性",
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

    if event.type != pygame.KEYDOWN:
        return

    maps_dict = list_maps()
    ids = sorted(maps_dict.keys())
    if not ids:
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
                    sfx.play_jump()
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
                elif event.key == player1.key_bind["up"] or event.key == pygame.K_UP:
                    # W/↑键：可攀爬时进入攀爬，攀爬中向上
                    if not player1.fly_mode:
                        if not player1.is_climbing and player1.can_climb:
                            player1.try_start_climbing(_current_map)
                        elif player1.is_climbing:
                            player1.climb_move(1.0)
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

        # ---- 移动物理（游戏结束/胜利时冻结）----
        if not _game_over and not _game_win:
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
                if keys[player1.key_bind["left"]] or keys[pygame.K_LEFT]:
                    dir_x -= 0.35
                if keys[player1.key_bind["right"]] or keys[pygame.K_RIGHT]:
                    dir_x += 0.35
                player1.move(dir_x)

                # 攀爬中持续按W/↑向上
                if player1.is_climbing and (keys[player1.key_bind["up"]] or keys[pygame.K_UP]):
                    player1.climb_move(1.0)

                if jump_pressed:
                    player1.jump()
                    jump_pressed = False

                player1.update_physics(dt, _current_map)
                player1.collide_with_world(_current_map, dt)

                # 攀爬中着陆或离开可攀爬方块：自动解除
                if player1.is_climbing and (player1.on_ground or not player1.can_climb):
                    player1.is_climbing = False

        px, py = player1.get_center()
        camera.follow(px, py)

        # 渲染世界
        logic_surface.fill((30, 30, 30))
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

        # ---- HP 血条 ----
        # ---- 音效检测 ----
        global _prev_score, _prev_alive, _win_played, _death_played
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
        draw_player_info(logic_surface, player1, dt)

        # ---- 濒死滤镜 ----
        draw_near_death_vignette(logic_surface, player1)

        # ---- 积分显示（顶部居中）----
        score_text = f"★ {player1.score}"
        score_img = FONT28.render(score_text, True, (255, 220, 80))
        score_x = LOGIC_WIDTH // 2 - score_img.get_width() // 2
        logic_surface.blit(score_img, (score_x, 18))

        # ---- 计时器（积分限时模式）----
        wmode = _current_map.mode if _current_map else "free"
        time_limit = getattr(_current_map, 'time_limit', 0.0)
        if wmode == "score_timed" and time_limit > 0:
            remaining = max(0, time_limit - _game_timer)
            timer_text = f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"
            timer_color = (255, 80, 80) if remaining < 30 else (255, 255, 255)
            timer_img = FONT28.render(timer_text, True, timer_color)
            timer_x = LOGIC_WIDTH // 2 - timer_img.get_width() // 2
            logic_surface.blit(timer_img, (timer_x, 48))

        # ---- 积分目标进度（积分目标模式）----
        score_goal = getattr(_current_map, 'score_goal', 0)
        if wmode == "score_target" and score_goal > 0:
            goal_text = f"目标: {score_goal}  ({int(player1.score / max(1, score_goal) * 100)}%)"
            goal_img = FONT20.render(goal_text, True, (200, 220, 255))
            goal_x = LOGIC_WIDTH // 2 - goal_img.get_width() // 2
            logic_surface.blit(goal_img, (goal_x, 48))

        # ---- 爱心（复活次数）----
        if _player_lives_left > 0:
            heart_text = "♥"
            if _player_lives_left <= 5:
                heart_text = "♥ " * _player_lives_left
            else:
                heart_text = f"♥ × {_player_lives_left}"
            heart_img = FONT24.render(heart_text.strip(), True, (255, 60, 60))
            logic_surface.blit(heart_img, (LOGIC_WIDTH - heart_img.get_width() - 24, 18))

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

        # 右上角 FPS（白字灰边）
        fps_text = f"FPS {int(clock.get_fps())}"
        fps_img = FONT28.render(fps_text, True, (255, 255, 255))
        # 灰边（8方向绘制阴影）
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            shadow = FONT28.render(fps_text, True, (80, 80, 90))
            logic_surface.blit(shadow, (LOGIC_WIDTH - fps_img.get_width() - 16 + dx, 8 + dy))
        logic_surface.blit(fps_img, (LOGIC_WIDTH - fps_img.get_width() - 16, 8))

        # 飞行模式指示
        if player1.fly_mode:
            draw_text_center(logic_surface, FONT20, "【飞行模式】", LOGIC_HEIGHT - 40, (100, 255, 200))

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
