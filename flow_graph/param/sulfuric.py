"""Sulfuric acid for the HF kiln made on site (owner decision t59u: no imports except waste or raw ore; A-M-421).

HF_GEN takes 98 wt% sulfuric acid at its fluoro_train demand and leaves an anhydrite cake. The new unit ACID_PLANT makes
that acid. Two routes of different technology can be selected with the driver h2so4_route:
- GYPSUM_LOOP (default): the kiln cake is reduced with plant char in a small kiln, CaSO4 + 1/2 C -> CaO + SO2 + 1/2 CO2
  (reductive decomposition), recovering caso4_dec_frac of its sulfur. The sulfur not recovered is made up with native
  sulfur, a raw ore taken at the dock and burned, S + O2 -> SO2. The lime residue, with the unreacted cake, is
  exported at the dock as a byproduct.
- SULFUR_ORE: all the sulfur is native sulfur ore burned to SO2; the cake is exported at the dock as before.
On either route the SO2 is oxidised on a vanadium catalyst, SO2 + 1/2 O2 -> SO3, and absorbed in water to H2SO4 (contact
process). Oxygen comes from air drawn through the plant (ATMOS), water from the well (GW_INTAKE). The kiln load is its
insulated-shell loss plus the reaction and feed heat; the contact steps are exothermic and are not credited.

Process basis ULLMANN_H2SO4. Called from flow_graph/param/fluoro_train.py apply() after the HF kiln is rated.
Run: python3 -m flow_graph.param.sulfuric"""
import json
from . import drivers as DR

TAG = 'X-PAR-02 TF: on-site sulfuric acid (A-M-421)'
FP = 'POLYMERS.fluoropolymer-train.'
M_S, M_O2, M_C, M_CO2, M_H2O, M_CAO, M_CAF2 = 32.06, 31.998, 12.011, 44.009, 18.015, 56.077, 78.074
M_H2SO4, M_CASO4 = M_S + 1.5*M_O2 + M_H2O, M_CAO + M_S + 1.5*M_O2   # built from the same parts so the balances close exactly
ROUTES = ('GYPSUM_LOOP', 'SULFUR_ORE')

def design(acid_soln, caf2_conv, cake, d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('h2so4_route')
    if route not in ROUTES:
        raise SystemExit(f'sulfuric: h2so4_route {route!r} is not one of {ROUTES}')
    wt = v(FP + 'H2SO4_wt'); n_acid = acid_soln*wt/M_H2SO4; water_dil = acid_soln*(1 - wt)
    anh = caf2_conv*M_CASO4/M_CAF2
    n_dec = anh*v('caso4_dec_frac')/M_CASO4 if route == 'GYPSUM_LOOP' else 0.0
    n_dec = min(n_dec, n_acid)                                    # never more SO2 than the acid needs
    n_s = n_acid - n_dec                                          # sulfur ore make-up, kmol-equivalent per day
    fc = v('char_fixed_C_frac'); c = 0.5*n_dec*M_C; char = c/fc
    co2 = 0.5*n_dec*M_CO2 + char*(1 - fc)                         # char volatiles and ash leave with the kiln gas (A-M-420 basis)
    cao = n_dec*M_CAO
    residue = (cake - n_dec*M_CASO4 + cao) if route == 'GYPSUM_LOOP' else 0.0
    ship = cake if route == 'SULFUR_ORE' else 0.0
    sulfur = n_s*M_S
    o2 = n_s*M_O2 + 0.5*n_acid*M_O2                               # sulfur burning + SO2 oxidation
    h2o = n_acid*M_H2O + water_dil
    feed_in = (cake if route == 'GYPSUM_LOOP' else 0.0) + char + o2 + h2o + sulfur
    assert abs(feed_in - acid_soln - residue - co2) < 1e-9, (feed_in, acid_soln + residue + co2)
    from .sizing import heat as HT
    kw = 0.0
    if n_dec > 0:
        T = v('caso4_kiln_T_C'); _, loss = HT.insulated_cylinder(T, v('caso4_kiln_D_mm'), v('caso4_kiln_L_m'))
        q_rxn = n_dec*1000*v('caso4_dHrxn_kJ_mol')/86400*1000         # kmol/d x 1000 mol/kmol x kJ/mol = kJ/d, / 86400 s = kW, x 1000 = W
        q_sens = (cake + char)*v('caso4_feed_cp_kJ_kgK')*(T - 25)/86400*1000
        kw = (loss + q_rxn + q_sens)/1000
    return dict(route=route, acid_kg_d=acid_soln, n_acid=n_acid, sulfur_kg_d=sulfur, char_kg_d=char, o2_kg_d=o2, h2o_kg_d=h2o,
                cake_kg_d=cake if route == 'GYPSUM_LOOP' else 0.0, residue_kg_d=residue, ship_kg_d=ship, co2_kg_d=co2,
                s_recovered_frac=n_dec/n_acid if n_acid else 0.0, kw=kw)

STREAMS = (('IA-SULFUR-MU', 'NORTH_DOCK', 'ACID_PLANT', 'native sulfur (raw ore) for the acid plant', 'S', {'S': 1.0}, 'sulfur_kg_d'),
           ('IA-GYPSUM-REGEN', 'HF_GEN', 'ACID_PLANT', 'HF kiln anhydrite cake to the sulfur-recovery kiln', 'S', {'CaSO4': 1.0}, 'cake_kg_d'),
           ('CHAR_TO_ACID', 'OIL_PYRO', 'ACID_PLANT', 'plant pyrolysis char reductant for the cake kiln', 'S', {'C': 1.0}, 'char_kg_d'),
           ('IA-ACID-O2', 'ATMOS', 'ACID_PLANT', 'oxygen of the process air (sulfur burning and SO2 oxidation)', 'G', {'O2': 1.0}, 'o2_kg_d'),
           ('IA-ACID-H2O', 'GW_INTAKE', 'ACID_PLANT', 'well water for SO3 absorption and dilution to 98 wt%', 'L', {'H2O': 1.0}, 'h2o_kg_d'),
           ('IA-ACID-CO2', 'ACID_PLANT', 'ATMOS', 'carbon dioxide of the cake kiln', 'G', {'CO2': 1.0}, 'co2_kg_d'),
           ('IA-LIME-SHIP', 'ACID_PLANT', 'NORTH_DOCK', 'lime residue byproduct of the cake kiln', 'S', {'CaO': 1.0}, 'residue_kg_d'),
           ('IA-H2SO4-ACID', 'ACID_PLANT', 'HF_GEN', '98 wt% sulfuric acid to the HF kiln', 'L', {'H2SO4': 1.0}, 'acid_kg_d'))

def tf(g, E, r_fluoro, d=None):
    from flow_graph.param.o2_close import _edge, _node
    r = design(r_fluoro['acid_soln'], r_fluoro['caf2_conv'], r_fluoro['cake'], d)
    N = {n['unit_id']: n for n in g['nodes']}
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
    E['IA-GYPSUM-SHIP']['presence'] = 'present' if r['ship_kg_d'] > 0 else 'retired'
    E['IA-GYPSUM-SHIP']['rate'] = {'value': round(r['ship_kg_d'], 6), 'unit': 'kg/d', 'status': 'study',
        'note': f"{TAG}: the HF kiln cake is exported only on the SULFUR_ORE route; on GYPSUM_LOOP it goes to ACID_PLANT on IA-GYPSUM-REGEN (route {r['route']})."}
    imp = E.get('IA-H2SO4-MU')
    if imp is not None:
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). The acid is made on site by ACID_PLANT (A-M-421).'}
    note = f"{TAG}: cake kiln shell loss + reaction + feed heat (sulfuric.py, route {r['route']})."
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
