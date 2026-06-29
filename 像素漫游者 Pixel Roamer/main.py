from __future__ import annotations

import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
from camera import Camera
from creature import Player
from maps import get_map, list_maps, load_map_config, save_map_config, get_map_folder_name

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
    print(f"可用地图：{list_maps()}")


def launch_world(map_id: int):
    """启动器：游戏世界。传入地图ID，加载地图、创建相机和玩家。"""
    global _current_map, camera, player1, _world_initialized
    _current_map = get_map(map_id)
    camera = Camera(LOGIC_WIDTH, LOGIC_HEIGHT, _current_map)
    sp_x, sp_y = _current_map.spawn_points

    # 读取玩家配置（若有）
    player_cfg = getattr(_current_map, 'player_config', {})
    hp_max = player_cfg.get("hp_max", 150)
    v_max = player_cfg.get("v_max", 36.5)
    v_jump = player_cfg.get("v_jump", 26.5)

    player1 = Player(player_id=0, player_name="玩家1", spawn_x=float(sp_x), spawn_y=float(sp_y),
                     key_bind=p1_keys, hp_max=hp_max)
    player1.v_max = v_max
    player1.v_jump = v_jump
    _world_initialized = True
    print(f"已加载地图：{_current_map.name}（{_current_map.width}x{_current_map.height}）")


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


def draw_hp_bar(surf, player, dt: float):
    """在逻辑画布左上角绘制精美血条。"""
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

    # 背景阴影
    shadow_rect = pygame.Rect(BAR_X + 2, BAR_Y + 2, BAR_W, BAR_H)
    pygame.draw.rect(surf, (0, 0, 0, 160), shadow_rect, border_radius=BORDER_R)

    # 主背景（深色）
    bg_rect = pygame.Rect(BAR_X, BAR_Y, BAR_W, BAR_H)
    pygame.draw.rect(surf, (25, 25, 35), bg_rect, border_radius=BORDER_R)

    # 血量条填充
    hp_ratio = max(0.0, min(1.0, player.hp / player.hp_max))
    fill_w = int((BAR_W - 8) * hp_ratio)
    if fill_w > 0:
        fill_rect = pygame.Rect(BAR_X + 4, BAR_Y + 4, fill_w, BAR_H - 8)

        # 受伤闪烁时用黄色覆盖
        if _damage_flash_timer > 0:
            flash_alpha = _damage_flash_timer / _damage_flash_duration
            # 主色从红色渐变到黄色
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
        if fill_w > 16:
            highlight_rect = pygame.Rect(BAR_X + 4, BAR_Y + 4, fill_w, (BAR_H - 8) // 2)
            hl_surf = pygame.Surface((fill_w, (BAR_H - 8) // 2), pygame.SRCALPHA)
            hl_surf.fill((255, 255, 255, 50))
            surf.blit(hl_surf, highlight_rect)

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

    # 文字：HP数值
    hp_text = f"{int(player.hp)} / {int(player.hp_max)}"
    text_img = FONT20.render(hp_text, True, (255, 255, 255))
    text_x = BAR_X + BAR_W // 2 - text_img.get_width() // 2
    text_y = BAR_Y + BAR_H // 2 - text_img.get_height() // 2
    # 文字阴影
    shadow_img = FONT20.render(hp_text, True, (0, 0, 0))
    surf.blit(shadow_img, (text_x + 1, text_y + 1))
    surf.blit(text_img, (text_x, text_y))


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
_setting_selected_row = 0          # 当前选中行（目前只有 fps 一行）
_setting_selected_fps_idx = 1      # 默认 fps=60 的索引
_setting_from_page = PAGE_DEV      # 从哪个页面进入设置的
_setting_fps_just_autodetected = False


def _run_fps_benchmark() -> int:
    """快速测试设备帧率能力，返回推荐的 fps 上限（30 的整数倍）。"""
    test_surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
    test_clock = pygame.time.Clock()
    # 模拟较重渲染负载
    start = pygame.time.get_ticks()
    frames = 0
    while pygame.time.get_ticks() - start < 800:  # 测试 800ms
        test_surface.fill((0, 0, 0))
        for i in range(50):
            pygame.draw.rect(test_surface, (i * 5 % 255, i * 3 % 255, i * 7 % 255),
                             (i * 20 % LOGIC_WIDTH, i * 15 % LOGIC_HEIGHT, 80, 60))
        test_clock.tick(1000)
        frames += 1
    # 取略低于实测值的 30 的整数倍
    measured = frames / 0.8 * 0.9
    best = 30
    for opt in _FPS_OPTIONS:
        if opt <= measured:
            best = opt
    return best


def run_setting_page(dt: float):
    """设置页面渲染。"""
    global _setting_selected_row, _setting_selected_fps_idx, _setting_fps_just_autodetected

    logic_surface.fill((20, 20, 40))

    # 标题
    y = 60
    y = draw_text_center(logic_surface, FONT40, "设置 (SETTING)", y, (100, 200, 255)) + 30

    # ---- FPS 设置行 ----
    row_y = y
    # 行背景
    is_active = (_setting_selected_row == 0)
    row_bg = pygame.Rect(200, row_y - 4, LOGIC_WIDTH - 400, 56)
    pygame.draw.rect(logic_surface, (40, 40, 70) if is_active else (25, 25, 45), row_bg)
    if is_active:
        pygame.draw.rect(logic_surface, (100, 180, 255), row_bg, 2)

    # ← 当前值  →
    fps_label = "自动" if _setting_fps_just_autodetected else str(_FPS_OPTIONS[_setting_selected_fps_idx])
    row_text = f"帧率上限：{fps_label} FPS"
    draw_text_left(logic_surface, FONT28, row_text, 240, row_y + 10, (255, 255, 255))

    # 操作提示
    draw_text_right(logic_surface, FONT24, "← → 调整", LOGIC_WIDTH - 240, row_y + 14, (180, 180, 200))

    y = row_y + 70

    # ---- 自动检测按钮 ----
    btn_y = y + 20
    btn_rect = pygame.Rect(350, btn_y, LOGIC_WIDTH - 700, 44)
    btn_color = (60, 60, 100) if _setting_selected_row == 1 else (40, 40, 60)
    pygame.draw.rect(logic_surface, btn_color, btn_rect)
    if _setting_selected_row == 1:
        pygame.draw.rect(logic_surface, (100, 180, 255), btn_rect, 2)
    draw_text_center(logic_surface, FONT24, "自动检测设备最佳帧率", btn_y + 8, (200, 200, 220))

    if _setting_fps_just_autodetected:
        y = btn_y + 56
        draw_text_center(logic_surface, FONT20, f"检测结果：{fps_label} FPS 已自动设定", y, (100, 255, 100))

    # ---- 底部提示 ----
    draw_text_center(logic_surface, FONT20, "↑ ↓ 选择项目    ← → 调整数值    Esc 返回游戏", LOGIC_HEIGHT - 60, (140, 140, 180))


def handle_setting_input(event):
    """处理设置页面的键盘事件。"""
    global _setting_selected_row, _setting_selected_fps_idx, current_fps
    global _setting_fps_just_autodetected, _setting_from_page

    if event.type != pygame.KEYDOWN:
        return

    # 一共2行：0=帧率选择，1=自动检测按钮
    if event.key == pygame.K_UP:
        _setting_selected_row = (_setting_selected_row - 1) % 2
        _setting_fps_just_autodetected = False
    elif event.key == pygame.K_DOWN:
        _setting_selected_row = (_setting_selected_row + 1) % 2
        _setting_fps_just_autodetected = False
    elif event.key == pygame.K_LEFT:
        if _setting_selected_row == 0:
            _setting_selected_fps_idx = (_setting_selected_fps_idx - 1) % len(_FPS_OPTIONS)
            _setting_fps_just_autodetected = False
            current_fps = _FPS_OPTIONS[_setting_selected_fps_idx]
            print(f"设定帧率上限：{current_fps}")
    elif event.key == pygame.K_RIGHT:
        if _setting_selected_row == 0:
            _setting_selected_fps_idx = (_setting_selected_fps_idx + 1) % len(_FPS_OPTIONS)
            _setting_fps_just_autodetected = False
            current_fps = _FPS_OPTIONS[_setting_selected_fps_idx]
            print(f"设定帧率上限：{current_fps}")
    elif event.key == pygame.K_RETURN:
        if _setting_selected_row == 1:
            # 自动检测
            detected = _run_fps_benchmark()
            # 找到最接近的索引
            try:
                _setting_selected_fps_idx = _FPS_OPTIONS.index(detected)
            except ValueError:
                _setting_selected_fps_idx = 1  # 默认 60
            _setting_fps_just_autodetected = True
            current_fps = detected
            print(f"自动检测完成，设定帧率上限：{current_fps}")
    elif event.key == pygame.K_ESCAPE:
        # 返回来源页面（恢复游戏，不重新初始化）
        set_page_no_launch(_setting_from_page)


# ===================== Dev 页面 =====================
# 可编辑字段定义：(属性路径, 显示名, 类型, 默认值, 步进)
_EDITABLE_FIELDS = [
    # world 属性
    ("world.gravity", "重力", float, -6.5, 0.5),
    ("world.view_blocks_h", "视野(格高)", float, 15.0, 1.0),
    # player 属性
    ("player.hp_max", "玩家最大血量", float, 150.0, 10.0),
    ("player.v_max", "玩家最大速度", float, 36.5, 1.0),
    ("player.v_jump", "玩家跳跃速度", float, 26.5, 1.0),
]


def _get_edit_config(map_id: int) -> dict:
    """获取地图的当前配置（合并默认与已保存）。"""
    saved = load_map_config(map_id)
    config = {"world": {}, "player": {}}
    # 从地图实例读取当前 world 值作为默认
    try:
        m = get_map(map_id)
        config["world"]["gravity"] = m.gravity
        config["world"]["view_blocks_h"] = m.view_blocks_h
    except Exception:
        config["world"]["gravity"] = -6.5
        config["world"]["view_blocks_h"] = 15.0
    # 合并已保存的玩家配置
    saved_player = saved.get("player", {})
    config["player"]["hp_max"] = saved_player.get("hp_max", 150.0)
    config["player"]["v_max"] = saved_player.get("v_max", 36.5)
    config["player"]["v_jump"] = saved_player.get("v_jump", 26.5)
    # 已保存的 world 配置覆盖
    saved_world = saved.get("world", {})
    config["world"].update(saved_world)
    return config


def _get_field_value(config: dict, field_path: str):
    """从配置字典中读取字段值。field_path 如 'player.hp_max'"""
    parts = field_path.split(".")
    val = config
    for p in parts:
        val = val[p]
    return val


def _set_field_value(config: dict, field_path: str, value):
    """设置配置字典中的字段值。"""
    parts = field_path.split(".")
    obj = config
    for p in parts[:-1]:
        obj = obj[p]
    obj[parts[-1]] = value


def run_dev_page(dt: float):
    """开发者界面：查询地图、选择地图、编辑属性、启动游戏。"""
    global _dev_edit_mode, _dev_edit_field_idx, _dev_edit_dirty, _dev_edit_config

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
        y = draw_text_center(logic_surface, FONT34, f"编辑地图属性 — ID={_dev_selected_id}", y, (100, 255, 150)) + 8
        y = draw_text_center(logic_surface, FONT20, "↑↓ 选择字段  ← → 调整数值  S 保存  Esc 返回", y, (180, 180, 180)) + 20

        for i, (field_path, label, ftype, default, step) in enumerate(_EDITABLE_FIELDS):
            val = _get_field_value(_dev_edit_config, field_path)
            is_sel = (i == _dev_edit_field_idx)

            row_h = 42
            row_y = y
            # 行背景
            if is_sel:
                pygame.draw.rect(logic_surface, (50, 50, 90), (300, row_y - 2, LOGIC_WIDTH - 600, row_h))
                pygame.draw.rect(logic_surface, (100, 255, 150), (300, row_y - 2, LOGIC_WIDTH - 600, row_h), 2)

            draw_text_left(logic_surface, FONT28 if is_sel else FONT24,
                           f"{label}:", 330, row_y + 6,
                           (255, 255, 180) if is_sel else (200, 200, 200))
            draw_text_right(logic_surface, FONT28 if is_sel else FONT24,
                            f"{val:.1f}" if isinstance(val, float) else str(val),
                            LOGIC_WIDTH - 330, row_y + 6,
                            (100, 255, 150) if is_sel else (150, 220, 150))
            y += row_h + 4

        y += 20
        status_color = (100, 255, 100) if _dev_edit_dirty else (150, 150, 150)
        draw_text_center(logic_surface, FONT20,
                         "已修改，按 S 保存" if _dev_edit_dirty else "无修改",
                         y, status_color)
    else:
        # ========== 地图列表模式 ==========
        y = draw_text_center(logic_surface, FONT34, "开发者界面 (DEV)", y, (100, 200, 255)) + 12
        y = draw_text_center(logic_surface, FONT24, "↑↓ 选择  Enter 启动  E 编辑属性  R 刷新", y, (180, 180, 180)) + 30

        # 表头
        col_x_id = 120
        col_x_name = 220
        col_x_size = 550
        col_x_grav = 730
        header_y = y
        pygame.draw.rect(logic_surface, (30, 30, 55), (80, y - 2, LOGIC_WIDTH - 160, 32))
        draw_text_left(logic_surface, FONT24, "ID", col_x_id, y, (150, 150, 150))
        draw_text_left(logic_surface, FONT24, "地图名称", col_x_name, y, (150, 150, 150))
        draw_text_left(logic_surface, FONT24, "尺寸", col_x_size, y, (150, 150, 150))
        draw_text_left(logic_surface, FONT24, "重力", col_x_grav, y, (150, 150, 150))
        y = header_y + 36

        for mid in map_ids:
            name = maps_dict[mid]
            try:
                m = get_map(mid)
                info_size = f"{m.width} x {m.height}"
                info_grav = str(m.gravity)
            except Exception:
                info_size = "?"
                info_grav = "?"

            is_selected = (mid == _dev_selected_id)
            row_h = 38
            if is_selected:
                pygame.draw.rect(logic_surface, (50, 50, 90), (80, y - 2, LOGIC_WIDTH - 160, row_h))
                pygame.draw.rect(logic_surface, (100, 200, 255), (80, y - 2, LOGIC_WIDTH - 160, row_h), 2)

            draw_text_left(logic_surface, FONT28 if is_selected else FONT24,
                           str(mid), col_x_id, y + 4,
                           (255, 255, 180) if is_selected else (200, 200, 200))
            draw_text_left(logic_surface, FONT28 if is_selected else FONT24,
                           name, col_x_name, y + 4,
                           (255, 255, 180) if is_selected else (200, 200, 200))
            draw_text_left(logic_surface, FONT28 if is_selected else FONT24,
                           info_size, col_x_size, y + 4,
                           (255, 255, 180) if is_selected else (200, 200, 200))
            draw_text_left(logic_surface, FONT28 if is_selected else FONT24,
                           info_grav, col_x_grav, y + 4,
                           (255, 255, 180) if is_selected else (200, 200, 200))
            y += row_h

    # 底部
    if _dev_selected_id is not None:
        if _dev_edit_mode:
            draw_text_center(logic_surface, FONT20,
                             "S: 保存到硬盘  |  Esc: 返回列表",
                             LOGIC_HEIGHT - 40, (140, 180, 255))
        else:
            draw_text_center(logic_surface, FONT24,
                             f"当前选中: ID={_dev_selected_id}  |  Enter 启动  E 编辑属性",
                             LOGIC_HEIGHT - 50, (140, 180, 255))


def handle_dev_input(event):
    """处理 dev 页面的键盘事件。"""
    global _dev_selected_id, _dev_edit_mode, _dev_edit_field_idx
    global _dev_edit_dirty, _dev_edit_config

    if event.type != pygame.KEYDOWN:
        return

    maps_dict = list_maps()
    ids = sorted(maps_dict.keys())
    if not ids:
        return

    # ========== 编辑模式按键 ==========
    if _dev_edit_mode and _dev_selected_id is not None:
        if event.key == pygame.K_ESCAPE:
            _dev_edit_mode = False
            _dev_edit_dirty = False
        elif event.key == pygame.K_UP:
            _dev_edit_field_idx = (_dev_edit_field_idx - 1) % len(_EDITABLE_FIELDS)
        elif event.key == pygame.K_DOWN:
            _dev_edit_field_idx = (_dev_edit_field_idx + 1) % len(_EDITABLE_FIELDS)
        elif event.key == pygame.K_LEFT:
            field_path, label, ftype, default, step = _EDITABLE_FIELDS[_dev_edit_field_idx]
            val = _get_field_value(_dev_edit_config, field_path)
            val -= step
            _set_field_value(_dev_edit_config, field_path, ftype(val))
            _dev_edit_dirty = True
        elif event.key == pygame.K_RIGHT:
            field_path, label, ftype, default, step = _EDITABLE_FIELDS[_dev_edit_field_idx]
            val = _get_field_value(_dev_edit_config, field_path)
            val += step
            _set_field_value(_dev_edit_config, field_path, ftype(val))
            _dev_edit_dirty = True
        elif event.key == pygame.K_s:
            # 保存到硬盘
            save_map_config(_dev_selected_id, _dev_edit_config)
            _dev_edit_dirty = False
            print(f"地图 {_dev_selected_id} 配置已保存: {_dev_edit_config}")
        elif event.key == pygame.K_RETURN:
            # 在编辑模式中 Enter 也保存并启动
            if _dev_edit_dirty:
                save_map_config(_dev_selected_id, _dev_edit_config)
                _dev_edit_dirty = False
                print(f"地图 {_dev_selected_id} 配置已保存: {_dev_edit_config}")
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
            print(f"进入编辑模式，当前配置: {_dev_edit_config}")
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
        print(f"地图列表已刷新：{list_maps()}")


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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                current_fps = min(current_fps + 10, MAX_FPS)
                print(f"当前帧率上限：{current_fps}")
            if event.key == pygame.K_F2:
                current_fps = max(current_fps - 10, MIN_FPS)
                print(f"当前帧率上限：{current_fps}")

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
                elif event.key == player1.key_bind["fly"]:
                    # 切换飞行模式
                    player1.fly_mode = not player1.fly_mode
                    player1.v_x = 0.0
                    player1.v_y = 0.0
                    player1.is_climbing = False
                    print(f"飞行模式: {'开启' if player1.fly_mode else '关闭'}")
                elif event.key == player1.key_bind["up"]:
                    # W键：可攀爬时进入攀爬，攀爬中向上
                    if not player1.fly_mode:
                        if not player1.is_climbing and player1.can_climb:
                            player1.try_start_climbing()
                        elif player1.is_climbing:
                            player1.climb_move(1.0)
                elif event.key == player1.key_bind["down"]:
                    # S键：攀爬中则解除
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

        # ---- 飞行模式 ----
        if player1.fly_mode:
            fly_dx, fly_dy = 0.0, 0.0
            if keys[player1.key_bind["left"]]:
                fly_dx -= 1.0
            if keys[player1.key_bind["right"]]:
                fly_dx += 1.0
            if keys[player1.key_bind["up"]]:
                fly_dy += 1.0
            if keys[player1.key_bind["down"]]:
                fly_dy -= 1.0
            # 直接操作坐标
            player1._x += fly_dx * player1.fly_speed * dt
            player1._y += fly_dy * player1.fly_speed * dt
            player1.v_x = 0.0
            player1.v_y = 0.0
            # 钳制在地图边界内
            player1._x = max(0.5, min(player1._x, _current_map.width - 0.5))
            player1._y = max(0.5, min(player1._y, _current_map.height - 0.5))
            # 更新接触池（用于绘制等）
            grect = player1.get_game_rect()
            player1.contact_pool = set()
            player1.stand_pool = None
        else:
            # ---- 正常模式 ----
            dir_x = 0.0
            if keys[player1.key_bind["left"]]:
                dir_x -= 0.35
            if keys[player1.key_bind["right"]]:
                dir_x += 0.35
            player1.move(dir_x)

            # 攀爬中持续按W向上
            if player1.is_climbing and keys[player1.key_bind["up"]]:
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

        # 绘制玩家
        player_screen_rect = camera.game_rect_to_screen_rect(player1.get_game_rect())
        pygame.draw.rect(logic_surface, (255, 80, 80), player_screen_rect)

        # ---- HP 血条 ----
        draw_hp_bar(logic_surface, player1, dt)

        # ---- 濒死滤镜 ----
        draw_near_death_vignette(logic_surface, player1)

        # 右上角 FPS
        fps_text = f"FPS: {int(clock.get_fps())}"
        draw_text_right(logic_surface, FONT24, fps_text, LOGIC_WIDTH - 16, 10, (200, 200, 200))

        # 飞行模式指示
        if player1.fly_mode:
            draw_text_center(logic_surface, FONT20, "【飞行模式】", LOGIC_HEIGHT - 40, (100, 255, 200))

        f += 1
        state_str = ("飞行" if player1.fly_mode
                     else ("攀爬中" if player1.is_climbing
                           else ("可攀爬" if player1.can_climb
                                 else ("地面" if player1.on_ground else "浮空"))))
        print(f"【{f}】{state_str}, v_x={player1.v_x:.2f} v_y={player1.v_y:.2f}")
        print(f"hp={player1.hp:.0f}, fly={player1.fly_mode} | climb={'Y' if player1.is_climbing else ('can' if player1.can_climb else 'N')}")
        if not player1.fly_mode:
            print(player1.contact_pool, "###", player1.stand_pool)

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
