from __future__ import annotations
import pygame
from constants import LOGIC_WIDTH, LOGIC_HEIGHT
from costumes import render_costume_at_feet, advance_costume_animation
import sfx
import music
import game_text as gt
from pixel_roamer.ui.config import FONT24, FONT28, FONT56
from pixel_roamer.ui.widgets import draw_text_center
from pixel_roamer.visual_effects import WorldEffects
from pixel_roamer.ui.theme import PALETTE as P, key_hint, panel

class WorldView:
    """Existing world rendering and feedback."""

    def __init__(self, app):
        self.app = app
        self.effects = WorldEffects()

    def draw(self, dt):
        fill_color = getattr(self.app._current_map, 'fill_color', (30, 30, 30))
        self.app.logic_surface.fill(fill_color)
        self.app._current_map.draw(self.app.logic_surface, self.app.camera)

        self.effects.draw(self.app.logic_surface, self.app.player1, self.app.camera)

        # 绘制玩家（时装系统）
        grect = self.app.player1.get_game_rect()
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

        animation_dt = 0 if self.app.help_open or self.app._game_over or self.app._game_win else dt
        advance_costume_animation(self.app.player1, anim_state, animation_dt)
        feet_x, feet_y = self.app.camera.world_to_screen(self.app.player1._x, grect.y)
        render_costume_at_feet(self.app.logic_surface, self.app.player1.costume_id,
                               feet_x, feet_y, grect.w * self.app.camera.scale,
                               grect.h * self.app.camera.scale,
                               flip_h=not self.app.player1.facing_right,
                               anim_state=anim_state, anim_frame=self.app.player1._anim_frame)

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

        gt.draw(self.app.logic_surface, gt.elide(self.app._current_map.name, 420, 18),
                LOGIC_WIDTH // 2, LOGIC_HEIGHT - 28, 18, P["text"], "sans", shadow=True, center_x=True)
        key_hint(self.app.logic_surface, "H", "操作指南", LOGIC_WIDTH - 202, LOGIC_HEIGHT - 44)
        if self.app.help_open:
            self.app.help.draw(self.app.logic_surface)
        if not getattr(self.app, 'focused', True):
            shade = pygame.Surface((LOGIC_WIDTH, LOGIC_HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 145))
            self.app.logic_surface.blit(shade, (0, 0))
            panel(self.app.logic_surface, (460, 350, 680, 188))
            gt.draw(self.app.logic_surface, '已暂停', 800, 380, 48,
                    P['text'], 'sans', center_x=True)
            gt.draw(self.app.logic_surface, '返回游戏窗口后继续漫游', 800, 464, 24,
                    P['muted'], 'sans', center_x=True)
