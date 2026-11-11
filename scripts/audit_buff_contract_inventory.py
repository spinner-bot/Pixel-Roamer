"""Inventory declared block/Buff links and code hints, never infer behavior passes."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map, list_maps


def inventory():
    buffs = json.loads((ROOT / 'data/catalogs/buffs.json').read_text())['entries']
    blocks = json.loads((ROOT / 'data/catalogs/blocks.json').read_text())['entries']
    paths = list(ROOT.glob('*.py')) + list((ROOT / 'pixel_roamer').rglob('*.py'))
    sources = {str(path.relative_to(ROOT)): path.read_text() for path in paths}
    calls, ticks = {}, {}
    for name, source in sources.items():
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ('has_buff', '_get_buff_param', 'apply_buff')
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and type(node.args[0].value) is int):
                calls.setdefault(node.args[0].value, []).append(
                    {'file': name, 'line': node.lineno, 'call': node.func.attr})
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                ticks.setdefault(node.value, []).append({'file': name, 'line': node.lineno})
    usage = {map_id: Counter(tile.type_id for tile in get_map(map_id).grid.values())
             for map_id in sorted(list_maps())}
    entries = []
    for buff in buffs:
        linked = []
        for block in blocks:
            if buff['id'] not in block['buff_ids']:
                continue
            index = block['buff_ids'].index(buff['id'])
            linked.append({'block_id': block['id'], 'name': block['name2'],
                'params': block['buff_params_list'][index] if index < len(block['buff_params_list']) else [],
                'duration': block['buff_durations'][index] if index < len(block['buff_durations']) else None,
                'map_cells': {str(i): count[block['id']] for i, count in usage.items() if count[block['id']]}})
        entries.append({'buff_id': buff['id'], 'name': buff['name2'], 'claim': buff['desc'],
            'tick': buff['tick'], 'category': buff['category'], 'linked_blocks': linked,
            'code_hints': calls.get(buff['id'], []), 'tick_hints': ticks.get(buff['tick'], []),
            'functional_verdict': 'unverified_by_this_inventory',
            'note': 'Code/data presence and prior invariant matrices are not functional acceptance.'})
    return {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'static catalog/code and current map placement inventory; no behavioral pass claims',
            'source_hashes': {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sources.items()},
            'catalog_hashes': {kind: hashlib.sha256((ROOT / f'data/catalogs/{kind}.json').read_bytes()).hexdigest()
                               for kind in ('blocks', 'buffs')}, 'entries': entries}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inventory()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'buffs': len(result['entries']),
        'without_catalog_block_links': [e['buff_id'] for e in result['entries'] if not e['linked_blocks']],
        'without_direct_behavior_calls': [e['buff_id'] for e in result['entries']
            if not any(h['call'] in ('has_buff', '_get_buff_param') for h in e['code_hints'])]}))
