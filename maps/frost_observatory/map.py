"""霜月观测台：紧凑双路线地图，布局由 JSON 加载。"""
from pathlib import Path
from world import World
from maps.layout import apply_layout

MAP_ID = 1002
world = World(map_id=MAP_ID, name="霜月观测台", w=96, h=36,
              gravity=-6.5, view_blocks_h=24, spawn_points=(4.5, 9.9),
              mode="explore", default_block_id=11, edge_behavior="solid")
world.lives = 3
apply_layout(world, Path(__file__).with_name("layout.json"))
