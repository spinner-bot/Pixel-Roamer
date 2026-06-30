"""
Buff 系统 — 生物状态效果
BuffType 定义模板，BuffInstance 管理实例，可扩展设计。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Any, List, Dict

# ===================== Buff 类别 =====================
CAT_POSITIVE = "positive"
CAT_NEUTRAL = "neutral"
CAT_NEGATIVE = "negative"


@dataclass
class BuffType:
    """Buff 模板定义（类似 BlockType）。"""
    id: int
    name: str = ""                    # 英文名
    name2: str = ""                   # 中文名
    category: str = CAT_NEUTRAL       # positive / neutral / negative
    icon: Optional[Tuple] = None      # 图标图案（同方块 pattern 格式）
    desc: str = ""                    # 描述模板 {0}→params[0], {1}→params[1] ...
    max_stacks: int = 1               # 最大叠加层数
    conflicts: Tuple[int, ...] = ()   # 冲突 buff ID（获取时移除这些）
    cleanup_by: Tuple[int, ...] = ()  # 被哪些 buff ID 获取时清除
    tick: Optional[str] = None        # 每帧 tick 效果名
    on_apply: Optional[str] = None    # 应用时一次性效果
    on_remove: Optional[str] = None   # 移除时效果


# ===================== Buff 注册表 =====================
BUFF_TYPES: Dict[int, BuffType] = {}


def register(buff: BuffType):
    BUFF_TYPES[buff.id] = buff


# ===================== Buff 实例（运行在生物上） =====================
class BuffInstance:
    """生物身上的一个活跃 buff。"""
    __slots__ = ("buff_id", "params", "applied_at", "duration", "stacks", "source")

    def __init__(self, buff_id: int, params: tuple = (),
                 duration: Optional[float] = None, source=None):
        self.buff_id = buff_id
        self.params = tuple(params)
        self.applied_at = 0.0        # 游戏时间，由 Creature 设置
        self.duration = duration     # None = 永久
        self.stacks = 1
        self.source = source

    @property
    def buff_type(self) -> Optional[BuffType]:
        return BUFF_TYPES.get(self.buff_id)

    @property
    def remaining(self) -> Optional[float]:
        """剩余时间（秒）。永久返回 None。"""
        if self.duration is None:
            return None
        return self.duration

    def tick(self, dt: float):
        """扣除持续时间，返回是否已过期。"""
        if self.duration is None:
            return False
        self.duration -= dt
        return self.duration <= 0

    def refresh(self, params: tuple = None, duration: Optional[float] = None):
        """刷新 buff（重新获取时调用）。"""
        if params is not None:
            self.params = tuple(params)
        if duration is not None:
            self.duration = duration
        if self.stacks < self.buff_type.max_stacks if self.buff_type else 1:
            self.stacks += 1

    def format_desc(self) -> str:
        """将描述模板与 params 拼接，返回最终描述字符串。"""
        bt = self.buff_type
        if not bt or not bt.desc:
            return ""
        s = bt.desc
        for i, p in enumerate(self.params):
            s = s.replace(f"{{{i}}}", str(p))
        return s
