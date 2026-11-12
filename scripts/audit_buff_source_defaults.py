"""Controlled contact probes distinguish numeric source placeholders from intentional API zero."""
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
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from creature import Player
from world import World
from resource_catalog import load_blocks

STATS = {5: 'stamina_recovery', 6: 'stamina_cost', 7: 'damage_taken',
         13: 'gravity', 51: 'v_max', 54: 'gravity'}
IDS = (*STATS, 42, 43, 44, 45, 47, 53, 55)


def fixture(tile_id, buff_id, control):
    world = World(0, 'source parameter probe', 30, 20, gravity=0)
    for x in range(3, 20):
        world.set_tile(x, 4, tile_id if x == 5 else 2)
    actor = Player(0, 'source parameter probe', 5.5, 5.9, {})
    actor.collide_with_world(world, 0)
    source = next(b for b in actor.buffs if b.buff_id == buff_id)
    params = source.params
    if control:
        actor.remove_buff(buff_id)
    return actor, world, params


def measure(tile_id, buff_id, control):
    actor, world, params = fixture(tile_id, buff_id, control)
    if buff_id in STATS:
        value = actor.get_buff_stat(STATS[buff_id], 1.)
    elif buff_id in (42, 43):
        # On an intrinsically frictionless source, both damping values may
        # already clamp to one. Retain the acquired Buff on neutral stone.
        actor._x = 10.5
        actor.collide_with_world(world, 0)
        actor.v_x = 1
        actor.collide_with_world(world, 1 / 60)
        value = actor.v_x
    elif buff_id == 53:
        actor.v_x = 2
        actor.update_physics(.5, world)
        value = actor.v_x
    elif buff_id == 44:
        with patch('status_effects.random.random', return_value=1.) as draw:
            actor.tick_buffs(.5)
            early = draw.call_count
            actor.tick_buffs(3.5)
        value = draw.call_count
    elif buff_id == 47:
        value = actor.phys_atk
    else:
        # Leave the source; electric damage uses a real water-contact state.
        actor._x = 10.5
        if buff_id == 45:
            world.set_tile(10, 5, 7)
        actor.collide_with_world(world, 0)
        hp = actor.hp
        actor.tick_buffs(.5)
        value = hp - actor.hp
    result = {'value': value, 'params': params}
    if buff_id == 44:
        result['opportunities_first_half_second'] = early
    return result


def run():
    rows = []
    for tile_id, block in load_blocks().items():
        for buff_id in block.buff_ids:
            if buff_id not in IDS:
                continue
            active = measure(tile_id, buff_id, False)
            control = measure(tile_id, buff_id, True)
            rows.append({'tile_id': tile_id, 'buff_id': buff_id,
                         'active': active, 'control': control,
                         'different': abs(active['value'] - control['value']) > 1e-10})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'isolated low-level real contact and consumer probes; explicit coordinates and input values; not original-map normal routes or full buff acceptance',
              'rows': run()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'rows': len(result['rows']), 'different': sum(r['different'] for r in result['rows'])}))
