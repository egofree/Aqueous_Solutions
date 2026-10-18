"""X-BLD-04. Clears pairs inside maint_clear_mm (600 mm) found by docs-authority/_ga_check.py by moving
seed rows the smallest distance on a 100 mm grid (search radius 4 m) so that no box on the level is hit,
the row stays inside its seed block (else the level's current envelope extent), and no row crosses a
partition line X=<mm> named in any source on that level. Writes placement_seed.json with --write; prints the moves."""
import json, re, subprocess, sys
sys.path.insert(0,'flow_graph'); import study_place as sp
SEED=sp.SEED; seed=json.load(open(SEED))
def ga():
    out=subprocess.run([sys.executable,'docs-authority/_ga_check.py'],capture_output=True,text=True,check=True).stdout.splitlines()
    return eval(out[2])
exec(open('docs-authority/_ga_check.py').read().split('def thin')[0].replace("open('docs-authority/GA_CHECK.md','w')","open('/dev/null','w')"))
U={r['unit_id']:r for r in seed['units']}
def ok(u,c):
    for k,q in B.items():
        if k==u or q[0]!=c[0]: continue
        if G.get(u)==k or G.get(k)==u or (G.get(u) and G.get(u)==G.get(k)): continue
        za,zb=Z.get(u,(0,0)),Z.get(k,(0,0))
        if za[1] and zb[1] and not(za[0]<zb[0]+zb[1] and zb[0]<za[0]+za[1]): continue
        if min(q[3],q[4])<=100: 
            if c[1]<q[1]+q[3] and q[1]<c[1]+c[3] and c[2]<q[2]+q[4] and q[2]<c[2]+c[4]: return False
            continue
        if sp.hit(c,q): return False
    return True
moves=[]; pairs=ga()
for a,b in pairs:
    if not sp.hit(B[a],B[b]): continue
    for u in sorted((a,b), key=lambda x: B[x][3]*B[x][4]):
        if u not in U: continue
        p=B[u]; lv=[q for q in B.values() if q[0]==p[0]]
        x0=min(q[1] for q in lv); y0=min(q[2] for q in lv); x1=max(q[1]+q[3] for q in lv); y1=max(q[2]+q[4] for q in lv)
        part=sorted({int(v) for r in seed['units'] if r.get('level')==p[0] for v in re.findall(r'X=(-?\d+)', str(r.get('source_doc',''))+str(r.get('source','')))})
        blk=[(b['origin_mm'][0],b['origin_mm'][1],b['origin_mm'][0]+b['size_mm'][0],b['origin_mm'][1]+b['size_mm'][1]) for b in seed['blocks'] if b['level']==p[0]
             and b['origin_mm'][0]<=p[1] and b['origin_mm'][1]<=p[2] and p[1]+p[3]<=b['origin_mm'][0]+b['size_mm'][0] and p[2]+p[4]<=b['origin_mm'][1]+b['size_mm'][1]]
        if blk: x0,y0,x1,y1=blk[0]
        cands=sorted(((dx,dy) for dx in range(-4000,4001,100) for dy in range(-4000,4001,100)), key=lambda t: abs(t[0])+abs(t[1]))
        for dx,dy in cands:
            c=(p[0],p[1]+dx,p[2]+dy,p[3],p[4])
            if c[1]<x0 or c[2]<y0 or c[1]+c[3]>x1 or c[2]+c[4]>y1: continue
            if any((p[1]<X)!=(c[1]<X) or (p[1]+p[3]>X)!=(c[1]+c[3]>X) for X in part): continue
            if ok(u,c):
                B[u]=c; moves.append((u,p[1:3],c[1:3])); break
        else: continue
        break
for u,o,n in moves:
    print(u,o,'->',n)
if '--write' in sys.argv:
    for u,o,n in moves:
        r=U[u]; r['origin_mm'][0],r['origin_mm'][1]=n
        r['source_doc']=str(r.get('source_doc') or '')+f' X-BLD-04: moved from ({o[0]}, {o[1]}) to ({n[0]}, {n[1]}) for the 600 mm maintenance clearance (flow_graph/clear_pairs.py).'
    seed['notes_rev_j']=f'2026-10-15, X-BLD-04. {len(moves)} rows moved the smallest distance to clear maint_clear_mm 600 (flow_graph/clear_pairs.py); partition sides kept.'
    seed['revision']='J'; json.dump(seed,open(SEED,'w'),indent=2,ensure_ascii=True)
