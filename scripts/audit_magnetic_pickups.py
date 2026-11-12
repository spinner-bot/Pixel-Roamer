"""Observe existing score pickups with and without the declared magnetic Buff."""
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
from world import World
from scripts.control_session import create_control_session
from scripts.audit_session_soak import errors_for


def run(fps, tile_id, side, active):
    world = World(0, 'magnetic pickup contract', 20, 12, gravity=0, spawn_points=(5.5, 4.5))
    gx = 6 if side > 0 else 4
    world.set_tile(gx, 4, tile_id)
    session = create_control_session(0, world=world)
    app, player = session.app, session.app.player1
    definition = app._current_map.block_types[tile_id]
    if active:
        player.apply_buff(14, (), 5)
    errors = []
    with patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
            patch.object(player, 'reset', wraps=player.reset) as reset:
        for _ in range(2 * fps):
            session.advance(1 / fps)
            errors.extend(errors_for(session))
        respawns = reset.call_count
    return dict(fps=fps, tile_id=tile_id, side=side, buff_active=active,
                position=player.get_center(), score=player.score,
                expected_score=int(definition.special_data) if active else 0,
                final_tile=app._current_map.get_tile(gx, 4).type_id,
                consumed_type_id=definition.consumed_type_id,
                attracted=player.score > 0,
                buff_remaining=player.has_buff(14), errors=errors, respawns=respawns)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sources = ['scripts/audit_magnetic_pickups.py', 'creature.py', 'status_effects.py',
               'pixel_roamer/world_session.py', 'data/catalogs/buffs.json']
    if (ROOT / 'magnetic_pickups.py').exists():
        sources.append('magnetic_pickups.py')
    result = {'code_revision': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'scope': 'explicit Buff14 fixture, existing ten score-pickup kinds just outside body contact; no loose-item/inventory subsystem or original-map-source claim',
        'source_hashes': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
        'runs': [run(fps, tile_id, side, active) for fps in (30, 60, 144)
                 for tile_id in range(310, 320) for side in (-1, 1) for active in (False, True)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'cases': len(result['runs']),
        'active_attracted': sum(r['attracted'] for r in result['runs'] if r['buff_active']),
        'inactive_attracted': sum(r['attracted'] for r in result['runs'] if not r['buff_active'])}))
