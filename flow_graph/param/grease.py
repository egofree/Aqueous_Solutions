"""Shop grease made on site from the plant's own wax cut, recovery first (owner decisions t58u and t61u; A-M-429).

The need comes from the maintenance plan: every powered rotating unit that docs-authority/_maint.py gives a lubrication
task (same rule as there) has grease_points_per_unit grease points, each relubricated every maint_rotating.lube_mo months
with the quantity Gp = 0.005 D B grams of the SKF relubrication rule (SKF_RELUB), for the bearing class of the plant's
bought bearings (grease_bearing_D_mm, grease_bearing_B_mm). MFG_SHOP issues the grease and collects the purged grease,
which goes to OIL_PYRO with the plastics feed (IA-GREASE-SPENT), so the shop balance is unchanged.

The grease is grease_soap_frac soap in the C19-C28 cut as base oil (ULLMANN_LUBRICANTS). The soap acid is made in the
kettle by air oxidation of part of the same cut to fatty acids (ULLMANN_FATTY_ACIDS): grease_wax_ox_acid_yield kg acid per
kg wax with grease_wax_ox_o2 kg oxygen from the process air (ATMOS); water, carbon dioxide and light acids leave to ATMOS.
Two thickeners of different chemistry can be selected with the driver grease_thickener:
- CA (default): calcium soap, 2 RCOOH + Ca(OH)2 -> (RCOO)2Ca + 2 H2O, in GREASE_CA. The calcium comes from waste: P_CA
  slakes the lime of the ACID_PLANT cake-kiln residue (IA-LIME-TO-PCA), CaO + H2O -> Ca(OH)2, with well water, and sends
  the rest of the residue to the dock with the residue export (IA-PCA-REJECT).
- LI: lithium soap, RCOOH + LiOH -> RCOOLi + H2O, in GREASE_LI, for a higher dropping point. The lithium comes from
  LI_RECOVER on the polish liquor, whose lithium tenor has not been measured (notes/DIGESTER_LI.md), so the LI route stands
  by: its edges carry the rate of the case that selects it (params rate_rated_kg_d) and POLISH_TO_LI waits on the tenor.
The kettle runs in campaigns every grease_campaign_d days; its load is the feed heat plus the shell loss for the run
(flow_graph/param/sizing/heat.py), over the heater efficiency.

Called from flow_graph/param/fluoro_train.py apply() after the acid plant is rated.
Run: python3 -m flow_graph.param.grease"""
import json, math
from . import drivers as DR

TAG = 'X-RTE TF: shop grease on site (A-M-429)'
M_ACID = 284.48                     # stearic-acid equivalent of the oxidised-wax acids, C18H36O2
M_H, M_O, M_CA, M_LI = 1.008, 15.999, 40.078, 6.941
M_H2O, M_CAO, M_CAOH2, M_LIOH = 2*M_H + M_O, M_CA + M_O, M_CA + 2*(M_O + M_H), M_LI + M_O + M_H   # built from the same parts so the balances close
M_CASOAP = 2*(M_ACID - 1.008) + M_CA
M_LISOAP = (M_ACID - 1.008) + M_LI
ROUTES = ('CA', 'LI')
NONROT = {'rectifier', 'inverter', 'pv', 'flow_battery', 'pem_fc', 'iem_fc', 'pem_electrolyser', 'genset', 'hydro',
          'farm', 'hab', 'shop', 'dock', 'heat_battery', 'digest'}

def lubricated_units(g):
    """Units with a lubrication task in AQS-OPS-002: powered (continuous_kw > 0), not electrical, farm, habitat, shop, dock, store or digester class."""
    out = []
    for n in g['nodes']:
        p = n.get('params') or {}; c = n.get('class') or ''
        if not p or p.get('presence') == 'absent' or c in ('boundary', 'building') or n.get('presence') == 'retired': continue
        if ((n.get('continuous_kw') or {}).get('value') or 0) > 0 and c not in NONROT: out.append(n['unit_id'])
    return out

def design(g, residue_comp=None, d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('grease_thickener')
    if route not in ROUTES: raise SystemExit(f'grease: grease_thickener {route!r} is not one of {ROUTES}')
    units = lubricated_units(g)
    gp = 0.005*v('grease_bearing_D_mm')*v('grease_bearing_B_mm')                 # g per point per relubrication (SKF_RELUB)
    interval_d = DR.val(d, 'maint_rotating')['lube_mo']*365.25/12
    grease = len(units)*v('grease_points_per_unit')*gp/interval_d/1000               # kg/d
    soap = grease*v('grease_soap_frac'); base = grease - soap
    msoap = M_CASOAP if route == 'CA' else M_LISOAP; nacid = (2 if route == 'CA' else 1)
    n_soap = soap/msoap                                                                # kmol/d
    acid = n_soap*nacid*M_ACID; base_kg = n_soap*(M_CAOH2 if route == 'CA' else M_LIOH)
    water_sap = n_soap*nacid*M_H2O
    wax_ox = acid/v('grease_wax_ox_acid_yield'); o2 = wax_ox*v('grease_wax_ox_o2')
    vent = wax_ox + o2 - acid + water_sap                                             # oxidation by-products + saponification water
    wax = base + wax_ox
    z = dict(route=route, units=len(units), gp_g=gp, interval_d=interval_d, grease_kg_d=grease, soap_kg_d=soap, base_oil_kg_d=base,
             wax_kg_d=wax, wax_ox_kg_d=wax_ox, acid_kg_d=acid, o2_kg_d=o2, vent_kg_d=vent, thickener_kg_d=base_kg,
             caoh2_kg_d=base_kg if route == 'CA' else 0.0, lioh_kg_d=base_kg if route == 'LI' else 0.0,
             lime_draw_kg_d=0.0, slake_h2o_kg_d=0.0, reject_kg_d=0.0)
    if route == 'CA':
        f = (residue_comp or {}).get('CaO', 0.0)
        if f <= 0: raise SystemExit('grease: the CA route takes its lime from the ACID_PLANT residue, which carries no CaO on this acid route; select LI or GYPSUM_LOOP')
        cao = n_soap*M_CAO; z['lime_draw_kg_d'] = cao/f; z['slake_h2o_kg_d'] = n_soap*M_H2O; z['reject_kg_d'] = z['lime_draw_kg_d'] - cao
    assert abs(wax + o2 + base_kg - grease - vent) < 1e-9*max(grease, 1e-6)
    # kettle: campaign batch; feed heat to the kettle temperature, shell loss for the run, over the heater efficiency
    T = v('grease_kettle_T_C_' + route.lower()); camp = v('grease_campaign_d'); run_h = v('grease_run_h')
    V = grease*camp/v('grease_rho_kg_m3')/v('grease_fill'); D = max(0.1, (4*V/math.pi)**(1/3))
    from .sizing import heat as HT
    thk, loss = HT.insulated_cylinder(T, D*1000, D)
    q_feed = (wax + base_kg)*v('grease_cp_kJ_kgK')*(T - 25)/86.4                       # W, daily average
    kw = (q_feed + loss*run_h/(camp*24))/v('grease_heater_eff')/1000
    z.update(kettle_L=V*1000, kettle_D_mm=D*1000, insul_mm=thk, loss_W=loss, kw=kw, kettle_T_C=T, campaign_d=camp)
    return z

def _rates(r):
    """Stream rates of both routes at the selected route's need (the other route at its rated case)."""
    return {'CA': dict(WAX='WAX_TO_GREASE_CA', TH='PCA_TO_GREASE', OUT='GREASE_CA_TO_MFG'),
            'LI': dict(WAX='WAX_TO_GREASE_LI', TH='LI_TO_GREASE', OUT='GREASE_LI_TO_MFG')}

def tf(g, E, d=None):
    from flow_graph.param.o2_close import _edge
    d = d or DR.load()
    N = {n['unit_id']: n for n in g['nodes']}
    ls = E['IA-LIME-SHIP']; comp = dict(ls.get('composition') or {})
    r = design(g, comp, d)
    other = 'LI' if r['route'] == 'CA' else 'CA'
    dd = json.loads(json.dumps(d)); dd['grease_thickener']['value'] = other
    try: ro = design(g, comp, dd)
    except SystemExit: ro = None
    names = _rates(r)
    def rate(sid, x, note, rated=None, case=None):
        e = E[sid]; e['presence'] = 'present'
        e['rate'] = {'value': round(x, 6), 'unit': 'kg/d', 'status': 'study', 'note': f'{TAG}: {note}'}
        p = e.setdefault('params', {})
        for k in ('rate_normal_kg_d', 'rate_rated_kg_d', 'rated_case', 'backs_up', 'rated_by'): p.pop(k, None)
        if rated is not None:
            p.update(rate_normal_kg_d=0.0, rate_rated_kg_d=round(rated, 6), rated_case=case, backs_up=names[r['route']]['OUT'], rated_by='flow_graph/param/grease.py')
        if not p: e.pop('params')
    def mk(sid, a, b, ph, carries, comp_, x, note):
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, x, 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp_, note); g['edges'].append(e); E[sid] = e
        E[sid].update(carries=carries, composition=comp_); rate(sid, x, note)
        E[sid]['presence'] = 'present' if x > 0 else 'retired'
    sel, oth = names[r['route']], names[other]
    rate(sel['WAX'], r['wax_kg_d'], f"C19-C28 cut: base oil {r['base_oil_kg_d']:.6f} + wax oxidised to soap acid {r['wax_ox_kg_d']:.6f} kg/d (route {r['route']}).")
    rate(sel['TH'], r['thickener_kg_d'], f"{'Ca(OH)2' if r['route'] == 'CA' else 'LiOH'} for the soap, stoichiometric (route {r['route']}).")
    rate(sel['OUT'], r['grease_kg_d'], f"grease need: {r['units']} lubricated units x points x Gp {r['gp_g']:.2f} g every {r['interval_d']:.1f} d (SKF_RELUB, AQS-OPS-002; route {r['route']}).")
    case = f"grease_thickener = {other}" + (' and the polish liquor lithium tenor is measured (notes/DIGESTER_LI.md)' if other == 'LI' else '')
    for k, key in (('WAX', 'wax_kg_d'), ('TH', 'thickener_kg_d'), ('OUT', 'grease_kg_d')):
        rate(oth[k], 0.0, f'standby thickener route, carries {key.replace("_kg_d", "")} when {case} (A-M-429).', rated=(ro or r)[key], case=case)
    mk('IA-GREASE-SPENT', 'MFG_SHOP', 'OIL_PYRO', 'S', 'purged grease to the pyrolysis feed', {'hydrocarbon': round(1 - r['soap_kg_d']/r['grease_kg_d'], 6), 'soap': round(r['soap_kg_d']/r['grease_kg_d'], 6)},
       r['grease_kg_d'], 'purged grease collected at relubrication goes to pyrolysis with the plastics feed (recovery first); equals the grease issued.')
    unit = 'GREASE_CA' if r['route'] == 'CA' else 'GREASE_LI'
    for sid, a, b, ph, carries, comp_, key in (('IA-GREASE-AIR', 'ATMOS', 'GREASE_CA', 'G', 'oxygen of the process air for the wax oxidation', {'O2': 1.0}, 'o2_kg_d'),
                                              ('IA-GREASE-VENT', 'GREASE_CA', 'ATMOS', 'G', 'water, carbon dioxide and light acids of the wax oxidation and saponification', {'CO2': 0.5, 'water': 0.5}, 'vent_kg_d'),
                                              ('IA-GREASE-AIR-LI', 'ATMOS', 'GREASE_LI', 'G', 'oxygen of the process air for the wax oxidation', {'O2': 1.0}, 'o2_kg_d'),
                                              ('IA-GREASE-VENT-LI', 'GREASE_LI', 'ATMOS', 'G', 'water, carbon dioxide and light acids of the wax oxidation and saponification', {'CO2': 0.5, 'water': 0.5}, 'vent_kg_d')):
        on = (b == unit or a == unit)
        mk(sid, a, b, ph, carries, comp_, r[key] if on else 0.0, f"{key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (grease.py, route {r['route']}).")
    for sid, a, b, ph, carries, comp_, key in (('IA-LIME-TO-PCA', 'ACID_PLANT', 'P_CA', 'S', 'cake-kiln lime residue to the slaker', comp, 'lime_draw_kg_d'),
                                              ('IA-PCA-H2O', 'GW_INTAKE', 'P_CA', 'L', 'well water to slake the lime', {'H2O': 1.0}, 'slake_h2o_kg_d'),
                                              ('IA-PCA-REJECT', 'P_CA', 'NORTH_DOCK', 'S', 'slaker grit (anhydrite, fluorspar and inerts of the kiln residue)', {k: x for k, x in comp.items() if k != 'CaO'} or {'inerts': 1.0}, 'reject_kg_d')):
        mk(sid, a, b, ph, carries, comp_, r[key], f"{key.replace('_kg_d', '')} = {r[key]:.6f} kg/d (grease.py, route {r['route']}).")
    if r['lime_draw_kg_d'] > 0:
        x = float(ls['rate']['value']) - r['lime_draw_kg_d']; assert x >= -1e-9, ('grease: lime draw exceeds the residue', x)
        ls['rate'] = dict(ls['rate'], value=round(x, 6), note=ls['rate']['note'] + f" Less {r['lime_draw_kg_d']:.6f} kg/d to P_CA for the grease soap (A-M-429).")
        # the S and F of the residue that leave with the slaker grit are declared on the acid-plant and HF-kiln records
        M_S, M_F = 32.06, 18.998
        s_kg = r['lime_draw_kg_d']*(comp.get('CaSO4', 0)*M_S/136.14 + comp.get('H2SO4', 0)*M_S/98.08)
        f_kg = r['lime_draw_kg_d']*comp.get('CaF2', 0)*2*M_F/78.074
        for u, el, kg, basis in (('ACID_PLANT', 'S', s_kg, 'cake-kiln non-conversion; the residue drawn for the grease lime leaves with the slaker grit'),
                                 ('HF_GEN', 'F', f_kg, 'fluorspar the HF kiln does not convert; the residue drawn for the grease lime leaves with the slaker grit')):
            for rec in (N[u].get('params') or {}).get('recovery') or []:
                if rec['element'] == el:
                    rec['unrecovered'] = [x for x in rec['unrecovered'] if x['stream'] != 'IA-PCA-REJECT'] + [dict(stream='IA-PCA-REJECT', kg_d=round(kg, 6), recoverable=False, basis=basis)]
        N['P_CA'].setdefault('params', {})['recovery'] = [dict(element='Ca', use='grease soap thickener', need_kg_d=r['caoh2_kg_d']*M_CA/M_CAOH2,
            recovered_kg_d=r['caoh2_kg_d']*M_CA/M_CAOH2, recovered_from=['IA-LIME-TO-PCA'], ore_streams=[], unrecovered=[],
            note='the calcium is the lime of the ACID_PLANT cake-kiln residue, a waste of the plant (A-M-429)')]
    else:
        (N['P_CA'].get('params') or {}).pop('recovery', None)
    N[unit].setdefault('params', {})['design'] = {k: (round(x, 6) if isinstance(x, float) else x) for k, x in r.items()}
    for u in ('GREASE_CA', 'GREASE_LI'):
        on = u == unit
        N[u]['continuous_kw'] = {'value': round(r['kw'], 5) if on else 0.0, 'unit': 'kW', 'status': 'study',
                                 'note': f"{TAG}: " + (f"feed heat to {r['kettle_T_C']:g} C + shell loss {r['loss_W']:.1f} W for a {DR.val(d, 'grease_run_h'):g} h run every {r['campaign_d']:g} d, over the heater efficiency" if on else f'standby kettle (route {r["route"]})') + '.'}
        sf = 'SF-' + u
        if sf not in E:
            e = _edge(sf, 'SOL_ARK_60K', u, 'E', ['elec'], '480 V AC', 0.0, 'kW', N['SOL_ARK_60K']['sector_id'], N[u]['sector_id'], None, '')
            e['header'] = 'tray'; g['edges'].append(e); E[sf] = e
        E[sf]['presence'] = 'present' if on else 'retired'
        if True:
            E[sf]['rate'] = {'value': round(r['kw'], 5) if on else 0.0, 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to {u} continuous_kw.'}
    return r

if __name__ == '__main__':
    g = json.load(open('flow_graph/plant_flow_graph.json')); E = {e['stream_id']: e for e in g['edges']}
    d = DR.load(); comp = E['IA-LIME-SHIP'].get('composition')
    for rt in ROUTES:
        dd = json.loads(json.dumps(d)); dd['grease_thickener']['value'] = rt
        print(json.dumps({k: (round(y, 6) if isinstance(y, float) else y) for k, y in design(g, comp, dd).items()}))
