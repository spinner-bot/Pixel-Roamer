"""Settings with shared pixel styling and pointer/keyboard control parity."""
from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
import sfx
import music
import game_text as gt
from pixel_roamer.ui.config import PAGE_WORLD, _FPS_OPTIONS, _SETTING_ROWS
from pixel_roamer.ui.theme import PALETTE as P, panel, key_hint


class SettingsPage:
    def __init__(self, app):
        self.app = app
        self._drag_row = None

    @staticmethod
    def rows():
        return [pygame.Rect(230, 220 + index * 110, 1140, 92) for index in range(4)]

    @staticmethod
    def slider(row):
        return pygame.Rect(790, 220 + row * 110 + 38, 430, 18)

    def _run_fps_benchmark(self):
        surface = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT))
        clock = pygame.time.Clock()
        start = pygame.time.get_ticks()
        frames = 0
        while pygame.time.get_ticks() - start < 800:
            if pygame.event.peek(pygame.QUIT):
                self.app.running = False
                return self.app.current_fps
            surface.fill((0, 0, 0))
            for i in range(50):
                pygame.draw.rect(surface, (i * 5 % 255, i * 3 % 255, i * 7 % 255),
                                 (i * 20 % LOGIC_WIDTH, i * 15 % LOGIC_HEIGHT, 80, 60))
            clock.tick(1000)
            frames += 1
        measured = frames / 0.8 * 0.9
        return max((option for option in _FPS_OPTIONS if option <= measured), default=30)

    def run_setting_page(self, dt):
        surface = self.app.logic_surface
        surface.fill(P['background'])
        panel(surface, (64, 64, 150, 46))
        gt.draw(surface, '返回  Esc', 139, 76, 21, P['text'], 'sans', center_x=True)
        title = '暂停与设置' if self.app._setting_from_page == PAGE_WORLD else '设置'
        gt.draw(surface, title, 230, 72, 48, P['text'], 'sans')
        gt.draw(surface, '即时调整，返回后继续漫游。', 232, 144, 21, P['muted'], 'sans')
        labels = ['帧率上限', '快速性能评估', '音效音量', '音乐音量']
        hints = ['左右键切换，也可点击右侧按钮', 'Enter 执行；评估后仍可手动选择',
                 '点击或拖动右侧音量条', '点击或拖动右侧音量条']
        for index, rect in enumerate(self.rows()):
            panel(surface, rect, index == self.app._setting_selected_row)
            gt.draw(surface, labels[index], rect.x + 26, rect.y + 13, 27, P['text'], 'sans')
            gt.draw(surface, hints[index], rect.x + 27, rect.y + 56, 18, P['muted'], 'sans')
            if index == 0:
                gt.draw(surface, f'{self.app.current_fps} FPS', 1130, rect.y + 26, 30, P['accent'], right_x=True)
                for x, text in ((1190, '-'), (1270, '+')):
                    panel(surface, (x, rect.y + 18, 58, 54))
                    gt.draw(surface, text, x + 29, rect.y + 28, 30, P['text'], center_x=True)
            elif index == 1:
                text = '评估完成' if self.app._setting_fps_just_autodetected else '开始评估  Enter'
                gt.draw(surface, text, rect.right - 34, rect.y + 30, 24, P['mint'], 'sans', right_x=True)
            else:
                value = sfx.get_sfx_volume() if index == 2 else music.get_volume()
                bar = self.slider(index)
                pygame.draw.rect(surface, P['border'], bar)
                pygame.draw.rect(surface, P['mint'], (bar.x, bar.y, round(bar.w * value), bar.h))
                pygame.draw.rect(surface, P['text'], (bar.x + round(bar.w * value) - 3, bar.y - 6, 6, 30))
                gt.draw(surface, f'{round(value * 100)}%', rect.right - 32, rect.y + 30,
                        24, P['text'], right_x=True)
        gt.draw(surface, '窗口可自由缩放；调整不会重新开始当前地图。', 232, 716, 21, P['muted'], 'sans')
        x = key_hint(surface, '↑ ↓', '选择', 230, 820)
        x = key_hint(surface, '← →', '调整', x, 820)
        key_hint(surface, 'Esc', '返回', x, 820)

    def _pointer_input(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self._drag_row = None
            return True
        if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            return False
        position = event.pos if hasattr(event, 'pos') else pygame.mouse.get_pos()
        point = ((position[0] - self.app.draw_offset_x) / self.app.scale,
                 (position[1] - self.app.draw_offset_y) / self.app.scale)
        pressed = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        if pressed and pygame.Rect(64, 64, 150, 46).collidepoint(point):
            self.app.set_page_no_launch(self.app._setting_from_page)
            return True
        for index, rect in enumerate(self.rows()):
            if rect.collidepoint(point):
                self.app._setting_selected_row = index
                if pressed and index in (2, 3) and self.slider(index).inflate(12, 32).collidepoint(point):
                    self._drag_row = index
                if pressed and index == 0 and point[0] >= 1190:
                    key = pygame.K_LEFT if point[0] < 1260 else pygame.K_RIGHT
                    self.handle_setting_input(pygame.event.Event(pygame.KEYDOWN, key=key))
                elif pressed and index == 1:
                    self.handle_setting_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
                break
        if self._drag_row in (2, 3):
            bar = self.slider(self._drag_row)
            value = max(0, min(1, (point[0] - bar.x) / bar.w))
            if self._drag_row == 2:
                sfx.set_sfx_volume(value)
            else:
                music.set_volume(value)
        return True

    def _adjust_fps(self, direction):
        current = self.app.current_fps
        if direction < 0:
            current = max((value for value in _FPS_OPTIONS if value < current), default=min(current, _FPS_OPTIONS[0]))
        else:
            current = min((value for value in _FPS_OPTIONS if value > current), default=max(current, _FPS_OPTIONS[-1]))
        self.app.current_fps = current
        self.app._setting_selected_fps_idx = _FPS_OPTIONS.index(current) if current in _FPS_OPTIONS else 0
        self.app._setting_fps_just_autodetected = False
        sfx.play_click()

    def handle_setting_input(self, event):
        """处理设置页面的键盘事件。"""

        if self._pointer_input(event):
            return

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
                self._adjust_fps(-1)
            elif self.app._setting_selected_row == 2:
                sfx.set_sfx_volume(sfx.get_sfx_volume() - 0.05)
                sfx.play_click()
            elif self.app._setting_selected_row == 3:
                sfx.set_music_volume(sfx.get_music_volume() - 0.05)
                music.set_volume(sfx.get_music_volume())
                sfx.play_click()
        elif event.key == pygame.K_RIGHT:
            if self.app._setting_selected_row == 0:
                self._adjust_fps(1)
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
