"""Exercise the explicitly patched A82 prototype, never label it production evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_magnetized_range import measure
from scripts.prototype_magnetized_field import apply_field
from environment_forces import apply_magnetism


def candidate(actor, world, types, dt):
    if world is not None and actor.has_buff(49):
        apply_field(actor, world, dt)
    else:
        apply_magnetism(actor, world, types, dt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with patch('environment_forces.apply_magnetism', new=candidate):
        report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'CANDIDATE ONLY: actual WorldSession with explicitly patched prototype field, production remains unchanged; same isolated ore fixtures as before',
            'runs': [measure(distance, side, polarity, active, fps)
                     for distance in (.9, 1.5, 3.5, 5.) for side in (-1, 1)
                     for polarity in (-1, 1) for active in (False, True) for fps in (30, 60, 144)],
            'immune': [measure(1.5, side, polarity, True, fps, immunity)
                       for immunity in (39, 41, 54) for side in (-1, 1)
                       for polarity in (-1, 1) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'active_nearby_with_motion': sum(r['active'] and r['distance'] in (1.5, 3.5) and abs(r['dx']) > 1e-8 for r in report['runs']),
                      'immune_moved': sum(abs(r['dx']) > 1e-8 for r in report['immune'])}))
