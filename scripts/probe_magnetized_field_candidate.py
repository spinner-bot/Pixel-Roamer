"""Exercise the explicitly patched A82 prototype, never label it production evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
from collections import defaultdict
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_magnetized_range import measure
from scripts.audit_magnetic_escape import run as escape
from scripts.prototype_magnetized_field import apply_field
from environment_forces import apply_magnetism
from block_types_data import BLOCK_TYPES
from scripts.control_session import create_control_session
from world import World
import pygame


def loop_probe(period, side, offset):
    ore = replace(BLOCK_TYPES[338], id=5000, special_data=8)
    source_x = 0 if side == 1 else period - 1
    start = period - .6 if side == 1 else .6
    world = World(0, 'nearest loop source', period, 12, gravity=0, loop_x=True,
                  spawn_points=(start + offset * period, 5.5), block_types={**BLOCK_TYPES, 5000: ore})
    world.set_tile(source_x, 5, 5000)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    actor.apply_buff(49, (), 1)
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)):
        session.advance(1 / 120)
    contact_distance = actor._w / 2 + .5
    expected = side * 8 * 2.5 * 10 * (1 - (1.1 - contact_distance) / (4 - contact_distance)) ** 2 / 120
    return {'period': period, 'side': side, 'offset': offset, 'velocity': [actor.v_x, actor.v_y],
            'expected_vx_one_physical_source': expected, 'error': abs(actor.v_x - expected)}


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
                       for polarity in (-1, 1) for fps in (30, 60, 144)],
            'escape': [escape(kind, side, fps) for kind in (338, 386, 403)
                       for side in ('left', 'right') for fps in (30, 60, 144)],
            'loop': [loop_probe(period, side, offset) for period in (3, 5, 8)
                     for side in (-1, 1) for offset in (-2, 0, 3)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'active_nearby_with_motion': sum(r['active'] and r['distance'] in (1.5, 3.5) and abs(r['dx']) > 1e-8 for r in report['runs']),
                      'immune_moved': sum(abs(r['dx']) > 1e-8 for r in report['immune']),
                      'escaped': sum(r['escaped'] for r in report['escape']),
                      'loop_max_error': max(r['error'] for r in report['loop'])}))
