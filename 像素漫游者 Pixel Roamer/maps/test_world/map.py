"""
test_world —— 探索测试地图（64x36）
"""
from world import World

MAP_ID = 1
world = World(map_id=MAP_ID, name="探索测试地图", w=64, h=36, gravity=-6.5, view_blocks_h=15, spawn_points=(4, 25))

# ---------- 底层基石（y=0~1） ----------
for x in range(64):
    for y in range(2):
        world.set_tile(x, y, 2)  # 石头

# ---------- 地表起伏（y=2） ----------
for x in range(64):
    if x < 10:
        world.set_tile(x, 2, 2)  # 左端石头
    elif x < 12:
        world.set_tile(x, 2, 3)  # 冰面
    elif x < 16:
        world.set_tile(x, 2, 2)
    elif x < 18:
        world.set_tile(x, 2, 4)  # 黏土
    elif x < 22:
        world.set_tile(x, 2, 2)
    elif x < 26:
        world.set_tile(x, 2, 5)  # 沙地
    elif x < 30:
        world.set_tile(x, 2, 2)
    elif x < 34:
        world.set_tile(x, 2, 3)  # 冰
    elif x < 38:
        world.set_tile(x, 2, 2)
    elif x < 42:
        world.set_tile(x, 2, 4)  # 黏土
    elif x < 46:
        world.set_tile(x, 2, 2)
    elif x < 50:
        world.set_tile(x, 2, 5)  # 沙
    else:
        world.set_tile(x, 2, 2)

# ---------- 地下岩洞（y=3~7）----------
# 左侧地下水池
for x in range(3, 10):
    for y in range(3, 7):
        world.set_tile(x, y, 7)  # 水
# 底部石头包围
for x in range(2, 11):
    world.set_tile(x, 2, 2)
    world.set_tile(x, 3, 2)
for y in range(4, 7):
    world.set_tile(2, y, 2)
    world.set_tile(10, y, 2)

# 右侧岩浆池
for x in range(50, 60):
    for y in range(3, 6):
        world.set_tile(x, y, 6)  # 岩浆
for x in range(49, 61):
    world.set_tile(x, 2, 2)
    world.set_tile(x, 3, 2)
for y in range(4, 6):
    world.set_tile(49, y, 2)
    world.set_tile(60, y, 2)

# 中部蜂蜜池（y=4）
for x in range(25, 35):
    for y in range(4, 6):
        world.set_tile(x, y, 8)  # 蜂蜜
for x in range(24, 36):
    world.set_tile(x, 3, 2)
for y in range(4, 6):
    world.set_tile(24, y, 2)
    world.set_tile(35, y, 2)

# ---------- 中层平台（y=8~10）----------
# 浮空石台
for x in range(5, 15):
    world.set_tile(x, 8, 2)
# 冰台
for x in range(16, 22):
    world.set_tile(x, 9, 3)
# 沙台
for x in range(40, 50):
    world.set_tile(x, 10, 5)

# ---------- 上层区域（y=12~16）----------
# 长石台
for x in range(20, 44):
    world.set_tile(x, 13, 2)
# 黏土台
for x in range(10, 16):
    world.set_tile(x, 15, 4)

# ---------- 高空藤蔓与梯子（y=17~25）----------
# 藤蔓区域
for y in range(17, 25):
    world.set_tile(28, y, 10)   # 藤蔓
    world.set_tile(30, y, 10)
# 梯子区域
for y in range(17, 22):
    world.set_tile(48, y, 9)    # 梯子
    world.set_tile(50, y, 9)

# ---------- 顶部空气墙测试（不可见屏障）----------
# 在左上角放置一些空气墙实体
for x in range(0, 4):
    for y in range(30, 34):
        world.set_tile(x, y, 13)  # 空气墙（白天）
# 右侧夜晚空气墙
for x in range(60, 64):
    for y in range(30, 34):
        world.set_tile(x, y, 14)  # 空气墙（夜晚）

# ---------- 特殊：角落黑暗空气（视觉测试）----------
for x in range(30, 34):
    for y in range(30, 34):
        world.set_tile(x, y, 12)  # 黑暗空气

# ---------- 设置玩家出生点（安全平台上方）----------
# 初始 spawn_points 已在 World 构造时设为 (4, 25)，但需确保该位置不是固体
# 将出生点下方设成平台
world.set_tile(3, 24, 2)
world.set_tile(4, 24, 2)
world.set_tile(5, 24, 2)
world.set_tile(4, 28, 56)  # 雕刻石砖标记
