from __future__ import annotations
import pygame
import sfx
from game_state import resolve_player_death

class WorldSession:
    """Existing world rules and input."""

    def __init__(self, app):
        self.app = app

    def advance(self, dt):
        if self.app.help_open:
            self.app.jump_pressed = False
            return
        keys = pygame.key.get_pressed()

        # ---- 游戏状态检查 ----

        # 计时器
        wmode = self.app._current_map.mode if self.app._current_map else "free"
        if not self.app._game_over and not self.app._game_win:
            self.app._game_timer += dt
            # 限时模式：时间到则失败
            time_limit = getattr(self.app._current_map, 'time_limit', 0.0)
            if wmode == "score_timed" and time_limit > 0 and self.app._game_timer >= time_limit:
                self.app._game_over = True

            # 积分目标模式：达到目标则胜利
            score_goal = getattr(self.app._current_map, 'score_goal', 0)
            if wmode == "score_target" and score_goal > 0 and self.app.player1.score >= score_goal:
                self.app._game_win = True

            # 探索模式：触碰终点则胜利
            if wmode == "explore" and self.app.player1._reached_end:
                self.app._game_win = True

        # 死亡处理（限复活次数）
        if not self.app.player1.alive and not self.app._game_over and not self.app._game_win:
            self.app._player_lives_left, self.app._game_over = resolve_player_death(
                self.app.player1, self.app._player_lives_left, self.app._infinite_lives)

        # ---- Buff 系统 tick ----
        if not self.app._game_over and not self.app._game_win and self.app.player1.alive:
            self.app.player1.tick_buffs(dt)
        # buff 属性修正
        self.app.player1.refresh_movement_stats()
        # 体力恢复速度（动态公式，三层结构）
        stamina_ratio = self.app.player1.stamina / max(1, self.app.player1.stamina_max)
        hp_ratio = self.app.player1.hp / max(1, self.app.player1.hp_max)
        stamina_missing = self.app.player1.stamina_max - self.app.player1.stamina
        base_stam_rec = (
            (1.15 + 5.5 * (1 - stamina_ratio) + 0.85 * hp_ratio) * (0.85 + 0.25 * hp_ratio)
            + 0.035 * stamina_missing
            + 0.15 * ((1 - stamina_ratio) ** 2)
            + 0.35 * ((1 - stamina_ratio) ** 3)
            + 0.65 * ((1 - stamina_ratio) ** 4)
        )
        buf_stam_rec = self.app.player1.get_buff_stat("stamina_recovery", base_stam_rec)
        buf_stam_cost = self.app.player1.get_buff_stat("stamina_cost", 1.0)
        # 控制效果检查（铁意 buff 40 免疫定身/晕眩/压制/反向）
        iron_will = self.app.player1.has_buff(40)
        rooted = self.app.player1.has_buff(21) and not iron_will
        stunned = self.app.player1.has_buff(28) and not iron_will
        grounded = self.app.player1.has_buff(27) and not iron_will
        hopping = self.app.player1.has_buff(33)
        reversed_ctrl = ((self.app.player1.has_buff(23) or getattr(self.app.player1, '_confused', False))
                         and not self.app.player1.has_buff(8) and not iron_will)

        # ---- 移动物理（游戏结束/胜利时冻结）----
        if not self.app._game_over and not self.app._game_win and self.app.player1.alive and not stunned:
            if self.app.player1.fly_mode:
                # ---- 飞行模式 ----
                fly_dx, fly_dy = 0.0, 0.0
                if keys[self.app.player1.key_bind["left"]] or keys[pygame.K_LEFT]:
                    fly_dx -= 1.0
                if keys[self.app.player1.key_bind["right"]] or keys[pygame.K_RIGHT]:
                    fly_dx += 1.0
                # 飞行模式朝向（与地面移动逻辑一致）
                if (keys[self.app.player1.key_bind["right"]] or keys[pygame.K_RIGHT]) and \
                   not (keys[self.app.player1.key_bind["left"]] or keys[pygame.K_LEFT]):
                    self.app.player1.facing_right = True
                elif (keys[self.app.player1.key_bind["left"]] or keys[pygame.K_LEFT]) and \
                     not (keys[self.app.player1.key_bind["right"]] or keys[pygame.K_RIGHT]):
                    self.app.player1.facing_right = False
                if keys[self.app.player1.key_bind["up"]] or keys[pygame.K_UP]:
                    fly_dy += 1.0
                if keys[self.app.player1.key_bind["down"]] or keys[pygame.K_DOWN]:
                    fly_dy -= 1.0
                # 直接操作坐标
                self.app.player1._x += fly_dx * self.app.player1.fly_speed * dt
                self.app.player1._y += fly_dy * self.app.player1.fly_speed * dt
                self.app.player1.v_x = 0.0
                self.app.player1.v_y = 0.0
                # 钳制在地图边界内（循环世界不钳制）
                if not self.app._current_map.loop_x:
                    self.app.player1._x = max(0.5, min(self.app.player1._x, self.app._current_map.width - 0.5))
                if not self.app._current_map.loop_y:
                    self.app.player1._y = max(0.5, min(self.app.player1._y, self.app._current_map.height - 0.5))
                # 更新接触池（用于绘制等）
                grect = self.app.player1.get_game_rect()
                self.app.player1.clear_environment_contacts(self.app._current_map)
            else:
                # ---- 正常模式 ----
                dir_x = 0.0
                if not rooted and not hopping:
                    left_key = keys[self.app.player1.key_bind["left"]] or keys[pygame.K_LEFT]
                    right_key = keys[self.app.player1.key_bind["right"]] or keys[pygame.K_RIGHT]
                    if reversed_ctrl:
                        left_key, right_key = right_key, left_key
                    if left_key:
                        dir_x -= 0.35
                    if right_key:
                        dir_x += 0.35
                    # 更新角色朝向（仅单方向按键时更新，同时按住保持原朝向）
                    if right_key and not left_key:
                        self.app.player1.facing_right = True
                    elif left_key and not right_key:
                        self.app.player1.facing_right = False
                self.app.player1.move(dir_x)

                # ---- 攀爬: W/↑向上 ----
                sm = getattr(self.app.player1, '_stamina_mult', 1.0)
                silenced = getattr(self.app.player1, '_silenced', False)
                climb_up_cost = 14.0 * sm * buf_stam_cost * dt + 0.01
                climb_idle_cost = 3.52 * sm * buf_stam_cost * dt + 0.01
                # 攀爬上边界：人物中心到达梯子顶端（半腰位置），消耗挂住体力
                climb_bound = getattr(self.app.player1, '_climb_top_y', None)
                at_climb_bound = False
                if climb_bound is not None and self.app.player1.is_climbing:
                    # 仅当靠近边界时吸附（防止远处瞬移）
                    if self.app.player1._y >= climb_bound - 0.05 and self.app.player1._y <= climb_bound + 2.0:
                        self.app.player1._y = climb_bound  # 中心与方块上边界齐平（半腰）
                        self.app.player1.v_y = 0.0
                        at_climb_bound = True
                if self.app.player1.is_climbing and (keys[self.app.player1.key_bind["up"]] or keys[pygame.K_UP]):
                    if at_climb_bound:
                        # 已到顶端，消耗挂住体力
                        if self.app.player1.stamina >= climb_idle_cost:
                            if not silenced: self.app.player1.consume_stamina(3.52 * sm * buf_stam_cost * dt)
                        else:
                            self.app.player1.stop_climbing()
                            self.app._stamina_flash_timer = self.app._stamina_flash_duration
                    elif self.app.player1.stamina >= climb_up_cost:
                        self.app.player1.climb_move(1.0)
                        if not silenced: self.app.player1.consume_stamina(14.0 * sm * buf_stam_cost * dt)
                    else:
                        self.app.player1.stop_climbing()
                        self.app._stamina_flash_timer = self.app._stamina_flash_duration
                elif self.app.player1.is_climbing:
                    self.app.player1.v_y = 0.0
                    if self.app.player1.stamina >= climb_idle_cost:
                        if not silenced: self.app.player1.consume_stamina(3.52 * sm * buf_stam_cost * dt)
                    else:
                        self.app.player1.stop_climbing()
                        self.app._stamina_flash_timer = self.app._stamina_flash_duration

                # ---- 游泳: W/↑向上，攀爬优先 ----
                swimming_now = False
                up_held = keys[self.app.player1.key_bind["up"]] or keys[pygame.K_UP]
                if not self.app.player1.is_climbing and self.app.player1.can_swim and not self.app.player1.has_buff(58):
                    if up_held:
                        swim_cost = 21.0 * sm * buf_stam_cost * dt + 0.01
                        if self.app.player1.stamina >= swim_cost:
                            # 游泳上边界仅在主动游泳且体力足够时生效
                            swim_bound = getattr(self.app.player1, '_swim_top_y', None)
                            at_swim_bound = False
                            if swim_bound is not None:
                                if self.app.player1._y >= swim_bound - 0.05 and self.app.player1._y <= swim_bound + 2.0:
                                    self.app.player1._y = swim_bound  # 中心与水面齐平（半腰）
                                    self.app.player1.v_y = 0.0
                                    at_swim_bound = True
                            if at_swim_bound:
                                if not silenced: self.app.player1.consume_stamina(21.0 * sm * buf_stam_cost * dt)
                                swimming_now = True
                            else:
                                swim_v = self.app.player1._swim_force
                                self.app.player1.v_y = swim_v  # 匀速上游
                                if not silenced: self.app.player1.consume_stamina(21.0 * sm * buf_stam_cost * dt)
                                swimming_now = True
                        else:
                            # 体力耗尽：不吸附、不游泳，自然下沉
                            self.app._stamina_flash_timer = self.app._stamina_flash_duration

                # ---- 体力恢复（攀爬中/水中按↑时不恢复，防止耗尽-恢复循环） ----
                can_recover = (not self.app.player1.is_climbing
                               and not swimming_now
                               and not (self.app.player1.can_swim and up_held)
                               and not (self.app.player1.can_climb and up_held and not self.app.player1.is_climbing))
                if can_recover and self.app.player1.stamina < self.app.player1.stamina_max:
                    self.app.player1.recover_stamina(buf_stam_rec * dt)

                # ---- 上岸：水面上 + 近岸 + 跳跃键 ----
                shore_exit_done = False
                if (self.app.jump_pressed and not grounded
                    and self.app.player1.can_swim and swimming_now
                    and getattr(self.app.player1, '_near_shore', False)
                    and self.app.player1.stamina >= 25):
                    _shore_pending = getattr(self.app.player1, '_shore_exit_pending', False)
                    if not _shore_pending:
                        # 高速上岸 + 临时空气墙：极速完成，不受液体阻力影响
                        self.app.player1.v_y = 32.0  # 高速向上
                        self.app.player1.v_x = 0.0
                        if not silenced: self.app.player1.consume_stamina(25)
                        self.app.player1.apply_buff(58, (), 0.3)
                        self.app.player1._shore_exit_pending = 'rise'  # 上升阶段
                        self.app.player1._shore_exit_dir = self.app.player1._shore_dir
                        self.app.player1._shore_exit_bound = getattr(self.app.player1, '_swim_top_y', None)
                        sfx.play_jump()
                        shore_exit_done = True
                        self.app.jump_pressed = False
                # 上岸后续：空气墙逻辑（到达高度→竖直停，再水平推→到位停）
                _shore_state = getattr(self.app.player1, '_shore_exit_pending', False)
                if _shore_state and not shore_exit_done:
                    exit_dir = self.app.player1._shore_exit_dir
                    swim_bound = getattr(self.app.player1, '_shore_exit_bound', None)
                    feet_y = self.app.player1._y - self.app.player1._h / 2
                    if _shore_state == 'rise':
                        if swim_bound is not None and feet_y >= swim_bound:
                            # 竖直空气墙：到达水面高度，锁 v_y，记录起始位置
                            self.app.player1.v_y = 0.0
                            self.app.player1.v_x = exit_dir * 16.0
                            self.app.player1._shore_slide_start_x = self.app.player1._x
                            self.app.player1._shore_exit_pending = 'slide'
                    elif _shore_state == 'slide':
                        # 水平空气墙：滑够 0.55 格（半身宽+岸边容差）即停
                        if abs(self.app.player1._x - self.app.player1._shore_slide_start_x) >= 0.55:
                            self.app.player1.v_x = 0.0
                            self.app.player1._shore_exit_pending = False
                        elif not self.app.player1.has_buff(58):
                            self.app.player1._shore_exit_pending = False
                    # buff 过期兜底
                    if self.app.player1._shore_exit_pending and not self.app.player1.has_buff(58):
                        self.app.player1._shore_exit_pending = False

                # ---- 正常跳跃 ----
                if self.app.jump_pressed and not grounded and not shore_exit_done:
                    can_actually_jump = self.app.player1.on_ground or self.app.player1.is_climbing
                    jump_cost = 15.0 * sm * buf_stam_cost + 0.01
                    if self.app.player1.stamina >= jump_cost:
                        if self.app.player1.jump():
                            if not silenced: self.app.player1.consume_stamina(15.0 * sm * buf_stam_cost)
                            sfx.play_jump()
                    elif can_actually_jump:
                        self.app._stamina_flash_timer = self.app._stamina_flash_duration
                    self.app.jump_pressed = False

                self.app.player1.update_physics(dt, self.app._current_map)
                self.app.player1.collide_with_world(self.app._current_map, dt)

                # 攀爬中着陆或离开可攀爬方块：自动解除
                if self.app.player1.is_climbing and (self.app.player1.on_ground or not self.app.player1.can_climb):
                    self.app.player1.is_climbing = False
                # 上岸后着陆或离开水面：清除上岸待处理状态
                if getattr(self.app.player1, '_shore_exit_pending', False):
                    if self.app.player1.on_ground or not self.app.player1.can_swim:
                        self.app.player1._shore_exit_pending = False

        # A keydown is consumed by this world frame even when a status blocks it.
        self.app.jump_pressed = False
        px, py = self.app.player1.get_center()
        self.app.camera.follow(px, py)
