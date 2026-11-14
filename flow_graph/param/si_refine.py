"""On-site silicon for the CZ charge: carbothermic reduction and electronic-grade refining (owner decision 2026-10-29, t58u; A-M-472).

The plant makes everything on site; only waste and raw ore come in. The CZ charge of WAFER_FAB (flow_graph/param/fab_silicon.py)
is therefore made here, in two steps, both sized from that charge, and every silicon waste is recovered before any ore is drawn
(recovery-first, F-20261110-06): the crop, square-off and pot scrap return to the charge (A-M-487), the reclaimed saw kerf and the
silicon of retired cells enter the chlorosilane loop (A-M-485/486), the furnace baghouse fume is briquetted back into the burden
(A-M-488), the crib silicate recovered from the leach feed (A-M-490) is briquetted as furnace burden, and dock quartz is drawn for
the shortfall only.

Reduction (SI_REDUCE). Briquetted recovered silica and pyrolysis char from OIL_PYRO react in a small submerged-arc furnace,
SiO2 + 2 C -> Si + 2 CO. Part of the silica leaves as fume (si_saf_recovery); the baghouse catch is briquetted straight back
into the burden at si_fume_burden_frac and only the rest goes with the solids to the acid leach LEACH_CSTR_1. The product is
metallurgical-grade silicon of purity si_mg_purity; the rest is the iron, aluminium and calcium that came in with the burden and
the char ash. As on an open-top arc furnace, the carbon monoxide burns to carbon dioxide in the hood with air drawn from the room.

Refining (SI_REFINE). Two routes of different technology can be selected with the driver si_refine_route:
- TCS_SIEMENS: the metallurgical silicon is hydrochlorinated to trichlorosilane, which is distilled and decomposed on
  heated silicon rods under hydrogen (Siemens). The reactor off-gas silicon tetrachloride is hydrogenated back to
  trichlorosilane, 3 SiCl4 + 2 H2 + Si -> 4 SiHCl3 (A-M-489), so on a closed loop the silicon not recovered stays in
  circulation and only chlorine is consumed.
- SILANE_FBR: trichlorosilane is redistributed to silane, which is decomposed on silicon seed in a fluidised bed. The
  chemistry of the loop is the same; the energy and the yield differ.
On either route the loop now bleeds only the impurity chlorides - their mass and chlorine are taken from the impurity balance
at the registered iron-rich blend (A-M-489) - plus the end-of-life separation residue, and that bleed goes to the acid leach
LEACH_CSTR_1, where the metal chlorides join the leach liquor, so its chlorine joins the plant acid loop. The chlorine of the
bleed is the make-up, drawn as Cl2 from the AL_POT cell gas, and the hydrogenation hydrogen comes from HDR_H2. The
electronic-grade silicon goes to the METAL_STORE buffer with the returned crop and pot scrap, which feeds the CZ charge
(STOCK_TO_FAB).

Run: python3 -m flow_graph.param.si_refine [--write]"""
import json, os, sys
from . import drivers as DR
from . import fab_silicon
from .constants import M, mw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GP = os.path.join(ROOT, 'flow_graph/plant_flow_graph.json')
TAG = 'X-MFG-40 TF, on-site silicon (A-M-472)'
M_SI, M_CL, M_C, M_H2 = M['Si'], M['Cl'], M['C'], 2*M['H']
M_O2, M_CO, M_CO2 = 2*M['O'], M_C + M['O'], M_C + 2*M['O']
M_SIO2, M_STC, M_TCS = mw({'Si': 1, 'O': 2}), M['Si'] + 4*M['Cl'], M['Si'] + M['H'] + 3*M['Cl']
# the registered iron-rich impurity blend of A-M-472's 2.2 kg Cl/kg (FeCl3 1.90, AlCl3 3.94, CaCl2 1.77):
# 0.75/0.15/0.10 by metal mass gives 2.20 kg Cl per kg of metal and the chloride masses below (A-M-489)
IMP_BLEND = {'FeCl3': 0.75*mw({'Fe': 1, 'Cl': 3})/M['Fe'], 'AlCl3': 0.15*mw({'Al': 1, 'Cl': 3})/M['Al'],
             'CaCl2': 0.10*mw({'Ca': 1, 'Cl': 2})/M['Ca']}
ROUTES = ('TCS_SIEMENS', 'SILANE_FBR')

def design(d=None, g=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('si_refine_route')
    if route not in ROUTES:
        raise SystemExit(f'si_refine: si_refine_route {route!r} is not one of {ROUTES}')
    fab = fab_silicon.design(d)
    fs = v('si_scrap_recycle_frac'); yk = v('si_kerf_recycle_frac'); ye = v('si_eol_yield')
    scrap = fab['scrap_rec_kg_d']                                       # crop/pot scrap back to the charge (A-M-487)
    eg = fab['si_kg_d'] - scrap                                         # electronic-grade silicon the loop must make
    eol_in = fab['pv_wafer_kg_d']; eol = eol_in*ye                      # retired cells into the loop (A-M-485) ...
    eol_res = eol_in - eol                                              # ... and their glass/encapsulant separation residue
    kerf = fab['kerf_rec_kg_d']                                         # reclaimed kerf into the loop (A-M-486)
    si_in = eg - eol - kerf                                             # silicon the furnace must reduce (loop net)
    if si_in < 0:
        raise SystemExit(f'si_refine: the recovered silicon ({eol + kerf:.4f} kg/d) exceeds the loop need ({eg:.4f} kg/d); '
                         f'lower si_eol_yield or si_kerf_recycle_frac')
    mg = si_in/v('si_mg_purity'); imp = mg - si_in                      # metallurgical silicon and its impurities
    y = v(f'si_refine_yield_{route}')
    cl_imp = imp*v('si_imp_cl_kg_kg'); cl2 = cl_imp                     # chlorine leaves only with the impurity chlorides
    purge = imp + cl_imp + eol_res                                      # the bleed: impurity chlorides + separation residue
    stc_rec = eg*(1 - y)/y                                              # SiCl4-Si hydrogenated back to TCS (A-M-489)
    h2 = stc_rec*v('si_h2_stc_kg_kg')                                   # hydrogenation hydrogen of the loop's own recycled off-gas
    sio2_r = si_in*M_SIO2/M_SI
    r = v('si_saf_recovery'); fume = sio2_r*(1 - r)/r                   # gross fume to the baghouse
    bf = v('si_fume_burden_frac'); fume_leach = fume*(1 - bf)           # the credited share is briquetted back (A-M-488)
    burden_need = sio2_r + imp + fume_leach                             # SiO2-equivalent the furnace takes in (dressing rides the burden)
    # recovery-first burden: the crib silicate recovered from the leach feed (A-M-490), short of the pool
    g = g or json.load(open(GP))
    feed = next((e for e in g['edges'] if e['stream_id'] == 'IA-FEED-01'), None)
    _ref = (((feed or {}).get('params') or {}).get('assay_envelope') or {})
    sil_class = (_ref.get('cases', {}).get('reference_point') or {}).get('silicate_oxide')
    crib = float(feed['rate']['value'])*float(sil_class)*v('s08_silicate_carry_frac') if feed and sil_class is not None else 0.0
    briq = min(crib, burden_need); quartz = burden_need - briq          # dock quartz is the shortfall only (A-M-472 recovery-first)
    c = 2*M_C*si_in/M_SI; co = 2*M_CO*si_in/M_SI
    o2_hood = co*M_O2/2/M_CO; co2 = co*M_CO2/M_CO                   # CO + 1/2 O2 -> CO2 in the hood
    kw_reduce = mg*v('si_saf_kWh_kg')/24; kw_refine = eg*v(f'si_refine_kWh_kg_{route}')/24
    out = dict(route=route, eg_kg_d=eg, charge_kg_d=fab['si_kg_d'], scrap_kg_d=scrap, eol_kg_d=eol, eol_in_kg_d=eol_in, eol_res_kg_d=eol_res,
               kerf_kg_d=kerf, yield_=y, si_in_kg_d=si_in, mg_kg_d=mg, imp_kg_d=imp, stc_rec_kg_d=stc_rec, h2_kg_d=h2, cl2_kg_d=cl2,
               purge_kg_d=purge, purge_chlorides_kg_d=imp + cl_imp, crib_si_kg_d=crib, briq_kg_d=briq, quartz_kg_d=quartz,
               sio2_r_kg_d=sio2_r,
               char_kg_d=c, co_kg_d=co, fume_kg_d=fume, fume_leach_kg_d=fume_leach, fume_burden_kg_d=fume*bf,
               o2_hood_kg_d=o2_hood, co2_kg_d=co2, kw_reduce=kw_reduce, kw_refine=kw_refine)
    if route == 'TCS_SIEMENS':
        out['tcs_circ_kg_d'] = eg/v('siemens_pass_conv')*M_TCS/M_SI   # trichlorosilane fed to the rods per day
    # the registered impurity blend must reproduce the registered chlorine ratio (A-M-472 / A-M-489)
    _blend_cl = sum({'Fe': 3*0.75*M['Cl']/M['Fe'], 'Al': 3*0.15*M['Cl']/M['Al'], 'Ca': 2*0.10*M['Cl']/M['Ca']}.values())
    assert abs(_blend_cl - v('si_imp_cl_kg_kg')) < 0.02, (_blend_cl, v('si_imp_cl_kg_kg'))
    out['kerf_leach_kg_d'] = fab['kerf_leach_kg_d']
    assert abs(briq + quartz + c + o2_hood - mg - co2 - fume_leach) < 1e-9, (briq + quartz + c + o2_hood, mg + co2 + fume_leach)
    assert abs(mg + eol_in + kerf + cl2 - eg - purge) < 1e-9            # loop closes: mg + credits + chlorine = rods + bleed
    return out

# stream id, from, to, carries, phase, composition, key of the design dict
STREAMS = (('IA-QUARTZ-MU', 'NORTH_DOCK', 'SI_REDUCE', 'quartz ore for the silicon furnace (raw ore), the burden shortfall only', 'S', {'SiO2': 1.0}, 'quartz_kg_d'),
           ('IA-SI-BRIQ', 'MFG_SHOP', 'SI_REDUCE', 'briquetted crib silicate recovered from the leach feed, furnace burden (A-M-490)', 'S', {'SiO2': 1.0}, 'briq_kg_d'),
           ('CHAR_TO_SI', 'OIL_PYRO', 'SI_REDUCE', 'pyrolysis char reductant', 'S', {'C': 1.0}, 'char_kg_d'),
           ('IA-SI-HOOD-O2', 'ATMOS', 'SI_REDUCE', 'oxygen of the hood air that burns the furnace carbon monoxide', 'G', {'O2': 1.0}, 'o2_hood_kg_d'),
           ('IA-SI-CO2', 'SI_REDUCE', 'ATMOS', 'carbon dioxide of the burned furnace gas', 'G', {'CO2': 1.0}, 'co2_kg_d'),
           ('IA-SI-FUME', 'SI_REDUCE', 'LEACH_CSTR_1', 'silica fume not briquetted back into the burden (1 - si_fume_burden_frac)', 'S', {'SiO2': 1.0}, 'fume_leach_kg_d'),
           ('IA-SI-MG', 'SI_REDUCE', 'SI_REFINE', 'metallurgical-grade silicon', 'S', {'Si': 1.0}, 'mg_kg_d'),
           ('IA-CL2-SIREF', 'CA_POT', 'SI_REFINE', 'chlorine make-up of the chlorosilane loop', 'G', {'Cl2': 1.0}, 'cl2_kg_d'),
           ('IA-SI-PURGE', 'SI_REFINE', 'LEACH_CSTR_1', 'impurity-chloride bleed with the end-of-life separation residue', 'L', None, 'purge_kg_d'),
           ('IA-PV-EOL', 'PV_ARRAY', 'SI_REFINE', 'silicon of the cells retired from end-of-life modules, crushed, to the chlorosilane loop', 'S', {'Si': 1.0}, 'eol_in_kg_d'),
           ('IA-SI-EG', 'SI_REFINE', 'METAL_STORE', 'electronic-grade silicon for the CZ charge', 'S', {'Si': 1.0}, 'eg_kg_d'))
WHY = {'quartz_kg_d': 'the burden shortfall left after the recovered crib silicate (recovery-first, A-M-472)',
       'briq_kg_d': 'the crib silicate of the leach feed (A-M-490) briquetted as furnace burden, short of the burden need',
       'char_kg_d': '2 C per Si reduced', 'o2_hood_kg_d': 'half an O2 per CO burned', 'co2_kg_d': 'one CO2 per CO burned',
       'fume_leach_kg_d': 'gross fume x (1 - si_fume_burden_frac): the baghouse catch returns to the burden (A-M-488)',
       'mg_kg_d': '(charge - returned scrap - eol - kerf credits) / purity', 'cl2_kg_d': 'chlorine leaving with the impurity chlorides',
       'purge_kg_d': 'impurity chlorides from the impurity balance at the registered blend, plus the eol separation residue',
       'eg_kg_d': 'the CZ charge less the returned crop and pot scrap (fab_silicon.py, A-M-487)',
       'eol_in_kg_d': 'cells retired a day, equal in steady state to the cells installed (pv_wafer.py, A-M-484); ye lands in the loop (A-M-485)'}

def tf(g, d=None):
    from flow_graph.param.o2_close import _edge, _node
    r = design(d, g); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    sh = E.get('IA-CA-CL2-SHIP')                               # the CA_POT chlorine export is net of this make-up (foundry_poly.py); keep it net when
    if sh is not None and (sh.get('params') or {}).get('si_cl2_kg_d') is not None:   # the cell need moves the make-up after foundry_poly ran (A-M-484; the source moved from AL_POT to CA_POT when the AL_POT chlorine closed on the cake chlorination, X-QA-19)
        dl = sh['params']['si_cl2_kg_d'] - r['cl2_kg_d']
        if dl:
            sh['rate']['value'] = round(sh['rate']['value'] + dl, 6); sh['params']['si_cl2_kg_d'] = r['cl2_kg_d']
    if 'SI_REFINE' not in N:
        n = _node('SI_REFINE', 'GLASS', 'reactor', None, 'Electronic-grade silicon refining (A-M-472).', {})
        n['notes'] = 'Electronic-grade silicon refining: chlorosilane loop on metallurgical silicon from SI_REDUCE (A-M-472).'
        g['nodes'].append(n); N['SI_REFINE'] = n
    from .recovery import frac as _fr
    imp_comp = {k: round(w/sum(IMP_BLEND.values()), 6) for k, w in IMP_BLEND.items()}
    for sid, a, b, carries, ph, comp, key in STREAMS:
        note = f"{TAG}: {WHY[key]} = {r[key]:.4f} kg/d (si_refine.py, route {r['route']})."
        if sid == 'IA-SI-PURGE':                                    # the bleed composition from the impurity balance (A-M-489)
            comp = dict(imp_comp); comp['separation residue'] = round(r['eol_res_kg_d']/r['purge_kg_d'], 6) if r['purge_kg_d'] else 0.0
            comp = {k: round(x/sum(comp.values()), 6) for k, x in comp.items()}
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(from_unit_id=a, to_unit_id=b, carries=carries, presence='present', composition=comp)
        if r[key] == 0.0:
            e['presence'] = 'retired'                    # nothing carries today; the edge returns when the driver moves
            if sid == 'IA-QUARTZ-MU':
                note = ('Retired by recovery-first silicon (F-20261110-06): the briquetted crib silicate of the leach feed covers the whole '
                        'furnace burden, so no dock quartz is drawn. The edge returns if a driver change leaves a shortfall (si_refine.py).')
        e['rate'] = {'value': round(r[key], 6), 'unit': 'kg/d', 'status': 'study', 'note': note}
    for u, k, why in (('SI_REDUCE', 'kw_reduce', f"{r['mg_kg_d']:.4f} kg/d metallurgical silicon x si_saf_kWh_kg / 24 h"),
                      ('SI_REFINE', 'kw_refine', f"{r['eg_kg_d']:.4f} kg/d electronic-grade silicon x si_refine_kWh_kg_{r['route']} / 24 h")):
        note = f'{TAG}: {why} (si_refine.py).'
        N[u]['continuous_kw'] = {'value': round(r[k], 4), 'unit': 'kW', 'status': 'study', 'note': note}
        sid = f'SF-{u}'
        if sid not in E:
            e = _edge(sid, 'SOL_ARK_60K', u, 'E', ['elec'], '480 V AC', r[k], 'kW', N['SOL_ARK_60K']['sector_id'], N[u]['sector_id'], None, note)
            e['header'] = 'tray'; g['edges'].append(e); E[sid] = e
        E[sid]['rate'] = {'value': round(r[k], 4), 'unit': 'kW', 'status': 'study', 'note': f'{TAG}: feed equal to {u} continuous_kw.'}
    # recovery records (F-20261110-06): every silicon recovery is stamped where it happens
    N['SI_REDUCE'].setdefault('params', {})['recovery'] = [dict(
        element='Si', use='silicon furnace burden', need_kg_d=(r['sio2_r_kg_d'] + r['fume_leach_kg_d'] + r['imp_kg_d'])*_fr('SiO2', 'Si'),
        recovered_kg_d=r['briq_kg_d']*_fr('SiO2', 'Si'), recovered_from=['IA-SI-BRIQ'],
        ore_streams=['IA-QUARTZ-MU'], unrecovered=[],
        note=('recovery-first: the crib silicate recovered from the leach feed (A-M-490) is briquetted as the whole furnace burden; '
              'the baghouse fume returns to the burden at si_fume_burden_frac (A-M-488) and dock quartz is drawn for the shortfall only '
              f"({r['quartz_kg_d']:.4f} kg/d). The spent foundry shell silica stays in the foundry loop (SHELL_BREAK to SHELL_BUILD), "
              'retiring the shell-silica export and import pair')),
        dict(element='C', use='furnace char reductant', need_kg_d=r['char_kg_d'], recovered_kg_d=0.0,
             recovered_from=[], ore_streams=[],
             unrecovered=[dict(stream='IA-SI-CO2', kg_d=round(r['co2_kg_d']*M_C/M_CO2, 6), recoverable=False,
                               basis='the furnace carbon monoxide burns to carbon dioxide in the hood with plant air; '
                                     'stack gas of the small submerged-arc class (A-M-472)')],
             note='the pyrolysis char carbon reduces the silica and leaves as hood CO2; the element mass balance closes (F-20261110-07 loss check)')]
    N['SI_REFINE'].setdefault('params', {})['recovery'] = [dict(
        element='Si', use='electronic-grade silicon for the CZ charge', need_kg_d=r['eg_kg_d'],
        recovered_kg_d=r['eol_kg_d'] + r['kerf_kg_d'], recovered_from=['IA-PV-EOL', 'IA-FAB-KERF-REC'],
        ore_streams=[], unrecovered=[dict(stream='IA-SI-PURGE', kg_d=r['eol_res_kg_d'], recoverable=False,
                                          basis='end-of-life glass and encapsulant separation residue at si_eol_yield (A-M-485); leaves with the impurity-chloride bleed to the leach'),
                                     dict(stream='IA-FAB-KERF', kg_d=r['kerf_leach_kg_d'], recoverable=False,
                                          basis='slurry-fine kerf fraction not reclaimed (1 - si_kerf_recycle_frac, A-M-486); stays with the spent slurry')],
        note=('the chlorosilane loop recovers the retired-cell silicon (A-M-485) and the reclaimed kerf (A-M-486) first and hydrogenates '
              'the recycled SiCl4 back to trichlorosilane (A-M-489), so only the impurity chlorides bleed; the crop and pot scrap return '
              'to the charge in METAL_STORE (A-M-487)'))]
    # the unit record (F-20261110-09 single-writer rule): this stage is the only writer of the
    # SI_REDUCE design values - the retired X-QA-06 study class specialty_sizing wrote beside the
    # route (A-M-466 replaced_by) no longer puts anything on the unit
    N['SI_REDUCE'].setdefault('params', {}).update({
        'design': {'duty': 'carbothermic silicon reduction: the briquetted crib-silicate burden and the pyrolysis char '
                           '-> metallurgical-grade silicon for the CZ charge (route si_refine.py, A-M-472)',
                   'si_kgd': round(r['si_in_kg_d'], 4), 'sio2_kgd': round(r['sio2_r_kg_d'], 4), 'char_kgd': round(r['char_kg_d'], 4)},
        'sizing': {'si_kgd': round(r['si_in_kg_d'], 4)},
        'size_mm': [1200, 1000, 1600],
        'size_basis': 'graphite hot-face furnace (the issued sec3 selection) at the batch class'})
    imp = E.get('IA-SI-IMPORT')
    if imp is not None and imp['presence'] != 'retired':
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t58u: no imports except waste or raw ore). The CZ charge is made on site by SI_REDUCE and SI_REFINE (A-M-472).'}
    return r

def main():
    """Silicon-route stage of the regen manifest (A-M-472): the family-4 graph writes, re-homed
    from the audit's balance.py to this stage. Order inside the pass: the wafer/litho/PV edges of
    fab_silicon.tf first (their silicon need sizes this loop), then the SI_REDUCE / SI_REFINE
    route and its chlorine make-up netting. foundry_poly seeds IA-CA-CL2-SHIP with the make-up it
    computed and this stage moves the export if the need moved after it (successive substitution)."""
    g = json.load(open(GP)); d = DR.load()
    fab_silicon.tf(g, d)
    r = tf(g, d)
    if '--write' in sys.argv:
        open(GP, 'w').write(json.dumps(g, indent=2))
    print(json.dumps({k: (round(x, 5) if isinstance(x, float) else x) for k, x in r.items()}, default=float))

if __name__ == '__main__':
    main()
