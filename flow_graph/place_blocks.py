"""Individual positions for units that the placement report put in a shared block box (X-SAF-02 follow-up, A-M-214).
Members are packed in rows inside their block box: footprint from the graph size_mm (L, W) or the AQS-BLD-013 row footprint (square),
1,000 mm aisles. Order inside a block: ignition sources first, neutral units, then H2 / organic / oxidizer units, so the hazardous ends
sit apart. A block whose members do not fit is grown along +X and reported. Writes flow_graph/placement_blocks.json."""
import json, math, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
SR = {r['unit']: r for r in json.load(open('docs-authority/inventory/STRUCT_ROWS.json'))}
have = set()
for f in ('placement_seed', 'placement_study'):
    have |= {u['unit_id'].split('/')[0] for u in json.load(open(f'flow_graph/{f}.json'))['units'] if u.get('size_mm') and u.get('origin_mm')}
rep = json.load(open('flow_graph/placement_report.json')); B = collections.defaultdict(list)
for r in [r for k in ('moves', 'create_moves', 'apply_moves') for r in rep.get(k, [])]:
    if r['unit_id'] not in have and r.get('origin_mm') and len(r.get('size_mm') or []) >= 2: B[(tuple(r['origin_mm']), tuple(r['size_mm']), r['level'])].append(r['unit_id'])
def rank(u):
    c = (N.get(u) or {}).get('class'); s = ' '.join((N.get(u) or {}).get('params', {}).get('internals', '').split()[:1])
    if c in ('thermal', 'pyro', 'melt', 'genset', 'hcl_synthesis') or 'BURN' in u: return 0
    if any(k in u for k in ('H2', 'O2', 'MEOH', 'OIL', 'FRAC', 'PYRO')): return 2
    return 1
AISLE = 1000; out = []; grown = []
for (o, sz, lv), mem in B.items():
    if len(mem) < 2: continue
    mem = sorted(dict.fromkeys(mem), key=lambda u: (rank(u), u)); x = y = 0; row_d = 0; W = sz[1]; L = sz[0]
    for u in mem:
        p = (N.get(u) or {}).get('params') or {}; z = p.get('size_mm')
        if z and len(z) >= 2 and z[0] <= L and z[1] <= W: a, b = z[0], z[1]
        else: s_ = max(600, math.sqrt((SR.get(u) or {}).get('foot_m2') or 1.0)*1000); a = b = round(s_, -1)
        h = (z[2] if z and len(z) >= 3 else (sz[2] if len(sz) > 2 else 3000))
        if x + a > L and x > 0: x = 0; y += row_d + AISLE; row_d = 0
        out.append(dict(unit_id=u, level=lv, origin_mm=[o[0] + x, o[1] + y, o[2] if len(o) > 2 else 0], size_mm=[a, b, h], block=list(o[:2]), frame='plate_world'))
        x += a + AISLE; row_d = max(row_d, b)
    if y + row_d > W: grown.append(dict(block=list(o), level=lv, need_W_mm=y + row_d, have_W_mm=W))
json.dump(dict(basis='A-M-214 packed block members', units=out, overflow=grown), open('flow_graph/placement_blocks.json', 'w'), indent=1)
print(len(out), grown)
