from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT, INIT_WIN_W, INIT_WIN_H, MIN_FPS, MAX_FPS, DEFAULT_FPS
import sfx
import music
from pixel_roamer.ui.config import (FONT20, FONT24, FONT28, FONT40, _FPS_OPTIONS, _SETTING_ROWS)
from pixel_roamer.ui.widgets import (draw_text_center, draw_text_left, draw_text_right)

class SettingsPage:
    """Settings behavior; shared session and viewport come from app."""

    def __init__(self, app):
        self.app = app

    def _run_fps_benchmark(self) -> int:
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

    def _draw_volume_bar(self, surf, x, y, w, h, value, is_active):
        """绘制音量条：value 0~1。"""
        bg = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surf, (20, 20, 35), bg, border_radius=4)
        if is_active:
            pygame.draw.rect(surf, (100, 180, 255), bg, 2, border_radius=4)
        fill_w = int((w - 4) * value)
        if fill_w > 0:
            fill_color = (80, 200, 120) if is_active else (60, 150, 90)
            pygame.draw.rect(surf, fill_color, (x + 2, y + 2, fill_w, h - 4), border_radius=2)

    def run_setting_page(self, dt: float):
        """设置页面渲染。"""

        sfx_vol = sfx.get_sfx_volume()
        mus_vol = sfx.get_music_volume()

        self.app.logic_surface.fill((20, 20, 40))

        y = 60
        y = draw_text_center(self.app.logic_surface, FONT40, "设置 (SETTING)", y, (100, 200, 255)) + 24

        # 辅助：绘制一行
        def _row(label, value_text, row_idx, hint="← → 调整"):
            nonlocal y
            is_active = (self.app._setting_selected_row == row_idx)
            row_h = 46
            bg = pygame.Rect(200, y - 2, LOGIC_WIDTH - 400, row_h)
            pygame.draw.rect(self.app.logic_surface, (40, 40, 70) if is_active else (25, 25, 45), bg, border_radius=4)
            if is_active:
                pygame.draw.rect(self.app.logic_surface, (100, 180, 255), bg, 2, border_radius=4)
            draw_text_left(self.app.logic_surface, FONT28, label, 240, y + 7, (255, 255, 255))
            draw_text_right(self.app.logic_surface, FONT24, value_text, LOGIC_WIDTH - 270, y + 9, (220, 220, 220))
            draw_text_right(self.app.logic_surface, FONT20, hint, LOGIC_WIDTH - 240, y + 9, (140, 140, 160))
            y += row_h + 6

        # 0: FPS
        fps_label = str(self.app.current_fps)
        _row(f"帧率上限", f"{fps_label} FPS", 0)

        # 1: 自动检测
        _row("自动检测设备最佳帧率", "Enter 执行", 1, "Enter")

        # 2: 音效音量
        _row("音效音量", f"{int(sfx_vol * 100)}%", 2)
        self._draw_volume_bar(self.app.logic_surface, 340, y - 48, LOGIC_WIDTH - 680, 16, sfx_vol, self.app._setting_selected_row == 2)

        # 3: 音乐音量（预留）
        _row("音乐音量", f"{int(mus_vol * 100)}%", 3)
        self._draw_volume_bar(self.app.logic_surface, 340, y - 48, LOGIC_WIDTH - 680, 16, mus_vol, self.app._setting_selected_row == 3)

        if self.app._setting_fps_just_autodetected:
            draw_text_center(self.app.logic_surface, FONT20, f"检测结果：{fps_label} FPS 已自动设定", LOGIC_HEIGHT - 86, (100, 255, 100))

        draw_text_center(self.app.logic_surface, FONT20, "↑ ↓ 选择    ← → 调整    Enter 确认    Esc 返回", LOGIC_HEIGHT - 58, (140, 140, 180))

    def handle_setting_input(self, event):
        """处理设置页面的键盘事件。"""

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP:
            self.app._setting_selected_row = (self.app._setting_selected_row - 1) % _SETTING_ROWS
            self.app._setting_fps_just_autodetected = False
            sfx.play_click()
        elif event.key == pygame.K_DOWN:
            self.app._setting_selected_row = (self.app._setting_selected_row + 1) % _SETTING_ROWS
            self.app._setting_fps_just_autodetected = False
            sfx.play_click()
        elif event.key == pygame.K_LEFT:
            if self.app._setting_selected_row == 0:
                self.app._setting_selected_fps_idx = (self.app._setting_selected_fps_idx - 1) % len(_FPS_OPTIONS)
                self.app._setting_fps_just_autodetected = False
                self.app.current_fps = _FPS_OPTIONS[self.app._setting_selected_fps_idx]
                sfx.play_click()
            elif self.app._setting_selected_row == 2:
                sfx.set_sfx_volume(sfx.get_sfx_volume() - 0.05)
                sfx.play_click()
            elif self.app._setting_selected_row == 3:
                sfx.set_music_volume(sfx.get_music_volume() - 0.05)
                music.set_volume(sfx.get_music_volume())
                sfx.play_click()
        elif event.key == pygame.K_RIGHT:
            if self.app._setting_selected_row == 0:
                self.app._setting_selected_fps_idx = (self.app._setting_selected_fps_idx + 1) % len(_FPS_OPTIONS)
                self.app._setting_fps_just_autodetected = False
                self.app.current_fps = _FPS_OPTIONS[self.app._setting_selected_fps_idx]
                sfx.play_click()
            elif self.app._setting_selected_row == 2:
                sfx.set_sfx_volume(sfx.get_sfx_volume() + 0.05)
                sfx.play_click()
            elif self.app._setting_selected_row == 3:
                sfx.set_music_volume(sfx.get_music_volume() + 0.05)
                music.set_volume(sfx.get_music_volume())
                sfx.play_click()
        elif event.key == pygame.K_RETURN:
            if self.app._setting_selected_row == 1:
                detected = self._run_fps_benchmark()
                try:
                    self.app._setting_selected_fps_idx = _FPS_OPTIONS.index(detected)
                except ValueError:
                    self.app._setting_selected_fps_idx = 1
                self.app._setting_fps_just_autodetected = True
                self.app.current_fps = detected
        elif event.key == pygame.K_ESCAPE:
            self.app.set_page_no_launch(self.app._setting_from_page)
