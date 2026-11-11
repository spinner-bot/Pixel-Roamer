"""Render actual original-spawn source contact frames without moving the player."""
import argparse
from functools import partial
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.audit_grand_routes import run
from scripts.audit_grand_polarity_gallery import continue_from_hall
from pixel_roamer.application import GameApp
import pygame


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    frames=[]
    seen=set()
    def capture(app,phase):
        if phase not in ('observe','positive_observe','expire') or phase in seen:
            return
        seen.add(phase)
        app.world_view.draw(0)
        path=args.output.with_name('A85_gallery_'+phase+'.png')
        pygame.image.save(app.logic_surface,str(path))
        frames.append({'phase':phase,'position':app.player1.get_center(),'time':app._game_timer,
                       'buffs':[{'id':b.buff_id,'params':list(b.params),'source':b.source} for b in app.player1.buffs],
                       'image':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)})
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=run(60,upper=True,app_factory=GameApp,hall_hook=partial(continue_from_hall,frame_hook=capture))
    pygame.quit()
    report={'code_revision':revision,'scope':'actual full GameApp, original spawn input route and production WorldView under SDL dummy; no Buff or position injection, not physical desktop acceptance','frames':frames,'result':result}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'frames':frames,'errors':result['hall_extension']['errors']},ensure_ascii=False))
    raise SystemExit(0 if len(frames)==3 and not result['hall_extension']['errors'] else 1)
