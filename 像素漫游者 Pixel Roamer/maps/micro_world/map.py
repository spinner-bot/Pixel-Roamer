"""
微型世界
"""
from world import World

MAP_ID = 19
world = World(map_id=MAP_ID, name="微型世界", w=1, h=1, gravity=-2, view_blocks_h=20, spawn_points=(0, 0), default_block_id=9,loop_x=True,loop_y=True)

world.begin_bulk_load()
world.end_bulk_load()
