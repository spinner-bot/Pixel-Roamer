"""Repeatable keyboard-like route inputs; never teleport or assign velocity."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from maps import get_map
from creature import Player
from simulation import FixedStepClock, SIMULATION_HZ


def run_route(map_id, fps, upper=False):
    world = get_map(map_id)
    player = Player(0, 'route', *world.spawn_points, {})
    clock = FixedStepClock()

    def step(dt):
        player.tick_buffs(dt)
        player.refresh_movement_stats()
        player.update_physics(dt, world)
        player.collide_with_world(world, dt)
    targets = [(90, 9.9)]
    if upper:
        targets = [(24.5, 13.9), (38.5, 16.9), (55.5, 13.9), (90, 9.9)]
    frames = jumps = 0
    min_hp = player.hp
    visited = []
    rewards = []
    for tx, ty in targets:
        previous_score = player.score
        for _ in range(fps * 90):
            desired_v = max(-6, min(6, (tx - player._x) * 3))
            error = desired_v - player.v_x
            player.move(1 if error > 0.6 else -1 if error < -0.6 else 0)
            if ty > player._y + 1 and player.on_ground:
                # Approach the platform before jumping so ascent is visible.
                if abs(tx - player._x) < 8 or player._y > 12:
                    jumps += int(player.jump())
            clock.advance(1 / fps, step)
            frames += 1
            min_hp = min(min_hp, player.hp)
            if not player.alive or not all(math.isfinite(v) for v in
                    (player._x, player._y, player.v_x, player.v_y)):
                raise AssertionError(f'{map_id}/{fps}: dead or nonfinite')
            rect = player.get_game_rect()
            for obstacle, kind in world.get_nearby_solid_blocks_game(rect):
                dx = min(rect.x + rect.w, obstacle.x + obstacle.w) - max(rect.x, obstacle.x)
                dy = min(rect.y + rect.h, obstacle.y + obstacle.h) - max(rect.y, obstacle.y)
                if dx > 1e-7 and dy > 1e-7:
                    raise AssertionError(f'{map_id}/{fps}: overlap {kind.id}')
            if getattr(player, '_reached_end', False):
                visited.append([round(player._x, 3), round(player._y, 3)])
                break
            if tx != 90 and abs(player._x - tx) < 0.5 and abs(player._y - ty) < 0.15 and player.on_ground:
                visited.append([round(player._x, 3), round(player._y, 3)])
                break
        else:
            raise AssertionError(f'{map_id}/{fps}: stuck at {(player._x, player._y)} target {(tx, ty)}')
        rewards.append(player.score - previous_score)
    if not getattr(player, '_reached_end', False):
        raise AssertionError(f'{map_id}/{fps}: no finish')
    if min_hp < player.hp_max:
        raise AssertionError(f'{map_id}/{fps}: safe route caused damage: {min_hp}')
    if upper and any(value <= 0 for value in rewards[:3]):
        raise AssertionError(f'{map_id}/{fps}: missing upper platform rewards: {rewards}')
    return {'id': map_id, 'fps': fps, 'route': 'upper' if upper else 'main',
            'frames': frames, 'seconds': round(frames / fps, 3), 'jumps': jumps,
            'score': player.score, 'waypoint_rewards': rewards, 'min_hp': min_hp, 'waypoints': visited,
            'reached_end': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    results = [run_route(mid, fps, upper) for mid in (1001, 1002, 1003)
               for fps in (30, 60, 144) for upper in (False, True)]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
              cwd=ROOT, text=True).strip(),
              'scope': 'physics route inputs only; no real device visual or control acceptance',
              'simulation_hz': SIMULATION_HZ, 'runs': results}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
