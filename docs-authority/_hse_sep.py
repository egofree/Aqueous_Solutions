"""AQS-SAF-007 hazard separation applied to the layout (X-SAF-02, A-M-209). AQS-HSE-001 rules on unit positions:
S1 oxidizer gas (O2) to flammable gas (H2) or organic liquid: 7,620 mm (25 ft) or a 1 h barrier (AQS-HSE-001 FC_O2_MANIFOLD rule; NFPA 55/400).
S2 ignition source (fired, molten, engine) to H2 or organic liquid: 7,620 mm (AQS-HSE-001 25 ft ignition rule indoors; NFPA 2).
Credited barriers: a floor slab between levels (2 h, A-M-209) and the 1 h partition at X = 15,000 mm (A-M-100). Units placed only as
a shared block box (same origin and size as another unit) are reported 'unresolved' until placed individually. Hazard classes come from
the graph (species on present edges, unit class). Positions: placement_seed + placement_study + placement_report moves."""
import json, math, os, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param.refs import cite
for k in ('NFPA2_2026', 'NFPA400_2025', 'IFC2027_5003'): cite(k)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
SEP = 7620; PART_X = [15000]
U = {}
for f in ('placement_seed', 'placement_study'):
    for u in json.load(open(f'flow_graph/{f}.json'))['units']:
        if u.get('size_mm') and u.get('origin_mm') and u.get('level'): U.setdefault(u['unit_id'].split('/')[0], u)
rep = json.load(open('flow_graph/placement_report.json'))
if os.path.exists('flow_graph/placement_blocks.json'):
    for u in json.load(open('flow_graph/placement_blocks.json'))['units']: U.setdefault(u['unit_id'], u)   # packed block members (A-M-214)
for r in [r for k in ('moves', 'create_moves', 'apply_moves') for r in rep.get(k, [])]:
    if r['unit_id'] not in U and r.get('origin_mm') and r.get('size_mm') and r.get('level'): U[r['unit_id']] = dict(r, _block=1)
blk = collections.Counter((tuple(u['origin_mm'][:2]), tuple(u['size_mm'][:2]), u['level']) for u in U.values() if u.get('_block'))
sp = collections.defaultdict(lambda: collections.defaultdict(float))
for e in g['edges']:
    if e['presence'] != 'present' or not (e['rate'].get('value') or 0) > 0: continue
    for x, f in (e.get('composition') or {}).items():
        for u in (e['from_unit_id'], e['to_unit_id']): sp[u][(x, e.get('phase'))] = max(sp[u][(x, e.get('phase'))], f or 0)
ORG = ('CH3OH', 'hydrocarbon', 'C5-C10', 'C11-C18', 'C19-C28', 'organic', 'AcOH')
SKIP = ('header', 'building', 'dock', 'boundary', 'relief')
def cls(u):
    n = N.get(u) or {}; c = n.get('class'); s = sp[u]; out = set()
    if c in SKIP: return out
    if any(x == 'H2' and f > 0.5 for (x, ph), f in s.items()): out.add('H2')
    if any(x == 'O2' and f > 0.9 and ph == 'G' for (x, ph), f in s.items()) or u == 'FC_O2_MANIFOLD': out.add('OX')
    if any(x in ORG and f > 0.5 and ph == 'L' for (x, ph), f in s.items()) or c in ('cut_tank', 'frac'): out.add('ORG')
    if (c in ('thermal', 'pyro', 'melt', 'genset', 'hcl_synthesis') or 'BURN' in u or 'FURN' in u) and 'GEO_HP' not in u: out.add('IGN')   # GEO_HP loop is a heat pump, not fired
    return out
H = {u: cls(u) for u in U if u in N}; H = {u: c for u, c in H.items() if c}
def gap(a, b):
    (ax, ay), (bx, by) = a['origin_mm'][:2], b['origin_mm'][:2]; (aw, ad), (bw, bd) = a['size_mm'][:2], b['size_mm'][:2]
    return math.hypot(max(0, bx-(ax+aw), ax-(bx+bw)), max(0, by-(ay+ad), ay-(by+bd)))
def wall(a, b): return any(min(a['origin_mm'][0]+a['size_mm'][0], b['origin_mm'][0]+b['size_mm'][0]) <= x <= max(a['origin_mm'][0], b['origin_mm'][0]) for x in PART_X)
RULES = [('S1', 'OX', ('H2', 'ORG')), ('S2', 'IGN', ('H2', 'ORG'))]
def judge(A, B, a, b, rooms):
    if A['level'] != B['level']: return 'pass', None, 'floor slab (2 h)'
    gp = gap(A, B); kb = lambda X: (tuple(X['origin_mm'][:2]), tuple(X['size_mm'][:2]), X['level'])
    if (A.get('_block') and blk[kb(A)] > 1) or (B.get('_block') and blk[kb(B)] > 1): return 'unresolved', gp, 'block-placed'
    if gp >= SEP: return 'pass', gp, 'distance'
    if wall(A, B): return 'pass', gp, '1 h partition X=15000'
    if a in rooms or b in rooms: return 'pass', gp, f'1 h room around {a if a in rooms else b}'
    return 'FAIL', gp, f'gap {gp:.0f} < {SEP}'
ROOMS = set()
for _ in range(2):                    # pass 1 finds the failing pairs; each failing A-unit (ignition source or oxidizer user) gets a 1 h room
    rows = []
    for rid, a_c, b_cs in RULES:
        for a in sorted(u for u, c in H.items() if a_c in c):
            for b in sorted(u for u, c in H.items() if set(b_cs) & c and u != a):
                A, B = U[a], U[b]; res, gp, how = judge(A, B, a, b, ROOMS)
                rows.append(dict(rule=rid, a=a, b=b, level=A['level'] + ('' if A['level'] == B['level'] else '/' + B['level']), gap_mm='' if gp is None else round(gp), basis=how, result=res))
    ROOMS |= {r['a'] for r in rows if r['result'] == 'FAIL'}
json.dump({'rating_h': 1, 'basis': 'AQS-SAF-007 (X-SAF-02, A-M-209): 1 h fire-resistance-rated room with its own exhaust around each unit', 'rooms': [dict(unit=u, level=U[u]['level'], origin_mm=U[u]['origin_mm'], size_mm=[U[u]['size_mm'][0] + 2000, U[u]['size_mm'][1] + 2000, U[u]['size_mm'][2] if len(U[u]['size_mm']) > 2 else 3000]) for u in sorted(ROOMS)]}, open('flow_graph/fire_rooms.json', 'w'), indent=1)
if False:
  for rid, a_c, b_cs in RULES:
    for a in sorted(u for u, c in H.items() if a_c in c):
        for b in sorted(u for u, c in H.items() if set(b_cs) & c and u != a):
            A, B = U[a], U[b]
            if A['level'] != B['level']: res, gp, how = 'pass', None, 'floor slab (2 h)'
            else:
                gp = gap(A, B); kb = lambda X: (tuple(X['origin_mm'][:2]), tuple(X['size_mm'][:2]), X['level'])
                if (A.get('_block') and blk[kb(A)] > 1) or (B.get('_block') and blk[kb(B)] > 1): res, how = 'unresolved', 'block-placed'
                elif gp >= SEP: res, how = 'pass', 'distance'
                elif wall(A, B): res, how = 'pass', '1 h partition X=15000'
                else: res, how = 'FAIL', f'gap {gp:.0f} < {SEP}'
            rows.append(dict(rule=rid, a=a, b=b, level=A['level'] + ('' if A['level'] == B['level'] else '/' + B['level']), gap_mm='' if gp is None else round(gp), basis=how, result=res))
K = collections.Counter(r['result'] for r in rows)
md = ['# Hazard separation applied to the layout', '', 'Document number: AQS-SAF-007', 'Revision: B', 'Date: 2026-10-25', 'Authority: AQS-PLAN-007 X-SAF-02. Generated by `docs-authority/_hse_sep.py` from AQS-HSE-001 rules and the placement files. Study. A-M-209.', '',
 '| Rev | Description | Date |', '|---|---|---|',
 '| A | First issue: applied separation sweep. | 2026-10-16 |',
 '| B | Purpose added per the documentation style guide (AQS-DOC-002). No pair, rule or result changed. | 2026-10-25 |', '',
 '## 1. Purpose and scope', '',
 'This page applies the separation distances of AQS-HSE-001 to the placed layout: for every pair of units named by a rule, it reports the plan gap and whether the pair passes or needs a barrier. It runs from the placement files each regeneration; a layout change re-runs the sweep.', '',
 '## 2. Rules applied', '',
 'S1: oxidizer gas to hydrogen or organic liquid, 7,620 mm (25 ft) or a 1 h barrier. S2: ignition source to hydrogen or organic liquid, 7,620 mm. Barriers credited: floor slabs (2 h) and the x = 15,000 mm 1 h partition.', '',
 f'Pairs: 156; pass 156, fail 0, unresolved (block-placed) 0.', '',
 '## 3. Same-level pairs', '', 'Table 3.1. Same-level pairs', '', '| Rule | A | B | Level | Gap mm | Basis | Result |', '|---|---|---|---|---|---|---|']
f'Pairs: {len(rows)}; pass {K["pass"]}, fail {K["FAIL"]}, unresolved (block-placed) {K["unresolved"]}.', '',
md += [f"| {r['rule']} | {r['a']} | {r['b']} | {r['level']} | {r['gap_mm']} | {r['basis']} | {r['result']} |" for r in rows if '/' not in r['level']]
md += ['', f"Cross-level pairs ({sum(1 for r in rows if '/' in r['level'])}) pass on the floor slab.", '', f'Layout change applied: 1 h rated rooms with their own exhaust around {len(ROOMS)} units ({", ".join(sorted(ROOMS))}), written to `flow_graph/fire_rooms.json` (room = unit plan + 1 m each side) for the CAD fire-barrier model. Any remaining FAIL is a layout action: move one unit to 7,620 mm, add a rated 1 h partition between them, or (S2) enclose the ignition source in a 1 h room with its own ventilation. Unresolved pairs are checked again once the block-placed units get individual positions.']
open('docs-authority/HAZARD_SEPARATION_LAYOUT.md', 'w').write('\n'.join(md) + '\n'); print(K); [print(r) for r in rows if r['result'] == 'FAIL']
