"""
无限森林 —— 仅X轴横向循环世界 (80×45)
向左右无限延伸的森林，循环边界无缝衔接
"""
from world import World
import math, random

MAP_ID = 6
world = World(
    map_id=MAP_ID, name="无限森林",
    w=80, h=45,
    gravity=-6.5, view_blocks_h=18,
    spawn_points=(40, 22),
    mode="adventure",
    default_block_id=0,     # 天空
    loop_x=True, loop_y=False,  # ★ 仅X轴循环
)
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


# ============ 基岩 ============
fill(0, 0, 79, 0, 68)
fill(0, 1, 79, 1, 67)

# ============ 无缝循环地形 ============
# 使用 sin/cos 组合确保 x=0 和 x=79 处高度连续
for x in range(0, 80):
    # 地表高度：利用周期函数保证循环连续性
    angle = x / 80.0 * 2 * math.pi
    ground = 14 + int(
        4 * math.sin(angle * 3) +
        3 * math.cos(angle * 5 + 1) +
        2 * math.sin(angle * 7 - 2)
    )
    # 地下填充
    for y in range(2, ground):
        world.set_tile(x, y, 16)  # 泥土
    # 地表
    world.set_tile(x, ground, 17)  # 草地

# ============ 树木（循环感知）============
tree_positions = [4, 12, 22, 30, 38, 48, 56, 66, 74]
for tx in tree_positions:
    # 找到该位置的地表高度
    angle = tx / 80.0 * 2 * math.pi
    ground = 14 + int(
        4 * math.sin(angle * 3) +
        3 * math.cos(angle * 5 + 1) +
        2 * math.sin(angle * 7 - 2)
    )
    # 树干
    for y in range(ground + 1, ground + 6):
        world.set_tile(tx, y, 18)   # 橡木
    # 树冠
    for dx in range(-2, 3):
        for dy in range(-1, 3):
            if abs(dx) + abs(dy) <= 3:
                wx = (tx + dx) % 80  # 循环包裹
                world.set_tile(wx, ground + 5 + dy, 22)  # 树叶
    # 偶尔用樱花树
    if tx % 3 == 0:
        for dx in range(-1, 2):
            for dy in range(0, 2):
                wx = (tx + dx) % 80
                world.set_tile(wx, ground + 4 + dy, 221)  # 樱花叶

# ============ 地表细节 ============
for x in range(0, 80):
    angle = x / 80.0 * 2 * math.pi
    ground = 14 + int(
        4 * math.sin(angle * 3) +
        3 * math.cos(angle * 5 + 1) +
        2 * math.sin(angle * 7 - 2)
    )
    # 花草
    if x % 5 == 0:
        world.set_tile(x, ground + 1, 50)   # 红花
    if x % 7 == 2:
        world.set_tile(x, ground + 1, 51)   # 黄花
    if x % 9 == 4:
        world.set_tile(x, ground + 1, 54)   # 枯灌木
    if x % 13 == 6:
        world.set_tile(x, ground + 1, 239)  # 贝壳（装饰）

# ============ 循环边界标记 ============
# x=0和x=79处用特殊方块标记（两侧实际是连通的）
for y in range(10, 35, 5):
    world.set_tile(0, y, 210)    # 星夜虚空标记
    world.set_tile(79, y, 210)

# ============ 地下洞穴 ============
# 洞穴1
for x in range(15, 30):
    for y in range(5, 12):
        if (x - 22)**2 / 49 + (y - 8)**2 / 9 <= 1.0:
            world.set_tile(x, y, 0)  # 挖空
# 洞穴水晶
for _ in range(20):
    cx, cy = random.randint(16, 29), random.randint(6, 11)
    if world.get_tile(cx, cy).type_id == 0:
        world.set_tile(cx, cy, random.choice([200, 201, 204, 206]))

# 洞穴2（跨循环边界！x=70~80→0~10）
for x in list(range(70, 80)) + list(range(0, 10)):
    for y in range(6, 13):
        if ((x - 75) % 80)**2 / 36 + (y - 9)**2 / 9 <= 1.0:
            world.set_tile(x, y, 0)

# ============ 湖泊（跨循环边界）============
for x in list(range(35, 80)) + list(range(0, 10)):
    angle = x / 80.0 * 2 * math.pi
    ground = 14 + int(4 * math.sin(angle * 3) + 3 * math.cos(angle * 5 + 1) + 2 * math.sin(angle * 7 - 2))
    if 37 <= x <= 79 or 0 <= x <= 7:
        for y in range(ground - 2, ground + 1):
            world.set_tile(x, y, 7)   # 水
# 湖底
for x in range(38, 79):
    world.set_tile(x, 12, 5)
for x in range(0, 7):
    world.set_tile(x, 12, 5)
# 湖心小岛
world.set_tile(75, 14, 17)
world.set_tile(76, 14, 17)
world.set_tile(3, 14, 17)
world.set_tile(4, 14, 17)
# 岛上树
for y in range(15, 19):
    world.set_tile(75, y, 18)
world.set_tile(75, 19, 22)

# ============ 传送门 ============
# 森林中央→跨边界湖区
world.set_tile(40, 21, 300)
if (40, 21) in world.grid:
    world.grid[(40, 21)].meta = {"tp_x": 75, "tp_y": 15}

# ============ 检查点与治愈 ============
world.set_tile(40, 21, 302)   # 中央检查点
world.set_tile(40, 22, 290)   # 治愈之泉
world.set_tile(20, 20, 302)
world.set_tile(60, 19, 302)
world.set_tile(75, 15, 302)   # 湖岛检查点

# 散布治愈
for cx in [12, 28, 35, 48, 55, 68, 5]:
    angle = cx / 80.0 * 2 * math.pi
    gy = 14 + int(4 * math.sin(angle * 3) + 3 * math.cos(angle * 5 + 1) + 2 * math.sin(angle * 7 - 2))
    if world.get_tile(cx, gy + 1).type_id == 0:
        world.set_tile(cx, gy + 1, 290)

# ============ 浮空云台 ============
for cx in [10, 30, 50, 70]:
    fill(cx % 80, 30, (cx + 2) % 80, 30, 33)  # 云
    fill((cx - 1) % 80, 31, (cx + 3) % 80, 31, 33)
    world.set_tile((cx + 1) % 80, 32, 297)  # 加速

world.end_bulk_load()
