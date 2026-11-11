"""Measure original cold sources followed by actual liquid/source contacts."""
import argparse
from collections import defaultdict
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
from scripts.control_session import create_control_session
from world import World


def run(source, liquid, fps, immune=False):
    world = World(0, 'original cold source to liquid', 40, 32, gravity=-9.8,
                  spawn_points=(10.5, 5.9))
    for x in range(40):
        world.set_tile(x, 4, source if x == 10 and source in (373, 395) else 2)
    if source == 410:
        world.set_tile(10, 5, source)
    if liquid:
        for x in range(14, 28):
            for y in range(5, 10):
                world.set_tile(x, y, liquid)
    session = create_control_session(0, world=world)
    actor, keys = session.app.player1, defaultdict(bool)
    if immune:
        actor.apply_buff(40, (), None)
    trace, first_water, frozen_frames = [], None, 0
    freeze_applications = []
    apply_buff = actor.apply_buff

    def observe_apply(buff_id, *args, **kwargs):
        result = apply_buff(buff_id, *args, **kwargs)
        effect = next((b for b in actor.buffs if b.buff_id == buff_id), None)
        if effect and effect.buff_type and effect.buff_type.tick == 'frozen':
            freeze_applications.append({'time': actor._buff_game_time,
                                        'duration': effect.duration, 'source': effect.source})
        return result

    acquisition = None
    was_frozen = False
    with patch('pygame.key.get_pressed', return_value=keys), patch('sfx.play_jump'), \
            patch.object(actor, 'apply_buff', new=observe_apply):
        # Let the original410 entry-root expire while51 keeps refreshing.
        for _ in range(math.ceil(5.2 * fps)):
            session.advance(1 / fps)
        acquisition = [{'id': b.buff_id, 'source': b.source} for b in actor.buffs]
        for frame in range(math.ceil(8 * fps)):
            elapsed = frame / fps
            keys[pygame.K_d] = True
            keys[pygame.K_w] = True
            session.advance(1 / fps)
            frozen = [b for b in actor.buffs if b.buff_type and b.buff_type.tick == 'frozen']
            in_water = actor.can_swim and liquid == 7
            if in_water and first_water is None:
                first_water = elapsed
            frozen_frames += bool(frozen)
            if frame % max(1, fps // 10) == 0 or bool(frozen) != was_frozen:
                trace.append({'time': elapsed, 'position': actor.get_center(),
                              'velocity': [actor.v_x, actor.v_y], 'water': in_water,
                              'cold': actor.has_buff(51), 'root': actor.has_buff(21),
                              'frozen': [{'id': b.buff_id, 'remaining': b.duration,
                                          'initial': b.initial_duration} for b in frozen],
                              'hp': actor.hp, 'stamina': actor.stamina})
            was_frozen = bool(frozen)
    return {'source': source, 'liquid': liquid, 'fps': fps, 'immune_api40': immune,
            'source_acquisition': acquisition, 'first_water': first_water,
            'frozen_frames': frozen_frames, 'freeze_applications': freeze_applications, 'trace': trace}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--immune', action='store_true')
    args = parser.parse_args()
    pygame.init()
    rows = [run(source, 7, fps, args.immune) for source in (2, 373, 395, 410)
            for fps in (30, 60, 144)]
    rows += [run(373, liquid, fps, args.immune) for liquid in (0, 8, 426)
             for fps in (30, 60, 144)]
    pygame.quit()
    report = {'code_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'scope': 'authored fixture with original373/395/410 and liquid7; original410 root allowed to expire; normal D/W WorldSession controls, no51 injection; optional40 explicitly API-only; normal-map reachability not tested',
              'rows': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{'source': r['source'], 'liquid': r['liquid'], 'fps': r['fps'],
                       'water': r['first_water'], 'frozen_frames': r['frozen_frames']}
                      for r in rows]))
