"""Original map1 spawn to Buff-only flower, remote pickups and natural expiry."""
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
from maps import get_map
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, capture_prefix=None):
    if capture_prefix:
        from pixel_roamer.application import GameApp
        from pixel_roamer.ui.config import PAGE_WORLD
        app = GameApp()
        app.set_page(PAGE_WORLD, map_id=1)
        session = app.session
    else:
        session = create_control_session(1)
        app = session.app
    actor, world = app.player1, app._current_map
    initial = {'position': actor.get_center(), 'buff14': actor.has_buff(14), 'score': actor.score}
    expected_score = sum(int(world.block_types[world.get_tile(x, y).type_id].special_data)
                         for x, y in ((1, 26), (0, 25)))
    source = world.block_types[439]
    keys = defaultdict(bool)
    phase, applied, reward, errors = 'approach', None, None, []
    transitions, screenshots = [], {}
    original_step = session._advance_step
    min_hp, min_stamina = actor.hp, actor.stamina

    def picture(label):
        if capture_prefix is None or label in screenshots:
            return
        app.world_view.draw(0)
        path = Path(str(capture_prefix) + '_' + label + '.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(app.logic_surface, str(path))
        screenshots[label] = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)

    def observe(dt, held):
        nonlocal applied, reward, min_hp, min_stamina
        original_step(dt, held)
        current = next((b for b in actor.buffs if b.buff_id == 14), None)
        if current is not None and applied is None:
            applied = {'time': app._game_timer, 'position': actor.get_center(),
                       'source': current.source, 'params': current.params, 'remaining': current.duration,
                       'contacts': sorted(actor.contact_pool)}
        if actor.score and reward is None:
            reward = {'time': app._game_timer, 'position': actor.get_center(), 'score': actor.score,
                      'flights': len(actor._pickup_flights)}
        min_hp, min_stamina = min(min_hp, actor.hp), min(min_stamina, actor.stamina)
        issues = errors_for(session)
        if issues and not errors:
            errors.append({'time': app._game_timer, 'issues': issues})

    completed = False
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(session, '_advance_step', side_effect=observe), \
            patch.object(actor, 'reset', wraps=actor.reset) as reset:
        for frame in range(40 * fps):
            target_x = 3.5 if phase == 'approach' else 5.
            error = max(-3, min(3, (target_x - actor._x) * 3)) - actor.v_x
            keys[pygame.K_d], keys[pygame.K_a] = error > .2, error < -.2
            with patch('pygame.event.get', return_value=[]):
                app._handle_events()
            session.advance(1 / fps)
            if applied and reward is None:
                picture('source')
            if reward and app._game_timer - reward['time'] >= .1 and actor._pickup_flights:
                picture('attracting')
            if phase == 'approach' and abs(actor._x - 3.5) < .1 and actor.score == expected_score:
                phase = 'leave'
                transitions.append({'phase': phase, 'time': app._game_timer, 'position': actor.get_center()})
            elif phase == 'leave' and abs(actor._x - 5) < .1 and actor.on_ground:
                phase = 'wait_for_expiry'
                transitions.append({'phase': phase, 'time': app._game_timer, 'position': actor.get_center()})
            elif phase == 'wait_for_expiry' and not actor.has_buff(14):
                completed = actor.score == expected_score and not actor._pickup_flights
                picture('expired')
                break
            if errors or reset.call_count:
                break
        respawns = reset.call_count
    fresh = get_map(1)
    result = {'fps': fps, 'initial': initial, 'completed': completed, 'phase': phase,
        'elapsed': app._game_timer, 'applied': applied, 'reward': reward,
        'expected_score': expected_score, 'final_score': actor.score, 'position': actor.get_center(),
        'buff14_at_finish': actor.has_buff(14), 'flights_at_finish': len(actor._pickup_flights),
        'tiles': {f'{x},{y}': world.get_tile(x, y).type_id for x, y in ((3, 25), (1, 26), (0, 25))},
        'fresh_tiles': {f'{x},{y}': fresh.get_tile(x, y).type_id for x, y in ((3, 25), (1, 26), (0, 25))},
        'source_definition': {'buff_ids': source.buff_ids, 'params': source.buff_params_list,
                              'durations': source.buff_durations, 'special': source.special},
        'min_hp': min_hp, 'min_stamina': min_stamina, 'respawns': respawns, 'errors': errors,
        'transitions': transitions, 'screenshots': screenshots}
    if capture_prefix:
        pygame.quit()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--capture-prefix', type=Path)
    args = parser.parse_args()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'normal authored map1 spawn and real movement; no direct Buff application or position/state transfer',
        'sources': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                    ('scripts/audit_magnetic_source_route.py', 'maps/test_world/map.py',
                     'maps/test_world/buff_sources.json', 'data/catalogs/extensions/blocks_magnetic.json')},
        'runs': [run(fps, args.capture_prefix if fps == 60 else None) for fps in (30, 60, 144)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: r[k] for k in ('fps', 'completed', 'elapsed', 'final_score', 'errors')}
                      for r in result['runs']]))
