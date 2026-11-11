"""Replay reviewed Buff49 source polarity changes without touching other fields."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.format_catalogs import formatted

BASELINE = '3822062'
RESPONSES = {386: 1, 403: 1, 411: -1}


def main():
    relative = 'data/catalogs/blocks.json'
    original = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:{relative}'], cwd=ROOT, text=True))
    old = {entry['id']: entry for entry in original['entries']}
    document = json.loads((ROOT / relative).read_text())
    current = {entry['id']: entry for entry in document['entries']}
    manifest_path = ROOT / 'tests/fixtures/catalog_gameplay_changes.json'
    manifest = json.loads(manifest_path.read_text())
    for block_id, response in RESPONSES.items():
        before = old[block_id]['buff_params_list']
        after = deepcopy(before)
        after[old[block_id]['buff_ids'].index(49)] = [response]
        if current[block_id]['buff_params_list'] not in (before, after):
            raise ValueError(f'block {block_id} has a newer parameter edit; refuse to overwrite')
        review = {'stage': 'A84', 'reason': 'Explicit Buff49 polarity; reverse pole reverses force as well as controls',
                  'fields': {'buff_params_list': {'before': before, 'after': after}}}
        previous = manifest['blocks'].get(str(block_id))
        if previous is not None and previous != review:
            raise ValueError(f'block {block_id} has a newer gameplay review; refuse to overwrite')
        current[block_id]['buff_params_list'] = after
        manifest['blocks'][str(block_id)] = review
    (ROOT / relative).write_text(formatted(document) + '\n')
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(RESPONSES))


if __name__ == '__main__':
    main()
