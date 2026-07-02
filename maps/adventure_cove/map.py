"""
冒险湾 Adventure Cove — 10分钟探索地图 (ID 21)
覆盖：游泳/攀爬/上岸/弹射/传送/buff/收集/滑冰/磁力/风
"""
from __future__ import annotations
from world import World
import random

MAP_ID = 21
MAP_NAME = "冒险湾"
MAP_NAME_EN = "Adventure Cove"
W, H = 420, 100
random.seed(42)

_placed = set()
def p(w, x, y, bid):
    if 0 <= x < W and 0 <= y < H:
        w.set_tile(x, y, bid)
        _placed.add(bid)

def pick(pool):
    return pool[random.randint(0, len(pool)-1)]

# =========== 笔刷 ===========
def rect(w, x, y, rw, rh, bid, hollow=False):
    for dx in range(rw):
        for dy in range(rh):
            if hollow and 0 < dx < rw-1 and 0 < dy < rh-1: continue
            p(w, x+dx, y+dy, bid)

def floor(w, x, y, wd, bid, thick=2):
    for dx in range(wd):
        for dy in range(thick):
            p(w, x+dx, y+dy, bid)

def wall(w, x, y, h, bid):
    for dy in range(h):
        p(w, x, y+dy, bid)

def platform(w, x, y, wd, bid):
    for dx in range(wd):
        p(w, x+dx, y, bid)
        p(w, x+dx, y+1, bid)

def tunnel_h(w, x1, y, x2, h=3):
    for x in range(min(x1,x2), max(x1,x2)+1):
        for dy in range(h):
            p(w, x, y+dy, 0)

def tunnel_v(w, x, y1, y2, wd=2):
    for y in range(min(y1,y2), max(y1,y2)+1):
        for dx in range(wd):
            p(w, x+dx, y, 0)

def ladder_col(w, x, y, h):
    for dy in range(h):
        p(w, x, y+dy, 9)

def vine_col(w, x, y, h):
    for dy in range(h):
        p(w, x, y+dy, 10)

def room(w, cx, cy, rw, rh):
    for x in range(cx-rw//2, cx+rw//2):
        for y in range(cy-rh//2, cy+rh//2):
            p(w, x, y, 0)

def pillar(w, x, y, h, bid):
    for dy in range(h):
        p(w, x, y+dy, bid)

# =========== 主生成 ===========
def generate():
    w = World(map_id=MAP_ID, name=MAP_NAME, w=W, h=H,
              loop_x=False, loop_y=False, gravity=-6.5,
              spawn_points=(30, 72), mode="explore",
              default_block_id=0, edge_behavior="solid",
              view_blocks_h=14.0)
    w.lives = 3
    w.fill_color = (12, 10, 22)
    w.begin_bulk_load()

    # ---- 全图基岩 ----
    for x in range(W):
        for y in range(H):
            p(w, x, y, 27 if y < 30 else 2)

    # ---- 清空可玩区域 ----
    for x in range(W):
        for y in range(10, 98):
            w.set_tile(x, y, 0)

    # ================================================================
    # 区域 1：晨曦海滩 (x=0-55) — 出生点·游泳·上岸
    # ================================================================
    # 阶梯海滩
    for x in range(0, 15):
        for dy in range(3):
            p(w, x, 60+dy, 24)
    for x in range(15, 30):
        for dy in range(2):
            p(w, x, 64+dy, 24)
    floor(w, 0, 66, 55, 17)     # 草地
    floor(w, 5, 68, 4, 19)      # 码头
    p(w, 6, 69, 43)             # 火把
    p(w, 8, 70, 42)             # 宝箱

    # 浅水池（游泳+上岸教学）
    rect(w, 30, 60, 14, 5, 7)   # 水
    floor(w, 30, 65, 14, 24)    # 砂岩岸（上岸点）
    floor(w, 30, 66, 14, 17)
    p(w, 35, 63, 314)           # 水中钻石
    p(w, 42, 63, 314)

    # 深水竖井 → 地下湖
    rect(w, 40, 52, 4, 8, 7)

    # 右侧崖壁 + 梯子
    wall(w, 50, 61, 8, 2)
    ladder_col(w, 51, 61, 8)

    # ================================================================
    # 区域 2：地下湖洞 (x=30-80, y=35-55) — 游泳·攀爬
    # ================================================================
    room(w, 58, 48, 26, 12)
    rect(w, 50, 42, 14, 5, 7)   # 地下湖
    # 湖心岛
    platform(w, 54, 49, 5, 2)
    p(w, 56, 51, 43)
    p(w, 55, 51, 314)
    # 藤蔓逃生
    vine_col(w, 66, 48, 10)
    platform(w, 63, 60, 8, 17)
    p(w, 65, 62, 42)
    p(w, 66, 62, 314)
    # 窄道
    tunnel_h(w, 70, 46, 78, 2)
    p(w, 75, 47, 315)

    # ================================================================
    # 区域 3：熔岩裂谷 (x=85-155, y=50-82) — 危险跳跃·弹射
    # ================================================================
    # 裂谷开口
    rect(w, 88, 57, 62, 20, 0)
    floor(w, 88, 55, 62, 16)    # 顶

    # 熔岩池（伤害45/s）
    rect(w, 98, 57, 28, 3, 6)

    # 安全岛
    platform(w, 105, 62, 3, 2)
    p(w, 106, 63, 43)
    platform(w, 123, 62, 3, 2)
    p(w, 124, 63, 43)

    # 弹射台（catapult）— 飞跃熔岩
    p(w, 92, 59, 433)           # gravity_flip_stone (catapult)
    p(w, 93, 59, 433)
    p(w, 130, 59, 433)
    p(w, 131, 59, 433)

    # 二段跳buff块 → 隐藏收集路线
    p(w, 90, 60, 415)           # bouncy_mushroom (轻身buff 4, jump height)
    p(w, 112, 70, 315)          # 高空金币
    p(w, 113, 70, 315)
    p(w, 114, 70, 315)

    # 对岸
    rect(w, 134, 58, 10, 3, 24)
    rect(w, 134, 61, 10, 2, 17)
    ladder_col(w, 145, 58, 9)
    floor(w, 140, 67, 15, 17)   # 上层平台

    # ================================================================
    # 区域 4：弹射风谷 (x=160-220, y=35-85) — 弹射·风力
    # ================================================================
    floor(w, 160, 42, 60, 2)

    # 弹射阵
    for bx in [165, 180, 195, 210]:
        p(w, bx, 44, 433)       # catapult
        p(w, bx+1, 44, 433)

    # 风助推（wind）
    for wx in [170, 185, 200, 215]:
        p(w, wx, 52, 387)       # wind_vortex
        p(w, wx, 53, 387)

    # 落点平台
    platform(w, 173, 68, 5, 34)
    platform(w, 188, 72, 5, 34)
    platform(w, 203, 66, 5, 34)

    # 收集品
    for bx in [175, 190, 205]:
        p(w, bx, 62, 315)
        p(w, bx, 63, 315)

    # 最高宝藏
    platform(w, 195, 84, 4, 17)
    p(w, 196, 85, 314)
    p(w, 197, 85, 314)

    # ================================================================
    # 区域 5：冰霜洞穴 (x=225-285, y=45-75) — 滑冰·寒冷
    # ================================================================
    room(w, 255, 60, 28, 14)
    # 冰面（低摩擦 surface_f=1.05）
    rect(w, 241, 53, 28, 2, 3)

    # 寒冷buff（触碰得 chilled buff 51）
    p(w, 246, 55, 373)          # frozen_ground
    p(w, 260, 55, 373)

    # 滑腻buff
    p(w, 253, 57, 383)          # slick_ice (滑腻 buff 42)

    # 冰上收集
    for ix in range(244, 266, 4):
        p(w, ix, 56, 315)

    # 冰柱障碍
    for ix in [245, 251, 257, 263]:
        pillar(w, ix, 58, 5, 23)

    # 黏着壁（爬墙）
    p(w, 270, 59, 382)          # sticky_floor (黏着 buff 43)
    vine_col(w, 278, 58, 14)
    p(w, 278, 72, 314)

    # ================================================================
    # 区域 6：磁力矿洞 (x=290-345, y=50-80) — 磁力·收集
    # ================================================================
    room(w, 317, 65, 26, 14)

    # 磁石（magnetic special）
    for mx in [302, 312, 322, 332]:
        p(w, mx, 60, 386)       # magnetic_lode
        p(w, mx, 61, 386)
        p(w, mx, 71, 386)
        p(w, mx, 72, 386)

    # 收集品（在磁石间）
    for mx in [306, 316, 326, 336]:
        p(w, mx, 65, 315)
        p(w, mx, 68, 315)

    # 磁化buff（增强磁力影响）
    p(w, 317, 66, 403)          # magnetized_vein

    # 稳足buff（抵抗外力 → surefooted buff 41）
    p(w, 298, 63, 428)          # crystal_cavern_wall (buffs 50+41)

    # 出口梯子
    ladder_col(w, 340, 60, 12)

    # ================================================================
    # 区域 7：天空神殿 (x=348-418, y=65-98) — 终点挑战
    # ================================================================
    floor(w, 348, 72, 70, 34)
    rect(w, 352, 74, 62, 3, 34)

    # 柱廊
    for cx in [358, 373, 388, 403]:
        pillar(w, cx, 74, 14, 34)

    # 风助推 → 最高收集
    p(w, 355, 77, 387)          # wind_vortex
    p(w, 409, 77, 387)

    # 轻羽buff（低重力 → feather buff 13）
    p(w, 370, 78, 389)          # anti_grav_ore

    # 迅捷buff（加速 → swiftness buff 3）
    p(w, 375, 78, 420)          # swift_current

    # 中央圣坛
    platform(w, 380, 82, 8, 265)
    p(w, 383, 84, 42)
    p(w, 384, 84, 42)

    # 最难收集
    p(w, 390, 96, 314)
    p(w, 391, 96, 314)

    # 终点传送
    p(w, 415, 78, 425)          # shadow_slip_gate (teleport)
    p(w, 415, 79, 425)
    p(w, 417, 80, 265)          # 终点光柱

    # ================================================================
    # 全局点缀
    # ================================================================
    # 沿途火把
    for tx in [20, 55, 95, 145, 200, 235, 295, 350, 415]:
        bt = w.get_block_type(tx, 70)
        if bt and bt.id == 0:
            p(w, tx, 70, 43)

    # 散落金币
    for _ in range(50):
        gx = random.randint(5, 412)
        gy = random.randint(30, 92)
        bt = w.get_block_type(gx, gy)
        if bt and bt.id == 0:
            p(w, gx, gy, 315)

    # 隐藏钻石
    hidden = [(20,64), (95,61), (175,56), (238,59), (308,65), (395,94)]
    for hx, hy in hidden:
        p(w, hx, hy, 314)

    w.end_bulk_load()
    w.lives = 3
    return w


world = generate()
