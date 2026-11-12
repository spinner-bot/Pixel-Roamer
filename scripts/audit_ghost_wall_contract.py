"""Measure the declared single-layer wall Buff against thick walls and supporting floors."""
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


def wall_case(mode, thickness, side, fps, *, size=(.8, 1.8), shift=0, loop=False):
    left, right = 20 + shift, 20 + shift + thickness
    start = left - 3 if side == 1 else right + 3
    world = World(0, 'single-layer wall contract', 48, 16, gravity=0,
                  spawn_points=(start, 5.5), loop_x=loop)
    world.player_config = {'w': size[0], 'h': size[1]}
    for x in range(left, right):
        for y in range(2, 10):
            world.set_tile(x, y, 384 if mode == 'source' and x == (left if side == 1 else right - 1) else 19)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    if mode == 'buff':
        actor.apply_buff(48, (), 4)
    elif mode == 'phantom':
        actor._phantom_active, actor._phantom_timer = True, 4
    keys = defaultdict(bool, {pygame.K_d if side == 1 else pygame.K_a: True})
    crossed, applied = False, None
    unwrapped_x, previous_x = start, actor._x
    with patch('pygame.key.get_pressed', return_value=keys), patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(3 * fps):
            session.advance(1 / fps)
            delta = actor._x - previous_x
            if loop:
                delta = (delta + world.width / 2) % world.width - world.width / 2
            unwrapped_x += delta
            previous_x = actor._x
            if applied is None and actor.has_buff(48):
                buff = next(b for b in actor.buffs if b.buff_id == 48)
                applied = {'source': buff.source, 'params': buff.params, 'duration': buff.duration}
            if (side == 1 and unwrapped_x - actor._w / 2 >= right) or (side == -1 and unwrapped_x + actor._w / 2 <= left):
                crossed = True
                break
        respawns = reset.call_count
    return {'mode': mode, 'thickness': thickness, 'side': side, 'fps': fps, 'crossed': crossed,
            'position': actor.get_center(), 'applied': applied, 'elapsed': session.app._game_timer,
            'respawns': respawns, 'hp': actor.hp, 'size': size, 'shift': shift,
            'loop': loop, 'unwrapped_x': unwrapped_x}


def floor_case(mode, fps, *, size=(.8, 1.8), isolated=False):
    world = World(0, 'supporting floor contract', 40, 16, gravity=-9.8,
                  spawn_points=(10.5, 5.9))
    world.player_config = {'w': size[0], 'h': size[1]}
    for x in ((10,) if isolated else range(2, 38)):
        world.set_tile(x, 4, 384 if mode == 'source' else 2)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    if mode == 'buff':
        actor.apply_buff(48, (), 4)
    minimum, dropped = actor._y, False
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(2 * fps):
            session.advance(1 / fps)
            minimum = min(minimum, actor._y)
            if minimum < 5 + size[1] / 2 - .1:
                dropped = True
                break
        respawns = reset.call_count
    return {'mode': mode, 'fps': fps, 'dropped_through_floor': dropped, 'min_center_y': minimum,
            'position': actor.get_center(), 'respawns': respawns, 'hp': actor.hp,
            'size': size, 'isolated': isolated}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extended', action='store_true')
    args = parser.parse_args()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'isolated authored wall/floor fixtures with real WorldSession input; Buff injected in buff mode, source mode obtained by contact; no normal original-map route claim',
        'walls': [wall_case(mode, width, side, fps) for mode in ('none', 'buff', 'source', 'phantom')
                  for width in (1, 2, 3) for side in (-1, 1) for fps in (30, 60, 144)],
        'floors': [floor_case(mode, fps) for mode in ('none', 'buff', 'source') for fps in (30, 60, 144)]}
    if args.extended:
        result['extended_walls'] = [wall_case(mode, width, side, fps, size=size, shift=shift, loop=loop)
            for size in ((.6, 1.5), (.8, 1.8), (1.4, 2.1))
            for shift, loop in ((0, False), (-20, True), (27, True))
            for mode in ('buff', 'source') for width in (1, 2) for side in (-1, 1) for fps in (30, 60, 144)]
        result['extended_floors'] = [floor_case(mode, fps, size=size, isolated=isolated)
            for size in ((.6, 1.5), (.8, 1.8), (1.4, 2.1))
            for isolated in (False, True) for mode in ('none', 'buff', 'source') for fps in (30, 60, 144)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'wall_cases': len(result['walls']), 'crossed': sum(r['crossed'] for r in result['walls']),
                      'floor_cases': len(result['floors']), 'dropped': sum(r['dropped_through_floor'] for r in result['floors'])}))
