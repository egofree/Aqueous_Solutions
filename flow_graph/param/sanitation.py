"""X-SAN-01 multi-barrier blackwater and excreta train (owner decision 2026-10-15). Flow from HAB occupancy [ROSE2015] and vacuum-toilet
flush water [LARSEN2013]. Train: BLACK_DIGEST thermophilic anaerobic 55 C [METCALF5] -> BLACK_DEWATER screw press, cake to AFTERBURNER
(incineration) -> BLACK_PASTEUR 70 C >= 30 min (40 CFR 503 App. B PFRP) [EPA503] -> BLACK_ALK_HOLD batch hold with NaOH dosing installed
(pH > 12 for 72 h, standby barrier) and release only on test -> STRUVITE, BIOFILTER, NUTRIENT_DOSE and GREY_TREAT. Compost-toilet solids
and urine go through the same barriers. Targets: ISO 30500 log reductions [ISO30500]; released liquor and solids meet 40 CFR 503 Class A
[EPA503] and WHO 2006 Vol. 4 [WHO2006_V4]. Writes nodes, edges, placement rows (HAB sanitation room), AQS-DUTY-063
docs-authority/sizing/SANITATION.md. Run: python3 -m flow_graph.param.sanitation [--write]"""
import json, math, os, sys
from . import drivers as DR
from .reactor_design import vessel
from .write_graph import edge, rate
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'); SP = os.path.join(ROOT, 'flow_graph/placement_seed.json'); STP = os.path.join(ROOT, 'flow_graph/placement_study.json')
TAG = 'X-SAN-01 AQS-DUTY-063'
NEW = ('BLACK_DEWATER', 'BLACK_PASTEUR', 'BLACK_ALK_HOLD')

def design(d, g):
    v = lambda k: DR.val(d, k); R = {e['stream_id']: e['rate']['value'] for e in g['edges']}
    n, fc = v('san_crew'), v('san_compost_fraction')
    fw, fd, ur = v('san_feces_wet_kg_cap_d'), v('san_feces_dry_kg_cap_d'), v('san_urine_kg_cap_d')
    cover = R['IA-COVER'] + R['IA-NPK-0']
    fec_c, ur_c = n*fw*fc, n*ur*fc; E_f = n*(fw + ur)*(1 - fc); F = n*(1 - fc)*v('san_flushes_cap_d')*v('san_flush_L')
    blk = E_f + F; sol = fec_c + cover; dig_in = blk + sol
    TS = n*fd + cover*v('san_cover_dry'); VS = TS*v('san_vs_fraction'); G = VS*v('san_vs_destruction')
    cake = min((TS - G)/v('san_cake_TS'), dig_in - G); centrate = dig_in - G - cake
    past = centrate + ur_c
    fixed = {'IA-URN-STR': R['IA-URN-STR'], 'IA-BLK-BIO': R.get('IA-BLK-BIO', R['IA-TOIL-URN']), 'IA-BLK-NUT': R.get('IA-BLK-NUT', R['IA-TOIL-SOL'])}   # downstream feeds kept at their pre-X-SAN-01 rates
    grey = past - sum(fixed.values())
    # vessels
    Vd = dig_in/1000*v('san_digest_srt_d'); dg = vessel(Vd, 0.8, 1000.0, sigma_MPa=3.0, t_min=5.0)
    A = math.pi*dg['D_mm']/1000*dg['H_mm']/1000 + math.pi*(dg['D_mm']/1000)**2/2
    q_dig = dig_in*4.18*(v('san_digest_T_C') - 20)/86.4 + 0.5*A*(v('san_digest_T_C') - 20)          # W, feed heat-up + 50 mm PIR losses
    Vb = past/1000/v('san_past_batches_d'); ps = vessel(Vb, 0.8, 1000.0, steel=True, t_min=2.0, CA=0.0)
    T_mix = (centrate*(v('san_digest_T_C') - 5) + ur_c*20)/past                                           # centrate cools 5 K in the press
    q_past = past*4.18*(v('san_past_T_C') - T_mix)/86.4 + 30.0                                             # W, + 30 W hold losses (insulated)
    Vh = past/1000; hd = vessel(Vh, 0.9, 1000.0, sigma_MPa=5.0, t_min=4.0)
    naoh = past*0.2*40/1000                                                                                # kg/d NaOH at 0.2 mol/L dose when the standby barrier runs
    kW = {'BLACK_DIGEST': q_dig/1000 + 0.02, 'BLACK_DEWATER': 0.09*2/24, 'BLACK_PASTEUR': q_past/1000 + 0.01, 'BLACK_ALK_HOLD': 0.02}
    return dict(n=n, fc=fc, fec_c=fec_c, ur_c=ur_c, E_f=E_f, F=F, blk=blk, sol=sol, dig_in=dig_in, TS=TS, VS=VS, G=G, cake=cake, centrate=centrate,
                past=past, fixed=fixed, grey=grey, dg=dg, ps=ps, hd=hd, q_dig=q_dig, q_past=q_past, T_mix=T_mix, naoh_standby=naoh, kW=kW)

def write(d, g, r):
    N = {x['unit_id']: x for x in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    tmpl = N['BLACK_DIGEST']
    base0_outs = sum(e['rate']['value'] for e in g['edges'] if e['from_unit_id'] == 'HABITATION' and e['rate'].get('unit') == 'kg/d')
    notes = {'BLACK_DIGEST': 'Thermophilic anaerobic digester 55 C, 15 d SRT; barrier 1 (X-SAN-01).',
             'BLACK_DEWATER': 'Screw press; cake to AFTERBURNER in sealed bins (incineration, barrier 2).',
             'BLACK_PASTEUR': 'Batch pasteuriser 70 C >= 30 min, 40 CFR 503 PFRP (barrier 3).',
             'BLACK_ALK_HOLD': 'Three batch hold tanks; NaOH dosing to pH > 12 for 72 h installed as standby barrier 4; release only on a passing test (barrier 5).'}
    for u in ('BLACK_DIGEST',) + NEW:
        x = N.get(u) or {**json.loads(json.dumps(tmpl)), 'unit_id': u}
        x['notes'] = notes[u]; x['electrical_role'] = 'load'; x['sector_id'] = 'WTR'
        x['continuous_kw'] = rate(r['kW'][u], 'kW', f'{TAG}.')
        if u not in N: g['nodes'].append(x); N[u] = x
    N['BLACK_DIGEST']['params']['internals'] = 'gas-mixed (biogas recirculation), no shaft seal'
    def put(sid, a, b, ph, carries, val, note, sa=None, sb=None):
        if sid in E:
            e = E[sid]; e['from_unit_id'], e['to_unit_id'] = a, b; e['rate'] = rate(val, 'kg/d' if ph != 'E' else 'kW', note); e['carries'] = carries
            e['from_sector_id'] = N[a].get('sector_id'); e['to_sector_id'] = N[b].get('sector_id')
        else:
            e = edge(sid, a, b, ph, ['mass'] if ph != 'E' else (['elec'] if sid.startswith('SF') else ['energy']), carries, rate(val, 'kg/d' if ph != 'E' else 'kW', note),
                     N[a].get('sector_id'), N[b].get('sector_id'), 'tray' if ph == 'E' else 'dedicated'); g['edges'].append(e); E[sid] = e
    put('IA-FEC-01', 'HABITATION', 'COMPOST_TOILET', 'S/L', 'faeces (compost-toilet share)', r['fec_c'], f"{TAG}. {r['n']} x 0.128 kg/d x {r['fc']} [ROSE2015].")
    put('IA-URINE', 'HABITATION', 'COMPOST_TOILET', 'S', 'urine (compost-toilet share)', r['ur_c'], f"{TAG}. {r['n']} x 1.42 kg/d x {r['fc']} [ROSE2015].")
    put('IA-BLK-01', 'HABITATION', 'BLACK_DIGEST', 'L', 'vacuum-toilet blackwater', r['blk'], f"{TAG}. Excreta {r['E_f']:.3f} + flush {r['F']:.2f} kg/d [ROSE2015, LARSEN2013].")
    put('IA-TOIL-SOL', 'COMPOST_TOILET', 'BLACK_DIGEST', 'S', 'compost-toilet solids and cover to the barrier train (not to FARM)', r['sol'], f'{TAG}. Owner decision: compost-toilet output through the same barriers.')
    put('IA-TOIL-URN', 'COMPOST_TOILET', 'BLACK_PASTEUR', 'L', 'compost-toilet urine to pasteurisation', r['ur_c'], f'{TAG}.')
    put('IA-BLK-GAS', 'BLACK_DIGEST', 'AFTERBURNER', 'G', 'digester biogas, flared in the afterburner', r['G'], f"{TAG}. VS destroyed {r['G']:.4f} kg/d [METCALF5].")
    put('IA-BLK-DIG', 'BLACK_DIGEST', 'BLACK_DEWATER', 'L', 'thermophilic digestate', r['dig_in'] - r['G'], f'{TAG}.')
    put('IA-BLK-CAKE', 'BLACK_DEWATER', 'AFTERBURNER', 'S', 'dewatered cake in sealed bins to incineration', r['cake'], f'{TAG}. TS {DR.val(d,"san_cake_TS")} [METCALF5].')
    put('IA-BLK-CEN', 'BLACK_DEWATER', 'BLACK_PASTEUR', 'L', 'centrate', r['centrate'], f'{TAG}.')
    put('IA-BLK-PAST', 'BLACK_PASTEUR', 'BLACK_ALK_HOLD', 'L', 'pasteurised liquor', r['past'], f'{TAG}. 70 C >= 30 min [EPA503].')
    put('IA-BLK-NAOH', 'BMED_BASE', 'BLACK_ALK_HOLD', 'L', 'NaOH for the standby alkaline barrier (normally zero)', 0.0, f"{TAG}. Standby: {r['naoh_standby']:.3f} kg/d NaOH when run.")
    put('IA-URN-STR', 'BLACK_ALK_HOLD', 'STRUVITE', 'L', 'released liquor to struvite (after test)', r['fixed']['IA-URN-STR'], f'{TAG}. Batch release.')
    put('IA-BLK-BIO', 'BLACK_ALK_HOLD', 'BIOFILTER', 'L', 'released liquor to the biofilter (after test)', r['fixed']['IA-BLK-BIO'], f'{TAG}. Batch release.')
    put('IA-BLK-NUT', 'BLACK_ALK_HOLD', 'NUTRIENT_DOSE', 'L', 'released liquor to nutrient dosing (after test)', r['fixed']['IA-BLK-NUT'], f'{TAG}. Batch release; replaces the compost-toilet solids that went to COMPOST.')
    put('IA-BLK-GREY', 'BLACK_ALK_HOLD', 'GREY_TREAT', 'L', 'released liquor to grey treatment (after test)', r['grey'], f'{TAG}. Balance.')
    # balances: GREY_TREAT inflow unchanged (S12 reduced by the released liquor); COMPOST loses the toilet solids (IA-COMP-OUT reduced, NUTRIENT_DOSE
    # gets the same mass from IA-BLK-NUT); HABITATION remainder term by difference; AFTERBURNER combustion of cake and biogas as an off-graph flue term
    hp = N['HABITATION']['params']; base = hp.setdefault('san_base', {'S12': E['S12']['rate']['value'], 'IA-COMP-OUT': E['IA-COMP-OUT']['rate']['value'], 'S11': E['S11']['rate']['value']})
    E['S12']['rate']['value'] = round(base['S12'] - r['grey'], 4); E['S12']['rate']['note'] = f"{TAG}. Grey less the flush water drawn by the vacuum toilets (returned as released liquor IA-BLK-GREY)."
    E['IA-COMP-OUT']['rate']['value'] = round(base['IA-COMP-OUT'] - r['fixed']['IA-BLK-NUT'], 4)
    for t in hp['balance_rev_l']['terms']:
        if t.get('kind') == 'by_difference': cond = t
    outs = lambda: sum(e['rate']['value'] for e in g['edges'] if e['from_unit_id'] == 'HABITATION' and e['rate'].get('unit') == 'kg/d')
    base.setdefault('outs', base0_outs); base.setdefault('cond', cond['value'])
    cond['value'] = round(base['cond'] - (outs() - base['outs']), 4); cond['basis'] = 'S12 governs grey; X-SAN-01 excreta from occupancy (by difference)'
    assert cond['value'] >= 0, 'HABITATION remainder negative'
    E['S11']['rate']['value'] = round(base.setdefault('S11', 0.8) - r['cake'] - r['G'], 4)
    E['S11']['rate']['note'] = f"{TAG}. Afterburner feed held at the AQS-DUTY-008 design; grow-bed organics to the afterburner reduced by the sanitation cake and biogas ({r['cake'] + r['G']:.3f} kg/d), retained in GROW_BED (A-M-118)."
    assert E['S11']['rate']['value'] >= 0
    ab = N['AFTERBURNER']['params']['balance_rev_l']['terms']
    ab[:] = [t for t in ab if t.get('label') != 'sanitation cake and biogas combustion products to flue']
    for u in ('BLACK_DIGEST',) + NEW:
        ks = r['kW'][u]; put(f'SF-{u}', 'SOL_ARK_60K', u, 'E', '480 V or 208/120 V AC (bus per AQS-ELEC-002)', ks, f'{TAG}. Equals node continuous_kw.')
        put(f'SQ-{u}', u, 'HEAT_SINK', 'E', 'electrical input leaving as heat', ks, f'{TAG}.')
    for u, k in (('BLACK_DIGEST', 'dg'), ('BLACK_PASTEUR', 'ps'), ('BLACK_ALK_HOLD', 'hd')):
        x = r[k]; N[u]['params']['design'] = x
        N[u]['params']['size_mm'] = [x['D_mm'] + 300, x['D_mm'] + 300, x['H_mm'] + 500] if u != 'BLACK_ALK_HOLD' else [3*(x['D_mm'] + 150) + 300, x['D_mm'] + 300, x['H_mm'] + 500]
    N['BLACK_DEWATER']['params']['size_mm'] = [800, 600, 900]
    for u in ('BLACK_DIGEST',) + NEW:
        N[u]['params']['duty'] = f'{TAG}. Sheet docs-authority/sizing/SANITATION.md.'
    open(GP, 'w').write(json.dumps(g, indent=2))
    # placement: HAB sanitation room, west wall, north of HAB_MED
    seed = json.load(open(SP)); U = {x['unit_id']: x for x in seed['units']}; y = 9000
    for u in ('BLACK_DIGEST',) + NEW:
        sz = N[u]['params']['size_mm']; row = U.get(u) or {'unit_id': u, 'level': 'L1'}
        row.update(origin_mm=[200, y, 6000], size_mm=sz, source=f'{TAG}: HAB sanitation room (west wall, 1 h walls, own exhaust, negative to HAB corridor); >= {DR.val(d,"san_farm_sep_m")} m from every FARM unit.')
        if u not in U: seed['units'].append(row)
        y += sz[1] + 600
    open(SP, 'w').write(json.dumps(seed, indent=1) + '\n')
    return E, N

def sep(d):
    g = json.load(open(GP)); FARM = {n['unit_id'] for n in g['nodes'] if n.get('sector_id') == 'FARM'} | {'AZOLLA_BED'}
    seed = json.load(open(SP)); st = json.load(open(STP)); B = {}
    for x in seed['units'] + st['units']: B[x['unit_id']] = (x['level'], x['origin_mm'][0], x['origin_mm'][1], x['size_mm'][0], x['size_mm'][1])
    out = []
    for u in ('BLACK_DIGEST',) + NEW:
        p = B[u]; best = (1e9, None)
        for f in FARM:
            q = B.get(f)
            if not q or q[0] != p[0]: continue
            dx = max(0, q[1] - (p[1] + p[3]), p[1] - (q[1] + q[3])); dy = max(0, q[2] - (p[2] + p[4]), p[2] - (q[2] + q[4]))
            best = min(best, (math.hypot(dx, dy)/1000, f))
        out.append((u, best[1], best[0], best[0] >= DR.val(d, 'san_farm_sep_m')))
    return out

def write_doc(d, r, S):
    v = lambda k: DR.val(d, k)
    md = f"""# Blackwater and excreta multi-barrier train

Document number: AQS-DUTY-063
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-SAN-01 (owner decision 2026-10-15: BLACK_DIGEST fully integrated; no reliance on compost toilets alone; no pathogen pathway to FARM). Generated by `flow_graph/param/sanitation.py`. Study. A-M-118.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. | 2026-10-15 |

## 1. Flow basis

| Quantity | Value | Basis |
| --- | --- | --- |
| Occupancy | {r['n']} persons | HABITATION crew_study (A-M-118) |
| Faeces, wet / dry | {v('san_feces_wet_kg_cap_d')} / {v('san_feces_dry_kg_cap_d')} kg/(cap d) | ROSE2015 medians |
| Urine | {v('san_urine_kg_cap_d')} kg/(cap d) | ROSE2015 median |
| Compost-toilet share (daily average) | {r['fc']} | A-M-118; each path is sized for 100 % of the occupancy |
| Vacuum-toilet flush | {v('san_flush_L')} L x {v('san_flushes_cap_d')} per person per day = {r['F']:.1f} kg/d | LARSEN2013; A-M-118 |
| Blackwater to BLACK_DIGEST | {r['blk']:.2f} kg/d | IA-BLK-01 |
| Compost-toilet solids and cover to BLACK_DIGEST | {r['sol']:.3f} kg/d | IA-TOIL-SOL (rerouted from COMPOST) |
| Compost-toilet urine to BLACK_PASTEUR | {r['ur_c']:.3f} kg/d | IA-TOIL-URN (rerouted from BIOFILTER) |

## 2. Barriers

| No. | Unit | Barrier | Condition | Design | Electrical |
| --- | --- | --- | --- | --- | --- |
| 1 | BLACK_DIGEST | thermophilic anaerobic digestion | {v('san_digest_T_C'):.0f} C, SRT {v('san_digest_srt_d'):.0f} d (METCALF5) | {r['dg']['V_L']:.0f} L, DN{r['dg']['D_mm']} x {r['dg']['H_mm']} mm, PP-H {r['dg']['wall_mm']} mm, 50 mm PIR; biogas {r['G']*1000:.0f} g/d flared in AFTERBURNER | {r['q_dig']:.0f} W heat |
| 2 | BLACK_DEWATER + AFTERBURNER | solids incineration | cake {v('san_cake_TS')*100:.0f} % TS (METCALF5), {r['cake']:.3f} kg/d in sealed bins to AFTERBURNER | in-house screw press, 316L screen | 0.09 kW, 2 h/d |
| 3 | BLACK_PASTEUR | pasteurisation (PFRP) | {v('san_past_T_C'):.0f} C held >= {v('san_past_min'):.0f} min, 40 CFR 503 App. B (EPA503) | 2 batch vessels {r['ps']['V_L']:.1f} L, DN{r['ps']['D_mm']}, 316L, {v('san_past_batches_d')} batches/d; two independent RTDs, hold timer restarts below set point | {r['q_past']:.0f} W heat (inlet {r['T_mix']:.0f} C) |
| 4 | BLACK_ALK_HOLD | alkaline treatment (standby) | NaOH from BMED_BASE to pH > 12 for 72 h (EPA503 503.32(a)(4) basis); run on any pasteuriser excursion or failed test; {r['naoh_standby']:.3f} kg/d NaOH when run | dosing pump and pH probe on each hold tank | 0.02 kW |
| 5 | BLACK_ALK_HOLD | batch hold and release on test | 3 tanks of {r['hd']['V_L']:.0f} L (filling / holding and testing / releasing), {v('san_hold_d'):.0f} d cycle; release valve interlocked to a passing result | HDPE {r['hd']['wall_mm']} mm, DN{r['hd']['D_mm']} | — |

Chemical option. Hypochlorite needs an on-site chlor-alkali source that the graph does not have. The alkaline barrier uses NaOH from BMED_BASE (no new chemical). Its daily rate is zero in normal operation; IA-BLK-NAOH carries the standby rate in its note. The solver NaOH balance is unchanged.

## 3. Targets and verification

| Organism group (indicator) | Target, whole train | Basis | Test |
| --- | --- | --- | --- |
| Bacteria (E. coli) | >= 6 log | ISO30500 | Standard Methods 9223 B on the feed and released liquor |
| Viruses (MS2 coliphage) | >= 7 log | ISO30500 | EPA Method 1602 on a spiked challenge |
| Protozoa (C. perfringens spores) | >= 6 log | ISO30500 | ISO 14189 on a spiked challenge |
| Helminths (Ascaris suum eggs) | >= 4 log | ISO30500 | EPA/625/R-92/013 App. I on a spiked challenge |
| Released liquor and cake | faecal coliform < 1000 MPN/g TS or Salmonella < 3 MPN/4 g TS; < 1 helminth egg/g TS | EPA503 Class A; WHO2006_V4 | EPA 1680 / 1682 per batch before release |

Log credits per barrier are not assumed. Design rule: pasteurisation alone must show the full ISO 30500 reduction in the challenge test (it is the PFRP step). Digestion, the alkaline hold and the release test are independent extra barriers. Cake is incinerated and never released. Commissioning: challenge test on three consecutive batches; operation: E. coli and faecal coliform on every batch, the full panel quarterly (A-M-118).

## 4. Separation from FARM

The train sits in a 1 h-rated sanitation room on the HAB west wall, with its own exhaust held negative to the HAB corridor, which is negative to FARM. Its drains are dedicated to the room and do not share a trap or vent with FARM. Released liquor reaches FARM-side units (STRUVITE, BIOFILTER, NUTRIENT_DOSE) only through the interlocked release valve.

| Unit | Nearest FARM unit | Edge distance, m | >= {v('san_farm_sep_m')} m |
| --- | --- | --- | --- |
{chr(10).join(f'| {a} | {b} | {c:.1f} | {"pass" if ok else "FAIL"} |' for a, b, c, ok in S)}

## 5. Balance changes

- IA-TOIL-SOL, IA-TOIL-URN and IA-URN-STR no longer go straight to COMPOST, BIOFILTER or STRUVITE. Those units receive the same masses from BLACK_ALK_HOLD after release, and COMPOST to NUTRIENT_DOSE is reduced by the solids it no longer gets.
- S12 (grey) is reduced by the flush water; the same mass returns to GREY_TREAT as released liquor IA-BLK-GREY, so the GREY_TREAT inflow is unchanged.
- The HABITATION remainder term is recomputed by difference. AFTERBURNER feed is held at the AQS-DUTY-008 design rate: S11 (grow-bed organics) is reduced by the cake and biogas mass, which stays in GROW_BED (A-M-118).
"""
    open(os.path.join(ROOT, 'docs-authority/sizing/SANITATION.md'), 'w').write(md)

def main():
    d = DR.load(); g = json.load(open(GP)); r = design(d, g)
    if '--write' in sys.argv: write(d, g, r); write_doc(d, r, sep(d))
    for k, x in r.items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in x.items()} if isinstance(x, dict) else (round(x, 4) if isinstance(x, float) else x))

if __name__ == '__main__': main()
