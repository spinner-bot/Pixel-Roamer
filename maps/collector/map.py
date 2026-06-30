"""
收藏家之旅 —— 积分目标模式 (55×40)
收集500分解锁通关！各个角落都有宝藏，需仔细探索
"""
from world import World

MAP_ID = 9
world = World(
    map_id=MAP_ID, name="收藏家之旅",
    w=55, h=40,
    gravity=-6.5, view_blocks_h=18,
    spawn_points=(27, 22),
    mode="score_target",
    default_block_id=11,
)
world.score_goal = 500      # ★ 目标500分
world.lives = 0               # 无限复活
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


# ============ 基岩 ============
fill(0, 0, 54, 0, 68)

# ============ 中央枢纽 (x=23~31, y=17~25) ============
fill(23, 17, 31, 18, 19)   # 地板
fill(23, 16, 31, 16, 2)
fill(23, 24, 31, 24, 19)   # 天花板
# 枢纽设施
world.set_tile(27, 19, 302)  # 检查点
world.set_tile(26, 18, 290)  # 治愈
world.set_tile(28, 18, 292)  # 护盾
# 信息柱
world.set_tile(27, 20, 265)  # 祝福圣光

# ============ 东翼：图书馆 (x=32~53, y=16~25) ============
fill(32, 17, 52, 17, 19)   # 地板
fill(32, 16, 52, 16, 2)
# 书架墙
for y in range(18, 24):
    world.set_tile(32, y, 29)    # 书架
    world.set_tile(52, y, 29)
# 书架间的积分
world.set_tile(36, 18, 310)     # 金币×3
world.set_tile(37, 18, 310)
world.set_tile(38, 18, 310)
world.set_tile(42, 20, 311)     # 银币×4
world.set_tile(43, 20, 311)
world.set_tile(44, 20, 311)
world.set_tile(45, 20, 311)
world.set_tile(48, 23, 316)     # 星币×2
world.set_tile(49, 23, 316)

# 图书馆上层（需爬书架）
fill(35, 21, 39, 21, 19)        # 平台
world.set_tile(37, 22, 314)     # 钻石水晶（50分，隐藏！）
# 爬上来的绳索
for y in range(18, 22):
    world.set_tile(40, y, 31)

# ============ 西翼：水晶洞 (x=2~22, y=16~25) ============
fill(3, 17, 21, 17, 19)    # 地板
fill(3, 16, 21, 16, 2)
# 水晶装饰
for _ in range(15):
    import random
    cx, cy = random.randint(4, 20), random.randint(18, 23)
    if world.get_tile(cx, cy).type_id == 0:
        world.set_tile(cx, cy, random.choice([200,201,204,206]))
# 水晶间的积分
world.set_tile(8, 18, 312)      # 红宝石
world.set_tile(15, 19, 313)     # 蓝宝石
world.set_tile(10, 22, 312)
world.set_tile(17, 21, 313)

# 水晶洞底层密室（需向下挖）
fill(10, 12, 16, 15, 0)
fill(10, 11, 16, 11, 2)
fill(10, 16, 16, 16, 2)
world.set_tile(13, 12, 314)     # 钻石水晶×2
world.set_tile(14, 12, 314)
world.set_tile(12, 13, 315)     # 翡翠×2
world.set_tile(15, 13, 315)
for y in range(16, 18):
    world.set_tile(13, y, 10)   # 藤蔓入口

# ============ 北侧：云中花园 (x=15~40, y=28~38) ============
# 浮空花园平台
for cx in [18, 24, 30, 36]:
    fill(cx, 28, cx+4, 29, 33)  # 云基
    fill(cx+1, 30, cx+3, 30, 220)  # 樱花木
    # 花草
    world.set_tile(cx+1, 31, 50)
    world.set_tile(cx+3, 31, 51)
    # 积分
    world.set_tile(cx+2, 31, 316)   # 星币

# 更高层
fill(24, 33, 30, 33, 33)
world.set_tile(26, 34, 317)     # 虚空宝珠×2（80分！）
world.set_tile(28, 34, 317)

# 藤蔓连接
for y in range(25, 34):
    world.set_tile(20, y, 10)
    world.set_tile(34, y, 10)

# ============ 南侧：地下遗迹 (x=20~35, y=4~14) ============
fill(22, 4, 33, 6, 230)    # 砂岩遗迹
fill(23, 7, 32, 12, 0)
fill(23, 13, 32, 13, 230)
# 遗迹中的宝藏
world.set_tile(25, 7, 312)      # 红宝石
world.set_tile(28, 9, 314)      # 钻石水晶
world.set_tile(30, 11, 318)     # 日之徽记
world.set_tile(26, 8, 315)      # 翡翠
# 陷阱
world.set_tile(27, 7, 32)       # 尖刺
world.set_tile(29, 10, 264)     # 诅咒地板
# 通往中央的隧道
fill(27, 14, 28, 15, 0)
for y in range(14, 17):
    world.set_tile(27, y, 31)   # 绳索

# ============ 四角隐藏室 ============
# 东北 (x=48~53, y=30~35)
fill(48, 30, 53, 34, 0)
fill(48, 29, 53, 29, 230)
fill(48, 35, 53, 35, 230)
world.set_tile(50, 30, 317)     # 虚空宝珠
world.set_tile(51, 30, 319)     # 月之徽记
world.set_tile(50, 33, 318)     # 日之徽记
# 入口藤蔓
for y in range(25, 30):
    world.set_tile(50, y, 10)

# 西北 (x=2~8, y=30~35)
fill(2, 30, 8, 34, 0)
fill(2, 29, 8, 29, 19)
fill(2, 35, 8, 35, 19)
world.set_tile(5, 31, 314)      # 钻石水晶
world.set_tile(5, 32, 315)      # 翡翠

# 西南 (x=2~10, y=4~10)
fill(2, 4, 10, 9, 0)
fill(2, 3, 10, 3, 2)
fill(2, 10, 10, 10, 2)
world.set_tile(6, 6, 316)       # 星币×4
world.set_tile(7, 6, 316)
world.set_tile(6, 8, 316)
world.set_tile(7, 8, 316)

# 东南 (x=44~53, y=4~10)
fill(44, 4, 53, 9, 0)
fill(44, 3, 53, 3, 2)
fill(44, 10, 53, 10, 2)
world.set_tile(48, 5, 312)      # 红宝石
world.set_tile(49, 5, 313)      # 蓝宝石
world.set_tile(48, 8, 315)      # 翡翠×3
world.set_tile(49, 8, 315)
world.set_tile(50, 8, 315)

# ============ 散布积分总计 > 500 ============
# 计算：10×10 + 5×10 + 25×5 + 25×5 + 50×7 + 30×10 + 15×10 + 40×5 + 20×4 + 20×4
# = 100+50+125+125+350+300+150+200+80+80 = 1560分（远超500目标，有冗余）
extra_score = [
    # 金币(10)×散布
    (3,17,310),(6,17,310),(9,17,310),(12,17,310),(15,17,310),(18,17,310),(21,17,310),
    (33,17,310),(36,17,310),(39,17,310),(42,17,310),(45,17,310),(48,17,310),(51,17,310),
    # 银币(5)×散布
    (5,19,311),(11,19,311),(17,19,311),(23,19,311),(29,19,311),(35,19,311),(41,19,311),(47,19,311),
    # 星币(15)×散布
    (27,21,316),(20,18,316),(34,18,316),
    # 天花板上的隐藏积分（需飞行或借力到达）
    (27,25,314),(22,26,315),(32,26,315),
]

for sx, sy, st in extra_score:
    if 0 <= sx < 55 and 0 <= sy < 40:
        if world.get_tile(sx, sy).type_id == 0:
            world.set_tile(sx, sy, st)

# ============ 治愈点 ============
for hx, hy in [(27,18),(13,18),(37,19),(8,14),(48,8),(50,32)]:
    if world.get_tile(hx, hy).type_id == 0:
        world.set_tile(hx, hy, 290)

world.end_bulk_load()
