"""
Buff 功能方块 — 精心设计，先有概念后有属性。
每个方块有独立视觉、有意义的名字、明确的游戏用途。
"""
from block_type import BlockType

G = 16
F = lambda r,g,b: ("fill",(r,g,b))
R = lambda x,y,w,h,c: ("rect",x,y,w,h,c)
C = lambda x,y,r,c: ("circle",x,y,r,c)

BUFF_BLOCKS = {}
_n = 360
def add(bt):
    global _n
    bt.id = _n
    BUFF_BLOCKS[_n] = bt
    _n += 1

# ═══════════════════════════════════════════════════════
# 恢复/庇护类 — 关卡前后的安全区、奖励房
# ═══════════════════════════════════════════════════════

add(BlockType(0, "life_spring", "生命之泉", is_solid=True, light_level=6,
    color=(80,180,220),
    pattern=("vector",(G,G),[F(80,180,220),C(8,9,5,(130,210,240)),C(8,9,3,(180,240,255)),
             R(6,6,4,6,(140,210,245)),C(8,6,2,(255,255,255))]),
    buff_ids=(1,), buff_params_list=((8,),), buff_durations=(6.0,), break_hp=80))

add(BlockType(0, "guardian_flower", "护佑花", is_solid=False, light_level=4,
    color=(60,150,80),
    pattern=("vector",(G,G),[F(60,130,60),R(7,10,2,6,(80,180,80)),
             R(5,8,6,1,(80,180,80)),R(4,10,8,1,(80,180,80)),
             C(8,5,4,(255,200,100)),C(8,5,2,(255,255,150)),
             C(6,3,1,(255,150,200)),C(10,3,1,(200,150,255)),C(8,7,1,(150,255,200))]),
    buff_ids=(2,1), buff_params_list=((5,),(3,)), buff_durations=(8.0,8.0), break_hp=30))

add(BlockType(0, "purifying_spring", "净化之泉", is_solid=True, light_level=4,
    color=(100,190,230),
    pattern=("vector",(G,G),[F(100,190,230),C(8,9,5,(160,225,250)),C(8,9,3,(220,245,255)),
             R(6,7,4,5,(180,235,250)),C(8,9,1,(255,255,255))]),
    buff_ids=(12,), buff_params_list=((2,),), buff_durations=(4.0,), break_hp=60))

add(BlockType(0, "vigor_bloom", "活力之花", is_solid=False, light_level=3,
    color=(255,180,40),
    pattern=("vector",(G,G),[F(180,140,60),R(7,10,2,6,(200,160,80)),
             R(4,9,8,1,(200,160,80)),C(8,5,4,(255,220,60)),C(8,5,2,(255,255,150))]),
    buff_ids=(5,), buff_params_list=((0,),), buff_durations=(10.0,), break_hp=30))

add(BlockType(0, "guardian_stele", "守护士碑", is_solid=True, light_level=2,
    color=(180,160,100),
    pattern=("vector",(G,G),[F(180,160,100),R(5,1,6,14,(200,180,120)),
             R(4,2,8,2,(220,200,140)),R(4,13,8,2,(220,200,140))]),
    buff_ids=(7,6), buff_params_list=((0,),(0,)), buff_durations=(12.0,12.0), break_hp=150))

add(BlockType(0, "phoenix_perch", "凤栖石", is_solid=True, light_level=5,
    color=(255,150,30),
    pattern=("vector",(G,G),[F(255,150,30),C(8,6,4,(255,200,80)),C(8,6,2,(255,255,150)),
             R(6,8,4,6,(255,180,60)),R(4,10,8,1,(255,200,100))]),
    buff_ids=(1,2), buff_params_list=((12,),(4,)), buff_durations=(5.0,5.0), break_hp=60))

add(BlockType(0, "holy_pillar", "圣光之柱", is_solid=True, light_level=8,
    color=(255,240,180),
    pattern=("vector",(G,G),[F(255,240,180),R(6,1,4,14,(255,250,220)),
             R(5,2,6,2,(255,255,240)),R(5,13,6,2,(255,255,240)),C(8,8,3,(255,255,255))]),
    buff_ids=(50,1), buff_params_list=((0,),(5,)), buff_durations=(15.0,15.0), break_hp=200))

add(BlockType(0, "rebirth_anchor", "重生之锚", is_solid=True, light_level=5,
    color=(255,200,100),
    pattern=("vector",(G,G),[F(255,200,100),R(6,2,4,12,(255,230,150)),
             R(2,7,12,2,(255,230,150)),C(8,8,3,(255,250,200)),
             R(5,1,6,3,(255,220,120)),R(5,12,6,3,(255,220,120))]),
    buff_ids=(1,), buff_params_list=((20,),), buff_durations=(3.0,),
    special="set_spawn", break_hp=300))

# ═══════════════════════════════════════════════════════
# 陷阱/危险类 — 复合负面效果，设计跑酷/战斗挑战
# ═══════════════════════════════════════════════════════

add(BlockType(0, "magma_flow", "熔岩流", is_solid=False, space_f=0.92, swim_f=2.5,
    color=(240,70,10), light_level=3, damage_ps=30,
    pattern=("vector",(G,G),[F(240,70,10),R(0,3,16,2,(255,130,20)),
             R(0,8,16,3,(255,100,15)),R(3,12,10,2,(255,150,30))]),
    buff_ids=(16,), buff_params_list=((15,),), buff_durations=(12.0,), break_hp=999))

add(BlockType(0, "magma_brick", "熔岩砖", is_solid=True, light_level=2,
    color=(180,50,10),
    pattern=("vector",(G,G),[F(180,50,10),R(2,2,5,5,(220,90,30)),R(9,2,5,5,(220,90,30)),
             R(2,9,5,5,(220,90,30)),R(9,9,5,5,(220,90,30)),R(4,4,3,3,(255,140,50))]),
    buff_ids=(16,), buff_params_list=((5,),), buff_durations=(3.0,), break_hp=80))

add(BlockType(0, "web_trap", "蛛网陷阱", is_solid=False, space_f=0.97,
    color=(200,200,210),
    pattern=("vector",(G,G),[F(180,175,185),R(1,7,14,2,(210,205,215)),
             R(7,1,2,14,(210,205,215)),R(3,4,10,1,(195,190,200)),R(4,11,8,1,(195,190,200))]),
    buff_ids=(21,22), buff_params_list=((0,),(50,)), buff_durations=(4.0,4.0), break_hp=20))

add(BlockType(0, "thorn_bush", "荆棘丛", is_solid=True, damage_ps=8,
    color=(120,80,40),
    pattern=("vector",(G,G),[F(120,80,40),R(3,3,4,6,(160,110,60)),R(10,2,3,8,(160,110,60)),
             R(6,1,2,10,(140,95,50)),R(5,8,8,1,(140,95,50))]),
    buff_ids=(17,), buff_params_list=((2,),), buff_durations=(6.0,), break_hp=40))

add(BlockType(0, "toxic_bog", "毒沼", is_solid=False, space_f=0.96, damage_ps=5,
    color=(100,160,80),
    pattern=("vector",(G,G),[F(100,160,80),C(6,7,3,(130,200,100)),C(12,9,2,(140,200,110)),
             R(3,10,10,2,(120,180,90))]),
    buff_ids=(22,46), buff_params_list=((30,),(0,)), buff_durations=(5.0,5.0), break_hp=30))

add(BlockType(0, "frozen_ground", "冰封地面", is_solid=True, surface_f=1.08,
    color=(180,220,240),
    pattern=("vector",(G,G),[F(180,220,240),R(0,3,16,1,(200,235,250)),
             R(0,8,16,1,(200,235,250)),R(0,13,16,1,(200,235,250)),
             C(4,5,2,(220,245,255)),C(12,11,2,(220,245,255))]),
    buff_ids=(51,42), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=50))

add(BlockType(0, "spike_trap", "尖刺陷阱", is_solid=True, damage_ps=40,
    color=(150,150,160),
    pattern=("vector",(G,G),[F(150,150,160),R(7,2,2,12,(180,180,190)),
             R(4,3,2,5,(180,180,190)),R(10,3,2,5,(180,180,190)),
             R(6,1,4,2,(200,200,210)),R(3,2,10,1,(200,200,210))]),
    buff_ids=(17,29), buff_params_list=((3,),(0,)), buff_durations=(4.0,4.0), break_hp=60))

add(BlockType(0, "confusion_mist", "混乱之雾", is_solid=False, space_f=1.0,
    color=(200,170,220),
    pattern=("vector",(G,G),[F(200,170,220),C(5,6,4,(220,200,240)),
             C(11,9,3,(220,200,240)),C(8,4,2,(230,215,245))]),
    buff_ids=(23,44), buff_params_list=((0,),(3,)), buff_durations=(5.0,5.0), break_hp=20))

add(BlockType(0, "cursed_stele", "诅咒石碑", is_solid=True, light_level=1,
    color=(70,25,70),
    pattern=("vector",(G,G),[F(70,25,70),C(8,8,5,(110,55,110)),C(8,8,3,(70,25,70)),
             R(4,4,8,1,(130,75,130)),R(4,12,8,1,(130,75,130))]),
    buff_ids=(57,18), buff_params_list=((0,),(3,)), buff_durations=(15.0,15.0), break_hp=120))

add(BlockType(0, "gravity_trap", "重力陷阱", is_solid=True,
    color=(100,80,120),
    pattern=("vector",(G,G),[F(100,80,120),C(8,8,6,(140,120,160)),C(8,8,4,(100,80,120)),
             C(8,8,2,(160,140,180)),R(6,8,4,1,(180,160,200))]),
    buff_ids=(27,), buff_params_list=((0,),), buff_durations=(6.0,),
    special="gravity_well", special_data=30, break_hp=100))

add(BlockType(0, "blinding_mist", "失明之雾", is_solid=False, space_f=1.0,
    color=(240,230,120),
    pattern=("vector",(G,G),[F(240,230,120),C(6,7,4,(250,245,180)),
             C(11,8,3,(250,245,180)),C(8,5,2,(255,250,200))]),
    buff_ids=(24,25), buff_params_list=((0,),(8,)), buff_durations=(6.0,6.0), break_hp=20))

add(BlockType(0, "silence_wall", "沉默之墙", is_solid=True,
    color=(130,120,160),
    pattern=("vector",(G,G),[F(130,120,160),R(3,2,10,12,(170,160,200)),
             R(5,4,6,8,(150,140,180)),R(9,3,1,10,(190,180,210))]),
    buff_ids=(32,30), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=80))

add(BlockType(0, "weakness_stone", "虚弱石", is_solid=True,
    color=(140,90,60),
    pattern=("vector",(G,G),[F(140,90,60),R(4,3,8,10,(180,130,100)),
             R(6,5,4,6,(120,70,40)),C(8,8,2,(160,110,80))]),
    buff_ids=(18,19), buff_params_list=((2.5,),(40,)), buff_durations=(8.0,8.0), break_hp=70))

# ═══════════════════════════════════════════════════════
# 环境/移动挑战 — 改变物理规则，解谜/跑酷
# ═══════════════════════════════════════════════════════

add(BlockType(0, "electrified_pool", "带电水域", is_solid=False, space_f=0.985, swim_f=4.0,
    color=(100,140,240),
    pattern=("vector",(G,G),[F(100,140,240),R(0,4,16,1,(140,180,255)),
             R(0,9,16,1,(140,180,255)),R(0,14,16,1,(140,180,255)),
             R(6,2,2,4,(255,220,80)),R(10,10,2,4,(255,220,80))]),
    buff_ids=(45,), buff_params_list=((0,),), buff_durations=(8.0,), break_hp=999))

add(BlockType(0, "sticky_floor", "黏着地面", is_solid=True, surface_f=0.92,
    color=(200,160,100),
    pattern=("vector",(G,G),[F(200,160,100),R(2,3,4,4,(180,140,80)),R(10,3,4,4,(180,140,80)),
             R(5,8,6,4,(180,140,80)),R(2,13,12,2,(180,140,80))]),
    buff_ids=(43,22), buff_params_list=((0,),(20,)), buff_durations=(6.0,6.0), break_hp=40))

add(BlockType(0, "slick_ice", "滑溜冰道", is_solid=True, surface_f=1.06,
    color=(200,240,255),
    pattern=("vector",(G,G),[F(200,240,255),R(0,1,16,2,(230,250,255)),
             R(0,7,16,2,(230,250,255)),R(0,13,16,2,(230,250,255)),
             C(5,8,2,(250,255,255)),C(12,4,1,(250,255,255))]),
    buff_ids=(42,), buff_params_list=((0,),), buff_durations=(8.0,), break_hp=40))

add(BlockType(0, "ghost_wall", "幽灵墙", is_solid=True, light_level=1,
    color=(120,130,180),
    pattern=("vector",(G,G),[F(120,130,180),R(4,3,8,10,(150,160,210)),
             C(8,8,4,(120,130,180)),C(8,8,2,(180,190,230))]),
    buff_ids=(48,), buff_params_list=((0,),), buff_durations=(5.0,), break_hp=200))

add(BlockType(0, "shadow_stone", "暗影石", is_solid=True, light_level=0,
    color=(50,50,80),
    pattern=("vector",(G,G),[F(50,50,80),C(8,8,6,(70,70,100)),C(8,8,3,(40,40,70)),
             R(6,6,4,4,(60,60,90))]),
    buff_ids=(38,), buff_params_list=((0,),), buff_durations=(10.0,), break_hp=80))

add(BlockType(0, "magnetic_lode", "磁石矿", is_solid=True,
    color=(140,110,90),
    pattern=("vector",(G,G),[F(140,110,90),C(8,8,6,(170,140,120)),C(8,8,4,(140,110,90)),
             R(3,7,10,2,(180,150,130)),R(7,3,2,10,(180,150,130))]),
    buff_ids=(49,), buff_params_list=((0,),), buff_durations=(8.0,),
    special="magnetic", special_data=15, break_hp=100))

add(BlockType(0, "wind_vortex", "旋风涡", is_solid=False, space_f=1.0,
    color=(180,200,210),
    pattern=("vector",(G,G),[F(180,200,210),R(3,7,10,2,(200,220,230)),
             C(8,5,3,(210,230,240)),C(5,10,2,(210,230,240)),C(12,10,2,(210,230,240))]),
    buff_ids=(53,), buff_params_list=((0,),), buff_durations=(5.0,),
    special="wind", special_data=(0,20), break_hp=60))

add(BlockType(0, "anchor_rock", "定锚岩", is_solid=True,
    color=(120,100,80),
    pattern=("vector",(G,G),[F(120,100,80),R(7,2,2,12,(150,130,110)),
             R(3,7,10,2,(150,130,110)),R(3,4,4,4,(140,120,100))]),
    buff_ids=(54,7), buff_params_list=((0,),(0,)), buff_durations=(15.0,15.0), break_hp=120))

add(BlockType(0, "anti_grav_ore", "浮空矿石", is_solid=True,
    color=(200,200,230),
    pattern=("vector",(G,G),[F(200,200,230),C(8,8,5,(220,220,250)),C(8,8,2,(240,240,255)),
             R(6,7,4,1,(240,240,255)),R(7,6,2,4,(240,240,255))]),
    buff_ids=(13,), buff_params_list=((0,),), buff_durations=(10.0,),
    bounce=(0,15), break_hp=60))

# ═══════════════════════════════════════════════════════
# 战斗辅助 — 风险/回报，策略选择
# ═══════════════════════════════════════════════════════

add(BlockType(0, "berserk_blood", "狂暴之血", is_solid=True, light_level=2,
    color=(180,25,25),
    pattern=("vector",(G,G),[F(180,25,25),C(8,8,5,(220,60,60)),C(8,8,3,(160,15,15)),
             R(6,6,4,4,(200,40,40))]),
    buff_ids=(47,17), buff_params_list=((0,),(1,)), buff_durations=(10.0,10.0), break_hp=60))

add(BlockType(0, "stone_skin_stele", "石肤之碑", is_solid=True, light_level=1,
    color=(160,150,140),
    pattern=("vector",(G,G),[F(160,150,140),R(4,1,8,14,(190,180,170)),
             R(3,2,10,2,(210,200,190)),R(3,13,10,2,(210,200,190))]),
    buff_ids=(39,7), buff_params_list=((0,),(0,)), buff_durations=(15.0,15.0), break_hp=150))

add(BlockType(0, "thorn_barrier", "荆棘之壁", is_solid=True, light_level=2,
    color=(140,180,80),
    pattern=("vector",(G,G),[F(140,180,80),C(8,8,5,(180,220,120)),C(8,8,3,(120,160,60)),
             R(5,7,6,2,(180,220,120)),R(7,5,2,6,(180,220,120))]),
    buff_ids=(10,2), buff_params_list=((30,),(3,)), buff_durations=(10.0,10.0), break_hp=100))

add(BlockType(0, "eye_of_clarity", "清明之眼", is_solid=True, light_level=4,
    color=(200,200,100),
    pattern=("vector",(G,G),[F(200,200,100),C(8,8,6,(230,230,150)),C(8,8,4,(180,180,60)),
             C(8,8,2,(255,255,200)),R(4,8,8,1,(160,160,50))]),
    buff_ids=(8,40), buff_params_list=((0,),(0,)), buff_durations=(20.0,20.0), break_hp=80))

add(BlockType(0, "stealth_mist", "隐身之雾", is_solid=False, space_f=1.0,
    color=(80,80,120),
    pattern=("vector",(G,G),[F(80,80,120),C(6,7,4,(120,120,160)),
             C(11,8,3,(120,120,160)),C(8,5,2,(140,140,180))]),
    buff_ids=(38,53), buff_params_list=((0,),(0,)), buff_durations=(12.0,12.0), break_hp=20))

# ═══════════════════════════════════════════════════════
# 元素复合 — 自然元素交互
# ═══════════════════════════════════════════════════════

add(BlockType(0, "frostfire_ore", "霜火石", is_solid=True, light_level=3,
    color=(140,120,180),
    pattern=("vector",(G,G),[F(140,120,180),R(2,2,6,6,(100,200,240)),
             R(8,8,6,6,(240,100,50)),R(2,8,6,6,(240,100,50)),R(8,2,6,6,(100,200,240))]),
    buff_ids=(51,46), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=80))

add(BlockType(0, "thunder_crystal", "雷鸣晶", is_solid=True, light_level=5,
    color=(180,180,100),
    pattern=("vector",(G,G),[F(180,180,100),R(7,2,2,8,(255,255,150)),
             R(6,7,4,2,(255,255,150)),R(7,10,2,4,(255,220,50)),C(8,1,1,(255,255,255))]),
    buff_ids=(45,), buff_params_list=((0,),), buff_durations=(8.0,),
    bounce=(0,12), break_hp=60))

add(BlockType(0, "parasitic_vine", "寄生藤", is_solid=False, climbable=True, damage_ps=3,
    color=(100,60,80),
    pattern=("vector",(G,G),[F(100,60,80),R(4,0,3,16,(140,90,110)),
             R(10,0,3,12,(140,90,110)),R(6,4,2,8,(120,75,100))]),
    buff_ids=(55,17), buff_params_list=((0,),(1,)), buff_durations=(8.0,8.0), break_hp=25))

# ═══════════════════════════════════════════════════════
# 趣味/探索 — 奖励、秘密、特殊机制
# ═══════════════════════════════════════════════════════

add(BlockType(0, "lucky_clover_patch", "幸运草甸", is_solid=False, light_level=3,
    color=(80,200,60),
    pattern=("vector",(G,G),[F(80,200,60),C(5,4,3,(120,240,100)),C(11,4,3,(120,240,100)),
             C(5,12,3,(120,240,100)),C(11,12,3,(120,240,100)),
             R(7,10,2,6,(60,180,40)),R(6,11,4,1,(60,180,40))]),
    buff_ids=(52,), buff_params_list=((0,),), buff_durations=(30.0,),
    special="score", special_data=200, break_hp=20))

add(BlockType(0, "echo_crystal_cluster", "回声晶簇", is_solid=True, light_level=3,
    color=(150,180,220),
    pattern=("vector",(G,G),[F(150,180,220),R(6,2,4,12,(190,210,240)),
             R(3,5,2,6,(190,210,240)),R(11,5,2,6,(190,210,240)),C(8,14,1,(220,240,255))]),
    buff_ids=(56,), buff_params_list=((0,),), buff_durations=(20.0,), break_hp=60))

add(BlockType(0, "windblessed_path", "风佑之路", is_solid=True,
    color=(170,210,220),
    pattern=("vector",(G,G),[F(170,210,220),R(3,7,10,2,(200,230,240)),
             R(7,3,2,10,(200,230,240)),C(8,8,3,(220,240,250)),C(8,8,1,(255,255,255))]),
    buff_ids=(53,3), buff_params_list=((0,),(30,)), buff_durations=(8.0,8.0), break_hp=50))

add(BlockType(0, "drowsy_spore", "困倦孢子", is_solid=False, space_f=1.0,
    color=(160,140,200),
    pattern=("vector",(G,G),[F(160,140,200),C(5,6,3,(190,170,220)),
             C(11,7,3,(190,170,220)),C(8,3,2,(210,190,230)),C(8,12,2,(130,110,170))]),
    buff_ids=(44,19), buff_params_list=((3,),(30,)), buff_durations=(6.0,6.0), break_hp=20))

add(BlockType(0, "slick_algae", "滑溜藻", is_solid=False, surface_f=1.06,
    color=(100,200,120),
    pattern=("vector",(G,G),[F(100,200,120),R(2,3,5,4,(140,230,150)),
             R(9,5,5,4,(140,230,150)),R(4,9,8,4,(120,220,140))]),
    buff_ids=(42,), buff_params_list=((0,),), buff_durations=(6.0,), break_hp=15))

add(BlockType(0, "magnetized_vein", "磁化矿脉", is_solid=True,
    color=(150,130,110),
    pattern=("vector",(G,G),[F(150,130,110),R(2,5,12,6,(180,160,140)),
             R(4,7,8,2,(200,180,160)),R(7,3,2,10,(130,110,90))]),
    buff_ids=(49,), buff_params_list=((0,),), buff_durations=(10.0,),
    special="magnetic", special_data=10, break_hp=90))

# ═══════════════════════════════════════════════════════
# 恢复/庇护 续 — 更多主题、更多组合
# ═══════════════════════════════════════════════════════

add(BlockType(0, "crystal_ward", "水晶结界", is_solid=True, light_level=5,
    color=(160,200,255),
    pattern=("vector",(G,G),[F(160,200,255),R(3,3,10,10,(200,230,255)),
             R(5,5,6,6,(240,250,255)),C(8,8,2,(100,160,240)),
             R(6,1,4,14,(180,220,250)),R(1,6,14,4,(180,220,250))]),
    buff_ids=(2,36), buff_params_list=((8,),(0,)), buff_durations=(6.0,3.0), break_hp=120))

add(BlockType(0, "soothing_blossom", "安神花", is_solid=False, light_level=2,
    color=(180,160,220),
    pattern=("vector",(G,G),[F(130,110,80),R(7,10,2,6,(160,140,110)),
             R(5,9,6,1,(160,140,110)),C(8,4,4,(200,180,240)),C(8,4,2,(240,230,255)),
             C(6,3,1,(255,200,255)),C(10,3,1,(200,200,255))]),
    buff_ids=(5,34), buff_params_list=((0,),(0,)), buff_durations=(8.0,8.0), break_hp=30))

add(BlockType(0, "ironheart_shrine", "铁心祭坛", is_solid=True, light_level=3,
    color=(160,140,80),
    pattern=("vector",(G,G),[F(160,140,80),R(4,2,8,12,(200,180,120)),
             R(5,3,6,1,(220,200,140)),R(5,12,6,2,(220,200,140)),
             C(8,8,3,(240,220,160)),C(8,8,1,(255,255,200))]),
    buff_ids=(40,6), buff_params_list=((0,),(0,)), buff_durations=(15.0,15.0), break_hp=160))

add(BlockType(0, "cleansing_pool", "涤罪之池", is_solid=True, light_level=4,
    color=(120,200,220),
    pattern=("vector",(G,G),[F(120,200,220),C(8,9,5,(170,230,245)),C(8,9,3,(220,245,255)),
             R(5,7,6,4,(190,235,248)),C(8,6,2,(255,255,255)),C(4,11,2,(200,240,255))]),
    buff_ids=(12,1), buff_params_list=((1.5,),(6,)), buff_durations=(4.0,6.0), break_hp=70))

# ═══════════════════════════════════════════════════════
# 陷阱/危险 续
# ═══════════════════════════════════════════════════════

add(BlockType(0, "spike_pit_filled", "尖刺陷坑", is_solid=True, damage_ps=60,
    color=(100,70,60),
    pattern=("vector",(G,G),[F(100,70,60),R(1,1,14,14,(140,110,100)),
             R(5,2,2,10,(180,150,140)),R(9,2,2,10,(180,150,140)),
             R(3,1,10,2,(160,130,120)),R(3,13,10,2,(160,130,120))]),
    buff_ids=(17,29), buff_params_list=((5,),(0,)), buff_durations=(5.0,5.0), break_hp=100))

add(BlockType(0, "corrosive_acid", "腐蚀酸液", is_solid=False, space_f=0.94, swim_f=2.0,
    color=(180,220,40), damage_ps=20,
    pattern=("vector",(G,G),[F(180,220,40),R(0,2,16,2,(200,240,80)),
             R(0,7,16,2,(160,200,30)),R(2,12,12,2,(200,240,80)),
             C(5,9,2,(220,250,120)),C(12,4,2,(220,250,120))]),
    buff_ids=(46,26), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=999))

add(BlockType(0, "frost_snare", "冰霜陷阱", is_solid=False, space_f=1.0,
    color=(200,230,250),
    pattern=("vector",(G,G),[F(200,230,250),C(8,8,6,(230,245,255)),
             C(8,8,3,(180,220,245)),R(4,4,8,8,(210,235,252)),
             C(5,5,1,(255,255,255)),C(11,11,1,(255,255,255))]),
    buff_ids=(51,21), buff_params_list=((0,),(0,)), buff_durations=(5.0,5.0), break_hp=30))

add(BlockType(0, "reverse_pole", "反转磁极", is_solid=True,
    color=(140,120,180),
    pattern=("vector",(G,G),[F(140,120,180),R(6,2,4,12,(180,160,220)),
             C(8,6,2,(220,200,250)),C(8,12,2,(100,80,150)),
             R(3,8,10,1,(180,160,220)),R(3,10,10,1,(100,80,150))]),
    buff_ids=(23,49), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=70))

add(BlockType(0, "grounding_field", "接地场", is_solid=True,
    color=(100,140,120),
    pattern=("vector",(G,G),[F(100,140,120),R(3,3,10,10,(140,180,160)),
             R(5,5,6,6,(120,160,140)),R(7,2,2,12,(80,120,100)),
             R(2,7,12,2,(80,120,100))]),
    buff_ids=(27,45), buff_params_list=((0,),(0,)), buff_durations=(6.0,3.0), break_hp=90))

add(BlockType(0, "disarming_mist", "缴械之雾", is_solid=False, space_f=1.0,
    color=(200,140,140),
    pattern=("vector",(G,G),[F(200,140,140),C(6,7,4,(230,180,180)),
             C(11,8,3,(230,180,180)),R(6,2,4,10,(180,120,120)),
             R(4,5,8,6,(210,160,160))]),
    buff_ids=(30,31), buff_params_list=((0,),(0,)), buff_durations=(5.0,5.0), break_hp=25))

add(BlockType(0, "interference_tower", "干扰塔", is_solid=True, light_level=2,
    color=(160,140,120),
    pattern=("vector",(G,G),[F(160,140,120),R(7,1,2,14,(200,180,160)),
             C(8,4,4,(220,200,180)),C(8,4,2,(180,160,140)),
             R(4,6,8,1,(220,200,180)),R(4,8,8,1,(140,120,100))]),
    buff_ids=(31,32), buff_params_list=((0,),(0,)), buff_durations=(6.0,6.0), break_hp=85))

# ═══════════════════════════════════════════════════════
# 环境/移动挑战 续
# ═══════════════════════════════════════════════════════

add(BlockType(0, "bouncy_mushroom", "弹跳蘑菇", is_solid=True,
    color=(255,120,80),
    pattern=("vector",(G,G),[F(180,140,100),R(5,12,6,4,(220,180,140)),
             R(6,6,4,8,(255,120,80)),C(8,6,3,(255,180,140)),
             C(6,4,1,(255,220,180)),C(10,4,1,(255,220,180))]),
    buff_ids=(4,), buff_params_list=((50,),), buff_durations=(5.0,),
    bounce=(0,22), break_hp=35))

add(BlockType(0, "wind_tunnel", "风之隧道", is_solid=False, space_f=1.0,
    color=(190,210,230),
    pattern=("vector",(G,G),[F(190,210,230),R(0,4,16,2,(210,230,250)),
             R(0,10,16,2,(210,230,250)),R(4,3,2,10,(200,220,240)),
             R(10,3,2,10,(200,220,240))]),
    buff_ids=(13,53), buff_params_list=((0,),(0,)), buff_durations=(4.0,4.0),
    special="wind", special_data=(15,10), break_hp=40))

add(BlockType(0, "heavy_anchor", "重锚", is_solid=True,
    color=(100,90,110),
    pattern=("vector",(G,G),[F(100,90,110),R(4,1,8,14,(140,130,150)),
             R(2,4,12,2,(130,120,140)),R(2,12,12,2,(130,120,140)),
             R(6,6,4,4,(120,110,130)),C(8,15,3,(160,150,170))]),
    buff_ids=(54,27), buff_params_list=((0,),(0,)), buff_durations=(10.0,10.0), break_hp=130))

add(BlockType(0, "lightweight_cloud", "轻云", is_solid=False, space_f=1.0,
    color=(230,235,245),
    pattern=("vector",(G,G),[F(230,235,245),C(8,8,6,(245,248,252)),
             C(5,7,3,(245,248,252)),C(11,7,3,(245,248,252)),
             C(8,5,4,(245,248,252)),R(4,8,8,6,(238,242,248))]),
    buff_ids=(13,4), buff_params_list=((0,),(30,)), buff_durations=(6.0,6.0), break_hp=15))

add(BlockType(0, "climbing_vine_wall", "攀藤壁", is_solid=False, climbable=True,
    color=(80,160,60),
    pattern=("vector",(G,G),[F(80,160,60),R(4,0,3,16,(100,190,80)),
             R(10,0,3,14,(100,190,80)),R(6,2,2,12,(90,175,70)),
             R(5,5,6,1,(120,200,100)),R(5,10,6,1,(120,200,100))]),
    buff_ids=(5,), buff_params_list=((0,),), buff_durations=(8.0,),
    k_stamina=0.6, break_hp=25))

add(BlockType(0, "swift_current", "激流", is_solid=False, space_f=0.98, swim_f=6.0,
    color=(80,160,240),
    pattern=("vector",(G,G),[F(80,160,240),R(0,3,16,2,(120,190,255)),
             R(0,8,16,2,(120,190,255)),R(0,13,16,1,(100,175,245)),
             R(4,1,2,14,(100,180,250)),R(10,1,2,14,(100,180,250))]),
    buff_ids=(3,), buff_params_list=((40,),), buff_durations=(3.0,), break_hp=999))

# ═══════════════════════════════════════════════════════
# 战斗辅助 续
# ═══════════════════════════════════════════════════════

add(BlockType(0, "vampiric_altar", "吸血祭坛", is_solid=True, light_level=2,
    color=(140,20,30),
    pattern=("vector",(G,G),[F(140,20,30),C(8,8,5,(190,50,60)),C(8,8,3,(110,15,20)),
             R(5,6,6,4,(170,35,45)),R(7,5,2,6,(160,25,35)),
             C(8,8,1,(255,100,100))]),
    buff_ids=(11,47), buff_params_list=((20,),(0,)), buff_durations=(10.0,10.0), break_hp=70))

add(BlockType(0, "stoneskin_pillar", "石肤之柱", is_solid=True, light_level=1,
    color=(150,145,140),
    pattern=("vector",(G,G),[F(150,145,140),R(5,1,6,14,(190,185,180)),
             R(4,2,8,2,(210,205,200)),R(4,13,8,2,(210,205,200)),
             R(6,4,4,8,(170,165,160))]),
    buff_ids=(39,44), buff_params_list=((0,),(0,)), buff_durations=(18.0,8.0), break_hp=160))

add(BlockType(0, "windblade_forge", "风刃锻台", is_solid=True, light_level=3,
    color=(180,190,210),
    pattern=("vector",(G,G),[F(180,190,210),R(5,2,6,12,(210,220,240)),
             R(3,4,2,8,(200,210,230)),R(11,4,2,8,(200,210,230)),
             C(8,8,3,(230,240,255)),C(8,8,1,(255,255,255))]),
    buff_ids=(53,3), buff_params_list=((0,),(50,)), buff_durations=(10.0,10.0), break_hp=80))

add(BlockType(0, "fortress_rune", "要塞符文", is_solid=True, light_level=3,
    color=(200,180,120),
    pattern=("vector",(G,G),[F(200,180,120),C(8,8,6,(230,210,150)),C(8,8,4,(180,160,100)),
             R(4,7,8,2,(240,220,160)),R(7,4,2,8,(240,220,160)),
             R(3,3,10,10,(210,190,130))]),
    buff_ids=(7,40), buff_params_list=((0,),(0,)), buff_durations=(15.0,15.0), break_hp=140))

add(BlockType(0, "shadow_slip_gate", "暗影步之门", is_solid=True, light_level=0,
    color=(40,30,60),
    pattern=("vector",(G,G),[F(40,30,60),C(8,8,6,(70,60,90)),C(8,8,3,(25,15,45)),
             R(6,6,4,4,(55,45,75)),R(6,2,4,12,(50,40,70))]),
    buff_ids=(38,53), buff_params_list=((0,),(0,)), buff_durations=(8.0,8.0),
    special="teleport", special_data=(0,0), break_hp=90))

# ═══════════════════════════════════════════════════════
# 元素复合 续
# ═══════════════════════════════════════════════════════

add(BlockType(0, "steam_vent", "蒸汽喷口", is_solid=False, space_f=0.96, climbable=False,
    color=(200,200,210),
    pattern=("vector",(G,G),[F(200,200,210),C(8,4,4,(225,225,235)),C(8,4,2,(245,245,250)),
             R(5,8,6,6,(215,215,225)),C(6,10,2,(230,230,240)),C(10,10,2,(230,230,240))]),
    buff_ids=(46,15), buff_params_list=((0,),(0,)), buff_durations=(4.0,4.0),
    special="wind", special_data=(0,12), break_hp=40))

add(BlockType(0, "volcanic_vent", "火山喷口", is_solid=False, space_f=0.95,
    color=(200,60,20), light_level=4, damage_ps=15,
    pattern=("vector",(G,G),[F(200,60,20),C(8,6,5,(240,100,50)),C(8,6,3,(255,160,80)),
             R(4,9,8,5,(180,40,15)),C(6,8,2,(255,200,120)),C(10,8,2,(255,200,120))]),
    buff_ids=(16,27), buff_params_list=((12,),(0,)), buff_durations=(6.0,6.0),
    special="wind", special_data=(0,25), break_hp=80))

add(BlockType(0, "crystal_cavern_wall", "晶洞壁", is_solid=True, light_level=4,
    color=(100,80,160),
    pattern=("vector",(G,G),[F(100,80,160),R(2,3,4,5,(140,120,200)),
             R(10,4,3,4,(140,120,200)),R(5,8,6,4,(130,110,190)),
             C(4,4,2,(180,160,240)),C(13,6,1,(180,160,240)),C(7,10,2,(180,160,240))]),
    buff_ids=(50,41), buff_params_list=((0,),(0,)), buff_durations=(12.0,8.0), break_hp=100))

add(BlockType(0, "quicksand", "流沙", is_solid=False, space_f=0.93, swim_f=1.5,
    color=(200,180,130),
    pattern=("vector",(G,G),[F(200,180,130),R(0,5,16,2,(180,160,110)),
             R(0,10,16,1,(180,160,110)),R(2,2,4,3,(190,170,120)),
             R(10,12,5,3,(190,170,120)),C(6,14,2,(180,160,110))]),
    buff_ids=(22,21), buff_params_list=((40,),(0,)), buff_durations=(5.0,5.0),
    damage_ps=5, break_hp=999))

add(BlockType(0, "coral_reef_sharp", "锐利珊瑚礁", is_solid=True, damage_ps=12,
    color=(240,100,120),
    pattern=("vector",(G,G),[F(240,100,120),R(4,3,3,7,(255,140,160)),
             R(10,2,2,8,(255,140,160)),R(7,5,3,6,(250,120,140)),
             C(5,5,2,(255,180,190)),C(11,4,1,(255,180,190)),C(8,8,2,(255,180,190))]),
    buff_ids=(17,46), buff_params_list=((2,),(0,)), buff_durations=(4.0,4.0), break_hp=45))

# ═══════════════════════════════════════════════════════
# 趣味/探索 续
# ═══════════════════════════════════════════════════════

add(BlockType(0, "mirage_veil", "幻象面纱", is_solid=False, space_f=1.0,
    color=(180,190,210),
    pattern=("vector",(G,G),[F(180,190,210),R(2,4,12,8,(200,210,230)),
             C(5,7,3,(190,200,220)),C(11,8,3,(190,200,220)),
             C(8,5,2,(210,220,240)),R(4,6,8,4,(190,200,220))]),
    buff_ids=(38,23), buff_params_list=((0,),(0,)), buff_durations=(6.0,3.0), break_hp=20))

add(BlockType(0, "treasure_mimic", "宝箱怪", is_solid=True, light_level=2,
    color=(200,160,80),
    pattern=("vector",(G,G),[F(200,160,80),R(3,4,10,8,(240,200,120)),
             R(4,5,8,6,(220,180,100)),R(5,7,2,2,(180,140,60)),
             R(9,7,2,2,(180,140,60))]),
    buff_ids=(17,44), buff_params_list=((3,),(2,)), buff_durations=(4.0,4.0),
    special="score", special_data=500, break_hp=50))

add(BlockType(0, "gravity_flip_stone", "重力反转石", is_solid=True, light_level=2,
    color=(160,160,200),
    pattern=("vector",(G,G),[F(160,160,200),C(8,8,5,(190,190,230)),C(8,8,3,(140,140,180)),
             R(7,4,2,8,(180,180,220)),R(4,7,8,2,(180,180,220))]),
    buff_ids=(13,), buff_params_list=((0,),), buff_durations=(5.0,),
    special="catapult", special_data=(0,35), break_hp=60))

add(BlockType(0, "portal_rune_latent", "潜隐传送符文", is_solid=True, light_level=2,
    color=(120,80,200),
    pattern=("vector",(G,G),[F(120,80,200),C(8,8,6,(160,120,240)),C(8,8,4,(100,60,180)),
             C(8,8,2,(180,140,255)),R(5,7,6,2,(140,100,220)),
             R(7,5,2,6,(140,100,220))]),
    buff_ids=(38,50), buff_params_list=((0,),(0,)), buff_durations=(5.0,5.0),
    special="teleport", special_data=(0,0), break_hp=100))

# ═══════════════════════════════════════════════════════
# 攀爬/游泳/飞行关联
# ═══════════════════════════════════════════════════════

add(BlockType(0, "slippery_moss", "滑溜苔藓", is_solid=False, climbable=True, surface_f=1.05,
    color=(100,180,100),
    pattern=("vector",(G,G),[F(100,180,100),R(1,2,14,3,(140,210,140)),
             R(2,7,12,4,(120,200,120)),R(4,13,8,3,(130,190,130)),
             C(5,4,2,(160,220,160)),C(12,9,1,(160,220,160)),C(8,14,2,(160,220,160))]),
    buff_ids=(42,), buff_params_list=((0,),), buff_durations=(4.0,), break_hp=20))

add(BlockType(0, "stamina_sap_vine", "吸力藤", is_solid=False, climbable=True,
    color=(130,90,140),
    pattern=("vector",(G,G),[F(130,90,140),R(4,0,3,16,(160,120,170)),
             R(9,0,3,13,(160,120,170)),R(6,3,2,10,(145,105,155)),
             R(5,6,6,1,(150,110,160)),R(5,9,6,1,(150,110,160))]),
    buff_ids=(18,19), buff_params_list=((2.0,),(30,)), buff_durations=(5.0,5.0),
    k_stamina=1.6, break_hp=25))

add(BlockType(0, "buoyant_kelp", "浮力海藻", is_solid=False, space_f=0.97, swim_f=8.0,
    color=(60,180,120),
    pattern=("vector",(G,G),[F(60,180,120),R(3,1,3,14,(80,210,140)),
             R(10,1,3,12,(80,210,140)),R(2,4,12,1,(100,220,160)),
             R(1,8,14,1,(100,220,160)),R(2,12,12,1,(100,220,160))]),
    buff_ids=(3,), buff_params_list=((30,),), buff_durations=(3.0,), break_hp=15))

add(BlockType(0, "drowning_depth", "溺水深渊", is_solid=False, space_f=0.99, swim_f=0.5,
    color=(20,60,120),
    pattern=("vector",(G,G),[F(20,60,120),R(0,3,16,1,(40,80,150)),
             R(0,8,16,1,(30,70,140)),R(0,13,16,1,(40,80,150)),
             C(6,6,2,(60,100,170)),C(11,11,2,(60,100,170))]),
    buff_ids=(27,54), buff_params_list=((0,),(0,)), buff_durations=(4.0,4.0), break_hp=999))

print(f'Generated {len(BUFF_BLOCKS)} hand-designed buff blocks (IDs {min(BUFF_BLOCKS.keys())}-{max(BUFF_BLOCKS.keys())})')
