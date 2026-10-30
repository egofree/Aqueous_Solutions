"""Wafer-fab photoresist made on site from plant streams, and the honest fab balance (A-M-432).

Need. The fab's chemical polymer consumable is the photoresist. Its other process polymers (PTFE and PFA wafer carriers,
PVDF wet-bench parts, seals) are formed parts made in MFG_SHOP from POLY_TO_MFG and FLUORO_TO_MFG, so they are spares and
not a direct fab draw. The resist need follows from the wafer starts of flow_graph/param/fab_silicon.py:
  coats/d          = starts x fab_mask_layers
  resist solution  = coats x fab_resist_mL_per_coat x fab_resist_rho_kg_m3           (POLY_TO_FAB, from POLY_STOCK)
  resist solids    = solution x fab_resist_solids_frac; the rest is the casting solvent
  rinse solvent    = coats x (fab_ebr_mL_per_coat + fab_strip_mL_per_coat) x acetone density   (IA-FAB-SOLV, from WS_SOLV)

Chemistry (fab_resist_route). DNQ_NOVOLAC, the positive diazonaphthoquinone-novolac class, is the one built (MOREAU1988):
it images at the 365 nm aligner and develops in the aqueous TMAH/KOH bench that LITHO_DEV already is. Every precursor is
a plant stream; RESIST_SYN makes it in small batches (stoichiometric ledger below, per mol):
  phenol      C6H6 + 1/2 O2 -> C6H5OH            Raschig-Hooker oxychlorination and hydrolysis, HCl catalytic (ULLMANN_PHENOL);
                                                  benzene extracted from the C5-C10 cut
  formaldehyde CH3OH + 1/2 O2 -> CH2O + H2O       silver or iron-molybdate oxidation in air (ULLMANN_FORMALDEHYDE); plant methanol
  novolac     C6H5OH + r CH2O -> (C6H6O + r CH2O - r H2O) + r H2O   acid-catalysed, r = novolac_fp_ratio
  1-naphthol  C10H8 + 1/2 O2 -> C10H7OH          same oxychlorination route; naphthalene extracted from the C11-C18 cut
  HNO2        NH3 + 3/2 O2 -> HNO2 + H2O         ammonia oxidation in air, absorbed as N2O3 (ULLMANN_NITRIC); WS_AMMONIA
  nitrosation C10H7OH + HNO2 -> 2-nitroso-1-naphthol + H2O
  reduction   C10H7NO2 + 2 H2 -> 2-amino-1-naphthol + H2O              header hydrogen
  sulfonation C10H9NO + H2SO4 -> C10H9NO4S + H2O                      ACID_PLANT acid
  diazotisation C10H9NO4S + HNO2 -> DNQ-5-sulfonic acid C10H6N2O4S + 2 H2O
  phosgenation C10H6N2O4S + CO + Cl2 -> DNQ-5-sulfonyl chloride + CO2 + HCl   chlorinator CO and AL_POT chlorine; the HCl
                                                  joins the dilute HCl returns to CRU, which turns it back into chlorine
  esterification DNQ-SO2Cl + novolac-OH + NH3 -> polymer-bound DNQ ester + NH4Cl
  casting solvent 2 (CH3)2CO -> diacetone alcohol (base-catalysed aldol), acetone from SOLV_PLANT
The polymer-bound DNQ moiety C10H5N2O3S is fab_resist_dnq_wt of the solids. Process air for the three oxidations is
taken at the feed strengths of practice (formox_meoh_vol_frac, ostwald_nh3_vol_frac; the oxychlorination at its
stoichiometric oxygen), and the nitrogen and unused oxygen vent. The water of reaction, the acid water and the NH4Cl
leave as a brine to the leach. The aromatic extraction returns its raffinate to OIL_FRAC.

The negative cyclised-polyisoprene / bis-azide class is not built: it develops in an organic solvent, not on the
aqueous develop bench, and its isoprene and its aromatic azide have no route on the plant. Those precursors are open
tasks X-RTE-RESIST-ISOPRENE and X-RTE-RESIST-AZIDE.

Spent resist and solvent leave the develop bench for the SOLV_PLANT still (IA-LITHO-OUT), which returns the acetone and
sends the resin and diacetone alcohol with its bottoms to the oil cut (flow_graph/param/solvent.py).

Fab balance. Before this module the S03 nitrogen purge never left WAFER_FAB: it balanced an unsourced 0.99 kg/d resist
issue and the 0.51 kg/d IA-FAB-LOSS dust line, which duplicated the kerf that fab_silicon.py already sends to the leach
on IA-FAB-KERF. The purge now vents on IA-FAB-N2-VENT at the S03 rate, IA-FAB-LOSS is retired, BAGHOUSE re-closes on
its live inputs, and the spent rinse water IA-FAB-SPENT closes the fab by difference.

Run: python3 -m flow_graph.param.fab_resist
"""
from flow_graph.param import site
import json, re
from . import drivers as DR

TAG = 'X-RTE TF: fab photoresist made on site (A-M-432)'
AW = dict(H=1.008, C=12.011, N=14.007, O=15.999, S=32.06, Cl=35.453)
ROUTES = ('DNQ_NOVOLAC',)

def _el(f):
    out = {}
    for el, n in re.findall(r'([A-Z][a-z]?)([\d.]*)', f):
        out[el] = out.get(el, 0.0) + (float(n) if n else 1.0)
    return out

def M(f):
    return sum(AW[k]*n for k, n in _el(f).items())

def design(d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('fab_resist_route')
    if route not in ROUTES:
        raise SystemExit(f'fab_resist: fab_resist_route {route!r} is not one of {ROUTES}')
    from flow_graph.param import fab_silicon
    fs = fab_silicon.design(d)
    starts = fs['wafer_kg_d']/(fs['wafer_g']/1000.0); coats = starts*v('fab_mask_layers')
    soln = coats*v('fab_resist_mL_per_coat')*1e-6*v('fab_resist_rho_kg_m3')
    solids = soln*v('fab_resist_solids_frac'); daa = soln - solids
    rinse = coats*(v('fab_ebr_mL_per_coat') + v('fab_strip_mL_per_coat'))*1e-6*v('acetone_rho_kg_m3')
    r = v('novolac_fp_ratio'); f_nov = f'C{6 + r}H6O'
    moiety = 'C10H5N2O3S'
    n_dnq = v('fab_resist_dnq_wt')*solids/M(moiety)                          # kmol/d
    n_ph = (solids - n_dnq*(M(moiety) - AW['H']))/M(f_nov)
    n_f = r*n_ph; n_daa = daa/M('C6H12O2')
    led = {}                                                                 # species -> kmol/d (+ made, - used)
    def rx(*terms):
        for c, sp in terms:
            led[sp] = led.get(sp, 0.0) + c
    rx((-n_ph, 'C6H6'), (-0.5*n_ph, 'O2'), (n_ph, 'C6H6O'))
    rx((-n_f, 'CH4O'), (-0.5*n_f, 'O2'), (n_f, 'CH2O'), (n_f, 'H2O'))
    rx((-n_ph, 'C6H6O'), (-n_f, 'CH2O'), (n_ph, f_nov), (n_f, 'H2O'))
    n = n_dnq
    rx((-n, 'C10H8'), (-0.5*n, 'O2'), (n, 'C10H8O'))
    rx((-2*n, 'NH3'), (-3*n, 'O2'), (2*n, 'HNO2'), (2*n, 'H2O'))
    rx((-n, 'C10H8O'), (-n, 'HNO2'), (n, 'C10H7NO2'), (n, 'H2O'))
    rx((-n, 'C10H7NO2'), (-2*n, 'H2'), (n, 'C10H9NO'), (n, 'H2O'))
    rx((-n, 'C10H9NO'), (-n, 'H2SO4'), (n, 'C10H9NO4S'), (n, 'H2O'))
    rx((-n, 'C10H9NO4S'), (-n, 'HNO2'), (n, 'C10H6N2O4S'), (2*n, 'H2O'))
    rx((-n, 'C10H6N2O4S'), (-n, 'CO'), (-n, 'Cl2'), (n, 'C10H5ClN2O3S'), (n, 'CO2'), (n, 'HCl'))
    rx((-n, 'C10H5ClN2O3S'), (-n, f_nov), (-n, 'NH3'), (n, 'ESTER'), (n, 'NH4Cl'))
    rx((-2*n_daa, 'C3H6O'), (n_daa, 'C6H12O2'))
    led = {k: x for k, x in led.items() if abs(x) > 1e-15}
    # element closure of the ledger: the ester unit is the novolac unit less H plus the DNQ-sulfonyl moiety
    tot = {}
    for sp, x in led.items():
        f = _el(f_nov)
        if sp == 'ESTER':
            f = dict(_el(f_nov)); f['H'] -= 1
            for k, c in _el(moiety).items(): f[k] = f.get(k, 0.0) + c
        else:
            f = _el(sp)
        for k, c in f.items(): tot[k] = tot.get(k, 0.0) + c*x
    assert all(abs(x) < 1e-12 for x in tot.values()), tot
    kg = lambda sp: abs(led.get(sp, 0.0))*M(sp)
    solids_chk = led.get(f_nov, 0.0)*M(f_nov) + led['ESTER']*(M(f_nov) - AW['H'] + M(moiety))
    assert abs(solids_chk - solids) < 1e-9*max(solids, 1e-9), (solids_chk, solids)
    # aromatic extraction from the cuts
    rec = v('aromatic_extract_recovery')
    bz_cut = kg('C6H6')/(v('oil_c5c10_benzene_frac')*rec); naph_cut = kg('C10H8')/(v('oil_c11c18_naphthalene_frac')*rec)
    raff = bz_cut - kg('C6H6') + naph_cut - kg('C10H8')
    # process air: formaldehyde and ammonia oxidation at their feed strengths, oxychlorination at stoichiometric oxygen
    yo = site.process_air_fraction('O2'); MA = yo*M('O2') + (1 - yo)*M('N2')
    y_f, y_n = v('formox_meoh_vol_frac'), v('ostwald_nh3_vol_frac')
    air_mol = n_f*(1 - y_f)/y_f + 2*n*(1 - y_n)/y_n + 0.5*(n_ph + n)/yo
    o2_in = air_mol*yo; o2_used = -led['O2']; assert o2_in >= o2_used - 1e-15
    air = air_mol*MA; vent = air - o2_used*M('O2') + kg('CO2')
    wt = v('POLYMERS.fluoropolymer-train.H2SO4_wt'); acid = kg('H2SO4')/wt
    brine = led.get('H2O', 0.0)*M('H2O') + kg('NH4Cl') + acid*(1 - wt)
    z = dict(route=route, starts_d=starts, coats_d=coats, resist_kg_d=soln, solids_kg_d=solids, daa_kg_d=daa, rinse_kg_d=rinse,
             novolac_kg_d=solids - led['ESTER']*(M(moiety) - AW['H']), dnq_kg_d=led['ESTER']*M(moiety),
             bz_cut_kg_d=bz_cut, naph_cut_kg_d=naph_cut, benzene_kg_d=kg('C6H6'), naphthalene_kg_d=kg('C10H8'), raff_kg_d=raff,
             meoh_kg_d=kg('CH4O'), nh3_kg_d=kg('NH3'), h2_kg_d=kg('H2'), co_kg_d=kg('CO'), cl2_kg_d=kg('Cl2'), acid_kg_d=acid,
             acetone_kg_d=kg('C3H6O'), air_kg_d=air, vent_kg_d=vent, hcl_kg_d=kg('HCl'), brine_kg_d=brine)
    ins = bz_cut + naph_cut + z['meoh_kg_d'] + z['nh3_kg_d'] + z['h2_kg_d'] + z['co_kg_d'] + z['cl2_kg_d'] + acid + z['acetone_kg_d'] + air
    outs = soln + raff + vent + z['hcl_kg_d'] + brine
    assert abs(ins - outs) < 1e-9*max(ins, 1e-9), (ins, outs)
    # batch heating: feeds to the reactor temperature, electric (A-M-157 convention)
    W = (ins - air)*v('resist_cp_kJ_kgK')*(v('resist_rx_T_C') - 25)/86.4/v('resist_heater_eff')
    z['kw'] = W/1000
    z['ledger_kmol_d'] = {k: x for k, x in led.items()}
    return z

STREAMS = (('IA-RESIST-BZ', 'PROD_C5_C10', 'RESIST_SYN', 'C5-C10 cut to the benzene extraction', 'L', {'C5-C10': 1.0}, 'bz_cut_kg_d'),
           ('IA-RESIST-NAPH', 'PROD_C11_C18', 'RESIST_SYN', 'C11-C18 cut to the naphthalene extraction', 'L', {'C11-C18': 1.0}, 'naph_cut_kg_d'),
           ('IA-RESIST-RAFF', 'RESIST_SYN', 'OIL_FRAC', 'aromatic-extraction raffinate back to the fractionator', 'L', {'hydrocarbon': 1.0}, 'raff_kg_d'),
           ('IA-RESIST-MEOH', 'MEOH_TANK', 'RESIST_SYN', 'plant methanol for the formaldehyde', 'L', {'CH3OH': 1.0}, 'meoh_kg_d'),
           ('IA-RESIST-NH3', 'WS_AMMONIA', 'RESIST_SYN', 'ammonia for the nitrous acid and the ester scavenger', 'L', {'NH3': 1.0}, 'nh3_kg_d'),
           ('IA-RESIST-H2', 'HDR_H2', 'RESIST_SYN', 'header hydrogen for the nitroso reduction', 'G', {'H2': 1.0}, 'h2_kg_d'),
           ('IA-RESIST-CO', 'TI_CELL', 'RESIST_SYN', 'chlorinator carbon monoxide for the phosgenation', 'G', {'CO': 1.0}, 'co_kg_d'),
           ('IA-RESIST-CL2', 'AL_POT', 'RESIST_SYN', 'pot chlorine for the phosgenation', 'G', {'Cl2': 1.0}, 'cl2_kg_d'),
           ('IA-RESIST-ACID', 'ACID_PLANT', 'RESIST_SYN', 'sulfuric acid for the naphthol sulfonation', 'L', {'H2SO4': 1.0}, 'acid_kg_d'),
           ('IA-RESIST-ACET', 'WS_SOLV', 'RESIST_SYN', 'acetone for the diacetone alcohol casting solvent', 'L', {'acetone': 1.0}, 'acetone_kg_d'),
           ('IA-RESIST-AIR', 'ATMOS', 'RESIST_SYN', 'process air for the oxidations', 'G', {'air': 1.0}, 'air_kg_d'),
           ('IA-RESIST-VENT', 'RESIST_SYN', 'ATMOS', 'oxidation off-gas: nitrogen, unused oxygen and carbon dioxide', 'G', {'N2': 1.0}, 'vent_kg_d'),
           ('IA-RESIST-HCL', 'RESIST_SYN', 'CRU', 'phosgenation HCl to the chlorate finish', 'L', {'HCl': 1.0}, 'hcl_kg_d'),
           ('IA-RESIST-BRINE', 'RESIST_SYN', 'LEACH_CSTR_1', 'reaction water, acid water and ammonium chloride', 'L', {'water': 1.0}, 'brine_kg_d'),
           ('IA-RESIST-STOCK', 'RESIST_SYN', 'POLY_STOCK', 'formulated positive photoresist to stock', 'L', {'resist': 1.0}, 'resist_kg_d'))

def _set(E, sid, v, note):
    E[sid]['rate'] = {'value': round(v, 6), 'unit': 'kg/d', 'status': 'study', 'note': note}

def tf(g, E, d=None):
    """Called from flow_graph/param/fluoro_train.py after the CRU block, so the chlorine export and CRU liquor are fresh."""
    from flow_graph.param.o2_close import _edge, _node
    d = d or DR.load(); r = design(d)
    N = {n['unit_id']: n for n in g['nodes']}
    if 'RESIST_SYN' not in N:
        n = _node('RESIST_SYN', N['WS_SOLV']['sector_id'], 'reactor', None, 'Photoresist synthesis (A-M-432).', {})
        g['nodes'].append(n); N['RESIST_SYN'] = n
    N['RESIST_SYN']['notes'] = 'Photoresist synthesis: aromatic extraction, phenol and naphthol oxychlorination, formaldehyde, novolac, diazonaphthoquinone sulfonyl ester and formulation batch reactors (A-M-432).'
    for sid, a, b, carries, ph, comp, key in STREAMS:
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, '')
            g['edges'].append(e); E[sid] = e
        E[sid].update(carries=carries, presence='present', composition=comp)
        _set(E, sid, r[key], f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (fab_resist.py, route {r['route']}).")
    E['IA-RESIST-VENT']['composition'] = {'N2': 0.75, 'O2': 0.24, 'CO2': 0.01}
    # shared edges give up what RESIST_SYN takes (each is re-rated upstream in the same pass)
    for sid, key, why in (('IA-CL2-SHIP', 'cl2_kg_d', 'IA-RESIST-CL2'), ('IA-KROLL-CO', 'co_kg_d', 'IA-RESIST-CO'), ('IA-C5-SHIP', 'bz_cut_kg_d', 'IA-RESIST-BZ')):
        e = E[sid]; e['rate'] = dict(e['rate'], value=round(float(e['rate']['value']) - r[key], 6),
                                     note=e['rate']['note'] + f' Less {r[key]:.6f} kg/d to RESIST_SYN on {why} (A-M-432).')
    _set(E, 'IA-RESIST-RAFF', round(r['bz_cut_kg_d'], 6) + round(r['naph_cut_kg_d'], 6) - round(r['benzene_kg_d'] + r['naphthalene_kg_d'], 6),
         f"{TAG}: extraction raffinate = cut drawn less the benzene and naphthalene taken.")
    e = E['IA-CRU-01']; e['rate'] = dict(e['rate'], value=round(float(e['rate']['value']) + r['hcl_kg_d'], 6),
                                         note=e['rate']['note'] + f" Plus the {r['hcl_kg_d']:.6f} kg/d phosgenation HCl of RESIST_SYN (A-M-432).")
    nh = E['IA-NH3-SRC']; b = nh.setdefault('params', {}).setdefault('pre_resist_kg_d', float(nh['rate']['value']))
    nh['rate'] = dict(nh['rate'], value=round(b + r['nh3_kg_d'], 6))
    # fab: resist and rinse issue, litho chain, nitrogen vent, honest close
    _set(E, 'POLY_TO_FAB', r['resist_kg_d'], f"{TAG}: formulated positive resist, {r['coats_d']:.0f} coats/d ({r['starts_d']:.1f} wafer starts x "
         f"{DR.val(d, 'fab_mask_layers'):g} mask layers) x {DR.val(d, 'fab_resist_mL_per_coat'):g} mL at {DR.val(d, 'fab_resist_solids_frac'):.0%} solids (MOREAU1988).")
    E['POLY_TO_FAB']['composition'] = {'novolac-DNQ resin': round(DR.val(d, 'fab_resist_solids_frac'), 6), 'diacetone alcohol': round(1 - DR.val(d, 'fab_resist_solids_frac'), 6)}
    if 'IA-FAB-SOLV' not in E:
        g['edges'].append(_edge('IA-FAB-SOLV', 'WS_SOLV', 'WAFER_FAB', 'L', ['mass'], 'acetone for edge-bead rinse and resist strip', 0, 'kg/d', 'FAB', 'FAB', {'acetone': 1.0}, '')); E['IA-FAB-SOLV'] = g['edges'][-1]
    _set(E, 'IA-FAB-SOLV', r['rinse_kg_d'], f"{TAG}: edge-bead rinse and strip acetone at the coat rate.")
    iss = round(r['resist_kg_d'], 6) + round(r['rinse_kg_d'], 6)
    for sid, w in (('IA-LITHO-IN', 'resist and rinse acetone issued to the coater'), ('IA-LITHO-CARRY', 'resist and acetone carried coat to develop'),
                   ('IA-LITHO-OUT', 'spent resist and acetone to the SOLV_PLANT still')):
        _set(E, sid, iss, f"{TAG}: {w} = POLY_TO_FAB + IA-FAB-SOLV.")
    E['IA-LITHO-OUT'].update(to_unit_id='SOLV_PLANT', to_sector_id=N['SOLV_PLANT']['sector_id'])
    if 'IA-FAB-N2-VENT' not in E:
        g['edges'].append(_edge('IA-FAB-N2-VENT', 'WAFER_FAB', 'ATMOS', 'G', ['mass'], 'fab nitrogen purge exhaust', 0, 'kg/d', 'FAB', N['ATMOS']['sector_id'], {'N2': 1.0}, '')); E['IA-FAB-N2-VENT'] = g['edges'][-1]
    _set(E, 'IA-FAB-N2-VENT', float(E['S03']['rate']['value']), f"{TAG}: the S03 nitrogen purge leaves the tools to atmosphere at its supply rate.")
    fl = E.get('IA-FAB-LOSS')
    if fl is not None:
        fl['presence'] = 'retired'
        fl['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-30 (A-M-432): the fab dust line duplicated the kerf that fab_silicon.py sends to the leach on IA-FAB-KERF, and only the unvented nitrogen purge balanced it.'}
    live = lambda e: e.get('presence') != 'retired' and 'mass' in (e.get('layers') or [])
    bag = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['to_unit_id'] == 'BAGHOUSE' and live(e))
    _set(E, 'IA-BAG-01', bag, f"{TAG}: BAGHOUSE dust to the leach = its live inputs.")
    fin = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['to_unit_id'] == 'WAFER_FAB' and live(e))
    fout = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['from_unit_id'] == 'WAFER_FAB' and live(e) and e['stream_id'] != 'IA-FAB-SPENT')
    _set(E, 'IA-FAB-SPENT', fin - fout, f"{TAG}: spent rinse water by difference on WAFER_FAB, now that the nitrogen purge vents.")
    N['RESIST_SYN'].setdefault('params', {})['design'] = {k: (round(x, 9) if isinstance(x, float) else x) for k, x in r.items() if k != 'ledger_kmol_d'}
    N['RESIST_SYN']['params']['design']['ledger_kmol_d'] = {k: round(x, 12) for k, x in r['ledger_kmol_d'].items()}
    note = f"{TAG}: batch reactor heating to {DR.val(d, 'resist_rx_T_C'):g} C (fab_resist.py)."
    N['RESIST_SYN']['continuous_kw'] = {'value': round(r['kw'], 5), 'unit': 'kW', 'status': 'study', 'note': note}
    if 'SF-RESIST_SYN' not in E:
        e = _edge('SF-RESIST_SYN', 'SOL_ARK_60K', 'RESIST_SYN', 'E', ['elec'], '480 V AC', r['kw'], 'kW', N['SOL_ARK_60K']['sector_id'], N['RESIST_SYN']['sector_id'], None, note)
        e['header'] = 'tray'; g['edges'].append(e); E['SF-RESIST_SYN'] = e
    E['SF-RESIST_SYN']['rate'] = {'value': round(r['kw'], 5), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to RESIST_SYN continuous_kw.'}
    return r

if __name__ == '__main__':
    print(json.dumps({k: (round(x, 6) if isinstance(x, float) else x) for k, x in design().items() if k != 'ledger_kmol_d'}))
