"""Validate existing map editor settings before they reach the game loop."""
from copy import deepcopy
import math


WORLD_RANGES = {
    "gravity": (-1000, 1000), "view_blocks_h": (2, 200),
    "void_limit": (0, 10000), "lives": (0, 10000),
    "score_goal": (0, 1e9), "time_limit": (0, 86400),
    "width": (1, 100000), "height": (1, 100000),
}
PLAYER_RANGES = {
    "hp_max": (0.01, 1e9), "shield": (0, 1e9),
    "v_max": (0, 1000), "v_jump": (0, 1000),
    "stamina_max": (0.01, 1e9), "w": (0.1, 10), "h": (0.1, 10),
    "f_x": (0, 1), "f_y": (0, 1), "dr": (0, 1),
    "phys_atk": (0, 1e9), "magic_atk": (0, 1e9),
    "phys_res": (-1e9, 1e9), "magic_res": (-1e9, 1e9),
    "phys_pen": (-1e9, 1e9), "magic_pen": (-1e9, 1e9),
    "k_res": (0, 1e9), "costume_id": (1, 100000),
}
INTEGER_FIELDS = {"void_limit", "lives", "score_goal", "width", "height", "costume_id"}


def validate_config(config):
    if not isinstance(config, dict) or set(config) - {"world", "player"}:
        raise ValueError("配置必须只包含 world/player 对象")
    result = deepcopy(config)
    for section, ranges in (("world", WORLD_RANGES), ("player", PLAYER_RANGES)):
        values = result.get(section, {})
        if not isinstance(values, dict):
            raise ValueError(f"{section} 必须是对象")
        for key, value in values.items():
            field = f"{section}.{key}"
            if key in ranges:
                low, high = ranges[key]
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not math.isfinite(value) or not low <= value <= high):
                    raise ValueError(f"{field} 必须在 {low} 到 {high} 之间")
                if key in INTEGER_FIELDS and not isinstance(value, int):
                    raise ValueError(f"{field} 必须是整数")
            elif section == "world" and key in ("loop_x", "loop_y"):
                if not isinstance(value, bool):
                    raise ValueError(f"{field} 必须为 true/false")
            elif section == "world" and key == "mode":
                if value not in ("free", "adventure", "explore", "score_timed", "score_target"):
                    raise ValueError(f"{field} 无效")
            elif section == "world" and key == "edge_behavior":
                if value not in ("solid", "void"):
                    raise ValueError(f"{field} 无效")
            elif section == "world" and key == "music":
                if not isinstance(value, str):
                    raise ValueError(f"{field} 必须是文本")
            elif section == "world" and key == "default_block_id":
                from block_types_data import BLOCK_TYPES
                if isinstance(value, bool) or not isinstance(value, int) or value not in BLOCK_TYPES:
                    raise ValueError(f"{field} 必须是已注册方块 ID")
            elif section == "world" and key == "fill_color":
                if isinstance(value, str):
                    try:
                        value = [int(part.strip()) for part in value.split(",")]
                    except ValueError:
                        raise ValueError(f"{field} 必须为 R,G,B") from None
                if (not isinstance(value, (list, tuple)) or len(value) != 3
                        or any(type(c) is not int or not 0 <= c <= 255 for c in value)):
                    raise ValueError(f"{field} 必须包含三个 0 到 255 的整数")
                values[key] = list(value)
            else:
                raise ValueError(f"未知配置字段 {field}")
    return result
