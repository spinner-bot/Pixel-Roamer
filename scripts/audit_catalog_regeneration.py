"""Replay catalog builders and reject drift in reviewed data or consumers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    paths = sorted(set(ROOT.joinpath('data/catalogs').rglob('*.json'))
                   | set(ROOT.joinpath('data/rules').glob('*.json'))
                   | set(ROOT.joinpath('tests/fixtures').glob('catalog_*.json')))
    paths += [ROOT / name for name in (
        'buff_behavior.py', 'buff_contacts.py', 'buff_cleanup.py', 'buff_controls.py',
        'buff_reactions.py', 'buff_system.py', 'status_effects.py', 'creature.py',
        'pixel_roamer/world_session.py', 'shore_exit.py',
        'docs/进展报告/evidence/art/A79_magnetic_flower.png',
        'docs/进展报告/evidence/art/A91_frozen_buff.png')]

    def hashes():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'actual sequential catalog migration/art and extension builder replay; protected files must remain byte-identical after every step',
              'before': hashes(), 'steps': []}
    output.parent.mkdir(parents=True, exist_ok=True)
    for script in ('repair_buff_source_defaults.py', 'repair_magnetic_polarity_sources.py',
                   'refine_pixel_art.py', 'build_magnetic_block.py', 'build_frozen_buff.py'):
        completed = subprocess.run([sys.executable, str(ROOT / 'scripts' / script)], cwd=ROOT,
                                   capture_output=True, text=True, timeout=120)
        after = hashes()
        changed = [name for name, value in after.items() if value != report['before'][name]]
        report['steps'].append({'script': script, 'returncode': completed.returncode,
                                'stdout': completed.stdout, 'stderr': completed.stderr,
                                'hashes': after, 'changed': changed})
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'script': script, 'returncode': completed.returncode, 'changed': changed}), flush=True)
        if completed.returncode or changed:
            return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output) else 1)
