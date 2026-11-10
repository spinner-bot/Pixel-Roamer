from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from costumes import render_costume_direct, get_costume_anim_info
import sfx
import music
import game_text as gt
from pixel_roamer.ui.config import FONT24, FONT28, FONT56
from pixel_roamer.ui.widgets import draw_text_center

class WorldView:
    """Existing world rendering and feedback."""

    def __init__(self, app):
        self.app = app

    def draw(self, dt):
        fill_color = getattr(self.app._current_map, 'fill_color', (30, 30, 30))
        self.app.logic_surface.fill(fill_color)
        self.app._current_map.draw(self.app.logic_surface, self.app.camera)

        # 绘制玩家（时装系统）
        grect = self.app.player1.get_game_rect()
        # 时装位图底部有透明行，向下偏移使脚部对齐碰撞箱底部
        shift = grect.h * 0.22
        cam_scale = self.app.camera.scale
        sx = (grect.x - self.app.camera.x) * cam_scale + self.app.camera.logic_width / 2
        sy_top = self.app.camera.logic_height / 2 - (grect.y + grect.h - shift - self.app.camera.y) * cam_scale
        sw = grect.w * cam_scale
        sh = grect.h * cam_scale
        player_screen_rect = pygame.Rect(sx, sy_top, sw, sh)

        # ---- 动画状态判定 ----
        if self.app.player1.fly_mode:
            anim_state = "idle"
        elif self.app.player1.is_climbing:
            anim_state = "climb"
        elif not self.app.player1.on_ground:
            anim_state = "jump"
        elif abs(self.app.player1.v_x) > 0.3:
            anim_state = "walk"
        else:
            anim_state = "idle"

        # 推进动画计时器并循环帧
        info = get_costume_anim_info(self.app.player1.costume_id)
        if info and anim_state in info:
            frame_count = info[anim_state]
            if frame_count > 1:
                self.app.player1._anim_timer += dt
                if self.app.player1._anim_timer >= 0.15:  # ~6.7 fps 行走周期
                    self.app.player1._anim_timer -= 0.15
                    self.app.player1._anim_frame = (self.app.player1._anim_frame + 1) % frame_count
        else:
            self.app.player1._anim_frame = 0

        render_costume_direct(self.app.logic_surface, self.app.player1.costume_id, player_screen_rect,
                              flip_h=not self.app.player1.facing_right,
                              anim_state=anim_state,
                              anim_frame=self.app.player1._anim_frame)

        # ---- Buff 视线效果（只影响世界/生物，不影响 UI） ----
        # Buff: 发光 (50) 自身发光照亮周围
        if self.app.player1.has_buff(50):
            px, py = self.app.player1.get_center()
            cam_scale = self.app.camera.scale
            sx = (px - self.app.camera.x) * cam_scale + self.app.camera.logic_width / 2
            sy = self.app.camera.logic_height / 2 - (py - self.app.camera.y) * cam_scale
            glow_radius = 120
            glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                alpha = 30 - i * 3
                r = glow_radius * i / 8
                pygame.draw.circle(glow, (255, 240, 180, max(0, alpha)),
                                   (glow_radius, glow_radius), int(r))
            self.app.logic_surface.blit(glow, (sx - glow_radius, sy - glow_radius), special_flags=pygame.BLEND_ADD)

        # Buff: 失明 (24) 屏幕变亮黄色（清明 buff 8 免疫）
        if self.app.player1.has_buff(24) and not self.app.player1.has_buff(8):
            blind_overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            blind_overlay.fill((255, 240, 80, 140))
            self.app.logic_surface.blit(blind_overlay, (0, 0))

        # Buff: 视野受限 (25) 缩小视野半径（清明 buff 8 免疫）
        if self.app.player1.has_buff(25) and not self.app.player1.has_buff(8):
            vision_radius = 5.0  # 默认半径（格）
            for b in self.app.player1.buffs:
                if b.buff_id == 25 and b.params:
                    vision_radius = float(b.params[0])
            px, py = self.app.player1.get_center()
            cam_scale = self.app.camera.scale
            sx = (px - self.app.camera.x) * cam_scale + self.app.camera.logic_width / 2
            sy = self.app.camera.logic_height / 2 - (py - self.app.camera.y) * cam_scale
            vision_radius_px = int(vision_radius * 24 * cam_scale)
            dark = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 220))
            if vision_radius_px > 0:
                pygame.draw.circle(dark, (0, 0, 0, 0), (int(sx), int(sy)), vision_radius_px)
            self.app.logic_surface.blit(dark, (0, 0))

        # ---- HP 血条 ----
        # ---- 音效检测 ----
        if self.app._prev_score < self.app.player1.score:
            sfx.play_pickup()
        self.app._prev_score = self.app.player1.score

        if self.app._prev_alive and not self.app.player1.alive and not self.app._death_played:
            sfx.play_death()
            music.stop(fade_out_ms=600)
            self.app._death_played = True
        if not self.app.player1.alive:
            self.app._prev_alive = self.app.player1.alive
        else:
            self.app._prev_alive = True
            self.app._death_played = False

        if self.app._game_win and not self.app._win_played:
            sfx.play_win()
            music.play("victory", fade_in_ms=300, loops=0)
            self.app._win_played = True

        # 低血量自动切换危险主题
        if self.app.player1.alive and not self.app._game_win and not self.app._game_over:
            hp_ratio = self.app.player1.hp / max(1, self.app.player1.hp_max)
            if hp_ratio < 0.25 and music.get_current_track() != "danger":
                music.play("danger", fade_in_ms=500)
            elif hp_ratio >= 0.25 and music.get_current_track() == "danger":
                # 恢复 → 回到地图音乐
                self.app._play_world_music(self.app._current_map)

        self.app.hud.draw_hp_bar(self.app.logic_surface, self.app.player1, dt)
        self.app.hud.draw_stamina_bar(self.app.logic_surface, self.app.player1, dt)
        self.app.hud.draw_player_info(self.app.logic_surface, self.app.player1, dt)

        # ---- 濒死滤镜 ----
        self.app.hud.draw_near_death_vignette(self.app.logic_surface, self.app.player1)
        self.app.hud.draw_buff_status(self.app.logic_surface, self.app.player1, dt)

        # ---- 积分显示（顶部居中）----
        score_text = f"* {self.app.player1.score}"
        gt.draw(self.app.logic_surface, score_text,
                           LOGIC_WIDTH // 2, 16, 22,
                           (255, 220, 80), "mono", shadow=True, center_x=True)

        # ---- 计时器（积分限时模式）----
        wmode = self.app._current_map.mode if self.app._current_map else "free"
        time_limit = getattr(self.app._current_map, 'time_limit', 0.0)
        if wmode == "score_timed" and time_limit > 0:
            remaining = max(0, time_limit - self.app._game_timer)
            timer_text = f"{int(remaining // 60):02d}:{int(remaining % 60):02d}"
            timer_color = (255, 80, 80) if remaining < 30 else (255, 255, 255)
            gt.draw(self.app.logic_surface, timer_text,
                               LOGIC_WIDTH // 2, 42, 20,
                               timer_color, "mono", shadow=True, center_x=True)

        # ---- 积分目标进度（积分目标模式）----
        score_goal = getattr(self.app._current_map, 'score_goal', 0)
        if wmode == "score_target" and score_goal > 0:
            goal_text = f"Goal: {score_goal} ({int(self.app.player1.score / max(1, score_goal) * 100)}%)"
            gt.draw(self.app.logic_surface, goal_text,
                               LOGIC_WIDTH // 2, 42, 15,
                               (200, 220, 255), "mono", shadow=True, center_x=True)

        # ---- 命数已移至体力条下方 (draw_player_info) ----

        # ---- 游戏结束/胜利叠加层 ----
        if self.app._game_over:
            overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.app.logic_surface.blit(overlay, (0, 0))
            y = LOGIC_HEIGHT // 2 - 80
            y = draw_text_center(self.app.logic_surface, FONT56, "游 戏 失 败", y, (255, 80, 60)) + 16
            if wmode == "score_timed":
                y = draw_text_center(self.app.logic_surface, FONT28, f"最终得分: {self.app.player1.score}", y, (255, 220, 80)) + 8
            draw_text_center(self.app.logic_surface, FONT24, "按 ESC 返回", y + 16, (180, 180, 180))

        elif self.app._game_win:
            overlay = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.app.logic_surface.blit(overlay, (0, 0))
            y = LOGIC_HEIGHT // 2 - 80
            y = draw_text_center(self.app.logic_surface, FONT56, "通 关！", y, (100, 255, 100)) + 16
            y = draw_text_center(self.app.logic_surface, FONT28, f"最终得分: {self.app.player1.score}", y, (255, 220, 80)) + 8
            draw_text_center(self.app.logic_surface, FONT24, "按 ESC 返回", y + 16, (180, 180, 180))

        # 右上角 FPS
        fps_text = f"FPS {int(self.app.clock.get_fps())}"
        gt.draw(self.app.logic_surface, fps_text,
                           LOGIC_WIDTH - 16, 8, 21,
                           (255, 255, 255), "mono", shadow=True, right_x=True)
        # 坐标（FPS 下方）
        px, py = self.app.player1.get_center()
        coord_text = f"({px:.1f}, {py:.1f})"
        gt.draw(self.app.logic_surface, coord_text,
                           LOGIC_WIDTH - 16, 30, 16,
                           (200, 210, 230), "mono", shadow=True, right_x=True)

        # 飞行模式指示
        if self.app.player1.fly_mode:
            gt.draw(self.app.logic_surface, "[FLY]",
                               LOGIC_WIDTH // 2, LOGIC_HEIGHT - 36, 15,
                               (100, 255, 200), "mono", shadow=True, center_x=True)
