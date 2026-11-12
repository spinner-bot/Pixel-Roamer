"""Local production-control fixture for the original tall-tower checkpoint."""
from collections import defaultdict
import argparse
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
import spawn_placement
from maps import get_map, _apply_config
from scripts.control_session import create_control_session
from scripts.audit_feature_clearance import contact_pose
from scripts.audit_session_soak import errors_for
from teleport import can_place


def run(fps, world):
    # Deliberately local: this fixture does NOT prove a route from forest spawn.
    fixture_spawn = (446.5, 202.9)
    world.spawn_points = fixture_spawn
    session = create_control_session(3, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    failure, min_hp = None, player.hp
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch('spawn_placement.record_checkpoint', wraps=spawn_placement.record_checkpoint) as record, \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(2 * fps):
            error = max(-2, min(2, (447.5 - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            with patch('pygame.event.get', return_value=[]):
                app._handle_events()
            session.advance(1 / fps)
            min_hp = min(min_hp, player.hp)
            issues = errors_for(session)
            if issues or reset.call_count or not player.alive:
                failure = issues or 'death or respawn during local walk'
                break
        activation = {'position': player.get_center(), 'saved_spawn': player.spawn_pos,
                      'checkpoint_seen': 302 in player.contact_pool or player.stand_pool == 302,
                      'record_calls': record.call_count,
                      'valid': can_place(player, world, *player.get_center())}
        normal_respawns = reset.call_count
        keys.clear()
        player.clear_buffs()
        player.take_raw_damage(1e9)
        for _ in range(3):
            session.advance(1 / fps)
            if player.alive:
                break
        after_death = {'position': player.get_center(), 'saved_spawn': player.spawn_pos,
                       'valid': can_place(player, world, *player.get_center()),
                       'respawns': reset.call_count - normal_respawns, 'alive': player.alive}
    return {'fps': fps, 'fixture_spawn': fixture_spawn, 'scope': 'local tower-top walk only',
            'failure': failure, 'min_hp': min_hp, 'normal_respawns': normal_respawns,
            'activation': activation, 'after_deliberate_death': after_death}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = ModuleType('legacy_tower_checkpoint')
    old.__file__ = str(ROOT / 'maps/pixel_journey/map.py')
    source = subprocess.check_output(['git', 'show', '1988619:maps/pixel_journey/map.py'], cwd=ROOT, text=True, encoding='utf-8')
    exec(compile(source, old.__file__, 'exec'), old.__dict__)
    _apply_config(old.world, 'pixel_journey')
    current = get_map(3)
    before_actor = create_control_session(3, world=old.world.create_session()).app.player1
    after_actor = create_control_session(3, world=current.create_session()).app.player1
    changes = [{'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
                'after': current.get_tile(x, y).type_id}
               for x, y in sorted(set(old.world.grid) | set(current.grid))
               if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '1988619',
              'scope': 'explicit local tower-top spawn override, production dimensions/config/controls and deliberate death; NOT forest-to-tower reachability',
              'tile_changes': changes,
              'before_contact_pose': contact_pose(old.world, before_actor, (450, 201)),
              'after_contact_pose': contact_pose(current, after_actor, (447, 201)),
              'before': [run(fps, old.world.create_session()) for fps in (30, 60, 144)],
              'after': [run(fps, current.create_session()) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [r['activation'] for r in report[name]] for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
