"""Sodium hydroxide make-up made on site, recovery first (owner decisions t59u and t61u; A-M-422).

The NaOH balance of flow_graph/param/solver.py leaves a make-up of sodium hydroxide that BMED_BASE cannot cover, because
the make-up sodium leaves the leach as sodium chloride on IA-NA-PURGE. Under the recovery-first rule (t61u) the new unit
NAOH_PLANT first recovers that sodium: membrane chlor-alkali cells split the fraction na_purge_recycle_frac of the purge
salt (IA-NA-RECYCLE), 2 NaCl + 2 H2O -> 2 NaOH + Cl2 + H2. The rest of the purge is bled to the dock to carry the
impurities out, and only that shortfall is topped up from a sodium ore taken at the dock, by one of two routes of
different technology selected with the driver naoh_route:
- CAUSTICIZE (default): trona ore (Na2CO3.NaHCO3.2H2O) is calcined to soda ash, 2 trona -> 3 Na2CO3 + CO2 + 5 H2O, and
  causticised with slaked lime, Na2CO3 + Ca(OH)2 -> 2 NaOH + CaCO3. The lime mud is recalcined in an electrically
  heated kiln, CaCO3 -> CaO + CO2, as in a kraft-mill lime cycle; the fraction lime_purge_frac of the mud is purged to
  the dock and made up with limestone ore. Unreacted soda ash in the white liquor is recycled inside the unit.
- CHLOR_ALKALI: halite ore re-saturates the cell brine, so the same cells make the top-up.
The cell chlorine is shipped at the dock with the plant's chlorine export, and the cell hydrogen goes to the H2 header the
way the electrowinning cells' hydrogen does. The liquor goes to EVAP_BASE at its mixed strength, and the evaporator
removes its water; solver.py takes that strength from product_wt(). Water comes from the well (GW_INTAKE), the kiln gases
leave to ATMOS, and ore insolubles with the lime-mud purge leave at the dock. Kiln shell losses come from
flow_graph/param/sizing/heat.py.

Process basis ULLMANN_NAOH (causticising and the membrane cell). Called from flow_graph/param/write_graph.py process().
Run: python3 -m flow_graph.param.caustic"""
import json
from . import drivers as DR

TAG = 'X-PAR-06 TF: on-site sodium hydroxide (A-M-422)'
M_NA, M_CL, M_H, M_O, M_C, M_CA = 22.990, 35.453, 1.008, 15.999, 12.011, 40.078
M_NAOH = M_NA + M_O + M_H
M_H2O = 2*M_H + M_O
M_CO2 = M_C + 2*M_O
M_NA2CO3 = 2*M_NA + M_C + 3*M_O
M_TRONA = M_NA2CO3 + (M_NA + M_H + M_C + 3*M_O) + 2*M_H2O       # Na2CO3.NaHCO3.2H2O
M_CACO3 = M_CA + M_C + 3*M_O
M_NACL = M_NA + M_CL
F = 96485.33212
ROUTES = ('CAUSTICIZE', 'CHLOR_ALKALI')

def _route(d):
    r = DR.val(d, 'naoh_route')
    if r not in ROUTES:
        raise SystemExit(f'caustic: naoh_route {r!r} is not one of {ROUTES}')
    return r

def product_wt(d=None):
    """Mixed NaOH strength of the make-up liquor: recovered part as catholyte, top-up at the strength of its route."""
    d = d or DR.load(); f = DR.val(d, 'na_purge_recycle_frac'); wc = DR.val(d, 'ca_catholyte_wt')
    wt = DR.val(d, 'caus_liquor_wt') if _route(d) == 'CAUSTICIZE' else wc
    return 1/(f/wc + (1 - f)/wt)

def _shell_W(d, pre):
    from .sizing import heat as HT
    return HT.insulated_cylinder(DR.val(d, pre + '_T_C'), DR.val(d, pre + '_D_mm'), DR.val(d, pre + '_L_m'))[1]

def design(naoh_mol_d, d=None):
    """naoh_mol_d: the NaOH make-up of solver.naoh_balance, mol/d. Returns the stream rates in kg/d, the load in kW and
    the sodium recovery record (recovered from waste first, ore only for the shortfall)."""
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = _route(d); wc = v('ca_catholyte_wt')
    n = naoh_mol_d/1000                                            # kmol/d
    rec = n*v('na_purge_recycle_frac'); top = n - rec              # recovered from the purge salt; ore shortfall
    naoh = n*M_NAOH
    z = dict(trona_ore_kg_d=0.0, limestone_ore_kg_d=0.0, halite_ore_kg_d=0.0, recycle_kg_d=rec*M_NACL, purge_kg_d=n*M_NACL,
             bleed_kg_d=top*M_NACL, vent_kg_d=0.0, vent_co2_kg_d=0.0, residue_kg_d=0.0)
    cell = rec; kw_kiln = 0.0
    if route == 'CAUSTICIZE':
        n_sa = top/2; n_tr = n_sa/1.5; n_ca = n_sa
        trona = n_tr*M_TRONA; p = v('lime_purge_frac'); ls = p*n_ca*M_CACO3
        z['trona_ore_kg_d'] = trona/v('trona_ore_purity'); z['limestone_ore_kg_d'] = ls/v('limestone_ore_purity')
        z['vent_co2_kg_d'] = 0.5*n_tr*M_CO2 + n_ca*M_CO2          # trona calciner + lime kiln (mud and limestone)
        z['vent_kg_d'] = z['vent_co2_kg_d'] + 2.5*n_tr*M_H2O
        z['residue_kg_d'] = p*n_ca*M_CACO3 + (z['trona_ore_kg_d'] - trona) + (z['limestone_ore_kg_d'] - ls)
        if top > 0:
            q_tr = n_tr*1000*v('trona_dH_kJ_mol')/86.4 + z['trona_ore_kg_d']*v('caus_feed_cp_kJ_kgK')*(v('trona_calc_T_C') - 25)/86.4
            q_lk = n_ca*1000*v('caco3_dH_kJ_mol')/86.4 + n_ca*M_CACO3*v('caus_feed_cp_kJ_kgK')*(v('lime_kiln_T_C') - 25)/86.4
            kw_kiln = (q_tr + q_lk + _shell_W(d, 'trona_calc') + _shell_W(d, 'lime_kiln'))/1000   # W -> kW
        liquor = rec*M_NAOH/wc + top*M_NAOH/v('caus_liquor_wt')
    else:
        hal = top*M_NACL; z['halite_ore_kg_d'] = hal/v('halite_ore_purity'); z['residue_kg_d'] = z['halite_ore_kg_d'] - hal
        cell = n; liquor = naoh/wc
    z['cl2_kg_d'] = cell*M_CL; z['h2_kg_d'] = cell*M_H
    dc_kWh_kg = v('ca_cell_V')*F/(M_NAOH/1000*v('ca_CE'))/3.6e6      # V x F / (M x CE), J/kg -> kWh/kg
    kw_cell = cell*M_NAOH*dc_kWh_kg/24/v('rect_efficiency')
    z.update(route=route, naoh_kg_d=naoh, product_wt=naoh/liquor if liquor else product_wt(d), liquor_kg_d=liquor,
             kw=kw_cell + kw_kiln, kw_cell=kw_cell, kw_kiln=kw_kiln)
    assert abs(z['product_wt'] - product_wt(d)) < 1e-12
    ins = z['trona_ore_kg_d'] + z['limestone_ore_kg_d'] + z['halite_ore_kg_d'] + z['recycle_kg_d']
    outs = liquor + z['cl2_kg_d'] + z['h2_kg_d'] + z['vent_kg_d'] + z['residue_kg_d']
    z['h2o_kg_d'] = outs - ins                                     # well water closes the unit (absorbed in the liquor, the slaker and the cell)
    # net reactions: Na2CO3 + H2O -> 2 NaOH + CO2 over the lime cycle; NaCl + H2O -> NaOH + 1/2 Cl2 + 1/2 H2 in the cell
    water_need = liquor - naoh + cell*M_H2O + (top/2*M_H2O if route == 'CAUSTICIZE' else 0.0)
    assert abs(z['h2o_kg_d'] - water_need) < 1e-9*max(1.0, liquor), (z['h2o_kg_d'], water_need)   # element balance agrees with closure
    na = lambda kmol: kmol*M_NA
    z['recovery'] = dict(element='Na', demand_kg_d=na(n), recovered_kg_d=na(rec), recovered_from=['IA-NA-PURGE'],
                         ore_kg_d=na(top), ore_streams=['IA-TRONA-MU' if route == 'CAUSTICIZE' else 'IA-HALITE-MU'],
                         unrecovered=[('IA-NA-PURGE', na(top), 'bleed of the purge salt that carries the impurities out (na_purge_recycle_frac)')])
    return z

STREAMS = (('IA-TRONA-MU', 'NORTH_DOCK', 'NAOH_PLANT', 'trona ore (raw ore) for soda ash', 'S', {'Na2CO3.NaHCO3.2H2O': 1.0}, 'trona_ore_kg_d', 'CAUSTICIZE'),
           ('IA-LIMESTONE-MU', 'NORTH_DOCK', 'NAOH_PLANT', 'limestone ore (raw ore), lime-cycle make-up', 'S', {'CaCO3': 1.0}, 'limestone_ore_kg_d', 'CAUSTICIZE'),
           ('IA-NAOH-VENT', 'NAOH_PLANT', 'ATMOS', 'carbon dioxide and water vapour of the trona calciner and lime kiln', 'G', {'CO2': 1.0}, 'vent_kg_d', 'CAUSTICIZE'),
           ('IA-HALITE-MU', 'NORTH_DOCK', 'NAOH_PLANT', 'halite ore (raw ore) to re-saturate the cell brine', 'S', {'NaCl': 1.0}, 'halite_ore_kg_d', 'CHLOR_ALKALI'),
           ('IA-NA-RECYCLE', 'LEACH_CSTR_1', 'NAOH_PLANT', 'sodium chloride of the leach purge recovered to the cell brine', 'L', {'NaCl': 1.0}, 'recycle_kg_d', None),
           ('IA-NAOH-CL2-SHIP', 'NAOH_PLANT', 'NORTH_DOCK', 'chlor-alkali chlorine, shipped with the chlorine export', 'G', {'Cl2': 1.0}, 'cl2_kg_d', None),
           ('IA-NAOH-H2', 'NAOH_PLANT', 'HDR_H2', 'chlor-alkali cathode hydrogen to the H2 header', 'G', {'H2': 0.98, 'water': 0.02}, 'h2_kg_d', None),
           ('IA-NAOH-H2O', 'GW_INTAKE', 'NAOH_PLANT', 'well water for the liquor, the slaker or the cell', 'L', {'H2O': 1.0}, 'h2o_kg_d', None),
           ('IA-NAOH-RESIDUE', 'NAOH_PLANT', 'NORTH_DOCK', 'ore insolubles and the lime-mud purge', 'S', {'CaCO3': 1.0}, 'residue_kg_d', None),
           ('IA-NAOH-LIQ', 'NAOH_PLANT', 'EVAP_BASE', 'sodium hydroxide liquor to the base evaporator', 'L', {'NaOH': 1.0}, 'liquor_kg_d', None))

def tf(g, E, naoh_mol_d, d=None):
    from flow_graph.param.o2_close import _edge, _node
    r = design(naoh_mol_d, d)
    N = {n['unit_id']: n for n in g['nodes']}
    if 'NAOH_PLANT' not in N:
        n = _node('NAOH_PLANT', N['EVAP_BASE']['sector_id'], 'reactor', None, 'Sodium hydroxide plant (A-M-422).', {})
        n['notes'] = 'Sodium hydroxide plant: trona calciner, causticiser and lime kiln, or membrane chlor-alkali cells (A-M-422).'
        g['nodes'].append(n); N['NAOH_PLANT'] = n
    for sid, a, b, carries, ph, comp, key, rt in STREAMS:
        note = f"{TAG}: {key.replace('_kg_d', '')} = {r[key]:.4f} kg/d (caustic.py, route {r['route']})."
        if sid in E:
            assert (E[sid]['from_unit_id'], E[sid]['to_unit_id']) == (a, b), f'caustic: {sid} already names another stream'
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(from_unit_id=a, to_unit_id=b, carries=carries, presence='retired' if (rt and rt != r['route']) or r[key] == 0 else 'present', composition=comp)
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    if r['vent_kg_d'] > 0:
        f = r['vent_co2_kg_d']/r['vent_kg_d']; E['IA-NAOH-VENT']['composition'] = {'CO2': round(f, 6), 'water': round(1 - f, 6)}
    E['IA-NAOH-LIQ']['params'] = {'NaOH_kg_d': round(r['naoh_kg_d'], 6), 'NaOH_wt': r['product_wt']}
    E['IA-NA-PURGE']['carries'] = 'sodium chloride bleed of the leach purge (impurity bleed)'
    E['IA-NA-PURGE']['rate'] = {'value': round(r['bleed_kg_d'], 6), 'unit': 'kg/d', 'status': 'study',
        'note': f"{TAG}: the make-up sodium leaves the leach as sodium chloride, one NaCl per NaOH; the fraction na_purge_recycle_frac is recovered to NAOH_PLANT on IA-NA-RECYCLE and the rest is bled here (recovery first, t61u; route {r['route']})."}
    imp = E.get('IA-NAOH-MU')
    if imp is not None:
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t59u: no imports except waste or raw ore). The make-up is made on site by NAOH_PLANT (A-M-422).'}
    why = (f"membrane cells {r['kw_cell']:.4f} kW (ca_cell_V x F / (M x ca_CE) through the rectifier)"
           + (f" + trona calciner and lime kiln {r['kw_kiln']:.4f} kW (shell loss + reaction + feed heat)" if r['route'] == 'CAUSTICIZE' else ''))
    note = f"{TAG}: {why} (caustic.py, route {r['route']})."
    N['NAOH_PLANT']['continuous_kw'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study', 'note': note}
    if 'SF-NAOH_PLANT' not in E:
        e = _edge('SF-NAOH_PLANT', 'SOL_ARK_60K', 'NAOH_PLANT', 'E', ['elec'], '480 V AC', r['kw'], 'kW', N['SOL_ARK_60K']['sector_id'], N['NAOH_PLANT']['sector_id'], None, note)
        e['header'] = 'tray'; g['edges'].append(e); E['SF-NAOH_PLANT'] = e
    E['SF-NAOH_PLANT']['rate'] = {'value': round(r['kw'], 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to NAOH_PLANT continuous_kw.'}
    return r

if __name__ == '__main__':
    from flow_graph.param import solver
    d, g, s = solver.solve()
    for rt in ROUTES:
        dd = json.loads(json.dumps(d)); dd['naoh_route']['value'] = rt
        print(json.dumps({k: (round(x, 5) if isinstance(x, float) else x) for k, x in design(s['naoh']['makeup_mol'], dd).items() if k != 'recovery'}))
