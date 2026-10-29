"""AQS-DUTY-063 blackwater and excreta train (task X-SAN-01, owner decision 2026-10-15).

Reads the plant graph and flow_graph/param/drivers.json and writes docs-authority/sizing/SANITATION.md. It does not edit the graph.
The graph carries the whole train as the one node BLACK_DIGEST (Rev AC retired the nodes BLACK_DEWATER, BLACK_PASTEUR and
BLACK_ALK_HOLD and carried their splits at the digester). This module sizes the equipment of every barrier from the flows of that
node: the thermophilic digester [METCALF5], the screw press whose cake is burned in AFTERBURNER, the batch pasteuriser held at the
40 CFR 503 time and temperature [EPA503], and the batch hold tanks with standby alkaline dosing. It also checks the afterburner
chamber against the graph flue [EU_IED2010] and the distance of each unit from the FARM units.
The first version of this module (2026-10-15) edited the graph once; that edit is in the graph, and this version only reads it.
Run: python3 -m flow_graph.param.sanitation [--write]"""
import json, math, os, sys
from . import drivers as DR, site as SITE
from .reactor_design import vessel
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json'); SP = os.path.join(ROOT, 'flow_graph/placement_seed.json'); STP = os.path.join(ROOT, 'flow_graph/placement_study.json')
OUT = os.path.join(ROOT, 'docs-authority/sizing/SANITATION.md')
SAN = 'WTR.grey-black-train.'
U = 'BLACK_DIGEST'
TRAIN = ('BLACK_DIGEST', 'BLACK_DEWATER', 'BLACK_PASTEUR', 'BLACK_ALK_HOLD')

def _mass(e):
    r = e.get('rate') or {}
    return r.get('value') if r.get('unit') == 'kg/d' and isinstance(r.get('value'), (int, float)) else None

def design(d, g):
    v = lambda k: DR.val(d, k)
    N = {n['unit_id']: n for n in g['nodes']}
    live = [e for e in g['edges'] if e.get('presence') != 'retired']
    ins = [(e['stream_id'], e['from_unit_id'], _mass(e)) for e in live if e['to_unit_id'] == U and _mass(e) is not None]
    outs = [(e['stream_id'], e['to_unit_id'], _mass(e)) for e in live if e['from_unit_id'] == U and _mass(e) is not None]
    unrated = sorted(e['stream_id'] for e in live if U in (e['from_unit_id'], e['to_unit_id']) and _mass(e) is None and 'elec' not in (e.get('layers') or []))
    E = {e['stream_id']: e for e in live}
    dig_in = sum(x[2] for x in ins); dig_out = sum(x[2] for x in outs)
    gas = sum(x[2] for x in outs if x[1] == 'AFTERBURNER' and 'GAS' in x[0])
    cake = sum(x[2] for x in outs if x[1] == 'AFTERBURNER' and 'GAS' not in x[0])
    liquor = dig_out - gas - cake                                   # every stream that leaves the train other than to the afterburner
    # occupancy check: the vacuum-toilet blackwater the drivers give for the occupancy, against IA-BLK-01
    crew = (N.get('HABITATION') or {}).get('params', {}).get('crew_study', v('san_crew')); fc = v('san_compost_fraction')
    excreta = crew*(v('san_feces_wet_kg_cap_d') + v('san_urine_kg_cap_d')); flush_all = crew*v('san_flushes_cap_d')*v('san_flush_L')
    blk_calc = excreta*(1 - fc) + flush_all*(1 - fc)
    # barrier 1: digester, volume from the solids retention time; heat for feed warm-up plus the insulated shell loss
    Vd = dig_in/1000*v('san_digest_srt_d')
    dg = vessel(Vd, v(SAN+'san_dig_fill'), 1000.0, sigma_MPa=v(SAN+'san_sigma_PP_MPa'), t_min=v(SAN+'san_pp_t_min_mm'))
    A = math.pi*dg['D_mm']/1000*dg['H_mm']/1000 + math.pi*(dg['D_mm']/1000)**2/2
    dT = v('san_digest_T_C') - v(SAN+'san_feed_T_C')
    q_dig = dig_in*v(SAN+'san_water_cp_kJ_kgK')*dT/86.4 + v(SAN+'san_dig_U_W_m2K')*A*dT
    # barrier 3: batch pasteuriser on the liquor, which leaves the press cooled by san_press_cool_K
    T_in = v('san_digest_T_C') - v(SAN+'san_press_cool_K')
    ps = vessel(liquor/1000/v('san_past_batches_d'), v(SAN+'san_dig_fill'), 1000.0, steel=True, t_min=v(SAN+'san_steel_t_min_mm'), CA=v(SAN+'san_CA_mm'))
    q_past = liquor*v(SAN+'san_water_cp_kJ_kgK')*(v('san_past_T_C') - T_in)/86.4 + v(SAN+'san_past_loss_W')
    # barriers 4 and 5: one hold tank per day of the hold cycle, each holding one day of liquor
    tanks = math.ceil(v('san_hold_d'))
    hd = vessel(liquor/1000, v(SAN+'san_hold_fill'), 1000.0, sigma_MPa=v(SAN+'san_sigma_HDPE_MPa'), t_min=v(SAN+'san_hdpe_t_min_mm'))
    naoh = liquor*v(SAN+'san_naoh_dose_mol_L')*40/1000
    kW = {'BLACK_DIGEST': q_dig/1000 + v(SAN+'san_dig_aux_kW'), 'BLACK_DEWATER': v(SAN+'san_press_kW')*v(SAN+'san_press_run_h')/24,
          'BLACK_PASTEUR': q_past/1000 + v(SAN+'san_past_aux_kW'), 'BLACK_ALK_HOLD': v(SAN+'san_hold_aux_kW')}
    sf = (E.get('SF-' + U) or {}).get('rate', {}).get('value')
    # afterburner chamber from the graph: every mass stream that leaves AFTERBURNER is flue at the chamber temperature
    ab_in = sum(_mass(e) for e in live if e['to_unit_id'] == 'AFTERBURNER' and _mass(e) is not None)
    flue = sum(_mass(e) for e in live if e['from_unit_id'] == 'AFTERBURNER' and _mass(e) is not None)
    rho = SITE.process_air_density(v(SAN+'san_ab_T_C')); Q = flue/86400/rho; Vc = Q*v(SAN+'san_ab_residence_s')
    lad = v(SAN+'san_ab_DN_ladder_mm')
    Dc = next((x for x in lad if v(SAN+'san_ab_LD')*(x/1000) >= 4*Vc/math.pi/(x/1000)**2), lad[-1]); Lc = 4*Vc/math.pi/(Dc/1000)**2
    ab = dict(feed_kg_d=ab_in, flue_kg_d=flue, V_L=Vc*1000, D_mm=Dc, L_mm=max(math.ceil(Lc*1000/50)*50, 50))
    return dict(ins=ins, outs=outs, unrated=unrated, dig_in=dig_in, dig_out=dig_out, gas=gas, cake=cake, liquor=liquor, crew=crew, fc=fc,
                excreta=excreta, flush_all=flush_all, blk_calc=blk_calc, blk_graph=_mass(E['IA-BLK-01']) if 'IA-BLK-01' in E else None,
                dg=dg, q_dig=q_dig, ps=ps, q_past=q_past, T_in=T_in, tanks=tanks, hd=hd, naoh=naoh, kW=kW, kW_total=sum(kW.values()), sf=sf, ab=ab,
                retired=[u for u in TRAIN[1:] if u not in N or N[u].get('presence') == 'retired'])

def sep(d):
    g = json.load(open(GP)); FARM = {n['unit_id'] for n in g['nodes'] if n.get('sector_id') == 'FARM'} | {'AZOLLA_BED'}
    B = {}
    for p in (SP, STP):
        if os.path.exists(p):
            for x in json.load(open(p)).get('units', []): B[x['unit_id']] = (x['level'], x['origin_mm'][0], x['origin_mm'][1], x['size_mm'][0], x['size_mm'][1])
    out = []
    for u in TRAIN:
        p = B.get(u)
        if p is None: continue
        best = (math.inf, None)
        for f in FARM:
            q = B.get(f)
            if not q or q[0] != p[0]: continue
            dx = max(0, q[1] - (p[1] + p[3]), p[1] - (q[1] + q[3])); dy = max(0, q[2] - (p[2] + p[4]), p[2] - (q[2] + q[4]))
            best = min(best, (math.hypot(dx, dy)/1000, f))
        out.append((u, best[1], best[0], best[0] >= DR.val(d, 'san_farm_sep_m')))
    return out

def _f(x, n=3): return f'{x:.{n}f}'

def _and(xs): return ', '.join(xs[:-1]) + ' and ' + xs[-1] if len(xs) > 1 else ''.join(xs)

def write_doc(d, r, S):
    v = lambda k: DR.val(d, k)
    ins = '\n'.join(f'| {s} | {u} | {_f(m)} |' for s, u, m in r['ins'])
    outs = '\n'.join(f'| {s} | {u} | {_f(m)} |' for s, u, m in r['outs'])
    unrated = (' The streams ' + _and(r['unrated']) + ' are on the graph without a mass rate and are left out.') if r['unrated'] else ''
    clos = r['dig_in'] - r['dig_out']
    blk = r['blk_graph']
    blk_txt = ''
    if blk is not None:
        blk_txt = (f"The drivers give {r['crew']} occupants {_f(r['excreta'])} kg/d of faeces and urine ([ROSE2015]) and {_f(r['flush_all'], 1)} kg/d of vacuum-toilet flush water ([LARSEN2013]). "
                   f"With the compost-toilet share `san_compost_fraction` of {r['fc']} taken out, the blackwater is {_f(r['blk_calc'])} kg/d, and stream IA-BLK-01 carries {_f(blk)} kg/d"
                   + (', so the two agree.' if abs(r['blk_calc'] - blk) < 0.01 else ', so the two differ.')
                   + " The excreta of the compost-toilet share reach BLACK_DIGEST directly, without flush water, by the streams IA-URINE and IA-FEC-01.")
    sf = r['sf']
    sf_txt = (f"The electrical load of the train is {_f(r['kW_total'])} kW. The graph feeds BLACK_DIGEST with {_f(sf, 4)} kW by stream SF-BLACK_DIGEST"
              + (', which agrees.' if sf is not None and abs(sf - r['kW_total']) < 0.0005 else ', so the feed differs from the load of the train by ' + _f(r['kW_total'] - (sf or 0)) + ' kW.')) if sf is not None else \
             f"The electrical load of the train is {_f(r['kW_total'])} kW. The graph has no feed stream SF-BLACK_DIGEST."
    retired = (' The graph no longer has the nodes ' + _and(r['retired']) + '; their equipment is still built (`models/mfg/`), and this page sizes it from the flows of BLACK_DIGEST.') if r['retired'] else ''
    seprows = '\n'.join(f'| {a} | {b} | {c:.1f} | {"pass" if ok else "fail"} |' for a, b, c, ok in S)
    dg, ps, hd, ab = r['dg'], r['ps'], r['hd'], r['ab']
    md = f"""# Blackwater and excreta train

Document number: AQS-DUTY-063
Revision: C
Date: 2026-10-29
Generated by `flow_graph/param/sanitation.py` from the plant graph and `flow_graph/param/drivers.json`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.
Authority: task X-SAN-01 of AQS-PLAN-007; owner decision of 2026-10-15 that BLACK_DIGEST is fully integrated, that the plant does not rely on compost toilets alone, and that there is no pathogen pathway to FARM; assumption A-M-118. Study.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. | 2026-10-15 |
| B | S11 trim withdrawn (owner): AFTERBURNER, FLUE_KO, NOX_SCRUB and downstream carry the cake and biogas mass; afterburner chamber sized. | 2026-10-15 |
| C | Generated from the present graph: the earlier script edited the graph once and was then retired, so the page had stopped matching the graph. The train is sized from the flows of BLACK_DIGEST; purpose and scope added; tables numbered; the record of the one-time graph edit removed | 2026-10-29 |

## 1. Purpose and scope

This page sizes the train that treats the blackwater and excreta of the occupants so that no pathogen reaches the FARM units. The train has five barriers: thermophilic digestion, incineration of the dewatered cake, pasteurisation, a standby alkaline treatment, and a batch hold that releases liquor only on a passing test. The page gives the flows of the train from the plant graph, the size and electrical load of each barrier, the treatment targets and tests, and the distance of each unit from the FARM units.

## 2. Flows

The graph carries the whole train as the one node BLACK_DIGEST.{retired} Table 2.1 lists the streams that enter it and Table 2.2 the streams that leave it.{unrated}

Table 2.1. Streams into BLACK_DIGEST

| Stream | From | Rate, kg/d |
| --- | --- | --- |
{ins}
| Sum | | {_f(r['dig_in'])} |

Table 2.2. Streams out of BLACK_DIGEST

| Stream | To | Rate, kg/d |
| --- | --- | --- |
{outs}
| Sum | | {_f(r['dig_out'])} |

The inflow and the outflow differ by {_f(abs(clos), 4)} kg/d. The streams to AFTERBURNER are the biogas ({_f(r['gas'])} kg/d) and the dewatered cake ({_f(r['cake'])} kg/d); every other stream out is released liquor, {_f(r['liquor'])} kg/d in all, and passes the pasteuriser and the hold tanks before it leaves the train.

{blk_txt}

## 3. Barriers

Table 3.1 gives the size and electrical load of each barrier.

Table 3.1. Barriers

| No. | Unit | Barrier | Condition | Design | Electrical, kW |
| --- | --- | --- | --- | --- | --- |
| 1 | BLACK_DIGEST | thermophilic anaerobic digestion | {v('san_digest_T_C'):g} °C, solids retention {v('san_digest_srt_d'):g} d [METCALF5] | {dg['V_L']:.0f} L, DN{dg['D_mm']} x {dg['H_mm']} mm, PP-H {dg['wall_mm']} mm wall, 50 mm PIR; heat {r['q_dig']:.0f} W | {_f(r['kW']['BLACK_DIGEST'])} |
| 2 | BLACK_DEWATER and AFTERBURNER | incineration of the cake | cake at {v('san_cake_TS')*100:.0f} % total solids [METCALF5], {_f(r['cake'])} kg/d in sealed bins to AFTERBURNER | screw press with 316L screen, built in house; {v(SAN+'san_press_kW'):g} kW for {v(SAN+'san_press_run_h'):g} h/d | {_f(r['kW']['BLACK_DEWATER'])} |
| 3 | BLACK_PASTEUR | pasteurisation, a process to further reduce pathogens | {v('san_past_T_C'):g} °C held for at least {v('san_past_min'):g} min (40 CFR 503 appendix B, [EPA503]) | 2 batch vessels of {ps['V_L']:.1f} L, DN{ps['D_mm']}, 316L, {v('san_past_batches_d')} batches a day; two independent temperature sensors; the hold timer restarts below the set point; heat {r['q_past']:.0f} W from an inlet at {r['T_in']:g} °C | {_f(r['kW']['BLACK_PASTEUR'])} |
| 4 | BLACK_ALK_HOLD | alkaline treatment, on standby | NaOH from BMED_BASE to pH above 12 for 72 h (40 CFR 503.32(a)(4), [EPA503]); run on any pasteuriser excursion or failed test; {_f(r['naoh'])} kg/d of NaOH when it runs | dosing pump and pH probe on each hold tank | {_f(r['kW']['BLACK_ALK_HOLD'])} |
| 5 | BLACK_ALK_HOLD | batch hold and release on test | {r['tanks']} tanks of {hd['V_L']:.0f} L, one filling, one holding and under test, one releasing, on a {v('san_hold_d'):g} d cycle; the release valve is interlocked to a passing result | HDPE, {hd['wall_mm']} mm wall, DN{hd['D_mm']} | — |

{sf_txt}

The alkaline barrier uses NaOH from BMED_BASE, so it needs no new chemical; hypochlorite would need an on-site chlor-alkali source, which the plant does not have. The NaOH rate is zero in normal operation, so the graph carries no stream for it.

## 4. Afterburner check

The cake and the biogas are burned in AFTERBURNER. Its feed on the graph is {_f(ab['feed_kg_d'])} kg/d and its flue {_f(ab['flue_kg_d'])} kg/d. A chamber that holds the flue at {v(SAN+'san_ab_T_C'):g} °C for {v(SAN+'san_ab_residence_s'):g} s [EU_IED2010] needs {ab['V_L']:.2f} L; with a length of at most {v(SAN+'san_ab_LD'):g} diameters this is an inside diameter of {ab['D_mm']} mm and a length of {ab['L_mm']} mm.

## 5. Targets and verification

Table 5.1 gives the reduction that the whole train must show for each group of organisms, and the test for each.

Table 5.1. Treatment targets

| Organism group (indicator) | Target, whole train | Basis | Test |
| --- | --- | --- | --- |
| Bacteria (E. coli) | at least 6 log | [ISO30500] | Standard Methods 9223 B on the feed and the released liquor |
| Viruses (MS2 coliphage) | at least 7 log | [ISO30500] | EPA Method 1602 on a spiked challenge |
| Protozoa (C. perfringens spores) | at least 6 log | [ISO30500] | ISO 14189 on a spiked challenge |
| Helminths (Ascaris suum eggs) | at least 4 log | [ISO30500] | EPA/625/R-92/013 appendix I on a spiked challenge |
| Released liquor and cake | faecal coliform below 1000 MPN/g TS or Salmonella below 3 MPN/4 g TS; below 1 helminth egg/g TS | [EPA503] Class A; [WHO2006_V4] | EPA 1680 or 1682 on each batch before release |

No reduction is credited to a single barrier. The pasteuriser alone must show the full ISO 30500 reduction in the challenge test, because it is the step that further reduces pathogens; digestion, the alkaline treatment and the release test are independent extra barriers. The cake is burned and never released. At commissioning, the challenge test is run on three consecutive batches. In operation, E. coli and faecal coliform are tested on every batch and the full panel each quarter (A-M-118).

## 6. Separation from FARM

The train sits in a sanitation room with 1 h fire-rated walls on the west wall of the habitation. The room has its own exhaust and is held at a lower pressure than the habitation corridor, which is in turn at a lower pressure than FARM. Its drains serve only the room and share no trap or vent with FARM. Released liquor reaches the FARM units only through the interlocked release valve. Table 6.1 gives the distance from each unit of the train to the nearest FARM unit, from the placement files.

Table 6.1. Distance from the nearest FARM unit

| Unit | Nearest FARM unit | Edge distance, m | At least {v('san_farm_sep_m')} m |
| --- | --- | --- | --- |
{seprows}
"""
    open(OUT, 'w').write(md)

def main():
    d = DR.load(); g = json.load(open(GP)); r = design(d, g)
    if '--write' in sys.argv: write_doc(d, r, sep(d))
    for k, x in r.items():
        if k in ('ins', 'outs'): continue
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in x.items()} if isinstance(x, dict) else (round(x, 4) if isinstance(x, float) else x))

if __name__ == '__main__': main()
