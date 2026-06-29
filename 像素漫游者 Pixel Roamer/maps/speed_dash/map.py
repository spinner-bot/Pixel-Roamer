"""
限时冲刺 —— 积分限时模式 (40×25)
120秒内尽可能多收集积分！弹射+加速优化路线
"""
from world import World

MAP_ID = 8
world = World(
    map_id=MAP_ID, name="限时冲刺",
    w=40, h=25,
    gravity=-5.8, view_blocks_h=20,
    spawn_points=(3, 4),
    mode="score_timed",
    default_block_id=11,
)
world.time_limit = 120.0    # 120秒
world.lives = 0              # 无限复活（但死亡损失时间）
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


# ============ 基岩 ============
fill(0, 0, 39, 0, 68)
fill(0, 1, 39, 1, 67)

# ============ 底道：加速直道 (y=2~4) ============
fill(1, 2, 38, 3, 254)     # 暗钢地板
fill(1, 4, 38, 4, 297)     # ★ 加速之路（全程）
# 散布积分
for x in range(2, 37, 3):
    world.set_tile(x, 5, 310)   # 金币

# ============ 中层：弹射跳跃区 (y=6~14) ============
# 左侧弹射柱
fill(2, 6, 2, 12, 254)
world.set_tile(2, 13, 294)     # 上弹板
world.set_tile(3, 12, 311)     # 银币

# 浮空平台链
fill(5, 9, 7, 9, 19)
world.set_tile(6, 10, 312)     # 红宝石（25分）
fill(10, 11, 12, 11, 33)
world.set_tile(11, 12, 313)    # 蓝宝石（25分）
fill(15, 8, 17, 8, 19)
world.set_tile(16, 9, 310)     # 金币
world.set_tile(16, 10, 310)
fill(20, 10, 22, 10, 33)
world.set_tile(21, 11, 314)    # 钻石水晶（50分！）
world.set_tile(21, 12, 316)    # 星币

# 绳索快速攀爬
for y in range(7, 13):
    world.set_tile(8, y, 31)
    world.set_tile(13, y, 31)
    world.set_tile(18, y, 31)

# 中层弹跳蘑菇（快速上升）
world.set_tile(8, 6, 293)
world.set_tile(18, 6, 293)

# ============ 高层：高分密集区 (y=16~22) ============
fill(3, 16, 37, 16, 19)
# 尖刺陷阱（高风险高回报）
world.set_tile(10, 16, 32)
world.set_tile(20, 16, 32)
world.set_tile(30, 16, 32)

# 跳跃增强辅助
fill(7, 17, 7, 17, 298)       # 跳增
fill(17, 17, 17, 17, 298)
fill(27, 17, 27, 17, 298)
fill(35, 17, 35, 17, 298)

# 高分宝藏
fill(6, 18, 8, 18, 19)
world.set_tile(7, 19, 314)     # 钻石水晶×2
world.set_tile(8, 19, 314)
fill(16, 18, 18, 18, 19)
world.set_tile(16, 19, 315)    # 翡翠×3
world.set_tile(17, 19, 315)
world.set_tile(18, 19, 315)
fill(26, 18, 28, 18, 19)
world.set_tile(26, 19, 317)    # 虚空宝珠×2（40分×2=80）
world.set_tile(28, 19, 317)
fill(34, 18, 36, 18, 19)
world.set_tile(34, 19, 312)    # 红宝石
world.set_tile(35, 19, 313)    # 蓝宝石
world.set_tile(36, 19, 316)    # 星币

# 顶层终极奖励
fill(15, 21, 25, 21, 33)
world.set_tile(19, 22, 314)    # 钻石水晶
world.set_tile(20, 22, 314)
world.set_tile(21, 22, 314)
world.set_tile(20, 23, 318)    # 日之徽记
world.set_tile(21, 23, 319)    # 月之徽记

# ============ 右侧快速下降通道 ============
for y in range(4, 21):
    world.set_tile(38, y, 31)   # 绳索（快速下滑）

# ============ 起始区 ============
world.set_tile(3, 5, 302)       # 检查点（唯一）
world.set_tile(2, 4, 290)       # 治愈
world.set_tile(4, 4, 297)       # 加速起步

# ============ 额外散布积分 ============
scattered = [
    (5,5,310),(9,5,310),(13,5,310),(17,5,310),(21,5,311),(25,5,311),
    (29,5,311),(33,5,310),(37,5,310),(6,7,311),(14,7,311),(22,7,311),
    (30,7,311),(3,10,312),(9,14,312),(15,13,313),(19,13,313),(25,13,313),
    (31,13,313),(5,15,316),(13,15,316),(23,15,316),(33,15,316),
    (11,20,318),(29,20,319),(8,22,316),(12,22,316),
]
for sx, sy, st in scattered:
    if 0 <= sx < 40 and 0 <= sy < 25:
        world.set_tile(sx, sy, st)

world.end_bulk_load()
