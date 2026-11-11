"""Compare the new gallery against the exact pre-gallery generated world."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from maps import get_map, _apply_config
from maps.placement import load_feature_plan


def run():
    baseline = 'a1349ea'
    module = ModuleType('pre_gallery_grand_journey')
    module.__file__ = str(ROOT/'maps/grand_journey/map.py')
    source = subprocess.check_output(['git','show',baseline+':maps/grand_journey/map.py'],cwd=ROOT,text=True)
    exec(compile(source,module.__file__,'exec'),module.__dict__)
    original = module.world
    _apply_config(original,'grand_journey')
    current = get_map(20)
    points, _ = load_feature_plan(current,ROOT/'maps/grand_journey/polarity_gallery.json')
    allowed = {(x,y) for x,y,bid in points}
    differences, outside = [], []
    for coord in sorted(set(original.grid) | set(current.grid)):
        before, after = original.get_tile(*coord), current.get_tile(*coord)
        if (before.type_id,before.meta) != (after.type_id,after.meta):
            row = {'position': list(coord),'before': before.type_id,'after': after.type_id,
                   'before_meta':before.meta,'after_meta':after.meta}
            differences.append(row)
            if coord not in allowed:
                outside.append(row)
    checks = {'all_changes_inside_plan': not outside,
              'all_plan_points_match': all(current.get_tile(x,y).type_id == bid for x,y,bid in points),
              'spawn_preserved': current.spawn_points == original.spawn_points,
              'gravity_preserved': current.gravity == original.gravity,
              'west_ruby_preserved': current.get_tile(2975,83).type_id == original.get_tile(2975,83).type_id == 312,
              'west_silver_preserved': current.get_tile(2975,84).type_id == original.get_tile(2975,84).type_id == 311,
              'original_reverse_preserved': current.get_tile(3744,73).type_id == original.get_tile(3744,73).type_id == 411,
              'original_ore_preserved': current.get_tile(2947,82).type_id == original.get_tile(2947,82).type_id == 403}
    return {'code_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'baseline':baseline,'checks':checks,'planned_cells':len(points),'changed_cells':len(differences),
            'differences':differences,'outside_plan':outside}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('differences','outside_plan')},ensure_ascii=False))
    raise SystemExit(0 if all(result['checks'].values()) else 1)
