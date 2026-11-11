"""Observe real wind-walk source acceleration, ordinary reversal and release."""
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
from scripts.control_session import create_control_session
from world import World


def measure(fps,direction,continuous,with_buff,release):
    world=World(0,'wind walk response',2000,32,gravity=-9.8,spawn_points=(1000.5,5.9))
    for x in range(2000):world.set_tile(x,4,2)
    if with_buff:
        if continuous:
            for x in range(2000):world.set_tile(x,5,394)
        else:world.set_tile(1000,5,394)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    keys=defaultdict(bool)
    charge=16 if continuous else 10
    reverse_at=None
    active_response_frames=0
    active_opposite_frames=0
    trace=[]
    start_x=None
    with patch('pygame.key.get_pressed',return_value=keys):
        session.advance(1/120)
        for frame in range((charge+4)*fps):
            responding=frame>=charge*fps
            desired=(-direction if responding else direction)
            keys[pygame.K_d]=desired>0 and not (responding and release)
            keys[pygame.K_a]=desired<0 and not (responding and release)
            if frame==charge*fps:
                start_x=actor._x
                start_velocity=actor.v_x
            session.advance(1/fps)
            if responding:
                if reverse_at is None and actor.v_x*direction < -.1:
                    reverse_at=(frame-charge*fps+1)/fps
                if actor.has_buff(53):
                    active_response_frames+=1
                    active_opposite_frames+=actor.v_x*direction>0
            if frame%fps==0:
                trace.append({'seconds':frame/fps,'position':actor.get_center(),'velocity':actor.v_x,
                              'acceleration':actor.a_x,'wind_time':getattr(actor,'_wind_walk_timer',0),
                              'buff53':next(({'stacks':b.stacks,'remaining':b.duration,'source':b.source} for b in actor.buffs if b.buff_id==53),None)})
    return {'fps':fps,'direction':direction,'continuous_source':continuous,'with_source':with_buff,
            'response':'release' if release else 'reverse','charge_seconds':charge,'start_velocity':start_velocity,
            'seconds_to_reverse':reverse_at,'active_response_frames':active_response_frames,
            'active_still_forward_frames':active_opposite_frames,'response_forward_distance':direction*(actor._x-start_x),
            'final_velocity':actor.v_x,'hp':actor.hp,'trace':trace}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--direction-candidate',action='store_true')
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    from scripts.wind_walk_candidate import directional_candidate
    with directional_candidate() if args.direction_candidate else nullcontext():
        rows=[measure(fps,direction,continuous,with_buff,release) for fps in (30,60,144) for direction in (-1,1)
              for continuous in (False,True) for with_buff in (False,True) for release in (False,True)]
    report={'direction_candidate':args.direction_candidate,'code_revision':revision,'scope':'actual394 source contact or explicit no-source control, native WorldSession held input, no Buff injection; not normal-map acceptance','runs':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'source_reverse_cases':sum(r['with_source'] and r['response']=='reverse' for r in rows),'source_no_reverse_in_four_seconds':sum(r['with_source'] and r['response']=='reverse' and r['seconds_to_reverse'] is None for r in rows)}))
