"""X-BLD-04 L1 farm re-row (AQS-BLD-012). Re-packs every L1 row east of the HAB rows so that every path between farm rows is at least
914 mm (NFPA 101 (2027) 7.3.4.1.1 / IBC 2027 1018.5 minimum clear width), and 600 mm (maint_clear_mm) to HAB rows. Envelope sizes are
issued sizes and are not changed (rotation by 90 deg allowed). Bottom-left greedy on a 100 mm grid, largest first, inside the plate
(y 0..18000, x up to 24000); the FARM/HAB boundary moves west only as far as needed (owner standing rule, A-M-102).
--write updates placement_seed.json / placement_study.json; block rows are not resized."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ga_envelopes as ge
AISLE, CLR, X1, Y0, Y1 = 914, 600, 24000, 0, 18000
B, G, Z = ge.load()
FARM = sorted([k for k, v in B.items() if v[0] == 'L1' and v[1] + v[3] > 11500 and min(v[3:]) > 100], key=lambda k: -B[k][3]*B[k][4])
HAB = [(v[1], v[2], v[1]+v[3], v[2]+v[4]) for k, v in B.items() if v[0] == 'L1' and k not in FARM and min(v[3:]) > 100]
import random
def near(a, b, g): return a[0] < b[2]+g and b[0] < a[2]+g and a[1] < b[3]+g and b[1] < a[3]+g
def pack(x0, order, ymode):
    out = {}
    for k in order:
        w, d = B[k][3], B[k][4]; cands = []
        for (ww, dd) in ([(w, d), (d, w)] if w != d else [(w, d)]):
            xs = range(x0, X1-ww+1, 100); ys = range(Y0, Y1-dd+1, 100)
            for x, y in (((x, y) for y in ys for x in xs) if ymode else ((x, y) for x in xs for y in ys)):
                c = (x, y, x+ww, y+dd)
                if not any(near(c, o, AISLE) for o in out.values()): cands.append(c); break
        if not cands: return None
        out[k] = min(cands, key=lambda c: (c[1], c[0]) if ymode else (c[0], c[1]))
    return out
def search(x0, tries=80):
    random.seed(1); base = FARM[:]
    for i in range(tries):
        o = base if i == 0 else base[:1] + random.sample(base[1:], len(base)-1)
        for ym in (0, 1):
            r = pack(x0, o, ym)
            if r: return r
for x0 in range(12000, 6000, -200):
    L = search(x0)
    if L: break
else: sys.exit('farm does not fit')
# HAB rows now inside the farm zone (or within 600 mm of it) are relocated to the nearest free HAB spot with 600 mm clearance
HABK = {k: v for k, v in B.items() if v[0] == 'L1' and k not in FARM and min(v[3:]) > 100}
xb_ = min(c[0] for c in L.values()); MOVE = {}
for k, v in HABK.items():
    b = (v[1], v[2], v[1]+v[3], v[2]+v[4])
    if b[2] + CLR <= xb_: continue
    fixed = [(u[1], u[2], u[1]+u[3], u[2]+u[4]) for kk, u in HABK.items() if kk != k and kk not in MOVE] + list(MOVE.values()) + list(L.values())
    best = None
    for x in range(0, xb_-CLR-v[3]+1, 100):
        for y in range(Y0, Y1-v[4]+1, 100):
            c = (x, y, x+v[3], y+v[4]); dist = abs(x-v[1]) + abs(y-v[2])
            if (best is None or dist < best[0]) and not any(near(c, f, CLR) for f in fixed): best = (dist, c)
    if not best: sys.exit(f'{k} has no HAB spot')
    MOVE[k] = best[1]
L.update(MOVE)
xb = xb_
for k, c in L.items(): print(k, B[k][1:3], '->', c[:2], 'rot' if (c[2]-c[0]) != B[k][3] else '')
print('farm west edge', xb)
if '--write' in sys.argv:
    note = f' Rev K farm re-row (flow_graph/farm_rerow.py): 914 mm paths between farm rows; FARM block west edge x={xb} (AQS-BLD-012, A-M-102).'
    for f in ['flow_graph/placement_seed.json', 'flow_graph/placement_study.json']:
        s = json.load(open(f))
        for r in s['units']:
            if r['unit_id'] in L:
                c = L[r['unit_id']]; z = r['size_mm']
                if (c[2]-c[0]) != z[0]: r['size_mm'] = [z[1], z[0]] + z[2:]
                r['origin_mm'] = [c[0], c[1]] + r['origin_mm'][2:]
                key = 'source' if 'source' in r else 'note'; r[key] = str(r.get(key, '')) + note
        if 'blocks' in s:   # block rows keep their AQS-BLD-001 size (placeholders are matched by it); the boundary shift is recorded as a note
            s['notes_rev_k_farm'] = f'2026-10-15, X-BLD-04 farm re-row: farm rows occupy x {xb}..24000 on L1, west of the AQS-BLD-001 FARM/HAB line at x=12000; HAB rows displaced: {sorted(MOVE)}. 914 mm between farm rows (A-M-102).'
        json.dump(s, open(f, 'w'), indent=2, ensure_ascii=True)
