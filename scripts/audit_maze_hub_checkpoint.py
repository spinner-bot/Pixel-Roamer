"""Verify the existing maze hub checkpoint actually activates from normal spawn."""
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
from teleport import can_place


def run(fps, world):
    session = create_control_session(4, world=world)
    player = session.app.player1
    keys = defaultdict(bool)
    with patch('pygame.key.get_pressed', return_value=keys), \
            patch('spawn_placement.record_checkpoint', wraps=spawn_placement.record_checkpoint) as record, \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for _ in range(fps):
            session.advance(1 / fps)
        checkpoint_seen = 302 in player.contact_pool or player.stand_pool == 302
        snapshot = {'position': player.get_center(), 'saved_spawn': player.spawn_pos,
                    'checkpoint_seen': checkpoint_seen, 'record_calls': record.call_count,
                    'valid': can_place(player, world, *player.get_center())}
        player.clear_buffs()
        player.take_raw_damage(1e9)
        for _ in range(3):
            session.advance(1 / fps)
            if player.alive:
                break
        final = {'position': player.get_center(), 'saved_spawn': player.spawn_pos,
                 'valid': can_place(player, world, *player.get_center()), 'respawns': reset.call_count,
                 'alive': player.alive}
    return {'fps': fps, 'activation': snapshot, 'after_deliberate_death': final}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = ModuleType('legacy_maze_hub_checkpoint')
    old.__file__ = str(ROOT / 'maps/loop_maze/map.py')
    source = subprocess.check_output(['git', 'show', '3c3f481:maps/loop_maze/map.py'], cwd=ROOT, text=True, encoding='utf-8')
    exec(compile(source, old.__file__, 'exec'), old.__dict__)
    _apply_config(old.world, 'loop_maze')
    current = get_map(4)
    before_player = create_control_session(4, world=old.world.create_session()).app.player1
    after_player = create_control_session(4, world=current.create_session()).app.player1
    changes = [{'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
                'after': current.get_tile(x, y).type_id}
               for x, y in sorted(set(old.world.grid) | set(current.grid))
               if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': '3c3f481',
              'scope': 'normal idle spawn checkpoint activation then deliberate lethal test hit and production respawn; not other hidden anchors',
              'tile_changes': changes,
              'before_contact_pose': contact_pose(old.world, before_player, (24, 15)),
              'after_contact_pose': contact_pose(current, after_player, (22, 15)),
              'before': [run(fps, old.world.create_session()) for fps in (30, 60, 144)],
              'after': [run(fps, get_map(4)) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [r['activation']['record_calls'] for r in report[name]] for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
