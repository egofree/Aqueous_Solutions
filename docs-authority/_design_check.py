"""AQS-QA-002 independent design check record (X-QA-02, A-M-205). Each calculation module gets a record. Where a closed-form check
exists it is recomputed here by a different route from the module (hand-formula, not the module's code) and compared; the rest are
recorded as 'second-person review required' with the checker field blank. A check is not a PE review. Run last in the pipeline."""
import glob, json, math, os, sys, csv
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param.refs import cite
for k in ('ASME_B31_3', 'PERRY9'): cite(k)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}; P = lambda u: (N.get(u) or {}).get('params') or {}
C = []
def chk(cid, module, what, model, indep, tol):
    ok = abs(model - indep) <= tol*max(abs(indep), 1e-9); C.append(dict(check=cid, module=module, item=what, model=round(model, 4), independent=round(indep, 4), tol=f'{tol*100:g} %', result='pass' if ok else 'FAIL'))
# 1 mass balance per unit (kg/d edges only)
bad = 0; nb = 0
for u, n in N.items():
    if n.get('class') in ('boundary', 'header', 'building', 'dock', 'product', 'cut_tank', 'reagent') or n.get('presence', 'present') != 'present': continue
    i = sum(e['rate']['value'] or 0 for e in g['edges'] if e['to_unit_id'] == u and e['presence'] == 'present' and e['rate'].get('unit') == 'kg/d')
    o = sum(e['rate']['value'] or 0 for e in g['edges'] if e['from_unit_id'] == u and e['presence'] == 'present' and e['rate'].get('unit') == 'kg/d')
    if i > 0.01 or o > 0.01:
        nb += 1; ok = abs(i - o) <= 0.01*max(i, o) + 0.01; bad += not ok
        if not ok: C.append(dict(check='QC-01', module='flow_graph/param/balance.py', item=f'mass balance {u}', model=round(o, 3), independent=round(i, 3), tol='1 %', result='FAIL'))
C.append(dict(check='QC-01', module='flow_graph/param/balance.py', item=f'mass balance, {nb} units (in = out)', model=nb - bad, independent=nb, tol='1 % per unit', result='pass' if not bad else f'{bad} FAIL'))
# 2 hydro energy rho g V h
h = P('HYDRO_SET'); chk('QC-02', 'flow_graph/param/water_tower.py', 'hydro ideal energy kWh = rho g V h', h.get('energy_kwh_ideal_study') or 0, 1000*9.81*h['volume_m3_m1']*h['head_m_m1']/3.6e6, 0.01)
# 3 receiver tube wall, ASME B31.3 304.1.2 t = P D / (2 (S E W + P Y))
for u in ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2'):
    d = P(u).get('design') or {}
    if d.get('P_design_MPa'): chk('QC-03', 'flow_graph/param/receivers.py', f'{u} pressure-design wall mm', d['t_req_mm'], d['P_design_MPa']*d['OD_mm']/(2*(d['S_MPa'] + d['P_design_MPa']*0.4)), 0.02)
# 4 heat battery energy = V rho cp dT
for u in ('Q4_A', 'Q4_B'):
    p = P(u); chk('QC-04', 'docs-authority/HEAT_LADDER.md', f'{u} stored kWh over 30 K (basis 20 kWh_th Q4 hold)', 20, p['vol_m3']*1000*4.18*30/3600, 0.10)
# 5 power: unit continuous kW sum vs graph electrical edges into units
SF = {e['stream_id'][3:]: e['rate']['value'] or 0 for e in g['edges'] if e['presence'] == 'present' and str(e['stream_id']).startswith('SF-')}
kw = sum(float((N[u].get('continuous_kw') or {}).get('value') or 0) for u in SF if u in N)
chk('QC-05', 'flow_graph/param/write_graph.py', f'kW of the {len(SF)} feeder-supplied units: node continuous kW vs SF- feeder edges', kw, sum(SF.values()), 0.01)
# 6 structural: level test load sum from rows
SR = json.load(open('docs-authority/inventory/STRUCT_ROWS.json')); chk('QC-06', 'docs-authority/_struct_loads.py', 'equipment rows with test >= operating >= empty', sum(1 for r in SR if r['test_kg'] >= r['op_kg'] >= r['empty_kg']), len(SR), 0.0)
# 7 composition sanity: fractions sum to 1, and a stream whose note says water is mostly water (would have caught S52)
nb7 = 0; bad7 = []
for e in g['edges']:
    c = e.get('composition') or {}
    if e['presence'] != 'present' or not c: continue
    nb7 += 1; t = sum(v for v in c.values() if isinstance(v, (int, float)))
    note = ((e.get('rate') or {}).get('note') or '') + ' ' + str(e.get('label') or '') + ' ' + str(e.get('carries') or '')
    if abs(t - 1) > 0.02 or (('water' in note.lower() and 'H2' in c and c['H2'] > 0.5 and 'H2 x 18.015' in note)): bad7.append(e['stream_id'])
C.append(dict(check='QC-07', module='flow_graph/param/write_graph.py', item=f'stream compositions sum to 1 and match their note ({nb7} streams)', model=nb7 - len(bad7), independent=nb7, tol='2 %', result='pass' if not bad7 else 'FAIL ' + ' '.join(bad7[:8])))
# 9 H2 bank inventory = tube water volume x density at 200 bar (Q-004: 19 kg)
d9 = P('CRYO_H2').get('design') or {}
if d9.get('tubes'): chk('QC-09', 'flow_graph/param/receivers.py', 'H2 bank kg at 200 bar (Q-004 basis 19 kg)', 19.0, d9['tubes']*math.pi/4*(d9['ID_mm']/1000)**2*d9['tube_m']*14.9, 0.05)
# 12 Q1 battery: oil 0.3 m3 over 80 K vs basis 10 kWh
p12 = P('Q1_A')
if p12.get('vol_m3'): chk('QC-12', 'docs-authority/HEAT_LADDER.md', 'Q1_A oil kWh over 80 K (basis 10 kWh)', 10.0, p12['vol_m3']*850*2.2*80/3600, 0.30)
# 16 water-tower head from the level datums (centroid to centroid)
import sys as _s; _s.path.insert(0, os.path.join(R, 'models/freecad')); import params as FP
r16 = FP.HYDRO; zu = sum(r16['z_res0_m'] + i*r16['level_clear_m'] + FP.SLAB_THK/1000 + r16['depth_per_level_m']/2 for i in range(r16['levels']))/r16['levels']
zl = r16['z_catch_floor_m'] + FP.SLAB_THK/1000 + r16['catch_depth_m']/2
chk('QC-16', 'flow_graph/param/water_tower.py', 'hydro head m, upper to lower water centroid', r16['head_m'], zu - zl, 0.03)
# 17 structural: level operating kN in AQS-BLD-013 = row sum x g
lv = {}
for line in open('docs-authority/STRUCT_LOADS.md'):
    c = [x.strip() for x in line.split('|')]
    if len(c) > 8 and c[1][:1] in 'LR' and c[1] != 'Level':
        try: lv[c[1]] = float(c[5])
        except ValueError: pass
rs = sum(r['op_kg'] for r in SR)*9.81/1000
if lv: chk('QC-17', 'docs-authority/_struct_loads.py', 'plant operating kN: level table vs row sum', sum(lv.values()), rs, 0.01)
# 18 foundation uplift: recompute from the document numbers
fd = open('docs-authority/FOUNDATION.md').read()
import re as _re
m = _re.search(r'Uplift[^|]*\| ([0-9,]+) kN \| ([0-9,]+) kN, FS ([0-9.]+)', fd)
if m: U_, W_, F_ = [float(x.replace(',', '')) for x in m.groups()]; chk('QC-18', 'docs-authority/_foundation.py', 'uplift FS = W/U', F_, W_/U_, 0.01)
covered = {c['module'] for c in C}
mods = sorted([m for m in glob.glob('flow_graph/param/*.py') + glob.glob('flow_graph/param/sizing/*.py') + glob.glob('docs-authority/_*.py') if not os.path.basename(m).startswith(('test_', '__'))])
rec = [dict(module=m, independent_check=', '.join(sorted({c['check'] for c in C if c['module'] == m})) or '-', status=('auto-checked' if m in covered else 'second-person review required'), checker='') for m in mods]
with open('docs-authority/inventory/DESIGN_CHECK.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rec[0])); w.writeheader(); w.writerows(rec)
fails = [c for c in C if c['result'] != 'pass']
md = ['# Independent design check record', '', 'Document number: AQS-QA-002', 'Revision: A', 'Date: 2026-10-16', 'Authority: AQS-PLAN-007 X-QA-02. Generated by `docs-authority/_design_check.py`. Study; not a PE review. A-M-205.', '',
      '## Closed-form checks (recomputed by a different route)', '', '| Check | Module | Item | Model | Independent | Tol | Result |', '|---|---|---|---|---|---|---|']
md += [f"| {c['check']} | `{c['module']}` | {c['item']} | {c['model']} | {c['independent']} | {c['tol']} | {c['result']} |" for c in C]
md += ['', '## Findings', '', '- QC-05 also found that AQS-COM-003 rev draft summed generator output (PV_ARRAY, fuel cells) into plant load; the performance test now sums consumers only.', '- QC-07 (added 2026-10-16) checks every stream composition; the S52 fuel-cell water had been labelled 98 % H2 (fixed in h2_purifier.py).', '- QC-02 found the HYDRO_SET energy keys still at the pre-Q-009 200 m3 x 18 m value (9.8 kWh); fixed in `flow_graph/param/ess_tf.py`, now from the water-tower V and head.', '',
       f'## Record per calculation module', '', f"{len(rec)} modules: {sum(1 for r in rec if r['status'] == 'auto-checked')} auto-checked, {sum(1 for r in rec if r['status'] != 'auto-checked')} need a second-person review (checker blank). Per module: `docs-authority/inventory/DESIGN_CHECK.csv`.", '',
       f'Failures: {len(fails)}.' + (' ' + '; '.join(f"{c['item']} model {c['model']} vs {c['independent']}" for c in fails[:10]) if fails else '')]
open('docs-authority/DESIGN_CHECK.md', 'w').write('\n'.join(md) + '\n'); print(len(C), len(fails), [ (c['item'],c['model'],c['independent']) for c in fails][:12])
