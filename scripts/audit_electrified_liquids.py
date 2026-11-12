"""Observe actual original45 sources entering water and independent fluid controls."""
from collections import defaultdict
import argparse
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
import status_effects
from scripts.control_session import create_control_session
from world import World


def run(source,liquid,fps):
    world=World(0,'original electricity to liquid',36,32,gravity=-9.8,spawn_points=(5.5,5.9))
    for x in range(36):world.set_tile(x,4,source if x==5 and source in (396,412) else 2)
    if source==381:world.set_tile(5,5,source)
    if liquid:
        for x in range(9,26):
            for y in range(5,13):world.set_tile(x,y,liquid)
    session=create_control_session(0,world=world)
    actor,keys=session.app.player1,defaultdict(bool)
    stats=defaultdict(lambda:{'ticks':0,'seconds':0.,'hp_loss':0.,'shield_loss':0.,'swimmable_ticks':0})
    original_tick=status_effects._tick_effect

    def observe_tick(player,buff,dt,context=None):
        hp,shield=player.hp,player.shield
        result=original_tick(player,buff,dt,context)
        if buff.buff_type and buff.buff_type.tick=='electrified':
            contacts=player.contact_pool|({player.stand_pool} if player.stand_pool is not None else set())
            label=str(liquid) if liquid and liquid in contacts else 'source' if source in contacts else 'dry'
            row=stats[label]
            row['ticks']+=1;row['seconds']+=dt
            row['hp_loss']+=hp-player.hp;row['shield_loss']+=shield-player.shield
            row['swimmable_ticks']+=int(player.can_swim)
        return result

    trace,first_target,acquisition=[],None,None
    with patch('pygame.key.get_pressed',return_value=keys),patch('status_effects._tick_effect',new=observe_tick):
        for _ in range(math.ceil(fps/120)):session.advance(1/fps)
        acquisition=[{'id':b.buff_id,'source':b.source,'duration':b.duration} for b in actor.buffs]
        started=session.app._game_timer
        for frame in range(5*fps):
            keys[pygame.K_d]=True
            session.advance(1/fps)
            elapsed=session.app._game_timer-started
            contacts=actor.contact_pool|({actor.stand_pool} if actor.stand_pool is not None else set())
            if liquid and liquid in contacts and first_target is None:first_target=elapsed
            if frame%max(1,fps//10)==0:
                trace.append({'time':elapsed,'position':actor.get_center(),'hp':actor.hp,
                              'can_swim':actor.can_swim,'contacts':sorted(contacts),
                              'electrified':actor.has_buff(45),'wet':actor.has_buff(15)})
            if not actor.alive or first_target is not None and elapsed-first_target>=1-1e-9:
                break
            if not liquid and elapsed>=2:break
    return {'source':source,'liquid':liquid,'fps':fps,'acquisition':acquisition,
            'first_target':first_target,'alive':actor.alive,'hp':actor.hp,
            'electrified_tick_observations':dict(stats),'trace':trace}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    pygame.init()
    rows=[run(source,liquid,fps) for source in (381,396,412) for liquid in (7,8,6,426,0)
          for fps in (30,60,144)]
    pygame.quit()
    report={'code_revision':revision,
            'scope':'authored arena using original381/396/412 and7/8/6/426; actual source45 acquisition and D input, no Buff/position injection; original status tick observed unchanged to attribute45 damage separately from lava/burning; not normal-map reachability or device acceptance',
            'rows':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{'source':r['source'],'liquid':r['liquid'],'fps':r['fps'],
                       'target':r['first_target'],'target_electric_loss':r['electrified_tick_observations'].get(str(r['liquid']),{}).get('hp_loss',0)}
                      for r in rows]))
