"""Measure signed Buff49 response and real source behavior independently of input reversal."""
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


def measure(fps, response=None, side=1, ore_polarity=1, source=None):
    kind = replace(BLOCK_TYPES[338], id=5000, special_data=8 * ore_polarity)
    start = (20.5 - 3.5 * side, 5.5) if source is None else (10.5, 5.9)
    world = World(0, 'Buff49 polarity contract', 40, 20, gravity=0 if source is None else -9.8,
                  spawn_points=start, block_types={**BLOCK_TYPES, 5000: kind})
    if source is None:
        world.set_tile(20, 5, 5000)
    else:
        for x in range(40):
            world.set_tile(x, 4, source if x == 10 else 2)
        world.set_tile(13, 5, 338)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    if source is None:
        actor.apply_buff(49, () if response is None else (response,), 2)
    first_vx = None
    original = session._advance_step
    def observe(dt, keys):
        nonlocal first_vx
        original(dt, keys)
        if first_vx is None:
            first_vx = actor.v_x
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(round(.25 * fps)):
            session.advance(1 / fps)
        respawns = reset.call_count
    buff = next(b for b in actor.buffs if b.buff_id == 49)
    return {'fps': fps, 'response_parameter': response, 'side': side, 'ore_polarity': ore_polarity,
            'source_block': source, 'actual_params': buff.params, 'actual_source': buff.source,
            'first_tick_vx': first_vx, 'dx': actor._x - start[0], 'description': buff.format_desc(),
            'hp': actor.hp, 'respawns': respawns, 'elapsed': session.app._game_timer}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'signed-response API contract probes and actual386/403/411 contact fixtures; no injected Buff for source rows, no key input, not original-map reachability evidence',
              'parameters': [measure(fps, response, side, ore) for fps in (30, 60, 144)
                             for response in (None, 0, 1, -1, 2, -2)
                             for side in (-1, 1) for ore in (-1, 1)],
              'sources': [measure(fps, source=source) for source in (386, 403, 411) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'parameter_probes': len(report['parameters']), 'sources': len(report['sources']),
                      'source_directions': [(r['source_block'], r['fps'], r['first_tick_vx']) for r in report['sources']]}))
