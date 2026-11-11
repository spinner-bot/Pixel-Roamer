"""Check the real maze spawn component and walk/jump out of the west hub door."""
from collections import defaultdict, deque
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
from maps import get_map, _apply_config
from player_factory import create_world_player
from scripts.control_session import create_control_session
from teleport import can_place
from scripts.maze_controls import west_departure


def spawn_component(world):
    # Sample free-body connectivity separately from gravity and available controls.
    player = create_world_player(world, {})
    start = (round(player._x * 10), round(player._y * 10))
    queue, seen = deque([start]), {start}
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            point = (x + dx, y + dy)
            if point in seen or not (200 <= point[0] <= 280 and 140 <= point[1] <= 250):
                continue
            if can_place(player, world, point[0] / 10, point[1] / 10):
                seen.add(point)
                queue.append(point)
    return {'samples': len(seen), 'west_boundary_reached': any(x == 200 for x, y in seen),
            'bounds': [min(x for x, y in seen) / 10, max(x for x, y in seen) / 10,
                       min(y for x, y in seen) / 10, max(y for x, y in seen) / 10],
            'scope': 'local sampled free-body connectivity, not a physical route proof'}


def run(fps, world=None):
    session = create_control_session(4, world=world)
    app, player = session.app, session.app.player1
    keys = defaultdict(bool)
    trace = []
    min_hp, min_stamina = player.hp, player.stamina
    escaped, failure = False, None
    departure_stage = 0
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for frame in range(20 * fps):
            departure_stage, target_x, jump, _ = west_departure(player, departure_stage)
            error = max(-5, min(5, (target_x - player._x) * 3)) - player.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)] if jump else []
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(1 / fps)
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            if frame % fps == 0:
                trace.append({'time': app._game_timer, 'position': player.get_center(),
                              'hp': player.hp, 'stamina': player.stamina, 'ground': player.on_ground})
            if not can_place(player, app._current_map, *player.get_center()):
                failure = 'invalid placement'
                break
            if not player.alive or reset.call_count or player.fly_mode:
                failure = 'death respawn or flight'
                break
            if player._x < 20.4 and player.on_ground and abs(player._y - 22.9) < .05:
                escaped = True
                break
        respawns = reset.call_count
    if not escaped and failure is None:
        failure = 'west corridor not reached'
    return {'fps': fps, 'escaped_to_west_corridor': escaped, 'failure': failure,
            'timer': app._game_timer, 'control_frames': frame + 1, 'position': player.get_center(),
            'min_hp': min_hp, 'min_stamina': min_stamina, 'respawns': respawns, 'trace': trace}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    old = ModuleType('legacy_maze_exit')
    old.__file__ = str(ROOT / 'maps/loop_maze/map.py')
    source = subprocess.check_output(['git', 'show', 'b1e1fb9:maps/loop_maze/map.py'], cwd=ROOT, text=True)
    exec(compile(source, old.__file__, 'exec'), old.__dict__)
    _apply_config(old.world, 'loop_maze')
    current = get_map(4)
    changes = [{'position': [x, y], 'before': old.world.get_tile(x, y).type_id,
                'after': current.get_tile(x, y).type_id}
               for x, y in sorted(set(old.world.grid) | set(current.grid))
               if old.world.get_tile(x, y).type_id != current.get_tile(x, y).type_id]
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'legacy_revision': 'b1e1fb9',
              'scope': 'normal-spawn west hub exit; no flight, injected buffs or positional relocation; rest of maze separate',
              'tile_changes': changes, 'before_component': spawn_component(old.world),
              'after_component': spawn_component(current),
              'before': [run(fps, old.world.create_session()) for fps in (30, 60, 144)],
              'after': [run(fps) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({name: [r['escaped_to_west_corridor'] for r in report[name]] for name in ('before', 'after')}))


if __name__ == '__main__':
    main()
