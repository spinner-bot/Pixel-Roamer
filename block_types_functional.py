"""
功能方块扩展包 — 30种特殊效果方块
ID 330-359
"""
from block_type import BlockType

FUNCTIONAL_BLOCKS = {
    # ============================================================
    # 弹射类 — 施加爆发性速度
    # ============================================================
    330: BlockType(330, "catapult_up", "弹射板(上)", is_solid=True,
                   color=(255, 180, 50), break_hp=80,
                   special="catapult", special_data=(0, 30),
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 180, 50)),
                       ("rect", 1, 1, 14, 14, (255, 220, 100)),
                       ("rect", 4, 6, 8, 4, (255, 140, 30)),
                   ])),

    331: BlockType(331, "catapult_right", "弹射板(右)", is_solid=True,
                   color=(50, 220, 100), break_hp=80,
                   special="catapult", special_data=(30, 5),
                   pattern=("vector", (16, 16), [
                       ("fill", (50, 220, 100)),
                       ("rect", 1, 1, 14, 14, (100, 255, 150)),
                       ("rect", 6, 4, 4, 8, (30, 180, 70)),
                   ])),

    332: BlockType(332, "catapult_left", "弹射板(左)", is_solid=True,
                   color=(50, 180, 255), break_hp=80,
                   special="catapult", special_data=(-30, 5),
                   pattern=("vector", (16, 16), [
                       ("fill", (50, 180, 255)),
                       ("rect", 1, 1, 14, 14, (120, 210, 255)),
                       ("rect", 6, 4, 4, 8, (30, 140, 220)),
                   ])),

    # ============================================================
    # 冲刺类 — 水平爆发
    # ============================================================
    333: BlockType(333, "dash_right", "冲刺板(右)", is_solid=True,
                   color=(200, 100, 255), break_hp=80,
                   special="dash", special_data=40,
                   pattern=("vector", (16, 16), [
                       ("fill", (200, 100, 255)),
                       ("rect", 0, 2, 16, 12, (230, 150, 255)),
                       ("rect", 8, 4, 4, 8, (160, 60, 220)),
                   ])),

    334: BlockType(334, "dash_left", "冲刺板(左)", is_solid=True,
                   color=(255, 150, 80), break_hp=80,
                   special="dash", special_data=-40,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 150, 80)),
                       ("rect", 0, 2, 16, 12, (255, 190, 130)),
                       ("rect", 4, 4, 4, 8, (220, 100, 40)),
                   ])),

    # ============================================================
    # 冻结 — 清空速度
    # ============================================================
    335: BlockType(335, "freeze_rune", "冻结符文", is_solid=True,
                   color=(150, 220, 255), break_hp=60, light_level=2,
                   special="freeze", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (150, 220, 255)),
                       ("rect", 2, 2, 12, 12, (200, 240, 255)),
                       ("rect", 5, 1, 6, 14, (100, 200, 250)),
                       ("rect", 1, 5, 14, 6, (100, 200, 250)),
                   ])),

    # ============================================================
    # 恢复类
    # ============================================================
    336: BlockType(336, "life_spring", "生命之泉", is_solid=True,
                   color=(255, 100, 180), break_hp=100, light_level=3,
                   special="full_heal", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 100, 180)),
                       ("circle", 8, 7, 5, (255, 180, 220)),
                       ("circle", 8, 7, 2, (255, 60, 140)),
                   ])),

    337: BlockType(337, "stamina_fount", "活力之泉", is_solid=True,
                   color=(255, 200, 60), break_hp=100, light_level=3,
                   special="full_stamina", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 200, 60)),
                       ("rect", 3, 1, 10, 14, (255, 240, 140)),
                       ("rect", 5, 3, 6, 10, (255, 180, 20)),
                   ])),

    # ============================================================
    # 环境效果 — 持续
    # ============================================================
    338: BlockType(338, "magnetic_ore", "磁矿石", is_solid=True,
                   color=(120, 120, 140), break_hp=100,
                   special="magnetic", special_data=8,
                   pattern=("vector", (16, 16), [
                       ("fill", (120, 120, 140)),
                       ("rect", 4, 4, 4, 8, (180, 180, 200)),
                       ("rect", 8, 4, 4, 8, (180, 180, 200)),
                   ])),

    339: BlockType(339, "gravity_well", "重力井", is_solid=True,
                   color=(60, 20, 80), break_hp=120, light_level=1,
                   special="gravity_well", special_data=25,
                   pattern=("vector", (16, 16), [
                       ("fill", (60, 20, 80)),
                       ("circle", 8, 8, 6, (40, 10, 60)),
                       ("circle", 8, 8, 3, (100, 40, 120)),
                   ])),

    340: BlockType(340, "wind_vent_up", "上升气流", is_solid=False, climbable=False,
                   color=(200, 230, 255), break_hp=40,
                   special="wind", special_data=(0, 15),
                   pattern=("vector", (16, 16), [
                       ("fill", (200, 230, 255)),
                       ("rect", 6, 2, 4, 12, (240, 250, 255)),
                       ("rect", 2, 6, 12, 4, (240, 250, 255)),
                   ])),

    341: BlockType(341, "wind_vent_right", "右向气流", is_solid=False, climbable=False,
                   color=(180, 240, 200), break_hp=40,
                   special="wind", special_data=(15, 0),
                   pattern=("vector", (16, 16), [
                       ("fill", (180, 240, 200)),
                       ("rect", 2, 6, 12, 4, (220, 255, 240)),
                       ("rect", 8, 2, 4, 12, (140, 220, 170)),
                   ])),

    342: BlockType(342, "slow_crystal", "减速水晶", is_solid=True,
                   color=(180, 180, 220), break_hp=60,
                   special="slow_field", special_data=0.4,
                   pattern=("vector", (16, 16), [
                       ("fill", (180, 180, 220)),
                       ("rect", 3, 3, 10, 10, (210, 210, 240)),
                       ("rect", 5, 1, 6, 14, (150, 150, 200)),
                   ])),

    343: BlockType(343, "speed_crystal", "加速水晶", is_solid=True,
                   color=(255, 200, 100), break_hp=60,
                   special="speed", special_data=1.8,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 200, 100)),
                       ("rect", 3, 3, 10, 10, (255, 240, 180)),
                       ("rect", 5, 1, 6, 14, (240, 160, 60)),
                   ])),

    344: BlockType(344, "silence_shrine", "静默圣坛", is_solid=True,
                   color=(80, 60, 140), break_hp=120, light_level=2,
                   special="silence", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (80, 60, 140)),
                       ("rect", 2, 2, 12, 12, (120, 100, 180)),
                       ("rect", 4, 4, 8, 8, (60, 40, 120)),
                       ("circle", 8, 8, 2, (160, 140, 220)),
                   ])),

    345: BlockType(345, "courage_monolith", "勇气石碑", is_solid=True,
                   color=(200, 150, 50), break_hp=150, light_level=2,
                   special="courage", special_data=0.3,
                   pattern=("vector", (16, 16), [
                       ("fill", (200, 150, 50)),
                       ("rect", 1, 1, 14, 14, (240, 200, 100)),
                       ("rect", 3, 3, 10, 10, (180, 120, 30)),
                       ("rect", 7, 1, 2, 14, (220, 180, 80)),
                   ])),

    # ============================================================
    # 伤害/负面
    # ============================================================
    346: BlockType(346, "poison_gas", "毒气", is_solid=False, space_f=1.0, damage_ps=0,
                   color=(140, 255, 60), break_hp=20, light_level=1,
                   special="poison", special_data=20,
                   pattern=("vector", (16, 16), [
                       ("fill", (140, 255, 60)),
                       ("circle", 4, 5, 3, (180, 255, 120)),
                       ("circle", 10, 9, 2, (180, 255, 120)),
                       ("circle", 7, 3, 2, (100, 220, 40)),
                   ])),

    347: BlockType(347, "weakness_smoke", "虚弱之雾", is_solid=False, space_f=1.0,
                   color=(180, 160, 200), break_hp=20,
                   special="weakness", special_data=0.5,
                   pattern=("vector", (16, 16), [
                       ("fill", (180, 160, 200)),
                       ("circle", 6, 6, 4, (210, 190, 230)),
                       ("circle", 3, 10, 3, (150, 130, 180)),
                   ])),

    348: BlockType(348, "berserk_altar", "狂暴祭坛", is_solid=True,
                   color=(200, 30, 30), break_hp=100, light_level=2,
                   special="berserk", special_data=2.5,
                   pattern=("vector", (16, 16), [
                       ("fill", (200, 30, 30)),
                       ("rect", 2, 2, 12, 12, (255, 80, 80)),
                       ("rect", 5, 5, 6, 6, (160, 10, 10)),
                       ("rect", 7, 1, 2, 14, (255, 50, 50)),
                   ])),

    # ============================================================
    # 特殊机制
    # ============================================================
    349: BlockType(349, "phantom_gate", "幻影之门", is_solid=True,
                   color=(100, 180, 220), break_hp=80, light_level=2,
                   special="phantom", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (100, 180, 220)),
                       ("rect", 2, 2, 12, 12, (160, 220, 250)),
                       ("rect", 5, 2, 6, 12, (70, 150, 200)),
                   ])),

    350: BlockType(350, "spawn_anchor", "重生锚点", is_solid=True,
                   color=(255, 220, 100), break_hp=200, light_level=4,
                   special="set_spawn", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 220, 100)),
                       ("circle", 8, 8, 6, (255, 250, 200)),
                       ("rect", 6, 2, 4, 12, (240, 200, 60)),
                       ("rect", 2, 6, 12, 4, (240, 200, 60)),
                   ])),

    351: BlockType(351, "fortune_block", "幸运方块", is_solid=True,
                   color=(255, 215, 0), break_hp=40, light_level=3,
                   special="fortune", special_data=500,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 215, 0)),
                       ("rect", 3, 3, 10, 10, (255, 240, 100)),
                       ("rect", 5, 1, 6, 14, (255, 200, 0)),
                       ("circle", 8, 8, 2, (255, 255, 200)),
                   ])),

    352: BlockType(352, "echo_crystal", "回声水晶", is_solid=True,
                   color=(120, 200, 255), break_hp=60, light_level=2,
                   special="echo", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (120, 200, 255)),
                       ("circle", 8, 7, 4, (180, 230, 255)),
                       ("rect", 6, 3, 4, 10, (80, 170, 240)),
                   ])),

    353: BlockType(353, "confusion_mist", "混乱之雾", is_solid=False, space_f=1.0,
                   color=(220, 180, 255), break_hp=20,
                   special="confusion", special_data=None,
                   pattern=("vector", (16, 16), [
                       ("fill", (220, 180, 255)),
                       ("circle", 5, 6, 4, (240, 210, 255)),
                       ("circle", 10, 9, 3, (200, 150, 240)),
                       ("circle", 8, 4, 2, (240, 210, 255)),
                   ])),

    # ============================================================
    # 控场/辅助
    # ============================================================
    354: BlockType(354, "jump_booster", "跳跃增强器", is_solid=True,
                   color=(100, 255, 150), break_hp=60,
                   special="jump", special_data=1.8,
                   pattern=("vector", (16, 16), [
                       ("fill", (100, 255, 150)),
                       ("rect", 3, 3, 10, 10, (180, 255, 210)),
                       ("rect", 5, 1, 6, 14, (60, 220, 110)),
                   ])),

    355: BlockType(355, "regen_totem", "再生图腾", is_solid=True,
                   color=(80, 200, 100), break_hp=100, light_level=2,
                   special="heal", special_data=40,
                   pattern=("vector", (16, 16), [
                       ("fill", (80, 200, 100)),
                       ("rect", 2, 1, 12, 14, (140, 240, 160)),
                       ("rect", 4, 4, 8, 8, (50, 160, 70)),
                   ])),

    356: BlockType(356, "shield_pylon", "护盾塔", is_solid=True,
                   color=(180, 200, 255), break_hp=150, light_level=3,
                   special="shield", special_data={"amount": 30, "max": 100},
                   pattern=("vector", (16, 16), [
                       ("fill", (180, 200, 255)),
                       ("rect", 2, 2, 12, 12, (220, 235, 255)),
                       ("rect", 6, 1, 4, 14, (140, 170, 240)),
                   ])),

    357: BlockType(357, "warp_rune", "传送符文", is_solid=True,
                   color=(150, 80, 220), break_hp=100, light_level=3,
                   special="teleport", special_data=(0, 0),
                   pattern=("vector", (16, 16), [
                       ("fill", (150, 80, 220)),
                       ("circle", 8, 8, 5, (200, 140, 250)),
                       ("circle", 8, 8, 2, (120, 50, 200)),
                   ])),

    358: BlockType(358, "chaos_rift", "混沌裂隙", is_solid=False,
                   color=(80, 10, 100), break_hp=80, light_level=2,
                   special="ender", special_data=(30, 20),
                   pattern=("vector", (16, 16), [
                       ("fill", (80, 10, 100)),
                       ("circle", 8, 8, 6, (120, 40, 140)),
                       ("circle", 5, 5, 2, (160, 80, 180)),
                       ("circle", 11, 11, 2, (40, 0, 60)),
                   ])),

    # ============================================================
    # 趣味/装饰性
    # ============================================================
    359: BlockType(359, "rainbow_trail", "彩虹小径", is_solid=True,
                   color=(255, 200, 200), break_hp=40, light_level=5,
                   special="speed", special_data=1.3,
                   pattern=("vector", (16, 16), [
                       ("fill", (255, 200, 200)),
                       ("rect", 0, 0, 16, 2, (255, 100, 100)),
                       ("rect", 0, 3, 16, 2, (255, 180, 40)),
                       ("rect", 0, 6, 16, 2, (255, 255, 80)),
                       ("rect", 0, 9, 16, 2, (100, 255, 80)),
                       ("rect", 0, 12, 16, 2, (80, 180, 255)),
                       ("rect", 0, 14, 16, 2, (150, 100, 255)),
                   ])),
}
