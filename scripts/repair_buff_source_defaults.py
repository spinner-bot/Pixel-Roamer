"""Replay the reviewed A80 source-parameter correction without redefining API zero."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.format_catalogs import formatted

BASELINE = 'e1124eb'
DEFAULTED_BUFFS = {5, 6, 7, 13, 42, 43, 44, 45, 47, 51, 53, 54, 55}


def main():
    relative = 'data/catalogs/blocks.json'
    original = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:{relative}'], cwd=ROOT, text=True))
    current = json.loads((ROOT / relative).read_text())
    by_id = {e['id']: e for e in current['entries']}
    manifest = {'schema_version': 1, 'baseline_ref': BASELINE, 'blocks': {}, 'buffs': {}}
    links = 0
    for block in original['entries']:
        before = block['buff_params_list']
        after = deepcopy(before)
        for index, buff_id in enumerate(block['buff_ids']):
            if buff_id in DEFAULTED_BUFFS and before[index] == [0]:
                after[index] = []
                links += 1
        if before == after:
            continue
        if by_id[block['id']]['buff_params_list'] not in (before, after):
            raise ValueError(f"block {block['id']} has a newer parameter edit; refuse to overwrite")
        by_id[block['id']]['buff_params_list'] = after
        manifest['blocks'][str(block['id'])] = {
            'stage': 'A80', 'reason': 'Use existing numeric Buff defaults instead of inert or zero-interval source placeholders',
            'fields': {'buff_params_list': {'before': before, 'after': after}}}
    if links != 37:
        raise ValueError(f'expected 37 reviewed placeholder links, found {links}')
    (ROOT / relative).write_text(formatted(current) + '\n')
    (ROOT / 'tests/fixtures/catalog_gameplay_changes.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'links': links, 'blocks': len(manifest['blocks'])}))


if __name__ == '__main__':
    main()
