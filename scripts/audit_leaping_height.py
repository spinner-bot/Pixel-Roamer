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


def measure(fps, source=2, parameter=None, press_jump=True, *, world_height=80, time_limit=12):
    world = World(0, 'leaping height contract', 40, world_height, gravity=-9.8, spawn_points=(10.5, 5.9))
    for x in range(40):
        world.set_tile(x, 4, 2)
    # A non-solid source is a contact volume above support, not a floor.
    world.set_tile(10, 4 if world.block_types[source].is_solid else 5, source)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    original = session._advance_step
    peak, airborne, landed, returned_to_source = actor._y, False, False, False

    def observe(dt, keys):
        nonlocal peak, airborne, landed, returned_to_source
        before_vy = actor.v_y
        original(dt, keys)
        peak = max(peak, actor._y)
        airborne |= not actor.on_ground and actor._y > 5.9 + 1e-7
        # A catapult clears on_ground while immediately relaunching on the
        # landing tick. Its exact supporting height still proves contact.
        landed |= airborne and abs(actor._y - 5.9) <= 1e-7
        returned_to_source |= (airborne and before_vy < 0 < actor.v_y
                               and source in actor.contact_pool and abs(actor._y - 5.9) <= .011)

    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch('sfx.play_jump'), patch.object(actor, 'reset', wraps=actor.reset) as reset:
        session.advance(1 / 120)
        if parameter is not None:
            actor.apply_buff(4, (parameter,), 30)
        actor.refresh_movement_stats()
        applied = [{'id': b.buff_id, 'params': b.params, 'source': b.source, 'stacks': b.stacks} for b in actor.buffs]
        initial_vertical_velocity = actor.v_y
        initially_supported = actor.on_ground
        launch_speed = actor.v_jump
        events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if press_jump else []
        with patch('pygame.event.get', return_value=events):
            session.app._handle_events()
        with patch.object(session, '_advance_step', side_effect=observe):
            for _ in range(time_limit * fps):
                session.advance(1 / fps)
                if landed or returned_to_source:
                    break
        respawns = reset.call_count
    return {'fps': fps, 'source_block': source, 'injected_parameter': parameter, 'jump_event': press_jump, 'applied': applied,
            'launch_speed': launch_speed, 'height': peak - 5.9, 'landed': landed,
            'returned_to_source': returned_to_source, 'cycle_complete': landed or returned_to_source,
            'initial_vertical_velocity': initial_vertical_velocity, 'initially_supported': initially_supported,
            'final_position': actor.get_center(), 'final_vertical_velocity': actor.v_y,
            'final_support_flag': actor.on_ground,
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
        for source, parameter, press_jump in ([(2, p, True) for p in (0, 25, 50, 100)]
                                              + [(415, None, True), (418, None, True), (415, None, False)]):
            row = measure(fps, source, parameter, press_jump)
            row['height_ratio'] = row['height'] / baseline['height']
            rows.append(row)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'fixed-tick apex observed inside actual WorldSession after Space event; explicit floor fixture, API injection labeled; sources415/418 acquired only by contact; not original-map route',
              'runs': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'source': r['source_block'], 'parameter': r['injected_parameter'],
                       'jump_event': r['jump_event'], 'height': r['height'], 'ratio': r.get('height_ratio'), 'landed': r['landed']}
                      for r in rows if r['fps'] == 60]))
