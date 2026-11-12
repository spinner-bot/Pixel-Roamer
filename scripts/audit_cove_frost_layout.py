"""Compare the exact pre-basin world and all preserved original features."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import _apply_config, get_map
from maps.placement import load_feature_plan

BASELINE = 'dd277a4'


def run():
    module = ModuleType('pre_frost_pool_cove')
    module.__file__ = str(ROOT / 'maps/adventure_cove/map.py')
    source = subprocess.check_output(['git', 'show', BASELINE + ':maps/adventure_cove/map.py'],
                                     cwd=ROOT, text=True, encoding='utf-8')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    original = module.world
    _apply_config(original, 'adventure_cove')
    current = get_map(21)
    points, _ = load_feature_plan(current, ROOT / 'maps/adventure_cove/frost_pool.json')
    allowed = {(x, y): bid for x, y, bid in points}
    changes, outside = [], []
    for coord in sorted(set(original.grid) | set(current.grid)):
        before, after = original.get_tile(*coord), current.get_tile(*coord)
        if (before.type_id, before.meta) != (after.type_id, after.meta):
            row = {'position': list(coord), 'before': before.type_id, 'after': after.type_id,
                   'before_meta': before.meta, 'after_meta': after.meta}
            changes.append(row)
            if coord not in allowed:
                outside.append(row)

    def pickups(world):
        return [(coord, tile.type_id, tile.meta) for coord, tile in sorted(world.grid.items())
                if world.block_types[tile.type_id].special == 'score']

    conflicting_plan_refused = False
    conflict_module = ModuleType('conflicting_frost_pool_cove')
    conflict_module.__file__ = module.__file__
    with patch('maps.placement.load_feature_plan', return_value=(((246,55,7),),frozenset())):
        try:
            exec(compile(Path(module.__file__).read_text(),module.__file__,'exec'),conflict_module.__dict__)
        except ValueError as error:
            conflicting_plan_refused = 'must not overwrite' in str(error)
    checks = {
        'nonempty_original_cell_rejected': conflicting_plan_refused,
        'only_seventeen_reviewed_air_cells': len(changes) == len(points) == 17
            and all(row['before'] == 0 and row['before_meta'] is None and row['after_meta'] is None
                    and allowed.get(tuple(row['position'])) == row['after'] for row in changes),
        'no_outside_changes': not outside,
        'all_plan_cells_loaded': all(current.get_tile(x, y).type_id == bid for x, y, bid in points),
        'all_pickups_preserved': pickups(original) == pickups(current),
        'both_original_cold_sources_preserved': all(current.get_tile(x, 55).type_id
            == original.get_tile(x, 55).type_id == 373 for x in (246, 260)),
        'all_original_pillars_preserved': all(current.get_tile(x, y).type_id
            == original.get_tile(x, y).type_id == 23 for x in (245, 251, 257, 263) for y in range(58, 63)),
        'world_and_player_configuration_preserved': all(getattr(original, key) == getattr(current, key)
            for key in ('spawn_points', 'gravity', 'mode', 'lives', 'player_config', 'loop_x', 'loop_y',
                        'view_blocks_h', 'score_goal', 'time_limit', 'void_limit'))}
    return {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'baseline': BASELINE, 'checks': checks, 'planned_cells': len(points),
            'changed_cells': len(changes), 'pickup_count': len(pickups(current)),
            'differences': changes, 'outside_plan': outside}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('baseline', 'checks', 'changed_cells', 'pickup_count')}))
    raise SystemExit(0 if all(report['checks'].values()) else 1)
