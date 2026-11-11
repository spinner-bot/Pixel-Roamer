"""Bounded safe placement when editor dimensions change a map's spawn footprint."""
import math
from teleport import can_place


class SpawnPlacementError(ValueError):
    pass


def place_world_spawn(player, world, reference_height):
    x, y = player.get_center()
    if can_place(player, world, x, y):
        return
    # A taller player usually needs the same feet, rather than the old center.
    foot_aligned = (x, y + (player._h - reference_height) / 2)
    if can_place(player, world, *foot_aligned):
        target = foot_aligned
    else:
        def axis_candidates(origin, half_size):
            grid = range(math.floor(origin) - 8, math.floor(origin) + 9)
            return ({origin + offset / 2 for offset in range(-16, 17)}
                    | {edge + side * half_size for edge in grid for side in (-1, 1)})
        candidates = [(cx, cy) for cx in axis_candidates(x, player._w / 2)
                      for cy in axis_candidates(y, player._h / 2)
                      if abs(cx - x) <= 8 and abs(cy - y) <= 8]
        candidates.sort(key=lambda p: ((p[0] - x) ** 2 + (p[1] - y) ** 2,
                                       abs(p[0] - x), p[1] < y, p))
        target = next((p for p in candidates if can_place(player, world, *p)), None)
    if target is None:
        raise SpawnPlacementError(f'出生点附近无法容纳宽{player._w:g}、高{player._h:g}的角色，请调整玩家尺寸或地图。')
    player._x, player._y = target
    player.spawn_pos = target
