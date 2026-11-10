"""Shared interface constants (editable data will be loaded separately)."""
GAME_NAME_CN = "像素漫游者"
GAME_NAME_EN = "Pixel Roamer"
GAME_DEV = "浪兮"
FONT56 = 56
FONT40 = 40
FONT34 = 34
FONT28 = 28
FONT24 = 24
FONT20 = 20
PAGE_DEV = 0
PAGE_INIT = 1
PAGE_HOME = 2
PAGE_WORLD = 3
PAGE_INFINITE_WORLD = 4
PAGE_SETTING = 5
BAR_X, BAR_Y = 24, 16
BAR_W, BAR_H = 280, 32
BAR_TEXT_H = 22                  # 文字高度（用于垂直居中）
BORDER_R = 6
PAD = 4
BAR_GAP = 5                     # 血条与体力条间距
_FPS_OPTIONS = [30, 60, 90, 120, 150, 180, 210, 240]
_SETTING_ROWS = 4  # 0:FPS  1:自动检测  2:音效音量  3:音乐音量
_EDITABLE_FIELDS = [
    # ---- World 属性 ----
    ("world.gravity",        "重力",               "float", -6.5,    0.5),
    ("world.mode",           "游戏模式",           "str",   "free",    ["free", "explore", "score_timed", "score_target"]),
    ("world.lives",          "复活次数(0=无限)",    "int",   0,        1),
    ("world.score_goal",     "积分目标",           "int",   100,      50),
    ("world.time_limit",     "时间限制(秒,0=无限)",  "float", 0.0,      30.0),
    ("world.music",          "背景音乐(文件名)",     "str",   "",       None),
    ("world.loop_x",         "X轴循环",            "bool",  False,    None),
    ("world.loop_y",         "Y轴循环",            "bool",  False,    None),
    ("world.edge_behavior",  "边界行为",           "str",   "solid",  ["solid", "void"]),
    ("world.view_blocks_h",  "视野(格高)",         "float", 15.0,     1.0),
    ("world.void_limit",     "虚空边界距离",       "int",   20,       5),
    ("world.fill_color",     "背景填充色(R,G,B)",   "str",  "30,30,30", None),
    ("world.default_block_id","默认方块ID",        "int",   0,        1),
    # ---- Player 属性 ----
    ("player.hp_max",        "最大血量",           "float", 150.0,    10.0),
    ("player.v_max",         "最大速度",           "float", 36.5,     1.0),
    ("player.v_jump",        "跳跃速度",           "float", 11.5,     1.0),
    ("player.stamina_max",   "最大体力",           "float", 200.0,    10.0),
    ("player.phys_atk",      "物理攻击",           "float", 10.0,     5.0),
    ("player.magic_atk",     "魔法攻击",           "float", 0.0,      5.0),
    ("player.phys_res",      "物理抗性",           "float", 0.0,      5.0),
    ("player.magic_res",     "魔法抗性",           "float", 0.0,      5.0),
    ("player.phys_pen",      "物理穿透",           "float", 0.0,      5.0),
    ("player.magic_pen",     "魔法穿透",           "float", 0.0,      5.0),
    ("player.k_res",         "抗性系数",           "float", 150.0,    10.0),
    ("player.dr",            "减伤率",             "float", 0.0,      0.05),
    ("player.f_x",           "X轴摩擦系数",        "float", 0.985,    0.005),
    ("player.f_y",           "Y轴摩擦系数",        "float", 1.0,      0.005),
    ("player.shield",        "初始护盾",           "float", 0.0,      5.0),
    ("player.w",             "玩家宽度",           "float", 0.8,      0.1),
    ("player.h",             "玩家高度",           "float", 1.8,      0.1),
    ("player.costume_id",    "时  装",            "int",   1,        1),
]
