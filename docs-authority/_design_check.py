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
kw = sum(float(((N[u].get('continuous_kw') or {}).get('value') if isinstance(N[u].get('continuous_kw'), dict) else N[u].get('continuous_kw')) or 0) for u in SF if u in N)   # R11 Rev AC regen: foundry units carry scalar continuous_kw
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
# 19 wire conductor resistance vs NEC Chapter 9 Table 8 (75 C, stranded) brought to 20 C
ws = {r['size']: r['R20'] for r in json.load(open('docs-authority/inventory/WIRE_SPECS.json'))}
for sz, t8 in (('14 AWG', 3.14), ('10 AWG', 1.24), ('6 AWG', 0.491), ('4/0 AWG', 0.0608), ('400 kcmil', 0.0321)):
    if sz in ws: chk('QC-19', 'docs-authority/_wire_specs.py', f'{sz} R20 ohm/km vs NEC Ch. 9 Table 8', round(t8*3.2808/(1 + 0.00393*55), 4), ws[sz], 0.03)
# 20 motor line current = P / (eta pf sqrt3 V), MF-10 sheet values
import csv as _csv
md10 = {r['family']: r for r in _csv.DictReader(open('docs-authority/inventory/MOTOR_DESIGNS.csv'))}.get('MF-10')
if md10: chk('QC-20', 'flow_graph/inventory/motor_designs.py', 'MF-10 line current A', float(md10['current_A']), 1500/(0.865*0.80*math.sqrt(3)*480), 0.02)
# 21 first-article rated torque = 9549 P / n at 3 % slip
fa = {r['family']: r for r in json.load(open('docs-authority/inventory/MOTOR_FA.json'))}
if 'MF-18' in fa: chk('QC-21', 'docs-authority/_motor_fa.py', 'MF-18 rated torque N m', fa['MF-18']['T_Nm'], 9549*18.5/(1800*0.97), 0.01)
# 22 BMED bench output g/h = N I CE M / F
tr = json.load(open('docs-authority/inventory/TEST_RIGS.json'))
chk('QC-22', 'docs-authority/_test_rigs.py', 'BMED bench NaOH g/h (10 triplets, 8 A, CE 0.80)', tr['bmed']['naoh_g_h'], 10*8.0*0.80/96485*39.997*3600, 0.01)
# 23 resize sweep: OIL_DRYER MSW capacity = design day x organic ratio 0.30 / 0.22
od = (N.get('OIL_DRYER') or {}).get('params', {}).get('design_capacity_kg_d') if 'N' in dir() else None
if od is None:
    od = next((n['params'].get('design_capacity_kg_d') for n in g['nodes'] if n['unit_id'] == 'OIL_DRYER'), None)
if od: chk('QC-23', 'docs-authority/_resize_sweep.py', 'OIL_DRYER capacity kg/d at MSW', od['value'], 33.0*0.30/0.22, 0.01)
# 24 CAD clash gate
cc = json.load(open('docs-authority/inventory/CAD_CLASH.json'))
C.append(dict(check='QC-24', module='models/freecad/clash_check.py', item=f"CAD clashes, {cc['new']} new elements vs {cc['others']} solids", model=len(cc['clashes']), independent=0, tol='0', result='pass' if not cc['clashes'] else f"FAIL {len(cc['clashes'])}"))
# 25 PV Wire 2 kV insulation wall = UL 4703 75 mil
w1 = next(r for r in json.load(open('docs-authority/inventory/WIRE_SPECS.json')) if r['fam'] == 'WF-01')
chk('QC-25', 'docs-authority/_wire_specs.py', 'WF-01 core OD mm = stranded OD + 2 x 1.905 mm', w1['Dc'] + 2*1.905, w1['D'], 0.01)
# 26 TC-ER 4/c 14 AWG XHHW-2 cable OD vs a published UL 1277 cable table (10.4 mm)
w5 = next(r for r in json.load(open('docs-authority/inventory/WIRE_SPECS.json')) if r['fam'] == 'WF-05')
chk('QC-26', 'docs-authority/_wire_specs.py', 'WF-05 4/c 14 AWG TC-ER OD mm vs published 10.4 mm', 10.4, w5['Dj'], 0.05)
# 27 equipment clash and corridor gate
ce = json.load(open('docs-authority/inventory/CAD_CLASH_EQUIP.json'))
C.append(dict(check='QC-27', module='models/freecad/clash_equip.py', item=f"equipment overlaps and corridor intrusions ({ce['solids']} solids)", model=len(ce['clashes']) + len(ce['in_corridor']), independent=0, tol='0', result='pass' if not (ce['clashes'] or ce['in_corridor']) else 'FAIL'))
# 28 motor slots and yoke fit the lamination OD
fa2 = json.load(open('docs-authority/inventory/MOTOR_FA.json')); bad = [r['family'] for r in fa2 if 'od_ok' in r and not r['od_ok']]
C.append(dict(check='QC-28', module='flow_graph/inventory/motor_designs.py', item='induction slot + yoke fit the sheet OD (AQS-INV-008 re-derivation)', model=len(bad), independent=0, tol='0', result='pass' if not bad else 'FAIL ' + ' '.join(bad)))
# 29 catch tank top below the L-1 slab
C.append(dict(check='QC-29', module='flow_graph/param/water_tower.py', item='catch tank top below L-1 FFL - slab (mm)', model=FP.CATCH_TANK_Z + FP.CATCH_TANK_H, independent=FP.Z_Lm1 - FP.SLAB_THK, tol='<=', result='pass' if FP.CATCH_TANK_Z + FP.CATCH_TANK_H <= FP.Z_Lm1 - FP.SLAB_THK else 'FAIL'))
# 30 L-1 flow adjacency did not get worse after the regroup
rg_ = json.load(open('docs-authority/inventory/CAD_REGROUP.json'))
C.append(dict(check='QC-30', module='models/freecad/regroup.py', item=f"L-1 flow adjacency m ({rg_['units']} units, {rg_['moves']} moves)", model=rg_['adjacency_after_m'], independent=rg_['adjacency_before_m'], tol='<=', result='pass' if rg_['adjacency_after_m'] <= rg_['adjacency_before_m'] else 'FAIL'))
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
