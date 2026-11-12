"""Audit production magnetized field range, immunity, retreat and loop images."""
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


def reversed_source_probe(fps):
    world = World(0, 'original411 and338 interaction', 40, 16, gravity=-9.8,
                  spawn_points=(15.5, 5.9))
    for x in range(40):
        world.set_tile(x, 4, 411 if x == 15 else 2)
    world.set_tile(18, 5, 338)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    keys = defaultdict(bool)
    with patch('pygame.key.get_pressed', return_value=keys), patch.object(actor, 'reset', wraps=actor.reset) as reset:
        session.advance(1 / 120)
        obtained = {str(b.buff_id): b.source for b in actor.buffs}
        # Reversed23 turns held D into effective left, away from the ore.
        keys[pygame.K_d] = True
        min_foot = actor._y - actor._h / 2
        for _ in range(2 * fps):
            session.advance(1 / fps)
            min_foot = min(min_foot, actor._y - actor._h / 2)
        respawns = reset.call_count
    return {'fps': fps, 'obtained': obtained, 'retreat': 15.5 - actor._x,
            'position': actor.get_center(), 'hp': actor.hp, 'respawns': respawns,
            'min_foot_y': min_foot, 'remaining49': actor.has_buff(49), 'remaining23': actor.has_buff(23)}


def jump_source_probe(fps, kind):
    world = World(0, 'magnetic source jump escape', 40, 40, gravity=-6.5, spawn_points=(20.5, 5.9))
    world.player_config = {'f_y': .9965}
    for x in range(40):
        world.set_tile(x, 4, kind if x == 20 else 2)
    world.set_tile(20, 3, kind)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    peak, min_foot, airborne, landed = actor._y, 5., False, False
    original = session._advance_step
    def observe(dt, held):
        nonlocal peak, min_foot, airborne, landed
        original(dt, held)
        peak = max(peak, actor._y)
        min_foot = min(min_foot, actor._y - actor._h / 2)
        airborne |= actor._y > 5.9 + 1e-7
        landed |= airborne and actor.on_ground
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), patch('sfx.play_jump'), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        session.advance(1 / 120)
        source = next((b.source for b in actor.buffs if b.buff_id == 49), None)
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]):
            session.app._handle_events()
        with patch.object(session, '_advance_step', side_effect=observe):
            for _ in range(8 * fps):
                session.advance(1 / fps)
                if landed:
                    break
        respawns = reset.call_count
    return {'fps': fps, 'kind': kind, 'buff_source': source, 'height': peak - 5.9,
            'min_foot': min_foot, 'landed': landed, 'respawns': respawns, 'hp': actor.hp,
            'escape_flag_at_landing': actor._jump_escape_active}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'actual production WorldSession without replacement force functions; isolated ore fixtures and injected49 only for controlled comparison; no original-map route claim',
        'runs': [measure(distance, side, polarity, active, fps)
                 for distance in (.9, 1.5, 3.5, 5.) for side in (-1, 1)
                 for polarity in (-1, 1) for active in (False, True) for fps in (30, 60, 144)],
        'immune': [measure(1.5, side, polarity, True, fps, immunity)
                   for immunity in (39, 41, 54) for side in (-1, 1)
                   for polarity in (-1, 1) for fps in (30, 60, 144)],
        'escape': [escape(kind, side, fps) for kind in (338, 386, 403)
                   for side in ('left', 'right') for fps in (30, 60, 144)],
        'loop': [loop_probe(period, side, offset) for period in (3, 5, 8)
                 for side in (-1, 1) for offset in (-2, 0, 3)],
        'reversed_source': [reversed_source_probe(fps) for fps in (30, 60, 144)],
        'jump_escape': [jump_source_probe(fps, kind) for kind in (338, 386, 403) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'active_nearby_with_motion': sum(r['active'] and r['distance'] in (1.5, 3.5) and abs(r['dx']) > 1e-8 for r in report['runs']),
                      'immune_moved': sum(abs(r['dx']) > 1e-8 for r in report['immune']),
                      'escaped': sum(r['escaped'] for r in report['escape']),
                      'loop_max_error': max(r['error'] for r in report['loop'])}))
