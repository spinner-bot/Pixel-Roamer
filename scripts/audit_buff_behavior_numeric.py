"""Compare isolated rule-data stat semantics against the current native API."""
import argparse
from contextlib import nullcontext
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from creature import Player
from scripts.buff_behavior_candidate import load_behaviors
from scripts.contact_exposure_candidate import exposure_candidate


def measure(buff_id,params,count,stat):
    actor=Player(0,'numeric rule contract',0,0,{})
    for _ in range(count):actor.apply_buff(buff_id,params,5)
    buff=next(b for b in actor.buffs if b.buff_id==buff_id)
    before=buff.stacks
    value=actor.get_buff_stat(stat,100)
    return {'buff':buff_id,'params':list(params),'stacks':buff.stacks,'value':value,'stacks_preserved':buff.stacks==before}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rules=load_behaviors()
    rows=[]
    for buff_id,default in ((22,50),(51,40)):
        for params in ((),(0,),(25,),(50,),(100,),(150,)):
            for count in (1,2,3):
                row={'native':measure(buff_id,params,count,'v_max')}
                with exposure_candidate(behaviors=rules):
                    row['candidate']=measure(buff_id,params,count,'v_max')
                value=params[0] if params else default
                row['expected_candidate']=100*max(0,1-value/100)**row['candidate']['stacks']
                rows.append(row)
    controls=[]
    for buff_id,params,count,stat in ((3,(20,),2,'v_max'),(4,(50,),2,'jump_height'),
                                       (6,(30,),2,'stamina_cost'),(13,(50,),1,'gravity')):
        native=measure(buff_id,params,count,stat)
        with exposure_candidate(behaviors=rules):candidate=measure(buff_id,params,count,stat)
        controls.append({'native':native,'candidate':candidate})
    errors=[r for r in rows if not math.isclose(r['candidate']['value'],r['expected_candidate'],abs_tol=1e-10)
            or not r['candidate']['stacks_preserved']]
    errors.extend(r for r in controls if r['native']!=r['candidate'])
    result={'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'scope':'isolated candidate rule metadata and real stat API, explicit Buff injection; not production or map acceptance',
            'pairs':rows,'unchanged_controls':controls,'errors':errors}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'pairs':len(rows),'controls':len(controls),'errors':len(errors)}))
    raise SystemExit(1 if errors else 0)
