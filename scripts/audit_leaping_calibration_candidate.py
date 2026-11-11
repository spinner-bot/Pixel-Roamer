"""Actual-session paired research of height claims; candidate stays out of production."""
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
from scripts.control_session import create_control_session
from scripts.leaping_calibration_candidate import apex, launch_speed
from world import World


def measure(fps,gravity,damping,parameter,feather,candidate):
    world=World(0,'height candidate fixture',30,2048,gravity=gravity,spawn_points=(10.5,5.9))
    world.player_config={'f_y':damping}
    for x in range(30):
        world.set_tile(x,4,2)
    session=create_control_session(0,world=world)
    actor=session.app.player1
    original_refresh=actor.refresh_movement_stats
    if candidate:
        def refresh():
            original_refresh()
            multiplier=1.
            for buff in actor.buffs:
                if buff.buff_id==4:
                    value=buff.params[0] if buff.params else 50
                    multiplier*=max(0.,1+value*buff.stacks/100)
            base=actor._base_v_jump*getattr(actor,'_environment_jump_mult',1.)
            actor.v_jump=launch_speed(base,world.gravity*actor.get_buff_stat('gravity',1.),actor.f_y,multiplier)
        actor.refresh_movement_stats=refresh
    peak=actor._y
    airborne=False
    original_step=session._advance_step
    def observe(dt,keys):
        nonlocal peak,airborne
        original_step(dt,keys)
        peak=max(peak,actor._y)
        airborne|=actor._y>5.9+1e-8
    with patch('pygame.key.get_pressed',return_value=defaultdict(bool)),patch('sfx.play_jump'):
        session.advance(1/120)
        if feather:
            actor.apply_buff(13,(50,),None)
        if parameter is not None:
            actor.apply_buff(4,(parameter,),None)
        actor.refresh_movement_stats()
        initial_speed=actor.v_jump
        events=[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]
        with patch('pygame.event.get',return_value=events):
            session.app._handle_events()
        with patch.object(session,'_advance_step',side_effect=observe),patch.object(actor,'reset',wraps=actor.reset) as reset:
            time_budget=max(12,math.ceil(2*initial_speed/abs(gravity*(.5 if feather else 1))+10))
            for frame in range(time_budget*fps):
                session.advance(1/fps)
                if actor.on_ground and (airborne or initial_speed==0) and session.app._game_timer>.1:
                    break
            respawns=reset.call_count
    return {'fps':fps,'gravity':gravity,'damping':damping,'parameter':parameter,'feather':feather,'candidate':candidate,
            'height':peak-5.9,'launch_speed':initial_speed,'landed':actor.on_ground,'hp':actor.hp,
            'respawns':respawns,'seconds':session.app._game_timer,'time_budget':time_budget,'buff_duration':None,
            'model_height':apex(initial_speed,gravity*(.5 if feather else 1),damping)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--quick',action='store_true')
    parser.add_argument('--retry-incomplete',type=Path)
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rows=[]
    errors=[]
    if args.retry_incomplete:
        parent=json.loads(args.retry_incomplete.read_text())
        for old in parent['runs']:
            if old['landed']:
                continue
            row=measure(old['fps'],old['gravity'],old['damping'],old['parameter'],old['feather'],old['candidate'])
            row['baseline_height']=old['baseline_height']
            row['height_ratio']=row['height']/row['baseline_height']
            row['expected_ratio']=old['expected_ratio']
            row['ratio_error']=row['height_ratio']-row['expected_ratio']
            rows.append(row)
            if not row['landed'] or row['respawns'] or row['hp']!=150 or (row['candidate'] and abs(row['ratio_error'])>1e-8):
                errors.append(row)
        report={'code_revision':revision,'scope':'rerun only incomplete trajectories with calculated observation budget and permanent explicit API Buffs; no production change','parent_report':str(args.retry_incomplete),'parent_completed_rows':sum(r['landed'] for r in parent['runs']),'rerun_rows':rows,'errors':errors}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'parent_completed_rows':report['parent_completed_rows'],'rerun_rows':len(rows),'errors':len(errors),'max_candidate_ratio_error':max(abs(r['ratio_error']) for r in rows if r['candidate'])}))
        return 1 if errors else 0
    gravities=(-6.5,-9.8) if args.quick else (-.7,-6.5,-9.8,-20.)
    for fps in ((60,) if args.quick else (30,60,144)):
        for gravity in gravities:
            for damping in (.98,.9965,1.):
                for feather in (False,True):
                    baseline=measure(fps,gravity,damping,None,feather,False)
                    for parameter in (-100,-50,0,25,50,100):
                        for candidate in (False,True):
                            row=measure(fps,gravity,damping,parameter,feather,candidate)
                            row['baseline_height']=baseline['height']
                            row['height_ratio']=row['height']/baseline['height']
                            row['expected_ratio']=max(0,1+parameter/100)
                            row['ratio_error']=row['height_ratio']-row['expected_ratio']
                            rows.append(row)
                            if candidate and (abs(row['ratio_error'])>1e-8 or not row['landed'] or row['respawns'] or row['hp']!=150):
                                errors.append(row)
    report={'code_revision':revision,'scope':'research only; original production path versus temporary per-instance candidate movement refresh; actual fixed-step WorldSession with explicit parameter injection; no production import or original-map acceptance','runs':rows,'errors':errors}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'candidate_errors':len(errors),'native_max_ratio_error':max(abs(r['ratio_error']) for r in rows if not r['candidate']),'candidate_max_ratio_error':max(abs(r['ratio_error']) for r in rows if r['candidate'])}))
    return 1 if errors else 0


if __name__=='__main__':
    raise SystemExit(main())
