"""Normal-spawn ice detour, optional explicit basin candidate, then original end."""
import argparse
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
from scripts.audit_cove_route import run as cove_route
from scripts.audit_session_soak import errors_for

CANDIDATE = ROOT / 'docs/进展报告/evidence/candidates/A92_cove_frost_pool_candidate.json'


def candidate_world(world):
    for tile in json.loads(CANDIDATE.read_text())['tiles']:
        current = world.get_block_type_by_coord(tile['x'], tile['y']).id
        if current != tile['before']:
            raise AssertionError(f'candidate would overwrite original cell: {tile}, current={current}')
        world.set_tile(tile['x'], tile['y'], tile['after'])


def ice_detour(app, session, keys, fps):
    actor = app.player1
    phase, started = 'dive', app._game_timer
    trace, transitions, touched, failures = [], [], set(), []
    min_hp, min_stamina = actor.hp, actor.stamina
    saw_cold, saw_frozen, thawed, shore_event = False, False, False, False
    jump_started = None
    for frame in range(60 * fps):
        elapsed = app._game_timer - started
        frozen = actor.has_buff(59)
        saw_cold |= any(b.buff_id == 51 and b.source == 373 for b in actor.buffs)
        if frozen:
            saw_frozen = True
        events = []
        old_phase = phase
        if phase == 'dive' and frozen:
            phase = 'frozen'
        elif phase == 'frozen' and not frozen:
            phase, thawed = 'swim', True
        elif phase == 'swim':
            surface = actor._swim_top_y
            if (surface is not None and abs(actor._y - surface) < .08
                    and actor._near_shore and actor._x > 247.8):
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
                phase, shore_event = 'shore', True
        elif phase == 'shore' and actor.on_ground and actor._x > 249 and not getattr(actor, '_shore_exit_pending', False):
            phase, jump_started = 'return', elapsed
            events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        elif phase == 'return' and actor.on_ground and abs(actor._x - 251.5) < .4 and abs(actor._y - 63.9) < .15:
            phase = 'complete'
        if old_phase != phase:
            transitions.append({'from': old_phase, 'to': phase, 'time': elapsed,
                                'position': actor.get_center()})
        if phase == 'complete':
            break
        tx = 246.5 if phase in ('dive', 'frozen') else 248.45 if phase == 'swim' else 249.8 if phase == 'shore' else 251.5
        desired = max(-3., min(3., (tx - actor._x) * 3))
        error = desired - actor.v_x
        keys.clear()
        keys[pygame.K_d], keys[pygame.K_a] = error > .15, error < -.15
        keys[pygame.K_w] = phase in ('swim', 'shore')
        if phase == 'frozen' or phase == 'return' and elapsed - jump_started < .6:
            keys[pygame.K_d] = keys[pygame.K_a] = False
        with patch('pygame.event.get', return_value=events):
            app._handle_events()
        session.advance(1 / fps)
        touched.update(actor.contact_pool)
        min_hp, min_stamina = min(min_hp, actor.hp), min(min_stamina, actor.stamina)
        issues = errors_for(session)
        if actor.fly_mode or app._player_lives_left != 3 or app._game_over:
            issues.append('flight, death, respawn or game over')
        if frame % max(1, fps // 10) == 0 or old_phase != phase:
            trace.append({'time': elapsed, 'phase': phase, 'position': actor.get_center(),
                          'velocity': [actor.v_x, actor.v_y], 'swim': actor.can_swim,
                          'surface': actor._swim_top_y, 'shore': getattr(actor, '_shore_exit_pending', False),
                          'on_ground': actor.on_ground, 'stamina': actor.stamina,
                          'buffs': [{'id': b.buff_id, 'source': b.source, 'remaining': b.duration}
                                    for b in actor.buffs]})
        if issues:
            failures.extend(issues)
            break
    if phase != 'complete' and not failures:
        failures.append('detour time budget exceeded: ' + phase)
    if not (saw_cold and saw_frozen and thawed and shore_event) and not failures:
        failures.append('required actual cold/freeze/thaw/shore coverage absent')
    return {'seconds': app._game_timer - started, 'phase': phase,
            'failure': '; '.join(failures) if failures else None,
            'cold_source373': saw_cold, 'freeze_seen': saw_frozen, 'thawed': thawed,
            'shore_event': shore_event, 'transitions': transitions,
            'min_hp': min_hp, 'min_stamina': min_stamina,
            'touched_types': sorted(touched), 'trace': trace}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', action='store_true')
    parser.add_argument('--fps', type=int, nargs='+', choices=(30, 60, 144), default=(30, 60, 144))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'candidate_geometry': args.candidate,
              'scope': 'original spawn/main controls through ice detour to original formal end; optional candidate changes world cells before route, no actor position/status injection; offscreen input route, not device acceptance',
              'runs': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for fps in args.fps:
        result = cove_route(fps, world_hook=candidate_world if args.candidate else None, ice_hook=ice_detour)
        report['runs'].append(result)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'fps': fps, 'win': result['game_win'], 'failure': result['failure'],
                          'detour': result.get('ice_extension', {}).get('phase')}), flush=True)
    if any(r['failure'] or not r['game_win'] for r in report['runs']):
        raise SystemExit(1)
