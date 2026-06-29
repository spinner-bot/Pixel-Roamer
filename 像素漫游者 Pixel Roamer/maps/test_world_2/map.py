"""
test_world_2 —— 主题大地图（650x80）
包含7个主题区域：森林、矿山/峡谷、沙漠、海洋、城镇、火山/下界、天空岛屿
"""
from world import World

MAP_ID = 2
world = World(map_id=MAP_ID, name="主题大地图", w=650, h=80,
              gravity=-6.5, view_blocks_h=20, spawn_points=(10, 55),
              default_block_id=11)  # 默认背景设为夜晚空气，凸显主题

world.begin_bulk_load()


def generate(world):
    """生成 650x80 的多主题区域地图"""
    # 辅助：填充矩形
    def fill(x0, y0, x1, y1, tile_id):
        for x in range(x0, x1+1):
            for y in range(y0, y1+1):
                world.set_tile(x, y, tile_id)

    # 辅助：生成山丘
    def hill(cx, cy, radius, tile_id):
        for x in range(max(0, cx-radius), min(world.width-1, cx+radius)+1):
            for y in range(max(0, cy-radius), min(world.height-1, cy+radius)+1):
                if (x-cx)**2 + (y-cy)**2 <= radius**2:
                    world.set_tile(x, y, tile_id)

    # 全图基岩底层
    for x in range(650):
        world.set_tile(x, 0, 68)   # 基岩
        world.set_tile(x, 1, 67)   # 玄武岩

    # ============ 区域1：森林 (0-100) ============
    # 地面：泥土+草地，有树，有湖泊
    for x in range(0, 100):
        for y in range(2, 8):
            world.set_tile(x, y, 16)  # 泥土
    for x in range(0, 100):
        if x % 10 < 7:
            world.set_tile(x, 9, 17)   # 草地表面
        else:
            world.set_tile(x, 9, 7)    # 小块水
    # 树
    for tx in [10, 20, 40, 55, 70, 85]:
        for y in range(10, 16):
            world.set_tile(tx, y, 18)   # 橡木原木
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                world.set_tile(tx+dx, 16+dy, 22)  # 树叶
    # 小湖
    fill(30, 8, 38, 9, 7)  # 水
    # 花丛
    world.set_tile(15, 10, 50)  # 红花
    world.set_tile(45, 10, 51)  # 黄花

    # ============ 区域2：矿山/峡谷 (100-200) ============
    # 山脉上升
    for x in range(100, 200):
        base_y = 8 + (x-100)//5 if x < 150 else 28 - (x-150)//5
        for y in range(2, base_y):
            world.set_tile(x, y, 2)   # 石头
        if x % 15 == 0:
            for y in range(base_y, base_y+3):
                world.set_tile(x, y, 25)  # 圆石表面
        else:
            world.set_tile(x, base_y, 25)
    # 矿洞
    fill(120, 10, 130, 15, 0)   # 空气洞穴
    # 矿石点缀
    world.set_tile(115, 9, 36)  # 煤矿
    world.set_tile(128, 10, 37) # 铁矿
    world.set_tile(135, 12, 38) # 金矿
    world.set_tile(145, 14, 39) # 钻石矿
    # 岩浆陷阱
    fill(180, 3, 190, 5, 6)    # 岩浆
    world.set_tile(185, 6, 32)  # 尖刺

    # ============ 区域3：沙漠 (200-300) ============
    for x in range(200, 300):
        for y in range(2, 12):
            world.set_tile(x, y, 5)   # 沙
    for x in range(200, 300):
        if x % 20 < 5:
            world.set_tile(x, 12, 5)  # 沙丘略高
        else:
            world.set_tile(x, 11, 5)
    # 仙人掌
    for cx in [210, 230, 260, 280]:
        for y in range(12, 16):
            world.set_tile(cx, y, 55)  # 仙人掌
    # 金字塔（简单造型）
    px, py = 240, 12
    for l in range(5):
        fill(px-l, py+l, px+l, py+l, 24)  # 砂岩
    # 内部陷阱
    fill(px-1, py+1, px+1, py+2, 0)  # 空
    world.set_tile(px, py+2, 28)     # 炸药
    # 藏宝箱
    world.set_tile(px, py+3, 42)     # 箱子

    # ============ 区域4：海洋 (300-400) ============
    # 海底地形
    for x in range(300, 400):
        for y in range(2, 6):
            world.set_tile(x, y, 2)   # 石头
    fill(300, 6, 400, 8, 5)         # 沙底
    # 海水
    fill(300, 9, 400, 18, 7)        # 水
    # 海床装饰
    for _ in range(50):
        rx = 300 + (hash(str(_)) % 100)
        ry = 7
        world.set_tile(rx, ry, 47)   # 白色羊毛(珊瑚)
        world.set_tile(rx+1, ry, 48) # 红色羊毛
    # 海底矿洞
    fill(340, 6, 350, 10, 0)        # 气室
    world.set_tile(345, 6, 37)      # 铁矿
    world.set_tile(345, 7, 64)      # 海晶石
    # 气泡柱
    fill(320, 14, 322, 18, 73)      # 气泡柱(向上推力)
    # 海面平台
    fill(360, 19, 370, 19, 17)      # 草平台(可站立)

    # ============ 区域5：城镇 (400-500) ============
    # 地面：石砖路
    for x in range(400, 500):
        for y in range(2, 6):
            world.set_tile(x, y, 2)   # 石头
    fill(400, 6, 500, 7, 20)        # 砖块路面
    # 房屋
    for hx in [410, 430, 460, 480]:
        fill(hx, 8, hx+6, 12, 19)    # 木板墙
        fill(hx+1, 8, hx+5, 12, 0)   # 内部空
        fill(hx+2, 8, hx+4, 8, 20)   # 砖块地板
        world.set_tile(hx+3, 9, 21)  # 玻璃窗
        world.set_tile(hx+3, 11, 21)
        # 门
        world.set_tile(hx+3, 7, 0)
    # 灯笼
    world.set_tile(408, 9, 30)
    world.set_tile(498, 9, 30)
    # 喷泉
    fill(445, 8, 455, 10, 24)       # 砂岩底
    fill(448, 11, 452, 12, 7)       # 水
    # 陷阱：暗藏尖刺
    world.set_tile(470, 7, 32)

    # ============ 区域6：火山/下界 (500-600) ============
    for x in range(500, 600):
        for y in range(2, 10):
            world.set_tile(x, y, 63)   # 下界砖
    # 岩浆湖
    fill(510, 10, 530, 12, 6)        # 熔岩
    fill(570, 10, 590, 12, 6)
    # 火山口
    for x in range(520, 580):
        for y in range(13, 16):
            world.set_tile(x, y, 61)  # 岩浆砖
    # 萤石点缀
    world.set_tile(525, 14, 69)
    world.set_tile(550, 14, 69)
    world.set_tile(575, 14, 69)
    # 黑曜石柱
    fill(540, 10, 542, 18, 27)       # 黑曜石
    fill(560, 10, 562, 16, 27)
    # 灵魂沙陷阱
    fill(555, 13, 565, 13, 70)       # 灵魂沙 (减速+伤害)

    # ============ 区域7：天空岛屿 (600-650) ============
    # 悬浮岛屿
    for cx in [610, 630, 645]:
        base_y = 40
        for x in range(cx-8, cx+9):
            for y in range(base_y-5, base_y+1):
                if (x-cx)**2/16 + (y-base_y)**2/4 <= 1.5:
                    world.set_tile(x, y, 2)  # 石头
        # 草地
        for x in range(cx-7, cx+8):
            world.set_tile(x, base_y+1, 17)
        # 树
        world.set_tile(cx, base_y+2, 18)
        for dx in [-1, 0, 1]:
            world.set_tile(cx+dx, base_y+3, 22)
        # 云朵装饰
        for dy in range(3):
            world.set_tile(cx+2, base_y+4+dy, 33)
            world.set_tile(cx-3, base_y+4+dy, 33)
    # 连接桥（树叶桥）
    for x in range(620, 630):
        world.set_tile(x, 47, 22)

    # ============ 全局细节：边界墙处理 ============
    # 边界已由 World 自动处理 (boundary id=1)

    # 设置玩家出生点附近安全区域
    fill(5, 52, 15, 56, 0)  # 清理出生区
    fill(5, 50, 15, 51, 2)  # 石头平台
    world.set_tile(10, 52, 43)  # 火把照明


# 调用生成
generate(world)

world.end_bulk_load()
