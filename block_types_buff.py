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

print(f'Generated {len(BUFF_BLOCKS)} hand-designed buff blocks (IDs {min(BUFF_BLOCKS.keys())}-{max(BUFF_BLOCKS.keys())})')
