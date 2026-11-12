"""Existing double-jump ability across real landing, walkoff and climbing cycles."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from creature import Player
from scripts.control_session import create_control_session
from teleport import can_place
from world import World


def ability_session(*, ladder=False, ceiling=False, floor_id=2, player_class=Player):
    world = World(0, 'air jump cycles', 12, 30, gravity=-6.5, spawn_points=(2.5, 1.9))
    for x in range(5):
        world.set_tile(x, 0, floor_id)
    if ladder:
        for y in range(1, 13):
            world.set_tile(2, y, 9)
    if ceiling:
        for x in range(12):
            world.set_tile(x, 8, 2)
    with patch('player_factory.Player', player_class):
        session = create_control_session(0, world=world)
    # Ability-specific fixture only: full map victory audits never grant buffs.
    session.app.player1.apply_buff(37, (), 30)
    session.app.player1.collide_with_world(world, 0)
    return session


def keydown(session, key):
    with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=key)]):
        session.app._handle_events()


def advance(session, fps, frames=1, keys=None):
    held = defaultdict(bool, keys or {})
    with patch('pygame.key.get_pressed', return_value=held), patch('sfx.play_jump'):
        for _ in range(frames):
            session.advance(1 / fps)
            player = session.app.player1
            if not can_place(player, session.app._current_map, *player.get_center()):
                raise AssertionError('air-jump fixture entered terrain or invalid coordinates')


def spend_air_jump(session, fps):
    keydown(session, pygame.K_SPACE)
    advance(session, fps, max(1, int(.25 * fps)))
    keydown(session, pygame.K_SPACE)
    advance(session, fps, 3)


def state(player):
    return {'position': player.get_center(), 'vy': player.v_y, 'air_used': player._air_jumps_used,
            'ground': player.on_ground, 'climbing': player.is_climbing,
            'stamina': player.stamina, 'ability_active': player.has_buff(37)}


def exercise(kind, fps, player_class=Player):
    session = ability_session(ladder=kind == 'climb_release', floor_id=33 if kind == 'cloud_walkoff' else 2,
                              player_class=player_class)
    player = session.app.player1
    spend_air_jump(session, fps)
    spent = state(player)
    if kind == 'climb_release':
        keydown(session, pygame.K_w)
        support = state(player)
        keydown(session, pygame.K_s)
        advance(session, fps, 1)
    else:
        for _ in range(8 * fps):
            advance(session, fps)
            if player.on_ground:
                break
        support = state(player)
        for _ in range(10 * fps):
            advance(session, fps, keys={pygame.K_d: True})
            if not player.on_ground:
                break
    before = state(player)
    keydown(session, pygame.K_SPACE)
    advance(session, fps, 3)
    after = state(player)
    return {'kind': kind, 'fps': fps, 'spent': spent, 'support': support,
            'before_retry': before, 'after_retry': after,
            'succeeded': after['vy'] > 0 and after['stamina'] < before['stamina'] - 10}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = ModuleType('legacy_air_jump_creature')
    module.__file__ = str(ROOT / 'creature.py')
    source = subprocess.check_output(['git', 'show', '444f39a:creature.py'], cwd=ROOT, text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                     text=True).strip(),
              'legacy_revision': '444f39a', 'scope': 'isolated existing buff 37 fixture with production session inputs; not map victory or device acceptance'}
    for name, player_class in (('before', module.Player), ('after', Player)):
        report[name] = [exercise(kind, fps, player_class) for kind in
                        ('ground_walkoff', 'cloud_walkoff', 'climb_release') for fps in (30, 60, 144)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: sum(run['succeeded'] for run in report[name]) for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
