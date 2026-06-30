"""
Buff 数据定义 — 第一期 35 个 buff
"""
from buff_system import BuffType, register, CAT_POSITIVE, CAT_NEUTRAL, CAT_NEGATIVE

# ============================================================
# 有益 Buff
# ============================================================
register(BuffType(
    id=1, name="regen", name2="恢复", category=CAT_POSITIVE,
    desc="每秒恢复 {0} 点生命值",
    icon=("vector", (12, 12), [
        ("fill", (255, 120, 150)),
        ("rect", 2, 2, 8, 8, (255, 200, 210)),
        ("rect", 5, 3, 2, 6, (255, 60, 100)),
    ]),
    max_stacks=3, tick="regen",
))

register(BuffType(
    id=2, name="shield_regen", name2="护佑", category=CAT_POSITIVE,
    desc="每秒获得 {0} 点护盾",
    icon=("vector", (12, 12), [
        ("fill", (180, 210, 255)),
        ("rect", 2, 2, 8, 8, (220, 240, 255)),
        ("rect", 5, 1, 2, 10, (140, 180, 240)),
    ]),
    max_stacks=3, tick="shield_regen",
))

register(BuffType(
    id=3, name="swiftness", name2="迅捷", category=CAT_POSITIVE,
    desc="移动速度 +{0}%",
    icon=("vector", (12, 12), [
        ("fill", (100, 255, 150)),
        ("rect", 2, 2, 8, 8, (180, 255, 200)),
        ("rect", 6, 4, 3, 4, (50, 200, 100)),
    ]),
    max_stacks=2, tick="swiftness",
))

register(BuffType(
    id=4, name="leaping", name2="轻身", category=CAT_POSITIVE,
    desc="跳跃高度 +{0}%",
    icon=("vector", (12, 12), [
        ("fill", (255, 220, 100)),
        ("rect", 2, 6, 8, 4, (255, 250, 180)),
        ("rect", 5, 2, 2, 6, (240, 180, 40)),
    ]),
    max_stacks=2, tick="leaping",
))

register(BuffType(
    id=5, name="vigor", name2="活力", category=CAT_POSITIVE,
    desc="体力恢复速度 +{0}%",
    icon=("vector", (12, 12), [
        ("fill", (255, 200, 60)),
        ("rect", 2, 3, 3, 6, (255, 240, 140)),
        ("rect", 7, 3, 3, 6, (255, 240, 140)),
    ]),
    max_stacks=2, tick="vigor",
))

register(BuffType(
    id=6, name="endurance", name2="坚忍", category=CAT_POSITIVE,
    desc="体力消耗 -{0}%",
    icon=("vector", (12, 12), [
        ("fill", (200, 160, 80)),
        ("rect", 2, 2, 8, 8, (240, 210, 140)),
        ("rect", 5, 3, 2, 6, (160, 120, 50)),
    ]),
    max_stacks=1, tick="endurance",
))

register(BuffType(
    id=7, name="fortify", name2="坚守", category=CAT_POSITIVE,
    desc="受到伤害 -{0}%",
    icon=("vector", (12, 12), [
        ("fill", (160, 180, 200)),
        ("rect", 2, 2, 8, 8, (210, 220, 240)),
        ("rect", 4, 1, 4, 10, (120, 140, 180)),
    ]),
    max_stacks=2, tick="fortify",
))

register(BuffType(
    id=8, name="clarity", name2="清明", category=CAT_POSITIVE,
    desc="免疫方向反转和视野干扰",
    icon=("vector", (12, 12), [
        ("fill", (200, 230, 255)),
        ("circle", 6, 6, 4, (240, 250, 255)),
        ("circle", 6, 6, 2, (160, 200, 240)),
    ]),
    max_stacks=1, tick="clarity",
    conflicts=(23, 24, 25),  # 清除反向、失明、视野受限
))

register(BuffType(
    id=9, name="fire_resist", name2="耐火", category=CAT_POSITIVE,
    desc="免疫火焰和熔岩伤害",
    icon=("vector", (12, 12), [
        ("fill", (255, 150, 60)),
        ("rect", 2, 2, 8, 3, (255, 220, 120)),
        ("rect", 2, 6, 8, 4, (255, 100, 20)),
    ]),
    max_stacks=1, tick="fire_resist",
    cleanup_by=(15,),  # 遇水时被清除（由着火buff驱动）
))

register(BuffType(
    id=10, name="thornmail", name2="荆棘", category=CAT_POSITIVE,
    desc="反弹 {0}% 受到的伤害",
    icon=("vector", (12, 12), [
        ("fill", (180, 200, 100)),
        ("rect", 2, 2, 8, 8, (220, 240, 160)),
        ("rect", 4, 1, 1, 6, (140, 170, 60)),
        ("rect", 7, 1, 1, 6, (140, 170, 60)),
    ]),
    max_stacks=3, tick="thornmail",
))

register(BuffType(
    id=11, name="lifesteal", name2="嗜血", category=CAT_POSITIVE,
    desc="造成伤害时回复其 {0}% 为生命",
    icon=("vector", (12, 12), [
        ("fill", (200, 40, 40)),
        ("rect", 2, 4, 8, 5, (255, 120, 100)),
        ("circle", 6, 6, 2, (180, 20, 20)),
    ]),
    max_stacks=3, tick="lifesteal",
))

register(BuffType(
    id=12, name="cleansing", name2="净化", category=CAT_POSITIVE,
    desc="每 {0} 秒移除一个负面效果",
    icon=("vector", (12, 12), [
        ("fill", (255, 255, 200)),
        ("circle", 6, 6, 5, (255, 255, 240)),
        ("circle", 6, 6, 2, (240, 240, 140)),
    ]),
    max_stacks=1, tick="cleansing",
))

register(BuffType(
    id=13, name="feather", name2="轻羽", category=CAT_POSITIVE,
    desc="重力降低 {0}%",
    icon=("vector", (12, 12), [
        ("fill", (200, 210, 230)),
        ("rect", 3, 5, 6, 4, (240, 245, 255)),
        ("rect", 4, 2, 4, 2, (180, 190, 220)),
    ]),
    max_stacks=1, tick="feather",
))

# ============================================================
# 中性 Buff
# ============================================================
register(BuffType(
    id=14, name="magnetic", name2="磁引", category=CAT_NEUTRAL,
    desc="自动吸引附近掉落物",
    icon=("vector", (12, 12), [
        ("fill", (180, 170, 200)),
        ("rect", 2, 2, 8, 8, (220, 210, 240)),
        ("rect", 3, 3, 6, 1, (140, 130, 180)),
        ("rect", 3, 8, 6, 1, (140, 130, 180)),
    ]),
    max_stacks=1, tick="magnetic",
))

register(BuffType(
    id=15, name="soaked", name2="浸湿", category=CAT_NEUTRAL,
    desc="处于潮湿状态（清除着火）",
    icon=("vector", (12, 12), [
        ("fill", (100, 160, 255)),
        ("rect", 2, 4, 8, 6, (160, 210, 255)),
    ]),
    max_stacks=1, tick="soaked",
    conflicts=(16,),  # 移除着火
))

# ============================================================
# 有害 Buff (Debuff)
# ============================================================
register(BuffType(
    id=16, name="burning", name2="着火", category=CAT_NEGATIVE,
    desc="每秒损失 {0} 点生命值，遇水清除",
    icon=("vector", (12, 12), [
        ("fill", (255, 120, 20)),
        ("rect", 2, 2, 3, 4, (255, 200, 60)),
        ("rect", 7, 3, 2, 5, (255, 180, 40)),
        ("rect", 4, 4, 3, 3, (255, 80, 10)),
    ]),
    max_stacks=3, tick="burning",
    cleanup_by=(15,),  # 浸湿时清除
))

register(BuffType(
    id=17, name="bleeding", name2="流血", category=CAT_NEGATIVE,
    desc="每秒损失当前生命值的 {0}%",
    icon=("vector", (12, 12), [
        ("fill", (200, 30, 30)),
        ("circle", 6, 6, 3, (240, 80, 80)),
        ("circle", 4, 8, 2, (160, 15, 15)),
        ("circle", 8, 4, 1, (220, 50, 50)),
    ]),
    max_stacks=5, tick="bleeding",
))

register(BuffType(
    id=18, name="weakened", name2="脱力", category=CAT_NEGATIVE,
    desc="体力消耗速度 ×{0}",
    icon=("vector", (12, 12), [
        ("fill", (180, 150, 100)),
        ("rect", 2, 2, 8, 8, (220, 190, 140)),
        ("rect", 5, 3, 2, 6, (140, 110, 60)),
    ]),
    max_stacks=1, tick="weakened",
))

register(BuffType(
    id=19, name="fatigue", name2="疲倦", category=CAT_NEGATIVE,
    desc="体力恢复速度 -{0}%",
    icon=("vector", (12, 12), [
        ("fill", (140, 130, 170)),
        ("rect", 2, 2, 8, 8, (180, 170, 210)),
        ("rect", 4, 4, 4, 4, (100, 90, 140)),
    ]),
    max_stacks=2, tick="fatigue",
))

register(BuffType(
    id=20, name="grievous_wound", name2="重伤", category=CAT_NEGATIVE,
    desc="受到的治疗效果 -{0}%",
    icon=("vector", (12, 12), [
        ("fill", (160, 60, 60)),
        ("rect", 2, 2, 8, 8, (210, 120, 120)),
        ("rect", 4, 3, 4, 6, (120, 30, 30)),
    ]),
    max_stacks=2, tick="grievous_wound",
))

register(BuffType(
    id=21, name="rooted", name2="定身", category=CAT_NEGATIVE,
    desc="无法左右移动",
    icon=("vector", (12, 12), [
        ("fill", (120, 140, 100)),
        ("rect", 2, 4, 8, 4, (180, 200, 160)),
        ("rect", 1, 5, 10, 2, (80, 100, 60)),
    ]),
    max_stacks=1, tick="rooted",
))

register(BuffType(
    id=22, name="slowed", name2="缓步", category=CAT_NEGATIVE,
    desc="移动速度 -{0}%",
    icon=("vector", (12, 12), [
        ("fill", (160, 180, 200)),
        ("rect", 2, 3, 8, 6, (200, 220, 240)),
        ("rect", 4, 5, 4, 2, (120, 140, 170)),
    ]),
    max_stacks=3, tick="slowed",
))

register(BuffType(
    id=23, name="reversed", name2="反向", category=CAT_NEGATIVE,
    desc="操作方向左右反转",
    icon=("vector", (12, 12), [
        ("fill", (200, 180, 220)),
        ("rect", 2, 2, 4, 8, (240, 220, 250)),
        ("rect", 6, 2, 4, 8, (160, 140, 200)),
        ("rect", 5, 3, 2, 6, (220, 200, 240)),
    ]),
    max_stacks=1, tick="reversed",
))

register(BuffType(
    id=24, name="blinded", name2="失明", category=CAT_NEGATIVE,
    desc="屏幕变亮黄色，仅能看清主角",
    icon=("vector", (12, 12), [
        ("fill", (255, 240, 20)),
        ("rect", 2, 2, 8, 8, (255, 250, 150)),
        ("rect", 5, 3, 2, 6, (240, 220, 10)),
    ]),
    max_stacks=1, tick="blinded",
))

register(BuffType(
    id=25, name="narrow_vision", name2="视野受限", category=CAT_NEGATIVE,
    desc="视野缩小为半径 {0} 格",
    icon=("vector", (12, 12), [
        ("fill", (20, 20, 30)),
        ("circle", 6, 6, 4, (80, 80, 100)),
        ("circle", 6, 6, 2, (150, 150, 170)),
    ]),
    max_stacks=1, tick="narrow_vision",
))

register(BuffType(
    id=26, name="armor_break", name2="破甲", category=CAT_NEGATIVE,
    desc="无视所有免伤属性",
    icon=("vector", (12, 12), [
        ("fill", (200, 180, 100)),
        ("rect", 2, 2, 8, 2, (240, 220, 140)),
        ("rect", 4, 5, 4, 5, (160, 140, 60)),
    ]),
    max_stacks=1, tick="armor_break",
))

register(BuffType(
    id=27, name="grounded", name2="压制", category=CAT_NEGATIVE,
    desc="无法跳跃",
    icon=("vector", (12, 12), [
        ("fill", (160, 140, 80)),
        ("rect", 2, 7, 8, 3, (200, 180, 120)),
        ("rect", 5, 4, 2, 3, (120, 100, 50)),
    ]),
    max_stacks=1, tick="grounded",
))

register(BuffType(
    id=28, name="stunned", name2="晕眩", category=CAT_NEGATIVE,
    desc="无法移动、跳跃、交互",
    icon=("vector", (12, 12), [
        ("fill", (200, 200, 100)),
        ("circle", 6, 6, 4, (240, 240, 180)),
        ("circle", 6, 6, 1, (160, 160, 60)),
    ]),
    max_stacks=1, tick="stunned",
))

register(BuffType(
    id=29, name="pierced", name2="穿甲", category=CAT_NEGATIVE,
    desc="伤害优先消耗血量，无视护盾",
    icon=("vector", (12, 12), [
        ("fill", (220, 100, 100)),
        ("rect", 2, 2, 8, 2, (255, 180, 160)),
        ("rect", 3, 5, 6, 5, (180, 60, 50)),
    ]),
    max_stacks=1, tick="pierced",
))

register(BuffType(
    id=30, name="disarmed", name2="缴械", category=CAT_NEGATIVE,
    desc="无法使用道具",
    icon=("vector", (12, 12), [
        ("fill", (180, 160, 140)),
        ("rect", 2, 4, 8, 4, (220, 200, 180)),
        ("rect", 5, 2, 2, 8, (140, 120, 100)),
    ]),
    max_stacks=1, tick="disarmed",
))

register(BuffType(
    id=31, name="interfered", name2="干扰", category=CAT_NEGATIVE,
    desc="无法使用技能",
    icon=("vector", (12, 12), [
        ("fill", (160, 140, 200)),
        ("rect", 2, 2, 8, 8, (200, 180, 240)),
        ("circle", 6, 6, 2, (120, 100, 170)),
    ]),
    max_stacks=1, tick="interfered",
))

register(BuffType(
    id=32, name="silenced_debuff", name2="沉默", category=CAT_NEGATIVE,
    desc="无法交互",
    icon=("vector", (12, 12), [
        ("fill", (120, 120, 150)),
        ("rect", 2, 2, 8, 8, (170, 170, 200)),
        ("rect", 5, 4, 2, 4, (80, 80, 120)),
    ]),
    max_stacks=1, tick="silenced_debuff",
))

register(BuffType(
    id=33, name="hopping", name2="跳跃锁定", category=CAT_NEGATIVE,
    desc="只能跳跃攀爬，无法水平移动",
    icon=("vector", (12, 12), [
        ("fill", (200, 180, 140)),
        ("rect", 2, 2, 8, 2, (240, 220, 180)),
        ("rect", 5, 5, 2, 5, (160, 140, 100)),
    ]),
    max_stacks=1, tick="hopping",
))

register(BuffType(
    id=34, name="physical_immune", name2="物理免疫", category=CAT_POSITIVE,
    desc="免疫物理伤害",
    icon=("vector", (12, 12), [
        ("fill", (200, 160, 100)),
        ("rect", 2, 2, 8, 8, (240, 210, 160)),
        ("rect", 4, 3, 4, 6, (160, 120, 60)),
    ]),
    max_stacks=1, tick="physical_immune",
))

register(BuffType(
    id=35, name="magic_immune", name2="法术免疫", category=CAT_POSITIVE,
    desc="免疫法术伤害",
    icon=("vector", (12, 12), [
        ("fill", (140, 160, 240)),
        ("rect", 2, 2, 8, 8, (190, 210, 255)),
        ("rect", 4, 3, 4, 6, (100, 120, 210)),
    ]),
    max_stacks=1, tick="magic_immune",
))

register(BuffType(
    id=36, name="full_immune", name2="完全免疫", category=CAT_POSITIVE,
    desc="免疫所有伤害（包括环境伤害）",
    icon=("vector", (12, 12), [
        ("fill", (255, 255, 200)),
        ("circle", 6, 6, 5, (255, 255, 240)),
        ("circle", 6, 6, 2, (240, 240, 100)),
    ]),
    max_stacks=1, tick="full_immune",
))

register(BuffType(
    id=37, name="double_jump", name2="二段跳", category=CAT_POSITIVE,
    desc="可在空中再跳跃一次",
    icon=("vector", (12, 12), [
        ("fill", (100, 200, 255)),
        ("rect", 3, 3, 6, 6, (180, 240, 255)),
        ("rect", 5, 1, 2, 4, (60, 160, 240)),
    ]),
    max_stacks=1, tick="double_jump",
))
