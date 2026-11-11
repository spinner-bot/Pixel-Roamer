"""Actual pickup/return inputs, score-once semantics and dirty chunk rendering."""
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
from camera import Camera
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for
from world import World


def corner(world, block_id):
    surface = pygame.Surface((128, 64))
    camera = Camera(128, 64, world)
    camera.follow(4, 2)
    world.draw(surface, camera)
    texture = world._terrain_texture(world.block_types[block_id])
    rgb = tuple(surface.get_at((48, 32)))[:3]
    return {'rgb': rgb, 'native_alpha': texture.get_at((0, 0)).a,
            'composites': rgb == tuple(world._default_bt.color) and texture.get_at((0, 0)).a == 0}


def run(block_id, background):
    world = World(0, 'pickup compositing', 8, 4, default_block_id=background,
                  gravity=0, spawn_points=(1.5, 1.9), view_blocks_h=4)
    for x in range(8):
        world.set_tile(x, 0, 19)
    world.set_tile(3, 1, block_id)
    expected_score = world.block_types[block_id].special_data
    consumed_id = world.block_types[block_id].consumed_type_id
    before = corner(world, block_id)
    session = create_control_session(0, world=world)
    # launch_world uses a private mutable session; inspect that same session.
    world = session.app._current_map
    player = session.app.player1
    keys, failure, returning, reached = defaultdict(bool), None, False, False
    with patch('pygame.key.get_pressed', return_value=keys), patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(15 * 60):
            target = 1.5 if returning else 4.5
            if abs(player._x - target) < .18:
                if returning:
                    reached = True
                    break
                returning = True
                target = 1.5
            error = max(-4, min(4, (target - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            session.advance(1 / 60)
            issues = errors_for(session)
            if issues or reset.call_count:
                failure = issues or 'respawn'
                break
        respawns = reset.call_count
    actual_id = world.get_tile(3, 1).type_id
    return {'block_id': block_id, 'background': background, 'reached_and_returned': reached,
            'failure': failure, 'score': player.score, 'expected_score': expected_score,
            'tile_after': actual_id, 'expected_consumed_id': consumed_id,
            'before': before, 'after': corner(world, actual_id), 'respawns': respawns,
            'hp': player.hp, 'stamina': player.stamina}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'controller_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'actual 60FPS controls through pickup and back; synthetic 8x4 worlds with cached rendering',
              'runs': [run(block_id, background) for block_id in range(310, 320) for background in (0, 11, 12)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cases': len(report['runs']),
                      'score_once': sum(r['score'] == r['expected_score'] for r in report['runs']),
                      'before_composited': sum(r['before']['composites'] for r in report['runs']),
                      'after_composited': sum(r['after']['composites'] for r in report['runs'])}))


if __name__ == '__main__':
    main()
