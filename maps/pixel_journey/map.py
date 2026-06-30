"""
像素启程 —— 大型探索冒险地图 (480×280 = 134,400)
模式：有限 (finite) | 6大主题区域 | 多层结构 | 传送网络
"""
from world import World

MAP_ID = 3

# ===================== World 构建 =====================
world = World(
    map_id=MAP_ID, name="像素启程",
    w=480, h=280,
    gravity=-6.2,          # 略低重力，利于探索与跑酷
    view_blocks_h=18,       # 适中的视野范围
    spawn_points=(15, 52),  # 起始森林出生点
    mode="adventure",
    default_block_id=0,     # 默认空气
    edge_behavior="solid",
)
world.void_limit = 25       # 虚空边界距离

world.begin_bulk_load()

# ===================== 快捷填充函数 =====================
def fill(x0, y0, x1, y1, tid):
    """矩形填充 [x0,x1]×[y0,y1]"""
    for x in range(max(0,x0), min(world.width-1, x1)+1):
        for y in range(max(0,y0), min(world.height-1, y1)+1):
            world.set_tile(x, y, tid)

def line(x0, y0, x1, y1, tid, thick=1):
    """Bresenham粗线"""
    dx, dy = abs(x1-x0), abs(y1-y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cx, cy = x0, y0
    while True:
        for tx in range(-thick//2, (thick+1)//2):
            for ty in range(-thick//2, (thick+1)//2):
                world.set_tile(cx+tx, cy+ty, tid)
        if cx == x1 and cy == y1: break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy

def circle(cx, cy, r, tid, fill_tid=None):
    """圆形/圆环"""
    for x in range(max(0,int(cx-r)), min(world.width-1, int(cx+r))+1):
        for y in range(max(0,int(cy-r)), min(world.height-1, int(cy+r))+1):
            d2 = (x-cx)**2 + (y-cy)**2
            if d2 <= r**2:
                if fill_tid is None or d2 > (r-1.0)**2:
                    world.set_tile(x, y, fill_tid if fill_tid else tid)
                elif fill_tid:
                    world.set_tile(x, y, fill_tid)

def hill(cx, cy, w, h, tid, top_tid=None):
    """椭圆山丘"""
    for x in range(max(0,int(cx-w)), min(world.width-1, int(cx+w))+1):
        for y in range(max(0,int(cy-h)), min(world.height-1, int(cy+h))+1):
            if ((x-cx)/w)**2 + ((y-cy)/h)**2 <= 1.0:
                world.set_tile(x, y, top_tid if top_tid and y >= cy else tid)

def platform(x0, y, x1, tid, support_tid=None, support_every=4):
    """浮空平台+支撑柱"""
    for x in range(x0, x1+1):
        world.set_tile(x, y, tid)
    if support_tid:
        for x in range(x0, x1+1, support_every):
            for sy in range(0, y):
                if world.get_tile(x, sy).type_id == 0:
                    world.set_tile(x, sy, support_tid)

def stairs(x0, y0, x1, y1, tid, w=3):
    """阶梯"""
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0: return
    for i in range(steps + 1):
        sx = int(x0 + dx * i / steps)
        sy = int(y0 + dy * i / steps)
        fill(sx, sy, sx+w-1, sy, tid)

def vine_col(x, y0, y1, tid=10):
    """藤蔓柱"""
    for y in range(y0, y1+1):
        if world.get_tile(x, y).type_id == 0:
            world.set_tile(x, y, tid)

def tree(tx, ty, trunk_id=18, leaf_id=22, h=6):
    """一棵树"""
    for y in range(ty, ty+h):
        world.set_tile(tx, y, trunk_id)
    for dy in range(-2, 3):
        for dx in range(-3, 4):
            if abs(dx) + abs(dy) <= 4 and not (dx==0 and dy<2):
                world.set_tile(tx+dx, ty+h-2+dy, leaf_id)

# ==================== 全图基岩底 ====================
fill(0, 0, 479, 1, 68)   # 基岩
fill(0, 2, 479, 2, 67)   # 玄武岩

# ================================================================
# 区域1：起始森林 (x: 0-80, y: 3-80)
# ================================================================
# 地表（起伏草地）
for x in range(0, 81):
    base_y = 42 + int(8 * __import__('math').sin(x/12.0) + 4 * __import__('math').sin(x/5.0+1))
    for y in range(3, base_y):
        world.set_tile(x, y, 16)   # 泥土
    world.set_tile(x, base_y, 17)  # 草地
    if x % 7 == 0:
        world.set_tile(x, base_y+1, 50)  # 红花
    if x % 11 == 3:
        world.set_tile(x, base_y+1, 51)  # 黄花

# 树木
for tx in [5, 12, 22, 35, 48, 60, 72]:
    ty = 43 + int(8 * __import__('math').sin(tx/12.0) + 4 * __import__('math').sin(tx/5.0+1)) + 1
    tree(tx, ty, trunk_id=18, leaf_id=22, h=5+tx%4)

# 地下洞穴系统
for x in range(5, 75):
    cave_floor = 2 + int(15 * __import__('math').sin(x/8.0)**2)
    for y in range(3, cave_floor):
        if world.get_tile(x, y).type_id in (0, 16):
            world.set_tile(x, y, 0)  # 挖空
# 洞穴中的水晶
for _ in range(60):
    cx, cy = __import__('random').randint(8,72), __import__('random').randint(4,18)
    if world.get_tile(cx, cy).type_id == 0:
        world.set_tile(cx, cy, __import__('random').choice([200,201,204,206]))  # 水晶

# 起始平台（安全区）
fill(10, 50, 22, 50, 19)   # 木板
fill(10, 49, 22, 49, 16)   # 泥土支撑
# 起始火把
world.set_tile(12, 51, 43)
world.set_tile(20, 51, 43)
# 起始治愈之泉
circle(16, 51, 2, 290)
# 第一个检查点
world.set_tile(16, 50, 302)  # 重生祭坛

# 森林右侧悬崖通道
platform(55, 48, 65, 19, support_tid=18)
platform(60, 44, 70, 19, support_tid=18)
platform(52, 40, 58, 19)
# 第一个弹跳蘑菇（教学)
world.set_tile(62, 49, 293)

# 隐藏洞穴（樱花主题）
fill(30, 30, 38, 35, 0)        # 挖空
fill(30, 29, 38, 29, 220)      # 樱花木板天花板
fill(30, 36, 38, 36, 220)      # 地板
for x in range(31, 38):
    world.set_tile(x, 31, 221)  # 樱花叶装饰
world.set_tile(34, 36, 302)     # 隐藏检查点

# ---------------------------------------------------------------
# 区域2：水晶洞窟 (x: 0-80, y深层 + x:30-80地下湖)
# ---------------------------------------------------------------
# 主洞窟
for x in range(20, 70):
    for y in range(10, 25):
        if __import__('random').random() < 0.6:
            if world.get_tile(x, y).type_id in (16, 2, 0):
                world.set_tile(x, y, 0)
# 水晶簇
for _ in range(80):
    cx, cy = __import__('random').randint(22,68), __import__('random').randint(12,24)
    if world.get_tile(cx, cy).type_id == 0:
        world.set_tile(cx, cy, __import__('random').choice([200,201,202,203,204,205,206,207,209,211]))
# 治愈之泉（洞窟休息点）
circle(45, 15, 3, 290)
world.set_tile(45, 15, 302)  # 检查点

# 地下湖
for x in range(35, 65):
    for y in range(5, 12):
        world.set_tile(x, y, 7)  # 水
# 湖边荧光
for x in range(34, 66):
    world.set_tile(x, 4, 2)   # 石底
    world.set_tile(x, 12, 2)  # 石顶
    if x % 3 == 0:
        world.set_tile(x, 13, 242)  # 荧光礁
# 水中气泡柱
for bx in [40, 50, 58]:
    for y in range(6, 11):
        world.set_tile(bx, y, 73)  # 气泡柱

# ---------------------------------------------------------------
# 区域3：古代遗迹 (x: 80-170)
# ---------------------------------------------------------------
# 地表神庙基底
fill(85, 30, 165, 32, 230)    # 神庙砂岩
fill(85, 33, 165, 33, 230)
# 神庙墙
for x in [85, 95, 105, 115, 125, 135, 145, 155, 165]:
    fill(x, 34, x, 45, 230)

# 神庙内部房间
# 主厅
fill(86, 34, 94, 44, 0)
fill(86, 34, 94, 34, 230)     # 天花板
fill(87, 35, 87, 43, 231)     # 象形文字壁
fill(93, 35, 93, 43, 231)
# 符文石
world.set_tile(90, 35, 229)    # 发光符文
# 陷阱：诅咒血纹
fill(88, 36, 92, 36, 264)     # 诅咒地板（伤害）

# 走廊1
fill(96, 38, 104, 39, 0)
fill(96, 37, 104, 37, 230)    # 天花板
fill(96, 40, 104, 40, 230)    # 地板
# 尖刺陷阱
world.set_tile(100, 40, 32)

# 攀爬通道（上升）
for y in range(40, 55):
    world.set_tile(110, y, 31)  # 绳索
    world.set_tile(112, y, 31)
# 上方平台奖励
platform(108, 55, 114, 19, support_tid=232)  # 希腊柱支撑
world.set_tile(111, 56, 240)   # 珍珠块奖励
world.set_tile(111, 56, 302)   # 检查点

# 右侧陷阱走廊
fill(120, 35, 130, 38, 0)
fill(120, 34, 130, 34, 230)
# 压力板触发陷阱（用减速蛛网+尖刺模拟）
fill(123, 35, 127, 35, 299)   # 减速蛛网
fill(123, 36, 127, 36, 32)    # 尖刺
# 安全通道（需跳跃）
for x in [122, 128]:
    world.set_tile(x, 35, 19)  # 安全木板

# 隐藏密室（需从下方藤蔓爬入）
fill(140, 20, 148, 25, 0)
fill(140, 19, 148, 19, 230)
fill(140, 26, 148, 26, 233)   # 罗马马赛克地板
# 宝箱
world.set_tile(144, 26, 42)    # 箱子
world.set_tile(143, 26, 79)    # 金块
world.set_tile(145, 26, 80)    # 钻石块
# 密室入口藤蔓
for y in range(26, 35):
    vine_col(144, y, y, 10)
# 传送门T1（遗迹隐藏室 → 起始森林）
world.set_tile(144, 20, 300)
if (144, 20) in world.grid:
    world.grid[(144, 20)].meta = {"tp_x": 30, "tp_y": 48}

# 神庙右侧弹射挑战
platform(150, 38, 155, 19, support_tid=230)
platform(158, 42, 163, 19, support_tid=230)
platform(166, 46, 170, 19, support_tid=230)
world.set_tile(153, 39, 298)   # 跳跃增强
world.set_tile(160, 43, 298)
world.set_tile(168, 47, 298)

# ---------------------------------------------------------------
# 区域4：火山深渊 (x: 80-170, y: 0-30 深层)
# ---------------------------------------------------------------
# 火山岩基底
for x in range(90, 160):
    for y in range(3, 8):
        world.set_tile(x, y, 63)   # 下界砖

# 岩浆湖
fill(100, 8, 140, 10, 6)          # 熔岩
fill(98, 7, 142, 7, 63)           # 湖边
fill(98, 11, 142, 11, 63)

# 黑曜石通道（安全路径）
for x in range(95, 145, 3):
    for y in range(12, 15):
        if world.get_tile(x, y).type_id == 0:
            world.set_tile(x, y, 27)  # 黑曜石
# 萤石照明
for x in range(100, 140, 10):
    world.set_tile(x, 14, 69)      # 萤石

# 火山口（通向上方区域）
fill(115, 15, 125, 30, 0)
for x in range(114, 127):
    world.set_tile(x, 15, 61)      # 岩浆砖
    world.set_tile(x, 30, 61)
for y in range(16, 30):
    world.set_tile(114, y, 61)
    world.set_tile(126, y, 61)

# 再生水晶（火山隐藏奖励）
world.set_tile(120, 18, 291)       # 再生水晶（高风险高回报）
world.set_tile(120, 18, 302)       # 检查点

# 岩浆砖陷阱
fill(105, 16, 113, 16, 61)        # 灼热地板
fill(127, 16, 135, 16, 61)

# ---------------------------------------------------------------
# 区域5：天空群岛 (x: 170-250, y: 55-160)
# ---------------------------------------------------------------
# 底层云基
fill(170, 30, 250, 31, 33)         # 云块基座

# 主岛（大型浮空岛）
for x in range(180, 240):
    for y in range(32, 36):
        world.set_tile(x, y, 16)    # 泥土
    world.set_tile(x, 36, 17)       # 草地

# 主岛上的树和建筑
tree(185, 37, trunk_id=18, leaf_id=22, h=8)
tree(235, 37, trunk_id=18, leaf_id=22, h=7)
# 主岛建筑
fill(200, 37, 220, 42, 19)         # 木板屋
fill(202, 38, 218, 41, 0)          # 内部
world.set_tile(210, 37, 21)        # 玻璃窗
world.set_tile(210, 37, 302)       # 检查点
world.set_tile(205, 38, 292)       # 护盾发生器

# 浮空小岛群（需跑酷）
islands = [
    (175, 50, 4), (185, 58, 3), (195, 48, 4),
    (225, 52, 3), (235, 60, 4), (245, 50, 3),
    (180, 65, 3), (210, 68, 4), (240, 66, 3),
    (190, 75, 3), (220, 78, 4), (230, 85, 3),
    (200, 90, 4), (215, 95, 3), (225, 88, 3),
]
for ix, iy, iw in islands:
    for x in range(ix, ix+iw):
        for y in range(iy, iy+2):
            world.set_tile(x, y, 16)
        world.set_tile(x, iy+2, 17)
    # 每岛有不同的特性
    if ix % 5 == 0:
        world.set_tile(ix+iw//2, iy+3, 298)  # 跳跃增强
    elif ix % 5 == 1:
        world.set_tile(ix+iw//2, iy+3, 293)  # 弹跳蘑菇
    elif ix % 5 == 2:
        world.set_tile(ix+iw//2, iy+3, 297)  # 加速之路

# 藤蔓连接
for y in range(36, 60):
    vine_col(178, y, y, 10)
for y in range(50, 78):
    vine_col(248, y, y, 10)

# 云中隐藏平台（极光主题）
platform(195, 105, 205, 248, support_tid=33)
platform(215, 110, 230, 248, support_tid=33)
for x in range(197, 204):
    world.set_tile(x, 108, 214)   # 极光波浪
for x in range(218, 227):
    world.set_tile(x, 113, 214)

# 传送门T2（天空群岛 → 遗迹神庙）
world.set_tile(220, 110, 300)
if (220, 110) in world.grid:
    world.grid[(220, 110)].meta = {"tp_x": 130, "tp_y": 40}

# 高空奖励
platform(210, 120, 225, 33)        # 云平台
world.set_tile(217, 121, 240)      # 珍珠块
world.set_tile(218, 121, 79)       # 金块
world.set_tile(217, 121, 302)      # 检查点

# 弹射板连接链
world.set_tile(182, 37, 294)       # 上弹板
world.set_tile(193, 49, 294)
world.set_tile(203, 69, 294)
world.set_tile(213, 91, 294)

# ---------------------------------------------------------------
# 区域6：冰封王国 (x: 250-330)
# ---------------------------------------------------------------
# 冰层基底
for x in range(250, 331):
    for y in range(3, 8):
        world.set_tile(x, y, 246)   # 冰脉永冻

# 冰面（地表）
for x in range(250, 331):
    base_y = 35 + int(5 * __import__('math').sin(x/20.0))
    for y in range(8, base_y):
        world.set_tile(x, y, 23)    # 雪块
    world.set_tile(x, base_y, 3)    # 冰面

# 冰宫主建筑
fill(270, 36, 310, 60, 244)        # 冰宫
fill(275, 40, 305, 58, 0)          # 内部空间
# 冰柱
for cx in [278, 292, 302]:
    for y in range(36, 50):
        world.set_tile(cx, y, 245)  # 冰花柱
# 冰宫地板
fill(275, 39, 305, 39, 23)
fill(275, 59, 305, 59, 23)
# 滑冰区域（浮冰）
fill(280, 42, 290, 48, 75)         # 浮冰（极滑）
world.set_tile(285, 50, 293)        # 弹跳蘑菇
# 冰宫检查点
world.set_tile(290, 40, 302)

# 冰宫上层
fill(275, 62, 305, 75, 244)
fill(278, 63, 302, 72, 0)
for x in range(280, 300, 4):
    world.set_tile(x, 72, 248)      # 极光冰
# 冰宫宝藏
world.set_tile(290, 63, 240)        # 珍珠块
world.set_tile(285, 63, 292)        # 护盾发生器

# 攀爬冰道
for y in range(36, 65):
    vine_col(268, y, y, 10)         # 藤蔓柱（方便上下）
    vine_col(312, y, y, 10)

# 极光滑雪道
for x in range(315, 330):
    for y in range(30, 36):
        world.set_tile(x, y, 248)   # 极光冰（美丽+滑）
# 底部弹射
world.set_tile(322, 36, 294)

# ---------------------------------------------------------------
# 区域7：地下湖 (x: 250-330, y: 0-30)
# ---------------------------------------------------------------
for x in range(260, 320):
    for y in range(10, 25):
        world.set_tile(x, y, 7)     # 水
# 湖底
for x in range(258, 322):
    world.set_tile(x, 9, 5)         # 沙底
    world.set_tile(x, 25, 2)        # 石顶
# 湖中珊瑚
for _ in range(40):
    cx, cy = __import__('random').randint(262,318), __import__('random').randint(10,24)
    if world.get_tile(cx, cy).type_id == 7:
        world.set_tile(cx, cy, __import__('random').choice([237,238,239,242]))
# 气泡柱上浮通道
for bx in [275, 290, 305]:
    for y in range(10, 25):
        world.set_tile(bx, y, 73)
# 湖底洞穴（气室）
fill(280, 15, 295, 18, 0)
fill(280, 14, 295, 14, 2)         # 石顶
fill(280, 19, 295, 19, 2)         # 石底
world.set_tile(287, 19, 291)       # 再生水晶
world.set_tile(287, 19, 302)       # 检查点

# ---------------------------------------------------------------
# 区域8：沙漠神庙 (x: 330-420)
# ---------------------------------------------------------------
# 沙漠地表
for x in range(330, 421):
    for y in range(3, 22):
        world.set_tile(x, y, 5)     # 沙

# 金字塔主体
py_base = 40
for layer in range(8):
    lx0, lx1 = 355 - layer*4, 395 + layer*4
    ly = py_base + layer * 5
    fill(lx0, ly, lx1, ly+4, 24)   # 砂岩

# 金字塔入口
fill(372, py_base, 378, py_base+5, 0)
fill(371, py_base-1, 379, py_base-1, 24)

# 金字塔内部
# 第一层
fill(365, py_base+6, 385, py_base+12, 0)
fill(365, py_base+5, 385, py_base+5, 24)
fill(365, py_base+13, 385, py_base+13, 24)
# 陷阱走廊
fill(368, py_base+6, 382, py_base+6, 264)  # 诅咒地板
world.set_tile(375, py_base+7, 302)  # 检查点

# 第二层
fill(368, py_base+14, 382, py_base+19, 0)
fill(368, py_base+14, 382, py_base+14, 24)
# 弹射挑战
fill(370, py_base+15, 375, py_base+15, 0)
world.set_tile(373, py_base+15, 294)
world.set_tile(373, py_base+19, 297)  # 加速

# 第三层（宝藏室）
fill(371, py_base+20, 379, py_base+26, 0)
fill(371, py_base+20, 379, py_base+20, 230)
# 宝藏
world.set_tile(374, py_base+21, 79)    # 金块
world.set_tile(376, py_base+21, 80)    # 钻石块
world.set_tile(375, py_base+21, 42)    # 箱子
# 传送门T3（金字塔顶 → 冰宫宝藏室）
world.set_tile(375, py_base+40, 300)
if (375, py_base+40) in world.grid:
    world.grid[(375, py_base+40)].meta = {"tp_x": 290, "tp_y": 63}

# 沙漠绿洲（回复区）
for x in range(400, 415):
    for y in range(18, 23):
        world.set_tile(x, y, 7)        # 水
fill(398, 17, 417, 17, 5)              # 沙岸
world.set_tile(407, 23, 290)            # 治愈之泉
world.set_tile(407, 17, 302)            # 检查点
tree(408, 24, trunk_id=18, leaf_id=22, h=5)

# ---------------------------------------------------------------
# 区域9：终焉高塔 (x: 420-480)
# ---------------------------------------------------------------
# 塔基
fill(430, 3, 470, 6, 68)               # 基岩底座
fill(432, 7, 468, 10, 254)             # 暗钢

# 塔身
for floor_y in range(15, 190, 25):
    # 地板
    fill(435, floor_y, 465, floor_y, 19)
    fill(435, floor_y+1, 465, floor_y+1, 0)  # 空间
    # 塔壁
    for y in range(floor_y+2, floor_y+23):
        world.set_tile(435, y, 254)     # 暗钢壁
        world.set_tile(465, y, 254)
    # 天花板
    fill(435, floor_y+23, 465, floor_y+23, 19)
    # 塔层内容（每层不同挑战）

# 第1层（入门）：加速跑道
fill(436, 16, 464, 17, 297)            # 加速之路

# 第2层（40）：弹射挑战
platform(440, 42, 460, 19)
world.set_tile(438, 41, 294)            # 上弹板

# 第3层（65）：攀爬墙
for y in range(66, 80):
    vine_col(440, y, y, 31)            # 绳索墙
    vine_col(460, y, y, 31)

# 第4层（90）：尖刺+跳跃
fill(440, 91, 460, 91, 32)             # 尖刺地板
platform(445, 93, 455, 19)

# 第5层（115）：减速+弹射
fill(442, 116, 458, 116, 299)           # 蛛网
world.set_tile(450, 117, 294)           # 弹射板

# 第6层（140）：休息层
fill(438, 141, 462, 155, 0)
world.set_tile(445, 141, 291)           # 再生水晶
world.set_tile(455, 141, 292)           # 护盾发生器
world.set_tile(450, 141, 302)           # 检查点

# 第7层（165）：最后冲刺
platform(440, 167, 445, 19)
platform(450, 172, 455, 19)
platform(440, 177, 445, 19)
world.set_tile(443, 168, 298)           # 跳跃增强
world.set_tile(453, 173, 298)
world.set_tile(443, 178, 298)

# 塔顶（终点）
fill(440, 195, 460, 200, 19)
fill(442, 201, 458, 201, 255)           # 黄铜齿轮板（华丽地板）
# 终端奖励台
world.set_tile(448, 202, 79)            # 金块
world.set_tile(450, 202, 80)            # 钻石块
world.set_tile(452, 202, 78)            # 铁块
world.set_tile(450, 203, 265)           # 祝福圣光
# 终点标记（用特殊方块组合）
world.set_tile(449, 202, 257)           # 电弧核心
world.set_tile(451, 202, 257)
world.set_tile(450, 203, 267)           # 奥术法阵
world.set_tile(450, 201, 302)           # 最终检查点

# 传送门T4（高塔底部 → 沙漠绿洲）
world.set_tile(468, 17, 300)
if (468, 17) in world.grid:
    world.grid[(468, 17)].meta = {"tp_x": 407, "tp_y": 23}

# ---------------------------------------------------------------
# 全图连通：传送门网络
# ---------------------------------------------------------------
# 传送门需要在地图配置中设置目标坐标（special_data）
# 这些在config.json中设置：

# T1: 遗迹隐藏室 → 起始森林  (144,20) → (30,48)
# T2: 天空群岛 → 遗迹区    (220,110) → (130,40)
# T3: 金字塔顶 → 冰宫     (375,py_base+40) → (290,63)
# T4: 高塔底部 → 沙漠绿洲  (468,17) → (407,23)
# 传送门T5（起始森林后方 → 天空群岛）
world.set_tile(70, 50, 300)
if (70, 50) in world.grid:
    world.grid[(70, 50)].meta = {"tp_x": 185, "tp_y": 70}

# 设置一些可用的传送门具体坐标（待config.json覆盖）
# 此处仅放置方块，目标坐标在地图配置文件中指定

# ---------------------------------------------------------------
# 全局细节：装饰与隐藏区域
# ---------------------------------------------------------------
# 全图散布的隐藏洞穴
hidden_caves = [
    (50, 55, 3), (100, 65, 2), (160, 70, 3),
    (200, 100, 2), (260, 80, 3), (320, 60, 2),
    (380, 75, 3), (440, 120, 2),
]
for hx, hy, hr in hidden_caves:
    for x in range(hx-hr, hx+hr+1):
        for y in range(hy-hr, hy+hr+1):
            if (x-hx)**2 + (y-hy)**2 <= hr**2:
                if world.get_tile(x, y).type_id == 0:
                    world.set_tile(x, y, 0)
    # 洞穴墙
    for x in range(max(0,hx-hr-1), min(479, hx+hr+1)+1):
        for y in range(max(0,hy-hr-1), min(279, hy+hr+1)+1):
            d2 = (x-hx)**2 + (y-hy)**2
            if hr**2 < d2 <= (hr+1)**2:
                if world.get_tile(x, y).type_id == 0:
                    world.set_tile(x, y, __import__('random').choice([2,25,34]))
    # 洞穴内奖励
    world.set_tile(hx, hy, __import__('random').choice([200,240,79,207,291]))

# 全图藤蔓/绳索连接（方便垂直移动）
for x in range(20, 470, 50):
    if world.get_tile(x, 30).type_id != 0:
        for y in range(31, 45):
            if world.get_tile(x, y).type_id == 0:
                world.set_tile(x, y, __import__('random').choice([10,31]))

# 全局治愈点分布（不至于太难）
heal_spots = [(30,48), (75,40), (120,42), (175,32), (210,36),
              (260,38), (300,50), (340,20), (375,30), (407,23),
              (450,141), (200,85), (150,55), (100,20)]
for hx, hy in heal_spots:
    if 0 <= hx < 480 and 0 <= hy < 280:
        if world.get_tile(hx, hy).type_id == 0:
            world.set_tile(hx, hy, 290)  # 治愈之泉

world.end_bulk_load()
