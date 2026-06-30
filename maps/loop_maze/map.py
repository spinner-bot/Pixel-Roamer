"""
循环迷宫 —— XY双向循环世界 (48×36)
利用循环特性：看似走不通的路，跨过边界就通了
"""
from world import World

MAP_ID = 4
world = World(
    map_id=MAP_ID, name="循环迷宫",
    w=48, h=36,
    gravity=-6.5, view_blocks_h=20,
    spawn_points=(24, 30),
    mode="adventure",
    default_block_id=11,       # 夜晚空气（深色背景）
    loop_x=True, loop_y=True,  # ★ XY双向循环
)
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


# ============ 底层基岩 ============
fill(0, 0, 47, 0, 68)   # 基岩

# ============ 中央枢纽 (x=20~28, y=14~22) ============
# 地板
fill(21, 15, 27, 15, 19)   # 木板
fill(21, 14, 27, 14, 2)    # 石头支撑
# 天花板
fill(21, 22, 27, 22, 19)
# 墙壁（有开口）
for y in range(16, 22):
    world.set_tile(21, y, 254)  # 暗钢墙
    world.set_tile(27, y, 254)
# 开口：左右各留门
world.set_tile(24, 16, 0)  # 右门
world.set_tile(24, 20, 0)  # 左门（上方）

# 枢纽内的设施
world.set_tile(24, 15, 302)  # 检查点
world.set_tile(23, 16, 291)  # 再生水晶
world.set_tile(25, 16, 292)  # 护盾发生器
# 中间的信息柱
for y in range(16, 22):
    world.set_tile(24, y, 265)  # 祝福圣光柱

# ============ 四向通道（利用循环连接）============
# 东通道 (x=28~47, 即向右走到边界外=回到0)
fill(28, 16, 47, 17, 230)   # 砂岩地板
fill(28, 15, 47, 15, 2)     # 石支撑
# 通道装饰
for x in range(29, 47, 4):
    world.set_tile(x, 18, 43)   # 火把
# 弹跳蘑菇（过了边界就是另一边）
world.set_tile(44, 18, 293)

# 西通道 (x=0~20)
fill(0, 20, 20, 21, 230)    # 砂岩地板（不同高度）
fill(0, 19, 20, 19, 2)
for x in range(2, 20, 4):
    world.set_tile(x, 22, 43)

# 北通道 (向上，y=23~35)
fill(22, 23, 26, 35, 220)   # 樱花木板地板
for y in range(24, 36, 3):
    world.set_tile(22, y, 229)  # 符文标记
# 攀爬藤蔓（直达边界外）
for y in range(23, 36):
    world.set_tile(25, y, 10)   # 藤蔓

# 南通道 (向下，y=0~13)
fill(22, 7, 26, 7, 220)     # 下层地板
for y in range(8, 14):
    world.set_tile(23, y, 31)   # 绳索（可攀爬）
    world.set_tile(25, y, 31)

# ============ 四角隐藏房间（跨边界才能到达）============
# 东北角：走过x=47→x=0时进入
fill(0, 28, 6, 32, 244)     # 冰宫墙
fill(1, 29, 5, 31, 0)       # 内部
world.set_tile(3, 29, 240)   # 珍珠块
world.set_tile(3, 29, 302)   # 隐藏检查点
# 入口标记
world.set_tile(47, 16, 248)  # 极光冰（提示跨边界入口）

# 西南角：跨y=0→y=35时进入
fill(12, 33, 18, 35, 230)   # 砂岩
fill(13, 34, 17, 34, 0)     # 内部
world.set_tile(15, 34, 79)   # 金块
world.set_tile(14, 34, 302)  # 隐藏检查点
world.set_tile(15, 7, 248)   # 下方入口提示

# 东南角：x=47且y=0附近
fill(42, 33, 47, 35, 254)   # 暗钢
fill(43, 34, 46, 34, 0)
world.set_tile(44, 34, 291)  # 再生水晶
world.set_tile(45, 34, 302)  # 隐藏检查点

# 西北角：x=0且y=35附近
fill(0, 0, 5, 0, 68)        # 基岩标记
fill(0, 3, 4, 6, 229)       # 符文石
world.set_tile(2, 7, 291)    # 再生水晶

# ============ 浮空平台（跨边界通路）============
# 中央上方的悬浮平台
fill(15, 25, 18, 25, 33)    # 云块
fill(30, 25, 33, 25, 33)
# 弹射板连接
world.set_tile(16, 25, 298)  # 跳跃增强
world.set_tile(31, 25, 298)

# 左右边缘的平台（跨x边界连接）
fill(0, 30, 3, 30, 33)      # 左边缘（会循环到右边）
fill(45, 30, 47, 30, 33)    # 右边缘
world.set_tile(1, 31, 297)   # 加速之路

# ============ 传送门网络（利用meta设置目标）============
# T1: 枢纽 → 东北隐藏室
world.set_tile(26, 15, 300)
if (26, 15) in world.grid:
    world.grid[(26, 15)].meta = {"tp_x": 3, "tp_y": 30}

# T2: 南通道 → 西北隐藏点
world.set_tile(23, 8, 300)
if (23, 8) in world.grid:
    world.grid[(23, 8)].meta = {"tp_x": 2, "tp_y": 8}

# ============ 装饰 ============
# 中央天花板的星夜装饰
world.set_tile(24, 23, 210)  # 星夜虚空
# 边界标记（帮助玩家理解循环）
for x in range(0, 48, 12):
    world.set_tile(x, 35, 212)  # 太阳光辉（顶部边界标记）
    world.set_tile(x, 0, 212)   # 底部标记
for y in range(0, 36, 9):
    world.set_tile(0, y, 212)   # 左边界
    world.set_tile(47, y, 212)  # 右边界

# 治愈点分布
for hx, hy in [(24,15),(3,29),(15,34),(44,34),(2,7),(30,17),(18,21),(40,30)]:
    if world.get_tile(hx, hy).type_id == 0:
        world.set_tile(hx, hy, 290)

world.end_bulk_load()
