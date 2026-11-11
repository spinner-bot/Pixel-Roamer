"""Boundary research for continuous kind exposure; explicit placements are labeled."""
import argparse
from collections import defaultdict
from contextlib import nullcontext
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
from scripts.contact_exposure_candidate import exposure_candidate
from scripts.control_session import create_control_session
from world import World


def strip(fps,direction,loop):
    world=World(0,'continuous cold strip',12 if loop else 60,32,gravity=-9.8,
                spawn_points=(5.5 if direction>0 else 6.5,5.9),loop_x=loop)
    for x in range(world.width):
        world.set_tile(x,4,373)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    keys=defaultdict(bool)
    keys[pygame.K_d if direction>0 else pygame.K_a]=True
    wraps=0
    max_stacks=0
    distance=0.
    with patch('pygame.key.get_pressed',return_value=keys):
        for _ in range(4*fps):
            before=actor._x
            session.advance(1/fps)
            dx=actor._x-before
            if loop and abs(dx)>world.width/2:
                wraps+=1
                dx=(dx+world.width/2)%world.width-world.width/2
            distance+=direction*dx
            max_stacks=max(max_stacks,max((b.stacks for b in actor.buffs if b.buff_id==51),default=0))
    return {'fps':fps,'direction':direction,'loop':loop,'distance':distance,'wraps':wraps,
            'max_cold_stacks':max_stacks,'v_max':actor.v_max,'position':actor.get_center()}


def placements():
    world=World(0,'explicit contact memory placements',30,32,gravity=-9.8,spawn_points=(5.5,5.9))
    for x in range(30):world.set_tile(x,4,2)
    world.set_tile(5,4,373)
    world.set_tile(6,4,373)
    world.set_tile(8,4,395)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    rows=[]
    def snapshot(label):
        rows.append({'label':label,'stacks':next((b.stacks for b in actor.buffs if b.buff_id==51),0),
                     'duration':next((b.duration for b in actor.buffs if b.buff_id==51),None)})
    def at(x):
        actor._x=x
        actor.collide_with_world(world,0)
    at(5.5);snapshot('first')
    for _ in range(100):at(5.5)
    snapshot('100_continuous_refreshes')
    at(6.5);snapshot('adjacent_same_kind')
    at(8.5);snapshot('different_source_kind')
    at(15.5);at(5.5);snapshot('leave_all_and_reenter')
    actor.clear_buffs();at(5.5);snapshot('clear_while_touching')
    actor.apply_buff(51,(),6);snapshot('explicit_api_while_touching')
    at(5.5);snapshot('continuous_after_explicit_api')
    actor.clear_buffs()
    actor.apply_buff(51,(),6);actor.apply_buff(51,(),6);snapshot('explicit_api_twice')
    actor.clear_buffs()
    other=world.create_session()
    actor.collide_with_world(other,0);snapshot('new_world_first_contact')
    actor.reset(5.5,5.9)
    actor.clear_buffs()
    actor.collide_with_world(world,0);snapshot('reset_then_contact')
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--exposure-candidate',action='store_true')
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    with exposure_candidate() if args.exposure_candidate else nullcontext():
        strips=[strip(fps,direction,loop) for fps in (30,60,144) for direction in (-1,1) for loop in (False,True)]
        cases=placements()
    report={'code_revision':revision,'exposure_candidate':args.exposure_candidate,
        'scope':'strip rows are real WorldSession held input; placements rows deliberately move coordinates in an API fixture to isolate contact memory, not normal gameplay or map acceptance',
        'strips':strips,'placements':cases}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'strips':strips,'placements':cases}))
