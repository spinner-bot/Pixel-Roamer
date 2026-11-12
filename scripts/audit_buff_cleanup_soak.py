"""Observe actual contact cleanup in an explicitly synthetic source arena."""
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
from block_type import BlockType
from block_types_data import BLOCK_TYPES
from creature import Creature
from scripts import audit_session_soak
from world import World


def run(seconds):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # The shipped catalog has no source of9. This local source exercises the
    # generic block->Buff path without adding catalog/gameplay content.
    types = dict(BLOCK_TYPES)
    types[5000] = BlockType(5000, name='fixture_fire_resistance', is_solid=False,
                           buff_ids=(9,), buff_params_list=((),), buff_durations=(6.,))
    template = World(0, 'cleanup relation contact arena', 64, 32, gravity=-9.8,
                     spawn_points=(31.5, 5.9), block_types=types)
    for x in range(64):
        template.set_tile(x, 4, 2)
        template.set_tile(x, 17, 2)
    for y in range(5, 17):
        for x in (0, 63):
            template.set_tile(x, y, 2)
        for x in range(19, 23):
            template.set_tile(x, y, 7)
        for x in range(29, 34):
            template.set_tile(x, y, 5000)
        for x in range(43, 47):
            template.set_tile(x, y, 426)
    factory = audit_session_soak.create_control_session
    apply_buff = Creature.apply_buff
    errors_for = audit_session_soak.errors_for
    observations = Counter()

    def observe_apply(actor, buff_id, *args, **kwargs):
        had_target, had_counter = actor.has_buff(9), actor.has_buff(15)
        result = apply_buff(actor, buff_id, *args, **kwargs)
        if buff_id == 9:
            observations['target_calls'] += 1
            if not had_target and actor.has_buff(9):
                observations['target_acquired'] += 1
            if had_counter and not actor.has_buff(9):
                observations['target_blocked_by_wet'] += 1
        if buff_id == 15:
            observations['wet_calls'] += 1
            if had_target and not actor.has_buff(9):
                observations['target_cleared_by_wet'] += 1
        if actor.has_buff(9) and actor.has_buff(15):
            observations['forbidden_coexistence'] += 1
        return result

    def observe_errors(session):
        issues = errors_for(session)
        actor = session.app.player1
        if actor.has_buff(9) and actor.has_buff(15):
            issues.append('cleanup relation9->15 violated')
        return issues

    pygame.init()
    with patch.object(audit_session_soak, 'create_control_session',
                      new=lambda _: factory(0, world=template.create_session())), \
            patch.object(Creature, 'apply_buff', new=observe_apply), \
            patch.object(audit_session_soak, 'errors_for', new=observe_errors):
        result = audit_session_soak.run(0, seconds)
    pygame.quit()
    missing = [key for key in ('target_acquired', 'target_blocked_by_wet', 'target_cleared_by_wet')
               if not observations[key]]
    return {'code_revision': revision,
            'scope': 'synthetic source5000 associates original9; actual7/426 supply15; unchanged original apply_buff observed; no actor Buff injection; scripted controls/pause/focus, not normal-map or physical-device acceptance',
            'run': result, 'observations': dict(observations), 'missing_coverage': missing}


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
    print(json.dumps({key: report[key] for key in ('observations', 'missing_coverage')}))
    if report['run']['errors'] or report['missing_coverage']:
        raise SystemExit(1)
