"""Measure whether magnetized49 responds to nearby ore without touching it."""
import argparse
from collections import defaultdict
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from block_types_data import BLOCK_TYPES
from scripts.control_session import create_control_session
from world import World


def measure(distance, side, polarity, active, fps, immunity=None):
    # A copy of original ore338 isolates polarity and avoids auto-applying49.
    kind = replace(BLOCK_TYPES[338], id=5000, special_data=8 * polarity)
    world = World(0, 'magnetized nearby contract', 40, 16, gravity=0,
                  spawn_points=(20.5 - side * distance, 5.5),
                  block_types={**BLOCK_TYPES, 5000: kind})
    world.set_tile(20, 5, 5000)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    if active:
        actor.apply_buff(49, (), 2)
    if immunity:
        actor.apply_buff(immunity, (), 2)
    initial = actor.get_center()
    max_speed, touched = 0., False
    original = session._advance_step
    def observe(dt, keys):
        nonlocal max_speed, touched
        original(dt, keys)
        max_speed = max(max_speed, abs(actor.v_x))
        touched |= 5000 in actor.contact_pool
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(round(.25 * fps)):
            session.advance(1 / fps)
        respawns = reset.call_count
    return {'distance': distance, 'side': side, 'polarity': polarity, 'active': active,
            'fps': fps, 'immunity': immunity, 'initial': initial, 'final': actor.get_center(),
            'dx': actor._x - initial[0], 'max_speed': max_speed, 'touched': touched,
            'respawns': respawns, 'hp': actor.hp}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'isolated ore-derived polarity fixture, actual WorldSession, Buff injected only for controlled comparison; no normal-map source route claim',
              'runs': [measure(distance, side, polarity, active, fps)
                       for distance in (.9, 1.5, 3.5, 5.) for side in (-1, 1)
                       for polarity in (-1, 1) for active in (False, True) for fps in (30, 60, 144)],
              'immune': [measure(1.5, side, polarity, True, fps, immunity)
                         for immunity in (39, 41, 54) for side in (-1, 1)
                         for polarity in (-1, 1) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'runs': len(report['runs']), 'immune': len(report['immune']),
                      'active_nearby_with_motion': sum(r['active'] and r['distance'] in (1.5, 3.5) and abs(r['dx']) > 1e-8 for r in report['runs'])}))
