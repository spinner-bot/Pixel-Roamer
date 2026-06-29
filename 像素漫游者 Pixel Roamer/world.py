from __future__ import annotations
import pygame
from typing import Optional, Tuple, Any

from block_type import BlockType
from block_types_data import BLOCK_TYPES
from game_rect import GameRect
from pattern import render_block_pattern


# ===================== 地图格子与 World =====================
class Tile:
    __slots__ = ("type_id", "meta")

    def __init__(self, type_id: int, meta: Any = None):
        self.type_id = type_id
        self.meta = meta


class World:
    def __init__(self,
                 map_id: int,
                 name: str,
                 w: int,
                 h: int,
                 loop_x: bool = False,
                 loop_y: bool = False,
                 gravity: float = -0.7,
                 spawn_points: tuple = None,
                 mode: str = "adventure",
                 block_types: dict = None,
                 default_block_id: int = 0,
                 edge_behavior: str = "solid",
                 view_blocks_h: float = 15.0):
        self.map_id = map_id
        self.name = name
        self.mode = mode
        self.gravity = gravity
        self.spawn_points = spawn_points or (0, 0)
        self.width = w
        self.height = h
        self.loop_x = loop_x
        self.loop_y = loop_y
        self.block_types = block_types if block_types is not None else BLOCK_TYPES
        self.default_tile = Tile(default_block_id)
        self.grid = {}
        self.edge_behavior = edge_behavior
        self.void_limit = 20
        self.view_blocks_h = view_blocks_h

    def _wrap(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        gx = int(x)
        gy = int(y)
        if self.loop_x:
            gx = gx % self.width
        elif gx < 0 or gx >= self.width:
            return None
        if self.loop_y:
            gy = gy % self.height
        elif gy < 0 or gy >= self.height:
            return None
        return gx, gy

    def _wrap_grid_coord(self, gx: int, gy: int) -> Optional[Tuple[int, int]]:
        if self.loop_x:
            gx = gx % self.width
        if self.loop_y:
            gy = gy % self.height
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return gx, gy
        return None

    def get_tile(self, x: float, y: float) -> Tile:
        coord = self._wrap(x, y)
        if coord is None:
            if self.edge_behavior == "solid":
                return Tile(1)
            else:
                return self.default_tile
        tile = self.grid.get(coord)
        if tile is None:
            return self.default_tile
        return tile

    def get_block_type(self, x: float, y: float) -> BlockType:
        tile = self.get_tile(x, y)
        return self.block_types.get(tile.type_id, BLOCK_TYPES[0])

    def set_tile(self, x: int, y: int, type_id: int, meta=None):
        coord = self._wrap_grid_coord(x, y)
        if coord is None:
            return
        if type_id == self.default_tile.type_id:
            self.grid.pop(coord, None)
        else:
            self.grid[coord] = Tile(type_id, meta)

    def get_nearby_solid_blocks_game(self, grect: GameRect, margin: int = 1) -> list:
        blocks = []
        min_x = int(grect.x) - margin
        max_x = int(grect.x + grect.w) + margin
        min_y = int(grect.y) - margin
        max_y = int(grect.y + grect.h) + margin
        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                coord = self._wrap_grid_coord(gx, gy)
                if coord is None:
                    if self.edge_behavior == "solid":
                        bt = self.block_types.get(1)
                        if bt and bt.is_solid:
                            block_rect = GameRect(gx, gy, 1, 1)
                            blocks.append((block_rect, bt))
                    continue
                tile = self.grid.get(coord)
                if tile is None:
                    tile = self.default_tile
                bt = self.block_types.get(tile.type_id)
                if bt and bt.is_solid:
                    block_rect = GameRect(gx, gy, 1, 1)
                    blocks.append((block_rect, bt))
        return blocks

    def is_out_of_bounds(self, x: float, y: float) -> bool:
        gx, gy = int(x), int(y)
        if self.loop_x or self.loop_y:
            return False
        if self.edge_behavior == "void":
            if (gx < -self.void_limit or gx >= self.width + self.void_limit or
                    gy < -self.void_limit or gy >= self.height + self.void_limit):
                return True
            return False
        return gx < 0 or gx >= self.width or gy < 0 or gy >= self.height

    def draw(self, surface: pygame.Surface, camera):
        # 视野范围
        view_world_w = camera.logic_width / camera.scale
        view_world_h = camera.logic_height / camera.scale
        start_x = int(camera.x - view_world_w / 2) - 1
        end_x = int(camera.x + view_world_w / 2) + 1
        start_y = int(camera.y - view_world_h / 2) - 1
        end_y = int(camera.y + view_world_h / 2) + 1

        for gx in range(start_x, end_x + 1):
            for gy in range(start_y, end_y + 1):
                coord = self._wrap_grid_coord(gx, gy)
                if coord is None:
                    # 越界：若边缘为实心则绘制边界墙，否则跳过
                    if self.edge_behavior == "solid":
                        bt = self.block_types.get(1)
                        if bt is None:
                            continue
                    else:
                        continue
                else:
                    # 合法坐标：取 grid 中的方块，若无则用默认方块
                    tile = self.grid.get(coord)
                    if tile is None:
                        tile = self.default_tile
                    bt = self.block_types.get(tile.type_id)
                    if bt is None:
                        continue

                # 绘制方块：使用图案系统（包含底色）
                sx, sy = camera.world_to_screen(gx, gy + 1)
                block_w = camera.scale
                block_h = camera.scale
                render_block_pattern(surface, bt, sx, sy, block_w, block_h)
