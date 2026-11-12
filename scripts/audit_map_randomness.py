"""Compare map geometry across seeds, loading orders, and generator reruns."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def fingerprint(world):
    entries = [(x, y, tile.type_id, tile.meta) for (x, y), tile in sorted(world.grid.items())]
    return hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def worker(seed, reverse):
    from maps import get_map, list_maps
    registry = list_maps()
    random.seed(seed)
    result = {}
    for mid in sorted(registry, reverse=reverse):
        state = random.getstate()
        world = get_map(mid)
        result[str(mid)] = {'hash': fingerprint(world), 'tiles': len(world.grid),
                            'global_rng_unchanged': random.getstate() == state}
    for mid in (20, 21):
        module = importlib.import_module(f'maps.{registry[mid]}.map')
        state = random.getstate()
        world = module.generate()
        result[str(mid)]['regenerate_hash'] = fingerprint(world)
        result[str(mid)]['regenerate_rng_unchanged'] = random.getstate() == state
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--reverse', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(args.seed, args.reverse)
        return
    if not args.output:
        parser.error('--output is required')
    cases = []
    for seed, reverse in ((1, False), (999, False), (1, True)):
        command = [sys.executable, __file__, '--worker', '--seed', str(seed)]
        if reverse:
            command.append('--reverse')
        result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
                                env={**os.environ, 'PYTHONHASHSEED': str(seed)})
        cases.append({'seed': seed, 'python_hash_seed': seed,
                      'reverse_order': reverse, 'maps': json.loads(result.stdout)})
    changed = [mid for mid in cases[0]['maps'] if len({case['maps'][mid]['hash'] for case in cases}) > 1]
    polluted = sorted({mid for case in cases for mid, entry in case['maps'].items()
                       if not entry['global_rng_unchanged']})
    regeneration = sorted({mid for case in cases for mid, entry in case['maps'].items()
                           if 'regenerate_hash' in entry and entry['regenerate_hash'] != entry['hash']})
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(), 'cases': cases, 'changed_maps': changed,
              'polluted_global_rng': polluted, 'changed_on_regeneration': regeneration}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('changed_maps', 'polluted_global_rng', 'changed_on_regeneration')}))


if __name__ == '__main__':
    main()
