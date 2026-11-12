"""Exercise original cold sources and water with counted freeze/thaw coverage."""
import argparse
from collections import Counter
import json
import math
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
from buff_controls import action_blocked
from creature import Creature
from scripts import audit_session_soak
from world import World


def run(seconds):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    template = World(0, 'original cold-water interaction arena', 64, 32, gravity=-9.8,
                     spawn_points=(31.5, 5.9))
    for x in range(64):
        template.set_tile(x, 4, 373 if 29 <= x <= 33 else 395 if 50 <= x <= 53 else 2)
        template.set_tile(x, 17, 2)
    for y in range(5, 17):
        for x in (0, 63):
            template.set_tile(x, y, 2)
        for x in (*range(19, 23), *range(43, 47)):
            template.set_tile(x, y, 7)
        for x in range(10, 14):
            template.set_tile(x, y, 410)
    factory, original_apply = audit_session_soak.create_control_session, Creature.apply_buff
    original_errors = audit_session_soak.errors_for
    sources, counts = Counter(), Counter()
    observed_frozen = False

    def observe_apply(actor, buff_id, *args, **kwargs):
        before = actor.has_buff(59)
        result = original_apply(actor, buff_id, *args, **kwargs)
        if buff_id == 51:
            sources[kwargs.get('source')] += 1
        if buff_id == 59:
            counts['freeze_attempts'] += 1
            if actor.has_buff(59) and not before:
                counts['new_freezes'] += 1
                effect = next(b for b in actor.buffs if b.buff_id == 59)
                if effect.initial_duration != 4:
                    counts['wrong_duration'] += 1
        return result

    def observe_errors(session):
        nonlocal observed_frozen
        actor = session.app.player1
        issues = original_errors(session)
        frozen = actor.has_buff(59)
        if frozen:
            counts['frozen_frames'] += 1
            if not all(action_blocked(actor, action) for action in ('horizontal', 'jump', 'climb', 'swim')):
                issues.append('frozen control restriction absent')
            if actor.is_climbing or actor._shore_exit_pending:
                issues.append('frozen actor retained active climb or shore exit')
        elif observed_frozen:
            counts['observed_thaws'] += 1
        observed_frozen = frozen
        return issues

    pygame.init()
    with patch.object(audit_session_soak, 'create_control_session',
                      new=lambda _: factory(0, world=template.create_session())), \
            patch.object(Creature, 'apply_buff', new=observe_apply), \
            patch.object(audit_session_soak, 'errors_for', new=observe_errors):
        result = audit_session_soak.run(0, seconds)
    pygame.quit()
    missing = [str(source) for source in (373, 395, 410) if not sources[source]]
    missing += [key for key in ('new_freezes', 'observed_thaws') if not counts[key]]
    return {'code_revision': revision,
            'scope': 'synthetic arena of original373/395/410 plus7; actual source contacts only, no actor Buff injection; original methods observed unchanged; WorldSession inputs/pause/focus, not original-map reachability or device acceptance',
            'run': result, 'cold_source_calls': dict(sources), 'observations': dict(counts),
            'missing_coverage': missing}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    report = run(args.seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('cold_source_calls', 'observations', 'missing_coverage')}))
    if report['run']['errors'] or report['missing_coverage'] or report['observations'].get('wrong_duration'):
        raise SystemExit(1)
