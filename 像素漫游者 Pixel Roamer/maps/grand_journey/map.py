"""
宏大旅程 — 6000×150 探索地图
12层结构 · 50种主题 · 全部方块 · 寻找终点
"""
from __future__ import annotations
from world import World
import random

MAP_ID = 20
MAP_NAME = "宏大旅程"
MAP_NAME_EN = "Grand Journey"

W = 6000
H = 150
SECTION_W = W // 50  # = 120 每主题宽度
LAYER_H = H // 12    # = 12.5 → 12 层，交替使用 12/13

random.seed(2026)

# ===================== 所有方块分类 =====================
# 固体建筑方块（墙壁/地板）
SOLID_WALLS = [
    2, 3, 4, 16, 17, 20, 23, 24, 25, 26, 27, 34, 35, 56,
    60, 61, 62, 63, 64, 65, 67, 68, 74, 75, 76, 77, 78, 79, 80,
    81, 82, 83, 87, 88, 89, 91, 92, 93, 94, 95, 97, 100,
    203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214,
    215, 216, 217, 218, 219, 220, 222, 225, 226, 227, 229, 230,
    231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242,
    244, 245, 246, 247, 248, 254, 255, 256, 258, 263,
]

LIQUIDS = [6, 7, 8]  # 熔岩、水、蜂蜜
LIQUID_IDS = set(LIQUIDS)
AIR_VARIANTS = {0, 11, 12, 13, 14, 15}

# ===================== 50 主题定义 =====================
THEMES = [
    # (名称, 墙壁id, 地板id, 装饰ids列表, 特色id)
    ("远古石殿", 2, 56, [34, 81, 87], 227),         # 0
    ("寒冰峡谷", 3, 75, [244, 246, 248], 247),       # 1
    ("黏土洞穴", 4, 74, [230, 231, 35], 228),         # 2
    ("沙漠废墟", 5, 24, [230, 231, 55], 232),         # 3
    ("熔岩地核", 61, 6, [62, 27, 68], 205),           # 4
    ("深海宫殿", 64, 65, [66, 237, 238, 239], 240),   # 5
    ("蜂蜜巢穴", 71, 72, [8, 73, 18], 293),           # 6
    ("橡木森林", 18, 17, [22, 29, 40, 43], 263),      # 7
    ("砖石城堡", 20, 25, [56, 81, 42, 43], 234),      # 8
    ("下界要塞", 63, 61, [89, 62, 27, 90], 92),       # 9
    ("末地虚空", 62, 95, [76, 93, 66, 96], 301),      # 10
    ("水晶矿洞", 36, 37, [38, 39, 60, 76], 204),      # 11
    ("黑曜石塔", 27, 91, [68, 95, 97, 96], 301),      # 12
    ("云上幻境", 33, 13, [100, 211, 207], 208),       # 13
    ("大理石厅", 34, 83, [81, 87, 82, 86], 226),      # 14
    ("雪原松林", 23, 22, [18, 17, 75], 248),           # 15
    ("樱花庭园", 220, 221, [224, 225, 226], 263),      # 16
    ("禅意砂庭", 228, 225, [224, 229, 223], 229),      # 17
    ("维京石碑", 235, 236, [18, 244, 20], 232),        # 18
    ("希腊神殿", 232, 233, [34, 87, 234], 87),         # 19
    ("埃及陵墓", 230, 231, [24, 232, 55], 233),        # 20
    ("符文遗迹", 229, 56, [210, 211, 217], 267),       # 21
    ("珊瑚礁岛", 237, 238, [239, 240, 241, 242], 243), # 22
    ("深渊裂隙", 241, 242, [65, 66, 240], 210),        # 23
    ("火山之心", 61, 62, [6, 27, 67, 68], 205),        # 24
    ("翠竹林海", 223, 17, [224, 18, 29], 263),          # 25
    ("枫林古道", 222, 17, [23, 18, 55], 263),           # 26
    ("赛博工厂", 254, 255, [256, 249, 250, 251, 252], 257), # 27
    ("霓虹都市", 249, 250, [251, 253, 254], 252),      # 28
    ("星光银河", 211, 212, [213, 214, 215, 216], 218),  # 29
    ("彩虹幻境", 100, 207, [208, 209, 204, 205, 206], 219), # 30
    ("魔法森林", 17, 265, [263, 266, 267, 22], 267),    # 31
    ("龙鳞宝库", 260, 79, [78, 80, 38, 77], 316),       # 32
    ("凤凰巢穴", 259, 61, [260, 6, 27], 291),            # 33
    ("妖精花园", 261, 262, [50, 51, 265, 50], 261),      # 34
    ("暗影地牢", 264, 98, [99, 27, 32, 299], 300),      # 35
    ("诅咒矿道", 264, 36, [37, 38, 39, 98], 301),       # 36
    ("神圣殿堂", 263, 265, [266, 267, 234], 290),        # 37
    ("机械核心", 255, 256, [257, 258, 254], 257),        # 38
    ("泡泡水宫", 73, 7, [64, 66, 238], 293),             # 39  (注意: 73=bubble_column 不是固体)
    ("史莱姆实验室", 71, 72, [73, 8, 70, 299], 293),     # 40
    ("灵魂沙漠", 70, 24, [5, 69, 55], 69),               # 41
    ("菌光洞穴", 89, 90, [52, 53, 98, 99], 90),         # 42
    ("彩虹晶洞", 206, 207, [208, 209, 204, 205], 219),   # 43
    ("传送迷宫", 300, 301, [217, 210, 302], 300),         # 44
    ("宝库金库", 77, 78, [79, 80, 38, 39, 40], 314),     # 45
    ("图书馆厅", 29, 82, [40, 56, 34, 43], 29),          # 46
    ("冰雪宫殿", 244, 247, [248, 86, 75, 23], 248),      # 47
    ("紫珀回廊", 93, 94, [64, 65, 66, 76], 96),         # 48
    ("终点圣所", 97, 68, [60, 76, 66, 96, 303], 303),    # 49
]

# 所有必须使用的方块ID（去重）
ALL_BLOCK_IDS = set(range(330))
# 排除一些我们不会故意放置的ID（消耗态、空气变体等）
EXCLUDE_IDS = {0, 1} | AIR_VARIANTS - {0}  # 排除空气变体和边界
PLACEABLE_IDS = sorted(ALL_BLOCK_IDS - EXCLUDE_IDS)

# 记录哪些ID已放置
_placed_ids = set()


def _try_place(world, x, y, bid):
    """放置方块并记录已使用的ID。"""
    world.set_tile(x, y, bid)
    _placed_ids.add(bid)


def _random_block(pool):
    """从池中随机选一个方块。"""
    return pool[random.randint(0, len(pool) - 1)]


# ===================== 生成地图 =====================
def generate():
    world = World(
        map_id=MAP_ID,
        name=MAP_NAME,
        w=W, h=H,
        loop_x=False, loop_y=False,
        gravity=-0.7,
        spawn_points=(SECTION_W * 25 + 60, 10),  # 在中间主题的顶层
        mode="explore",
        default_block_id=0,
        edge_behavior="solid",
        view_blocks_h=15.0,
    )
    world.lives = 5
    world.music = ""
    world.fill_color = (20, 15, 30)

    # 批量加载以提升性能
    world.begin_bulk_load()

    # 为每层/每主题区域调用生成器
    # 每主题宽 120，每层高约 12-13

    for section in range(50):
        sx = section * SECTION_W  # 本段起始x
        theme_name, wall_id, floor_id, deco_ids, feature_id = THEMES[section]

        # 本主题的墙壁/地板池
        wall_pool = [wall_id, floor_id] + list(set(deco_ids[:3]))
        floor_pool = [floor_id, wall_id, floor_id]

        for layer in range(12):
            ly = layer * (H // 12)
            layer_h = 13 if layer < 6 else 12  # 上半高一点
            ly_end = min(ly + layer_h, H)

            # 地板行（该层的底部）
            floor_y = ly

            # 在该层的主题区域内填充
            for x in range(sx, sx + SECTION_W):
                for y in range(ly, ly_end):
                    # 在区域边缘放围墙
                    if x == sx or x == sx + SECTION_W - 1:
                        _try_place(world, x, y, wall_id)
                        continue
                    if y == floor_y:
                        _try_place(world, x, y, floor_id)
                        continue

                    # 天花板（每层顶部）
                    if y == ly_end - 1 and layer < 11:
                        _try_place(world, x, y, floor_id)
                        continue

                    # 内部：创建通道和填充
                    # 使用伪随机确保多样性
                    rng = random.randint(0, 99)
                    if rng < 15:
                        # 15% 空隙/通道
                        continue  # 保持空气
                    elif rng < 55:
                        # 40% 主墙壁
                        _try_place(world, x, y, wall_id)
                    elif rng < 70:
                        # 15% 副墙壁
                        _try_place(world, x, y, _random_block(wall_pool))
                    elif rng < 80:
                        # 10% 装饰
                        _try_place(world, x, y, _random_block(deco_ids))
                    elif rng < 88:
                        # 8% 特色方块
                        _try_place(world, x, y, feature_id)
                    else:
                        # 12% 随机填充
                        all_theme_blocks = [wall_id, floor_id] + list(deco_ids) + [feature_id]
                        _try_place(world, x, y, _random_block(all_theme_blocks))

            # 在该层添加水平通道（每4个主题段添加一个连接通道）
            if section % 4 == 0:
                passage_y = ly + layer_h // 2
                for px in range(sx - 3, sx + SECTION_W + 3):
                    if 0 <= px < W and 0 <= passage_y < H:
                        pass  # 不放置，让空气保持

        # 在每个主题段的特殊位置放置该主题的独特方块
        # 分散放置确保多样性
        for i in range(15):
            rx = sx + random.randint(5, SECTION_W - 6)
            ry = random.randint(2, H - 3)
            bid = _random_block(deco_ids + [feature_id])
            _try_place(world, rx, ry, bid)

    # ---- 放置所有未使用的方块 ----
    unused = sorted(set(PLACEABLE_IDS) - _placed_ids)
    for bid in unused:
        # 随机找个位置放置
        for attempt in range(200):
            rx = random.randint(2, W - 3)
            ry = random.randint(2, H - 3)
            bt = world.get_block_type(rx, ry)
            if bt is not None and bt.id == 0:
                _try_place(world, rx, ry, bid)
                break

    # ---- 放置终点 ----
    # 终点放在最后一个主题段（终点圣所）的深层
    end_x = (49 * SECTION_W) + SECTION_W // 2
    end_y = H - 20
    world.set_tile(end_x, end_y, 303)  # end_beacon
    # 在终点周围放置引导装饰
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            ex = end_x + dx
            ey = end_y + dy
            if 0 <= ex < W and 0 <= ey < H and not (dx == 0 and dy == 0):
                _try_place(world, ex, ey, _random_block([97, 60, 76, 66, 96, 303]))

    # ---- 确保无10×5同质区域 ----
    # 扫描并替换大面积同质区域
    for _pass in range(3):
        fixed = 0
        for check_x in range(2, W - 12, 10):
            for check_y in range(2, H - 7, 7):
                # 检查10×5区域
                first_id = None
                all_same = True
                for dx in range(10):
                    if not all_same:
                        break
                    for dy in range(5):
                        bt = world.get_block_type(check_x + dx, check_y + dy)
                        bid = bt.id if bt else 0
                        if first_id is None:
                            first_id = bid
                        elif bid != first_id:
                            all_same = False
                            break
                if all_same and first_id != 0:
                    # 在区域内混入变体
                    mid_x = check_x + 5
                    mid_y = check_y + 2
                    pool = SOLID_WALLS if first_id in SOLID_WALLS else list({first_id} | set(SOLID_WALLS[:20]))
                    for dx in range(10):
                        for dy in range(5):
                            if random.random() < 0.4:
                                repl = _random_block(pool)
                                _try_place(world, check_x + dx, check_y + dy, repl)
                                fixed += 1
        # 如果这轮没有修复任何东西，就结束
        # （但总是做至少2轮以确保）

    # ---- 确保可通行路径 ----
    # 在玩家出生点附近清理空间
    spawn_x = SECTION_W * 25 + 60
    for cx in range(spawn_x - 5, spawn_x + 6):
        for cy in range(2, 16):
            world.set_tile(cx, cy, 0)  # 清理出生区域

    # 清理终点周围的路径
    for cx in range(end_x - 3, end_x + 4):
        for cy in range(end_y - 8, end_y + 8):
            bt = world.get_block_type(cx, cy)
            if bt and bt.is_solid and bt.id not in {97, 68}:  # 保留终点装饰
                world.set_tile(cx, cy, 0)

    # 添加一些可攀爬的梯子/藤蔓用于垂直移动
    for section in range(50):
        if section % 5 == 0:
            ladder_x = section * SECTION_W + SECTION_W // 3
            for ly in range(5, H - 10):
                if world.get_block_type(ladder_x, ly) is None or world.get_block_type(ladder_x, ly).id == 0:
                    ladder_type = 9 if random.random() < 0.7 else 10  # 梯子或藤蔓
                    _try_place(world, ladder_x, ly, ladder_type)

    world.end_bulk_load()

    # ---- 配置终点检测 ----
    # 终点方块(303)带有 end_point 特效，由碰撞检测自动触发

    return world


world = generate()
