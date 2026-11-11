"""Actual source contacts and ordinary escape inputs; no injected root effect."""
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
from scripts.control_session import create_control_session
from teleport import can_place
from world import World


def measure(source,fps,gravity,jump,immune):
    world=World(0,'root source escape',40,80,gravity=gravity,spawn_points=(10.5,5.9))
    world.lives=5
    for x in range(40):
        world.set_tile(x,4,2)
    world.set_tile(10,4 if world.block_types[source].is_solid else 5,source)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    actor.f_y=.9965
    if immune:
        actor.apply_buff(40,(),60)
    keys=defaultdict(bool)
    seen=False
    min_remaining=None
    max_x=actor._x
    jumps=0
    errors=[]
    trace=[]
    with patch('pygame.key.get_pressed',return_value=keys),patch('sfx.play_jump'):
        # Acquire the original block's effects at rest before attempting exit.
        session.advance(1/120)
        contact_buffs=[{'id':b.buff_id,'source':b.source,'duration':b.duration} for b in actor.buffs]
        for frame in range(20*fps):
            keys[pygame.K_d]=True
            events=[]
            if jump and actor.on_ground:
                events.append(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
                jumps+=1
            with patch('pygame.event.get',return_value=events):
                session.app._handle_events()
            session.advance(1/fps)
            root=next((b for b in actor.buffs if b.buff_id==21),None)
            seen|=root is not None
            if root is not None:
                min_remaining=root.duration if min_remaining is None else min(min_remaining,root.duration)
            max_x=max(max_x,actor._x)
            if not can_place(actor,world,*actor.get_center()) or session.app._player_lives_left!=5:
                errors.append({'position':actor.get_center(),'lives':session.app._player_lives_left})
                break
            if frame%fps==0:
                trace.append({'seconds':frame/fps,'position':actor.get_center(),'root_remaining':root.duration if root else None,'stamina':actor.stamina})
            if actor._x>=14.5 and not actor.has_buff(21):
                break
    return {'source':source,'fps':fps,'gravity':gravity,'jump_input':jump,'immune_api_injection':immune,
            'contact_buffs':contact_buffs,'root_seen':seen,'escaped':actor._x>=14.5 and not actor.has_buff(21),
            'seconds':session.app._game_timer,'max_x':max_x,'position':actor.get_center(),'jumps':jumps,
            'min_root_remaining':min_remaining,'hp':actor.hp,'errors':errors,'trace':trace}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rows=[measure(source,fps,gravity,jump,immune) for source in (370,410,429) for fps in (30,60,144)
          for gravity in (-6.5,-9.8) for jump in (False,True) for immune in (False,True)]
    result={'code_revision':revision,'scope':'actual source contact at rest, original Buff links, production WorldSession D / D+Space; API40 control explicitly labeled; finite fixture horizon, not all escape abilities or original-map acceptance','runs':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'ordinary_escaped':sum(r['escaped'] for r in rows if not r['immune_api_injection']),
                      'ordinary_rows':sum(not r['immune_api_injection'] for r in rows),'immune_escaped':sum(r['escaped'] for r in rows if r['immune_api_injection']),
                      'errors':sum(bool(r['errors']) for r in rows)}))
    raise SystemExit(1 if any(r['errors'] for r in rows) else 0)
