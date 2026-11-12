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
from resource_catalog import load_interface

_FPS_OPTIONS, _EDITABLE_FIELDS = load_interface()
_SETTING_ROWS = 4
