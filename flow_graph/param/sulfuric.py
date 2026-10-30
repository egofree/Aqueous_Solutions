"""Sulfuric acid for the HF kiln made on site (owner decision t59u: no imports except waste or raw ore; A-M-421).

HF_GEN takes 98 wt% sulfuric acid at its fluoro_train demand and leaves an anhydrite cake. The new unit ACID_PLANT makes
that acid. Two routes of different technology can be selected with the driver h2so4_route:
- GYPSUM_LOOP (default): the kiln cake, anhydrite and the free acid of the stoichiometric excess, is reduced with plant
  char in a small kiln, CaSO4 + 1/2 C -> CaO + SO2 + 1/2 CO2 (reductive decomposition), recovering caso4_dec_frac of all
  the acid sulfur first (owner rule t61u, A-M-423). Only the sulfur not recovered is topped up with native sulfur, a raw
  ore taken at the dock and burned, S + O2 -> SO2. The lime of the residue is the lime make-up of NAOH_PLANT
  (IA-LIME-TO-NAOH); the rest of the residue is exported at the dock.
- SULFUR_ORE: all the sulfur is native sulfur ore burned to SO2 and the cake is exported at the dock. It recovers no
  sulfur, so the recovery-first check (flow_graph/param/recovery.py) flags it while it is selected.
On either route the SO2 is oxidised on a vanadium catalyst, SO2 + 1/2 O2 -> SO3, and absorbed in water to H2SO4 (contact
process). Oxygen comes from air drawn through the plant (ATMOS), water from the well (GW_INTAKE). The kiln load is its
insulated-shell loss plus the reaction and feed heat; the contact steps are exothermic and are not credited. The kiln
runs in campaigns from a cake store by default (driver acid_kiln_mode, Q-034, A-M-425): the shell loss is nearly all of
its load at this throughput, so firing one run every acid_kiln_campaign_d days and holding the acid in a store cuts the
average load; CONTINUOUS duty is selectable.

Process basis ULLMANN_H2SO4. Called from flow_graph/param/fluoro_train.py apply() after the HF kiln is rated.
Run: python3 -m flow_graph.param.sulfuric"""
import json
from . import drivers as DR

TAG = 'X-PAR-02 TF: on-site sulfuric acid (A-M-421)'
FP = 'POLYMERS.fluoropolymer-train.'
M_S, M_O2, M_C, M_CO2, M_H2O, M_CAO, M_CAF2 = 32.06, 31.998, 12.011, 44.009, 18.015, 56.077, 78.074
M_H2SO4, M_CASO4 = M_S + 1.5*M_O2 + M_H2O, M_CAO + M_S + 1.5*M_O2   # built from the same parts so the balances close exactly
ROUTES = ('GYPSUM_LOOP', 'SULFUR_ORE')

KILN_MODES = ('CAMPAIGN', 'CONTINUOUS')

def _duty(d, T, loss_W, proc_W, feed_kg_d, acid_kg_d):
    """Cake-kiln duty (Q-034, A-M-425). On CONTINUOUS the kiln is held at T every day and draws its shell loss plus the
    process heat. On CAMPAIGN the cake is stored and fired in one run of acid_kiln_run_h every acid_kiln_campaign_d days:
    each run pays the heat-up of the tube and its fibre insulation (insulation taken to its mean temperature) and the
    shell loss for the run only, and the process heat is the same per kg. The acid for the HF kiln is held in a store
    sized for one campaign. Returns the daily average and peak loads in kW and the store sizes."""
    v = lambda k: DR.val(d, k); mode = v('acid_kiln_mode')
    if mode not in KILN_MODES:
        raise SystemExit(f'sulfuric: acid_kiln_mode {mode!r} is not one of {KILN_MODES}')
    import math
    from .sizing import heat as HT
    thk = HT.insulated_cylinder(T, v('caso4_kiln_D_mm'), v('caso4_kiln_L_m'))[0]
    D = v('caso4_kiln_D_mm')/1000; L = v('caso4_kiln_L_m'); t = v('caso4_kiln_wall_mm')/1000; ti = thk/1000
    m_tube = math.pi*(D + t)*t*L*v('inconel600_rho_kg_m3')
    m_fibre = math.pi/4*((D + 2*t + 2*ti)**2 - (D + 2*t)**2)*L*v('kiln_fibre_rho_kg_m3')
    heatup_kJ = m_tube*v('inconel600_cp_kJ_kgK')*(T - 25) + m_fibre*v('kiln_fibre_cp_kJ_kgK')*((T + 25)/2 - 25)
    N = v('acid_kiln_campaign_d') if mode == 'CAMPAIGN' else 1; run_h = v('acid_kiln_run_h') if mode == 'CAMPAIGN' else 24.0
    if mode == 'CAMPAIGN':
        loss_kWh = loss_W/1000*run_h; kw_avg = (heatup_kJ/3600 + loss_kWh)/(N*24) + proc_W/1000
        kw_peak = loss_W/1000 + proc_W/1000*N*24/run_h
    else:
        kw_avg = (loss_W + proc_W)/1000; kw_peak = kw_avg
    kw_cont = (loss_W + proc_W)/1000
    return dict(mode=mode, campaign_d=N, run_h=run_h, insul_mm=thk, tube_kg=m_tube, fibre_kg=m_fibre, heatup_kWh=heatup_kJ/3600,
                kw_avg=kw_avg, kw_peak=kw_peak, kw_continuous=kw_cont, cake_store_kg=feed_kg_d*N, acid_store_kg=acid_kg_d*N,
                acid_store_L=acid_kg_d*N/v('acid_store_rho_kg_m3')*1000)

def design(acid_soln, caf2_conv, cake, d=None, spar=None, extra_acid=0.0):
    """Acid plant at the HF kiln demand. All the acid sulfur leaves HF_GEN in its cake, as anhydrite (one CaSO4 per CaF2
    converted) and as the free acid of the stoichiometric excess. On GYPSUM_LOOP the cake kiln reduces the fraction
    caso4_dec_frac of both with char, recovering that sulfur first (owner rule t61u); sulfur ore covers only the rest.
    spar (kg/d, optional) gives the unconverted fluorspar in the residue composition."""
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('h2so4_route')
    if route not in ROUTES:
        raise SystemExit(f'sulfuric: h2so4_route {route!r} is not one of {ROUTES}')
    wt = v(FP + 'H2SO4_wt'); n_acid = acid_soln*wt/M_H2SO4; water_dil = acid_soln*(1 - wt)
    n_anh = min(caf2_conv/M_CAF2, n_acid); n_free = n_acid - n_anh  # anhydrite and free acid in the cake, kmol/d
    f = v('caso4_dec_frac') if route == 'GYPSUM_LOOP' else 0.0
    r_anh, r_free = f*n_anh, f*n_free; n_dec = r_anh + r_free     # sulfur recovered as SO2, kmol/d
    n_x = extra_acid*wt/M_H2SO4                                   # acid for the resist sulfonation (A-M-432); its sulfur leaves in the resist
    n_s = n_acid - n_dec + n_x                                    # sulfur ore top-up, kmol/d
    fc = v('char_fixed_C_frac'); char = 0.5*n_dec*M_C/fc          # CaSO4 or H2SO4 + 1/2 C -> SO2 + 1/2 CO2 (+ CaO or H2O)
    co2 = 0.5*n_dec*M_CO2 + char*(1 - fc)                         # char volatiles and ash leave with the kiln gas (A-M-420 basis)
    vap = r_free*M_H2O                                            # water of the reduced free acid
    residue = (cake - r_anh*(M_CASO4 - M_CAO) - r_free*M_H2SO4) if route == 'GYPSUM_LOOP' else 0.0
    ship = cake if route == 'SULFUR_ORE' else 0.0
    sulfur = n_s*M_S
    o2 = n_s*M_O2 + 0.5*(n_acid + n_x)*M_O2                               # sulfur burning + SO2 oxidation
    h2o = n_acid*M_H2O + water_dil + n_x*M_H2O + extra_acid*(1 - wt)
    feed_in = (cake if route == 'GYPSUM_LOOP' else 0.0) + char + o2 + h2o + sulfur
    assert abs(feed_in - acid_soln - extra_acid - residue - co2 - vap) < 1e-9, (feed_in, acid_soln + extra_acid + residue + co2 + vap)
    from .sizing import heat as HT
    kw = 0.0
    if n_dec > 0:
        T = v('caso4_kiln_T_C'); _, loss = HT.insulated_cylinder(T, v('caso4_kiln_D_mm'), v('caso4_kiln_L_m'))
        q_rxn = n_dec*1000*v('caso4_dHrxn_kJ_mol')/86400*1000         # kmol/d x 1000 mol/kmol x kJ/mol = kJ/d, / 86400 s = kW, x 1000 = W
        q_sens = (cake + char)*v('caso4_feed_cp_kJ_kgK')*(T - 25)/86400*1000
        kw = (loss + q_rxn + q_sens)/1000
        duty = _duty(d, T, loss, q_rxn + q_sens, cake + char, acid_soln)
        kw = duty['kw_avg']
    caf2_left = max(0.0, spar*v(FP + 'fluorspar_CaF2_wt') - caf2_conv) if spar is not None else 0.0
    comp = {}
    if residue > 0:
        parts = {'CaO': r_anh*M_CAO, 'CaSO4': (n_anh - r_anh)*M_CASO4, 'H2SO4': (n_free - r_free)*M_H2SO4, 'CaF2': caf2_left}
        parts['inerts'] = max(0.0, residue - sum(parts.values()))
        comp = {k: round(x/residue, 6) for k, x in parts.items() if x > 0}
    if n_dec <= 0: duty = None
    return dict(duty=duty, route=route, acid_kg_d=acid_soln, n_acid=n_acid, sulfur_kg_d=sulfur, char_kg_d=char, o2_kg_d=o2, h2o_kg_d=h2o,
                cake_kg_d=cake if route == 'GYPSUM_LOOP' else 0.0, residue_kg_d=residue, ship_kg_d=ship, co2_kg_d=co2 + vap,
                co2_only_kg_d=co2, s_recovered_frac=n_dec/n_acid if n_acid else 0.0, kw=kw, residue_comp=comp,
                cao_kg_d=r_anh*M_CAO, caf2_left_kg_d=caf2_left,
                s_need_kg_d=(n_acid + n_x)*M_S, s_recovered_kg_d=n_dec*M_S, s_ore_kg_d=n_s*M_S,
                extra_acid_kg_d=extra_acid, s_resist_kg_d=n_x*M_S)

STREAMS = (('IA-SULFUR-MU', 'NORTH_DOCK', 'ACID_PLANT', 'native sulfur (raw ore) for the acid plant', 'S', {'S': 1.0}, 'sulfur_kg_d'),
           ('IA-GYPSUM-REGEN', 'HF_GEN', 'ACID_PLANT', 'HF kiln anhydrite cake to the sulfur-recovery kiln', 'S', {'CaSO4': 1.0}, 'cake_kg_d'),
           ('CHAR_TO_ACID', 'OIL_PYRO', 'ACID_PLANT', 'plant pyrolysis char reductant for the cake kiln', 'S', {'C': 1.0}, 'char_kg_d'),
           ('IA-ACID-O2', 'ATMOS', 'ACID_PLANT', 'oxygen of the process air (sulfur burning and SO2 oxidation)', 'G', {'O2': 1.0}, 'o2_kg_d'),
           ('IA-ACID-H2O', 'GW_INTAKE', 'ACID_PLANT', 'well water for SO3 absorption and dilution to 98 wt%', 'L', {'H2O': 1.0}, 'h2o_kg_d'),
           ('IA-ACID-CO2', 'ACID_PLANT', 'ATMOS', 'carbon dioxide and water vapour of the cake kiln', 'G', {'CO2': 1.0}, 'co2_kg_d'),
           ('IA-LIME-SHIP', 'ACID_PLANT', 'NORTH_DOCK', 'lime residue byproduct of the cake kiln', 'S', {'CaO': 1.0}, 'residue_kg_d'),
           ('IA-H2SO4-ACID', 'ACID_PLANT', 'HF_GEN', '98 wt% sulfuric acid to the HF kiln', 'L', {'H2SO4': 1.0}, 'acid_kg_d'))

def tf(g, E, r_fluoro, d=None):
    from flow_graph.param.o2_close import _edge, _node
    xa = E.get('IA-RESIST-ACID'); xa = float(xa['rate']['value'] or 0) if xa is not None and xa.get('presence') != 'retired' else 0.0
    r = design(r_fluoro['acid_soln'], r_fluoro['caf2_conv'], r_fluoro['cake'], d, spar=r_fluoro['spar'], extra_acid=xa)
    N = {n['unit_id']: n for n in g['nodes']}
    lt = E.get('IA-LIME-TO-NAOH'); draw = float(lt['rate']['value'] or 0) if lt is not None and lt.get('presence') != 'retired' else 0.0
    assert draw <= r['residue_kg_d'] + 1e-9, (draw, r['residue_kg_d'])
    r['draw_kg_d'] = draw; r['ship_residue_kg_d'] = r['residue_kg_d'] - draw          # NAOH_PLANT takes its lime make-up from the residue first
    if 'ACID_PLANT' not in N:
        n = _node('ACID_PLANT', N['HF_GEN']['sector_id'], 'reactor', None, 'Sulfuric acid plant (A-M-421).', {})
        n['notes'] = 'Sulfuric acid plant: cake kiln and sulfur burner, contact converter and absorber (A-M-421).'
        g['nodes'].append(n); N['ACID_PLANT'] = n
    for sid, a, b, carries, ph, comp, key in STREAMS:
        note = f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.4f} kg/d (sulfuric.py, route {r['route']})."
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        unused = r[key] == 0 and key in ('cake_kg_d', 'char_kg_d', 'residue_kg_d', 'co2_kg_d')   # cake-loop routes on the SULFUR_ORE route
        e.update(from_unit_id=a, to_unit_id=b, carries=carries, presence='retired' if unused else 'present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    E['IA-LIME-SHIP']['rate'] = {'value': round(r['ship_residue_kg_d'], 6), 'unit': 'kg/d', 'status': 'study',
        'note': f"{TAG}: cake-kiln residue {r['residue_kg_d']:.4f} kg/d less the lime make-up of NAOH_PLANT on IA-LIME-TO-NAOH {draw:.4f} kg/d (route {r['route']})."}
    E['IA-LIME-SHIP']['presence'] = 'present' if r['ship_residue_kg_d'] > 0 else 'retired'
    E['IA-LIME-SHIP']['carries'] = 'cake-kiln residue (lime, unreacted anhydrite and fluorspar) beyond the NAOH_PLANT lime make-up'
    if r['residue_comp']:
        E['IA-LIME-SHIP']['composition'] = dict(r['residue_comp'])
    if r['co2_kg_d'] > 0:
        E['IA-ACID-CO2']['composition'] = {'CO2': round(r['co2_only_kg_d']/r['co2_kg_d'], 6), 'water': round(1 - r['co2_only_kg_d']/r['co2_kg_d'], 6)}
    # recovery-first records (owner rule t61u, A-M-423; checked by flow_graph/param/recovery.py)
    split = (lambda kg: [(sid, kg*x) for sid, x in (('IA-LIME-SHIP', r['ship_residue_kg_d']), ('IA-NAOH-RESIDUE', draw)) if x > 0]) \
        if r['route'] == 'GYPSUM_LOOP' else (lambda kg: [('IA-GYPSUM-SHIP', kg)])
    tot = r['residue_kg_d'] if r['route'] == 'GYPSUM_LOOP' else 1.0
    s_rec = dict(element='S', use='sulfuric acid for the HF kiln and the resist', need_kg_d=r['s_need_kg_d'], recovered_kg_d=r['s_recovered_kg_d'],
                 recovered_from=['IA-GYPSUM-REGEN'] if r['s_recovered_kg_d'] > 0 else [], ore_streams=['IA-SULFUR-MU'],
                 unrecovered=[dict(stream=sid, kg_d=round(kg/tot, 6), recoverable=r['route'] != 'GYPSUM_LOOP',
                                   basis=('cake-kiln non-conversion (caso4_dec_frac) leaves with the residue' if r['route'] == 'GYPSUM_LOOP'
                                          else 'SULFUR_ORE ships the cake: its sulfur is recoverable on GYPSUM_LOOP'))
                              for sid, kg in split(r['s_need_kg_d'] - r['s_recovered_kg_d'] - r['s_resist_kg_d'])]
                             + ([dict(stream='IA-RESIST-ACID', kg_d=round(r['s_resist_kg_d'], 6), recoverable=False,
                                      basis='sulfur bound in the photoresist ester; it leaves the still bottoms with the oil cut (A-M-432)')] if r['s_resist_kg_d'] > 0 else []))
    N['ACID_PLANT'].setdefault('params', {})['recovery'] = [s_rec]
    M_HF, M_F = 20.006, 18.998
    f_left = r['caf2_left_kg_d']*2*M_F/M_CAF2
    f_rec = dict(element='F', use='HF kiln', need_kg_d=r_fluoro['hf_prod']*M_F/M_HF + f_left,
                 recovered_kg_d=r_fluoro['conc']*M_F/M_HF, recovered_from=['F_RECOVER_TO_HF_GEN'], ore_streams=['IA-CAF2-MU'],
                 unrecovered=[dict(stream=sid, kg_d=round(kg/tot, 6), recoverable=False,
                                   basis='fluorspar the HF kiln does not convert (hf_kiln.CaF2_conversion) leaves with the cake')
                              for sid, kg in split(f_left)])
    N['HF_GEN'].setdefault('params', {})['recovery'] = [f_rec]
    E['IA-GYPSUM-SHIP']['presence'] = 'present' if r['ship_kg_d'] > 0 else 'retired'
    E['IA-GYPSUM-SHIP']['rate'] = {'value': round(r['ship_kg_d'], 6), 'unit': 'kg/d', 'status': 'study',
        'note': f"{TAG}: the HF kiln cake is exported only on the SULFUR_ORE route; on GYPSUM_LOOP it goes to ACID_PLANT on IA-GYPSUM-REGEN (route {r['route']})."}
    imp = E.get('IA-H2SO4-MU')
    if imp is not None:
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). The acid is made on site by ACID_PLANT (A-M-421).'}
    note = f"{TAG}: cake kiln shell loss + reaction + feed heat (sulfuric.py, route {r['route']})."
    if r['duty']:
        u = r['duty']
        note = (f"{TAG}: cake kiln on {u['mode']} duty (Q-034, A-M-425): daily average of shell loss + reaction + feed heat"
                + (f" with one {u['run_h']:g} h run every {u['campaign_d']:g} d and {u['heatup_kWh']:.2f} kWh heat-up per run; peak {u['kw_peak']:.4f} kW"
                   if u['mode'] == 'CAMPAIGN' else '') + f" (sulfuric.py, route {r['route']}).")
        N['ACID_PLANT'].setdefault('params', {})['kiln_duty'] = {k: (round(x, 4) if isinstance(x, float) else x) for k, x in u.items()}
    N['ACID_PLANT']['continuous_kw'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study', 'note': note}
    if 'SF-ACID_PLANT' not in E:
        e = _edge('SF-ACID_PLANT', 'SOL_ARK_60K', 'ACID_PLANT', 'E', ['elec'], '480 V AC', r['kw'], 'kW', N['SOL_ARK_60K']['sector_id'], N['ACID_PLANT']['sector_id'], None, note)
        e['header'] = 'tray'; g['edges'].append(e); E['SF-ACID_PLANT'] = e
    E['SF-ACID_PLANT']['rate'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to ACID_PLANT continuous_kw.'}
    return r

if __name__ == '__main__':
    from flow_graph.param import fluoro_train
    rf = fluoro_train.solve()
    print(json.dumps({k: (round(x, 5) if isinstance(x, float) else x) for k, x in design(rf['acid_soln'], rf['caf2_conv'], rf['cake']).items()}))
