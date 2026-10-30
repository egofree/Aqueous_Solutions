"""Bench solvent made on site, recovery first (owner decisions t59u and t61u; A-M-428).

WET_BENCH draws ethanol and acetone from WS_SOLV on IA-SOLV-WB. That solvent was a dock import (IA-SOLV-MU). Under the
recovery-first rule the new unit SOLV_PLANT first recovers the spent solvent: the bench collects the fraction
solv_spent_catch_frac of the solvent it uses as a segregated spent-solvent drain (IA-SOLV-SPENT), and a batch still
returns solv_still_recovery_frac of it, redistilled to ethanol and acetone, to WS_SOLV. The still bottoms go to the
plastics oil cut (IA-SOLV-BTMS to OIL_FRAC), where they are burned with the light oil. Only the shortfall is made new,
by one of two routes of different technology selected with the driver solv_route:
- MEOH_CO (default): plant methanol from MEOH_TANK is carbonylated with the chlorinator carbon monoxide of TI_CELL,
  which was exported at the dock as fuel gas, to acetic acid, CH3OH + CO -> CH3COOH (iodide-promoted low-pressure
  carbonylation, ULLMANN_ACETIC). Part of the acid is ketonised over ceria-zirconia to acetone,
  2 CH3COOH -> (CH3)2CO + CO2 + H2O, and the rest hydrogenated to ethanol with header hydrogen,
  CH3COOH + 2 H2 -> C2H5OH + H2O (PHAM2013, ULLMANN_ETHANOL). The feeds are taken at 1/solv_cat_selectivity of
  the stoichiometric need, and the unconverted gas and the by-product carbon dioxide and water leave at the dock with the
  fuel-gas class export, as the chlorinator CO did.
- FERMENT: galley food waste is diverted from the blackwater digester; its fermentable sugar feeds an acetone-butanol-
  ethanol fermentation (JONES1986) for the acetone and a yeast fermentation (BAI2008) for the rest of the ethanol. The
  butanol joins the still bottoms to the oil cut, the fermentation gas leaves with the dock fuel-gas class export and the stillage returns to
  BLACK_DIGEST. The route is valid only while the galley waste carries enough sugar; design() stops with a message if not.
The still reboiler, the reactor heaters and the fermenter heating are electric; their loads come from the drivers below.

Called from flow_graph/param/foundry_poly.py apply() after the chlorinator CO is rated.
Run: python3 -m flow_graph.param.solvent"""
import json, math
from . import drivers as DR

TAG = 'X-RTE TF: on-site bench solvent (A-M-428)'
M_C, M_H, M_O = 12.011, 1.008, 15.999
M_ETOH = 2*M_C + 6*M_H + M_O
M_ACE = 3*M_C + 6*M_H + M_O
M_MEOH = M_C + 4*M_H + M_O
M_CO = M_C + M_O
M_H2 = 2*M_H
M_GLU = 6*M_C + 12*M_H + 6*M_O
ROUTES = ('MEOH_CO', 'FERMENT')

def _route(d):
    r = DR.val(d, 'solv_route')
    if r not in ROUTES:
        raise SystemExit(f'solvent: solv_route {r!r} is not one of {ROUTES}')
    return r

def _tank_W(V_L, T, Ta=20.0, U=0.5):
    """Loss of a small insulated tank of working volume V_L, H = 2 D, U in W/(m2 K)."""
    V = max(V_L, 1e-6)/1000; D = (2*V/math.pi)**(1/3); A = math.pi*D*2*D + math.pi*D**2/2
    return U*A*(T - Ta), D*1000

def design(bench_kg_d, galley_kg_d=None, co_avail_kg_d=None, d=None, fab_need_kg_d=0.0, fab_spent_kg_d=0.0, fab_spent_acetone_kg_d=0.0):
    """bench_kg_d: solvent drawn by WET_BENCH (IA-SOLV-WB). Returns the stream rates in kg/d, the load in kW and the
    carbon recovery record. fab_*: acetone that RESIST_SYN and the fab rinse draw from WS_SOLV, and the spent resist and
    acetone that returns on IA-LITHO-OUT with the acetone share recovered by the still (A-M-432)."""
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = _route(d); fa = v('solv_acetone_frac')
    spent = bench_kg_d*v('solv_spent_catch_frac'); rec_b = spent*v('solv_still_recovery_frac')
    rec_f = fab_spent_acetone_kg_d*v('solv_still_recovery_frac'); rec = rec_b + rec_f
    btms = spent + fab_spent_kg_d - rec
    make = bench_kg_d + fab_need_kg_d - rec; ace = (bench_kg_d - rec_b)*fa + fab_need_kg_d - rec_f; eth = (bench_kg_d - rec_b)*(1 - fa)
    z = dict(route=route, bench_kg_d=bench_kg_d, spent_kg_d=spent, fab_need_kg_d=fab_need_kg_d, fab_spent_kg_d=fab_spent_kg_d, fab_recovered_kg_d=rec_f, recovered_kg_d=rec, make_kg_d=make, acetone_kg_d=ace, ethanol_kg_d=eth,
             meoh_kg_d=0.0, co_kg_d=0.0, h2_kg_d=0.0, fw_kg_d=0.0, stillage_kg_d=0.0, butanol_kg_d=0.0)
    kw_rx = 0.0
    if route == 'MEOH_CO':
        s = v('solv_cat_selectivity'); na = ace/M_ACE; ne = eth/M_ETOH            # kmol/d
        n_acid = 2*na + ne
        z['meoh_kg_d'] = n_acid/s*M_MEOH; z['co_kg_d'] = n_acid/s*M_CO; z['h2_kg_d'] = 2*ne/s*M_H2
        if co_avail_kg_d is not None:
            assert z['co_kg_d'] <= co_avail_kg_d + 1e-12, f"solvent: MEOH_CO needs {z['co_kg_d']:.4f} kg/d CO, TI_CELL makes {co_avail_kg_d:.4f}"
        feed = z['meoh_kg_d'] + z['co_kg_d'] + z['h2_kg_d']
        z['vent_kg_d'] = feed - make                                         # CO2 and water of the ketonisation and hydrogenation, unconverted feed
        # heaters (A-M-157 convention): feed sensible heat to the reactor temperature + methanol vaporisation, / heater efficiency
        q = (feed*v('solv_cat_cp_kJ_kgK')*(v('solv_cat_T_C') - 25) + z['meoh_kg_d']*v('meoh_dHvap_kJ_kg'))/86.4   # kJ/d -> W
        kw_rx = q/v('solv_cat_heater_eff')/1000
    else:
        ya = v('abe_acetone_yield'); sugar_abe = ace/ya
        eth_abe = sugar_abe*v('abe_ethanol_yield'); but = sugar_abe*v('abe_butanol_yield')
        eth_y = max(0.0, eth - eth_abe); sugar_y = eth_y/(2*M_ETOH/M_GLU*v('yeast_ethanol_yield_frac'))
        sugar = sugar_abe + sugar_y; fw = sugar/v('solv_fw_sugar_frac')
        if galley_kg_d is not None and fw > galley_kg_d + 1e-12:
            raise SystemExit(f'solvent: FERMENT needs {fw:.3f} kg/d of galley waste, the galley makes {galley_kg_d:.3f}; select MEOH_CO')
        gas = sugar_abe*v('abe_gas_yield') + sugar_y*(1 - 2*M_ETOH/M_GLU)*v('yeast_ethanol_yield_frac')
        z.update(fw_kg_d=fw, butanol_kg_d=but, vent_kg_d=gas, eth_extra_kg_d=max(0.0, eth_abe - eth))
        z['stillage_kg_d'] = fw - make - but - gas - z['eth_extra_kg_d']
        assert z['stillage_kg_d'] >= 0, z
        btms += but + z['eth_extra_kg_d']
        V_abe = fw*sugar_abe/sugar*v('rx_abe_tau_h')/24; V_y = fw*sugar_y/sugar*v('rx_yeast_tau_h')/24 if sugar else 0.0   # L at about 1 kg/L
        W = 0.0
        for V, T in ((V_abe, v('rx_abe_T_C')), (V_y, v('rx_yeast_T_C'))):
            if V > 0: W += _tank_W(V, T)[0]
        W += fw*4.18*(max(v('rx_abe_T_C'), v('rx_yeast_T_C')) - 20)/86.4
        kw_rx = W/1000; z['fermenter_L'] = V_abe + V_y
    z['btms_kg_d'] = btms
    z['product_kg_d'] = rec + make
    # still: batch rectification of the spent solvent and of the new product, reboiler duty (R + 1) x distillate x heat of vaporisation
    dist = rec + make + (z['butanol_kg_d'] if route == 'FERMENT' else 0.0)
    kw_still = (v('solv_still_reflux') + 1)*dist*v('solv_dHvap_kJ_kg')/86.4/v('solv_still_heater_eff')/1000
    z.update(kw=kw_still + kw_rx, kw_still=kw_still, kw_rx=kw_rx)
    ins = spent + fab_spent_kg_d + z['meoh_kg_d'] + z['co_kg_d'] + z['h2_kg_d'] + z['fw_kg_d']
    outs = z['product_kg_d'] + z['btms_kg_d'] + z['vent_kg_d'] + z['stillage_kg_d']
    assert abs(ins - outs) < 1e-9, (ins, outs)
    cf = lambda kg, M, nc: kg*nc*M_C/M
    c_need = cf(bench_kg_d*fa + fab_need_kg_d, M_ACE, 3) + cf(bench_kg_d*(1 - fa), M_ETOH, 2)
    c_rec = cf(rec_b*fa + rec_f, M_ACE, 3) + cf(rec_b*(1 - fa), M_ETOH, 2)
    c_s10 = (cf(bench_kg_d*fa, M_ACE, 3) + cf(bench_kg_d*(1 - fa), M_ETOH, 2))*(1 - v('solv_spent_catch_frac'))
    z['recovery'] = dict(element='C', use='bench solvent (ethanol and acetone)', need_kg_d=c_need, recovered_kg_d=c_rec, recovered_from=['IA-SOLV-SPENT'] + (['IA-LITHO-OUT'] if rec_f > 0 else []),
                         ore_streams=[], unrecovered=[
                             dict(stream='S10', kg_d=c_s10, recoverable=False,
                                  basis='solvent that evaporates at the bench or leaves with the spent etch, outside the segregated drain (solv_spent_catch_frac)'),
                             dict(stream='IA-SOLV-BTMS', kg_d=c_need - c_rec - c_s10, recoverable=False,
                                  basis='still bottoms with the resist residue, burned with the light oil cut (solv_still_recovery_frac)')],
                         note=('the shortfall is made from plant methanol and the chlorinator CO that was exported as fuel gas' if route == 'MEOH_CO'
                               else 'the shortfall is fermented from galley food waste'))
    return z

STREAMS = (('IA-SOLV-SPENT', 'WET_BENCH', 'SOLV_PLANT', 'segregated spent solvent from the bench rinse drain', 'L', {'ethanol': 0.5, 'acetone': 0.5}, 'spent_kg_d', None),
           ('IA-SOLV-PLANT', 'SOLV_PLANT', 'WS_SOLV', 'recovered and new ethanol and acetone to the solvent store', 'L', {'ethanol': 0.5, 'acetone': 0.5}, 'product_kg_d', None),
           ('IA-SOLV-BTMS', 'SOLV_PLANT', 'OIL_FRAC', 'still bottoms (resist residue and heavy alcohols) to the light oil cut', 'L', {'hydrocarbon': 1.0}, 'btms_kg_d', None),
           ('IA-SOLV-VENT', 'SOLV_PLANT', 'NORTH_DOCK', 'reactor or fermenter off-gas (fuel-gas class export)', 'G', {'CO2': 1.0}, 'vent_kg_d', None),
           ('IA-SOLV-MEOH', 'MEOH_TANK', 'SOLV_PLANT', 'plant methanol for the carbonylation', 'L', {'CH3OH': 1.0}, 'meoh_kg_d', 'MEOH_CO'),
           ('IA-SOLV-CO', 'TI_CELL', 'SOLV_PLANT', 'chlorinator carbon monoxide for the carbonylation', 'G', {'CO': 1.0}, 'co_kg_d', 'MEOH_CO'),
           ('IA-SOLV-H2', 'HDR_H2', 'SOLV_PLANT', 'header hydrogen for the acetic acid hydrogenation', 'G', {'H2': 1.0}, 'h2_kg_d', 'MEOH_CO'),
           ('IA-SOLV-FW', 'HABITATION', 'SOLV_PLANT', 'galley food waste for the solvent fermentation', 'S', {'food waste': 1.0}, 'fw_kg_d', 'FERMENT'),
           ('IA-SOLV-STILLAGE', 'SOLV_PLANT', 'BLACK_DIGEST', 'fermentation stillage to the digester', 'L', {'water': 0.9, 'solids': 0.1}, 'stillage_kg_d', 'FERMENT'))

def _base(e, key):
    """Rate of a shared edge before this module's draw, kept in params so repeated runs do not compound."""
    return e.setdefault('params', {}).setdefault(key, float(e['rate']['value'] or 0))

def tf(g, E, d=None):
    from flow_graph.param.o2_close import _edge, _node
    d = d or DR.load()
    N = {n['unit_id']: n for n in g['nodes']}
    gal = E['IA-GAL']; co = E['IA-KROLL-CO']
    from flow_graph.param import fab_resist                              # fab resist acetone and its spent return (A-M-432)
    fr = fab_resist.design(d)
    r = design(float(E['IA-SOLV-WB']['rate']['value']), galley_kg_d=(gal.get('params') or {}).get('pre_solv_kg_d', float(gal['rate']['value'])),
               co_avail_kg_d=float(co['rate']['value']), d=d, fab_need_kg_d=round(fr['acetone_kg_d'], 6) + round(fr['rinse_kg_d'], 6),
               fab_spent_kg_d=round(fr['resist_kg_d'], 6) + round(fr['rinse_kg_d'], 6), fab_spent_acetone_kg_d=fr['rinse_kg_d'])
    if 'SOLV_PLANT' not in N:
        n = _node('SOLV_PLANT', N['WS_SOLV']['sector_id'], 'reactor', None, 'Solvent plant (A-M-428).', {})
        n['notes'] = 'Solvent plant: spent-solvent still, with carbonylation, ketonisation and hydrogenation reactors or solvent fermenters (A-M-428).'
        g['nodes'].append(n); N['SOLV_PLANT'] = n
    for sid, a, b, carries, ph, comp, key, rt in STREAMS:
        note = f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (solvent.py, route {r['route']})."
        if sid in E:
            assert (E[sid]['from_unit_id'], E[sid]['to_unit_id']) == (a, b), f'solvent: {sid} already names another stream'
        else:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(carries=carries, presence='retired' if (rt and rt != r['route']) or r[key] == 0 else 'present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    fa = DR.val(d, 'solv_acetone_frac')
    for sid in ('IA-SOLV-SPENT', 'IA-SOLV-PLANT', 'IA-SOLV-WB'):
        E[sid]['composition'] = {'ethanol': round(1 - fa, 6), 'acetone': round(fa, 6)}
    if r['route'] == 'MEOH_CO' and r['vent_kg_d'] > 0:
        E['IA-SOLV-VENT']['composition'] = {'CO2, water and unconverted CO, H2 and methanol': 1.0}
    # shared edges: the spent etch, the chlorinator CO export and the galley waste give up what SOLV_PLANT takes
    s10 = E['S10']; b = _base(s10, 'pre_solv_kg_d')
    s10['rate'] = dict(s10['rate'], value=round(b - r['spent_kg_d'], 6))
    co['rate'] = dict(co['rate'], value=round(float(co['rate']['value']) - r['co_kg_d'], 6),
                      note=co['rate']['note'] + f" Less {r['co_kg_d']:.6f} kg/d to SOLV_PLANT on IA-SOLV-CO (A-M-428).")
    if r['fw_kg_d'] > 0 or 'pre_solv_kg_d' in (gal.get('params') or {}):
        gb = _base(gal, 'pre_solv_kg_d'); gal['rate'] = dict(gal['rate'], value=round(gb - r['fw_kg_d'], 6))
    N['SOLV_PLANT'].setdefault('params', {})['recovery'] = [r['recovery']]
    N['SOLV_PLANT']['params']['design'] = {k: (round(x, 6) if isinstance(x, float) else x) for k, x in r.items() if k != 'recovery'}
    why = f"still reboiler {r['kw_still']:.5f} kW + " + ('reactor heaters' if r['route'] == 'MEOH_CO' else 'fermenter heating') + f" {r['kw_rx']:.5f} kW"
    note = f"{TAG}: {why} (solvent.py, route {r['route']})."
    N['SOLV_PLANT']['continuous_kw'] = {'value': round(r['kw'], 5), 'unit': 'kW', 'status': 'study', 'note': note}
    if 'SF-SOLV_PLANT' not in E:
        e = _edge('SF-SOLV_PLANT', 'SOL_ARK_60K', 'SOLV_PLANT', 'E', ['elec'], '480 V AC', r['kw'], 'kW', N['SOL_ARK_60K']['sector_id'], N['SOLV_PLANT']['sector_id'], None, note)
        e['header'] = 'tray'; g['edges'].append(e); E['SF-SOLV_PLANT'] = e
    E['SF-SOLV_PLANT']['rate'] = {'value': round(r['kw'], 5), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to SOLV_PLANT continuous_kw.'}
    imp = E.get('IA-SOLV-MU')
    if imp is not None:
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). SOLV_PLANT recovers the spent solvent and makes the shortfall on site (A-M-428).'}
    return r

if __name__ == '__main__':
    g = json.load(open('flow_graph/plant_flow_graph.json')); E = {e['stream_id']: e for e in g['edges']}
    d = DR.load()
    for rt in ROUTES:
        dd = json.loads(json.dumps(d)); dd['solv_route']['value'] = rt
        try:
            x = design(float(E['IA-SOLV-WB']['rate']['value']), d=dd)
            print(json.dumps({k: (round(y, 5) if isinstance(y, float) else y) for k, y in x.items() if k != 'recovery'}))
        except SystemExit as ex:
            print(rt, ex)
