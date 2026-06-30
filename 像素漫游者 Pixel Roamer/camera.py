from __future__ import annotations
import pygame
from typing import TYPE_CHECKING, Tuple

from game_rect import GameRect

if TYPE_CHECKING:
    from world import World


# ===================== 相机系统（y向上 → 屏幕y向下） =====================
class Camera:
    def __init__(self, logic_width: int, logic_height: int, world: "World"):
        self.logic_width = logic_width
        self.logic_height = logic_height
        self.world = world
        self.scale = logic_height / world.view_blocks_h
        self.x = 0.0   # 相机中心游戏 x
        self.y = 0.0   # 相机中心游戏 y

    def follow(self, target_x: float, target_y: float):
        """跟随目标点（游戏坐标），循环世界不钳制边界"""
        self.x = target_x
        self.y = target_y

        half_world_w = (self.logic_width / self.scale) / 2
        half_world_h = (self.logic_height / self.scale) / 2

        if not self.world.loop_x:
            # 视口大于地图时，居中显示地图
            if half_world_w * 2 >= self.world.width:
                self.x = self.world.width / 2
            else:
                if self.x - half_world_w < 0:
                    self.x = half_world_w
                if self.x + half_world_w > self.world.width:
                    self.x = self.world.width - half_world_w

        if not self.world.loop_y:
            # 视口大于地图时，居中显示地图
            if half_world_h * 2 >= self.world.height:
                self.y = self.world.height / 2
            else:
                if self.y - half_world_h < 0:
                    self.y = half_world_h
                if self.y + half_world_h > self.world.height:
                    self.y = self.world.height - half_world_h

    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        """游戏坐标（x右y上）→ 逻辑画布像素坐标（y下）"""
        sx = (wx - self.x) * self.scale + self.logic_width / 2
        sy = self.logic_height / 2 - (wy - self.y) * self.scale
        return sx, sy

    def game_rect_to_screen_rect(self, grect: GameRect) -> pygame.Rect:
        """游戏矩形 → 屏幕矩形（用于绘制）"""
        # 矩形左上角在游戏坐标中为 (grect.x, grect.y + grect.h)
        sx, sy_top = self.world_to_screen(grect.x, grect.y + grect.h)
        sw = grect.w * self.scale
        sh = grect.h * self.scale
        return pygame.Rect(sx, sy_top, sw, sh)
