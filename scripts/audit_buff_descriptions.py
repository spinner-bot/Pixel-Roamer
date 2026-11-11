"""Inventory actual source descriptions used by the HUD/reference view."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import buff_data
from buff_system import BUFF_TYPES, BuffInstance
from resource_catalog import load_blocks


def run():
    rows = []
    for block in load_blocks().values():
        for index, buff_id in enumerate(block.buff_ids):
            params, duration = block.buff_params_list[index], block.buff_durations[index]
            text = BuffInstance(buff_id, params, duration).format_desc()
            rows.append({'block_id': block.id, 'buff_id': buff_id, 'params': params,
                         'duration': duration, 'description': text,
                         'unresolved': '{' in text or '}' in text or not text,
                         'false_zero_duration': bool(duration and re.search(r'持续\s+0(?:\.0+)?\s+秒', text))})
    return {'buff_definitions': len(BUFF_TYPES), 'rows': rows,
            'issues': [r for r in rows if r['unresolved'] or r['false_zero_duration']]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'actual registered BuffInstance descriptions, no pixel/physical device claim', **run()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'source_links': len(result['rows']), 'buff_definitions': result['buff_definitions'],
                      'issues': len(result['issues'])}))
