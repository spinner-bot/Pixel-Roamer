"""
无尽攀爬 —— 仅Y轴纵向循环世界 (20×120)
窄而高，掉落会从底部重新出现，永远爬不到顶
"""
from world import World

MAP_ID = 5
world = World(
    map_id=MAP_ID, name="无尽攀爬",
    w=20, h=120,
    gravity=-5.8,           # 略低重力，利于跳跃
    view_blocks_h=22,       # 看得远一些
    spawn_points=(10, 6),
    mode="adventure",
    default_block_id=11,    # 深色背景
    loop_x=False, loop_y=True,  # ★ 仅Y轴循环
)
world.begin_bulk_load()


def fill(x0, y0, x1, y1, tid):
    for x in range(max(0, x0), min(world.width - 1, x1) + 1):
        for y in range(max(0, y0), min(world.height - 1, y1) + 1):
            world.set_tile(x, y, tid)


def plat(y, x0, x1, tid=19, extra=None):
    """一层平台"""
    fill(x0, y, x1, y, tid)
    if extra:
        for x in range(x0, x1 + 1):
            world.set_tile(x, y + 1, extra)


# ============ 起始区 (y=2~8) ============
fill(0, 0, 19, 0, 68)         # 基岩
fill(0, 1, 19, 1, 67)
fill(6, 2, 14, 3, 17)         # 草地
world.set_tile(10, 4, 302)    # 检查点
world.set_tile(9, 4, 290)     # 治愈之泉
world.set_tile(11, 4, 290)
# 起始火把
world.set_tile(8, 4, 43)
world.set_tile(12, 4, 43)
# 两侧墙
for y in range(2, 120):
    world.set_tile(0, y, 254)  # 左墙
    world.set_tile(19, y, 254) # 右墙

# ============ 攀爬层 y=8~30（入门）============
# 第1跳
plat(10, 4, 7, 19)
plat(12, 13, 16, 19)
world.set_tile(15, 13, 298)   # 跳跃增强

# 第2跳
plat(16, 3, 6, 19)
plat(18, 10, 14, 19)
# 绳索辅助
for y in range(10, 18):
    world.set_tile(5, y, 31)

# 第3跳
plat(23, 13, 17, 19)
plat(26, 2, 6, 19)
for y in range(24, 28):
    world.set_tile(9, y, 10)   # 藤蔓
world.set_tile(10, 27, 302)   # 检查点
world.set_tile(10, 26, 290)

# ============ 技巧区 y=30~55（弹射+藤蔓）============
# 弹射板层
plat(33, 3, 5, 19)
world.set_tile(4, 34, 294)     # 上弹板
plat(38, 13, 18, 19)

# 藤蔓墙
for y in range(33, 48):
    world.set_tile(9, y, 10)
    world.set_tile(10, y, 10)
# 加速跑道
fill(7, 43, 12, 43, 297)       # 加速之路

# 弹跳蘑菇
plat(48, 3, 6, 19)
world.set_tile(4, 49, 293)     # 弹跳蘑菇
plat(52, 14, 18, 19)
world.set_tile(16, 53, 298)    # 跳跃增强

# 检查点
world.set_tile(10, 49, 302)
world.set_tile(10, 48, 291)    # 再生水晶

# ============ 难度区 y=55~80（尖刺+窄平台）============
# 窄平台
plat(58, 3, 5, 19)
plat(60, 15, 18, 19)
# 尖刺陷阱
world.set_tile(4, 59, 32)      # 尖刺！
world.set_tile(16, 61, 32)

# 需要精确跳跃
plat(65, 2, 4, 19)
plat(67, 8, 11, 19)
plat(70, 16, 18, 19)

# 绳索安全网
for y in range(64, 76):
    world.set_tile(6, y, 31)

plat(75, 5, 9, 19)
world.set_tile(7, 76, 293)     # 弹跳蘑菇
plat(78, 11, 15, 19)
# 护盾
world.set_tile(13, 79, 292)
world.set_tile(10, 76, 302)    # 检查点

# ============ 极难区 y=80~105（减速+弹射Combo）============
plat(83, 6, 10, 19)
fill(6, 84, 10, 84, 299)       # 减速蛛网
world.set_tile(2, 83, 294)     # 左弹板

plat(88, 15, 18, 19)
plat(92, 3, 5, 33)         # 云平台
plat(95, 8, 13, 19)

# 弹射连跳
fill(3, 97, 3, 97, 298)        # 跳跃增强
plat(100, 12, 17, 19)
world.set_tile(14, 101, 294)
plat(105, 2, 5, 19)

world.set_tile(10, 101, 302)   # 检查点
world.set_tile(9, 100, 291)

# ============ 极限区 y=105~119 ============
# 窄到极致的平台
plat(108, 2, 3, 19)
plat(110, 16, 18, 19)
plat(113, 5, 8, 19)
plat(115, 11, 14, 19)

# 诅咒地板（伤害）
fill(10, 117, 15, 117, 264)

# 最终层——大量奖励
fill(6, 119, 14, 119, 255)     # 黄铜齿轮板
world.set_tile(9, 119, 79)     # 金块
world.set_tile(10, 119, 80)    # 钻石块
world.set_tile(11, 119, 78)    # 铁块
world.set_tile(10, 118, 302)   # 检查点
world.set_tile(10, 117, 292)   # 护盾

# ============ 循环提示标记 ============
# 顶部(y=119)→底部(y=0)循环标记
world.set_tile(1, 119, 212)    # 太阳光辉
world.set_tile(18, 0, 212)

# 额外治愈点分布
for y in range(10, 115, 20):
    world.set_tile(10, y + 2, 290)

world.end_bulk_load()
