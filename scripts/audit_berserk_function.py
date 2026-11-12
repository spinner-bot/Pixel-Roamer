"""Measure berserk attack/cost through API and existing source blocks, not a combat game mode."""
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
from creature import Player
from world import World
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def attack_snapshot(actor):
    target = Player(1, 'API target only', 0, 0, {}, hp_max=10000)
    # Isolate outgoing attack values; do not trigger source lifesteal here.
    damage = target.take_damage(actor.phys_atk, actor.magic_atk)
    return {'physical': actor.phys_atk, 'magic': actor.magic_atk, 'damage': damage, 'hp': actor.hp}


def api_case(base, params):
    actor = Player(0, 'API probe', 0, 0, {}, phys_atk=base, magic_atk=base / 2)
    initial = attack_snapshot(actor)
    actor.apply_buff(47, params, 1)
    active = attack_snapshot(actor)
    actor.tick_buffs(.5)
    halfway = attack_snapshot(actor)
    actor.tick_buffs(.5)
    return {'base': base, 'params': params, 'initial': initial, 'active': active,
            'halfway': halfway, 'expired': attack_snapshot(actor), 'buff_after': actor.has_buff(47)}


def source_case(tile_id, side, fps):
    world = World(0, 'existing source fixture', 30, 15, gravity=-9.8,
                  spawn_points=(10.5 - side * 2, 5.9))
    for x in range(3, 20):
        world.set_tile(x, 4, tile_id if x == 10 else 2)
    session = create_control_session(0, world=world)
    actor = session.app.player1
    keys, phase, applied = defaultdict(bool), 'approach', None
    errors, min_hp, completed = [], actor.hp, False
    original = session._advance_step

    def observe(dt, held):
        nonlocal applied, min_hp
        original(dt, held)
        if actor.has_buff(47) and applied is None:
            buff = next(b for b in actor.buffs if b.buff_id == 47)
            applied = {'time': session.app._game_timer, 'source': buff.source,
                       'params': buff.params, 'duration': buff.duration, **attack_snapshot(actor)}
        min_hp = min(min_hp, actor.hp)
        issues = errors_for(session)
        if issues and not errors:
            errors.append(issues)

    with patch('pygame.key.get_pressed', return_value=keys), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for _ in range(25 * fps):
            target = 10.5 if phase == 'approach' else 10.5 + 2 * side
            error = max(-3, min(3, (target - actor._x) * 3)) - actor.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            session.advance(1 / fps)
            if phase == 'approach' and applied and abs(actor._x - target) < .1:
                phase = 'leave'
            elif phase == 'leave' and abs(actor._x - target) < .1:
                phase = 'wait'
            elif phase == 'wait' and not actor.has_buff(47):
                completed = True
                break
            if errors or reset.call_count:
                break
        respawns = reset.call_count
    return {'tile_id': tile_id, 'side': side, 'fps': fps, 'applied': applied, 'completed': completed,
            'elapsed': session.app._game_timer, 'min_hp': min_hp, 'respawns': respawns,
            'errors': errors, 'final': attack_snapshot(actor), 'buff_after': actor.has_buff(47)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'API numeric effect and isolated real WorldSession contact with existing blocks; no playable combat encounter claim',
              'api': [api_case(base, params) for base in (.1, 1.25, 10) for params in ((), (0,), (3,))],
              'sources': [source_case(tile, side, fps) for tile in (390, 421)
                          for side in (-1, 1) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'api': len(result['api']), 'sources': len(result['sources']),
                      'source_completions': sum(r['completed'] for r in result['sources']),
                      'source_errors': sum(bool(r['errors']) for r in result['sources'])}))
