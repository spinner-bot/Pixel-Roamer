"""Check both acquisition orders of declared cleanup relations and real wet sources."""
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pygame
from creature import Player
from resource_catalog import load_buffs
from scripts.control_session import create_control_session
from world import World


def api_case(target,counter,counter_first):
    actor=Player(0,'cleanup ordering',0,0,{})
    order=(counter,target) if counter_first else (target,counter)
    for buff_id in order:actor.apply_buff(buff_id,(),5)
    return {'target':target,'counter':counter,'order':list(order),'active':[b.buff_id for b in actor.buffs],
            'relation_satisfied':actor.has_buff(counter) and not actor.has_buff(target)}


def source_case(target,source,fps,counter_first):
    world=World(0,'wet source cleanup',32,32,gravity=-9.8,spawn_points=(10.5,5.9))
    for x in range(32):world.set_tile(x,4,2)
    world.set_tile(10,5,source)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    with patch('pygame.key.get_pressed',return_value=defaultdict(bool)):
        if not counter_first:actor.apply_buff(target,(),5)
        acquisition_frames=math.ceil(fps/120)
        for _ in range(acquisition_frames):session.advance(1/fps)
        if counter_first:actor.apply_buff(target,(),5)
    fire_loss=actor.take_raw_damage(10,damage_type='fire') if target==9 else None
    return {'target_api_injection':target,'actual_counter_source':source,'fps':fps,'counter_first':counter_first,
            'active':[{'id':b.buff_id,'source':b.source,'duration':b.duration} for b in actor.buffs],
            'acquisition_frames':acquisition_frames,'physics_time':session.app._game_timer,'wet_observed':actor.has_buff(15),'target_remains':actor.has_buff(target),
            'post_water_api_fire_loss':fire_loss,'hp':actor.hp,
            'relation_satisfied':actor.has_buff(15) and not actor.has_buff(target)}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    definitions=load_buffs()
    edges=[(b.id,counter) for b in definitions.values() for counter in b.cleanup_by]
    api=[api_case(target,counter,first) for target,counter in edges for first in (False,True)]
    sources=[source_case(target,source,fps,first) for target in (9,16) for source in (7,426)
             for fps in (30,60,144) for first in (False,True)]
    result={'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'scope':'declared cleanup_by edges and actual7/426 source acquisition of15; target9/16 and damage explicitly injected through API, not a normal target source route',
            'edges':edges,'api':api,'sources':sources}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'edges':len(edges),'api_bad':sum(not r['relation_satisfied'] for r in api),'source_rows':len(sources),'source_bad':sum(not r['relation_satisfied'] for r in sources)}))
