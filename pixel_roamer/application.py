from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
from camera import Camera
from creature import Player
from maps import (get_map, list_maps, load_map_config, save_map_config,
                  get_map_folder_name, get_map_summary, rename_map)
from costumes import (COSTUMES, DEFAULT_COSTUME_ID, list_costumes,
                       render_costume_direct, get_costume_anim_info,
                       clear_costume_cache)
import sfx
import music
import game_text as gt
import loading_screen as ls
import home_page as hp
from game_state import resolve_player_death
from pixel_roamer.ui.config import (FONT24, FONT28, FONT56, GAME_NAME_CN, GAME_NAME_EN, PAGE_DEV, PAGE_HOME, PAGE_INFINITE_WORLD, PAGE_INIT, PAGE_SETTING, PAGE_WORLD, _FPS_OPTIONS)
from pixel_roamer.ui.widgets import (draw_text_center)

from pathlib import Path

from pixel_roamer.ui.hud import HudRenderer
from pixel_roamer.ui.settings import SettingsPage
from pixel_roamer.ui.references import ReferenceBrowser
from pixel_roamer.ui.map_browser import MapBrowser

PROJECT_ROOT = Path(__file__).resolve().parents[1]

class GameApp:
    """Own the application lifetime, session state and page coordination."""

    def __init__(self):
        self.hud = HudRenderer(self)
        self.settings = SettingsPage(self)
        self.references = ReferenceBrowser(self)
        self.map_browser = MapBrowser(self)
        pygame.mixer.pre_init(22050, -16, 2, 512)  # 音频预初始化（立体声）
        pygame.init()
        pygame.key.stop_text_input()
        pygame.key.set_repeat(0, 0)
        self.win_surface = pygame.display.set_mode((INIT_WIN_W, INIT_WIN_H), pygame.RESIZABLE)
        pygame.display.set_caption(f"{GAME_NAME_CN}  {GAME_NAME_EN}")
        self.clock = pygame.time.Clock()
        self.logic_surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
        self.win_w, self.win_h = INIT_WIN_W, INIT_WIN_H
        self.scale = 1.0
        self.draw_offset_x = 0
        self.draw_offset_y = 0
        self.current_fps = DEFAULT_FPS
        self.update_scale_param()
        self.page = PAGE_INIT  # 启动时进入加载界面
        self._page_need_launch = True
        self._page_launch_kwargs = {}
        self._world_initialized = False  # 跟踪世界是否已初始化（从设置返回时跳过重新初始化）
        self._transition_alpha = 255      # 当前黑屏透明度 (0~255)，启动时全黑
        self._transition_target = 0        # 目标透明度
        self._transition_speed = 800       # 过渡速度（alpha/秒）
        self._next_page_after_transition = None  # 过渡完成后切换的页面
        self._current_map = None
        self.camera = None
        self.player1 = None
        self.p1_keys = {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_SPACE,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fly": pygame.K_f,
        }
        self._dev_selected_id = None
        self._dev_edit_mode = False        # 开发者地图编辑模式
        self._dev_edit_field_idx = 0       # 当前编辑字段索引
        self._dev_edit_dirty = False       # 是否有未保存的修改
        self._dev_edit_config = {}         # 当前编辑中的配置
        self._dev_error = ""
        self._dev_renaming = False         # 是否正在重命名地图
        self._game_over = False
        self._game_win = False
        self._game_timer = 0.0             # 累计游戏时间（秒）
        self._player_lives_left = 0        # 剩余复活次数
        self._infinite_lives = True        # lives=0 时无限复活；有限次数耗尽后保持为 False
        self._damage_flash_timer = 0.0       # 受伤黄色闪烁计时器
        self._damage_flash_duration = 0.3    # 闪烁持续时间（秒）
        self._stamina_flash_timer = 0.0      # 体力不足闪烁计时器
        self._stamina_flash_duration = 1.0   # 体力闪烁持续1秒
        self._prev_hp = None                 # 上一帧血量（用于检测受伤）
        self._prev_score = 0                 # 上一帧积分（检测拾取）
        self._prev_alive = True              # 上一帧存活状态（检测死亡）
        self._win_played = False             # 通关音效是否已播放
        self._death_played = False           # 死亡音效是否已播放
        self._buff_icon_rects = []  # [(ix, iy, p, buff_instance), ...]
        self._setting_selected_row = 0
        self._setting_selected_fps_idx = 1
        self._setting_from_page = PAGE_DEV
        self._setting_fps_just_autodetected = False
        self._dev_inputting = False       # 是否处于精确输入模式
        self._dev_input_text = ""         # 输入缓冲区
        self._dev_block_browser = False        # 是否处于方块预览模式
        self._dev_block_browser_mode = "grid"
        self._dev_block_browser_cursor = 0
        self._dev_block_browser_scroll = 0
        self._dev_block_browser_show_name2 = False
        self._dev_block_detail_id = None
        self._dev_block_page_offset = 0
        self._dev_buff_browser = False         # 是否处于 Buff 预览模式
        self._dev_buff_browser_mode = "grid"
        self._dev_buff_browser_cursor = 0
        self._dev_buff_browser_scroll = 0
        self._dev_buff_browser_show_name2 = False
        self._dev_buff_detail_id = None
        self._LAUNCHERS = {
            PAGE_DEV: self.launch_dev,
            PAGE_INIT: self.launch_init,
            PAGE_HOME: self.launch_home,
            PAGE_WORLD: self.launch_world,
            PAGE_INFINITE_WORLD: self.launch_default,
            PAGE_SETTING: self.launch_setting,
        }
        self._page_launch_kwargs = {}
        self._dispatch_launcher()
        self.running = True
        self.jump_pressed = False
        self.f = 0

    def update_scale_param(self):
        scale_w = self.win_w / LOGIC_WIDTH
        scale_h = self.win_h / LOGIC_HEIGHT
        self.scale = min(scale_w, scale_h)
        real_draw_w = LOGIC_WIDTH * self.scale
        real_draw_h = LOGIC_HEIGHT * self.scale
        self.draw_offset_x = (self.win_w - real_draw_w) / 2
        self.draw_offset_y = (self.win_h - real_draw_h) / 2

    def set_page(self, page_id: int, **kwargs):
        """设置当前页面，立即执行对应启动器。"""
        self.jump_pressed = False
        # 页面切换时管理音乐
        if page_id == PAGE_INIT:
            music.stop(fade_out_ms=400)  # 加载界面静音
        elif page_id == PAGE_HOME:
            music.play("home", fade_in_ms=1000)
        elif page_id == PAGE_WORLD:
            pass  # 音乐由 launch_world 处理
        elif page_id == PAGE_SETTING:
            music.stop(fade_out_ms=400)
        elif page_id == PAGE_DEV:
            music.stop(fade_out_ms=400)
        elif self.page != page_id:
            music.stop(fade_out_ms=400)
        self.page = page_id
        self._page_launch_kwargs = kwargs
        self._page_need_launch = False
        self._dispatch_launcher()
        self._trigger_fade_in()

    def _trigger_fade_in(self):
        """触发页面淡入过渡效果。"""
        self._transition_alpha = 200
        self._transition_target = 0

    def set_page_no_launch(self, page_id: int):
        """切换页面但不触发启动器（用于返回暂停状态）。"""
        self.jump_pressed = False
        self.page = page_id
        self._page_need_launch = False
        # 恢复目标页面的背景音乐
        if page_id == PAGE_HOME:
            music.play("home", fade_in_ms=800)
        elif page_id == PAGE_WORLD and self._current_map is not None:
            self._play_world_music(self._current_map)
        self._trigger_fade_in()

    def set_page_by_name(self, name: str, **kwargs):
        """按名称设置页面（兼容旧接口）。"""
        ids = {"dev": 0, "init": 1, "home": 2, "world": 3, "infinite_world": 4, "setting": 5}
        self.set_page(ids[name], **kwargs)

    def _init_dev_selection(self):
        maps_dict = list_maps()
        if not maps_dict:
            self._dev_selected_id = None
            return
        ids = sorted(maps_dict.keys())
        if self._dev_selected_id not in ids:
            self._dev_selected_id = ids[0]

    def launch_init(self):
        """启动器：加载界面。初始化粒子、星空和加载进度。"""
        ls.init_loading_screen(LOGIC_WIDTH, LOGIC_HEIGHT)

    def launch_home(self):
        """启动器：游戏主页。初始化粒子、星空和菜单动画。"""
        hp.init_home_page(LOGIC_WIDTH, LOGIC_HEIGHT)

    def launch_dev(self):
        """启动器：开发者界面。"""
        self._init_dev_selection()

    def launch_world(self, map_id: int):
        """启动器：游戏世界。传入地图ID，加载地图、创建相机和玩家。"""
        self._current_map = get_map(map_id)
        self.camera = Camera(LOGIC_WIDTH, LOGIC_HEIGHT, self._current_map)
        sp_x, sp_y = self._current_map.spawn_points

        # 读取玩家配置（若有），全部传入 Player 构造函数
        cfg = getattr(self._current_map, 'player_config', {})
        self.player1 = Player(
            player_id=0, player_name="玩家1",
            spawn_x=float(sp_x), spawn_y=float(sp_y),
            key_bind=self.p1_keys,
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
        self.player1.costume_id = cfg.get("costume_id", DEFAULT_COSTUME_ID)

        # 初始化游戏状态
        self._game_over = False
        self._game_win = False
        self._game_timer = 0.0
        self._prev_hp = None
        self._prev_score = 0
        self._prev_alive = True
        self._win_played = False
        self._death_played = False
        self._damage_flash_timer = 0.0
        self._stamina_flash_timer = 0.0
        self.jump_pressed = False
        self._player_lives_left = getattr(self._current_map, 'lives', 0)
        self._infinite_lives = self._player_lives_left == 0

        # 播放地图专属音乐
        self._play_world_music(self._current_map)

        self._world_initialized = True
        clear_costume_cache()  # 地图切换时清除缩放缓存，释放 Atlas 内存

    def _play_world_music(self, world):
        """根据地图配置播放背景音乐（支持合成音乐和文件音乐）。"""
        music_name = getattr(world, 'music', '')
        if music_name and music_name in ("home", "adventure", "danger", "victory"):
            # 合成音乐曲目
            music.play(music_name, fade_in_ms=1200)
        elif music_name:
            # 文件音乐（向后兼容）
            import os
            music_path = os.path.join(str(PROJECT_ROOT), 'music', music_name)
            if os.path.isfile(music_path):
                try:
                    music.play_file(music_path)
                except pygame.error:
                    music.play("adventure", fade_in_ms=1200)
            else:
                music.play("adventure", fade_in_ms=1200)
        else:
            # 默认：冒险主题
            music.play("adventure", fade_in_ms=1200)

    def launch_setting(self, from_page: int = PAGE_WORLD):
        """启动器：设置页面。保存来源页面，以便返回。"""
        # from_page 存储在 kwargs 中，由调用方传入
        pass

    def launch_default(self, page_id: int):
        """占位启动器。"""
        pass

    def _dispatch_launcher(self):
        """根据当前 page 和 _page_launch_kwargs 调用对应启动器。"""
        launcher = self._LAUNCHERS.get(self.page, self.launch_default)
        launcher(**self._page_launch_kwargs)

    def run(self):
        try:
            while self.running:
                self.dt = self.clock.tick(self.current_fps) / 1000.0
                music.update()

                # ----- 事件处理 -----
                for self.event in pygame.event.get():
                    if self.event.type == pygame.QUIT:
                        self.running = False
                    if self.event.type == pygame.VIDEORESIZE:
                        self.win_w, self.win_h = max(320, self.event.w), max(180, self.event.h)
                        self.win_surface = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
                        self.update_scale_param()
                        if self._current_map is not None:
                            self._current_map.invalidate_chunks()
                    if self.event.type == pygame.KEYDOWN:
                        if self.event.key == pygame.K_F1:
                            self.current_fps = min(self.current_fps + 10, MAX_FPS)
                            # [log removed]
                        if self.event.key == pygame.K_F2:
                            self.current_fps = max(self.current_fps - 10, MIN_FPS)
                            # [log removed]

                    # 页面分发
                    if self.page == PAGE_DEV:
                        self.map_browser.handle_dev_input(self.event)
                    elif self.page == PAGE_WORLD:
                        if self.event.type == pygame.KEYDOWN:
                            if self.event.key == pygame.K_ESCAPE:
                                self.set_page(PAGE_DEV)
                            elif self.event.key == pygame.K_BACKSPACE:
                                self._setting_from_page = PAGE_WORLD
                                try:
                                    self._setting_selected_fps_idx = _FPS_OPTIONS.index(self.current_fps)
                                except ValueError:
                                    self._setting_selected_fps_idx = 1
                                self._setting_fps_just_autodetected = False
                                self._setting_selected_row = 0
                                self.set_page(PAGE_SETTING)
                            elif self.event.key == self.player1.key_bind["jump"]:
                                self.jump_pressed = True
                            elif self.event.key == pygame.K_c:
                                # 切换时装
                                self.cids = sorted(COSTUMES.keys())
                                try:
                                    self.idx = self.cids.index(self.player1.costume_id)
                                    self.idx = (self.idx + 1) % len(self.cids)
                                except ValueError:
                                    self.idx = 0
                                self.player1.costume_id = self.cids[self.idx]
                                # [log removed]
                            elif self.event.key == self.player1.key_bind["fly"]:
                                # 切换飞行模式
                                self.player1.fly_mode = not self.player1.fly_mode
                                self.player1.v_x = 0.0
                                self.player1.v_y = 0.0
                                self.player1.is_climbing = False
                                self.jump_pressed = False
                                # [log removed]
                            elif self.event.key == pygame.K_F5:
                                # 调试：随机获得1-3个未生效的buff
                                import random as _rnd
                                from buff_system import BUFF_TYPES
                                self.active_ids = {b.buff_id for b in self.player1.buffs}
                                self.available = [bid for bid in BUFF_TYPES if bid not in self.active_ids]
                                if self.available:
                                    self.n = _rnd.randint(1, min(3, len(self.available)))
                                    self.chosen = _rnd.sample(self.available, self.n)
                                    for self.bid in self.chosen:
                                        self.bt = BUFF_TYPES[self.bid]
                                        self.dur = _rnd.uniform(3.0, 15.0)  # 必定有时限，最多15s
                                        self.p0 = _rnd.uniform(1, 30) if _rnd.random() < 0.6 else 0
                                        self.p1 = _rnd.uniform(1, 50) if _rnd.random() < 0.4 else 0
                                        self.player1.apply_buff(self.bid, (self.p0, self.p1), self.dur)
                            elif self.event.key == self.player1.key_bind["up"] or self.event.key == pygame.K_UP:
                                # W/↑键：可攀爬时进入攀爬，攀爬中向上
                                if not self.player1.fly_mode:
                                    if not self.player1.is_climbing and self.player1.can_climb:
                                        if self.player1.stamina >= 1.0:
                                            self.player1.try_start_climbing(self._current_map)
                                        else:
                                            self._stamina_flash_timer = self._stamina_flash_duration
                                    elif self.player1.is_climbing:
                                        if self.player1.stamina >= 1.0:
                                            self.player1.climb_move(1.0)
                                        else:
                                            self.player1.stop_climbing()
                                            self._stamina_flash_timer = self._stamina_flash_duration
                            elif self.event.key == self.player1.key_bind["down"] or self.event.key == pygame.K_DOWN:
                                # S/↓键：攀爬中则解除
                                if not self.player1.fly_mode and self.player1.is_climbing:
                                    self.player1.stop_climbing()
                    elif self.page == PAGE_SETTING:
                        self.settings.handle_setting_input(self.event)
                    elif self.page == PAGE_INIT:
                        if self.event.type == pygame.KEYDOWN:
                            if self.event.key == pygame.K_RETURN or self.event.key == pygame.K_SPACE:
                                if ls.is_loading_complete():
                                    self.set_page(PAGE_HOME)
                            elif self.event.key == pygame.K_ESCAPE:
                                # Esc 跳过加载直接进主页
                                ls.mark_loading_complete()
                                self.set_page(PAGE_HOME)
                        elif self.event.type == pygame.MOUSEBUTTONDOWN and self.event.button == 1:
                            if ls.is_loading_complete():
                                self.set_page(PAGE_HOME)
                    elif self.page == PAGE_HOME:
                        if self.event.type == pygame.KEYDOWN:
                            if self.event.key == pygame.K_ESCAPE:
                                self.set_page(PAGE_DEV)
                            elif self.event.key == pygame.K_q:
                                # Q 键快速退出
                                pygame.event.post(pygame.event.Event(pygame.QUIT))
                            else:
                                self.action = hp.handle_home_input(self.event)
                                if self.action == hp.MENU_START:
                                    self.set_page(PAGE_DEV)
                                elif self.action == hp.MENU_SETTINGS:
                                    self._setting_from_page = PAGE_HOME
                                    self._setting_selected_row = 0
                                    self._setting_fps_just_autodetected = False
                                    self.set_page(PAGE_SETTING)
                                elif self.action == hp.MENU_DEV:
                                    self.set_page(PAGE_DEV)
                                elif self.action == hp.MENU_QUIT:
                                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                        elif self.event.type == pygame.MOUSEMOTION:
                            hp.handle_home_mouse(
                                self.event.pos, LOGIC_WIDTH, LOGIC_HEIGHT, self.scale,
                                self.draw_offset_x, self.draw_offset_y)
                        elif self.event.type == pygame.MOUSEBUTTONDOWN and self.event.button == 1:
                            self.action = hp.handle_home_mouse(
                                self.event.pos, LOGIC_WIDTH, LOGIC_HEIGHT, self.scale,
                                self.draw_offset_x, self.draw_offset_y)
                            if self.action == hp.MENU_START:
                                self.set_page(PAGE_DEV)
                            elif self.action == hp.MENU_SETTINGS:
                                self._setting_from_page = PAGE_HOME
                                self._setting_selected_row = 0
                                self._setting_fps_just_autodetected = False
                                self.set_page(PAGE_SETTING)
                            elif self.action == hp.MENU_DEV:
                                self.set_page(PAGE_DEV)
                            elif self.action == hp.MENU_QUIT:
                                pygame.event.post(pygame.event.Event(pygame.QUIT))

                # ----- 页面逻辑 & 渲染 -----
                if self.page == PAGE_DEV:
                    self.map_browser.run_dev_page(self.dt)

                elif self.page == PAGE_WORLD:
                    self.keys = pygame.key.get_pressed()

                    # ---- 游戏状态检查 ----

                    # 计时器
                    self.wmode = self._current_map.mode if self._current_map else "free"
                    if not self._game_over and not self._game_win:
                        self._game_timer += self.dt
                        # 限时模式：时间到则失败
                        self.time_limit = getattr(self._current_map, 'time_limit', 0.0)
                        if self.wmode == "score_timed" and self.time_limit > 0 and self._game_timer >= self.time_limit:
                            self._game_over = True

                        # 积分目标模式：达到目标则胜利
                        self.score_goal = getattr(self._current_map, 'score_goal', 0)
                        if self.wmode == "score_target" and self.score_goal > 0 and self.player1.score >= self.score_goal:
                            self._game_win = True

                        # 探索模式：触碰终点则胜利
                        if self.wmode == "explore" and self.player1._reached_end:
                            self._game_win = True

                    # 死亡处理（限复活次数）
                    if not self.player1.alive and not self._game_over and not self._game_win:
                        self._player_lives_left, self._game_over = resolve_player_death(
                            self.player1, self._player_lives_left, self._infinite_lives)

                    # ---- Buff 系统 tick ----
                    if not self._game_over and not self._game_win and self.player1.alive:
                        self.player1.tick_buffs(self.dt)
                    # buff 属性修正
                    self.player1.refresh_movement_stats()
                    # 体力恢复速度（动态公式，三层结构）
                    self.stamina_ratio = self.player1.stamina / max(1, self.player1.stamina_max)
                    self.hp_ratio = self.player1.hp / max(1, self.player1.hp_max)
                    self.stamina_missing = self.player1.stamina_max - self.player1.stamina
                    self.base_stam_rec = (
                        (1.15 + 5.5 * (1 - self.stamina_ratio) + 0.85 * self.hp_ratio) * (0.85 + 0.25 * self.hp_ratio)
                        + 0.035 * self.stamina_missing
                        + 0.15 * ((1 - self.stamina_ratio) ** 2)
                        + 0.35 * ((1 - self.stamina_ratio) ** 3)
                        + 0.65 * ((1 - self.stamina_ratio) ** 4)
                    )
                    self.buf_stam_rec = self.player1.get_buff_stat("stamina_recovery", self.base_stam_rec)
                    self.buf_stam_cost = self.player1.get_buff_stat("stamina_cost", 1.0)
                    # 控制效果检查（铁意 buff 40 免疫定身/晕眩/压制/反向）
                    self.iron_will = self.player1.has_buff(40)
                    self.rooted = self.player1.has_buff(21) and not self.iron_will
                    self.stunned = self.player1.has_buff(28) and not self.iron_will
                    self.grounded = self.player1.has_buff(27) and not self.iron_will
                    self.hopping = self.player1.has_buff(33)
                    self.reversed_ctrl = ((self.player1.has_buff(23) or getattr(self.player1, '_confused', False))
                                     and not self.player1.has_buff(8) and not self.iron_will)

                    # ---- 移动物理（游戏结束/胜利时冻结）----
                    if not self._game_over and not self._game_win and self.player1.alive and not self.stunned:
                        if self.player1.fly_mode:
                            # ---- 飞行模式 ----
                            self.fly_dx, self.fly_dy = 0.0, 0.0
                            if self.keys[self.player1.key_bind["left"]] or self.keys[pygame.K_LEFT]:
                                self.fly_dx -= 1.0
                            if self.keys[self.player1.key_bind["right"]] or self.keys[pygame.K_RIGHT]:
                                self.fly_dx += 1.0
                            # 飞行模式朝向（与地面移动逻辑一致）
                            if (self.keys[self.player1.key_bind["right"]] or self.keys[pygame.K_RIGHT]) and \
                               not (self.keys[self.player1.key_bind["left"]] or self.keys[pygame.K_LEFT]):
                                self.player1.facing_right = True
                            elif (self.keys[self.player1.key_bind["left"]] or self.keys[pygame.K_LEFT]) and \
                                 not (self.keys[self.player1.key_bind["right"]] or self.keys[pygame.K_RIGHT]):
                                self.player1.facing_right = False
                            if self.keys[self.player1.key_bind["up"]] or self.keys[pygame.K_UP]:
                                self.fly_dy += 1.0
                            if self.keys[self.player1.key_bind["down"]] or self.keys[pygame.K_DOWN]:
                                self.fly_dy -= 1.0
                            # 直接操作坐标
                            self.player1._x += self.fly_dx * self.player1.fly_speed * self.dt
                            self.player1._y += self.fly_dy * self.player1.fly_speed * self.dt
                            self.player1.v_x = 0.0
                            self.player1.v_y = 0.0
                            # 钳制在地图边界内（循环世界不钳制）
                            if not self._current_map.loop_x:
                                self.player1._x = max(0.5, min(self.player1._x, self._current_map.width - 0.5))
                            if not self._current_map.loop_y:
                                self.player1._y = max(0.5, min(self.player1._y, self._current_map.height - 0.5))
                            # 更新接触池（用于绘制等）
                            self.grect = self.player1.get_game_rect()
                            self.player1.contact_pool = set()
                            self.player1.stand_pool = None
                        else:
                            # ---- 正常模式 ----
                            self.dir_x = 0.0
                            if not self.rooted and not self.hopping:
                                self.left_key = self.keys[self.player1.key_bind["left"]] or self.keys[pygame.K_LEFT]
                                self.right_key = self.keys[self.player1.key_bind["right"]] or self.keys[pygame.K_RIGHT]
                                if self.reversed_ctrl:
                                    self.left_key, self.right_key = self.right_key, self.left_key
                                if self.left_key:
                                    self.dir_x -= 0.35
                                if self.right_key:
                                    self.dir_x += 0.35
                                # 更新角色朝向（仅单方向按键时更新，同时按住保持原朝向）
                                if self.right_key and not self.left_key:
                                    self.player1.facing_right = True
                                elif self.left_key and not self.right_key:
                                    self.player1.facing_right = False
                            self.player1.move(self.dir_x)

                            # ---- 攀爬: W/↑向上 ----
                            self.sm = getattr(self.player1, '_stamina_mult', 1.0)
                            self.silenced = getattr(self.player1, '_silenced', False)
                            self.climb_up_cost = 14.0 * self.sm * self.buf_stam_cost * self.dt + 0.01
                            self.climb_idle_cost = 3.52 * self.sm * self.buf_stam_cost * self.dt + 0.01
                            # 攀爬上边界：人物中心到达梯子顶端（半腰位置），消耗挂住体力
                            self.climb_bound = getattr(self.player1, '_climb_top_y', None)
                            self.at_climb_bound = False
                            if self.climb_bound is not None and self.player1.is_climbing:
                                # 仅当靠近边界时吸附（防止远处瞬移）
                                if self.player1._y >= self.climb_bound - 0.05 and self.player1._y <= self.climb_bound + 2.0:
                                    self.player1._y = self.climb_bound  # 中心与方块上边界齐平（半腰）
                                    self.player1.v_y = 0.0
                                    self.at_climb_bound = True
                            if self.player1.is_climbing and (self.keys[self.player1.key_bind["up"]] or self.keys[pygame.K_UP]):
                                if self.at_climb_bound:
                                    # 已到顶端，消耗挂住体力
                                    if self.player1.stamina >= self.climb_idle_cost:
                                        if not self.silenced: self.player1.consume_stamina(3.52 * self.sm * self.buf_stam_cost * self.dt)
                                    else:
                                        self.player1.stop_climbing()
                                        self._stamina_flash_timer = self._stamina_flash_duration
                                elif self.player1.stamina >= self.climb_up_cost:
                                    self.player1.climb_move(1.0)
                                    if not self.silenced: self.player1.consume_stamina(14.0 * self.sm * self.buf_stam_cost * self.dt)
                                else:
                                    self.player1.stop_climbing()
                                    self._stamina_flash_timer = self._stamina_flash_duration
                            elif self.player1.is_climbing:
                                self.player1.v_y = 0.0
                                if self.player1.stamina >= self.climb_idle_cost:
                                    if not self.silenced: self.player1.consume_stamina(3.52 * self.sm * self.buf_stam_cost * self.dt)
                                else:
                                    self.player1.stop_climbing()
                                    self._stamina_flash_timer = self._stamina_flash_duration

                            # ---- 游泳: W/↑向上，攀爬优先 ----
                            self.swimming_now = False
                            self.up_held = self.keys[self.player1.key_bind["up"]] or self.keys[pygame.K_UP]
                            if not self.player1.is_climbing and self.player1.can_swim and not self.player1.has_buff(58):
                                if self.up_held:
                                    self.swim_cost = 21.0 * self.sm * self.buf_stam_cost * self.dt + 0.01
                                    if self.player1.stamina >= self.swim_cost:
                                        # 游泳上边界仅在主动游泳且体力足够时生效
                                        self.swim_bound = getattr(self.player1, '_swim_top_y', None)
                                        self.at_swim_bound = False
                                        if self.swim_bound is not None:
                                            if self.player1._y >= self.swim_bound - 0.05 and self.player1._y <= self.swim_bound + 2.0:
                                                self.player1._y = self.swim_bound  # 中心与水面齐平（半腰）
                                                self.player1.v_y = 0.0
                                                self.at_swim_bound = True
                                        if self.at_swim_bound:
                                            if not self.silenced: self.player1.consume_stamina(21.0 * self.sm * self.buf_stam_cost * self.dt)
                                            self.swimming_now = True
                                        else:
                                            self.swim_v = self.player1._swim_force
                                            self.player1.v_y = self.swim_v  # 匀速上游
                                            if not self.silenced: self.player1.consume_stamina(21.0 * self.sm * self.buf_stam_cost * self.dt)
                                            self.swimming_now = True
                                    else:
                                        # 体力耗尽：不吸附、不游泳，自然下沉
                                        self._stamina_flash_timer = self._stamina_flash_duration

                            # ---- 体力恢复（攀爬中/水中按↑时不恢复，防止耗尽-恢复循环） ----
                            self.can_recover = (not self.player1.is_climbing
                                           and not self.swimming_now
                                           and not (self.player1.can_swim and self.up_held)
                                           and not (self.player1.can_climb and self.up_held and not self.player1.is_climbing))
                            if self.can_recover and self.player1.stamina < self.player1.stamina_max:
                                self.player1.recover_stamina(self.buf_stam_rec * self.dt)

                            # ---- 上岸：水面上 + 近岸 + 跳跃键 ----
                            self.shore_exit_done = False
                            if (self.jump_pressed and not self.grounded
                                and self.player1.can_swim and self.swimming_now
                                and getattr(self.player1, '_near_shore', False)
                                and self.player1.stamina >= 25):
                                self._shore_pending = getattr(self.player1, '_shore_exit_pending', False)
                                if not self._shore_pending:
                                    # 高速上岸 + 临时空气墙：极速完成，不受液体阻力影响
                                    self.player1.v_y = 32.0  # 高速向上
                                    self.player1.v_x = 0.0
                                    if not self.silenced: self.player1.consume_stamina(25)
                                    self.player1.apply_buff(58, (), 0.3)
                                    self.player1._shore_exit_pending = 'rise'  # 上升阶段
                                    self.player1._shore_exit_dir = self.player1._shore_dir
                                    self.player1._shore_exit_bound = getattr(self.player1, '_swim_top_y', None)
                                    sfx.play_jump()
                                    self.shore_exit_done = True
                                    self.jump_pressed = False
                            # 上岸后续：空气墙逻辑（到达高度→竖直停，再水平推→到位停）
                            self._shore_state = getattr(self.player1, '_shore_exit_pending', False)
                            if self._shore_state and not self.shore_exit_done:
                                self.exit_dir = self.player1._shore_exit_dir
                                self.swim_bound = getattr(self.player1, '_shore_exit_bound', None)
                                self.feet_y = self.player1._y - self.player1._h / 2
                                if self._shore_state == 'rise':
                                    if self.swim_bound is not None and self.feet_y >= self.swim_bound:
                                        # 竖直空气墙：到达水面高度，锁 v_y，记录起始位置
                                        self.player1.v_y = 0.0
                                        self.player1.v_x = self.exit_dir * 16.0
                                        self.player1._shore_slide_start_x = self.player1._x
                                        self.player1._shore_exit_pending = 'slide'
                                elif self._shore_state == 'slide':
                                    # 水平空气墙：滑够 0.55 格（半身宽+岸边容差）即停
                                    if abs(self.player1._x - self.player1._shore_slide_start_x) >= 0.55:
                                        self.player1.v_x = 0.0
                                        self.player1._shore_exit_pending = False
                                    elif not self.player1.has_buff(58):
                                        self.player1._shore_exit_pending = False
                                # buff 过期兜底
                                if self.player1._shore_exit_pending and not self.player1.has_buff(58):
                                    self.player1._shore_exit_pending = False

                            # ---- 正常跳跃 ----
                            if self.jump_pressed and not self.grounded and not self.shore_exit_done:
                                self.can_actually_jump = self.player1.on_ground or self.player1.is_climbing
                                self.jump_cost = 15.0 * self.sm * self.buf_stam_cost + 0.01
                                if self.player1.stamina >= self.jump_cost:
                                    if self.player1.jump():
                                        if not self.silenced: self.player1.consume_stamina(15.0 * self.sm * self.buf_stam_cost)
                                        sfx.play_jump()
                                elif self.can_actually_jump:
                                    self._stamina_flash_timer = self._stamina_flash_duration
                                self.jump_pressed = False

                            self.player1.update_physics(self.dt, self._current_map)
                            self.player1.collide_with_world(self._current_map, self.dt)

                            # 攀爬中着陆或离开可攀爬方块：自动解除
                            if self.player1.is_climbing and (self.player1.on_ground or not self.player1.can_climb):
                                self.player1.is_climbing = False
                            # 上岸后着陆或离开水面：清除上岸待处理状态
                            if getattr(self.player1, '_shore_exit_pending', False):
                                if self.player1.on_ground or not self.player1.can_swim:
                                    self.player1._shore_exit_pending = False

                    # A keydown is consumed by this world frame even when a status blocks it.
                    self.jump_pressed = False
                    self.px, self.py = self.player1.get_center()
                    self.camera.follow(self.px, self.py)

                    # 渲染世界
                    self.fill_color = getattr(self._current_map, 'fill_color', (30, 30, 30))
                    self.logic_surface.fill(self.fill_color)
                    self._current_map.draw(self.logic_surface, self.camera)

                    # 绘制玩家（时装系统）
                    self.grect = self.player1.get_game_rect()
                    # 时装位图底部有透明行，向下偏移使脚部对齐碰撞箱底部
                    self.shift = self.grect.h * 0.22
                    self.cam_scale = self.camera.scale
                    self.sx = (self.grect.x - self.camera.x) * self.cam_scale + self.camera.logic_width / 2
                    self.sy_top = self.camera.logic_height / 2 - (self.grect.y + self.grect.h - self.shift - self.camera.y) * self.cam_scale
                    self.sw = self.grect.w * self.cam_scale
                    self.sh = self.grect.h * self.cam_scale
                    self.player_screen_rect = pygame.Rect(self.sx, self.sy_top, self.sw, self.sh)

                    # ---- 动画状态判定 ----
                    if self.player1.fly_mode:
                        self.anim_state = "idle"
                    elif self.player1.is_climbing:
                        self.anim_state = "climb"
                    elif not self.player1.on_ground:
                        self.anim_state = "jump"
                    elif abs(self.player1.v_x) > 0.3:
                        self.anim_state = "walk"
                    else:
                        self.anim_state = "idle"

                    # 推进动画计时器并循环帧
                    self.info = get_costume_anim_info(self.player1.costume_id)
                    if self.info and self.anim_state in self.info:
                        self.frame_count = self.info[self.anim_state]
                        if self.frame_count > 1:
                            self.player1._anim_timer += self.dt
                            if self.player1._anim_timer >= 0.15:  # ~6.7 fps 行走周期
                                self.player1._anim_timer -= 0.15
                                self.player1._anim_frame = (self.player1._anim_frame + 1) % self.frame_count
                    else:
                        self.player1._anim_frame = 0

                    render_costume_direct(self.logic_surface, self.player1.costume_id, self.player_screen_rect,
                                          flip_h=not self.player1.facing_right,
                                          anim_state=self.anim_state,
                                          anim_frame=self.player1._anim_frame)

                    # ---- Buff 视线效果（只影响世界/生物，不影响 UI） ----
                    # Buff: 发光 (50) 自身发光照亮周围
                    if self.player1.has_buff(50):
                        self.px, self.py = self.player1.get_center()
                        self.cam_scale = self.camera.scale
                        self.sx = (self.px - self.camera.x) * self.cam_scale + self.camera.logic_width / 2
                        self.sy = self.camera.logic_height / 2 - (self.py - self.camera.y) * self.cam_scale
                        self.glow_radius = 120
                        self.glow = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
                        for self.i in range(8, 0, -1):
                            self.alpha = 30 - self.i * 3
                            self.r = self.glow_radius * self.i / 8
                            pygame.draw.circle(self.glow, (255, 240, 180, max(0, self.alpha)),
                                               (self.glow_radius, self.glow_radius), int(self.r))
                        self.logic_surface.blit(self.glow, (self.sx - self.glow_radius, self.sy - self.glow_radius), special_flags=pygame.BLEND_ADD)

                    # Buff: 失明 (24) 屏幕变亮黄色（清明 buff 8 免疫）
                    if self.player1.has_buff(24) and not self.player1.has_buff(8):
                        self.blind_overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
                        self.blind_overlay.fill((255, 240, 80, 140))
                        self.logic_surface.blit(self.blind_overlay, (0, 0))

                    # Buff: 视野受限 (25) 缩小视野半径（清明 buff 8 免疫）
                    if self.player1.has_buff(25) and not self.player1.has_buff(8):
                        self.vision_radius = 5.0  # 默认半径（格）
                        for self.b in self.player1.buffs:
                            if self.b.buff_id == 25 and self.b.params:
                                self.vision_radius = float(self.b.params[0])
                        self.px, self.py = self.player1.get_center()
                        self.cam_scale = self.camera.scale
                        self.sx = (self.px - self.camera.x) * self.cam_scale + self.camera.logic_width / 2
                        self.sy = self.camera.logic_height / 2 - (self.py - self.camera.y) * self.cam_scale
                        self.vision_radius_px = int(self.vision_radius * 24 * self.cam_scale)
                        self.dark = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
                        self.dark.fill((0, 0, 0, 220))
                        if self.vision_radius_px > 0:
                            pygame.draw.circle(self.dark, (0, 0, 0, 0), (int(self.sx), int(self.sy)), self.vision_radius_px)
                        self.logic_surface.blit(self.dark, (0, 0))

                    # ---- HP 血条 ----
                    # ---- 音效检测 ----
                    if self._prev_score < self.player1.score:
                        sfx.play_pickup()
                    self._prev_score = self.player1.score

                    if self._prev_alive and not self.player1.alive and not self._death_played:
                        sfx.play_death()
                        music.stop(fade_out_ms=600)
                        self._death_played = True
                    if not self.player1.alive:
                        self._prev_alive = self.player1.alive
                    else:
                        self._prev_alive = True
                        self._death_played = False

                    if self._game_win and not self._win_played:
                        sfx.play_win()
                        music.play("victory", fade_in_ms=300, loops=0)
                        self._win_played = True

                    # 低血量自动切换危险主题
                    if self.player1.alive and not self._game_win and not self._game_over:
                        self.hp_ratio = self.player1.hp / max(1, self.player1.hp_max)
                        if self.hp_ratio < 0.25 and music.get_current_track() != "danger":
                            music.play("danger", fade_in_ms=500)
                        elif self.hp_ratio >= 0.25 and music.get_current_track() == "danger":
                            # 恢复 → 回到地图音乐
                            self._play_world_music(self._current_map)

                    self.hud.draw_hp_bar(self.logic_surface, self.player1, self.dt)
                    self.hud.draw_stamina_bar(self.logic_surface, self.player1, self.dt)
                    self.hud.draw_player_info(self.logic_surface, self.player1, self.dt)

                    # ---- 濒死滤镜 ----
                    self.hud.draw_near_death_vignette(self.logic_surface, self.player1)
                    self.hud.draw_buff_status(self.logic_surface, self.player1, self.dt)

                    # ---- 积分显示（顶部居中）----
                    self.score_text = f"* {self.player1.score}"
                    gt.draw(self.logic_surface, self.score_text,
                                       LOGIC_WIDTH // 2, 16, 22,
                                       (255, 220, 80), "mono", shadow=True, center_x=True)

                    # ---- 计时器（积分限时模式）----
                    self.wmode = self._current_map.mode if self._current_map else "free"
                    self.time_limit = getattr(self._current_map, 'time_limit', 0.0)
                    if self.wmode == "score_timed" and self.time_limit > 0:
                        self.remaining = max(0, self.time_limit - self._game_timer)
                        self.timer_text = f"{int(self.remaining // 60):02d}:{int(self.remaining % 60):02d}"
                        self.timer_color = (255, 80, 80) if self.remaining < 30 else (255, 255, 255)
                        gt.draw(self.logic_surface, self.timer_text,
                                           LOGIC_WIDTH // 2, 42, 20,
                                           self.timer_color, "mono", shadow=True, center_x=True)

                    # ---- 积分目标进度（积分目标模式）----
                    self.score_goal = getattr(self._current_map, 'score_goal', 0)
                    if self.wmode == "score_target" and self.score_goal > 0:
                        self.goal_text = f"Goal: {self.score_goal} ({int(self.player1.score / max(1, self.score_goal) * 100)}%)"
                        gt.draw(self.logic_surface, self.goal_text,
                                           LOGIC_WIDTH // 2, 42, 15,
                                           (200, 220, 255), "mono", shadow=True, center_x=True)

                    # ---- 命数已移至体力条下方 (draw_player_info) ----

                    # ---- 游戏结束/胜利叠加层 ----
                    if self._game_over:
                        self.overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
                        self.overlay.fill((0, 0, 0, 180))
                        self.logic_surface.blit(self.overlay, (0, 0))
                        self.y = LOGIC_HEIGHT // 2 - 80
                        self.y = draw_text_center(self.logic_surface, FONT56, "游 戏 失 败", self.y, (255, 80, 60)) + 16
                        if self.wmode == "score_timed":
                            self.y = draw_text_center(self.logic_surface, FONT28, f"最终得分: {self.player1.score}", self.y, (255, 220, 80)) + 8
                        draw_text_center(self.logic_surface, FONT24, "按 ESC 返回", self.y + 16, (180, 180, 180))

                    elif self._game_win:
                        self.overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
                        self.overlay.fill((0, 0, 0, 120))
                        self.logic_surface.blit(self.overlay, (0, 0))
                        self.y = LOGIC_HEIGHT // 2 - 80
                        self.y = draw_text_center(self.logic_surface, FONT56, "通 关！", self.y, (100, 255, 100)) + 16
                        self.y = draw_text_center(self.logic_surface, FONT28, f"最终得分: {self.player1.score}", self.y, (255, 220, 80)) + 8
                        draw_text_center(self.logic_surface, FONT24, "按 ESC 返回", self.y + 16, (180, 180, 180))

                    # 右上角 FPS
                    self.fps_text = f"FPS {int(self.clock.get_fps())}"
                    gt.draw(self.logic_surface, self.fps_text,
                                       LOGIC_WIDTH - 16, 8, 21,
                                       (255, 255, 255), "mono", shadow=True, right_x=True)
                    # 坐标（FPS 下方）
                    self.px, self.py = self.player1.get_center()
                    self.coord_text = f"({self.px:.1f}, {self.py:.1f})"
                    gt.draw(self.logic_surface, self.coord_text,
                                       LOGIC_WIDTH - 16, 30, 16,
                                       (200, 210, 230), "mono", shadow=True, right_x=True)

                    # 飞行模式指示
                    if self.player1.fly_mode:
                        gt.draw(self.logic_surface, "[FLY]",
                                           LOGIC_WIDTH // 2, LOGIC_HEIGHT - 36, 15,
                                           (100, 255, 200), "mono", shadow=True, center_x=True)

                    self.f += 1
                    self.state_str = ("飞行" if self.player1.fly_mode
                                 else ("攀爬中" if self.player1.is_climbing
                                       else ("可攀爬" if self.player1.can_climb
                                             else ("地面" if self.player1.on_ground else "浮空"))))
                    # [log removed]
                    self.costume_name = COSTUMES.get(self.player1.costume_id, {}).get("name", "?")
                    # [log removed]


                elif self.page == PAGE_SETTING:
                    self.settings.run_setting_page(self.dt)

                elif self.page == PAGE_INIT:
                    # ---- 加载界面 ----
                    # 模拟加载进度（根据经过时间）
                    import time as _time
                    self.load_elapsed = _time.time() - ls._start_time
                    self.simulated_progress = min(1.0, self.load_elapsed / 2.8)  # 约2.8秒加载完成
                    ls.set_progress(self.simulated_progress)
                    if self.simulated_progress >= 1.0 and not ls.is_loading_complete():
                        ls.mark_loading_complete()
                    ls.run_loading_screen(self.logic_surface, self.dt, LOGIC_WIDTH, LOGIC_HEIGHT)

                elif self.page == PAGE_HOME:
                    # ---- 游戏主页 ----
                    hp.run_home_page(self.logic_surface, self.dt, LOGIC_WIDTH, LOGIC_HEIGHT)

                # ----- 最终输出 -----
                # 页面过渡淡入效果
                if self._transition_alpha > self._transition_target:
                    self._transition_alpha = max(self._transition_target, self._transition_alpha - self._transition_speed * self.dt)
                elif self._transition_alpha < self._transition_target:
                    self._transition_alpha = min(self._transition_target, self._transition_alpha + self._transition_speed * self.dt)

                self.win_surface.fill((0, 0, 0))
                self.scaled_surf = pygame.transform.scale(self.logic_surface, (int(LOGIC_WIDTH * self.scale), int(LOGIC_HEIGHT * self.scale)))
                self.win_surface.blit(self.scaled_surf, (self.draw_offset_x, self.draw_offset_y))

                # 过渡黑幕覆盖
                if self._transition_alpha > 1:
                    self.overlay = pygame.Surface((self.win_w, self.win_h), pygame.SRCALPHA)
                    self.overlay.fill((0, 0, 0, int(self._transition_alpha)))
                    self.win_surface.blit(self.overlay, (0, 0))

                pygame.display.flip()
        finally:
            pygame.quit()
