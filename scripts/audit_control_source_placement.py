"""Read real trap/cold/jump placement geometry; never claim route reachability."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from maps import get_map


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    wanted={370,373,395,410,429,415,418}
    rows=[]
    for map_id in (20,21):
        world=get_map(map_id)
        for (x,y),tile in sorted(world.grid.items()):
            if tile.type_id not in wanted:
                continue
            kind=world.block_types[tile.type_id]
            below=world.get_block_type(x,y-1)
            rows.append({'map':map_id,'source':tile.type_id,'name':kind.name2,'position':[x,y],
                         'source_solid':kind.is_solid,'below_id':below.id,'below_solid':below.is_solid,
                         'buffs':[{'id':bid,'params':list(kind.buff_params_list[i]) if i<len(kind.buff_params_list) else [],'duration':kind.buff_durations[i] if i<len(kind.buff_durations) else None} for i,bid in enumerate(kind.buff_ids)],
                         'neighbors':[[world.get_tile(x+dx,y+dy).type_id for dx in range(-1,2)] for dy in range(2,-2,-1)]})
    report={'code_revision':revision,'scope':'original map20/21 generated-world geometry and links; no controls, no gameplay or reachability acceptance','sources':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('map','source','position','source_solid','below_solid')} for r in rows],ensure_ascii=False))
