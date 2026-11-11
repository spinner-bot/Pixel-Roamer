"""Long actual-source interaction soak with observed original force calls."""
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
import environment_forces
from buff_parameters import magnetic_response
from scripts import audit_session_soak
from world import World


def run(seconds):
    template = World(0, 'signed source interaction arena', 64, 32, gravity=-9.8,
                     spawn_points=(31.5, 5.9))
    for x in range(64):
        template.set_tile(x, 4, {22: 411, 31: 403, 37: 386}.get(x, 2))
    for x in (19, 43):
        for y in range(5, 8):
            template.set_tile(x, y, 338)
    factory = audit_session_soak.create_control_session
    original_force = environment_forces.apply_magnetism
    stats = {label: {'calls': 0, 'nonzero_force_calls': 0} for label in ('positive', 'reverse', 'neutral', 'unmagnetized')}
    sources = Counter()

    def session_factory(map_id):
        return factory(0, world=template.create_session())

    def observe_force(actor, world, types, dt):
        before = actor.v_x, actor.v_y
        original_force(actor, world, types, dt)
        if dt <= 0:
            return
        buff = next((b for b in actor.buffs if b.buff_id == 49), None)
        response = magnetic_response(buff.params) if buff else None
        label = ('unmagnetized' if buff is None else 'positive' if response > 0
                 else 'reverse' if response < 0 else 'neutral')
        stats[label]['calls'] += 1
        if abs(actor.v_x - before[0]) + abs(actor.v_y - before[1]) > 1e-10:
            stats[label]['nonzero_force_calls'] += 1
        if buff:
            sources[buff.source] += 1

    pygame.init()
    with patch.object(audit_session_soak, 'create_control_session', new=session_factory), \
            patch('environment_forces.apply_magnetism', new=observe_force):
        result = audit_session_soak.run(0, seconds)
    pygame.quit()
    return {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'scope': 'authored fixture of original386/403/411/338, actual source contact only, no Buff injection; original force called unchanged and delta observed; scripted WorldSession controls/pause/focus; not original-map reachability evidence',
            'run': result, 'response_force_calls': stats, 'active_source_calls': dict(sources)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    result = run(args.seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'errors': result['run']['errors'], 'sources': result['active_source_calls'],
                      'response_force_calls': result['response_force_calls']}))
    if result['run']['errors'] or any(result['response_force_calls'][k]['nonzero_force_calls'] == 0 for k in ('positive', 'reverse')):
        raise SystemExit(1)
