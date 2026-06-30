"""Buff 功能方块库 — 342 个方块，ID 400-741"""
from block_type import BlockType

BUFF_BLOCKS = {
    400: BlockType(id=400, name="regen_a", name2="恢复·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('circle', 4, 4, 2, (80, 220, 120)), ('circle', 12, 4, 2, (80, 220, 120)), ('circle', 4, 12, 2, (80, 220, 120)), ('circle', 12, 12, 2, (80, 220, 120)), ('circle', 8, 8, 2, (110, 250, 150))]),
        buff_id=1, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=4, light_level=0),

    401: BlockType(id=401, name="regen_b", name2="恢复·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 3, (60, 200, 220)), ('rect', 0, 8, 16, 3, (80, 220, 240)), ('rect', 0, 14, 16, 2, (60, 200, 220))]),
        buff_id=1, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=0),

    402: BlockType(id=402, name="regen_c", name2="恢复·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 0, 0, 8, 8, (220, 200, 80)), ('rect', 8, 8, 8, 8, (220, 200, 80)), ('rect', 8, 0, 8, 8, (250, 230, 110)), ('rect', 0, 8, 8, 8, (250, 230, 110))]),
        buff_id=1, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=6, light_level=0),

    403: BlockType(id=403, name="regen_d", name2="恢复·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 6, 2, 4, 12, (100, 160, 240)), ('rect', 2, 6, 12, 4, (100, 160, 240)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=1, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=4, light_level=3),

    404: BlockType(id=404, name="regen_e", name2="恢复·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 8, 1, 2, 14, (180, 140, 220)), ('rect', 1, 8, 14, 2, (180, 140, 220)), ('circle', 8, 8, 3, (210, 170, 250))]),
        buff_id=1, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=4, light_level=2),

    405: BlockType(id=405, name="regen_f", name2="恢复·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('circle', 8, 8, 6, (60, 240, 160)), ('circle', 8, 8, 4, (80, 255, 180)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=1, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=9, light_level=0),

    406: BlockType(id=406, name="shield_regen_a", name2="护佑·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=2, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=3, light_level=0),

    407: BlockType(id=407, name="shield_regen_b", name2="护佑·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=2, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=0),

    408: BlockType(id=408, name="shield_regen_c", name2="护佑·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=2, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=3, light_level=2),

    409: BlockType(id=409, name="shield_regen_d", name2="护佑·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=2, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=6, light_level=3),

    410: BlockType(id=410, name="shield_regen_e", name2="护佑·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=2, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=9, light_level=0),

    411: BlockType(id=411, name="shield_regen_f", name2="护佑·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=2, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=10, light_level=2),

    412: BlockType(id=412, name="swiftness_a", name2="迅捷·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=3, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=7, light_level=0),

    413: BlockType(id=413, name="swiftness_b", name2="迅捷·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=3, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=3),

    414: BlockType(id=414, name="swiftness_c", name2="迅捷·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=3, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=0),

    415: BlockType(id=415, name="swiftness_d", name2="迅捷·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=3, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=0),

    416: BlockType(id=416, name="swiftness_e", name2="迅捷·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=3, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=0),

    417: BlockType(id=417, name="swiftness_f", name2="迅捷·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=3, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=0),

    418: BlockType(id=418, name="leaping_a", name2="轻身·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 3, 0, 3, 16, (80, 220, 120)), ('rect', 10, 0, 3, 12, (100, 240, 140)), ('rect', 6, 4, 2, 8, (60, 200, 100))]),
        buff_id=4, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=0),

    419: BlockType(id=419, name="leaping_b", name2="轻身·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 1, 8, 3, (60, 200, 220)), ('rect', 10, 1, 6, 3, (60, 200, 220)), ('rect', 0, 7, 6, 3, (60, 200, 220)), ('rect', 8, 7, 8, 3, (60, 200, 220)), ('rect', 0, 13, 8, 3, (60, 200, 220)), ('rect', 10, 13, 6, 3, (60, 200, 220))]),
        buff_id=4, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=8, light_level=0),

    420: BlockType(id=420, name="leaping_c", name2="轻身·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('circle', 4, 4, 2, (220, 200, 80)), ('circle', 12, 4, 2, (220, 200, 80)), ('circle', 4, 12, 2, (220, 200, 80)), ('circle', 12, 12, 2, (220, 200, 80)), ('circle', 8, 8, 2, (250, 230, 110))]),
        buff_id=4, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=7, light_level=0),

    421: BlockType(id=421, name="leaping_d", name2="轻身·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 3, (100, 160, 240)), ('rect', 0, 8, 16, 3, (120, 180, 255)), ('rect', 0, 14, 16, 2, (100, 160, 240))]),
        buff_id=4, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=10, light_level=2),

    422: BlockType(id=422, name="leaping_e", name2="轻身·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 0, 0, 8, 8, (180, 140, 220)), ('rect', 8, 8, 8, 8, (180, 140, 220)), ('rect', 8, 0, 8, 8, (210, 170, 250)), ('rect', 0, 8, 8, 8, (210, 170, 250))]),
        buff_id=4, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=4, light_level=1),

    423: BlockType(id=423, name="leaping_f", name2="轻身·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 6, 2, 4, 12, (60, 240, 160)), ('rect', 2, 6, 12, 4, (60, 240, 160)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=4, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=2),

    424: BlockType(id=424, name="vigor_a", name2="活力·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 8, 1, 2, 14, (80, 220, 120)), ('rect', 1, 8, 14, 2, (80, 220, 120)), ('circle', 8, 8, 3, (110, 250, 150))]),
        buff_id=5, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=7, light_level=3),

    425: BlockType(id=425, name="vigor_b", name2="活力·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('circle', 8, 8, 6, (60, 200, 220)), ('circle', 8, 8, 4, (80, 220, 240)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=5, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=8, light_level=2),

    426: BlockType(id=426, name="vigor_c", name2="活力·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 2, 1, 4, 5, (220, 200, 80)), ('rect', 8, 1, 4, 5, (220, 200, 80)), ('rect', 5, 4, 4, 5, (220, 200, 80)), ('rect', 11, 4, 4, 5, (220, 200, 80)), ('rect', 2, 10, 4, 5, (220, 200, 80)), ('rect', 8, 10, 4, 5, (220, 200, 80))]),
        buff_id=5, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=6, light_level=3),

    427: BlockType(id=427, name="vigor_d", name2="活力·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 2, (100, 160, 240)), ('rect', 0, 6, 16, 2, (100, 160, 240)), ('rect', 0, 10, 16, 2, (100, 160, 240)), ('rect', 0, 14, 16, 2, (100, 160, 240)), ('rect', 2, 4, 12, 1, (130, 190, 255))]),
        buff_id=5, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=4, light_level=0),

    428: BlockType(id=428, name="vigor_e", name2="活力·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 3, 0, 3, 16, (180, 140, 220)), ('rect', 10, 0, 3, 12, (200, 160, 240)), ('rect', 6, 4, 2, 8, (160, 120, 200))]),
        buff_id=5, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=0),

    429: BlockType(id=429, name="vigor_f", name2="活力·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 1, 8, 3, (60, 240, 160)), ('rect', 10, 1, 6, 3, (60, 240, 160)), ('rect', 0, 7, 6, 3, (60, 240, 160)), ('rect', 8, 7, 8, 3, (60, 240, 160)), ('rect', 0, 13, 8, 3, (60, 240, 160)), ('rect', 10, 13, 6, 3, (60, 240, 160))]),
        buff_id=5, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=0),

    430: BlockType(id=430, name="endurance_a", name2="坚忍·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('circle', 4, 4, 2, (80, 220, 120)), ('circle', 12, 4, 2, (80, 220, 120)), ('circle', 4, 12, 2, (80, 220, 120)), ('circle', 12, 12, 2, (80, 220, 120)), ('circle', 8, 8, 2, (110, 250, 150))]),
        buff_id=6, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=4, light_level=1),

    431: BlockType(id=431, name="endurance_b", name2="坚忍·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 3, (60, 200, 220)), ('rect', 0, 8, 16, 3, (80, 220, 240)), ('rect', 0, 14, 16, 2, (60, 200, 220))]),
        buff_id=6, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=1),

    432: BlockType(id=432, name="endurance_c", name2="坚忍·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 0, 0, 8, 8, (220, 200, 80)), ('rect', 8, 8, 8, 8, (220, 200, 80)), ('rect', 8, 0, 8, 8, (250, 230, 110)), ('rect', 0, 8, 8, 8, (250, 230, 110))]),
        buff_id=6, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=8, light_level=0),

    433: BlockType(id=433, name="endurance_d", name2="坚忍·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 6, 2, 4, 12, (100, 160, 240)), ('rect', 2, 6, 12, 4, (100, 160, 240)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=6, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=8, light_level=0),

    434: BlockType(id=434, name="endurance_e", name2="坚忍·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 8, 1, 2, 14, (180, 140, 220)), ('rect', 1, 8, 14, 2, (180, 140, 220)), ('circle', 8, 8, 3, (210, 170, 250))]),
        buff_id=6, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=3),

    435: BlockType(id=435, name="endurance_f", name2="坚忍·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('circle', 8, 8, 6, (60, 240, 160)), ('circle', 8, 8, 4, (80, 255, 180)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=6, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=7, light_level=3),

    436: BlockType(id=436, name="fortify_a", name2="坚守·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=7, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=4, light_level=2),

    437: BlockType(id=437, name="fortify_b", name2="坚守·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=7, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=2),

    438: BlockType(id=438, name="fortify_c", name2="坚守·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=7, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=6, light_level=0),

    439: BlockType(id=439, name="fortify_d", name2="坚守·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=7, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=10, light_level=1),

    440: BlockType(id=440, name="fortify_e", name2="坚守·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=7, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=7, light_level=3),

    441: BlockType(id=441, name="fortify_f", name2="坚守·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=7, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=6, light_level=3),

    442: BlockType(id=442, name="clarity_a", name2="清明·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=8, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=8, light_level=0),

    443: BlockType(id=443, name="clarity_b", name2="清明·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=8, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=0),

    444: BlockType(id=444, name="clarity_c", name2="清明·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=8, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=8, light_level=1),

    445: BlockType(id=445, name="clarity_d", name2="清明·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=8, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=0),

    446: BlockType(id=446, name="clarity_e", name2="清明·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=8, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=2),

    447: BlockType(id=447, name="clarity_f", name2="清明·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=8, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=8, light_level=0),

    448: BlockType(id=448, name="fire_resist_a", name2="耐火·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 3, 0, 3, 16, (80, 220, 120)), ('rect', 10, 0, 3, 12, (100, 240, 140)), ('rect', 6, 4, 2, 8, (60, 200, 100))]),
        buff_id=9, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=10, light_level=1),

    449: BlockType(id=449, name="fire_resist_b", name2="耐火·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 1, 8, 3, (60, 200, 220)), ('rect', 10, 1, 6, 3, (60, 200, 220)), ('rect', 0, 7, 6, 3, (60, 200, 220)), ('rect', 8, 7, 8, 3, (60, 200, 220)), ('rect', 0, 13, 8, 3, (60, 200, 220)), ('rect', 10, 13, 6, 3, (60, 200, 220))]),
        buff_id=9, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=10, light_level=0),

    450: BlockType(id=450, name="fire_resist_c", name2="耐火·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('circle', 4, 4, 2, (220, 200, 80)), ('circle', 12, 4, 2, (220, 200, 80)), ('circle', 4, 12, 2, (220, 200, 80)), ('circle', 12, 12, 2, (220, 200, 80)), ('circle', 8, 8, 2, (250, 230, 110))]),
        buff_id=9, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=7, light_level=0),

    451: BlockType(id=451, name="fire_resist_d", name2="耐火·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 3, (100, 160, 240)), ('rect', 0, 8, 16, 3, (120, 180, 255)), ('rect', 0, 14, 16, 2, (100, 160, 240))]),
        buff_id=9, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=6, light_level=3),

    452: BlockType(id=452, name="fire_resist_e", name2="耐火·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 0, 0, 8, 8, (180, 140, 220)), ('rect', 8, 8, 8, 8, (180, 140, 220)), ('rect', 8, 0, 8, 8, (210, 170, 250)), ('rect', 0, 8, 8, 8, (210, 170, 250))]),
        buff_id=9, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=7, light_level=3),

    453: BlockType(id=453, name="fire_resist_f", name2="耐火·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 6, 2, 4, 12, (60, 240, 160)), ('rect', 2, 6, 12, 4, (60, 240, 160)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=9, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=9, light_level=2),

    454: BlockType(id=454, name="thornmail_a", name2="荆棘·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 8, 1, 2, 14, (80, 220, 120)), ('rect', 1, 8, 14, 2, (80, 220, 120)), ('circle', 8, 8, 3, (110, 250, 150))]),
        buff_id=10, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=0),

    455: BlockType(id=455, name="thornmail_b", name2="荆棘·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('circle', 8, 8, 6, (60, 200, 220)), ('circle', 8, 8, 4, (80, 220, 240)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=10, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=0),

    456: BlockType(id=456, name="thornmail_c", name2="荆棘·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 2, 1, 4, 5, (220, 200, 80)), ('rect', 8, 1, 4, 5, (220, 200, 80)), ('rect', 5, 4, 4, 5, (220, 200, 80)), ('rect', 11, 4, 4, 5, (220, 200, 80)), ('rect', 2, 10, 4, 5, (220, 200, 80)), ('rect', 8, 10, 4, 5, (220, 200, 80))]),
        buff_id=10, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=10, light_level=0),

    457: BlockType(id=457, name="thornmail_d", name2="荆棘·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 2, (100, 160, 240)), ('rect', 0, 6, 16, 2, (100, 160, 240)), ('rect', 0, 10, 16, 2, (100, 160, 240)), ('rect', 0, 14, 16, 2, (100, 160, 240)), ('rect', 2, 4, 12, 1, (130, 190, 255))]),
        buff_id=10, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=3, light_level=0),

    458: BlockType(id=458, name="thornmail_e", name2="荆棘·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 3, 0, 3, 16, (180, 140, 220)), ('rect', 10, 0, 3, 12, (200, 160, 240)), ('rect', 6, 4, 2, 8, (160, 120, 200))]),
        buff_id=10, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=5, light_level=3),

    459: BlockType(id=459, name="thornmail_f", name2="荆棘·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 1, 8, 3, (60, 240, 160)), ('rect', 10, 1, 6, 3, (60, 240, 160)), ('rect', 0, 7, 6, 3, (60, 240, 160)), ('rect', 8, 7, 8, 3, (60, 240, 160)), ('rect', 0, 13, 8, 3, (60, 240, 160)), ('rect', 10, 13, 6, 3, (60, 240, 160))]),
        buff_id=10, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=5, light_level=3),

    460: BlockType(id=460, name="lifesteal_a", name2="嗜血·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('circle', 4, 4, 2, (80, 220, 120)), ('circle', 12, 4, 2, (80, 220, 120)), ('circle', 4, 12, 2, (80, 220, 120)), ('circle', 12, 12, 2, (80, 220, 120)), ('circle', 8, 8, 2, (110, 250, 150))]),
        buff_id=11, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=2),

    461: BlockType(id=461, name="lifesteal_b", name2="嗜血·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 3, (60, 200, 220)), ('rect', 0, 8, 16, 3, (80, 220, 240)), ('rect', 0, 14, 16, 2, (60, 200, 220))]),
        buff_id=11, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=4, light_level=1),

    462: BlockType(id=462, name="lifesteal_c", name2="嗜血·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 0, 0, 8, 8, (220, 200, 80)), ('rect', 8, 8, 8, 8, (220, 200, 80)), ('rect', 8, 0, 8, 8, (250, 230, 110)), ('rect', 0, 8, 8, 8, (250, 230, 110))]),
        buff_id=11, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=2),

    463: BlockType(id=463, name="lifesteal_d", name2="嗜血·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 6, 2, 4, 12, (100, 160, 240)), ('rect', 2, 6, 12, 4, (100, 160, 240)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=11, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=10, light_level=2),

    464: BlockType(id=464, name="lifesteal_e", name2="嗜血·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 8, 1, 2, 14, (180, 140, 220)), ('rect', 1, 8, 14, 2, (180, 140, 220)), ('circle', 8, 8, 3, (210, 170, 250))]),
        buff_id=11, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=7, light_level=2),

    465: BlockType(id=465, name="lifesteal_f", name2="嗜血·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('circle', 8, 8, 6, (60, 240, 160)), ('circle', 8, 8, 4, (80, 255, 180)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=11, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=3, light_level=3),

    466: BlockType(id=466, name="cleansing_a", name2="净化·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=12, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=4, light_level=3),

    467: BlockType(id=467, name="cleansing_b", name2="净化·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=12, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=3),

    468: BlockType(id=468, name="cleansing_c", name2="净化·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=12, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=8, light_level=0),

    469: BlockType(id=469, name="cleansing_d", name2="净化·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=12, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=1),

    470: BlockType(id=470, name="cleansing_e", name2="净化·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=12, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=5, light_level=1),

    471: BlockType(id=471, name="cleansing_f", name2="净化·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=12, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=3, light_level=3),

    472: BlockType(id=472, name="feather_a", name2="轻羽·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=13, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=7, light_level=2),

    473: BlockType(id=473, name="feather_b", name2="轻羽·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=13, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=2),

    474: BlockType(id=474, name="feather_c", name2="轻羽·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=13, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=4, light_level=3),

    475: BlockType(id=475, name="feather_d", name2="轻羽·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=13, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=3),

    476: BlockType(id=476, name="feather_e", name2="轻羽·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=13, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=0),

    477: BlockType(id=477, name="feather_f", name2="轻羽·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=13, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=8, light_level=0),

    478: BlockType(id=478, name="magnetic_a", name2="磁引·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 3, 0, 3, 16, (160, 160, 180)), ('rect', 10, 0, 3, 12, (180, 180, 200)), ('rect', 6, 4, 2, 8, (140, 140, 160))]),
        buff_id=14, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=3, light_level=2),

    479: BlockType(id=479, name="magnetic_b", name2="磁引·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('rect', 0, 1, 8, 3, (180, 160, 140)), ('rect', 10, 1, 6, 3, (180, 160, 140)), ('rect', 0, 7, 6, 3, (180, 160, 140)), ('rect', 8, 7, 8, 3, (180, 160, 140)), ('rect', 0, 13, 8, 3, (180, 160, 140)), ('rect', 10, 13, 6, 3, (180, 160, 140))]),
        buff_id=14, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=8, light_level=1),

    480: BlockType(id=480, name="magnetic_c", name2="磁引·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('circle', 4, 4, 2, (140, 160, 180)), ('circle', 12, 4, 2, (140, 160, 180)), ('circle', 4, 12, 2, (140, 160, 180)), ('circle', 12, 12, 2, (140, 160, 180)), ('circle', 8, 8, 2, (170, 190, 210))]),
        buff_id=14, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=3, light_level=0),

    481: BlockType(id=481, name="magnetic_d", name2="磁引·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 0, 2, 16, 3, (160, 180, 160)), ('rect', 0, 8, 16, 3, (180, 200, 180)), ('rect', 0, 14, 16, 2, (160, 180, 160))]),
        buff_id=14, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=8, light_level=0),

    482: BlockType(id=482, name="magnetic_e", name2="磁引·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 0, 0, 8, 8, (180, 140, 180)), ('rect', 8, 8, 8, 8, (180, 140, 180)), ('rect', 8, 0, 8, 8, (210, 170, 210)), ('rect', 0, 8, 8, 8, (210, 170, 210))]),
        buff_id=14, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=6, light_level=0),

    483: BlockType(id=483, name="magnetic_f", name2="磁引·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 6, 2, 4, 12, (140, 180, 160)), ('rect', 2, 6, 12, 4, (140, 180, 160)), ('circle', 8, 8, 2, (180, 220, 200))]),
        buff_id=14, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=6, light_level=2),

    484: BlockType(id=484, name="soaked_a", name2="浸湿·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 8, 1, 2, 14, (160, 160, 180)), ('rect', 1, 8, 14, 2, (160, 160, 180)), ('circle', 8, 8, 3, (190, 190, 210))]),
        buff_id=15, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=4, light_level=0),

    485: BlockType(id=485, name="soaked_b", name2="浸湿·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('circle', 8, 8, 6, (180, 160, 140)), ('circle', 8, 8, 4, (200, 180, 160)), ('circle', 8, 8, 2, (220, 200, 180))]),
        buff_id=15, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=10, light_level=0),

    486: BlockType(id=486, name="soaked_c", name2="浸湿·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('rect', 2, 1, 4, 5, (140, 160, 180)), ('rect', 8, 1, 4, 5, (140, 160, 180)), ('rect', 5, 4, 4, 5, (140, 160, 180)), ('rect', 11, 4, 4, 5, (140, 160, 180)), ('rect', 2, 10, 4, 5, (140, 160, 180)), ('rect', 8, 10, 4, 5, (140, 160, 180))]),
        buff_id=15, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=5, light_level=0),

    487: BlockType(id=487, name="soaked_d", name2="浸湿·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 0, 2, 16, 2, (160, 180, 160)), ('rect', 0, 6, 16, 2, (160, 180, 160)), ('rect', 0, 10, 16, 2, (160, 180, 160)), ('rect', 0, 14, 16, 2, (160, 180, 160)), ('rect', 2, 4, 12, 1, (190, 210, 190))]),
        buff_id=15, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=10, light_level=2),

    488: BlockType(id=488, name="soaked_e", name2="浸湿·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 3, 0, 3, 16, (180, 140, 180)), ('rect', 10, 0, 3, 12, (200, 160, 200)), ('rect', 6, 4, 2, 8, (160, 120, 160))]),
        buff_id=15, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=5, light_level=0),

    489: BlockType(id=489, name="soaked_f", name2="浸湿·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 0, 1, 8, 3, (140, 180, 160)), ('rect', 10, 1, 6, 3, (140, 180, 160)), ('rect', 0, 7, 6, 3, (140, 180, 160)), ('rect', 8, 7, 8, 3, (140, 180, 160)), ('rect', 0, 13, 8, 3, (140, 180, 160)), ('rect', 10, 13, 6, 3, (140, 180, 160))]),
        buff_id=15, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=9, light_level=0),

    490: BlockType(id=490, name="burning_a", name2="着火·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=16, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=3),

    491: BlockType(id=491, name="burning_b", name2="着火·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=16, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=1),

    492: BlockType(id=492, name="burning_c", name2="着火·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=16, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=8, light_level=1),

    493: BlockType(id=493, name="burning_d", name2="着火·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=16, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=10, light_level=0),

    494: BlockType(id=494, name="burning_e", name2="着火·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=16, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=6, light_level=0),

    495: BlockType(id=495, name="burning_f", name2="着火·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=16, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=4, light_level=0),

    496: BlockType(id=496, name="bleeding_a", name2="流血·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 2, 1, 4, 5, (240, 80, 60)), ('rect', 8, 1, 4, 5, (240, 80, 60)), ('rect', 5, 4, 4, 5, (240, 80, 60)), ('rect', 11, 4, 4, 5, (240, 80, 60)), ('rect', 2, 10, 4, 5, (240, 80, 60)), ('rect', 8, 10, 4, 5, (240, 80, 60))]),
        buff_id=17, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=3, light_level=2),

    497: BlockType(id=497, name="bleeding_b", name2="流血·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 2, (200, 60, 100)), ('rect', 0, 6, 16, 2, (200, 60, 100)), ('rect', 0, 10, 16, 2, (200, 60, 100)), ('rect', 0, 14, 16, 2, (200, 60, 100)), ('rect', 2, 4, 12, 1, (230, 90, 130))]),
        buff_id=17, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=6, light_level=2),

    498: BlockType(id=498, name="bleeding_c", name2="流血·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 3, 0, 3, 16, (160, 50, 50)), ('rect', 10, 0, 3, 12, (180, 70, 70)), ('rect', 6, 4, 2, 8, (140, 30, 30))]),
        buff_id=17, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=6, light_level=0),

    499: BlockType(id=499, name="bleeding_d", name2="流血·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 1, 8, 3, (200, 80, 30)), ('rect', 10, 1, 6, 3, (200, 80, 30)), ('rect', 0, 7, 6, 3, (200, 80, 30)), ('rect', 8, 7, 8, 3, (200, 80, 30)), ('rect', 0, 13, 8, 3, (200, 80, 30)), ('rect', 10, 13, 6, 3, (200, 80, 30))]),
        buff_id=17, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=4, light_level=3),

    500: BlockType(id=500, name="bleeding_e", name2="流血·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('circle', 4, 4, 2, (140, 40, 80)), ('circle', 12, 4, 2, (140, 40, 80)), ('circle', 4, 12, 2, (140, 40, 80)), ('circle', 12, 12, 2, (140, 40, 80)), ('circle', 8, 8, 2, (170, 70, 110))]),
        buff_id=17, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=3, light_level=0),

    501: BlockType(id=501, name="bleeding_f", name2="流血·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 3, (180, 60, 60)), ('rect', 0, 8, 16, 3, (200, 80, 80)), ('rect', 0, 14, 16, 2, (180, 60, 60))]),
        buff_id=17, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=4, light_level=0),

    502: BlockType(id=502, name="weakened_a", name2="脱力·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 0, 0, 8, 8, (240, 80, 60)), ('rect', 8, 8, 8, 8, (240, 80, 60)), ('rect', 8, 0, 8, 8, (255, 110, 90)), ('rect', 0, 8, 8, 8, (255, 110, 90))]),
        buff_id=18, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    503: BlockType(id=503, name="weakened_b", name2="脱力·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 6, 2, 4, 12, (200, 60, 100)), ('rect', 2, 6, 12, 4, (200, 60, 100)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=18, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=6, light_level=0),

    504: BlockType(id=504, name="weakened_c", name2="脱力·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 8, 1, 2, 14, (160, 50, 50)), ('rect', 1, 8, 14, 2, (160, 50, 50)), ('circle', 8, 8, 3, (190, 80, 80))]),
        buff_id=18, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=0),

    505: BlockType(id=505, name="weakened_d", name2="脱力·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('circle', 8, 8, 6, (200, 80, 30)), ('circle', 8, 8, 4, (220, 100, 50)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=18, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=5, light_level=3),

    506: BlockType(id=506, name="weakened_e", name2="脱力·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 2, 1, 4, 5, (140, 40, 80)), ('rect', 8, 1, 4, 5, (140, 40, 80)), ('rect', 5, 4, 4, 5, (140, 40, 80)), ('rect', 11, 4, 4, 5, (140, 40, 80)), ('rect', 2, 10, 4, 5, (140, 40, 80)), ('rect', 8, 10, 4, 5, (140, 40, 80))]),
        buff_id=18, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=10, light_level=0),

    507: BlockType(id=507, name="weakened_f", name2="脱力·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 2, (180, 60, 60)), ('rect', 0, 6, 16, 2, (180, 60, 60)), ('rect', 0, 10, 16, 2, (180, 60, 60)), ('rect', 0, 14, 16, 2, (180, 60, 60)), ('rect', 2, 4, 12, 1, (210, 90, 90))]),
        buff_id=18, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=10, light_level=1),

    508: BlockType(id=508, name="fatigue_a", name2="疲倦·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 3, 0, 3, 16, (240, 80, 60)), ('rect', 10, 0, 3, 12, (255, 100, 80)), ('rect', 6, 4, 2, 8, (220, 60, 40))]),
        buff_id=19, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=0),

    509: BlockType(id=509, name="fatigue_b", name2="疲倦·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 1, 8, 3, (200, 60, 100)), ('rect', 10, 1, 6, 3, (200, 60, 100)), ('rect', 0, 7, 6, 3, (200, 60, 100)), ('rect', 8, 7, 8, 3, (200, 60, 100)), ('rect', 0, 13, 8, 3, (200, 60, 100)), ('rect', 10, 13, 6, 3, (200, 60, 100))]),
        buff_id=19, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=4, light_level=3),

    510: BlockType(id=510, name="fatigue_c", name2="疲倦·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('circle', 4, 4, 2, (160, 50, 50)), ('circle', 12, 4, 2, (160, 50, 50)), ('circle', 4, 12, 2, (160, 50, 50)), ('circle', 12, 12, 2, (160, 50, 50)), ('circle', 8, 8, 2, (190, 80, 80))]),
        buff_id=19, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=9, light_level=0),

    511: BlockType(id=511, name="fatigue_d", name2="疲倦·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 3, (200, 80, 30)), ('rect', 0, 8, 16, 3, (220, 100, 50)), ('rect', 0, 14, 16, 2, (200, 80, 30))]),
        buff_id=19, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=9, light_level=1),

    512: BlockType(id=512, name="fatigue_e", name2="疲倦·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 0, 0, 8, 8, (140, 40, 80)), ('rect', 8, 8, 8, 8, (140, 40, 80)), ('rect', 8, 0, 8, 8, (170, 70, 110)), ('rect', 0, 8, 8, 8, (170, 70, 110))]),
        buff_id=19, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=10, light_level=3),

    513: BlockType(id=513, name="fatigue_f", name2="疲倦·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 6, 2, 4, 12, (180, 60, 60)), ('rect', 2, 6, 12, 4, (180, 60, 60)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=19, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=3),

    514: BlockType(id=514, name="grievous_wound_a", name2="重伤·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 8, 1, 2, 14, (240, 80, 60)), ('rect', 1, 8, 14, 2, (240, 80, 60)), ('circle', 8, 8, 3, (255, 110, 90))]),
        buff_id=20, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=4, light_level=0),

    515: BlockType(id=515, name="grievous_wound_b", name2="重伤·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('circle', 8, 8, 6, (200, 60, 100)), ('circle', 8, 8, 4, (220, 80, 120)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=20, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=9, light_level=3),

    516: BlockType(id=516, name="grievous_wound_c", name2="重伤·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 2, 1, 4, 5, (160, 50, 50)), ('rect', 8, 1, 4, 5, (160, 50, 50)), ('rect', 5, 4, 4, 5, (160, 50, 50)), ('rect', 11, 4, 4, 5, (160, 50, 50)), ('rect', 2, 10, 4, 5, (160, 50, 50)), ('rect', 8, 10, 4, 5, (160, 50, 50))]),
        buff_id=20, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=8, light_level=0),

    517: BlockType(id=517, name="grievous_wound_d", name2="重伤·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 2, (200, 80, 30)), ('rect', 0, 6, 16, 2, (200, 80, 30)), ('rect', 0, 10, 16, 2, (200, 80, 30)), ('rect', 0, 14, 16, 2, (200, 80, 30)), ('rect', 2, 4, 12, 1, (230, 110, 60))]),
        buff_id=20, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=6, light_level=0),

    518: BlockType(id=518, name="grievous_wound_e", name2="重伤·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 3, 0, 3, 16, (140, 40, 80)), ('rect', 10, 0, 3, 12, (160, 60, 100)), ('rect', 6, 4, 2, 8, (120, 20, 60))]),
        buff_id=20, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=6, light_level=2),

    519: BlockType(id=519, name="grievous_wound_f", name2="重伤·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 1, 8, 3, (180, 60, 60)), ('rect', 10, 1, 6, 3, (180, 60, 60)), ('rect', 0, 7, 6, 3, (180, 60, 60)), ('rect', 8, 7, 8, 3, (180, 60, 60)), ('rect', 0, 13, 8, 3, (180, 60, 60)), ('rect', 10, 13, 6, 3, (180, 60, 60))]),
        buff_id=20, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=10, light_level=0),

    520: BlockType(id=520, name="rooted_a", name2="定身·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=21, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=9, light_level=0),

    521: BlockType(id=521, name="rooted_b", name2="定身·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=21, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=1),

    522: BlockType(id=522, name="rooted_c", name2="定身·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=21, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=6, light_level=0),

    523: BlockType(id=523, name="rooted_d", name2="定身·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=21, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=10, light_level=2),

    524: BlockType(id=524, name="rooted_e", name2="定身·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=21, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=4, light_level=0),

    525: BlockType(id=525, name="rooted_f", name2="定身·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=21, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=0),

    526: BlockType(id=526, name="slowed_a", name2="缓步·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 2, 1, 4, 5, (240, 80, 60)), ('rect', 8, 1, 4, 5, (240, 80, 60)), ('rect', 5, 4, 4, 5, (240, 80, 60)), ('rect', 11, 4, 4, 5, (240, 80, 60)), ('rect', 2, 10, 4, 5, (240, 80, 60)), ('rect', 8, 10, 4, 5, (240, 80, 60))]),
        buff_id=22, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=0),

    527: BlockType(id=527, name="slowed_b", name2="缓步·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 2, (200, 60, 100)), ('rect', 0, 6, 16, 2, (200, 60, 100)), ('rect', 0, 10, 16, 2, (200, 60, 100)), ('rect', 0, 14, 16, 2, (200, 60, 100)), ('rect', 2, 4, 12, 1, (230, 90, 130))]),
        buff_id=22, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=9, light_level=1),

    528: BlockType(id=528, name="slowed_c", name2="缓步·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 3, 0, 3, 16, (160, 50, 50)), ('rect', 10, 0, 3, 12, (180, 70, 70)), ('rect', 6, 4, 2, 8, (140, 30, 30))]),
        buff_id=22, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=0),

    529: BlockType(id=529, name="slowed_d", name2="缓步·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 1, 8, 3, (200, 80, 30)), ('rect', 10, 1, 6, 3, (200, 80, 30)), ('rect', 0, 7, 6, 3, (200, 80, 30)), ('rect', 8, 7, 8, 3, (200, 80, 30)), ('rect', 0, 13, 8, 3, (200, 80, 30)), ('rect', 10, 13, 6, 3, (200, 80, 30))]),
        buff_id=22, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=9, light_level=0),

    530: BlockType(id=530, name="slowed_e", name2="缓步·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('circle', 4, 4, 2, (140, 40, 80)), ('circle', 12, 4, 2, (140, 40, 80)), ('circle', 4, 12, 2, (140, 40, 80)), ('circle', 12, 12, 2, (140, 40, 80)), ('circle', 8, 8, 2, (170, 70, 110))]),
        buff_id=22, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=5, light_level=1),

    531: BlockType(id=531, name="slowed_f", name2="缓步·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 3, (180, 60, 60)), ('rect', 0, 8, 16, 3, (200, 80, 80)), ('rect', 0, 14, 16, 2, (180, 60, 60))]),
        buff_id=22, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=1),

    532: BlockType(id=532, name="reversed_a", name2="反向·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 0, 0, 8, 8, (240, 80, 60)), ('rect', 8, 8, 8, 8, (240, 80, 60)), ('rect', 8, 0, 8, 8, (255, 110, 90)), ('rect', 0, 8, 8, 8, (255, 110, 90))]),
        buff_id=23, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=7, light_level=1),

    533: BlockType(id=533, name="reversed_b", name2="反向·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 6, 2, 4, 12, (200, 60, 100)), ('rect', 2, 6, 12, 4, (200, 60, 100)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=23, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=1),

    534: BlockType(id=534, name="reversed_c", name2="反向·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 8, 1, 2, 14, (160, 50, 50)), ('rect', 1, 8, 14, 2, (160, 50, 50)), ('circle', 8, 8, 3, (190, 80, 80))]),
        buff_id=23, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=0),

    535: BlockType(id=535, name="reversed_d", name2="反向·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('circle', 8, 8, 6, (200, 80, 30)), ('circle', 8, 8, 4, (220, 100, 50)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=23, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=6, light_level=0),

    536: BlockType(id=536, name="reversed_e", name2="反向·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 2, 1, 4, 5, (140, 40, 80)), ('rect', 8, 1, 4, 5, (140, 40, 80)), ('rect', 5, 4, 4, 5, (140, 40, 80)), ('rect', 11, 4, 4, 5, (140, 40, 80)), ('rect', 2, 10, 4, 5, (140, 40, 80)), ('rect', 8, 10, 4, 5, (140, 40, 80))]),
        buff_id=23, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=6, light_level=0),

    537: BlockType(id=537, name="reversed_f", name2="反向·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 2, (180, 60, 60)), ('rect', 0, 6, 16, 2, (180, 60, 60)), ('rect', 0, 10, 16, 2, (180, 60, 60)), ('rect', 0, 14, 16, 2, (180, 60, 60)), ('rect', 2, 4, 12, 1, (210, 90, 90))]),
        buff_id=23, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=3),

    538: BlockType(id=538, name="blinded_a", name2="失明·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 3, 0, 3, 16, (240, 80, 60)), ('rect', 10, 0, 3, 12, (255, 100, 80)), ('rect', 6, 4, 2, 8, (220, 60, 40))]),
        buff_id=24, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    539: BlockType(id=539, name="blinded_b", name2="失明·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 1, 8, 3, (200, 60, 100)), ('rect', 10, 1, 6, 3, (200, 60, 100)), ('rect', 0, 7, 6, 3, (200, 60, 100)), ('rect', 8, 7, 8, 3, (200, 60, 100)), ('rect', 0, 13, 8, 3, (200, 60, 100)), ('rect', 10, 13, 6, 3, (200, 60, 100))]),
        buff_id=24, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=3, light_level=2),

    540: BlockType(id=540, name="blinded_c", name2="失明·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('circle', 4, 4, 2, (160, 50, 50)), ('circle', 12, 4, 2, (160, 50, 50)), ('circle', 4, 12, 2, (160, 50, 50)), ('circle', 12, 12, 2, (160, 50, 50)), ('circle', 8, 8, 2, (190, 80, 80))]),
        buff_id=24, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=2),

    541: BlockType(id=541, name="blinded_d", name2="失明·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 3, (200, 80, 30)), ('rect', 0, 8, 16, 3, (220, 100, 50)), ('rect', 0, 14, 16, 2, (200, 80, 30))]),
        buff_id=24, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=5, light_level=0),

    542: BlockType(id=542, name="blinded_e", name2="失明·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 0, 0, 8, 8, (140, 40, 80)), ('rect', 8, 8, 8, 8, (140, 40, 80)), ('rect', 8, 0, 8, 8, (170, 70, 110)), ('rect', 0, 8, 8, 8, (170, 70, 110))]),
        buff_id=24, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=4, light_level=0),

    543: BlockType(id=543, name="blinded_f", name2="失明·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 6, 2, 4, 12, (180, 60, 60)), ('rect', 2, 6, 12, 4, (180, 60, 60)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=24, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=4, light_level=2),

    544: BlockType(id=544, name="narrow_vision_a", name2="视野受限·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 8, 1, 2, 14, (240, 80, 60)), ('rect', 1, 8, 14, 2, (240, 80, 60)), ('circle', 8, 8, 3, (255, 110, 90))]),
        buff_id=25, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=4, light_level=3),

    545: BlockType(id=545, name="narrow_vision_b", name2="视野受限·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('circle', 8, 8, 6, (200, 60, 100)), ('circle', 8, 8, 4, (220, 80, 120)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=25, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=6, light_level=1),

    546: BlockType(id=546, name="narrow_vision_c", name2="视野受限·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 2, 1, 4, 5, (160, 50, 50)), ('rect', 8, 1, 4, 5, (160, 50, 50)), ('rect', 5, 4, 4, 5, (160, 50, 50)), ('rect', 11, 4, 4, 5, (160, 50, 50)), ('rect', 2, 10, 4, 5, (160, 50, 50)), ('rect', 8, 10, 4, 5, (160, 50, 50))]),
        buff_id=25, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=4, light_level=2),

    547: BlockType(id=547, name="narrow_vision_d", name2="视野受限·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 2, (200, 80, 30)), ('rect', 0, 6, 16, 2, (200, 80, 30)), ('rect', 0, 10, 16, 2, (200, 80, 30)), ('rect', 0, 14, 16, 2, (200, 80, 30)), ('rect', 2, 4, 12, 1, (230, 110, 60))]),
        buff_id=25, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=6, light_level=2),

    548: BlockType(id=548, name="narrow_vision_e", name2="视野受限·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 3, 0, 3, 16, (140, 40, 80)), ('rect', 10, 0, 3, 12, (160, 60, 100)), ('rect', 6, 4, 2, 8, (120, 20, 60))]),
        buff_id=25, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=3, light_level=2),

    549: BlockType(id=549, name="narrow_vision_f", name2="视野受限·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 1, 8, 3, (180, 60, 60)), ('rect', 10, 1, 6, 3, (180, 60, 60)), ('rect', 0, 7, 6, 3, (180, 60, 60)), ('rect', 8, 7, 8, 3, (180, 60, 60)), ('rect', 0, 13, 8, 3, (180, 60, 60)), ('rect', 10, 13, 6, 3, (180, 60, 60))]),
        buff_id=25, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=4, light_level=1),

    550: BlockType(id=550, name="armor_break_a", name2="破甲·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=26, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    551: BlockType(id=551, name="armor_break_b", name2="破甲·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=26, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=6, light_level=3),

    552: BlockType(id=552, name="armor_break_c", name2="破甲·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=26, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=8, light_level=0),

    553: BlockType(id=553, name="armor_break_d", name2="破甲·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=26, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=7, light_level=1),

    554: BlockType(id=554, name="armor_break_e", name2="破甲·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=26, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=5, light_level=3),

    555: BlockType(id=555, name="armor_break_f", name2="破甲·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=26, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=7, light_level=1),

    556: BlockType(id=556, name="grounded_a", name2="压制·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 2, 1, 4, 5, (240, 80, 60)), ('rect', 8, 1, 4, 5, (240, 80, 60)), ('rect', 5, 4, 4, 5, (240, 80, 60)), ('rect', 11, 4, 4, 5, (240, 80, 60)), ('rect', 2, 10, 4, 5, (240, 80, 60)), ('rect', 8, 10, 4, 5, (240, 80, 60))]),
        buff_id=27, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    557: BlockType(id=557, name="grounded_b", name2="压制·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 2, (200, 60, 100)), ('rect', 0, 6, 16, 2, (200, 60, 100)), ('rect', 0, 10, 16, 2, (200, 60, 100)), ('rect', 0, 14, 16, 2, (200, 60, 100)), ('rect', 2, 4, 12, 1, (230, 90, 130))]),
        buff_id=27, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=3, light_level=1),

    558: BlockType(id=558, name="grounded_c", name2="压制·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 3, 0, 3, 16, (160, 50, 50)), ('rect', 10, 0, 3, 12, (180, 70, 70)), ('rect', 6, 4, 2, 8, (140, 30, 30))]),
        buff_id=27, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=4, light_level=0),

    559: BlockType(id=559, name="grounded_d", name2="压制·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 1, 8, 3, (200, 80, 30)), ('rect', 10, 1, 6, 3, (200, 80, 30)), ('rect', 0, 7, 6, 3, (200, 80, 30)), ('rect', 8, 7, 8, 3, (200, 80, 30)), ('rect', 0, 13, 8, 3, (200, 80, 30)), ('rect', 10, 13, 6, 3, (200, 80, 30))]),
        buff_id=27, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=6, light_level=2),

    560: BlockType(id=560, name="grounded_e", name2="压制·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('circle', 4, 4, 2, (140, 40, 80)), ('circle', 12, 4, 2, (140, 40, 80)), ('circle', 4, 12, 2, (140, 40, 80)), ('circle', 12, 12, 2, (140, 40, 80)), ('circle', 8, 8, 2, (170, 70, 110))]),
        buff_id=27, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=7, light_level=0),

    561: BlockType(id=561, name="grounded_f", name2="压制·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 3, (180, 60, 60)), ('rect', 0, 8, 16, 3, (200, 80, 80)), ('rect', 0, 14, 16, 2, (180, 60, 60))]),
        buff_id=27, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=8, light_level=0),

    562: BlockType(id=562, name="stunned_a", name2="晕眩·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 0, 0, 8, 8, (240, 80, 60)), ('rect', 8, 8, 8, 8, (240, 80, 60)), ('rect', 8, 0, 8, 8, (255, 110, 90)), ('rect', 0, 8, 8, 8, (255, 110, 90))]),
        buff_id=28, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=0),

    563: BlockType(id=563, name="stunned_b", name2="晕眩·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 6, 2, 4, 12, (200, 60, 100)), ('rect', 2, 6, 12, 4, (200, 60, 100)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=28, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=0),

    564: BlockType(id=564, name="stunned_c", name2="晕眩·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 8, 1, 2, 14, (160, 50, 50)), ('rect', 1, 8, 14, 2, (160, 50, 50)), ('circle', 8, 8, 3, (190, 80, 80))]),
        buff_id=28, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=2),

    565: BlockType(id=565, name="stunned_d", name2="晕眩·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('circle', 8, 8, 6, (200, 80, 30)), ('circle', 8, 8, 4, (220, 100, 50)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=28, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=7, light_level=2),

    566: BlockType(id=566, name="stunned_e", name2="晕眩·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 2, 1, 4, 5, (140, 40, 80)), ('rect', 8, 1, 4, 5, (140, 40, 80)), ('rect', 5, 4, 4, 5, (140, 40, 80)), ('rect', 11, 4, 4, 5, (140, 40, 80)), ('rect', 2, 10, 4, 5, (140, 40, 80)), ('rect', 8, 10, 4, 5, (140, 40, 80))]),
        buff_id=28, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=3, light_level=3),

    567: BlockType(id=567, name="stunned_f", name2="晕眩·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 2, (180, 60, 60)), ('rect', 0, 6, 16, 2, (180, 60, 60)), ('rect', 0, 10, 16, 2, (180, 60, 60)), ('rect', 0, 14, 16, 2, (180, 60, 60)), ('rect', 2, 4, 12, 1, (210, 90, 90))]),
        buff_id=28, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=7, light_level=3),

    568: BlockType(id=568, name="pierced_a", name2="穿甲·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 3, 0, 3, 16, (240, 80, 60)), ('rect', 10, 0, 3, 12, (255, 100, 80)), ('rect', 6, 4, 2, 8, (220, 60, 40))]),
        buff_id=29, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=4, light_level=0),

    569: BlockType(id=569, name="pierced_b", name2="穿甲·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 1, 8, 3, (200, 60, 100)), ('rect', 10, 1, 6, 3, (200, 60, 100)), ('rect', 0, 7, 6, 3, (200, 60, 100)), ('rect', 8, 7, 8, 3, (200, 60, 100)), ('rect', 0, 13, 8, 3, (200, 60, 100)), ('rect', 10, 13, 6, 3, (200, 60, 100))]),
        buff_id=29, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=0),

    570: BlockType(id=570, name="pierced_c", name2="穿甲·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('circle', 4, 4, 2, (160, 50, 50)), ('circle', 12, 4, 2, (160, 50, 50)), ('circle', 4, 12, 2, (160, 50, 50)), ('circle', 12, 12, 2, (160, 50, 50)), ('circle', 8, 8, 2, (190, 80, 80))]),
        buff_id=29, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=4, light_level=3),

    571: BlockType(id=571, name="pierced_d", name2="穿甲·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 3, (200, 80, 30)), ('rect', 0, 8, 16, 3, (220, 100, 50)), ('rect', 0, 14, 16, 2, (200, 80, 30))]),
        buff_id=29, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=5, light_level=0),

    572: BlockType(id=572, name="pierced_e", name2="穿甲·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 0, 0, 8, 8, (140, 40, 80)), ('rect', 8, 8, 8, 8, (140, 40, 80)), ('rect', 8, 0, 8, 8, (170, 70, 110)), ('rect', 0, 8, 8, 8, (170, 70, 110))]),
        buff_id=29, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=7, light_level=2),

    573: BlockType(id=573, name="pierced_f", name2="穿甲·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 6, 2, 4, 12, (180, 60, 60)), ('rect', 2, 6, 12, 4, (180, 60, 60)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=29, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=6, light_level=3),

    574: BlockType(id=574, name="disarmed_a", name2="缴械·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 8, 1, 2, 14, (240, 80, 60)), ('rect', 1, 8, 14, 2, (240, 80, 60)), ('circle', 8, 8, 3, (255, 110, 90))]),
        buff_id=30, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    575: BlockType(id=575, name="disarmed_b", name2="缴械·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('circle', 8, 8, 6, (200, 60, 100)), ('circle', 8, 8, 4, (220, 80, 120)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=30, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=2),

    576: BlockType(id=576, name="disarmed_c", name2="缴械·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 2, 1, 4, 5, (160, 50, 50)), ('rect', 8, 1, 4, 5, (160, 50, 50)), ('rect', 5, 4, 4, 5, (160, 50, 50)), ('rect', 11, 4, 4, 5, (160, 50, 50)), ('rect', 2, 10, 4, 5, (160, 50, 50)), ('rect', 8, 10, 4, 5, (160, 50, 50))]),
        buff_id=30, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=0),

    577: BlockType(id=577, name="disarmed_d", name2="缴械·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 2, (200, 80, 30)), ('rect', 0, 6, 16, 2, (200, 80, 30)), ('rect', 0, 10, 16, 2, (200, 80, 30)), ('rect', 0, 14, 16, 2, (200, 80, 30)), ('rect', 2, 4, 12, 1, (230, 110, 60))]),
        buff_id=30, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=3, light_level=0),

    578: BlockType(id=578, name="disarmed_e", name2="缴械·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 3, 0, 3, 16, (140, 40, 80)), ('rect', 10, 0, 3, 12, (160, 60, 100)), ('rect', 6, 4, 2, 8, (120, 20, 60))]),
        buff_id=30, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=9, light_level=0),

    579: BlockType(id=579, name="disarmed_f", name2="缴械·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 1, 8, 3, (180, 60, 60)), ('rect', 10, 1, 6, 3, (180, 60, 60)), ('rect', 0, 7, 6, 3, (180, 60, 60)), ('rect', 8, 7, 8, 3, (180, 60, 60)), ('rect', 0, 13, 8, 3, (180, 60, 60)), ('rect', 10, 13, 6, 3, (180, 60, 60))]),
        buff_id=30, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=0),

    580: BlockType(id=580, name="interfered_a", name2="干扰·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=31, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=8, light_level=0),

    581: BlockType(id=581, name="interfered_b", name2="干扰·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=31, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=0),

    582: BlockType(id=582, name="interfered_c", name2="干扰·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=31, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=10, light_level=2),

    583: BlockType(id=583, name="interfered_d", name2="干扰·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=31, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=9, light_level=2),

    584: BlockType(id=584, name="interfered_e", name2="干扰·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=31, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=3, light_level=0),

    585: BlockType(id=585, name="interfered_f", name2="干扰·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=31, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=4, light_level=3),

    586: BlockType(id=586, name="silenced_debuff_a", name2="沉默·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 2, 1, 4, 5, (240, 80, 60)), ('rect', 8, 1, 4, 5, (240, 80, 60)), ('rect', 5, 4, 4, 5, (240, 80, 60)), ('rect', 11, 4, 4, 5, (240, 80, 60)), ('rect', 2, 10, 4, 5, (240, 80, 60)), ('rect', 8, 10, 4, 5, (240, 80, 60))]),
        buff_id=32, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=5, light_level=2),

    587: BlockType(id=587, name="silenced_debuff_b", name2="沉默·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 2, (200, 60, 100)), ('rect', 0, 6, 16, 2, (200, 60, 100)), ('rect', 0, 10, 16, 2, (200, 60, 100)), ('rect', 0, 14, 16, 2, (200, 60, 100)), ('rect', 2, 4, 12, 1, (230, 90, 130))]),
        buff_id=32, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=3, light_level=0),

    588: BlockType(id=588, name="silenced_debuff_c", name2="沉默·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 3, 0, 3, 16, (160, 50, 50)), ('rect', 10, 0, 3, 12, (180, 70, 70)), ('rect', 6, 4, 2, 8, (140, 30, 30))]),
        buff_id=32, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=5, light_level=1),

    589: BlockType(id=589, name="silenced_debuff_d", name2="沉默·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 1, 8, 3, (200, 80, 30)), ('rect', 10, 1, 6, 3, (200, 80, 30)), ('rect', 0, 7, 6, 3, (200, 80, 30)), ('rect', 8, 7, 8, 3, (200, 80, 30)), ('rect', 0, 13, 8, 3, (200, 80, 30)), ('rect', 10, 13, 6, 3, (200, 80, 30))]),
        buff_id=32, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=5, light_level=0),

    590: BlockType(id=590, name="silenced_debuff_e", name2="沉默·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('circle', 4, 4, 2, (140, 40, 80)), ('circle', 12, 4, 2, (140, 40, 80)), ('circle', 4, 12, 2, (140, 40, 80)), ('circle', 12, 12, 2, (140, 40, 80)), ('circle', 8, 8, 2, (170, 70, 110))]),
        buff_id=32, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=7, light_level=0),

    591: BlockType(id=591, name="silenced_debuff_f", name2="沉默·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 3, (180, 60, 60)), ('rect', 0, 8, 16, 3, (200, 80, 80)), ('rect', 0, 14, 16, 2, (180, 60, 60))]),
        buff_id=32, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=0),

    592: BlockType(id=592, name="hopping_a", name2="跳跃锁定·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 0, 0, 8, 8, (240, 80, 60)), ('rect', 8, 8, 8, 8, (240, 80, 60)), ('rect', 8, 0, 8, 8, (255, 110, 90)), ('rect', 0, 8, 8, 8, (255, 110, 90))]),
        buff_id=33, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=3),

    593: BlockType(id=593, name="hopping_b", name2="跳跃锁定·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 6, 2, 4, 12, (200, 60, 100)), ('rect', 2, 6, 12, 4, (200, 60, 100)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=33, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=6, light_level=3),

    594: BlockType(id=594, name="hopping_c", name2="跳跃锁定·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 8, 1, 2, 14, (160, 50, 50)), ('rect', 1, 8, 14, 2, (160, 50, 50)), ('circle', 8, 8, 3, (190, 80, 80))]),
        buff_id=33, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=4, light_level=0),

    595: BlockType(id=595, name="hopping_d", name2="跳跃锁定·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('circle', 8, 8, 6, (200, 80, 30)), ('circle', 8, 8, 4, (220, 100, 50)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=33, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=9, light_level=2),

    596: BlockType(id=596, name="hopping_e", name2="跳跃锁定·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 2, 1, 4, 5, (140, 40, 80)), ('rect', 8, 1, 4, 5, (140, 40, 80)), ('rect', 5, 4, 4, 5, (140, 40, 80)), ('rect', 11, 4, 4, 5, (140, 40, 80)), ('rect', 2, 10, 4, 5, (140, 40, 80)), ('rect', 8, 10, 4, 5, (140, 40, 80))]),
        buff_id=33, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=5, light_level=0),

    597: BlockType(id=597, name="hopping_f", name2="跳跃锁定·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 2, (180, 60, 60)), ('rect', 0, 6, 16, 2, (180, 60, 60)), ('rect', 0, 10, 16, 2, (180, 60, 60)), ('rect', 0, 14, 16, 2, (180, 60, 60)), ('rect', 2, 4, 12, 1, (210, 90, 90))]),
        buff_id=33, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=5, light_level=0),

    598: BlockType(id=598, name="physical_immune_a", name2="物理免疫·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 3, 0, 3, 16, (80, 220, 120)), ('rect', 10, 0, 3, 12, (100, 240, 140)), ('rect', 6, 4, 2, 8, (60, 200, 100))]),
        buff_id=34, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=0),

    599: BlockType(id=599, name="physical_immune_b", name2="物理免疫·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 1, 8, 3, (60, 200, 220)), ('rect', 10, 1, 6, 3, (60, 200, 220)), ('rect', 0, 7, 6, 3, (60, 200, 220)), ('rect', 8, 7, 8, 3, (60, 200, 220)), ('rect', 0, 13, 8, 3, (60, 200, 220)), ('rect', 10, 13, 6, 3, (60, 200, 220))]),
        buff_id=34, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=3),

    600: BlockType(id=600, name="physical_immune_c", name2="物理免疫·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('circle', 4, 4, 2, (220, 200, 80)), ('circle', 12, 4, 2, (220, 200, 80)), ('circle', 4, 12, 2, (220, 200, 80)), ('circle', 12, 12, 2, (220, 200, 80)), ('circle', 8, 8, 2, (250, 230, 110))]),
        buff_id=34, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=8, light_level=1),

    601: BlockType(id=601, name="physical_immune_d", name2="物理免疫·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 3, (100, 160, 240)), ('rect', 0, 8, 16, 3, (120, 180, 255)), ('rect', 0, 14, 16, 2, (100, 160, 240))]),
        buff_id=34, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=6, light_level=0),

    602: BlockType(id=602, name="physical_immune_e", name2="物理免疫·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 0, 0, 8, 8, (180, 140, 220)), ('rect', 8, 8, 8, 8, (180, 140, 220)), ('rect', 8, 0, 8, 8, (210, 170, 250)), ('rect', 0, 8, 8, 8, (210, 170, 250))]),
        buff_id=34, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=5, light_level=3),

    603: BlockType(id=603, name="physical_immune_f", name2="物理免疫·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 6, 2, 4, 12, (60, 240, 160)), ('rect', 2, 6, 12, 4, (60, 240, 160)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=34, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=1),

    604: BlockType(id=604, name="magic_immune_a", name2="法术免疫·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 8, 1, 2, 14, (80, 220, 120)), ('rect', 1, 8, 14, 2, (80, 220, 120)), ('circle', 8, 8, 3, (110, 250, 150))]),
        buff_id=35, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=3, light_level=1),

    605: BlockType(id=605, name="magic_immune_b", name2="法术免疫·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('circle', 8, 8, 6, (60, 200, 220)), ('circle', 8, 8, 4, (80, 220, 240)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=35, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=0),

    606: BlockType(id=606, name="magic_immune_c", name2="法术免疫·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 2, 1, 4, 5, (220, 200, 80)), ('rect', 8, 1, 4, 5, (220, 200, 80)), ('rect', 5, 4, 4, 5, (220, 200, 80)), ('rect', 11, 4, 4, 5, (220, 200, 80)), ('rect', 2, 10, 4, 5, (220, 200, 80)), ('rect', 8, 10, 4, 5, (220, 200, 80))]),
        buff_id=35, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=10, light_level=0),

    607: BlockType(id=607, name="magic_immune_d", name2="法术免疫·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 2, (100, 160, 240)), ('rect', 0, 6, 16, 2, (100, 160, 240)), ('rect', 0, 10, 16, 2, (100, 160, 240)), ('rect', 0, 14, 16, 2, (100, 160, 240)), ('rect', 2, 4, 12, 1, (130, 190, 255))]),
        buff_id=35, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=0),

    608: BlockType(id=608, name="magic_immune_e", name2="法术免疫·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 3, 0, 3, 16, (180, 140, 220)), ('rect', 10, 0, 3, 12, (200, 160, 240)), ('rect', 6, 4, 2, 8, (160, 120, 200))]),
        buff_id=35, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=0),

    609: BlockType(id=609, name="magic_immune_f", name2="法术免疫·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 1, 8, 3, (60, 240, 160)), ('rect', 10, 1, 6, 3, (60, 240, 160)), ('rect', 0, 7, 6, 3, (60, 240, 160)), ('rect', 8, 7, 8, 3, (60, 240, 160)), ('rect', 0, 13, 8, 3, (60, 240, 160)), ('rect', 10, 13, 6, 3, (60, 240, 160))]),
        buff_id=35, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=6, light_level=1),

    610: BlockType(id=610, name="full_immune_a", name2="完全免疫·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('circle', 4, 4, 2, (80, 220, 120)), ('circle', 12, 4, 2, (80, 220, 120)), ('circle', 4, 12, 2, (80, 220, 120)), ('circle', 12, 12, 2, (80, 220, 120)), ('circle', 8, 8, 2, (110, 250, 150))]),
        buff_id=36, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=8, light_level=0),

    611: BlockType(id=611, name="full_immune_b", name2="完全免疫·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 3, (60, 200, 220)), ('rect', 0, 8, 16, 3, (80, 220, 240)), ('rect', 0, 14, 16, 2, (60, 200, 220))]),
        buff_id=36, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=4, light_level=0),

    612: BlockType(id=612, name="full_immune_c", name2="完全免疫·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 0, 0, 8, 8, (220, 200, 80)), ('rect', 8, 8, 8, 8, (220, 200, 80)), ('rect', 8, 0, 8, 8, (250, 230, 110)), ('rect', 0, 8, 8, 8, (250, 230, 110))]),
        buff_id=36, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=8, light_level=3),

    613: BlockType(id=613, name="full_immune_d", name2="完全免疫·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 6, 2, 4, 12, (100, 160, 240)), ('rect', 2, 6, 12, 4, (100, 160, 240)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=36, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=9, light_level=3),

    614: BlockType(id=614, name="full_immune_e", name2="完全免疫·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 8, 1, 2, 14, (180, 140, 220)), ('rect', 1, 8, 14, 2, (180, 140, 220)), ('circle', 8, 8, 3, (210, 170, 250))]),
        buff_id=36, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=8, light_level=0),

    615: BlockType(id=615, name="full_immune_f", name2="完全免疫·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('circle', 8, 8, 6, (60, 240, 160)), ('circle', 8, 8, 4, (80, 255, 180)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=36, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=0),

    616: BlockType(id=616, name="double_jump_a", name2="二段跳·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=37, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=5, light_level=2),

    617: BlockType(id=617, name="double_jump_b", name2="二段跳·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=37, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=0),

    618: BlockType(id=618, name="double_jump_c", name2="二段跳·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=37, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=4, light_level=2),

    619: BlockType(id=619, name="double_jump_d", name2="二段跳·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=37, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=9, light_level=0),

    620: BlockType(id=620, name="double_jump_e", name2="二段跳·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=37, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=8, light_level=1),

    621: BlockType(id=621, name="double_jump_f", name2="二段跳·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=37, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=1),

    622: BlockType(id=622, name="stealth_a", name2="隐身·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=38, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=6, light_level=0),

    623: BlockType(id=623, name="stealth_b", name2="隐身·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=38, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=3, light_level=3),

    624: BlockType(id=624, name="stealth_c", name2="隐身·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=38, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=0),

    625: BlockType(id=625, name="stealth_d", name2="隐身·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=38, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=6, light_level=0),

    626: BlockType(id=626, name="stealth_e", name2="隐身·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=38, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=9, light_level=0),

    627: BlockType(id=627, name="stealth_f", name2="隐身·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=38, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=8, light_level=2),

    628: BlockType(id=628, name="stone_skin_a", name2="石肤·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 3, 0, 3, 16, (80, 220, 120)), ('rect', 10, 0, 3, 12, (100, 240, 140)), ('rect', 6, 4, 2, 8, (60, 200, 100))]),
        buff_id=39, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=8, light_level=3),

    629: BlockType(id=629, name="stone_skin_b", name2="石肤·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 1, 8, 3, (60, 200, 220)), ('rect', 10, 1, 6, 3, (60, 200, 220)), ('rect', 0, 7, 6, 3, (60, 200, 220)), ('rect', 8, 7, 8, 3, (60, 200, 220)), ('rect', 0, 13, 8, 3, (60, 200, 220)), ('rect', 10, 13, 6, 3, (60, 200, 220))]),
        buff_id=39, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=4, light_level=3),

    630: BlockType(id=630, name="stone_skin_c", name2="石肤·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('circle', 4, 4, 2, (220, 200, 80)), ('circle', 12, 4, 2, (220, 200, 80)), ('circle', 4, 12, 2, (220, 200, 80)), ('circle', 12, 12, 2, (220, 200, 80)), ('circle', 8, 8, 2, (250, 230, 110))]),
        buff_id=39, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=7, light_level=2),

    631: BlockType(id=631, name="stone_skin_d", name2="石肤·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 3, (100, 160, 240)), ('rect', 0, 8, 16, 3, (120, 180, 255)), ('rect', 0, 14, 16, 2, (100, 160, 240))]),
        buff_id=39, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=7, light_level=3),

    632: BlockType(id=632, name="stone_skin_e", name2="石肤·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 0, 0, 8, 8, (180, 140, 220)), ('rect', 8, 8, 8, 8, (180, 140, 220)), ('rect', 8, 0, 8, 8, (210, 170, 250)), ('rect', 0, 8, 8, 8, (210, 170, 250))]),
        buff_id=39, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=9, light_level=0),

    633: BlockType(id=633, name="stone_skin_f", name2="石肤·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 6, 2, 4, 12, (60, 240, 160)), ('rect', 2, 6, 12, 4, (60, 240, 160)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=39, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=9, light_level=3),

    634: BlockType(id=634, name="iron_will_a", name2="铁意·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 8, 1, 2, 14, (80, 220, 120)), ('rect', 1, 8, 14, 2, (80, 220, 120)), ('circle', 8, 8, 3, (110, 250, 150))]),
        buff_id=40, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=7, light_level=2),

    635: BlockType(id=635, name="iron_will_b", name2="铁意·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('circle', 8, 8, 6, (60, 200, 220)), ('circle', 8, 8, 4, (80, 220, 240)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=40, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=0),

    636: BlockType(id=636, name="iron_will_c", name2="铁意·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 2, 1, 4, 5, (220, 200, 80)), ('rect', 8, 1, 4, 5, (220, 200, 80)), ('rect', 5, 4, 4, 5, (220, 200, 80)), ('rect', 11, 4, 4, 5, (220, 200, 80)), ('rect', 2, 10, 4, 5, (220, 200, 80)), ('rect', 8, 10, 4, 5, (220, 200, 80))]),
        buff_id=40, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=3),

    637: BlockType(id=637, name="iron_will_d", name2="铁意·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 2, (100, 160, 240)), ('rect', 0, 6, 16, 2, (100, 160, 240)), ('rect', 0, 10, 16, 2, (100, 160, 240)), ('rect', 0, 14, 16, 2, (100, 160, 240)), ('rect', 2, 4, 12, 1, (130, 190, 255))]),
        buff_id=40, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=9, light_level=3),

    638: BlockType(id=638, name="iron_will_e", name2="铁意·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 3, 0, 3, 16, (180, 140, 220)), ('rect', 10, 0, 3, 12, (200, 160, 240)), ('rect', 6, 4, 2, 8, (160, 120, 200))]),
        buff_id=40, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=5, light_level=2),

    639: BlockType(id=639, name="iron_will_f", name2="铁意·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 1, 8, 3, (60, 240, 160)), ('rect', 10, 1, 6, 3, (60, 240, 160)), ('rect', 0, 7, 6, 3, (60, 240, 160)), ('rect', 8, 7, 8, 3, (60, 240, 160)), ('rect', 0, 13, 8, 3, (60, 240, 160)), ('rect', 10, 13, 6, 3, (60, 240, 160))]),
        buff_id=40, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=7, light_level=1),

    640: BlockType(id=640, name="surefooted_a", name2="稳足·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('circle', 4, 4, 2, (80, 220, 120)), ('circle', 12, 4, 2, (80, 220, 120)), ('circle', 4, 12, 2, (80, 220, 120)), ('circle', 12, 12, 2, (80, 220, 120)), ('circle', 8, 8, 2, (110, 250, 150))]),
        buff_id=41, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=3, light_level=0),

    641: BlockType(id=641, name="surefooted_b", name2="稳足·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 3, (60, 200, 220)), ('rect', 0, 8, 16, 3, (80, 220, 240)), ('rect', 0, 14, 16, 2, (60, 200, 220))]),
        buff_id=41, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=0),

    642: BlockType(id=642, name="surefooted_c", name2="稳足·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 0, 0, 8, 8, (220, 200, 80)), ('rect', 8, 8, 8, 8, (220, 200, 80)), ('rect', 8, 0, 8, 8, (250, 230, 110)), ('rect', 0, 8, 8, 8, (250, 230, 110))]),
        buff_id=41, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=2),

    643: BlockType(id=643, name="surefooted_d", name2="稳足·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 6, 2, 4, 12, (100, 160, 240)), ('rect', 2, 6, 12, 4, (100, 160, 240)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=41, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=8, light_level=1),

    644: BlockType(id=644, name="surefooted_e", name2="稳足·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 8, 1, 2, 14, (180, 140, 220)), ('rect', 1, 8, 14, 2, (180, 140, 220)), ('circle', 8, 8, 3, (210, 170, 250))]),
        buff_id=41, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=10, light_level=1),

    645: BlockType(id=645, name="surefooted_f", name2="稳足·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('circle', 8, 8, 6, (60, 240, 160)), ('circle', 8, 8, 4, (80, 255, 180)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=41, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=6, light_level=2),

    646: BlockType(id=646, name="slick_a", name2="滑腻·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 2, 1, 4, 5, (160, 160, 180)), ('rect', 8, 1, 4, 5, (160, 160, 180)), ('rect', 5, 4, 4, 5, (160, 160, 180)), ('rect', 11, 4, 4, 5, (160, 160, 180)), ('rect', 2, 10, 4, 5, (160, 160, 180)), ('rect', 8, 10, 4, 5, (160, 160, 180))]),
        buff_id=42, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=10, light_level=3),

    647: BlockType(id=647, name="slick_b", name2="滑腻·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('rect', 0, 2, 16, 2, (180, 160, 140)), ('rect', 0, 6, 16, 2, (180, 160, 140)), ('rect', 0, 10, 16, 2, (180, 160, 140)), ('rect', 0, 14, 16, 2, (180, 160, 140)), ('rect', 2, 4, 12, 1, (210, 190, 170))]),
        buff_id=42, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=5, light_level=3),

    648: BlockType(id=648, name="slick_c", name2="滑腻·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('rect', 3, 0, 3, 16, (140, 160, 180)), ('rect', 10, 0, 3, 12, (160, 180, 200)), ('rect', 6, 4, 2, 8, (120, 140, 160))]),
        buff_id=42, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=4, light_level=0),

    649: BlockType(id=649, name="slick_d", name2="滑腻·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 0, 1, 8, 3, (160, 180, 160)), ('rect', 10, 1, 6, 3, (160, 180, 160)), ('rect', 0, 7, 6, 3, (160, 180, 160)), ('rect', 8, 7, 8, 3, (160, 180, 160)), ('rect', 0, 13, 8, 3, (160, 180, 160)), ('rect', 10, 13, 6, 3, (160, 180, 160))]),
        buff_id=42, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=8, light_level=0),

    650: BlockType(id=650, name="slick_e", name2="滑腻·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('circle', 4, 4, 2, (180, 140, 180)), ('circle', 12, 4, 2, (180, 140, 180)), ('circle', 4, 12, 2, (180, 140, 180)), ('circle', 12, 12, 2, (180, 140, 180)), ('circle', 8, 8, 2, (210, 170, 210))]),
        buff_id=42, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=6, light_level=3),

    651: BlockType(id=651, name="slick_f", name2="滑腻·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 0, 2, 16, 3, (140, 180, 160)), ('rect', 0, 8, 16, 3, (160, 200, 180)), ('rect', 0, 14, 16, 2, (140, 180, 160))]),
        buff_id=42, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=7, light_level=0),

    652: BlockType(id=652, name="sticky_a", name2="黏着·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 0, 0, 8, 8, (160, 160, 180)), ('rect', 8, 8, 8, 8, (160, 160, 180)), ('rect', 8, 0, 8, 8, (190, 190, 210)), ('rect', 0, 8, 8, 8, (190, 190, 210))]),
        buff_id=43, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=0),

    653: BlockType(id=653, name="sticky_b", name2="黏着·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('rect', 6, 2, 4, 12, (180, 160, 140)), ('rect', 2, 6, 12, 4, (180, 160, 140)), ('circle', 8, 8, 2, (220, 200, 180))]),
        buff_id=43, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=3, light_level=0),

    654: BlockType(id=654, name="sticky_c", name2="黏着·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('rect', 8, 1, 2, 14, (140, 160, 180)), ('rect', 1, 8, 14, 2, (140, 160, 180)), ('circle', 8, 8, 3, (170, 190, 210))]),
        buff_id=43, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=6, light_level=1),

    655: BlockType(id=655, name="sticky_d", name2="黏着·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('circle', 8, 8, 6, (160, 180, 160)), ('circle', 8, 8, 4, (180, 200, 180)), ('circle', 8, 8, 2, (200, 220, 200))]),
        buff_id=43, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=4, light_level=1),

    656: BlockType(id=656, name="sticky_e", name2="黏着·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 2, 1, 4, 5, (180, 140, 180)), ('rect', 8, 1, 4, 5, (180, 140, 180)), ('rect', 5, 4, 4, 5, (180, 140, 180)), ('rect', 11, 4, 4, 5, (180, 140, 180)), ('rect', 2, 10, 4, 5, (180, 140, 180)), ('rect', 8, 10, 4, 5, (180, 140, 180))]),
        buff_id=43, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=9, light_level=3),

    657: BlockType(id=657, name="sticky_f", name2="黏着·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 0, 2, 16, 2, (140, 180, 160)), ('rect', 0, 6, 16, 2, (140, 180, 160)), ('rect', 0, 10, 16, 2, (140, 180, 160)), ('rect', 0, 14, 16, 2, (140, 180, 160)), ('rect', 2, 4, 12, 1, (170, 210, 190))]),
        buff_id=43, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=6, light_level=3),

    658: BlockType(id=658, name="drowsy_a", name2="困倦·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 3, 0, 3, 16, (240, 80, 60)), ('rect', 10, 0, 3, 12, (255, 100, 80)), ('rect', 6, 4, 2, 8, (220, 60, 40))]),
        buff_id=44, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=9, light_level=1),

    659: BlockType(id=659, name="drowsy_b", name2="困倦·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 1, 8, 3, (200, 60, 100)), ('rect', 10, 1, 6, 3, (200, 60, 100)), ('rect', 0, 7, 6, 3, (200, 60, 100)), ('rect', 8, 7, 8, 3, (200, 60, 100)), ('rect', 0, 13, 8, 3, (200, 60, 100)), ('rect', 10, 13, 6, 3, (200, 60, 100))]),
        buff_id=44, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=9, light_level=0),

    660: BlockType(id=660, name="drowsy_c", name2="困倦·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('circle', 4, 4, 2, (160, 50, 50)), ('circle', 12, 4, 2, (160, 50, 50)), ('circle', 4, 12, 2, (160, 50, 50)), ('circle', 12, 12, 2, (160, 50, 50)), ('circle', 8, 8, 2, (190, 80, 80))]),
        buff_id=44, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=5, light_level=3),

    661: BlockType(id=661, name="drowsy_d", name2="困倦·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 3, (200, 80, 30)), ('rect', 0, 8, 16, 3, (220, 100, 50)), ('rect', 0, 14, 16, 2, (200, 80, 30))]),
        buff_id=44, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=3, light_level=0),

    662: BlockType(id=662, name="drowsy_e", name2="困倦·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 0, 0, 8, 8, (140, 40, 80)), ('rect', 8, 8, 8, 8, (140, 40, 80)), ('rect', 8, 0, 8, 8, (170, 70, 110)), ('rect', 0, 8, 8, 8, (170, 70, 110))]),
        buff_id=44, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=9, light_level=0),

    663: BlockType(id=663, name="drowsy_f", name2="困倦·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 6, 2, 4, 12, (180, 60, 60)), ('rect', 2, 6, 12, 4, (180, 60, 60)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=44, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=5, light_level=3),

    664: BlockType(id=664, name="electrified_a", name2="带电·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 8, 1, 2, 14, (160, 160, 180)), ('rect', 1, 8, 14, 2, (160, 160, 180)), ('circle', 8, 8, 3, (190, 190, 210))]),
        buff_id=45, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=10, light_level=0),

    665: BlockType(id=665, name="electrified_b", name2="带电·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('circle', 8, 8, 6, (180, 160, 140)), ('circle', 8, 8, 4, (200, 180, 160)), ('circle', 8, 8, 2, (220, 200, 180))]),
        buff_id=45, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=6, light_level=0),

    666: BlockType(id=666, name="electrified_c", name2="带电·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('rect', 2, 1, 4, 5, (140, 160, 180)), ('rect', 8, 1, 4, 5, (140, 160, 180)), ('rect', 5, 4, 4, 5, (140, 160, 180)), ('rect', 11, 4, 4, 5, (140, 160, 180)), ('rect', 2, 10, 4, 5, (140, 160, 180)), ('rect', 8, 10, 4, 5, (140, 160, 180))]),
        buff_id=45, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=10, light_level=0),

    667: BlockType(id=667, name="electrified_d", name2="带电·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 0, 2, 16, 2, (160, 180, 160)), ('rect', 0, 6, 16, 2, (160, 180, 160)), ('rect', 0, 10, 16, 2, (160, 180, 160)), ('rect', 0, 14, 16, 2, (160, 180, 160)), ('rect', 2, 4, 12, 1, (190, 210, 190))]),
        buff_id=45, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=10, light_level=3),

    668: BlockType(id=668, name="electrified_e", name2="带电·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 3, 0, 3, 16, (180, 140, 180)), ('rect', 10, 0, 3, 12, (200, 160, 200)), ('rect', 6, 4, 2, 8, (160, 120, 160))]),
        buff_id=45, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=8, light_level=1),

    669: BlockType(id=669, name="electrified_f", name2="带电·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 0, 1, 8, 3, (140, 180, 160)), ('rect', 10, 1, 6, 3, (140, 180, 160)), ('rect', 0, 7, 6, 3, (140, 180, 160)), ('rect', 8, 7, 8, 3, (140, 180, 160)), ('rect', 0, 13, 8, 3, (140, 180, 160)), ('rect', 10, 13, 6, 3, (140, 180, 160))]),
        buff_id=45, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=9, light_level=2),

    670: BlockType(id=670, name="inflamed_a", name2="发炎·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=46, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=10, light_level=0),

    671: BlockType(id=671, name="inflamed_b", name2="发炎·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=46, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=10, light_level=1),

    672: BlockType(id=672, name="inflamed_c", name2="发炎·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=46, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=7, light_level=0),

    673: BlockType(id=673, name="inflamed_d", name2="发炎·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=46, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=7, light_level=2),

    674: BlockType(id=674, name="inflamed_e", name2="发炎·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=46, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=10, light_level=3),

    675: BlockType(id=675, name="inflamed_f", name2="发炎·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=46, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=6, light_level=0),

    676: BlockType(id=676, name="berserk_a", name2="狂暴·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=47, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=10, light_level=0),

    677: BlockType(id=677, name="berserk_b", name2="狂暴·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=47, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=7, light_level=0),

    678: BlockType(id=678, name="berserk_c", name2="狂暴·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=47, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=7, light_level=0),

    679: BlockType(id=679, name="berserk_d", name2="狂暴·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=47, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=8, light_level=2),

    680: BlockType(id=680, name="berserk_e", name2="狂暴·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=47, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=4, light_level=0),

    681: BlockType(id=681, name="berserk_f", name2="狂暴·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=47, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=5, light_level=0),

    682: BlockType(id=682, name="ghostly_a", name2="幽灵·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=48, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=3),

    683: BlockType(id=683, name="ghostly_b", name2="幽灵·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=48, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=5, light_level=3),

    684: BlockType(id=684, name="ghostly_c", name2="幽灵·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=48, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=6, light_level=0),

    685: BlockType(id=685, name="ghostly_d", name2="幽灵·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=48, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=9, light_level=1),

    686: BlockType(id=686, name="ghostly_e", name2="幽灵·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=48, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=8, light_level=2),

    687: BlockType(id=687, name="ghostly_f", name2="幽灵·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=48, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=10, light_level=1),

    688: BlockType(id=688, name="magnetized_a", name2="磁化·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('rect', 3, 0, 3, 16, (160, 160, 180)), ('rect', 10, 0, 3, 12, (180, 180, 200)), ('rect', 6, 4, 2, 8, (140, 140, 160))]),
        buff_id=49, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=3, light_level=0),

    689: BlockType(id=689, name="magnetized_b", name2="磁化·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('rect', 0, 1, 8, 3, (180, 160, 140)), ('rect', 10, 1, 6, 3, (180, 160, 140)), ('rect', 0, 7, 6, 3, (180, 160, 140)), ('rect', 8, 7, 8, 3, (180, 160, 140)), ('rect', 0, 13, 8, 3, (180, 160, 140)), ('rect', 10, 13, 6, 3, (180, 160, 140))]),
        buff_id=49, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=9, light_level=1),

    690: BlockType(id=690, name="magnetized_c", name2="磁化·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('circle', 4, 4, 2, (140, 160, 180)), ('circle', 12, 4, 2, (140, 160, 180)), ('circle', 4, 12, 2, (140, 160, 180)), ('circle', 12, 12, 2, (140, 160, 180)), ('circle', 8, 8, 2, (170, 190, 210))]),
        buff_id=49, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=3, light_level=2),

    691: BlockType(id=691, name="magnetized_d", name2="磁化·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 0, 2, 16, 3, (160, 180, 160)), ('rect', 0, 8, 16, 3, (180, 200, 180)), ('rect', 0, 14, 16, 2, (160, 180, 160))]),
        buff_id=49, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=9, light_level=1),

    692: BlockType(id=692, name="magnetized_e", name2="磁化·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 0, 0, 8, 8, (180, 140, 180)), ('rect', 8, 8, 8, 8, (180, 140, 180)), ('rect', 8, 0, 8, 8, (210, 170, 210)), ('rect', 0, 8, 8, 8, (210, 170, 210))]),
        buff_id=49, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=3, light_level=0),

    693: BlockType(id=693, name="magnetized_f", name2="磁化·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('rect', 6, 2, 4, 12, (140, 180, 160)), ('rect', 2, 6, 12, 4, (140, 180, 160)), ('circle', 8, 8, 2, (180, 220, 200))]),
        buff_id=49, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=7, light_level=1),

    694: BlockType(id=694, name="glowing_a", name2="发光·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 8, 1, 2, 14, (80, 220, 120)), ('rect', 1, 8, 14, 2, (80, 220, 120)), ('circle', 8, 8, 3, (110, 250, 150))]),
        buff_id=50, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=2),

    695: BlockType(id=695, name="glowing_b", name2="发光·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('circle', 8, 8, 6, (60, 200, 220)), ('circle', 8, 8, 4, (80, 220, 240)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=50, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=1),

    696: BlockType(id=696, name="glowing_c", name2="发光·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 2, 1, 4, 5, (220, 200, 80)), ('rect', 8, 1, 4, 5, (220, 200, 80)), ('rect', 5, 4, 4, 5, (220, 200, 80)), ('rect', 11, 4, 4, 5, (220, 200, 80)), ('rect', 2, 10, 4, 5, (220, 200, 80)), ('rect', 8, 10, 4, 5, (220, 200, 80))]),
        buff_id=50, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=6, light_level=0),

    697: BlockType(id=697, name="glowing_d", name2="发光·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 2, (100, 160, 240)), ('rect', 0, 6, 16, 2, (100, 160, 240)), ('rect', 0, 10, 16, 2, (100, 160, 240)), ('rect', 0, 14, 16, 2, (100, 160, 240)), ('rect', 2, 4, 12, 1, (130, 190, 255))]),
        buff_id=50, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=9, light_level=1),

    698: BlockType(id=698, name="glowing_e", name2="发光·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 3, 0, 3, 16, (180, 140, 220)), ('rect', 10, 0, 3, 12, (200, 160, 240)), ('rect', 6, 4, 2, 8, (160, 120, 200))]),
        buff_id=50, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=3, light_level=1),

    699: BlockType(id=699, name="glowing_f", name2="发光·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 1, 8, 3, (60, 240, 160)), ('rect', 10, 1, 6, 3, (60, 240, 160)), ('rect', 0, 7, 6, 3, (60, 240, 160)), ('rect', 8, 7, 8, 3, (60, 240, 160)), ('rect', 0, 13, 8, 3, (60, 240, 160)), ('rect', 10, 13, 6, 3, (60, 240, 160))]),
        buff_id=50, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=8, light_level=3),

    700: BlockType(id=700, name="chilled_a", name2="寒冷·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('circle', 4, 4, 2, (240, 80, 60)), ('circle', 12, 4, 2, (240, 80, 60)), ('circle', 4, 12, 2, (240, 80, 60)), ('circle', 12, 12, 2, (240, 80, 60)), ('circle', 8, 8, 2, (255, 110, 90))]),
        buff_id=51, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=9, light_level=3),

    701: BlockType(id=701, name="chilled_b", name2="寒冷·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 3, (200, 60, 100)), ('rect', 0, 8, 16, 3, (220, 80, 120)), ('rect', 0, 14, 16, 2, (200, 60, 100))]),
        buff_id=51, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=5, light_level=1),

    702: BlockType(id=702, name="chilled_c", name2="寒冷·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 0, 0, 8, 8, (160, 50, 50)), ('rect', 8, 8, 8, 8, (160, 50, 50)), ('rect', 8, 0, 8, 8, (190, 80, 80)), ('rect', 0, 8, 8, 8, (190, 80, 80))]),
        buff_id=51, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=5, light_level=2),

    703: BlockType(id=703, name="chilled_d", name2="寒冷·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 6, 2, 4, 12, (200, 80, 30)), ('rect', 2, 6, 12, 4, (200, 80, 30)), ('circle', 8, 8, 2, (240, 120, 70))]),
        buff_id=51, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=3, light_level=1),

    704: BlockType(id=704, name="chilled_e", name2="寒冷·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 8, 1, 2, 14, (140, 40, 80)), ('rect', 1, 8, 14, 2, (140, 40, 80)), ('circle', 8, 8, 3, (170, 70, 110))]),
        buff_id=51, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=3, light_level=0),

    705: BlockType(id=705, name="chilled_f", name2="寒冷·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('circle', 8, 8, 6, (180, 60, 60)), ('circle', 8, 8, 4, (200, 80, 80)), ('circle', 8, 8, 2, (220, 100, 100))]),
        buff_id=51, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=9, light_level=0),

    706: BlockType(id=706, name="lucky_a", name2="幸运·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 2, 1, 4, 5, (80, 220, 120)), ('rect', 8, 1, 4, 5, (80, 220, 120)), ('rect', 5, 4, 4, 5, (80, 220, 120)), ('rect', 11, 4, 4, 5, (80, 220, 120)), ('rect', 2, 10, 4, 5, (80, 220, 120)), ('rect', 8, 10, 4, 5, (80, 220, 120))]),
        buff_id=52, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=10, light_level=0),

    707: BlockType(id=707, name="lucky_b", name2="幸运·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 2, 16, 2, (60, 200, 220)), ('rect', 0, 6, 16, 2, (60, 200, 220)), ('rect', 0, 10, 16, 2, (60, 200, 220)), ('rect', 0, 14, 16, 2, (60, 200, 220)), ('rect', 2, 4, 12, 1, (90, 230, 250))]),
        buff_id=52, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=3, light_level=0),

    708: BlockType(id=708, name="lucky_c", name2="幸运·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 3, 0, 3, 16, (220, 200, 80)), ('rect', 10, 0, 3, 12, (240, 220, 100)), ('rect', 6, 4, 2, 8, (200, 180, 60))]),
        buff_id=52, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=9, light_level=0),

    709: BlockType(id=709, name="lucky_d", name2="幸运·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 1, 8, 3, (100, 160, 240)), ('rect', 10, 1, 6, 3, (100, 160, 240)), ('rect', 0, 7, 6, 3, (100, 160, 240)), ('rect', 8, 7, 8, 3, (100, 160, 240)), ('rect', 0, 13, 8, 3, (100, 160, 240)), ('rect', 10, 13, 6, 3, (100, 160, 240))]),
        buff_id=52, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=6, light_level=1),

    710: BlockType(id=710, name="lucky_e", name2="幸运·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('circle', 4, 4, 2, (180, 140, 220)), ('circle', 12, 4, 2, (180, 140, 220)), ('circle', 4, 12, 2, (180, 140, 220)), ('circle', 12, 12, 2, (180, 140, 220)), ('circle', 8, 8, 2, (210, 170, 250))]),
        buff_id=52, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=8, light_level=0),

    711: BlockType(id=711, name="lucky_f", name2="幸运·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 3, (60, 240, 160)), ('rect', 0, 8, 16, 3, (80, 255, 180)), ('rect', 0, 14, 16, 2, (60, 240, 160))]),
        buff_id=52, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=9, light_level=0),

    712: BlockType(id=712, name="wind_walk_a", name2="风步·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 0, 0, 8, 8, (80, 220, 120)), ('rect', 8, 8, 8, 8, (80, 220, 120)), ('rect', 8, 0, 8, 8, (110, 250, 150)), ('rect', 0, 8, 8, 8, (110, 250, 150))]),
        buff_id=53, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=9, light_level=0),

    713: BlockType(id=713, name="wind_walk_b", name2="风步·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 6, 2, 4, 12, (60, 200, 220)), ('rect', 2, 6, 12, 4, (60, 200, 220)), ('circle', 8, 8, 2, (100, 240, 255))]),
        buff_id=53, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=4, light_level=1),

    714: BlockType(id=714, name="wind_walk_c", name2="风步·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('rect', 8, 1, 2, 14, (220, 200, 80)), ('rect', 1, 8, 14, 2, (220, 200, 80)), ('circle', 8, 8, 3, (250, 230, 110))]),
        buff_id=53, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=3, light_level=3),

    715: BlockType(id=715, name="wind_walk_d", name2="风步·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('circle', 8, 8, 6, (100, 160, 240)), ('circle', 8, 8, 4, (120, 180, 255)), ('circle', 8, 8, 2, (140, 200, 255))]),
        buff_id=53, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=3, light_level=0),

    716: BlockType(id=716, name="wind_walk_e", name2="风步·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 2, 1, 4, 5, (180, 140, 220)), ('rect', 8, 1, 4, 5, (180, 140, 220)), ('rect', 5, 4, 4, 5, (180, 140, 220)), ('rect', 11, 4, 4, 5, (180, 140, 220)), ('rect', 2, 10, 4, 5, (180, 140, 220)), ('rect', 8, 10, 4, 5, (180, 140, 220))]),
        buff_id=53, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=6, light_level=3),

    717: BlockType(id=717, name="wind_walk_f", name2="风步·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 0, 2, 16, 2, (60, 240, 160)), ('rect', 0, 6, 16, 2, (60, 240, 160)), ('rect', 0, 10, 16, 2, (60, 240, 160)), ('rect', 0, 14, 16, 2, (60, 240, 160)), ('rect', 2, 4, 12, 1, (90, 255, 190))]),
        buff_id=53, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=3),

    718: BlockType(id=718, name="anchored_a", name2="定锚·壹",
        is_solid=True, color=(30, 140, 60), pattern=('vector', (16, 16), [('fill', (30, 140, 60)), ('rect', 3, 0, 3, 16, (80, 220, 120)), ('rect', 10, 0, 3, 12, (100, 240, 140)), ('rect', 6, 4, 2, 8, (60, 200, 100))]),
        buff_id=54, buff_params=(2,), buff_duration=5.0,
        break_hp=40, break_level=3, light_level=0),

    719: BlockType(id=719, name="anchored_b", name2="定锚·贰",
        is_solid=True, color=(20, 100, 120), pattern=('vector', (16, 16), [('fill', (20, 100, 120)), ('rect', 0, 1, 8, 3, (60, 200, 220)), ('rect', 10, 1, 6, 3, (60, 200, 220)), ('rect', 0, 7, 6, 3, (60, 200, 220)), ('rect', 8, 7, 8, 3, (60, 200, 220)), ('rect', 0, 13, 8, 3, (60, 200, 220)), ('rect', 10, 13, 6, 3, (60, 200, 220))]),
        buff_id=54, buff_params=(4,), buff_duration=8.0,
        break_hp=55, break_level=6, light_level=0),

    720: BlockType(id=720, name="anchored_c", name2="定锚·叁",
        is_solid=True, color=(140, 120, 30), pattern=('vector', (16, 16), [('fill', (140, 120, 30)), ('circle', 4, 4, 2, (220, 200, 80)), ('circle', 12, 4, 2, (220, 200, 80)), ('circle', 4, 12, 2, (220, 200, 80)), ('circle', 12, 12, 2, (220, 200, 80)), ('circle', 8, 8, 2, (250, 230, 110))]),
        buff_id=54, buff_params=(6,), buff_duration=11.0,
        break_hp=70, break_level=3, light_level=2),

    721: BlockType(id=721, name="anchored_d", name2="定锚·肆",
        is_solid=True, color=(40, 80, 160), pattern=('vector', (16, 16), [('fill', (40, 80, 160)), ('rect', 0, 2, 16, 3, (100, 160, 240)), ('rect', 0, 8, 16, 3, (120, 180, 255)), ('rect', 0, 14, 16, 2, (100, 160, 240))]),
        buff_id=54, buff_params=(8,), buff_duration=14.0,
        break_hp=85, break_level=5, light_level=0),

    722: BlockType(id=722, name="anchored_e", name2="定锚·伍",
        is_solid=True, color=(100, 60, 140), pattern=('vector', (16, 16), [('fill', (100, 60, 140)), ('rect', 0, 0, 8, 8, (180, 140, 220)), ('rect', 8, 8, 8, 8, (180, 140, 220)), ('rect', 8, 0, 8, 8, (210, 170, 250)), ('rect', 0, 8, 8, 8, (210, 170, 250))]),
        buff_id=54, buff_params=(10,), buff_duration=17.0,
        break_hp=100, break_level=5, light_level=1),

    723: BlockType(id=723, name="anchored_f", name2="定锚·陆",
        is_solid=True, color=(20, 160, 100), pattern=('vector', (16, 16), [('fill', (20, 160, 100)), ('rect', 6, 2, 4, 12, (60, 240, 160)), ('rect', 2, 6, 12, 4, (60, 240, 160)), ('circle', 8, 8, 2, (100, 255, 200))]),
        buff_id=54, buff_params=(12,), buff_duration=20.0,
        break_hp=115, break_level=4, light_level=2),

    724: BlockType(id=724, name="parasitic_a", name2="寄生·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 8, 1, 2, 14, (240, 80, 60)), ('rect', 1, 8, 14, 2, (240, 80, 60)), ('circle', 8, 8, 3, (255, 110, 90))]),
        buff_id=55, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=6, light_level=1),

    725: BlockType(id=725, name="parasitic_b", name2="寄生·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('circle', 8, 8, 6, (200, 60, 100)), ('circle', 8, 8, 4, (220, 80, 120)), ('circle', 8, 8, 2, (240, 100, 140))]),
        buff_id=55, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=7, light_level=0),

    726: BlockType(id=726, name="parasitic_c", name2="寄生·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 2, 1, 4, 5, (160, 50, 50)), ('rect', 8, 1, 4, 5, (160, 50, 50)), ('rect', 5, 4, 4, 5, (160, 50, 50)), ('rect', 11, 4, 4, 5, (160, 50, 50)), ('rect', 2, 10, 4, 5, (160, 50, 50)), ('rect', 8, 10, 4, 5, (160, 50, 50))]),
        buff_id=55, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=5, light_level=2),

    727: BlockType(id=727, name="parasitic_d", name2="寄生·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 2, 16, 2, (200, 80, 30)), ('rect', 0, 6, 16, 2, (200, 80, 30)), ('rect', 0, 10, 16, 2, (200, 80, 30)), ('rect', 0, 14, 16, 2, (200, 80, 30)), ('rect', 2, 4, 12, 1, (230, 110, 60))]),
        buff_id=55, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=4, light_level=0),

    728: BlockType(id=728, name="parasitic_e", name2="寄生·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('rect', 3, 0, 3, 16, (140, 40, 80)), ('rect', 10, 0, 3, 12, (160, 60, 100)), ('rect', 6, 4, 2, 8, (120, 20, 60))]),
        buff_id=55, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=7, light_level=0),

    729: BlockType(id=729, name="parasitic_f", name2="寄生·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 1, 8, 3, (180, 60, 60)), ('rect', 10, 1, 6, 3, (180, 60, 60)), ('rect', 0, 7, 6, 3, (180, 60, 60)), ('rect', 8, 7, 8, 3, (180, 60, 60)), ('rect', 0, 13, 8, 3, (180, 60, 60)), ('rect', 10, 13, 6, 3, (180, 60, 60))]),
        buff_id=55, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=3, light_level=0),

    730: BlockType(id=730, name="echo_a", name2="回声·壹",
        is_solid=True, color=(100, 100, 120), pattern=('vector', (16, 16), [('fill', (100, 100, 120)), ('circle', 4, 4, 2, (160, 160, 180)), ('circle', 12, 4, 2, (160, 160, 180)), ('circle', 4, 12, 2, (160, 160, 180)), ('circle', 12, 12, 2, (160, 160, 180)), ('circle', 8, 8, 2, (190, 190, 210))]),
        buff_id=56, buff_params=(1,), buff_duration=3.0,
        break_hp=40, break_level=9, light_level=1),

    731: BlockType(id=731, name="echo_b", name2="回声·贰",
        is_solid=True, color=(120, 100, 80), pattern=('vector', (16, 16), [('fill', (120, 100, 80)), ('rect', 0, 2, 16, 3, (180, 160, 140)), ('rect', 0, 8, 16, 3, (200, 180, 160)), ('rect', 0, 14, 16, 2, (180, 160, 140))]),
        buff_id=56, buff_params=(2,), buff_duration=4.5,
        break_hp=55, break_level=6, light_level=0),

    732: BlockType(id=732, name="echo_c", name2="回声·叁",
        is_solid=True, color=(80, 100, 120), pattern=('vector', (16, 16), [('fill', (80, 100, 120)), ('rect', 0, 0, 8, 8, (140, 160, 180)), ('rect', 8, 8, 8, 8, (140, 160, 180)), ('rect', 8, 0, 8, 8, (170, 190, 210)), ('rect', 0, 8, 8, 8, (170, 190, 210))]),
        buff_id=56, buff_params=(3,), buff_duration=6.0,
        break_hp=70, break_level=6, light_level=0),

    733: BlockType(id=733, name="echo_d", name2="回声·肆",
        is_solid=True, color=(100, 120, 100), pattern=('vector', (16, 16), [('fill', (100, 120, 100)), ('rect', 6, 2, 4, 12, (160, 180, 160)), ('rect', 2, 6, 12, 4, (160, 180, 160)), ('circle', 8, 8, 2, (200, 220, 200))]),
        buff_id=56, buff_params=(4,), buff_duration=7.5,
        break_hp=85, break_level=7, light_level=3),

    734: BlockType(id=734, name="echo_e", name2="回声·伍",
        is_solid=True, color=(120, 80, 120), pattern=('vector', (16, 16), [('fill', (120, 80, 120)), ('rect', 8, 1, 2, 14, (180, 140, 180)), ('rect', 1, 8, 14, 2, (180, 140, 180)), ('circle', 8, 8, 3, (210, 170, 210))]),
        buff_id=56, buff_params=(5,), buff_duration=9.0,
        break_hp=100, break_level=4, light_level=2),

    735: BlockType(id=735, name="echo_f", name2="回声·陆",
        is_solid=True, color=(80, 120, 100), pattern=('vector', (16, 16), [('fill', (80, 120, 100)), ('circle', 8, 8, 6, (140, 180, 160)), ('circle', 8, 8, 4, (160, 200, 180)), ('circle', 8, 8, 2, (180, 220, 200))]),
        buff_id=56, buff_params=(6,), buff_duration=10.5,
        break_hp=115, break_level=3, light_level=0),

    736: BlockType(id=736, name="cursed_a", name2="诅咒·壹",
        is_solid=True, color=(180, 30, 30), pattern=('vector', (16, 16), [('fill', (180, 30, 30)), ('rect', 2, 1, 4, 5, (240, 80, 60)), ('rect', 8, 1, 4, 5, (240, 80, 60)), ('rect', 5, 4, 4, 5, (240, 80, 60)), ('rect', 11, 4, 4, 5, (240, 80, 60)), ('rect', 2, 10, 4, 5, (240, 80, 60)), ('rect', 8, 10, 4, 5, (240, 80, 60))]),
        buff_id=57, buff_params=(2,), buff_duration=3.0,
        break_hp=40, break_level=9, light_level=3),

    737: BlockType(id=737, name="cursed_b", name2="诅咒·贰",
        is_solid=True, color=(140, 20, 60), pattern=('vector', (16, 16), [('fill', (140, 20, 60)), ('rect', 0, 2, 16, 2, (200, 60, 100)), ('rect', 0, 6, 16, 2, (200, 60, 100)), ('rect', 0, 10, 16, 2, (200, 60, 100)), ('rect', 0, 14, 16, 2, (200, 60, 100)), ('rect', 2, 4, 12, 1, (230, 90, 130))]),
        buff_id=57, buff_params=(5,), buff_duration=5.0,
        break_hp=55, break_level=8, light_level=0),

    738: BlockType(id=738, name="cursed_c", name2="诅咒·叁",
        is_solid=True, color=(80, 20, 20), pattern=('vector', (16, 16), [('fill', (80, 20, 20)), ('rect', 3, 0, 3, 16, (160, 50, 50)), ('rect', 10, 0, 3, 12, (180, 70, 70)), ('rect', 6, 4, 2, 8, (140, 30, 30))]),
        buff_id=57, buff_params=(8,), buff_duration=7.0,
        break_hp=70, break_level=8, light_level=0),

    739: BlockType(id=739, name="cursed_d", name2="诅咒·肆",
        is_solid=True, color=(120, 40, 10), pattern=('vector', (16, 16), [('fill', (120, 40, 10)), ('rect', 0, 1, 8, 3, (200, 80, 30)), ('rect', 10, 1, 6, 3, (200, 80, 30)), ('rect', 0, 7, 6, 3, (200, 80, 30)), ('rect', 8, 7, 8, 3, (200, 80, 30)), ('rect', 0, 13, 8, 3, (200, 80, 30)), ('rect', 10, 13, 6, 3, (200, 80, 30))]),
        buff_id=57, buff_params=(11,), buff_duration=9.0,
        break_hp=85, break_level=9, light_level=1),

    740: BlockType(id=740, name="cursed_e", name2="诅咒·伍",
        is_solid=True, color=(60, 10, 40), pattern=('vector', (16, 16), [('fill', (60, 10, 40)), ('circle', 4, 4, 2, (140, 40, 80)), ('circle', 12, 4, 2, (140, 40, 80)), ('circle', 4, 12, 2, (140, 40, 80)), ('circle', 12, 12, 2, (140, 40, 80)), ('circle', 8, 8, 2, (170, 70, 110))]),
        buff_id=57, buff_params=(14,), buff_duration=11.0,
        break_hp=100, break_level=4, light_level=1),

    741: BlockType(id=741, name="cursed_f", name2="诅咒·陆",
        is_solid=True, color=(100, 30, 30), pattern=('vector', (16, 16), [('fill', (100, 30, 30)), ('rect', 0, 2, 16, 3, (180, 60, 60)), ('rect', 0, 8, 16, 3, (200, 80, 80)), ('rect', 0, 14, 16, 2, (180, 60, 60))]),
        buff_id=57, buff_params=(17,), buff_duration=13.0,
        break_hp=115, break_level=8, light_level=3),

}