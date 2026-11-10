from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
from camera import Camera
from creature import Player
from maps import get_map, list_maps
from costumes import COSTUMES, DEFAULT_COSTUME_ID, clear_costume_cache
import music
import loading_screen as ls
import home_page as hp
from pixel_roamer.ui.config import GAME_NAME_CN, GAME_NAME_EN, PAGE_DEV, PAGE_HOME, PAGE_INFINITE_WORLD, PAGE_INIT, PAGE_SETTING, PAGE_WORLD, _FPS_OPTIONS

from pathlib import Path
from pixel_roamer.world_session import WorldSession
from pixel_roamer.world_view import WorldView

from pixel_roamer.ui.hud import HudRenderer
from pixel_roamer.ui.settings import SettingsPage
from pixel_roamer.ui.references import ReferenceBrowser
from pixel_roamer.ui.map_browser import MapBrowser
from pixel_roamer.ui.map_selector import MapSelector

PROJECT_ROOT = Path(__file__).resolve().parents[1]

class GameApp:
    """Own the application lifetime, session state and page coordination."""

    def __init__(self):
        self.session = WorldSession(self)
        self.world_view = WorldView(self)
        self.hud = HudRenderer(self)
        self.settings = SettingsPage(self)
        self.references = ReferenceBrowser(self)
        self.map_browser = MapBrowser(self)
        self.map_selector = MapSelector(self)
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

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                self.win_w, self.win_h = max(320, event.w), max(180, event.h)
                self.win_surface = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
                self.update_scale_param()
                if self._current_map is not None:
                    self._current_map.invalidate_chunks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.current_fps = min(self.current_fps + 10, MAX_FPS)
                if event.key == pygame.K_F2:
                    self.current_fps = max(self.current_fps - 10, MIN_FPS)

            # 页面分发
            if self.page == PAGE_DEV:
                self.map_browser.handle_dev_input(event)
            elif self.page == PAGE_WORLD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_page(PAGE_DEV)
                    elif event.key == pygame.K_BACKSPACE:
                        self._setting_from_page = PAGE_WORLD
                        try:
                            self._setting_selected_fps_idx = _FPS_OPTIONS.index(self.current_fps)
                        except ValueError:
                            self._setting_selected_fps_idx = 1
                        self._setting_fps_just_autodetected = False
                        self._setting_selected_row = 0
                        self.set_page(PAGE_SETTING)
                    elif event.key == self.player1.key_bind["jump"]:
                        self.jump_pressed = True
                    elif event.key == pygame.K_c:
                        # 切换时装
                        cids = sorted(COSTUMES.keys())
                        try:
                            idx = cids.index(self.player1.costume_id)
                            idx = (idx + 1) % len(cids)
                        except ValueError:
                            idx = 0
                        self.player1.costume_id = cids[idx]
                    elif event.key == self.player1.key_bind["fly"]:
                        # 切换飞行模式
                        self.player1.fly_mode = not self.player1.fly_mode
                        self.player1.v_x = 0.0
                        self.player1.v_y = 0.0
                        self.player1.is_climbing = False
                        self.jump_pressed = False
                    elif event.key == pygame.K_F5:
                        # 调试：随机获得1-3个未生效的buff
                        import random as _rnd
                        from buff_system import BUFF_TYPES
                        active_ids = {b.buff_id for b in self.player1.buffs}
                        available = [bid for bid in BUFF_TYPES if bid not in active_ids]
                        if available:
                            n = _rnd.randint(1, min(3, len(available)))
                            chosen = _rnd.sample(available, n)
                            for bid in chosen:
                                bt = BUFF_TYPES[bid]
                                dur = _rnd.uniform(3.0, 15.0)  # 必定有时限，最多15s
                                p0 = _rnd.uniform(1, 30) if _rnd.random() < 0.6 else 0
                                p1 = _rnd.uniform(1, 50) if _rnd.random() < 0.4 else 0
                                self.player1.apply_buff(bid, (p0, p1), dur)
                    elif event.key == self.player1.key_bind["up"] or event.key == pygame.K_UP:
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
                    elif event.key == self.player1.key_bind["down"] or event.key == pygame.K_DOWN:
                        # S/↓键：攀爬中则解除
                        if not self.player1.fly_mode and self.player1.is_climbing:
                            self.player1.stop_climbing()
            elif self.page == PAGE_SETTING:
                self.settings.handle_setting_input(event)
            elif self.page == PAGE_INIT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if ls.is_loading_complete():
                            self.set_page(PAGE_HOME)
                    elif event.key == pygame.K_ESCAPE:
                        # Esc 跳过加载直接进主页
                        ls.mark_loading_complete()
                        self.set_page(PAGE_HOME)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ls.is_loading_complete():
                        self.set_page(PAGE_HOME)
            elif self.page == PAGE_HOME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_page(PAGE_DEV)
                    elif event.key == pygame.K_q:
                        # Q 键快速退出
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    else:
                        action = hp.handle_home_input(event)
                        if action == hp.MENU_START:
                            self.set_page(PAGE_DEV)
                        elif action == hp.MENU_SETTINGS:
                            self._setting_from_page = PAGE_HOME
                            self._setting_selected_row = 0
                            self._setting_fps_just_autodetected = False
                            self.set_page(PAGE_SETTING)
                        elif action == hp.MENU_DEV:
                            self.set_page(PAGE_DEV)
                            self._dev_block_browser = True
                        elif action == hp.MENU_QUIT:
                            pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.type == pygame.MOUSEMOTION:
                    hp.handle_home_mouse(
                        event.pos, LOGIC_WIDTH, LOGIC_HEIGHT, self.scale,
                        self.draw_offset_x, self.draw_offset_y)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = hp.handle_home_mouse(
                        event.pos, LOGIC_WIDTH, LOGIC_HEIGHT, self.scale,
                        self.draw_offset_x, self.draw_offset_y)
                    if action == hp.MENU_START:
                        self.set_page(PAGE_DEV)
                    elif action == hp.MENU_SETTINGS:
                        self._setting_from_page = PAGE_HOME
                        self._setting_selected_row = 0
                        self._setting_fps_just_autodetected = False
                        self.set_page(PAGE_SETTING)
                    elif action == hp.MENU_DEV:
                        self.set_page(PAGE_DEV)
                        self._dev_block_browser = True
                    elif action == hp.MENU_QUIT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _draw_current_page(self, dt):
        if self.page == PAGE_DEV:
            self.map_browser.run_dev_page(dt)

        elif self.page == PAGE_WORLD:
            self.session.advance(dt)
            self.world_view.draw(dt)


        elif self.page == PAGE_SETTING:
            self.settings.run_setting_page(dt)

        elif self.page == PAGE_INIT:
            # ---- 加载界面 ----
            # 模拟加载进度（根据经过时间）
            import time as _time
            load_elapsed = _time.time() - ls._start_time
            simulated_progress = min(1.0, load_elapsed / 2.8)  # 约2.8秒加载完成
            ls.set_progress(simulated_progress)
            if simulated_progress >= 1.0 and not ls.is_loading_complete():
                ls.mark_loading_complete()
            ls.run_loading_screen(self.logic_surface, dt, LOGIC_WIDTH, LOGIC_HEIGHT)

        elif self.page == PAGE_HOME:
            # ---- 游戏主页 ----
            hp.run_home_page(self.logic_surface, dt, LOGIC_WIDTH, LOGIC_HEIGHT)

    def _present_frame(self, dt):
        if self._transition_alpha > self._transition_target:
            self._transition_alpha = max(self._transition_target, self._transition_alpha - self._transition_speed * dt)
        elif self._transition_alpha < self._transition_target:
            self._transition_alpha = min(self._transition_target, self._transition_alpha + self._transition_speed * dt)

        self.win_surface.fill((0, 0, 0))
        scaled_surf = pygame.transform.scale(self.logic_surface, (int(LOGIC_WIDTH * self.scale), int(LOGIC_HEIGHT * self.scale)))
        self.win_surface.blit(scaled_surf, (self.draw_offset_x, self.draw_offset_y))

        # 过渡黑幕覆盖
        if self._transition_alpha > 1:
            overlay = pygame.Surface((self.win_w, self.win_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self._transition_alpha)))
            self.win_surface.blit(overlay, (0, 0))

        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                dt = self.clock.tick(self.current_fps) / 1000.0
                music.update()
                self._handle_events()
                if not self.running:
                    break
                self._draw_current_page(dt)
                self._present_frame(dt)
        finally:
            pygame.quit()
