"""Compare claimed jump-height bonuses with fixed-tick measured jump apexes."""
import argparse
from collections import defaultdict
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
from scripts.control_session import create_control_session
from world import World


def measure(fps, source=2, parameter=None):
    world = World(0, 'leaping height contract', 40, 80, gravity=-9.8, spawn_points=(10.5, 5.9))
    for x in range(40):
        world.set_tile(x, 4, source if x == 10 else 2)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    original = session._advance_step
    peak, airborne, landed = actor._y, False, False

    def observe(dt, keys):
        nonlocal peak, airborne, landed
        original(dt, keys)
        peak = max(peak, actor._y)
        airborne |= not actor.on_ground and actor._y > 5.9 + 1e-7
        landed |= airborne and actor.on_ground

    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch('sfx.play_jump'), patch.object(actor, 'reset', wraps=actor.reset) as reset:
        session.advance(1 / 120)
        if parameter is not None:
            actor.apply_buff(4, (parameter,), 30)
        actor.refresh_movement_stats()
        applied = [{'id': b.buff_id, 'params': b.params, 'source': b.source} for b in actor.buffs]
        launch_speed = actor.v_jump
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]):
            session.app._handle_events()
        with patch.object(session, '_advance_step', side_effect=observe):
            for _ in range(12 * fps):
                session.advance(1 / fps)
                if landed:
                    break
        respawns = reset.call_count
    return {'fps': fps, 'source_block': source, 'injected_parameter': parameter, 'applied': applied,
            'launch_speed': launch_speed, 'height': peak - 5.9, 'landed': landed,
            'elapsed': session.app._game_timer, 'respawns': respawns, 'hp': actor.hp,
            'physics': {'gravity': world.gravity, 'vertical_damping': actor.f_y}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for fps in (30, 60, 144):
        baseline = measure(fps)
        rows.append(baseline)
        for source, parameter in [(2, p) for p in (0, 25, 50, 100)] + [(415, None), (418, None)]:
            row = measure(fps, source, parameter)
            row['height_ratio'] = row['height'] / baseline['height']
            rows.append(row)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'fixed-tick apex observed inside actual WorldSession after Space event; explicit floor fixture, API injection labeled; sources415/418 acquired only by contact; not original-map route',
              'runs': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'source': r['source_block'], 'parameter': r['injected_parameter'],
                       'height': r['height'], 'ratio': r.get('height_ratio'), 'landed': r['landed']}
                      for r in rows if r['fps'] == 60]))
