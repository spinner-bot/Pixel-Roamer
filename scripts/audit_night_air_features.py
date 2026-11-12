"""Expose night-air healing and every later intentional map difference explicitly."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map, list_maps

CASES = ((7, 'end_temple', (36, 29)), (4, 'loop_maze', (40, 30)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '3e5204b', 'scope': 'full map diff for missed night-air healing plus reviewed west hub exit; actual control routes separate',
              'maps': []}
    for map_id, legacy_folder, point in CASES:
        old = ModuleType(f'legacy_night_{map_id}')
        old.__file__ = str(ROOT / 'maps' / legacy_folder / 'map.py')
        source = subprocess.check_output(['git', 'show', f'3e5204b:maps/{legacy_folder}/map.py'], cwd=ROOT, text=True)
        exec(compile(source, old.__file__, 'exec'), old.__dict__)
        before, after = old.world, get_map(map_id)
        changes = [{'position': [x, y], 'before': before.get_tile(x, y).type_id,
                    'after': after.get_tile(x, y).type_id}
                   for x, y in sorted(set(before.grid) | set(after.grid))
                   if before.get_tile(x, y).type_id != after.get_tile(x, y).type_id]
        report['maps'].append({'map_id': map_id, 'folder': list_maps()[map_id],
                               'point': point, 'before': before.get_tile(*point).type_id,
                               'after': after.get_tile(*point).type_id, 'changes': changes,
                               'healing_is_solid': after.block_types[290].is_solid})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['maps']))


if __name__ == '__main__':
    main()
