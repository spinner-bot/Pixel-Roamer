"""
终焉神殿 —— 探索模式 (50×45)
找到终点信标通关。多路线，隐藏房间，3条命。
"""
from world import World

MAP_ID = 7
world = World(
    map_id=MAP_ID, name="终焉神殿",
    w=50, h=45,
    gravity=-6.5, view_blocks_h=18,
    spawn_points=(6, 18),
    mode="explore",
    default_block_id=11,
)
world.lives = 3           # 3条命
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


def wall(x, y0, y1, tid=254):
    for y in range(y0, y1 + 1):
        world.set_tile(x, y, tid)


# ============ 起始室 (x=2~10, y=14~22) ============
fill(0, 0, 49, 0, 68)      # 基岩
fill(2, 14, 10, 17, 19)    # 地板
fill(2, 13, 10, 13, 2)     # 支撑
wall(1, 13, 22, 254)       # 左墙
wall(11, 13, 22, 254)      # 右墙
fill(2, 22, 10, 22, 19)    # 天花板

# 起始设施
world.set_tile(6, 18, 302)  # 检查点
world.set_tile(5, 18, 290)  # 治愈
world.set_tile(7, 19, 291)  # 再生水晶
# 符文提示
world.set_tile(9, 18, 229)  # "找到终点"

# 出口门（右侧y=17处开口）
fill(11, 16, 11, 19, 0)     # 门洞
world.set_tile(11, 20, 229)  # 符文标记

# ============ 东走廊 (x=12~20, y=15~20) ============
fill(12, 15, 20, 16, 230)   # 砂岩地板
fill(12, 14, 20, 14, 2)
fill(12, 20, 20, 20, 230)   # 天花板
wall(12, 15, 20, 254)       # 左墙
wall(20, 15, 20, 254)       # 右墙
# 走廊中的尖刺陷阱
world.set_tile(16, 16, 32)   # 尖刺（需跳过）

# 北向岔路（向上到y=26）
fill(16, 17, 17, 21, 0)     # 开口
for y in range(22, 27):
    world.set_tile(16, y, 31)   # 绳索
    world.set_tile(17, y, 31)
# 上方平台
fill(13, 27, 19, 27, 19)
world.set_tile(16, 28, 310)     # 金币×3
world.set_tile(15, 28, 310)
world.set_tile(17, 28, 310)

# ============ 南侧下层 (x=12~25, y=6~12) ============
# 向下通道
fill(18, 12, 19, 14, 0)     # 开口
fill(18, 11, 19, 11, 2)
for y in range(7, 11):
    world.set_tile(18, y, 31)
    world.set_tile(19, y, 31)
# 下层房间
fill(20, 5, 28, 8, 2)       # 石地板
fill(20, 6, 28, 9, 0)
fill(20, 10, 28, 10, 2)     # 石天花板
world.set_tile(22, 8, 32)    # 尖刺
world.set_tile(26, 8, 32)
world.set_tile(24, 9, 310)   # 金币（奖励探索）
world.set_tile(24, 8, 302)   # 检查点
world.set_tile(23, 7, 290)   # 治愈

# ============ 中央大厅 (x=21~35, y=15~30) ============
fill(21, 14, 35, 14, 2)     # 石底
fill(21, 15, 35, 15, 19)    # 木地板
fill(21, 28, 35, 28, 19)    # 木天花板
wall(21, 15, 28, 228)        # 禅砂墙
wall(35, 15, 28, 228)

# 大厅中央的浮空台
fill(26, 19, 30, 19, 33)    # 云台
world.set_tile(28, 20, 312)  # 红宝石（奖励）
world.set_tile(27, 20, 311)  # 银币
world.set_tile(29, 20, 311)
# 弹跳蘑菇（上台）
world.set_tile(28, 15, 293)

# 大厅上方隐藏平台
fill(24, 25, 26, 25, 33)
world.set_tile(25, 26, 314)  # 钻石水晶（隐藏！）
fill(30, 25, 32, 25, 33)
world.set_tile(31, 26, 314)

# 传送门（去隐藏室）
world.set_tile(28, 17, 300)
if (28, 17) in world.grid:
    world.grid[(28, 17)].meta = {"tp_x": 44, "tp_y": 38}

# ============ 西侧攀爬塔 (x=36~49, y=16~42) ============
fill(36, 15, 49, 15, 230)
fill(37, 16, 48, 18, 0)
# 攀爬墙
for y in range(19, 36):
    world.set_tile(38, y, 10)   # 藤蔓
    world.set_tile(40, y, 10)
    world.set_tile(42, y, 31)   # 绳索
# 各层平台
fill(37, 22, 48, 22, 19)
fill(37, 28, 48, 28, 19)
fill(37, 35, 48, 35, 19)

# 中层陷阱
world.set_tile(39, 23, 32)
world.set_tile(42, 23, 32)
world.set_tile(45, 23, 32)
world.set_tile(43, 27, 264)    # 诅咒地板
world.set_tile(44, 34, 264)

# 攀爬途中奖励
world.set_tile(39, 23, 312)    # 红宝石
world.set_tile(46, 29, 313)    # 蓝宝石
world.set_tile(41, 36, 315)    # 翡翠

# 高层平台——终点入口
fill(38, 37, 47, 37, 19)
world.set_tile(42, 38, 292)    # 护盾
world.set_tile(43, 38, 302)    # 检查点

# ============ 终点密室 (x=36~49, y=38~44) ============
fill(40, 39, 46, 43, 0)
fill(40, 38, 46, 38, 267)     # 奥术法阵天花板
fill(40, 44, 46, 44, 267)     # 奥术法阵地板
world.set_tile(43, 39, 303)    # ★ 终点信标
world.set_tile(43, 40, 257)    # 电弧核心装饰
world.set_tile(42, 39, 314)    # 钻石水晶
world.set_tile(44, 39, 317)    # 虚空宝珠

# 隐藏传送阵目标室（大厅传送门的目的地）
fill(42, 38, 47, 40, 0)
world.set_tile(44, 38, 302)    # 检查点
world.set_tile(45, 39, 316)    # 星币×3
world.set_tile(44, 39, 316)
world.set_tile(46, 39, 316)

# ============ 全图治愈分布 ============
for hx, hy in [(6,18),(24,10),(28,20),(43,38),(36,29),(28,15)]:
    if world.get_tile(hx, hy).type_id == 0:
        world.set_tile(hx, hy, 290)

world.end_bulk_load()
