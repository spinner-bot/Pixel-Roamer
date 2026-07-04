"""
时装系统：玩家皮肤渲染
每个时装为 16×32 位图（宽×高），统一使用该尺寸设计。
"""
from __future__ import annotations
from typing import Tuple, Dict, Optional
import pygame

# ===================== 颜色常量 =====================
_SKIN      = (255, 205, 165)
_SKIN_D    = (230, 175, 135)
_SKIN_L    = (255, 225, 195)
_WHITE     = (255, 255, 255)
_BLACK     = (25, 22, 28)
_DARK      = (45, 42, 50)
_GRAY      = (130, 125, 135)

# ---- 经典冒险家 ----
_ADV_HAIR   = (130, 85, 40)
_ADV_HAIR_L = (160, 110, 55)
_ADV_SHIRT  = (55, 115, 215)
_ADV_SHIRT_D= (30, 80, 170)
_ADV_PANTS  = (115, 85, 45)
_ADV_PANTS_D= (85, 60, 30)
_ADV_BELT   = (170, 140, 60)
_ADV_BOOT   = (65, 45, 28)

# ---- 暗影忍者 ----
_NIN_PURP  = (50, 18, 60)
_NIN_PURP_M= (70, 30, 85)
_NIN_PURP_L= (90, 45, 110)
_NIN_EYE   = (255, 35, 35)
_NIN_SASH  = (130, 25, 25)
_NIN_WRAP  = (38, 32, 42)
_NIN_SKIN  = (220, 190, 155)

# ---- 星辰法师 ----
_MAG_ROBE   = (45, 85, 205)
_MAG_ROBE_D = (25, 55, 165)
_MAG_ROBE_L = (80, 130, 240)
_MAG_HAT    = (105, 45, 185)
_MAG_STAR   = (255, 235, 60)
_MAG_BEARD  = (225, 220, 210)
_MAG_BEARD_D= (195, 190, 180)
_MAG_BELT   = (180, 150, 80)

# ========================================================================
# 时装位图定义（16×32）
# 每个元素为 (R,G,B) 或 0=透明（渲染时跳过）
# ========================================================================

# ---------- 时装1：经典冒险家 ----------
_COSTUME_ADVENTURER = [
    # Row 0-3: 头发
    [0,0,0,0, _ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR, 0,0,0,0],
    [0,0, _ADV_HAIR,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR_L, 0,0,0],
    [0, _ADV_HAIR,_ADV_HAIR_L,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR, 0,0],
    [ _ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR_L,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR,_ADV_HAIR, 0],
    # Row 4-7: 脸部
    [0, _ADV_HAIR,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_ADV_HAIR, 0],
    [0, _ADV_HAIR,_SKIN,_SKIN,_SKIN_D,_SKIN,_WHITE,_SKIN,_SKIN,_WHITE,_SKIN,_SKIN_D,_SKIN,_SKIN,_ADV_HAIR, 0],
    [0, _ADV_HAIR,_SKIN,_SKIN_D,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN_D,_SKIN,_ADV_HAIR, 0],
    [0, _ADV_HAIR,_SKIN,_SKIN,_SKIN,_SKIN_D,_SKIN,_SKIN,_SKIN,_SKIN_D,_SKIN,_SKIN,_SKIN,_SKIN,_ADV_HAIR, 0],
    # Row 8-15: 身体（衬衫）
    [0,0, _ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT_D, 0,0],
    [0,0, _ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT_D, 0,0],
    [0,0, _ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT_D, 0,0],
    [0,0, _ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT_D,_ADV_SHIRT,_ADV_SHIRT,_ADV_SHIRT_D, 0,0],
    [0,0, _ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT,_ADV_BELT, 0,0],
    [0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0],
    [0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0],
    [0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0],
    # Row 16-19: 腿
    [0,0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0,0],
    [0,0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0,0],
    [0,0,0,0, _ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS, 0,0,0,0],
    [0,0,0,0, _ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS,_ADV_PANTS,_ADV_PANTS_D,_ADV_PANTS_D,_ADV_PANTS_D, 0,0,0,0],
    # Row 20-23: 靴子
    [0,0,0,0, _ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT, 0,0,0,0],
    [0,0,0,0, _ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT,_ADV_BOOT, 0,0,0,0],
    [0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0],
    [0,0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0,0],
    # Row 24-31: 阴影/底部（透明占位）
    [0]*16, [0]*16, [0]*16, [0]*16,
    [0]*16, [0]*16, [0]*16, [0]*16,
]

# ---------- 时装2：暗影忍者 ----------
_COSTUME_NINJA = [
    # Row 0-3: 兜帽
    [0,0,0,0,0, _NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP, 0,0,0,0,0],
    [0,0,0, _NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP, 0,0,0],
    [0,0, _NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M, 0,0],
    [0, _NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP_L,_NIN_PURP_L,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M, 0],
    # Row 4-7: 脸部（蒙面）
    [0, _NIN_WRAP,_NIN_WRAP,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_WRAP,_NIN_WRAP, 0],
    [0, _NIN_WRAP,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_EYE,_NIN_SKIN,_NIN_SKIN,_NIN_EYE,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_WRAP, 0],
    [0, _NIN_WRAP,_NIN_WRAP,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_WRAP,_NIN_WRAP, 0],
    [0, _NIN_PURP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_SKIN,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_PURP, 0],
    # Row 8-15: 身体
    [0,0, _NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP, 0,0],
    [0,0, _NIN_PURP_M,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP_L,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP_L,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP_M, 0,0],
    [0,0, _NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP, 0,0],
    [0,0, _NIN_PURP_M,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP_M,_NIN_PURP,_NIN_PURP_M, 0,0],
    [0,0, _NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH,_NIN_SASH, 0,0],
    [0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_PURP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP,_NIN_PURP,_NIN_WRAP,_NIN_WRAP, 0,0,0],
    [0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP, 0,0,0],
    [0,0,0, _NIN_PURP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_PURP, 0,0,0],
    # Row 16-19: 腿
    [0,0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_PURP,_NIN_WRAP,_NIN_WRAP, 0,0,0,0],
    [0,0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_PURP,_NIN_PURP_M,_NIN_PURP_M,_NIN_PURP,_NIN_WRAP,_NIN_WRAP, 0,0,0,0],
    [0,0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_PURP,_NIN_PURP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP, 0,0,0,0],
    [0,0,0,0, _NIN_PURP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_PURP, 0,0,0,0],
    # Row 20-23: 足部
    [0,0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP, 0,0,0,0],
    [0,0,0,0, _NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP,_NIN_WRAP, 0,0,0,0],
    [0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0],
    [0,0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0,0],
    # Row 24-31: 底部
    [0]*16, [0]*16, [0]*16, [0]*16,
    [0]*16, [0]*16, [0]*16, [0]*16,
]

# ---------- 时装3：星辰法师 ----------
_COSTUME_MAGE = [
    # Row 0-5: 法师帽
    [0,0,0,0,0,0,0, _MAG_HAT,_MAG_HAT, 0,0,0,0,0,0,0],
    [0,0,0,0,0, _MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_HAT, 0,0,0,0,0],
    [0,0,0,0, _MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_HAT,_MAG_HAT,_MAG_HAT, 0,0,0,0],
    [0,0,0, _MAG_HAT,_MAG_HAT,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_HAT,_MAG_HAT, 0,0,0],
    [0,0, _MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_HAT,_MAG_HAT,_MAG_HAT,_MAG_HAT, 0,0],
    [ _MAG_HAT,_MAG_HAT,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_HAT,_MAG_HAT, 0],
    # Row 6-9: 脸部（胡须）
    [0, _MAG_HAT,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_SKIN,_MAG_HAT, 0],
    [0, _MAG_HAT,_SKIN,_SKIN_D,_SKIN,_WHITE,_SKIN,_SKIN,_SKIN,_SKIN,_WHITE,_SKIN,_SKIN_D,_SKIN,_MAG_HAT, 0],
    [0,0, _MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD_D,_SKIN,_SKIN,_SKIN,_SKIN,_MAG_BEARD_D,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD, 0,0],
    [0,0, _MAG_BEARD_D,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD,_MAG_BEARD_D, 0,0],
    # Row 10-15: 身体（法袍）
    [0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0],
    [0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_L,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_L,_MAG_ROBE,_MAG_ROBE_D, 0,0],
    [0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_STAR,_MAG_ROBE,_MAG_ROBE,_MAG_STAR,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0],
    [0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_L,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_L,_MAG_ROBE,_MAG_ROBE_D, 0,0],
    [0,0, _MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT,_MAG_BELT, 0,0],
    [0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0,0],
    # Row 16-21: 法袍下摆
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_L,_MAG_ROBE_L,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE,_MAG_STAR,_MAG_STAR,_MAG_ROBE,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    [0,0,0,0, _MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE,_MAG_ROBE_D, 0,0,0,0],
    # Row 22-25: 鞋子
    [0,0,0,0, _DARK,_DARK,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_MAG_ROBE_D,_DARK,_DARK, 0,0,0,0],
    [0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0],
    [0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0],
    [0,0,0,0,0, _DARK,_DARK,_DARK,_DARK,_DARK,_DARK, 0,0,0,0,0],
    # Row 26-31: 底部
    [0]*16, [0]*16, [0]*16, [0]*16, [0]*16, [0]*16,
]

# ========================================================================
# 时装注册表
# ========================================================================
COSTUMES: Dict[int, dict] = {
    1: {
        "id": 1,
        "name": "经典冒险家",
        "name_en": "Classic Adventurer",
        "desc": "勇敢的探险者，蓝色衬衫搭配棕色长裤，经典永不过时。",
        "pixels": _COSTUME_ADVENTURER,
        "w": 16, "h": 32,
    },
    2: {
        "id": 2,
        "name": "暗影忍者",
        "name_en": "Shadow Ninja",
        "desc": "来自阴影中的战士，紫色兜帽蒙面，红色双目摄人心魄。",
        "pixels": _COSTUME_NINJA,
        "w": 16, "h": 32,
    },
    3: {
        "id": 3,
        "name": "星辰法师",
        "name_en": "Star Mage",
        "desc": "掌握星辰之力的智者，蓝色法袍缀有星纹，白须飘然。",
        "pixels": _COSTUME_MAGE,
        "w": 16, "h": 32,
    },
}

DEFAULT_COSTUME_ID = 1

# ===================== 预渲染辅助 =====================
def _pixels_to_surface(pixels: list, w: int, h: int) -> pygame.Surface:
    """将二维像素列表转换为带透明通道的 pygame.Surface。
    0 (整数零) 表示透明像素。仅在模块导入时调用。"""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(h):
        row_data = pixels[row]
        for col in range(w):
            color = row_data[col]
            if color != 0:
                surf.set_at((col, row), color)
    return surf


# ===================== 预渲染所有时装源表面（模块导入时一次性执行） =====================
for _cid, _cdata in COSTUMES.items():
    _cdata["src_surf"] = _pixels_to_surface(_cdata["pixels"], _cdata["w"], _cdata["h"])


# ===================== 渲染缓存 =====================
_costume_cache: dict = {}  # (costume_id, w, h) → pygame.Surface


def get_costume(costume_id: int) -> Optional[dict]:
    """获取时装数据。"""
    return COSTUMES.get(costume_id)


def list_costumes() -> dict:
    """列出所有时装 {id: name}。"""
    return {c["id"]: c["name"] for c in COSTUMES.values()}


def render_costume(surface: pygame.Surface, costume_id: int,
                   x: float, y: float, w: float, h: float):
    """
    在 surface 的 (x,y,w,h) 矩形区域绘制时装。
    使用预渲染源表面 + 缩放缓存加速重复渲染。
    """
    costume = COSTUMES.get(costume_id)
    if costume is None:
        # 未知时装：绘制默认红色
        pygame.draw.rect(surface, (255, 80, 80), (x, y, w, h))
        return

    pw, ph = int(w), int(h)
    if pw <= 0 or ph <= 0:
        return

    cache_key = (costume_id, pw, ph)
    if cache_key in _costume_cache:
        surface.blit(_costume_cache[cache_key], (x, y))
        return

    # 使用导入时预渲染的源表面，直接缩放（无 set_at 循环）
    src = costume["src_surf"]
    scaled = pygame.transform.scale(src, (pw, ph))
    _costume_cache[cache_key] = scaled
    surface.blit(scaled, (x, y))


def render_costume_direct(surface: pygame.Surface, costume_id: int,
                          dest_rect: pygame.Rect):
    """直接在目标矩形上绘制时装。"""
    render_costume(surface, costume_id,
                   dest_rect.x, dest_rect.y,
                   dest_rect.w, dest_rect.h)
