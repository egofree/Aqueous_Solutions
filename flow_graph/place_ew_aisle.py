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
out={}; placed=[]
AISLE=914   # NFPA 101 7.3.4.1.1 / IBC 1018.5 minimum clear width between cells (AQS-BLD-012)
NEC=1219     # NEC 2023 Table 110.26(A)(1), 151-600 V, Condition 3, all faces of RECT_EW (face not yet fixed)
def aisle(a,b,g=AISLE): return a[1]<b[1]+b[3]+g and b[1]<a[1]+a[3]+g and a[2]<b[2]+b[4]+g and b[2]<a[2]+a[4]+g
for u,sz in items:
    ok=None
    for y in range(oy,oy+by-sz[1]+1,100):
        for x in range(ox,ox+bx-sz[0]+1,100):
            c=(lv,x,y,sz[0],sz[1])
            if not any(sp.hit(c,p) for p in obst) and not any(aisle(c,p) for p in placed) and not (u=='RECT_EW' and any(aisle(c,p,NEC) for p in obst)): ok=c;break
        if ok:break
    if not ok: sys.exit(f'{u} does not fit LEACH_EW')
    obst.append(ok); placed.append(ok); out[u]=dict(unit_id=u,level=lv,origin_mm=[ok[1],ok[2],z],size_mm=list(sz),
        source=f'X-RSZ-03 sized envelope (AQS-DUTY-051{" cathode count "+str(next(r["cathodes"] for r in ew if r["cell"]==u)) if u!="RECT_EW" else ", study cabinet"}); LEACH_EW block, 600 mm clear to other rows, 914 mm aisle between cells (AQS-BLD-012)')
if '--write' in sys.argv:
    seed['units']=[r for r in seed['units'] if r['unit_id'] not in out]+list(out.values())
    L=[r['size_mm'][0] for r in ew]
    seed['notes_rev_i']=f'2026-10-15, X-RSZ-03, re-run for the X-PAR acid-loop decision (CE 0.85, AQS-PAR-001). EW_1..EW_9 at sized envelopes {min(L)}-{max(L)} mm long (cathode count per AQS-DUTY-051) and RECT_EW placed in LEACH_EW; 600 mm clear, 914 mm access aisle between cells (Rev K, AQS-BLD-012). Supersedes the 750 mm pitch rows.'
    json.dump(seed,open(SEED,'w'),indent=2,ensure_ascii=True)
print(json.dumps(out))
