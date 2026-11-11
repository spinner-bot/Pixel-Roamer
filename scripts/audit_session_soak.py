"""Repeatable production-session input soak; no claim of complete map traversal."""
from collections import defaultdict
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from collision import spans_overlap
from maps import list_maps
from scripts.control_session import create_control_session, terminal_snapshot
from world import MAX_CHUNK_SURFACES, MAX_SCALED_CACHE_BYTES


def state(session):
    snapshot = terminal_snapshot(session)
    snapshot['buff_clock'] = session.app.player1._buff_game_time
    snapshot['clock_remainder'] = session.clock.remainder
    return snapshot


def errors_for(session):
    app, player = session.app, session.app.player1
    world = app._current_map
    errors = []
    values = (*player.get_center(), player.v_x, player.v_y, player.hp, player.stamina,
              player.shield, app._game_timer)
    if not all(math.isfinite(v) for v in values):
        return ['nonfinite state']
    if not (-1e-7 <= player.hp <= player.hp_max + 1e-7):
        errors.append('health outside bounds')
    if not (-1e-7 <= player.stamina <= player.stamina_max + 1e-7):
        errors.append('stamina outside bounds')
    if player.shield < 0:
        errors.append('negative shield')
    # One-way platforms can be crossed from below; ghost effects allow solid overlap.
    if player.alive and not player.has_buff(48) and not player._phantom_active:
        rect = player.get_game_rect()
        for block, kind in world.get_nearby_solid_blocks_game(rect):
            if (not kind.one_way and spans_overlap(rect.x, rect.w, block.x, block.w)
                    and spans_overlap(rect.y, rect.h, block.y, block.h)):
                errors.append(f'solid overlap: {kind.id} at {block.x},{block.y}')
                break
    if (len(world._chunk_surfaces) > MAX_CHUNK_SURFACES
            or world._scaled_chunk_cache_bytes > MAX_SCALED_CACHE_BYTES):
        errors.append('terrain cache exceeded budget')
    return errors


def run(map_id, seconds):
    started = time.perf_counter()
    session = create_control_session(map_id)
    keys = defaultdict(bool)
    surface = pygame.Surface((640, 360))
    elapsed, frames, resets, rounds, pauses, next_pause, next_draw = 0., 0, 0, 1, 0, 30., 0.
    failures, trace = [], []
    min_hp, min_stamina = session.app.player1.hp, session.app.player1.stamina
    next_jump = .75

    def observe_reset(player):
        original = player.reset
        def reset(*args, **kwargs):
            nonlocal resets
            resets += 1
            return original(*args, **kwargs)
        player.reset = reset

    observe_reset(session.app.player1)
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'):
        while elapsed < seconds - 1e-8:
            app, player = session.app, session.app.player1
            fps = (30, 60, 144)[int(elapsed // 10) % 3]
            dt = min(1 / fps, seconds - elapsed)
            keys.clear()
            phase = int(elapsed // 8) % 4
            keys[pygame.K_d if phase < 2 else pygame.K_a] = True
            keys[pygame.K_w] = int(elapsed // 4) % 3 != 2
            keys[pygame.K_s] = int(elapsed // 4) % 3 == 2
            events = []
            if elapsed >= next_jump - 1e-8:
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                next_jump += .75
            with patch('pygame.event.get', return_value=events):
                app._handle_events()
            session.advance(dt)
            elapsed += dt
            frames += 1
            min_hp, min_stamina = min(min_hp, player.hp), min(min_stamina, player.stamina)
            issues = errors_for(session)
            if issues:
                failures.append({'elapsed': elapsed, 'errors': issues, 'state': state(session)})
                break
            if elapsed >= next_draw - 1e-8:
                app._current_map.draw(surface, app.camera)
                trace.append({'elapsed': elapsed, 'round': rounds, 'state': terminal_snapshot(session)})
                next_draw += 10
            if elapsed >= next_pause - 1e-8:
                # Use actual help events; a large paused dt must not accumulate catch-up.
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
                with patch('pygame.event.get', return_value=[event]):
                    app._handle_events()
                before = state(session)
                app.jump_pressed = True
                session.advance(17.25)
                if before != state(session) or app.jump_pressed:
                    failures.append({'elapsed': elapsed, 'errors': ['help pause changed simulation']})
                    break
                with patch('pygame.event.get', return_value=[event]):
                    app._handle_events()
                app.focused = False
                before = state(session)
                app.jump_pressed = True
                session.advance(19.5)
                if before != state(session) or app.jump_pressed:
                    failures.append({'elapsed': elapsed, 'errors': ['unfocused session changed simulation']})
                    break
                app.focused = True
                pauses += 1
                next_pause += 30
            if app._game_win or app._game_over:
                before = terminal_snapshot(session)
                session.advance(2)
                if before != terminal_snapshot(session):
                    failures.append({'elapsed': elapsed, 'errors': ['terminal state changed']})
                    break
                session = create_control_session(map_id)
                observe_reset(session.app.player1)
                rounds += 1
    return {'map_id': map_id, 'requested_seconds': seconds, 'input_seconds': elapsed,
            'frames': frames, 'rounds': rounds, 'respawns': resets, 'pause_pairs': pauses,
            'min_hp': min_hp, 'min_stamina': min_stamina, 'errors': failures,
            'trace': trace, 'wall_seconds': time.perf_counter() - started}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--maps', type=int, nargs='+')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    pygame.init()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'normal-spawn session input soak; finite scripted paths, not all-region or device acceptance; focus flag tests WorldSession only',
              'fps_cycle': [30, 60, 144], 'simulation_hz': 120, 'runs': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for map_id in args.maps or sorted(list_maps()):
        result = run(map_id, args.seconds)
        report['runs'].append(result)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({k: result[k] for k in ('map_id', 'input_seconds', 'respawns', 'errors')}, ensure_ascii=False), flush=True)
    pygame.quit()
    if any(r['errors'] for r in report['runs']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
