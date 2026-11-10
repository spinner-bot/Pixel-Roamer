from __future__ import annotations
import math
import pygame
from typing import TYPE_CHECKING, Optional, Tuple, Any
import buff_data  # 确保 BUFF_TYPES 在生物模块加载时即被填充

from constants import RES_NORMAL_SCALE, CORR_FLOOR
from game_rect import GameRect
from collision import CONTACT_EPSILON, spans_overlap, sweep_axis
from block_type import BlockType

if TYPE_CHECKING:
    from world import World


# ===================== 生物体（中心点坐标，y向上） =====================
class Creature:
    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        hp_max: float,
        shield: float = 0.0,
        v_max: float = 4,
        v_jump: float = 7.5,            # 正数向上
        a_x: float = 0,
        a_y: float = 0,
        f_x: float = 0.88,
        f_y: float = 0.9965,
        v_x: float = 0.0,
        v_y: float = 0.0,
        phys_atk: float = 10,
        magic_atk: float = 0,
        phys_res: float = 0,
        magic_res: float = 0,
        phys_pen: float = 0,
        magic_pen: float = 0,
        k_res: float = 150,
        dr: float = 0.0,
        is_solid: bool = False
    ):
        self.alive = True
        self.on_ground = False
        self.on_wall_left = False
        self.on_wall_right = False
        self.on_ceiling = False
        self.can_climb = False       # 接触池中有可攀爬方块
        self.is_climbing = False     # 主动攀爬中
        self.can_swim = False        # 接触池中有可游泳方块
        self._swim_force = 0.0       # 当前最大浮力值
        self._stamina_mult = 1.0     # 当前体力消耗倍率

        self._x = float(x)
        self._y = float(y)
        self._w = w
        self._h = h
        self.rect = pygame.Rect(0, 0, w, h)

        self.hp = hp_max
        self.hp_max = hp_max
        self.shield = shield

        self.v_x = v_x
        self.v_y = v_y
        self.v_max = v_max
        self.v_jump = v_jump
        self.a_x = a_x
        self.a_y = a_y
        self.f_x = f_x
        self.f_y = f_y

        self.phys_atk = phys_atk
        self._base_phys_atk = phys_atk
        self.magic_atk = magic_atk
        self.phys_res = phys_res
        self.magic_res = magic_res
        self.phys_pen = phys_pen
        self.magic_pen = magic_pen
        self.k_res = k_res
        self.dr = dr
        self.is_solid = is_solid

        self.contact_pool = set()       # 自动去重
        self.stand_pool = None
        self.score = 0                 # 玩家积分
        self._reached_end = False      # 是否触碰终点

        # ---- Buff 系统 ----
        self.buffs: list = []          # [BuffInstance, ...]
        self._buff_timer = 0.0         # buff tick 累计时间
        self._buff_game_time = 0.0     # 累计游戏时间（计算时长用）
        self._air_jumps_used = 0       # 空中已跳跃次数（二段跳用）

    # ----- 游戏矩形 -----
    def get_game_rect(self) -> GameRect:
        return GameRect(self._x - self._w / 2, self._y - self._h / 2, self._w, self._h)

    def set_from_game_rect(self, grect: GameRect):
        self._x = grect.x + grect.w / 2
        self._y = grect.y + grect.h / 2

    # ----- 战斗 -----
    def clamp_velocity(self):
        self.v_x = max(-self.v_max, min(self.v_x, self.v_max))

    def _get_buff_param(self, buff_id: int, idx: int = 0, default: float = 0.0) -> float:
        """读取身上某 buff 的参数值，无此 buff 则返回 default。"""
        for b in self.buffs:
            if b.buff_id == buff_id and b.params and len(b.params) > idx:
                return float(b.params[idx])
        return default

    def _receive_damage(self, amount: float, bypass_shield: bool = False) -> float:
        """Return resources actually lost, including shield and capped overkill."""
        if not self.alive or amount <= 0:
            return 0.0
        shield_lost = 0.0 if bypass_shield else min(self.shield, amount)
        self.shield -= shield_lost
        health_lost = min(self.hp, amount - shield_lost)
        self.hp -= health_lost
        if self.hp <= 0:
            self.hp = 0.0
            self.alive = False
            self.on_death()
        return shield_lost + health_lost

    def take_damage(self, phys_damage: float, magic_damage: float,
                    phys_pen: float = 0.0, magic_pen: float = 0.0,
                    source: "Creature" = None, damage_type: str = "physical") -> float:
        if not all(math.isfinite(value) for value in (phys_damage, magic_damage, phys_pen, magic_pen)):
            raise ValueError("damage inputs must be finite")
        if not self.alive or self.has_buff(36) or (damage_type == "fire" and self.has_buff(9)):
            return 0.0
        phys_damage = 0.0 if self.has_buff(34) else max(0.0, phys_damage)
        magic_damage = 0.0 if self.has_buff(35) else max(0.0, magic_damage)
        armor_broken = self.has_buff(26)

        def resistance_multiplier(penetration, resistance):
            if armor_broken:
                return 1.0
            x = max(-1.0, min((penetration - resistance) / RES_NORMAL_SCALE, 1.0))
            correction = max(x, CORR_FLOOR, 0.95 * math.sin(x) + 0.15 * x ** 2)
            return 1.0 + correction

        total = (phys_damage * resistance_multiplier(phys_pen, self.phys_res)
                 + magic_damage * resistance_multiplier(magic_pen, self.magic_res))
        reduction = 0.0 if armor_broken else max(0.0, min(1.0, self.dr + getattr(self, '_courage_dr', 0.0)))
        fortify = 1.0 if armor_broken else self.get_buff_stat("damage_taken", 1.0)
        if self.has_buff(46) and damage_type == "fire":
            total *= 2
        amount = total * (1 - reduction) * getattr(self, '_weakness_mult', 1.0) * fortify
        actual = self._receive_damage(amount, bypass_shield=self.has_buff(29))
        if source is not None and source.alive and actual > 0:
            if self.has_buff(10):
                source.take_raw_damage(actual * max(0, self._get_buff_param(10, 0, 30)) / 100)
            if source.alive and source.has_buff(11):
                source.heal(actual * max(0, source._get_buff_param(11, 0, 15)) / 100)
        return actual

    def take_raw_damage(self, damage: float, damage_type: str = "raw",
                        bypass_shield: bool = False) -> float:
        if not math.isfinite(damage):
            raise ValueError("damage must be finite")
        if not self.alive or damage <= 0 or self.has_buff(36):
            return 0.0
        if ((damage_type == "fire" and self.has_buff(9))
                or (damage_type == "magic" and self.has_buff(35))
                or (damage_type == "physical" and self.has_buff(34))):
            return 0.0
        if self.has_buff(46) and damage_type == "fire":
            damage *= 2
        return self._receive_damage(damage, bypass_shield=bypass_shield or self.has_buff(29))

    def heal(self, amount: float) -> float:
        if not self.alive or amount <= 0:
            return 0.0

        # ---- Buff: 重伤 (20) 受到的治疗效果减少 ----
        grievous_mult = self.get_buff_stat("healing_received", 1.0)

        # ---- Buff: 发炎 (46) 治疗效果减半 ----
        if self.has_buff(46):
            grievous_mult *= 0.5

        effective_amount = amount * grievous_mult
        if effective_amount <= 0:
            return 0.0

        recover = min(effective_amount, self.hp_max - self.hp)
        self.hp += recover

        # ---- Buff: 寄生 (55) 被治愈时额外扣除等量生命 ----
        if self.has_buff(55) and recover > 0:
            self.take_raw_damage(recover)

        return recover

    def add_shield(self, amount: float, max_shield: float = None) -> float:
        if not self.alive or amount <= 0:
            return 0.0
        if max_shield is not None:
            target = max(self.shield, min(self.shield + amount, max_shield))
        else:
            target = self.shield + amount
        add = target - self.shield
        self.shield = target
        return add

    def on_death(self):
        pass

    # ----- 运动基元 -----
    def apply_impulse(self, impulse_x: float, impulse_y: float):
        self.v_x += impulse_x
        self.v_y += impulse_y

    def reset_motion(self):
        self.v_x = 0.0
        self.v_y = 0.0

    def jump(self, not_on_ground_ok=False) -> bool:
        """跳跃。可从地面或攀爬中起跳；攀爬中跳跃会解除攀爬状态。
        有二段跳 buff (37) 时，可在空中再跳一次。需体力>0。"""
        if self.stamina < 0.01:
            return False

        # 落地或攀爬时重置空中跳跃计数
        if self.on_ground or self.is_climbing:
            self._air_jumps_used = 0

        # 计算最大空中跳跃次数（二段跳 buff 37 提供 +1）
        max_air_jumps = 1 if self.has_buff(37) else 0

        on_ground_or_climb = self.on_ground or self.is_climbing
        can_air_jump = (not on_ground_or_climb and
                        self._air_jumps_used < max_air_jumps)

        if (not_on_ground_ok or on_ground_or_climb or can_air_jump) and self.alive:
            self.v_y = self.v_jump
            self.on_ground = False
            self.is_climbing = False
            if can_air_jump:
                self._air_jumps_used += 1
            return True
        return False

    def update_physics(self, dt: float, world):
        if not self.alive:
            return
        # 飞行模式：完全跳过物理
        if getattr(self, 'fly_mode', False):
            return
        # 攀爬中：无重力，加速度归零防止残余滑动
        if self.is_climbing:
            self.a_x = 0.0
            self.a_y = 0.0
            self.v_x = 0.0
            self.clamp_velocity()
            return
        self.v_x += self.a_x * dt
        self.v_y += self.a_y * dt

        # ---- Buff: 重力修正（轻羽13/定锚54） ----
        buf_grav = self.get_buff_stat("gravity", 1.0)
        self.v_y += world.gravity * buf_grav * dt

        # ---- Buff: 风步 (53) 连续移动加速 ----
        if self.has_buff(53):
            moving = abs(self.v_x) > 0.1
            if moving:
                self._wind_walk_timer = getattr(self, '_wind_walk_timer', 0.0) + dt
                bonus = min(self._wind_walk_timer * 0.5, self._get_buff_param(53, 0, 0.5) * self.v_max)
                # 按当前移动方向加速
                direction = 1.0 if self.v_x > 0 else -1.0
                self.v_x += direction * bonus * dt * 3
            else:
                self._wind_walk_timer = 0.0
        else:
            self._wind_walk_timer = 0.0

        self.clamp_velocity()

    # ----- 采样：仅自身矩形微扩 0.01，不做整格扩展 -----
    def _sample_contact_tiles(self, grect: GameRect, world):
        """返回所有接触到的方块ID集合（不负责边界方块）。

        优化：使用 get_block_type_by_coord 跳过冗余的浮点→整数转换。
        """
        expanded_rect = GameRect(
            grect.x - 0.01,
            grect.y - 0.01,
            grect.w + 0.02,
            grect.h + 0.02
        )
        tiles = set()
        min_gx = math.floor(expanded_rect.x)
        max_gx = math.floor(expanded_rect.x + expanded_rect.w - 1e-9)
        min_gy = math.floor(expanded_rect.y)
        max_gy = math.floor(expanded_rect.y + expanded_rect.h - 1e-9)
        _wrap = world._wrap_grid_coord
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                coord = _wrap(gx, gy)
                if coord is None:
                    # 越界处若为实心边界则视为 ID=1
                    if world.edge_behavior == "solid":
                        tiles.add(1)
                    continue
                bt = world.get_block_type_by_coord(coord[0], coord[1])
                tiles.add(bt.id)
        return tiles

    def _contact_tile_instances(self, world):
        """Yield actual touched tiles once, including across looping seams."""
        rect = self.get_game_rect()
        seen = set()
        for gx in range(math.floor(rect.x - 0.01),
                        math.floor(rect.x + rect.w + 0.01 - 1e-9) + 1):
            for gy in range(math.floor(rect.y - 0.01),
                            math.floor(rect.y + rect.h + 0.01 - 1e-9) + 1):
                coord = world._wrap_grid_coord(gx, gy)
                if coord is None or coord in seen:
                    continue
                seen.add(coord)
                tile = world.grid.get(coord)
                if tile is not None:
                    yield gx, gy, coord, tile

    # ----- 碰撞与效果总控 -----
    def collide_with_world(self, world, dt: float):
        """Keep each collision step below half a tile, even after a long frame."""
        remaining = max(0.0, dt)
        for _ in range(256):
            if not self.alive:
                break
            speed = max(abs(self.v_x), abs(self.v_y))
            if not math.isfinite(speed):
                self.reset_motion()
                break
            step = min(remaining, 0.4 / speed) if speed > 0 else remaining
            self._collide_with_world_step(world, step)
            remaining -= step
            if remaining < 1e-9:
                break
        if self.alive and world.edge_behavior == "void" and world.is_out_of_bounds(self._x, self._y):
            # The void ends a life even during respawn immunity.
            self.hp = 0
            self.alive = False
            self.on_death()

    def _collide_with_world_step(self, world, dt: float):
        if not self.alive:
            return

        grect = self.get_game_rect()

        # ---------- 阶段1：预收集接触方块 ----------
        pre_contact = self._sample_contact_tiles(grect, world)

        # 预判脚下方块（精准）
        foot_gy = grect.y - 0.001
        foot_gx = grect.x + grect.w / 2
        bt_foot = world.get_block_type(foot_gx, foot_gy)
        pre_stand = bt_foot.id if bt_foot.id != 0 else None

        all_ids = pre_contact.copy()
        if pre_stand is not None:
            all_ids.add(pre_stand)

        block_types_list = []
        for bid in all_ids:
            bt = world.block_types.get(bid)
            if bt:
                block_types_list.append(bt)

        # ---------- 摩擦计算 ----------
        if self.on_ground and pre_stand is not None:
            surface_f_list = []
            for bt in block_types_list:
                if bt.surface_f != 1.0:
                    surface_f_list.append(bt.surface_f)
            if pre_stand is not None:
                stand_bt = world.block_types.get(pre_stand)
                if stand_bt:
                    surface_f_list.append(stand_bt.surface_f)
            final_surface_f = min(surface_f_list) if surface_f_list else 1.0
            final_fx = self.f_x * final_surface_f
            final_fy = self.f_y
        else:
            final_fx = self.f_x
            final_fy = self.f_y

        # Surface modifiers can reduce damping to zero; passive friction must
        # never turn into an energy source (ice surface_f can be greater than 1).
        final_fx = max(0.0, min(1.0, final_fx))
        final_fy = max(0.0, min(1.0, final_fy))

        # ---- Buff: 摩擦修正（滑腻42/黏着43/寒冷51） ----
        # 滑腻 (42)：系数越高越滑，param[0]=滑腻度%，默认85%→15%摩擦
        if self.has_buff(42):
            slick_pct = min(99.0, max(0.0, self._get_buff_param(42, 0, 85.0)))
            slick_mult = 1.0 - slick_pct / 100.0
            final_fx = final_fx ** slick_mult
        if self.has_buff(43):  # 黏着：高摩擦
            sticky_pct = max(0.0, self._get_buff_param(43, 0, 80.0))
            sticky_mult = 1.0 + sticky_pct / 100.0
            final_fx = final_fx ** sticky_mult
        if self.has_buff(51):  # 寒冷：冰面摩擦
            chill_pct = min(99.0, max(0.0, self._get_buff_param(51, 0, 70.0)))
            chill_mult = 1.0 - chill_pct / 100.0
            final_fx = final_fx ** chill_mult

        # Liquid drag remains active when a friction buff is present.
        liquid_space = min((bt.space_f for bt in block_types_list if bt.space_f != 1.0), default=1.0)
        if liquid_space < 1.0:
            liquid_space = max(0.0, liquid_space)
            final_fx *= liquid_space
            final_fy *= liquid_space

        self.v_x *= pow(final_fx, dt * 60)
        self.v_y *= pow(final_fy, dt * 60)

        # ---------- 阶段2：分轴碰撞修正 ----------
        self.on_ground = False
        self.on_wall_left = False
        self.on_wall_right = False
        self.on_ceiling = False

        # ---- Buff: 幽灵 (48) / 幻影方块效果 ----
        ghost_mode = self.has_buff(48) or getattr(self, '_phantom_active', False)

        if not ghost_mode:
            dx = self.v_x * dt
            swept_x = GameRect(grect.x + min(0, dx), grect.y,
                               grect.w + abs(dx), grect.h)
            if sweep_axis(grect, dx, world.get_nearby_solid_blocks_game(swept_x), True):
                self.on_wall_right = dx > 0
                self.on_wall_left = dx < 0
                self.v_x = 0

            dy = self.v_y * dt
            swept_y = GameRect(grect.x, grect.y + min(0, dy),
                               grect.w, grect.h + abs(dy))
            if sweep_axis(grect, dy, world.get_nearby_solid_blocks_game(swept_y), False):
                self.on_ground = dy < 0
                self.on_ceiling = dy > 0
                self.v_y = 0
        else:
            # 幽灵模式：自由穿过固体，但仍受重力影响
            grect.x += self.v_x * dt
            grect.y += self.v_y * dt

        # A later substep can have zero velocity after an earlier collision.
        # Preserve resting contact from geometry rather than clearing its flags.
        if not ghost_mode and (self.v_x == 0 or self.v_y == 0):
            for block_rect, bt in world.get_nearby_solid_blocks_game(grect):
                overlap_x = spans_overlap(grect.x, grect.w, block_rect.x, block_rect.w)
                overlap_y = spans_overlap(grect.y, grect.h, block_rect.y, block_rect.h)
                if overlap_x and self.v_y == 0:
                    if abs(grect.y - block_rect.y - block_rect.h) <= CONTACT_EPSILON:
                        self.on_ground = True
                    if not bt.one_way and abs(grect.y + grect.h - block_rect.y) <= CONTACT_EPSILON:
                        self.on_ceiling = True
                if overlap_y and self.v_x == 0 and not bt.one_way:
                    if abs(grect.x + grect.w - block_rect.x) <= CONTACT_EPSILON:
                        self.on_wall_right = True
                    if abs(grect.x - block_rect.x - block_rect.w) <= CONTACT_EPSILON:
                        self.on_wall_left = True

        self.set_from_game_rect(grect)

        # ---------- 阶段3：最终收集接触池与站立池 ----------
        self.contact_pool = self._sample_contact_tiles(grect, world)
        self.stand_pool = None

        # 独立分支：根据碰撞标志补充边界方块（ID=1）
        if self.on_wall_left or self.on_wall_right or self.on_ceiling:
            self.contact_pool.add(1)

        if self.on_ground:
            foot_gx = grect.x + grect.w / 2
            foot_gy = grect.y - 0.001
            bt_foot = world.get_block_type(foot_gx, foot_gy)
            if bt_foot.id != 0:
                self.stand_pool = bt_foot.id

        # ---------- 阶段4：应用方块效果 ----------
        self._apply_tile_effects(world, dt)

    def _apply_tile_effects(self, world, dt: float):
        all_ids = self.contact_pool.copy()
        if self.stand_pool is not None:
            all_ids.add(self.stand_pool)
        types = []
        for bid in all_ids:
            bt = world.block_types.get(bid)
            if bt:
                types.append(bt)
        # ---- 一次性效果冷却系统 ----
        if not hasattr(self, '_special_cooldowns'):
            self._special_cooldowns = {}
        for k in list(self._special_cooldowns):
            self._special_cooldowns[k] -= dt
            if self._special_cooldowns[k] <= 0:
                del self._special_cooldowns[k]

        self.can_climb = any(bt.climbable for bt in types)
        self.can_swim = any(bt.swim_f > 0 for bt in types)
        # 若接触池中有可游泳的方块，取最大浮力；同时记录最小空间阻力（用于上岸速度补偿）
        self._swim_force = max((bt.swim_f for bt in types), default=0.0)
        self._liquid_space_f = min((bt.space_f for bt in types if bt.swim_f > 0), default=1.0)
        # 计算攀爬/游泳的上边界（用于到达顶端时停住）
        self._climb_top_y = None
        self._swim_top_y = None
        if self.can_climb or self.can_swim:
            grect = self.get_game_rect()
            min_gx = int(grect.x) - 1
            max_gx = int(grect.x + grect.w) + 1
            min_gy = int(grect.y) - 1
            max_gy = int(grect.y + grect.h) + 1
            climb_top = -999.0
            swim_top = -999.0
            for gx in range(min_gx, max_gx + 1):
                for gy in range(min_gy, max_gy + 1):
                    coord = world._wrap_grid_coord(gx, gy)
                    if coord is None:
                        continue
                    bt = world.get_block_type_by_coord(coord[0], coord[1])
                    if bt.climbable:
                        climb_top = max(climb_top, float(gy + 1))
                    if bt.swim_f > 0:
                        swim_top = max(swim_top, float(gy + 1))
            if climb_top > -999:
                self._climb_top_y = climb_top
            if swim_top > -999:
                self._swim_top_y = swim_top
        # 检测岸边：水面高度处紧邻固体方块（水平距离 ≤0.2 格）
        self._near_shore = False
        self._shore_dir = 0  # 1=右侧岸, -1=左侧岸
        if self._swim_top_y is not None:
            surface_y = self._swim_top_y
            shore_margin = 0.2
            grect = self.get_game_rect()
            # 检查右侧：水面相邻的固体方块
            check_gx = int(grect.x + grect.w + shore_margin)
            for gy in range(int(surface_y - 1), int(surface_y) + 1):
                coord = world._wrap_grid_coord(check_gx, gy)
                if coord is None:
                    continue
                bt = world.get_block_type_by_coord(coord[0], coord[1])
                if bt.is_solid:
                    # 该固体方块顶部应与水面齐平
                    if gy + 1 >= surface_y - 0.1:
                        self._near_shore = True
                        self._shore_dir = 1
                        break
            # 检查左侧
            if not self._near_shore:
                check_gx = int(grect.x - shore_margin)
                for gy in range(int(surface_y - 1), int(surface_y) + 1):
                    coord = world._wrap_grid_coord(check_gx, gy)
                    if coord is None:
                        continue
                    bt = world.get_block_type_by_coord(coord[0], coord[1])
                    if bt.is_solid:
                        if gy + 1 >= surface_y - 0.1:
                            self._near_shore = True
                            self._shore_dir = -1
                            break
        # 水中自动浸湿（清除着火 buff 16），离开水后 1 秒消失
        # 仅水系液体触发（排除熔岩/蜂蜜等非水液体）
        if self.can_swim:
            is_water_liquid = any(
                bt.swim_f > 0 and bt.id != 8  # 排除蜂蜜
                and not (bt.buff_ids and 16 in bt.buff_ids)  # 排除熔岩类
                and bt.damage_ps == 0  # 排除伤害液体
                for bt in types
            )
            if is_water_liquid:
                self.apply_buff(15, (), 1.0)
        # 体力消耗倍率（取接触方块中最大值）
        self._stamina_mult = max((bt.k_stamina for bt in types), default=1.0)
        # 沉默效果（抑制体力消耗）
        self._silenced = any(bt.special == "silence" for bt in types)
        # 勇气效果（临时减伤）
        courage_val = max((float(bt.special_data) for bt in types if bt.special == "courage"), default=0.0)
        self._courage_dr = courage_val
        # 虚弱效果（受伤加深）
        weakness_val = max((float(bt.special_data) for bt in types if bt.special == "weakness"), default=0.0)
        self._weakness_mult = 1.0 + weakness_val

        # 攀爬中但已离开可攀爬方块：自动解除攀爬状态
        if self.is_climbing and not self.can_climb:
            self.is_climbing = False
            self.v_y = 0.0

        self._environment_speed_mult = 1.0
        self._environment_jump_mult = 1.0

        # ---- Buff: 稳足(41)/定锚(54)/石肤(39) 免疫环境力 ----
        immune_forces = self.has_buff(41) or self.has_buff(54) or self.has_buff(39)

        if not immune_forces:
            ax_add, ay_add = 0.0, 0.0
            for bt in types:
                kx, ky = bt.accel_k
                bx, by = bt.accel_b
                ax_add += kx * self.v_x + bx
                ay_add += ky * self.v_y + by
            self.v_x += ax_add * dt
            self.v_y += ay_add * dt

            bounce_x, bounce_y = 0.0, 0.0
            for bt in types:
                bx, by = bt.bounce
                if abs(bx) > abs(bounce_x):
                    bounce_x = bx
                if abs(by) > abs(bounce_y):
                    bounce_y = by
            self.v_x += bounce_x
            self.v_y += bounce_y

        max_dps = max((bt.damage_ps for bt in types), default=0.0)
        if max_dps > 0:
            self.take_raw_damage(max_dps * dt, damage_type="fire" if any(
                bt.damage_ps == max_dps and bt.buff_ids and 16 in bt.buff_ids for bt in types
            ) else "raw")

        # ---- Buff 施加（接触方块时触发，支持复合）----
        for bt in types:
            if bt.buff_ids:
                for i, bid in enumerate(bt.buff_ids):
                    params = bt.buff_params_list[i] if i < len(bt.buff_params_list) else ()
                    dur = bt.buff_durations[i] if i < len(bt.buff_durations) else None
                    self.apply_buff(bid, params, dur)

        for bt in types:
            if bt.special is not None:
                if bt.special == "teleport" and bt.special_data is not None:
                    # 支持 meta 覆盖目标坐标
                    tx, ty = bt.special_data
                    for _, _, _, tile in self._contact_tile_instances(world):
                        if tile.type_id == bt.id and isinstance(tile.meta, dict):
                            tx = tile.meta.get("tp_x", tx)
                            ty = tile.meta.get("tp_y", ty)
                            break
                    self._x = float(tx)
                    self._y = float(ty)
                    self.reset_motion()
                elif bt.special == "checkpoint":
                    if hasattr(self, "spawn_pos"):
                        self.spawn_pos = (self._x, self._y)
                elif bt.special == "heal" and bt.special_data is not None:
                    self.heal(float(bt.special_data) * dt)
                elif bt.special == "shield" and bt.special_data is not None:
                    if isinstance(bt.special_data, dict):
                        amt = float(bt.special_data.get("amount", 0))
                        mx = bt.special_data.get("max", None)
                        self.add_shield(amt * dt, mx)
                    else:
                        self.add_shield(float(bt.special_data) * dt, None)
                elif bt.special == "speed" and bt.special_data is not None:
                    # 临时速度倍率（持续接触期间）
                    self._environment_speed_mult = float(bt.special_data)
                elif bt.special == "jump" and bt.special_data is not None:
                    self._environment_jump_mult = float(bt.special_data)
                elif bt.special == "score" and bt.special_data is not None:
                    consumed_id = (bt.consumed_type_id if bt.consumed_type_id is not None
                                   else world.default_tile.type_id)
                    for gx, gy, _, tile in self._contact_tile_instances(world):
                        if tile.type_id == bt.id:
                            self.score += int(bt.special_data)
                            world.set_tile(gx, gy, consumed_id)
                elif bt.special == "end_point":
                    # 终点：触发通关（由 main.py 检测）
                    self._reached_end = True
                elif bt.special == "explosive":
                    # 破坏时爆炸（由方块破坏逻辑处理）
                    pass
                elif bt.special == "ender" and bt.special_data is not None:
                    # 随机传送：special_data = (x_range, y_range) 最大偏移
                    import random
                    rx, ry = bt.special_data
                    self._x += random.uniform(-rx, rx)
                    self._y += random.uniform(-ry, ry)

                # ========== 新增功能方块特效 ==========
                elif bt.special == "catapult" and bt.special_data is not None:
                    # 弹射：设置初速度 (vx, vy)
                    if not immune_forces and self._special_cooldowns.get("catapult", 0) <= 0:
                        vx, vy = bt.special_data
                        self.v_x = float(vx)
                        self.v_y = float(vy)
                        self._special_cooldowns["catapult"] = 0.4

                elif bt.special == "dash" and bt.special_data is not None:
                    # 水平冲刺：special_data = 速度
                    if self._special_cooldowns.get("dash", 0) <= 0:
                        self.v_x = float(bt.special_data)
                        self._special_cooldowns["dash"] = 0.3

                elif bt.special == "freeze":
                    # 冻结：清空速度
                    if self._special_cooldowns.get("freeze", 0) <= 0:
                        self.v_x = 0.0
                        self.v_y = 0.0
                        self._special_cooldowns["freeze"] = 0.5

                elif bt.special == "full_heal":
                    # 瞬间满血（一次性）
                    if self._special_cooldowns.get("full_heal", 0) <= 0:
                        self.hp = self.hp_max
                        self._special_cooldowns["full_heal"] = 2.0

                elif bt.special == "full_stamina":
                    # 瞬间满体力（一次性）
                    if self._special_cooldowns.get("full_stamina", 0) <= 0:
                        self.stamina = self.stamina_max
                        self._special_cooldowns["full_stamina"] = 2.0

                elif bt.special == "magnetic" and bt.special_data is not None:
                    if immune_forces:
                        continue
                    # 磁力吸引：向方块中心加速，special_data = 力度
                    force = float(bt.special_data)
                    # Buff: 磁化 (49) 磁力效果加倍
                    if self.has_buff(49):
                        force *= 2.5
                    grect = self.get_game_rect()
                    cx, cy = self._x, self._y
                    # 在接触池中找到该方块坐标
                    for gx, gy, _, tile in self._contact_tile_instances(world):
                        if tile.type_id == bt.id:
                            dx = gx + 0.5 - cx
                            dy = gy + 0.5 - cy
                            dist = max(0.1, (dx*dx + dy*dy) ** 0.5)
                            self.v_x += dx / dist * force * dt * 10
                            self.v_y += dy / dist * force * dt * 10

                elif bt.special == "set_spawn":
                    # 设置重生点（一次性）
                    if self._special_cooldowns.get("set_spawn", 0) <= 0:
                        if hasattr(self, "spawn_pos"):
                            self.spawn_pos = (self._x, self._y)
                            self._special_cooldowns["set_spawn"] = 3.0

                elif bt.special == "fortune" and bt.special_data is not None:
                    # 一次性积分奖励
                    if self._special_cooldowns.get("fortune", 0) <= 0:
                        self.score += int(bt.special_data)
                        self._special_cooldowns["fortune"] = 1.5

                elif bt.special == "poison" and bt.special_data is not None:
                    # 毒：无视50%护盾的伤害
                    raw_dmg = float(bt.special_data) * dt
                    bypass = raw_dmg * 0.5
                    self.take_raw_damage(bypass, bypass_shield=True)
                    self.take_raw_damage(raw_dmg - bypass)

                elif bt.special == "berserk" and bt.special_data is not None:
                    # 狂暴：攻击翻倍但持续受伤
                    mult = float(bt.special_data)
                    self.phys_atk = int(self.phys_atk * mult) if not hasattr(self, '_berserk_active') else self.phys_atk
                    self._berserk_active = True
                    self.take_raw_damage(3.0 * dt)

                elif bt.special == "phantom":
                    # 幻影：接触后3秒内可穿透固体
                    if self._special_cooldowns.get("phantom", 0) <= 0:
                        self._phantom_active = True
                        self._phantom_timer = 3.0
                        self._special_cooldowns["phantom"] = 5.0

                elif bt.special == "slow_field" and bt.special_data is not None:
                    # 减速场
                    self._environment_speed_mult = float(bt.special_data)

                elif bt.special == "gravity_well" and bt.special_data is not None:
                    if immune_forces:
                        continue
                    # 重力井：增加向下的加速度
                    self.v_y -= float(bt.special_data) * dt

                elif bt.special == "wind" and bt.special_data is not None:
                    if immune_forces:
                        continue
                    # 风力：持续推力 (vx, vy)
                    wx, wy = bt.special_data
                    self.v_x += float(wx) * dt
                    self.v_y += float(wy) * dt

                elif bt.special == "echo":
                    # 回声：无功能效果，仅视觉/音频提示（在 main.py 处理）
                    pass

                elif bt.special == "confusion":
                    # 混乱：短暂反转移动方向（铁意免疫）
                    if self.has_buff(40):
                        continue
                    if self._special_cooldowns.get("confusion", 0) <= 0:
                        self._confused = True
                        self._confusion_timer = 2.0
                        self._special_cooldowns["confusion"] = 8.0

        # ---- 时效状态清理 ----
        # 狂暴：离开狂暴方块后重置
        if not any(bt.special == "berserk" for bt in types):
            if hasattr(self, '_berserk_active') and self._berserk_active:
                self.phys_atk = getattr(self, '_base_phys_atk', self.phys_atk)
                self._berserk_active = False

        # 幻影：计时衰减
        if hasattr(self, '_phantom_timer') and self._phantom_timer > 0:
            self._phantom_timer -= dt
            if self._phantom_timer <= 0:
                self._phantom_active = False

        # 混乱：计时衰减
        if hasattr(self, '_confusion_timer') and self._confusion_timer > 0:
            self._confusion_timer -= dt
            if self._confusion_timer <= 0:
                self._confused = False

        # 沉默/勇气/虚弱效果在下次 _apply_tile_effects 时重新计算
        self.refresh_movement_stats()

    def refresh_movement_stats(self):
        """Combine environmental modifiers with active buffs."""
        if hasattr(self, '_base_v_max'):
            speed = self._base_v_max * getattr(self, '_environment_speed_mult', 1.0)
            jump = self._base_v_jump * getattr(self, '_environment_jump_mult', 1.0)
            self.v_max = max(0.0, self.get_buff_stat("v_max", speed))
            self.v_jump = max(0.0, self.get_buff_stat("v_jump", jump))

    # ================================================================
    #  Buff 系统
    # ================================================================
    def apply_buff(self, buff_id: int, params: tuple = (),
                   duration: float = None, source=None):
        """给生物添加一个 buff。已存在则刷新时长。"""
        from buff_system import BUFF_TYPES, BuffInstance, CAT_POSITIVE
        bt = BUFF_TYPES.get(buff_id)
        if bt is None:
            return

        # ---- Buff: 诅咒 (57) 无法获得有益 buff ----
        if bt.category == CAT_POSITIVE and self.has_buff(57):
            return

        # ---- Buff: 铁意 (40) 免疫定身/晕眩/压制/反向 ----
        if buff_id in (21, 27, 28, 23) and self.has_buff(40):
            return

        # 检查冲突：新 buff 会移除冲突列表中的 buff
        for cid in bt.conflicts:
            self.remove_buff(cid)
        # 检查清理：某些 buff 获取时会清除自身
        for cid in bt.cleanup_by:
            if self.has_buff(cid):
                self.remove_buff(buff_id)
                return

        # 已存在则刷新
        for b in self.buffs:
            if b.buff_id == buff_id:
                b.refresh(params, duration)
                b.applied_at = self._buff_game_time
                return

        # 新建
        inst = BuffInstance(buff_id, params, duration, source)
        inst.applied_at = self._buff_game_time
        self.buffs.append(inst)
        # 触发 on_apply 回调
        if bt.on_apply:
            self._dispatch_buff_callback(bt.on_apply, b=inst)

    def remove_buff(self, buff_id: int):
        """移除指定 buff。"""
        from buff_system import BUFF_TYPES
        bt_removed = BUFF_TYPES.get(buff_id)
        self.buffs = [b for b in self.buffs if b.buff_id != buff_id]
        # 触发 on_remove 回调
        if bt_removed and bt_removed.on_remove:
            self._dispatch_buff_callback(bt_removed.on_remove, buff_id=buff_id)

    def _dispatch_buff_callback(self, callback: str, b=None, buff_id: int = None):
        """执行 buff 的 on_apply / on_remove 回调。"""
        from buff_system import BUFF_TYPES
        if buff_id is None and b is not None:
            buff_id = b.buff_id
        bt = BUFF_TYPES.get(buff_id) if buff_id is not None else None
        p = b.params if b is not None else ()

        if callback == "full_heal":
            self.hp = self.hp_max
        elif callback == "full_stamina":
            self.stamina = self.stamina_max
        elif callback == "clear_negative":
            from buff_system import CAT_NEGATIVE
            for cb in list(self.buffs):
                cbt = BUFF_TYPES.get(cb.buff_id)
                if cbt and cbt.category == CAT_NEGATIVE:
                    self.remove_buff(cb.buff_id)
        elif callback == "explode":
            # 对周围敌人造成伤害（预留接口）
            pass
        elif callback == "teleport_spawn":
            if hasattr(self, 'spawn_pos'):
                self._x, self._y = self.spawn_pos

    def has_buff(self, buff_id: int) -> bool:
        return any(b.buff_id == buff_id for b in self.buffs)

    def clear_buffs(self, category: str = None):
        """清除 buff。category 可选 positive/neutral/negative。"""
        from buff_system import BUFF_TYPES, CAT_NEGATIVE
        if category is None:
            self.buffs.clear()
        else:
            self.buffs = [b for b in self.buffs
                          if BUFF_TYPES.get(b.buff_id) and
                          BUFF_TYPES[b.buff_id].category != category]

    def tick_buffs(self, dt: float):
        from status_effects import advance_buffs
        advance_buffs(self, dt)

    def get_buff_stat(self, stat_name: str, base_value: float) -> float:
        from status_effects import modified_stat
        return modified_stat(self, stat_name, base_value)

    # ----- 工具 -----
    def get_center(self) -> Tuple[float, float]:
        return self._x, self._y

    def collide_with(self, other: "Creature") -> bool:
        return self.get_game_rect().collides(other.get_game_rect())

    def reset(self, x: float, y: float):
        self._x = float(x)
        self._y = float(y)
        self.hp = self.hp_max
        self.shield = 0.0
        self.reset_motion()
        self.alive = True
        self.on_ground = False
        self.on_wall_left = False
        self.on_wall_right = False
        self.on_ceiling = False
        self.can_climb = False
        self.is_climbing = False
        self.can_swim = False
        self._swim_force = 0.0
        self._liquid_space_f = 1.0
        self._climb_top_y = None
        self._swim_top_y = None
        self._near_shore = False
        self._shore_dir = 0
        self._shore_exit_pending = False
        self._environment_speed_mult = 1.0
        self._environment_jump_mult = 1.0
        self._stamina_mult = 1.0
        self._silenced = False
        self._courage_dr = 0.0
        self._weakness_mult = 1.0
        self._phantom_active = False
        self._phantom_timer = 0.0
        self._confused = False
        self._confusion_timer = 0.0
        self._berserk_active = False
        self.phys_atk = self._base_phys_atk
        self._special_cooldowns = {}
        self._air_jumps_used = 0
        self._wind_walk_timer = 0.0
        if hasattr(self, '_base_v_max'):
            self.v_max = self._base_v_max
            self.v_jump = self._base_v_jump
        self.fly_mode = False
        self.contact_pool = set()
        self.stand_pool = None
        self.score = 0
        self._reached_end = False


# ===================== 玩家 =====================
class Player(Creature):
    def __init__(self,
                 player_id: int, player_name: str,
                 spawn_x: float, spawn_y: float,
                 key_bind: dict,
                 hp_max: float = 100,
                 shield: float = 0.0,
                 w: float = 0.8,
                 h: float = 1.8,
                 v_max: float = 36.5,
                 v_jump: float = 11.5,
                 f_x: float = 0.985,
                 f_y: float = 0.9965,
                 phys_atk: float = 10,
                 magic_atk: float = 0,
                 phys_res: float = 0,
                 magic_res: float = 0,
                 phys_pen: float = 0,
                 magic_pen: float = 0,
                 k_res: float = 150,
                 dr: float = 0,
                 stamina_max: float = 200.0):
        super().__init__(
            x=spawn_x,
            y=spawn_y,
            w=w,
            h=h,
            hp_max=hp_max,
            shield=shield,
            v_max=v_max,
            v_jump=v_jump,
            a_x=0.0,
            a_y=0.0,
            f_x=f_x,
            f_y=f_y,
            phys_atk=phys_atk,
            magic_atk=magic_atk,
            phys_res=phys_res,
            magic_res=magic_res,
            phys_pen=phys_pen,
            magic_pen=magic_pen,
            k_res=k_res,
            dr=dr,
        )
        self.player_id = player_id
        self.player_name = player_name
        self.spawn_pos = (spawn_x, spawn_y)
        self.key_bind = key_bind
        self.stamina = stamina_max
        self.stamina_max = stamina_max
        self.fly_mode = False
        self.fly_speed = 8.0
        self.costume_id = 1      # 默认时装ID
        self.facing_right = True  # 朝向（True=右, False=左），用于时装渲染翻转
        self._anim_timer = 0.0    # 动画帧计时器（累计秒数）
        self._anim_frame = 0      # 当前动画帧索引
        # 存储基础值，供 speed/jump 特效临时修改后恢复
        self._base_v_max = v_max
        self._base_v_jump = v_jump

    def on_death(self):
        super().on_death()
        # Leave the player dead so the game loop can apply the configured
        # respawn limit and run the death transition exactly once.

    def consume_stamina(self, cost: float) -> bool:
        if self.stamina >= cost:
            self.stamina = self.stamina - cost
            if self.stamina < 0.01:
                self.stamina = 0.0
            return True
        # 扣减失败但体力已极低：归零防止浮点残留
        if self.stamina < 0.01:
            self.stamina = 0.0
        return False

    def recover_stamina(self, amount: float):
        self.stamina = min(self.stamina_max, max(0.0, self.stamina + amount))

    def move(self, dir_x: float):
        self.a_x = dir_x * self.v_max

    # ----- 攀爬控制 -----
    def try_start_climbing(self, world=None) -> bool:
        """若可攀爬则进入攀爬中状态，强制居中防止卡墙。
        必须人物中心在可攀爬方块的垂直范围内（±0.3格容差），防止离梯子很远时误触发。"""
        if not (self.can_climb and not self.is_climbing and self.alive and self.stamina >= 1.0):
            return False
        # 垂直邻近判定：人物中心必须在可攀爬方块的垂直跨度内
        if world is not None:
            grect = self.get_game_rect()
            cy = self._y
            in_range = False
            for gx in range(int(grect.x) - 1, int(grect.x + grect.w) + 2):
                for gy in range(int(grect.y) - 1, int(grect.y + grect.h) + 2):
                    coord = world._wrap_grid_coord(gx, gy)
                    if coord is None:
                        continue
                    bt = world.get_block_type_by_coord(coord[0], coord[1])
                    if bt.climbable:
                        if gy - 0.3 <= cy <= gy + 1 + 0.3:
                            in_range = True
                            break
                if in_range:
                    break
            if not in_range:
                return False
        self.is_climbing = True
        self.v_x = 0.0
        self.v_y = 0.0
        self.a_x = 0.0
        self.a_y = 0.0
        # 强制居中到最近的 climbable 方块中心
        if world is not None:
            grect = self.get_game_rect()
            cx = grect.x + grect.w / 2
            best_x = None
            best_dist = 999.0
            for gx in range(int(grect.x) - 1, int(grect.x + grect.w) + 2):
                for gy in range(int(grect.y) - 1, int(grect.y + grect.h) + 2):
                    coord = world._wrap_grid_coord(gx, gy)
                    if coord is None:
                        continue
                    bt = world.get_block_type_by_coord(coord[0], coord[1])
                    if bt.climbable:
                        block_cx = gx + 0.5
                        dist = abs(cx - block_cx)
                        if dist < best_dist:
                            best_dist = dist
                            best_x = block_cx
            if best_x is not None:
                self._x = best_x
        return True

    def stop_climbing(self):
        """主动解除攀爬状态（落下）。"""
        if self.is_climbing:
            self.is_climbing = False
            self.v_y = 0.0

    def climb_move(self, dy: float, speed: float = 3.0):
        """攀爬中上下移动。dy>0 向上，dy<0 向下。"""
        if self.is_climbing:
            self.v_y = dy * speed
            self.v_x = 0.0
