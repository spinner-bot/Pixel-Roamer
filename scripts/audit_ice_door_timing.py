"""Separate presentation-sampled input timing from fixed-step door physics."""
from collections import defaultdict
import argparse
import hashlib
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
from maps import get_map
from maps.layout import apply_layout
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def measure(fps, jump_tick, layout=None):
    world = get_map(3).create_session()
    if layout:
        apply_layout(world, layout)
    world.spawn_points = (269.5, 39.9)
    session = create_control_session(3, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool, {pygame.K_d: True})
    tick, entry, trace, issues = 0, None, [], []
    original_step = session._advance_step

    def scheduled_step(dt, held):
        nonlocal tick, entry
        tick += 1
        if tick == jump_tick:
            with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]):
                app._handle_events()
        original_step(dt, held)
        if entry is None:
            state = {'tick': tick, 'time': app._game_timer, 'position': player.get_center(),
                     'velocity': [player.v_x, player.v_y], 'hp': player.hp, 'stamina': player.stamina}
            trace.append(state)
            if player._x >= 270.4:
                entry = state

    session._advance_step = scheduled_step
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        for _ in range(20 * fps):
            session.advance(1 / fps)
            issues = errors_for(session)
            if entry is not None or issues:
                break
    digest = hashlib.sha256(json.dumps(trace, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'fps': fps, 'jump_tick': jump_tick, 'entry': entry, 'physics_trace_sha256': digest,
            'physics_samples': len(trace), 'issues': issues, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--layout', type=Path)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'constant real D key; real Space event at identical 120Hz tick across presentation rates; explicit local fixture',
              'candidate_layout': json.loads(args.layout.read_text()) if args.layout else None,
              'runs': [measure(fps, jump_tick, args.layout) for jump_tick in (2, 3, 5) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'jump_tick': tick, 'entry_ticks': [r['entry']['tick'] if r['entry'] else None for r in report['runs'] if r['jump_tick'] == tick],
                       'unique_hashes': len({r['physics_trace_sha256'] for r in report['runs'] if r['jump_tick'] == tick})}
                      for tick in (2, 3, 5)]))


if __name__ == '__main__':
    main()
