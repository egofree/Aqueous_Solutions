"""Envelope set used by AQS-BLD-010 (docs-authority/_ga_check.py), as a function: {unit_id: (level, x, y, dx, dy)}, plus group and z maps."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import study_place as sp
def load():
    seed=json.load(open(sp.SEED)); rep=json.load(open(sp.REP)); st=json.load(open('flow_graph/placement_study.json'))
    BLK={tuple(b['size_mm'][:2]) for b in seed['blocks']}; B={}
    for r in seed['units']+rep.get('moves',[])+rep.get('create_moves',[])+rep.get('apply_moves',[]):
        o,z=r.get('origin_mm'),r.get('size_mm')
        if not(o and z and len(z)>=2) or tuple(z[:2]) in BLK: continue
        B[r['unit_id']]=(r.get('level'),o[0],o[1],z[0],z[1])
    for r in seed['units']:
        o,z=r['origin_mm'],r['size_mm']
        if tuple(z[:2]) not in BLK: B[r['unit_id']]=(r['level'],o[0],o[1],z[0],z[1])
    for r in st['units']:
        o,z=r['origin_mm'],r['size_mm']; B[r['unit_id']]=(r['level']+('T2' if r.get('tier')==2 else ''),o[0],o[1],z[0],z[1])
    G={r['unit_id']:r.get('group') for r in seed['units']}
    Z={r['unit_id']:(r['origin_mm'][2] if len(r['origin_mm'])>2 else 0,(r['size_mm']+[0,0,0])[2]) for r in seed['units']+st['units']}
    return B, G, Z
