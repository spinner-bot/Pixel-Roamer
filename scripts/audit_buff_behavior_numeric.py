"""Check rule-data stat semantics, with explicit production and isolated research modes."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from creature import Player


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
    parser.add_argument('--production',action='store_true')
    args=parser.parse_args()
    if not args.production:
        from scripts.buff_behavior_candidate import load_behaviors
        from scripts.contact_exposure_candidate import exposure_candidate
        rules=load_behaviors()
    rows=[]
    for buff_id,default in ((22,50),(51,40)):
        for params in ((),(0,),(25,),(50,),(100,),(150,)):
            for count in (1,2,3):
                observed=measure(buff_id,params,count,'v_max')
                row={'production':observed} if args.production else {'native':observed}
                if not args.production:
                    with exposure_candidate(behaviors=rules):
                        row['candidate']=measure(buff_id,params,count,'v_max')
                value=params[0] if params else default
                checked=row['production'] if args.production else row['candidate']
                row['expected']=100*max(0,1-value/100)**checked['stacks']
                rows.append(row)
    controls=[]
    for buff_id,params,count,stat,sign in ((3,(20,),2,'v_max',1),(4,(50,),2,'jump_height',1),
                                          (6,(30,),2,'stamina_cost',-1),(13,(50,),1,'gravity',-1)):
        observed=measure(buff_id,params,count,stat)
        row={'production':observed} if args.production else {'native':observed}
        if not args.production:
            with exposure_candidate(behaviors=rules):row['candidate']=measure(buff_id,params,count,stat)
        row['expected']=100*(1+sign*params[0]*observed['stacks']/100)
        controls.append(row)
    checked_key='production' if args.production else 'candidate'
    errors=[r for r in rows+controls if not math.isclose(r[checked_key]['value'],r['expected'],abs_tol=1e-10)
            or not r[checked_key]['stacks_preserved']]
    result={'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'production':args.production,
            'scope':('actual unmodified production stat API and startup rule data; explicit Buff injection, not normal map acceptance' if args.production else 'isolated candidate rules and stat API, explicit Buff injection; not production or map acceptance'),
            'pairs':rows,'unchanged_controls':controls,'errors':errors}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'production':args.production,'pairs':len(rows),'controls':len(controls),'errors':len(errors)}))
    raise SystemExit(1 if errors else 0)
