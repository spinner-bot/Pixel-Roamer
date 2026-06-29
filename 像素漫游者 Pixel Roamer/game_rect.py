# ===================== 游戏坐标系矩形（x右y上） =====================
class GameRect:
    __slots__ = ("x", "y", "w", "h")

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x   # 左下角 x
        self.y = y   # 左下角 y
        self.w = w
        self.h = h

    def collides(self, other: "GameRect") -> bool:
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)
