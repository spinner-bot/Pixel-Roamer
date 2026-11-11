"""Compare immediate Space versus automatic launch across every upward source."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from resource_catalog import load_blocks
from scripts.audit_leaping_height import measure


def run():
    sources = [b for b in load_blocks().values() if b.bounce[1] > 0
               or (b.special == 'catapult' and b.special_data and b.special_data[1] > 0)]
    rows = []
    for block in sources:
        for fps in (30, 60, 144):
            automatic = measure(fps, block.id, press_jump=False, world_height=256, time_limit=24)
            pressed = measure(fps, block.id, press_jump=True, world_height=256, time_limit=24)
            rows.append({'block_id': block.id, 'name': block.name2, 'fps': fps,
                         'automatic': automatic, 'pressed': pressed,
                         'height_lost_by_pressing': automatic['height'] - pressed['height']})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = run()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'real contact with every authored upward launch source and real Space event in explicit supporting fixtures; 120Hz apex sampling; no original-map route or device claim',
              'pairs': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pairs': len(rows), 'lost_height': sum(r['height_lost_by_pressing'] > 1e-7 for r in rows),
                      'unfinished': sum(not r[k]['landed'] for r in rows for k in ('automatic', 'pressed'))}))
