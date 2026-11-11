"""Observe first contact and continued refresh for every stackable authored source."""
import argparse
from collections import defaultdict
import json
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
from resource_catalog import load_blocks,load_buffs
from scripts.control_session import create_control_session
from world import World


def measure(source,fps):
    world=World(0,'source stack exposure',40,80,gravity=-9.8,spawn_points=(10.5,5.9))
    for x in range(40):
        world.set_tile(x,4,2)
    world.set_tile(10,4 if world.block_types[source].is_solid else 5,source)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    original=session._advance_step
    steps=0
    samples=[]
    def observe(dt,keys):
        nonlocal steps
        original(dt,keys)
        steps+=1
        if steps in (1,2,3,12,60):
            samples.append({'step':steps,'source_contact':source in actor.contact_pool or actor.stand_pool==source,
                'position':actor.get_center(),'v_max':actor.v_max,'v_jump':actor.v_jump,
                'buffs':[{'id':b.buff_id,'source':b.source,'params':list(b.params),'stacks':b.stacks,'duration':b.duration} for b in actor.buffs]})
    with patch('pygame.key.get_pressed',return_value=defaultdict(bool)),patch.object(session,'_advance_step',side_effect=observe):
        for _ in range(fps//2):
            session.advance(1/fps)
    return {'source':source,'fps':fps,'samples':samples}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    blocks,buffs=load_blocks(),load_buffs()
    sources=[b.id for b in blocks.values() if any(buffs[i].max_stacks>1 for i in b.buff_ids)]
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rows=[measure(source,fps) for source in sources for fps in (30,60,144)]
    inflated=[{'source':r['source'],'fps':r['fps'],'step':s['step'],'buff':b['id'],'stacks':b['stacks']}
              for r in rows for s in r['samples'] for b in s['buffs'] if b['source']==r['source'] and b['stacks']>1]
    report={'code_revision':revision,'scope':'actual source contact without Buff injection or input; source may legitimately launch/clear/conflict, samples record actual contact; stack observations alone are not whole-effect acceptance','source_count':len(sources),'runs':rows,'multiple_stack_samples':inflated}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sources':len(sources),'runs':len(rows),'multiple_stack_samples':len(inflated),'affected_sources':len({r['source'] for r in inflated})}))
