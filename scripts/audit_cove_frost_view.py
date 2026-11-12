"""Capture initialized GameApp rendering along the actual cold basin input route."""
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
from pixel_roamer.application import GameApp
from scripts.audit_cove_frost_pool import candidate_world, ice_detour
from scripts.audit_cove_route import run as cove_route
from scripts.control_session import terminal_snapshot


def run(output, candidate):
    captures, apps = [], []
    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = 'A92_cove_frost_' + ('candidate' if candidate else 'production')

    def app_factory():
        app = GameApp()
        apps.append(app)
        return app

    def capture(label, app, session):
        before = terminal_snapshot(session)
        app.world_view.draw(0)
        if terminal_snapshot(session) != before:
            raise AssertionError('zero-time native capture changed simulation')
        path = output.parent / 'art' / f'{prefix}_{label}.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(app.logic_surface, str(path))
        captures.append({'phase': label, 'path': str(path.relative_to(ROOT)),
                         'state': before, 'buff_sources': [(b.buff_id, b.source) for b in app.player1.buffs]})

    def observe_detour(app, session, keys, fps):
        advance = session.advance
        seen = set()

        def capture_advance(dt):
            result = advance(dt)
            actor = app.player1
            label = ('frozen' if actor.has_buff(59) else
                     'shore' if getattr(actor, '_shore_exit_pending', False) else
                     'thaw' if 'frozen' in seen and actor.can_swim else
                     'return' if actor.on_ground and abs(actor._x - 251.5) < .4
                     and abs(actor._y - 63.9) < .15 else None)
            if label is not None and label not in seen:
                capture(label, app, session)
                seen.add(label)
            return result

        with patch.object(session, 'advance', new=capture_advance):
            return ice_detour(app, session, keys, fps)

    result = cove_route(60, world_hook=candidate_world if candidate else None,
                        ice_hook=observe_detour, app_factory=app_factory)
    capture('finish', apps[0], apps[0].session)
    pygame.quit()
    missing = sorted({'frozen', 'thaw', 'shore', 'return', 'finish'} - {r['phase'] for r in captures})
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'initialized GameApp and real WorldView logical-surface rendering during normal-spawn controls; SDL dummy captures, not physical-device acceptance; capture must preserve simulation',
              'candidate_geometry': candidate, 'route': result, 'captures': captures,
              'missing_captures': missing}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'win': result['game_win'], 'failure': result['failure'],
                      'captures': [r['phase'] for r in captures], 'missing': missing}))
    return not missing and not result['failure'] and result['game_win']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output, args.candidate) else 1)
