"""Load pixel costumes from JSON and render cached animation frames."""
from __future__ import annotations
from typing import Tuple, Dict, Optional
import pygame
from resource_catalog import load_costumes

COSTUMES, DEFAULT_COSTUME_ID = load_costumes()

# ===================== 预渲染辅助 =====================
def _pixels_to_surface(pixels: list, w: int, h: int) -> pygame.Surface:
    """将二维像素列表转换为带透明通道的 pygame.Surface。
    0 (整数零) 表示透明像素。仅在模块导入时调用。"""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(h):
        row_data = pixels[row]
        for col in range(w):
            color = row_data[col]
            if color != 0:
                surf.set_at((col, row), color)
    return surf


# ===================== 预渲染所有时装源表面（模块导入时一次性执行） =====================
for _cid, _cdata in COSTUMES.items():
    _cdata["src_frames"] = {}
    for _state, _frame_list in _cdata["frames"].items():
        _cdata["src_frames"][_state] = [
            _pixels_to_surface(_f, _cdata["w"], _cdata["h"])
            for _f in _frame_list
        ]


# ===================== 渲染缓存 =====================
_costume_cache: dict = {}  # (costume_id, w, h) → pygame.Surface


def get_costume(costume_id: int) -> Optional[dict]:
    """获取时装数据。"""
    return COSTUMES.get(costume_id)


def list_costumes() -> dict:
    """列出所有时装 {id: name}。"""
    return {c["id"]: c["name"] for c in COSTUMES.values()}


def register_costume(costume_id: int, name: str, name_en: str, desc: str,
                     w: int, h: int, idle_pixels: list) -> None:
    """运行时注册新时装。立即预渲染所有帧，支持热添加。
    初始时所有动画状态共用 idle_pixels（后续可手动扩展 frames）。
    """
    COSTUMES[costume_id] = {
        "id": costume_id,
        "name": name,
        "name_en": name_en,
        "desc": desc,
        "w": w, "h": h,
        "frames": {
            "idle":  [idle_pixels],
            "walk":  [idle_pixels],
            "jump":  [idle_pixels],
            "climb": [idle_pixels],
        },
    }
    # 立即预渲染所有帧
    cdata = COSTUMES[costume_id]
    cdata["src_frames"] = {}
    for state, frame_list in cdata["frames"].items():
        cdata["src_frames"][state] = [
            _pixels_to_surface(f, w, h) for f in frame_list
        ]
    cdata["pixels"] = idle_pixels  # 兼容旧接口
    # 清除旧缓存以确保新时装可被渲染
    _costume_cache.clear()


def render_costume(surface: pygame.Surface, costume_id: int,
                   x: float, y: float, w: float, h: float,
                   flip_h: bool = False,
                   anim_state: str = "idle", anim_frame: int = 0):
    """
    在 surface 的 (x,y,w,h) 矩形区域绘制时装。
    使用预渲染源表面 + 缩放缓存加速重复渲染。
    flip_h=True 时水平翻转（用于角色朝向）。
    anim_state: "idle" | "walk" | "jump" | "climb"
    anim_frame: 当前动画帧索引（自动取模）
    """
    costume = COSTUMES.get(costume_id)
    if costume is None:
        # 未知时装：绘制默认红色
        pygame.draw.rect(surface, (255, 80, 80), (x, y, w, h))
        return

    pw, ph = int(w), int(h)
    if pw <= 0 or ph <= 0:
        return

    # 查找动画帧源表面（带回退到 idle）
    src_frames = costume["src_frames"]
    frames = src_frames.get(anim_state, src_frames["idle"])
    frame_idx = anim_frame % len(frames)
    src = frames[frame_idx]

    cache_key = (costume_id, anim_state, frame_idx, pw, ph)
    if cache_key in _costume_cache:
        scaled = _costume_cache[cache_key]
    else:
        scaled = pygame.transform.scale(src, (pw, ph))
        _costume_cache[cache_key] = scaled

    if flip_h:
        scaled = pygame.transform.flip(scaled, True, False)
    surface.blit(scaled, (x, y))


def render_costume_direct(surface: pygame.Surface, costume_id: int,
                          dest_rect: pygame.Rect, flip_h: bool = False,
                          anim_state: str = "idle", anim_frame: int = 0):
    """直接在目标矩形上绘制时装。"""
    render_costume(surface, costume_id,
                   dest_rect.x, dest_rect.y,
                   dest_rect.w, dest_rect.h, flip_h=flip_h,
                   anim_state=anim_state, anim_frame=anim_frame)


def get_costume_anim_info(costume_id: int) -> Optional[dict]:
    """返回时装的动画信息 {state_name: frame_count}，未找到返回 None。"""
    costume = COSTUMES.get(costume_id)
    if costume is None:
        return None
    return {state: len(frames) for state, frames in costume["frames"].items()}


def clear_costume_cache():
    """清除缩放缓存。地图切换时调用，不影响预渲染源表面。"""
    _costume_cache.clear()


def get_costume_cache_info() -> dict:
    """返回缓存诊断信息 {entries, total_pixels}。"""
    total_pixels = sum(s.get_width() * s.get_height() for s in _costume_cache.values())
    return {"entries": len(_costume_cache), "total_pixels": total_pixels}


# ---- 兼容旧接口：仍可通过 costumes["pixels"] 访问原始像素数据 ----
for _cid, _cdata in COSTUMES.items():
    _cdata["pixels"] = _cdata["frames"]["idle"][0]  # 指向 idle 第一帧
