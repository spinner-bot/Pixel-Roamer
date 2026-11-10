from __future__ import annotations
from collections import OrderedDict
from copy import copy, deepcopy
import math
import pygame
from typing import Optional, Tuple, Any

from block_type import BlockType
from block_types_data import BLOCK_TYPES
from game_rect import GameRect
from pattern import render_block_pattern


# ===================== 性能常量 =====================
CHUNK_SIZE = 32          # 每个 Chunk 边长（方块数）
CHUNK_TEX_PX = 16        # Preserve native 16px terrain without downsampling first.
MAX_CHUNK_SURFACES = 64  # 64 MiB base textures, plus the separate scaled budget.
MAX_SCALED_CACHE_BYTES = 64 * 1024 * 1024
MAX_TERRAIN_TEXTURES = 512


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
        self.edge_behavior = edge_behavior
        self.void_limit = 20
        self.view_blocks_h = view_blocks_h

        # ---- 游戏结束条件 ----
        self.lives = 0               # 复活次数，0=无限
        self.score_goal = 0          # 积分目标（score_target模式）
        self.time_limit = 0.0        # 时间限制秒（score_timed模式），0=无限
        self.music = ""              # 背景音乐文件名（music/目录下），空=无
        self.fill_color = (30, 30, 30)  # 地图小于视口时的填充色

        # ---- 旧版存储（保留兼容） ----
        self.grid = {}                     # (gx, gy) → Tile  仅非默认方块

        # ---- 性能优化：实体方块空间索引 ----
        self._solid_index = set()          # {(gx, gy)}  所有 is_solid 的格子坐标
        self._boundary_bt = self.block_types.get(1)  # 缓存边界方块类型

        # ---- 性能优化：方块类型查询加速 ----
        # 直接数组索引比 dict.get() 快约 3-5 倍
        max_id = max(self.block_types.keys()) if self.block_types else 0
        self._bt_fast = [None] * (max_id + 1)
        for bid, bt in self.block_types.items():
            self._bt_fast[bid] = bt
        self._default_bt = self.block_types.get(default_block_id, BLOCK_TYPES[0])

        # ---- 性能优化：Chunk 渲染缓存 ----
        # 每个 Chunk 预渲染为固定像素尺寸的 Surface（方块数×CHUNK_TEX_PX）
        self._chunk_surfaces = OrderedDict()  # (cx, cy) → 原始纹理（LRU 上限）
        self._scaled_chunk_cache = OrderedDict()  # 缩放纹理（按字节数限制）
        self._scaled_chunk_cache_bytes = 0
        self._dirty_chunks = set()         # 待重渲染的 Chunk 键
        self._terrain_textures = OrderedDict()
        self._bulk_loading = False         # 批量加载模式标志

    def create_session(self):
        """Create mutable gameplay state without changing the generated template."""
        session = copy(self)
        session.grid = {
            coord: Tile(tile.type_id, deepcopy(tile.meta))
            for coord, tile in self.grid.items()
        }
        session.default_tile = Tile(self.default_tile.type_id, deepcopy(self.default_tile.meta))
        session._solid_index = self._solid_index.copy()
        session._chunk_surfaces = OrderedDict()
        session._terrain_textures = OrderedDict()
        session._scaled_chunk_cache = OrderedDict()
        session._scaled_chunk_cache_bytes = 0
        session._dirty_chunks = set()
        session._bulk_loading = False
        session.player_config = deepcopy(getattr(self, 'player_config', {}))
        return session

    # ================================================================
    #  坐标包装（内联快速路径）
    # ================================================================
    def _wrap(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        gx, gy = math.floor(x), math.floor(y)
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
        """整数坐标包装。无循环时使用快速路径。"""
        if self.loop_x:
            gx = gx % self.width
        elif gx < 0 or gx >= self.width:
            return None
        if self.loop_y:
            gy = gy % self.height
        elif gy < 0 or gy >= self.height:
            return None
        return gx, gy

    # ================================================================
    #  Chunk 辅助
    # ================================================================
    def _chunk_key(self, gx: int, gy: int) -> Tuple[int, int]:
        return self._chunk_wrap(gx // CHUNK_SIZE, gy // CHUNK_SIZE)

    def _chunk_wrap(self, cx: int, cy: int) -> Tuple[int, int]:
        """Repeat chunk phases at the true tile period, including partial chunks."""
        if self.loop_x:
            cx %= self.width // math.gcd(self.width, CHUNK_SIZE)
        if self.loop_y:
            cy %= self.height // math.gcd(self.height, CHUNK_SIZE)
        return cx, cy

    def _mark_dirty(self, gx: int, gy: int):
        if self.loop_x or self.loop_y:
            # One tile can occur in several chunk phases when a loop is not
            # aligned to CHUNK_SIZE. The bounded caches are cheap to invalidate.
            self._chunk_surfaces.clear()
            self._dirty_chunks.clear()
            self.invalidate_chunks()
            return
        ck = self._chunk_key(gx, gy)
        self._dirty_chunks.add(ck)
        stale = [key for key in self._scaled_chunk_cache if key[:2] == ck]
        for key in stale:
            cached = self._scaled_chunk_cache.pop(key)
            self._scaled_chunk_cache_bytes -= cached.get_pitch() * cached.get_height()

    # ================================================================
    #  Tile 读写
    # ================================================================
    def get_tile(self, x: float, y: float) -> Tile:
        coord = self._wrap(x, y)
        if coord is None:
            return Tile(1) if self.edge_behavior == "solid" else self.default_tile
        return self.grid.get(coord, self.default_tile)

    def get_block_type(self, x: float, y: float) -> BlockType:
        """获取方块类型。使用快速数组查找。"""
        coord = self._wrap(x, y)
        if coord is None:
            if self.edge_behavior == "solid":
                return self._boundary_bt if self._boundary_bt else BLOCK_TYPES[1]
            return self._default_bt
        tile = self.grid.get(coord)
        if tile is None:
            return self._default_bt
        tid = tile.type_id
        if 0 <= tid < len(self._bt_fast):
            bt = self._bt_fast[tid]
            if bt is not None:
                return bt
        return self.block_types.get(tid, BLOCK_TYPES[0])

    def get_block_type_by_coord(self, gx: int, gy: int) -> BlockType:
        """直接用整数坐标查方块类型（跳过 _wrap，调用者保证坐标有效）。"""
        tile = self.grid.get((gx, gy))
        if tile is None:
            return self._default_bt
        tid = tile.type_id
        if 0 <= tid < len(self._bt_fast):
            bt = self._bt_fast[tid]
            if bt is not None:
                return bt
        return self.block_types.get(tid, BLOCK_TYPES[0])

    # ---- 批量加载 ----
    def begin_bulk_load(self):
        """暂停 Chunk 脏标记和实体索引增量更新，用于地图生成。"""
        self._bulk_loading = True

    def end_bulk_load(self):
        """结束批量加载，一次性重建实体索引并标记所有 Chunk 为脏。"""
        self._bulk_loading = False
        # 重建实体索引
        self._solid_index.clear()
        _bt_fast = self._bt_fast
        for coord, tile in self.grid.items():
            tid = tile.type_id
            if 0 <= tid < len(_bt_fast):
                bt = _bt_fast[tid]
            else:
                bt = self.block_types.get(tid)
            if bt and bt.is_solid:
                self._solid_index.add(coord)
        # 标记所有 Chunk 待重建
        self._chunk_surfaces.clear()
        self._scaled_chunk_cache.clear()
        self._scaled_chunk_cache_bytes = 0
        self._dirty_chunks.clear()

    def set_tile(self, x: int, y: int, type_id: int, meta=None):
        coord = self._wrap_grid_coord(x, y)
        if coord is None:
            return

        # 批量加载模式：仅更新 grid，延迟索引/chunk 重建
        if getattr(self, '_bulk_loading', False):
            if type_id == self.default_tile.type_id:
                self.grid.pop(coord, None)
            else:
                self.grid[coord] = Tile(type_id, meta)
            return

        # 获取新方块类型信息
        if 0 <= type_id < len(self._bt_fast):
            new_bt = self._bt_fast[type_id]
        else:
            new_bt = self.block_types.get(type_id)

        if type_id == self.default_tile.type_id:
            # 移除方块
            old = self.grid.pop(coord, None)
            if old is not None:
                self._solid_index.discard(coord)
                self._mark_dirty(x, y)
        else:
            old = self.grid.get(coord)
            if old is None or old.type_id != type_id:
                self.grid[coord] = Tile(type_id, meta)
                if new_bt and new_bt.is_solid:
                    self._solid_index.add(coord)
                else:
                    self._solid_index.discard(coord)
                self._mark_dirty(x, y)
            else:
                # Match bulk-load semantics when only portal/interaction data
                # changes. Metadata does not affect the current terrain raster.
                old.meta = meta

    # ================================================================
    #  碰撞查询（使用实体索引加速）
    # ================================================================
    def get_nearby_solid_blocks_game(self, grect: GameRect, margin: int = 1) -> list:
        """Query only nearby cells, including solid defaults and wrapped copies."""
        min_x = math.floor(grect.x) - margin
        max_x = math.floor(grect.x + grect.w) + margin
        min_y = math.floor(grect.y) - margin
        max_y = math.floor(grect.y + grect.h) + margin
        blocks = []
        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                coord = self._wrap_grid_coord(gx, gy)
                if coord is None:
                    bt = self._boundary_bt if self.edge_behavior == "solid" else None
                else:
                    bt = self.get_block_type_by_coord(*coord)
                if bt is not None and bt.is_solid:
                    blocks.append((GameRect(gx, gy, 1, 1), bt))
        return blocks

    # ================================================================
    #  越界检测
    # ================================================================
    def is_out_of_bounds(self, x: float, y: float) -> bool:
        margin = self.void_limit if self.edge_behavior == "void" else 0
        outside_x = not self.loop_x and (x < -margin or x >= self.width + margin)
        outside_y = not self.loop_y and (y < -margin or y >= self.height + margin)
        return outside_x or outside_y

    # ================================================================
    #  绘制（Chunk 缓存 + 增量重渲染）
    # ================================================================
    def _terrain_texture(self, block_type):
        """Rasterize a terrain definition once instead of hashing it per tile."""
        key = block_type.id
        cached = self._terrain_textures.get(key)
        if (cached is not None and cached[0] is block_type
                and cached[1] == tuple(block_type.color)
                and cached[2] is block_type.pattern):
            self._terrain_textures.move_to_end(key)
            return cached[3]
        texture = pygame.Surface((CHUNK_TEX_PX, CHUNK_TEX_PX))
        render_block_pattern(texture, block_type, 0, 0, CHUNK_TEX_PX, CHUNK_TEX_PX,
                             overdraw=False)
        self._terrain_textures[key] = (block_type, tuple(block_type.color),
                                       block_type.pattern, texture)
        self._terrain_textures.move_to_end(key)
        while len(self._terrain_textures) > MAX_TERRAIN_TEXTURES:
            self._terrain_textures.popitem(last=False)
        return texture

    def _render_chunk(self, ck: Tuple[int, int]):
        """将指定 Chunk 渲染到固定尺寸 Surface 并缓存。"""
        cx, cy = ck
        chunk_w = CHUNK_SIZE
        chunk_h = CHUNK_SIZE
        tex_w = chunk_w * CHUNK_TEX_PX
        tex_h = chunk_h * CHUNK_TEX_PX

        surf = pygame.Surface((tex_w, tex_h))
        # 先填充默认方块底色
        default_color = self._default_bt.color
        surf.fill(default_color)

        # 绘制默认方块图案（若有）
        if self._default_bt.pattern is not None:
            texture = self._terrain_texture(self._default_bt)
            for lx in range(chunk_w):
                for ly in range(chunk_h):
                    px = lx * CHUNK_TEX_PX
                    py = (chunk_h - 1 - ly) * CHUNK_TEX_PX
                    surf.blit(texture, (px, py))

        # 覆盖非默认方块
        base_x = cx * CHUNK_SIZE
        base_y = cy * CHUNK_SIZE
        for ly in range(chunk_h):
            gy = base_y + ly
            for lx in range(chunk_w):
                gx = base_x + lx
                # 循环世界：格子坐标取模
                if self.loop_x:
                    gx = gx % self.width
                if self.loop_y:
                    gy = gy % self.height
                coord = self._wrap_grid_coord(gx, gy)
                if coord is None:
                    continue
                tile = self.grid.get(coord)
                if tile is None:
                    continue
                tid = tile.type_id
                if 0 <= tid < len(self._bt_fast):
                    bt = self._bt_fast[tid]
                else:
                    bt = self.block_types.get(tid)
                if bt is None or bt is self._default_bt:
                    continue

                px = lx * CHUNK_TEX_PX
                # Y 轴翻转：世界坐标 y↑，纹理 y↓
                py = (chunk_h - 1 - ly) * CHUNK_TEX_PX
                surf.blit(self._terrain_texture(bt), (px, py))

        self._chunk_surfaces[ck] = surf
        self._chunk_surfaces.move_to_end(ck)
        while len(self._chunk_surfaces) > MAX_CHUNK_SURFACES:
            self._chunk_surfaces.popitem(last=False)
        self._dirty_chunks.discard(ck)

    def draw(self, surface: pygame.Surface, camera):
        # 空的双向循环小世界在每格远小于一个屏幕像素时无法分辨纹理细节。
        # 直接填充默认色，避免遍历数百万个重复 chunk。
        if (self.loop_x and self.loop_y and not self.grid
                and self.width * camera.scale < 0.5
                and self.height * camera.scale < 0.5):
            surface.fill(self._default_bt.color)
            return

        # 视野范围（世界坐标）
        view_world_w = camera.logic_width / camera.scale
        view_world_h = camera.logic_height / camera.scale
        start_x = int(camera.x - view_world_w / 2) - 1
        end_x = int(camera.x + view_world_w / 2) + 1
        start_y = int(camera.y - view_world_h / 2) - 1
        end_y = int(camera.y + view_world_h / 2) + 1

        # 可见 Chunk 范围
        min_cx = start_x // CHUNK_SIZE
        max_cx = end_x // CHUNK_SIZE
        min_cy = start_y // CHUNK_SIZE
        max_cy = end_y // CHUNK_SIZE

        scale = camera.scale

        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                # 循环世界：Chunk 索引映射到有效范围
                wck = self._chunk_wrap(cx, cy) if (self.loop_x or self.loop_y) else (cx, cy)
                chunk_surf = self._chunk_surfaces.get(wck)
                if chunk_surf is None or wck in self._dirty_chunks:
                    self._render_chunk(wck)
                    chunk_surf = self._chunk_surfaces[wck]
                else:
                    self._chunk_surfaces.move_to_end(wck)

                # Chunk 世界坐标左下角
                chunk_wx = cx * CHUNK_SIZE
                chunk_wy = cy * CHUNK_SIZE
                # 屏幕坐标（左上角）
                sx, sy_top = camera.world_to_screen(chunk_wx, chunk_wy + CHUNK_SIZE)
                right = round(sx + CHUNK_SIZE * scale)
                bottom = round(sy_top + CHUNK_SIZE * scale)
                sx, sy_top = round(sx), round(sy_top)
                blit_w, blit_h = max(1, right - sx), max(1, bottom - sy_top)

                # 缩放至屏幕尺寸（缓存避免每帧分配巨型临时Surface）
                need_scale = (blit_w != CHUNK_SIZE * CHUNK_TEX_PX or blit_h != CHUNK_SIZE * CHUNK_TEX_PX)
                if need_scale:
                    cache_key = (*wck, blit_w, blit_h)
                    scaled = self._scaled_chunk_cache.get(cache_key)
                    if scaled is None:
                        scaled = pygame.transform.scale(chunk_surf, (blit_w, blit_h))
                        size_bytes = scaled.get_pitch() * scaled.get_height()
                        if size_bytes <= MAX_SCALED_CACHE_BYTES:
                            self._scaled_chunk_cache[cache_key] = scaled
                            self._scaled_chunk_cache_bytes += size_bytes
                            while self._scaled_chunk_cache_bytes > MAX_SCALED_CACHE_BYTES:
                                _, evicted = self._scaled_chunk_cache.popitem(last=False)
                                self._scaled_chunk_cache_bytes -= evicted.get_pitch() * evicted.get_height()
                    else:
                        self._scaled_chunk_cache.move_to_end(cache_key)
                    surface.blit(scaled, (sx, sy_top))
                else:
                    surface.blit(chunk_surf, (sx, sy_top))

    def invalidate_chunks(self):
        """丢弃缩放纹理（如窗口 resize）；基础 chunk 纹理可继续复用。"""
        self._scaled_chunk_cache.clear()
        self._scaled_chunk_cache_bytes = 0
