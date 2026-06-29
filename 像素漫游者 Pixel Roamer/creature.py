from __future__ import annotations
import math
import pygame
from typing import TYPE_CHECKING, Optional, Tuple, Any

from constants import RES_NORMAL_SCALE, CORR_FLOOR
from game_rect import GameRect
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
        f_y: float = 0.98,
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

    # ----- 游戏矩形 -----
    def get_game_rect(self) -> GameRect:
        return GameRect(self._x - self._w / 2, self._y - self._h / 2, self._w, self._h)

    def set_from_game_rect(self, grect: GameRect):
        self._x = grect.x + grect.w / 2
        self._y = grect.y + grect.h / 2

    # ----- 战斗 -----
    def clamp_velocity(self):
        self.v_x = max(-self.v_max, min(self.v_x, self.v_max))

    def take_damage(self, phys_damage: float, magic_damage: float,
                    phys_pen: float = 0.0, magic_pen: float = 0.0) -> float:
        if not self.alive:
            return 0.0

        x_phys = (phys_pen - self.phys_res) / RES_NORMAL_SCALE
        x_phys = max(-1.0, min(x_phys, 1.0))
        phys_correction = max(x_phys, CORR_FLOOR, 0.95 * math.sin(x_phys) + 0.15 * (x_phys ** 2))
        phys_mult = 1.0 + phys_correction

        x_magic = (magic_pen - self.magic_res) / RES_NORMAL_SCALE
        x_magic = max(-1.0, min(x_magic, 1.0))
        magic_correction = max(x_magic, CORR_FLOOR, 0.95 * math.sin(x_magic) + 0.15 * (x_magic ** 2))
        magic_mult = 1.0 + magic_correction

        total_raw = phys_damage * phys_mult + magic_damage * magic_mult
        damage = total_raw * (1 - self.dr)

        if damage <= 0:
            return 0.0

        if self.shield > 0:
            if self.shield >= damage:
                self.shield -= damage
                return damage
            else:
                damage -= self.shield
                self.shield = 0

        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.on_death()
        return damage

    def take_raw_damage(self, damage: float) -> float:
        if not self.alive or damage <= 0:
            return 0.0
        if self.shield > 0:
            if self.shield >= damage:
                self.shield -= damage
                return damage
            else:
                damage -= self.shield
                self.shield = 0
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.on_death()
        return damage

    def heal(self, amount: float) -> float:
        if not self.alive or amount <= 0:
            return 0.0
        recover = min(amount, self.hp_max - self.hp)
        self.hp += recover
        return recover

    def add_shield(self, amount: float, max_shield: float = None) -> float:
        if not self.alive or amount <= 0:
            return 0.0
        if max_shield is not None:
            target = min(self.shield + amount, max_shield)
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
        """跳跃。可从地面或攀爬中起跳；攀爬中跳跃会解除攀爬状态。"""
        can_jump = self.on_ground or (self.is_climbing and not_on_ground_ok) or (self.is_climbing and self.alive)
        if (not_on_ground_ok or self.on_ground or self.is_climbing) and self.alive:
            self.v_y = self.v_jump
            self.on_ground = False
            self.is_climbing = False
            return True
        return False

    def update_physics(self, dt: float, world):
        if not self.alive:
            return
        # 飞行模式：完全跳过物理
        if getattr(self, 'fly_mode', False):
            return
        # 攀爬中：无重力，仅保留手动设置的 v_y
        if self.is_climbing:
            self.v_y += self.a_y * dt  # 不含 gravity
            self.clamp_velocity()
            return
        self.v_x += self.a_x * dt
        self.v_y += self.a_y * dt
        self.v_y += world.gravity * dt
        self.clamp_velocity()

    # ----- 采样：仅自身矩形微扩 0.01，不做整格扩展 -----
    def _sample_contact_tiles(self, grect: GameRect, world):
        """返回所有接触到的方块ID集合（不负责边界方块）"""
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
        for gx in range(min_gx, max_gx + 1):
            for gy in range(min_gy, max_gy + 1):
                bt = world.get_block_type(gx + 0.5, gy + 0.5)
                if bt.id != 0:
                    tiles.add(bt.id)
        return tiles

    # ----- 碰撞与效果总控 -----
    def collide_with_world(self, world, dt: float):
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

        # 液体空间阻力
        liquid_space = min((bt.space_f for bt in block_types_list if bt.space_f != 1.0), default=1.0)
        if liquid_space < 1.0:
            final_fx *= liquid_space
            final_fy *= liquid_space

        self.v_x *= pow(final_fx, dt * 60)
        self.v_y *= pow(final_fy, dt * 60)

        # ---------- 阶段2：分轴碰撞修正 ----------
        self.on_ground = False
        self.on_wall_left = False
        self.on_wall_right = False
        self.on_ceiling = False

        # X轴
        grect.x += self.v_x * dt
        for block_grect, bt in world.get_nearby_solid_blocks_game(grect):
            if grect.collides(block_grect) and not bt.one_way:
                if self.v_x > 0:
                    grect.x = block_grect.x - grect.w
                    self.on_wall_right = True
                elif self.v_x < 0:
                    grect.x = block_grect.x + block_grect.w
                    self.on_wall_left = True
                self.v_x = 0

        # Y轴
        grect.y += self.v_y * dt
        for block_grect, bt in world.get_nearby_solid_blocks_game(grect):
            if grect.collides(block_grect):
                if bt.one_way:
                    if self.v_y < 0 and (grect.y - self.v_y * dt) >= block_grect.y + block_grect.h + 0.001:
                        grect.y = block_grect.y + block_grect.h
                        self.v_y = 0
                        self.on_ground = True
                    continue
                if self.v_y < 0:
                    grect.y = block_grect.y + block_grect.h
                    self.on_ground = True
                elif self.v_y > 0:
                    grect.y = block_grect.y - grect.h
                    self.on_ceiling = True
                self.v_y = 0

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
        if not all_ids:
            return

        types = []
        for bid in all_ids:
            bt = world.block_types.get(bid)
            if bt:
                types.append(bt)
        if not types:
            return

        self.can_climb = any(bt.climbable for bt in types)

        # 攀爬中但已离开可攀爬方块：自动解除攀爬状态
        if self.is_climbing and not self.can_climb:
            self.is_climbing = False
            self.v_y = 0.0

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
            self.take_raw_damage(max_dps * dt)

        for bt in types:
            if bt.special is not None:
                if bt.special == "teleport" and bt.special_data is not None:
                    tx, ty = bt.special_data
                    self._x = float(tx)
                    self._y = float(ty)
                elif bt.special == "checkpoint":
                    if hasattr(self, "spawn_pos"):
                        self.spawn_pos = (self._x, self._y)

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
        self.fly_mode = False
        self.contact_pool = set()
        self.stand_pool = None


# ===================== 玩家 =====================
class Player(Creature):
    def __init__(self, player_id: int, player_name: str, spawn_x: float, spawn_y: float, key_bind: dict, hp_max: float=100):
        super().__init__(
            x=spawn_x,
            y=spawn_y,
            w=0.8,
            h=1.8,
            hp_max=hp_max,
            v_max=36.5,
            v_jump=26.5,         # 正数向上
            a_x=0.0,
            a_y=0.0,
            f_x=0.985,
            f_y=0.98,
            phys_atk=10,
            magic_atk=0,
            phys_res=0,
            magic_res=0,
            phys_pen=0,
            magic_pen=0,
            dr=0
        )
        self.player_id = player_id
        self.player_name = player_name
        self.spawn_pos = (spawn_x, spawn_y)
        self.key_bind = key_bind
        self.stamina = 100.0
        self.stamina_max = 100.0
        self.fly_mode = False
        self.fly_speed = 8.0

    def on_death(self):
        super().on_death()
        self.reset(*self.spawn_pos)
        self.stamina = self.stamina_max

    def consume_stamina(self, cost: float) -> bool:
        if self.stamina >= cost:
            self.stamina -= cost
            return True
        return False

    def recover_stamina(self, amount: float):
        self.stamina = min(self.stamina_max, self.stamina + amount)

    def move(self, dir_x: float):
        self.a_x = dir_x * self.v_max

    # ----- 攀爬控制 -----
    def try_start_climbing(self) -> bool:
        """若可攀爬则进入攀爬中状态，返回是否成功。"""
        if self.can_climb and not self.is_climbing and self.alive:
            self.is_climbing = True
            self.v_x = 0.0
            self.v_y = 0.0
            return True
        return False

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
