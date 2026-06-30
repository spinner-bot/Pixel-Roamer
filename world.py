from __future__ import annotations
import pygame
from typing import Optional, Tuple, Any

from block_type import BlockType
from block_types_data import BLOCK_TYPES
from game_rect import GameRect
from pattern import render_block_pattern


# ===================== 性能常量 =====================
CHUNK_SIZE = 32          # 每个 Chunk 边长（方块数）
CHUNK_TEX_PX = 10        # Chunk 纹理中每方块的像素（平衡质量与内存）


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
        self._chunk_surfaces = {}          # (cx, cy) → pygame.Surface (原始纹理)
        self._scaled_chunk_cache = {}      # (cx, cy, blit_w, blit_h) → pygame.Surface (缩放后)
        self._dirty_chunks = set()         # 待重渲染的 Chunk 键
        self._chunk_initialized = False    # 首次绘制时批量构建
        self._bulk_loading = False         # 批量加载模式标志

    # ================================================================
    #  坐标包装（内联快速路径）
    # ================================================================
    def _wrap(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        gx, gy = int(x), int(y)
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
        """返回格子所属 Chunk 的键。循环世界自动取模。"""
        cx = gx // CHUNK_SIZE
        cy = gy // CHUNK_SIZE
        if self.loop_x:
            cx = cx % max(1, (self.width + CHUNK_SIZE - 1) // CHUNK_SIZE)
        if self.loop_y:
            cy = cy % max(1, (self.height + CHUNK_SIZE - 1) // CHUNK_SIZE)
        return (cx, cy)

    def _chunk_wrap(self, cx: int, cy: int) -> Tuple[int, int]:
        """将 Chunk 索引按循环规则包裹到有效范围。"""
        if self.loop_x:
            cx = cx % max(1, (self.width + CHUNK_SIZE - 1) // CHUNK_SIZE)
        if self.loop_y:
            cy = cy % max(1, (self.height + CHUNK_SIZE - 1) // CHUNK_SIZE)
        return (cx, cy)

    def _mark_dirty(self, gx: int, gy: int):
        """标记某个方块所在的 Chunk 需要重渲染。循环世界同时标记所有副本。"""
        ck = self._chunk_key(gx, gy)
        self._dirty_chunks.add(ck)
        if self.loop_x or self.loop_y:
            ncx = max(1, (self.width + CHUNK_SIZE - 1) // CHUNK_SIZE)
            ncy = max(1, (self.height + CHUNK_SIZE - 1) // CHUNK_SIZE)
            for dck in list(self._chunk_surfaces.keys()):
                if dck[0] % ncx == ck[0] % ncx and dck[1] % ncy == ck[1] % ncy:
                    self._dirty_chunks.add(dck)
        # 缩放缓存：循环世界要失效所有映射到同一Chunk的副本
        if self.loop_x or self.loop_y:
            ncx = max(1, (self.width + CHUNK_SIZE - 1) // CHUNK_SIZE)
            ncy = max(1, (self.height + CHUNK_SIZE - 1) // CHUNK_SIZE)
            stale = [k for k in self._scaled_chunk_cache
                     if k[0] % ncx == ck[0] % ncx and k[1] % ncy == ck[1] % ncy]
        else:
            stale = [k for k in self._scaled_chunk_cache
                     if k[0] == ck[0] and k[1] == ck[1]]
        for k in stale:
            del self._scaled_chunk_cache[k]

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
        self._chunk_initialized = False
        self._chunk_surfaces.clear()
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

    # ================================================================
    #  碰撞查询（使用实体索引加速）
    # ================================================================
    def get_nearby_solid_blocks_game(self, grect: GameRect, margin: int = 1) -> list:
        """返回与 grect 附近所有实体方块的 (GameRect, BlockType) 列表。

        优化：使用 _solid_index 预过滤，跳过大量空气方块。
        对于稠密地图回退到逐格扫描。
        """
        min_x = int(grect.x) - margin
        max_x = int(grect.x + grect.w) + margin
        min_y = int(grect.y) - margin
        max_y = int(grect.y + grect.h) + margin
        total_cells = (max_x - min_x + 1) * (max_y - min_y + 1)

        blocks = []
        _solid = self._solid_index
        _grid = self.grid
        _wrap = self._wrap_grid_coord
        _bt_fast = self._bt_fast
        _loop_x = self.loop_x
        _loop_y = self.loop_y
        _w = self.width
        _h = self.height
        _edge = self.edge_behavior
        _boundary_bt = self._boundary_bt

        # 循环世界：稀疏路径在边界处会漏掉对侧方块，直接走逐格扫描
        if _loop_x or _loop_y or len(_solid) > total_cells * 0.7:
            # 稠密地图：逐格扫描
            for gx in range(min_x, max_x + 1):
                for gy in range(min_y, max_y + 1):
                    coord = _wrap(gx, gy)
                    if coord is None:
                        if _edge == "solid" and _boundary_bt and _boundary_bt.is_solid:
                            blocks.append((GameRect(gx, gy, 1, 1), _boundary_bt))
                        continue
                    tile = _grid.get(coord)
                    if tile is not None:
                        tid = tile.type_id
                        if 0 <= tid < len(_bt_fast):
                            bt = _bt_fast[tid]
                        else:
                            bt = self.block_types.get(tid)
                        if bt and bt.is_solid:
                            blocks.append((GameRect(gx, gy, 1, 1), bt))
        else:
            # 稀疏地图：通过实体索引快速过滤
            # 确定查询范围内的 Chunk 范围
            c_min_x = min_x // CHUNK_SIZE
            c_max_x = max_x // CHUNK_SIZE
            c_min_y = min_y // CHUNK_SIZE
            c_max_y = max_y // CHUNK_SIZE

            for gx, gy in _solid:
                # 快速排除不在范围内的坐标
                if gx < min_x or gx > max_x or gy < min_y or gy > max_y:
                    continue
                coord = _wrap(gx, gy)
                if coord is None:
                    continue
                tile = _grid.get(coord)
                if tile is None:
                    continue
                tid = tile.type_id
                if 0 <= tid < len(_bt_fast):
                    bt = _bt_fast[tid]
                else:
                    bt = self.block_types.get(tid)
                if bt and bt.is_solid:
                    blocks.append((GameRect(gx, gy, 1, 1), bt))

            # 边界处理
            if _edge == "solid" and _boundary_bt and _boundary_bt.is_solid:
                for gx in range(min_x, max_x + 1):
                    for gy in range(min_y, max_y + 1):
                        if _wrap(gx, gy) is None:
                            blocks.append((GameRect(gx, gy, 1, 1), _boundary_bt))

        return blocks

    # ================================================================
    #  越界检测
    # ================================================================
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

    # ================================================================
    #  绘制（Chunk 缓存 + 增量重渲染）
    # ================================================================
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
            for lx in range(chunk_w):
                for ly in range(chunk_h):
                    px = lx * CHUNK_TEX_PX
                    py = (chunk_h - 1 - ly) * CHUNK_TEX_PX
                    render_block_pattern(surf, self._default_bt, px, py, CHUNK_TEX_PX, CHUNK_TEX_PX)

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
                render_block_pattern(surf, bt, px, py, CHUNK_TEX_PX, CHUNK_TEX_PX)

        self._chunk_surfaces[ck] = surf
        self._dirty_chunks.discard(ck)

    def _rebuild_all_chunks(self):
        """首次绘制或 scale 变化时重建所有 Chunk。"""
        self._chunk_surfaces.clear()
        self._dirty_chunks.clear()
        # 收集所有有非默认方块的 Chunk + 脏 Chunk
        all_chunks = set()
        for gx, gy in self.grid:
            all_chunks.add(self._chunk_key(gx, gy))
        for ck in all_chunks:
            self._render_chunk(ck)
        self._chunk_initialized = True

    def draw(self, surface: pygame.Surface, camera):
        # 视野范围（世界坐标）
        view_world_w = camera.logic_width / camera.scale
        view_world_h = camera.logic_height / camera.scale
        start_x = int(camera.x - view_world_w / 2) - 1
        end_x = int(camera.x + view_world_w / 2) + 1
        start_y = int(camera.y - view_world_h / 2) - 1
        end_y = int(camera.y + view_world_h / 2) + 1

        # 首次或 scale 变化时重建
        if not self._chunk_initialized:
            self._rebuild_all_chunks()

        # 重渲染脏 Chunk
        for ck in list(self._dirty_chunks):
            self._render_chunk(ck)

        # 可见 Chunk 范围
        min_cx = start_x // CHUNK_SIZE
        max_cx = end_x // CHUNK_SIZE
        min_cy = start_y // CHUNK_SIZE
        max_cy = end_y // CHUNK_SIZE

        scale = camera.scale
        blit_w = int(CHUNK_SIZE * scale)
        blit_h = int(CHUNK_SIZE * scale)

        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                # 循环世界：Chunk 索引映射到有效范围
                wck = self._chunk_wrap(cx, cy) if (self.loop_x or self.loop_y) else (cx, cy)
                ck = (cx, cy)  # 屏幕位置用原始 cx,cy
                chunk_surf = self._chunk_surfaces.get(wck)
                if chunk_surf is None:
                    # 此 Chunk 无任何非默认方块——只绘制默认底色
                    chunk_surf = self._render_empty_chunk(wck)

                # Chunk 世界坐标左下角
                chunk_wx = cx * CHUNK_SIZE
                chunk_wy = cy * CHUNK_SIZE
                # 屏幕坐标（左上角）
                sx, sy_top = camera.world_to_screen(chunk_wx, chunk_wy + CHUNK_SIZE)

                # 缩放至屏幕尺寸（缓存避免每帧分配巨型临时Surface）
                need_scale = (blit_w != CHUNK_SIZE * CHUNK_TEX_PX or blit_h != CHUNK_SIZE * CHUNK_TEX_PX)
                if need_scale:
                    cache_key = (cx, cy, blit_w, blit_h)
                    scaled = self._scaled_chunk_cache.get(cache_key)
                    if scaled is None:
                        scaled = pygame.transform.scale(chunk_surf, (blit_w, blit_h))
                        self._scaled_chunk_cache[cache_key] = scaled
                    surface.blit(scaled, (sx, sy_top))
                else:
                    surface.blit(chunk_surf, (sx, sy_top))

    def _render_empty_chunk(self, ck: Tuple[int, int]) -> pygame.Surface:
        """仅为默认方块填充的 Chunk 创建 Surface（懒加载+缓存）。"""
        tex_w = CHUNK_SIZE * CHUNK_TEX_PX
        tex_h = CHUNK_SIZE * CHUNK_TEX_PX
        surf = pygame.Surface((tex_w, tex_h))
        default_color = self._default_bt.color
        surf.fill(default_color)

        if self._default_bt.pattern is not None:
            for lx in range(CHUNK_SIZE):
                for ly in range(CHUNK_SIZE):
                    px = lx * CHUNK_TEX_PX
                    py = (CHUNK_SIZE - 1 - ly) * CHUNK_TEX_PX
                    render_block_pattern(surf, self._default_bt, px, py, CHUNK_TEX_PX, CHUNK_TEX_PX)

        self._chunk_surfaces[ck] = surf
        return surf

    def invalidate_chunks(self):
        """强制下次绘制时重建所有 Chunk（如窗口 resize 导致 scale 变化）。"""
        self._chunk_initialized = False
        self._scaled_chunk_cache.clear()
