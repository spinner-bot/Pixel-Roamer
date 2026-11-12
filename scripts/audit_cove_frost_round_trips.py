"""Repeated real-map dry/reentry loops through the basin, then formal victory."""
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
from scripts.audit_cove_frost_pool import ice_detour
from scripts.audit_cove_route import run as cove_route
from scripts.audit_session_soak import errors_for


def return_to_first(app, session, keys, fps):
    actor, started = app.player1, app._game_timer
    trace, failures, jumped = [], [], False
    arrived = False
    for frame in range(15 * fps):
        elapsed = app._game_timer - started
        tx = 245.5
        if (actor.on_ground and abs(actor._x - tx) < .3 and abs(actor._y - 63.9) < .15
                and not actor.has_buff(15) and not actor.has_buff(59)):
            arrived = True
            break
        keys.clear()
        desired = max(-6., min(6., (tx - actor._x) * 3))
        keys[pygame.K_d], keys[pygame.K_a] = desired - actor.v_x > .3, desired - actor.v_x < -.3
        events = []
        if actor.on_ground and abs(actor._x - tx) > 1:
            events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            jumped = True
        with patch('pygame.event.get', return_value=events):
            app._handle_events()
        session.advance(1 / fps)
        if frame % max(1, fps // 10) == 0:
            trace.append({'time': elapsed, 'position': actor.get_center(),
                          'velocity': [actor.v_x, actor.v_y], 'on_ground': actor.on_ground,
                          'wet': actor.has_buff(15), 'frozen': actor.has_buff(59)})
        issues = errors_for(session)
        if actor.fly_mode or app._player_lives_left != 3 or app._game_over:
            issues.append('flight, death, respawn or game over')
        if issues:
            failures.extend(issues)
            break
    if not arrived and not failures:
        failures.append('return-to-first pillar time budget exceeded')
    return {'seconds': app._game_timer - started, 'arrived_dry': arrived,
            'jump_input': jumped, 'failure': '; '.join(failures) if failures else None,
            'trace': trace}


def repeat_detour(app, session, keys, fps, loops):
    started = app._game_timer
    results, returns = [], []
    for index in range(loops):
        if index:
            returns.append(return_to_first(app, session, keys, fps))
            if returns[-1]['failure']:
                break
        results.append(ice_detour(app, session, keys, fps))
        if results[-1]['failure']:
            break
    failures = [r['failure'] for r in (*results, *returns) if r['failure']]
    if len(results) != loops and not failures:
        failures.append('requested loop coverage absent')
    return {'seconds': app._game_timer - started, 'phase': 'complete' if not failures else 'failed',
            'failure': '; '.join(failures) if failures else None, 'requested_loops': loops,
            'loops': results, 'dry_returns': returns,
            'min_hp': min(r['min_hp'] for r in results),
            'min_stamina': min(r['min_stamina'] for r in results),
            'touched_types': sorted({bid for r in results for bid in r['touched_types']})}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--loops', type=int, default=3)
    parser.add_argument('--fps', type=int, nargs='+', choices=(30,60,144), default=(30,60,144))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 2 <= args.loops <= 20:
        parser.error('--loops must be between2 and20')
    report = {'code_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'scope': 'original spawn then repeated original373/water freeze-thaw-shore, actual jump return to first pillar while fully dry, then original formal victory; no actor position/Buff injection or flight; not all-region/device acceptance',
              'requested_loops': args.loops, 'runs': []}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for fps in args.fps:
        row = cove_route(fps, ice_hook=lambda a,s,k,f: repeat_detour(a,s,k,f,args.loops))
        report['runs'].append(row)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'fps':fps,'win':row['game_win'],'failure':row['failure'],
                          'loops':len(row['ice_extension']['loops'])}),flush=True)
    raise SystemExit(1 if any(r['failure'] or not r['game_win'] for r in report['runs']) else 0)
