from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Any


# ===================== 方块类型 =====================
@dataclass
class BlockType:
    id: int
    name: str = ""
    name2: str = ""
    is_solid: bool = True
    one_way: bool = False
    climbable: bool = False
    surface_f: float = 1.0
    space_f: float = 1.0
    swim_f: float = 0.0              # 浮力（>0 可游泳，值越大上浮越快）
    bounce: Tuple[float, float] = (0.0, 0.0)    # (vx, vy) 正 vy 向上
    accel_k: Tuple[float, float] = (0.0, 0.0)
    accel_b: Tuple[float, float] = (0.0, 0.0)
    damage_ps: float = 0.0
    k_stamina: float = 1.0
    special: Optional[str] = None
    special_data: Any = None
    break_level: int = 15
    break_hp: float = 100.0
    break_special: Optional[str] = None
    drops_item_id: Optional[str] = None
    light_level: int = 0
    color: Tuple[int, int, int] = (128, 128, 128)
    # 图案属性：为 None 时仅使用纯色底色
    pattern: Optional[Tuple] = None
    # Buff 触发（接触时自动施加）
    buff_id: Optional[int] = None       # 施加的 buff ID
    buff_params: Tuple = ()             # buff 参数
    buff_duration: Optional[float] = None  # 持续时间（秒），None=永久
