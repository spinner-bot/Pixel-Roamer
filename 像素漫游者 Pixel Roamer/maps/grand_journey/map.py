"""
宏大旅程 — 手作探索地图
像作画一样逐步设计，每个区域精心布局。
"""
from __future__ import annotations
from world import World
import random, math

MAP_ID = 20
MAP_NAME = "宏大旅程"
MAP_NAME_EN = "Grand Journey"
W, H = 6000, 150
random.seed(2026)

_placed = set()
def p(w, x, y, bid):
    if 0 <= x < W and 0 <= y < H:
        w.set_tile(x, y, bid)
        _placed.add(bid)

def pick(pool):
    return pool[random.randint(0, len(pool)-1)]

# ============================================================
# 快捷绘制原语（像画家的笔刷）
# ============================================================
def rect(w, x, y, rw, rh, bid, hollow=False):
    """填充矩形。hollow=True 时仅绘制边框。"""
    for dx in range(rw):
        for dy in range(rh):
            if hollow and (0 < dx < rw-1 and 0 < dy < rh-1):
                continue
            p(w, x+dx, y+dy, bid)

def floor(w, x, y, width, bid, thick=2):
    """水平地板。"""
    for dx in range(width):
        for dy in range(thick):
            p(w, x+dx, y+dy, bid)

def wall_col(w, x, y, height, bid):
    """垂直墙柱。"""
    for dy in range(height):
        p(w, x, y+dy, bid)

def passage_h(w, x1, y, x2, h=3):
    """水平通道，微弯。"""
    for x in range(min(x1,x2), max(x1,x2)+1):
        off = int(math.sin(x*0.1)*1.2)
        for dy in range(h):
            p(w, x, y+off+dy, 0)

def passage_v(w, x, y1, y2, wd=2, ladder=True):
    """垂直通道，可选梯子。"""
    for y in range(min(y1,y2), max(y1,y2)+1):
        for dx in range(wd):
            p(w, x+dx, y, 0)
    if ladder:
        for y in range(min(y1,y2), max(y1,y2)+1):
            p(w, x+wd//2, y, pick([9,9,9,10,31]))

def room(w, cx, cy, rw, rh):
    """挖掘矩形房间。"""
    for x in range(cx-rw//2, cx+rw//2):
        for y in range(cy-rh//2, cy+rh//2):
            p(w, x, y, 0)

def platform(w, x, y, wd, bid):
    """悬浮平台。"""
    for dx in range(wd):
        for dy in range(2):
            p(w, x+dx, y+dy, bid)

def deco(w, x, y, bid):
    """单个装饰方块（仅当目标为空气时放置）。"""
    bt = w.get_block_type(x, y)
    if bt and bt.id == 0:
        p(w, x, y, bid)

def _noise_static(x, y):
    n = (x*374761393 + y*668265263) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 17)) % 10000) / 10000.0

# ============================================================
# 绘制画布
# ============================================================
def generate():
    w = World(map_id=MAP_ID, name=MAP_NAME, w=W, h=H,
              loop_x=False, loop_y=False, gravity=-0.7,
              spawn_points=(3000, 40), mode="explore",
              default_block_id=0, edge_behavior="solid",
              view_blocks_h=15.0)
    w.lives = 5; w.fill_color = (18, 14, 28)
    w.begin_bulk_load()

    # ---- 全图填充基岩 + 清空上半部 ----
    for x in range(W):
        for y in range(H):
            bt_id = 2 if y < 75 else 27  # 上半石头，下半黑曜石（更深）
            p(w, x, y, bt_id)
    for x in range(W):
        for y in range(20, 148):
            w.set_tile(x, y, 0)

    # 覆上一层薄土
    for x in range(W):
        for dy in range(3):
            p(w, x, 17+dy, 16)

    # ================================================================
    # 区域 1：出生点 — 天光废墟 (x=2800-3200, 地表)
    # ================================================================
    Z1 = 2800
    # 废墟大厅
    room(w, Z1+200, 36, 24, 14)
    floor(w, Z1+188, 29, 24, 17)
    # 断柱（交替高低）
    for i, dx in enumerate([188, 196, 204, 212]):
        wall_col(w, Z1+dx, 20, 12 if i%2==0 else 8, 56)
    # 中央祭坛（出生点标记）
    platform(w, Z1+198, 31, 8, 265)
    p(w, Z1+202, 33, 265)  # blessed_light
    # 墙上的火把
    p(w, Z1+188, 40, 43); p(w, Z1+211, 40, 43)
    p(w, Z1+188, 35, 43); p(w, Z1+211, 35, 43)
    # 向下通道入口（北墙）
    passage_v(w, Z1+200, 22, 29, 2, True)

    # ================================================================
    # 区域 2：地下第一层 — 老根洞穴 (x=2800-3200, y=45-70)
    # ================================================================
    Z2 = 2800
    # 天然洞穴感的不规则空间
    room(w, Z2+200, 57, 28, 12)
    # 悬垂土块天花板
    for dx in range(-8, 9, 4):
        for dy in range(2):
            p(w, Z2+200+dx, 63-dy, 16)
    # 中央水潭（不能直接穿越——需要绕路或游泳）
    rect(w, Z2+193, 55, 14, 3, 7)  # water
    # 绕潭的两条路：左路（窄道）和右路（主路）
    passage_h(w, Z2+186, 57, Z2+192, 2)   # 左窄道
    passage_h(w, Z2+207, 57, Z2+220, 3)   # 右主路
    # 分叉！右路尽头是一个小密室（需要破坏薄墙）
    rect(w, Z2+218, 55, 3, 4, 4, hollow=True)  # 薄黏土墙，可破坏
    p(w, Z2+219, 57, 314)  # 钻石（藏在墙后）
    # 左路通向竖井
    passage_v(w, Z2+190, 51, 68, 2, True)

    # ================================================================
    # 区域 3：中层 — 十字路大厅 (x=2800-3200, y=70-95)
    # ================================================================
    Z3 = 2800
    # 十字形大厅
    room(w, Z3+200, 82, 22, 16)
    floor(w, Z3+189, 74, 22, 34)  # 大理石地板
    # 四角支柱
    for (cx, cy) in [(Z3+191, 90), (Z3+209, 90), (Z3+191, 78), (Z3+209, 78)]:
        wall_col(w, cx, cy-3, 6, 81)
    # 天顶吊灯
    p(w, Z3+200, 88, 66); p(w, Z3+198, 89, 66); p(w, Z3+202, 89, 66)
    # 四条出口：东→继续前行 / 西→死路宝箱 / 南→回上层 / 北→深层竖井
    passage_h(w, Z3+189, 83, Z3+181, 3)   # 西（往密室）
    room(w, Z3+175, 83, 6, 5)
    p(w, Z3+175, 83, 312); p(w, Z3+175, 84, 311)  # 红宝石+银币
    passage_h(w, Z3+211, 83, Z3+225, 3)   # 东（主路向前）
    passage_v(w, Z3+205, 74, 82, 2, True) # 南（回上层）
    passage_v(w, Z3+195, 90, 100, 2, True)# 北（下深层）

    # ================================================================
    # 区域 4：深层 — 黑曜石裂隙 (x=2800-3200, y=100-130)
    # ================================================================
    Z4 = 2800
    # 窄高裂隙（只有2-3格宽，但有12格高）
    for dx in range(40):
        off_y = int(math.sin(dx*0.3)*3)
        for dy in range(10):
            p(w, Z4+180+dx, 100+off_y+dy, 0)
    # 裂隙底部熔岩池
    rect(w, Z4+195, 100, 10, 2, 6)  # lava
    # 跨熔岩的窄落脚点
    p(w, Z4+197, 103, 27); p(w, Z4+200, 103, 27); p(w, Z4+203, 103, 27)
    # 裂隙壁上突出的平台——需要精准跳跃
    platform(w, Z4+190, 110, 4, 68)
    platform(w, Z4+205, 115, 3, 68)
    platform(w, Z4+198, 118, 5, 68)
    # 裂隙尽头：传送门（通向远方）
    p(w, Z4+218, 120, 300)
    w.set_tile(Z4+218, 120, 300, {"tp_x": 4800.0, "tp_y": 60.0})
    p(w, Z4+218, 119, 76); p(w, Z4+218, 121, 76)

    # ================================================================
    # 区域 5：东行 — 砖石回廊 (x=3200-3700)
    # ================================================================
    Z5 = 3200
    # 规则排列的砖石走廊（人工建筑感）
    for cx in range(Z5, Z5+500, 30):
        # 柱廊
        wall_col(w, cx, 25, 60, 20)
        p(w, cx, 25, 43)   # 柱顶火把
        p(w, cx, 84, 43)   # 柱底火把
        # 柱间拱门（每2柱一个拱）
        if (cx - Z5) % 60 == 0:
            for dy in range(25, 84):
                if 25 <= dy < 84:
                    p(w, cx-2, dy, 56)
                    p(w, cx+2, dy, 56)
            # 拱顶
            for ax in range(-4, 5):
                arch_y = 25 + int(4 * math.sin((ax+4)/8 * math.pi))
                p(w, cx+ax, arch_y, 56)
    # 柱廊之间：通道、凹陷、侧室
    for i in range(15):
        sx = Z5 + 15 + i*30
        if i % 3 == 0:
            # 侧室
            room(w, sx, 55, 10, 8)
            floor(w, sx-5, 51, 10, 20)
            p(w, sx, 53, pick([40, 42, 29]))  # 工作台/箱子/书架
        elif i % 5 == 0:
            # 向下通道
            passage_v(w, sx, 35, 80, 2, i%2==0)
        else:
            # 壁龛装饰
            p(w, sx, 60, pick([50, 51, 52, 53, 54, 55]))  # 花/蘑菇/仙人掌
    # 廊道尽头分叉：左上（回廊上层）和直行（通往新区域）
    room(w, Z5+480, 50, 14, 10)
    passage_h(w, Z5+470, 55, Z5+455, 3)  # 左上支路
    passage_h(w, Z5+487, 50, Z5+520, 3)  # 直行

    # ================================================================
    # 区域 6：水没隧道 (x=3700-4200, y=40-90)
    # ================================================================
    Z6 = 3700
    # 大型洞穴，中部被水淹没
    room(w, Z6+200, 65, 50, 30)
    # 水面占据下半部
    rect(w, Z6+180, 52, 40, 4, 7)   # water
    # 水下隐藏通道（需要游泳穿过）
    for dx in range(10):
        for dy in range(3):
            p(w, Z6+210+dx, 50+dy, 0)
    # 水下密室入口
    p(w, Z6+215, 53, 293)  # 弹跳蘑菇标记
    room(w, Z6+220, 45, 8, 6)
    p(w, Z6+220, 45, 315)  # 翡翠
    p(w, Z6+219, 45, 316)  # 星币
    # 上层干燥通道（绕行路线）
    platform(w, Z6+190, 72, 40, 64)  # 海晶石桥
    # 天顶钟乳石
    for dx in range(-15, 16, 5):
        for dy in range(3):
            p(w, Z6+200+dx, 80-dy, 65)  # 暗海晶石
    # 右侧出口区域
    passage_h(w, Z6+225, 60, Z6+260, 3)
    passage_v(w, Z6+250, 50, 78, 2, True)  # 竖井回到上层

    # ================================================================
    # 区域 7：熔岩锻造厂 (x=4200-4700, y=60-120)
    # ================================================================
    Z7 = 4200
    # 下沉式工业结构——跨越多层的开放式"坑"
    for x in range(Z7, Z7+400):
        for y in range(30, 130):
            if (x-Z7-200)**2 / 40000 + (y-80)**2 / 2500 < 1:
                w.set_tile(x, y, 0)
    # 四周墙壁用下界砖
    for x in range(Z7+20, Z7+380):
        for dy in range(2):
            if not w.get_block_type(x, 125) or w.get_block_type(x, 125).id != 0:
                p(w, x, 128+dy, 63)
    # 中央熔岩池（巨大）
    rect(w, Z7+170, 60, 60, 5, 6)  # lava pool
    # 横跨熔岩的金属窄桥
    for bx in range(Z7+150, Z7+250):
        p(w, bx, 67, 255)  # brass_gearplate
    # 桥两端平台——左侧锻造台，右侧控制室
    room(w, Z7+160, 72, 12, 8)
    floor(w, Z7+154, 68, 12, 61)
    p(w, Z7+160, 70, 41)   # furnace
    p(w, Z7+157, 70, 40)   # crafting_table
    room(w, Z7+240, 72, 10, 7)
    p(w, Z7+240, 74, 300)  # portal_gate → 控制室传送门
    w.set_tile(Z7+240, 74, 300, {"tp_x": 5200.0, "tp_y": 55.0})
    # 下方密室（需要从侧面绕进去）
    room(w, Z7+200, 50, 16, 8)
    passage_h(w, Z7+180, 55, Z7+170, 2)  # 狭窄入口，容易错过
    p(w, Z7+200, 48, 291)  # regen_crystal
    p(w, Z7+195, 48, 314)  # diamond

    # ================================================================
    # 区域 8：冰封图书馆 (x=4700-5200, y=20-80)
    # ================================================================
    Z8 = 4700
    # 多层书架结构——规整但寒冷
    for level_y in [30, 48, 66]:
        floor(w, Z8+20, level_y, 360, 244 if level_y == 30 else 75)
    # 书架（隔墙）
    for bx in range(Z8+50, Z8+340, 25):
        wall_col(w, bx, 32, 14, 29)  # bookshelf as walls
        p(w, bx, 40, 82)  # ornate wood accent
    # 中层阅览室
    room(w, Z8+180, 57, 30, 10)
    # 桌子和灯
    for tx in range(Z8+168, Z8+192, 8):
        p(w, tx, 55, 40)  # crafting table
        p(w, tx, 54, 66)  # sea lantern above
    # 被冰封的密道（需要从下层绕）
    rect(w, Z8+300, 58, 6, 5, 75, hollow=True)  # 冰墙——可破坏
    room(w, Z8+305, 55, 8, 7)
    p(w, Z8+305, 57, 292)  # shield_generator
    p(w, Z8+308, 57, 315)  # emerald
    # 传送门——穿过冰墙后的奖励
    p(w, Z8+305, 53, 300)
    w.set_tile(Z8+305, 53, 300, {"tp_x": 5500.0, "tp_y": 90.0})

    # ================================================================
    # 区域 9：彩虹晶洞 (x=5200-5600, y=40-110)
    # ================================================================
    Z9 = 5200
    # 巨大的不规则晶洞
    for x in range(Z9, Z9+400):
        for y in range(30, 120):
            dx, dy = (x-Z9-200)/200, (y-75)/45
            if dx*dx + dy*dy < 1.2 and _noise_static(x, y) > 0.25:
                w.set_tile(x, y, 0)
    # 晶簇从墙壁生长
    for _ in range(200):
        cx = Z9 + random.randint(20, 380)
        cy = random.randint(35, 115)
        bt = w.get_block_type(cx, cy)
        bt2 = w.get_block_type(cx+1, cy) if cx+1 < W else None
        if (bt and bt.is_solid) != (bt2 and not bt2.is_solid if bt2 else False):
            if bt and bt.is_solid:
                p(w, cx+1, cy, pick([60, 76, 204, 205, 206, 207, 208, 209]))
    # 水晶桥——狭窄，需要平衡
    for bx in range(Z9+160, Z9+240):
        if bx % 5 < 3:
            p(w, bx, 70, pick([60, 76, 204]))  # 半透明落脚
    # 洞穴底部水潭
    rect(w, Z9+180, 38, 40, 3, 7)
    # 传送门——在洞穴最深处
    room(w, Z9+310, 50, 10, 8)
    p(w, Z9+310, 52, 300)
    w.set_tile(Z9+310, 52, 300, {"tp_x": 5850.0, "tp_y": 85.0})
    # 标记：发光紫水晶围绕
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx)+abs(dy) == 3:
                p(w, Z9+310+dx, 52+dy, 76)

    # ================================================================
    # 区域 10：终点圣所 (x=5600-6000, y=60-110)
    # ================================================================
    Z10 = 5600
    # 上层：暗影走廊——视觉屏障，制造"遥不可及"感
    for gx in range(Z10, Z10+380, 8):
        wall_col(w, gx, 20, 40, 264)  # cursed_vein 暗色柱
    # 走廊地面
    floor(w, Z10+20, 18, 360, 98)
    # 下层才是真正的入口
    passage_h(w, Z10+20, 85, Z10+380, 4)
    # 终点前厅（需要之前的传送门才能到达）
    room(w, Z10+340, 85, 18, 14)
    floor(w, Z10+331, 78, 18, 97)  # lodestone base
    # 墙壁用终点主题
    rect(w, Z10+331, 78, 18, 14, 97, hollow=True)
    # 终点信标——挑高台上
    platform(w, Z10+337, 83, 6, 68)
    p(w, Z10+340, 85, 303); p(w, Z10+340, 86, 303)  # end_beacon 双层
    # 光柱
    for dy in range(-5, 6):
        p(w, Z10+336, 85+dy, 66); p(w, Z10+344, 85+dy, 66)
    # 终点前最后的窄桥（考验）
    bridge_y = 82
    for bx in range(Z10+300, Z10+330):
        for ddy in range(4):
            w.set_tile(bx, bridge_y-ddy, 0)
        p(w, bx, bridge_y, 68 if bx%3==0 else 66)
    # 终点标记装饰
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
        p(w, Z10+340+dx, 85+dy, 96)

    # ================================================================
    # 连接各区域的过渡走廊
    # ================================================================
    # Z1→Z2→Z3→Z4 已通过竖井连接
    # Z4 传送门 → Z8
    # Z5→Z6 水平过渡
    passage_h(w, 3150, 55, 3750, 3)
    passage_v(w, 3450, 30, 65, 2, True)
    # Z6→Z7
    passage_h(w, 4150, 68, 4250, 3)
    # Z7→Z8: 上层走廊
    passage_h(w, 4600, 45, 4750, 3)
    passage_v(w, 4670, 40, 70, 2, True)
    # Z8→Z9: 中层走廊
    passage_h(w, 5050, 60, 5250, 3)
    passage_v(w, 5150, 45, 85, 2, True)
    # Z9→Z10: 直接水平
    passage_h(w, 5550, 85, 5650, 3)

    # ---- 关键传送门（放置目标处也设门，形成双向）----
    portal_pairs = [
        ((Z4+218, 120), (Z8+100, 60)),     # Z4↔Z8
        ((Z7+240, 74),  (Z9+100, 55)),     # Z7↔Z9
        ((Z8+305, 53),  (Z9+300, 90)),     # Z8↔Z9(深层)
        ((Z9+310, 52),  (Z10+340, 85)),    # Z9↔Z10(终点)
    ]
    for (x1, y1), (x2, y2) in portal_pairs:
        p(w, x1, y1, 300); p(w, x2, y2, 300)
        w.set_tile(x1, y1, 300, {"tp_x": float(x2), "tp_y": float(y2)})
        w.set_tile(x2, y2, 300, {"tp_x": float(x1), "tp_y": float(y1)})
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            p(w, x1+dx, y1+dy, pick([76,60,66,211]))
            p(w, x2+dx, y2+dy, pick([76,60,66,211]))
    # Z7 传送门 → Z8
    # Z8 传送门 → Z9
    # Z9 传送门 → Z10

    # ================================================================
    # 散布特殊方块（确保全部使用）
    # ================================================================
    from block_types_data import BLOCK_TYPES
    all_ids = set(BLOCK_TYPES.keys())
    needed = sorted(all_ids - {0,1,11,12,13,14,15} - _placed)
    for bid in needed:
        for _ in range(200):
            rx = random.randint(100, W-100)
            ry = random.randint(25, 125)
            bt = w.get_block_type(rx, ry)
            if bt and bt.id == 0:
                p(w, rx, ry, bid)
                break

    # 散布收集品到空位
    treasures = [310,311,312,313,314,315,316,317,318,319]
    for _ in range(500):
        tx = random.randint(50, W-50)
        ty = random.randint(22, 140)
        bt = w.get_block_type(tx, ty)
        if bt and bt.id == 0 and random.random() < 0.3:
            p(w, tx, ty, pick(treasures))

    # 检查点
    checkpoints = [(3000,36),(3000,80),(3200,50),(3450,55),(3750,65),
                   (4300,72),(4800,48),(5250,70),(5650,85)]
    for cx, cy in checkpoints:
        p(w, cx, cy, 302)

    # 散布梯子和藤蔓用于垂直移动
    for _ in range(400):
        lx = random.randint(50, W-50)
        ly = random.randint(25, 135)
        bt = w.get_block_type(lx, ly)
        tb = w.get_block_type(lx, ly+1)
        if (bt and bt.id == 0) and (tb and tb.is_solid if tb else False):
            p(w, lx, ly, pick([9,10,31]))

    w.end_bulk_load()
    return w


world = generate()
