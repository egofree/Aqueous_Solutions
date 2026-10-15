"""X-RSZ-03. Re-place EW_1..EW_9 and RECT_EW in the LEACH_EW block at the sized
envelopes from docs-authority/_ew_sizing.py (AQS-DUTY-051). Cells in lanes along X,
600 mm clear (maint_clear_mm), launders between neighbours (AQS-MAT-001 §11).
Updates placement_seed.json EW rows and adds RECT_EW; prints the layout."""
import json, subprocess, sys
sys.path.insert(0,'flow_graph'); import study_place as sp
SEED='flow_graph/placement_seed.json'
seed=json.load(open(SEED)); rep=json.load(open(sp.REP))
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['rows']
blk=next(b for b in seed['blocks'] if b['block_id']=='LEACH_EW'); lv=blk['level']; z=seed['datums_mm'][lv]
ox,oy=blk['origin_mm']; bx,by=blk['size_mm'][:2]; own=(ox,oy,bx,by)
B=sp.boxes(seed,rep)
mov=[f'EW_{i}' for i in range(1,10)]+['RECT_EW']
obst=[v for k,v in B.items() if k.split('#')[0] not in mov and v[0]==lv and v[1:]!=own]
items=[(r['cell'],r['size_mm']) for r in ew]+[('RECT_EW',[2400,800,2000])]
items.sort(key=lambda t:-t[1][0]*t[1][1])
out={}
for u,sz in items:
    ok=None
    for y in range(oy,oy+by-sz[1]+1,100):
        for x in range(ox,ox+bx-sz[0]+1,100):
            c=(lv,x,y,sz[0],sz[1])
            if not any(sp.hit(c,p) for p in obst): ok=c;break
        if ok:break
    if not ok: sys.exit(f'{u} does not fit LEACH_EW')
    obst.append(ok); out[u]=dict(unit_id=u,level=lv,origin_mm=[ok[1],ok[2],z],size_mm=list(sz),
        source=f'X-RSZ-03 sized envelope (AQS-DUTY-051{" cathode count "+str(next(r["cathodes"] for r in ew if r["cell"]==u)) if u!="RECT_EW" else ", study cabinet"}); LEACH_EW block, 600 mm clear')
if '--write' in sys.argv:
    seed['units']=[r for r in seed['units'] if r['unit_id'] not in out]+list(out.values())
    seed['notes_rev_i']='2026-10-15, X-RSZ-03. EW_1..EW_9 at sized envelopes 370-2670 mm long (cathode count per AQS-DUTY-051) and RECT_EW placed in LEACH_EW; 600 mm clear. Supersedes the 750 mm pitch rows.'
    seed['revision']='I'
    json.dump(seed,open(SEED,'w'),indent=2,ensure_ascii=True)
print(json.dumps(out))
