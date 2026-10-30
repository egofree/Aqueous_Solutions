"""On-site silicon for the CZ charge: carbothermic reduction and electronic-grade refining (owner decision 2026-10-29, t58u; A-M-419).

The plant makes everything on site; only waste and raw ore come in. The CZ charge of WAFER_FAB (flow_graph/param/fab_silicon.py)
is therefore made here, in two steps, both sized from that charge.

Reduction (SI_REDUCE). Quartz ore and pyrolysis char from OIL_PYRO react in a small submerged-arc furnace,
SiO2 + 2 C -> Si + 2 CO. Part of the silica leaves as fume (si_saf_recovery). The product is metallurgical-grade silicon of
purity si_mg_purity; the rest is the iron, aluminium and calcium that came in with the ore and the char ash. As on an
open-top arc furnace, the carbon monoxide burns to carbon dioxide in the hood with air drawn from the room, and the
silica fume is caught in the baghouse and sent with the solids to the acid leach LEACH_CSTR_1.

Refining (SI_REFINE). Two routes of different technology can be selected with the driver si_refine_route:
- TCS_SIEMENS: the metallurgical silicon is hydrochlorinated to trichlorosilane, which is distilled and decomposed on
  heated silicon rods under hydrogen (Siemens). The hydrogen, hydrogen chloride and silicon tetrachloride of the reactor
  off-gas are recovered and recycled to the hydrochlorinator, so on a closed loop only chlorine is consumed.
- SILANE_FBR: trichlorosilane is redistributed to silane, which is decomposed on silicon seed in a fluidised bed. The
  chemistry of the loop is the same; the energy and the yield differ.
On either route the loop bleeds the impurity chlorides and a silicon tetrachloride purge (the silicon not recovered,
1 - yield) to the acid leach LEACH_CSTR_1, where the tetrachloride hydrolyses to silica and hydrogen chloride, so its
chlorine joins the plant acid loop and the metal chlorides join the leach liquor. The chlorine they carry is the make-up, drawn as Cl2 from the AL_POT cell
gas; inside the loop it is burned with the recycled hydrogen to hydrogen chloride. The electronic-grade silicon goes to
the METAL_STORE buffer, which feeds the CZ charge (STOCK_TO_FAB).

Run: python3 -m flow_graph.param.si_refine"""
import json
from . import drivers as DR
from . import fab_silicon

TAG = 'X-MFG-40 TF, on-site silicon (A-M-419)'
M_SI, M_CL, M_O2, M_C, M_CO, M_CO2 = 28.0855, 35.453, 31.998, 12.011, 28.010, 44.009
M_SIO2, M_STC, M_TCS = M_SI + M_O2, M_SI + 4*M_CL, M_SI + 1.008 + 3*M_CL
ROUTES = ('TCS_SIEMENS', 'SILANE_FBR')

def design(d=None):
    d = d or DR.load(); v = lambda k: DR.val(d, k)
    route = v('si_refine_route')
    if route not in ROUTES:
        raise SystemExit(f'si_refine: si_refine_route {route!r} is not one of {ROUTES}')
    eg = fab_silicon.design(d)['si_kg_d']                       # electronic-grade silicon for the CZ charge
    y = v(f'si_refine_yield_{route}'); si_tot = eg/y             # silicon fed to the loop
    eol = fab_silicon.design(d)['pv_wafer_kg_d']                 # retired cells of end-of-life modules, recovered first (A-M-437)
    si_in = si_tot - eol                                         # silicon in the metallurgical feed
    mg = si_in/v('si_mg_purity'); imp = mg - si_in               # metallurgical silicon and its impurities
    si_lost = si_tot - eg
    stc = si_lost*M_STC/M_SI; cl_stc = si_lost*4*M_CL/M_SI; cl_imp = imp*v('si_imp_cl_kg_kg')
    cl2 = cl_stc + cl_imp; purge = stc + imp + cl_imp
    r = v('si_saf_recovery')
    sio2_r = si_in*M_SIO2/M_SI; fume = sio2_r*(1 - r)/r
    quartz = sio2_r + fume + imp; c = 2*M_C*si_in/M_SI; co = 2*M_CO*si_in/M_SI
    o2_hood = co*M_O2/2/M_CO; co2 = co*M_CO2/M_CO                   # CO + 1/2 O2 -> CO2 in the hood
    kw_reduce = mg*v('si_saf_kWh_kg')/24; kw_refine = eg*v(f'si_refine_kWh_kg_{route}')/24
    out = dict(route=route, eg_kg_d=eg, eol_kg_d=eol, yield_=y, si_in_kg_d=si_in, mg_kg_d=mg, imp_kg_d=imp, stc_kg_d=stc, cl2_kg_d=cl2, purge_kg_d=purge,
               quartz_kg_d=quartz, char_kg_d=c, co_kg_d=co, fume_kg_d=fume, o2_hood_kg_d=o2_hood, co2_kg_d=co2, kw_reduce=kw_reduce, kw_refine=kw_refine)
    if route == 'TCS_SIEMENS':
        out['tcs_circ_kg_d'] = eg/v('siemens_pass_conv')*M_TCS/M_SI   # trichlorosilane fed to the rods per day
    assert abs(quartz + c + o2_hood - mg - co2 - fume) < 1e-9 and abs(mg + eol + cl2 - eg - purge) < 1e-9
    return out

# stream id, from, to, carries, phase, composition, key of the design dict
STREAMS = (('IA-QUARTZ-MU', 'NORTH_DOCK', 'SI_REDUCE', 'quartz ore for the silicon furnace (raw ore)', 'S', {'SiO2': 1.0}, 'quartz_kg_d'),
           ('CHAR_TO_SI', 'OIL_PYRO', 'SI_REDUCE', 'pyrolysis char reductant', 'S', {'C': 1.0}, 'char_kg_d'),
           ('IA-SI-HOOD-O2', 'ATMOS', 'SI_REDUCE', 'oxygen of the hood air that burns the furnace carbon monoxide', 'G', {'O2': 1.0}, 'o2_hood_kg_d'),
           ('IA-SI-CO2', 'SI_REDUCE', 'ATMOS', 'carbon dioxide of the burned furnace gas', 'G', {'CO2': 1.0}, 'co2_kg_d'),
           ('IA-SI-FUME', 'SI_REDUCE', 'LEACH_CSTR_1', 'silica fume from the furnace baghouse', 'S', {'SiO2': 1.0}, 'fume_kg_d'),
           ('IA-SI-MG', 'SI_REDUCE', 'SI_REFINE', 'metallurgical-grade silicon', 'S', {'Si': 1.0}, 'mg_kg_d'),
           ('IA-CL2-SIREF', 'AL_POT', 'SI_REFINE', 'chlorine make-up of the chlorosilane loop', 'G', {'Cl2': 1.0}, 'cl2_kg_d'),
           ('IA-SI-PURGE', 'SI_REFINE', 'LEACH_CSTR_1', 'impurity chlorides and silicon tetrachloride bleed', 'L', {'SiCl4': 1.0}, 'purge_kg_d'),
           ('IA-PV-EOL', 'PV_ARRAY', 'SI_REFINE', 'silicon of the cells retired from end-of-life modules, crushed, to the chlorosilane loop', 'S', {'Si': 1.0}, 'eol_kg_d'),
           ('IA-SI-EG', 'SI_REFINE', 'METAL_STORE', 'electronic-grade silicon for the CZ charge', 'S', {'Si': 1.0}, 'eg_kg_d'))
WHY = {'quartz_kg_d': 'silica reduced plus fume plus impurities', 'char_kg_d': '2 C per Si reduced', 'o2_hood_kg_d': 'half an O2 per CO burned', 'co2_kg_d': 'one CO2 per CO burned', 'fume_kg_d': 'silica not recovered as silicon',
       'mg_kg_d': 'refining feed / yield / purity', 'cl2_kg_d': 'chlorine leaving in the purge', 'purge_kg_d': 'impurity chlorides plus SiCl4 of the unrecovered silicon',
       'eg_kg_d': 'the CZ charge of fab_silicon.py', 'eol_kg_d': 'cells retired a day, equal in steady state to the cells installed (pv_wafer.py, A-M-437)'}

def tf(g, d=None):
    from flow_graph.param.o2_close import _edge, _node
    r = design(d); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    sh = E.get('IA-CL2-SHIP')                                  # the pot chlorine export is net of this make-up (foundry_poly.py); keep it net when
    if sh is not None and (sh.get('params') or {}).get('si_cl2_kg_d') is not None:   # the cell need moves the make-up after foundry_poly ran (A-M-437)
        dl = sh['params']['si_cl2_kg_d'] - r['cl2_kg_d']
        if dl:
            sh['rate']['value'] = round(sh['rate']['value'] + dl, 6); sh['params']['base_kg_d'] = round(sh['params']['base_kg_d'] + dl, 6)
            sh['params']['si_cl2_kg_d'] = r['cl2_kg_d']
    if 'SI_REFINE' not in N:
        n = _node('SI_REFINE', 'GLASS', 'reactor', None, 'Electronic-grade silicon refining (A-M-419).', {})
        n['notes'] = 'Electronic-grade silicon refining: chlorosilane loop on metallurgical silicon from SI_REDUCE (A-M-419).'
        g['nodes'].append(n); N['SI_REFINE'] = n
    for sid, a, b, carries, ph, comp, key in STREAMS:
        note = f"{TAG}: {WHY[key]} = {r[key]:.4f} kg/d (si_refine.py, route {r['route']})."
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass'], carries, r[key], 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, note)
            g['edges'].append(e); E[sid] = e
        e = E[sid]
        e.update(from_unit_id=a, to_unit_id=b, carries=carries, presence='present', composition=comp)
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
    from .recovery import frac as _fr
    N['SI_REDUCE'].setdefault('params', {})['recovery'] = [dict(
        element='Si', use='silicon furnace quartz', need_kg_d=r['quartz_kg_d']*_fr('SiO2', 'Si'), recovered_kg_d=0.0, recovered_from=[],
        ore_streams=['IA-QUARTZ-MU'], unrecovered=[],
        note='the plant silica wastes are fines (spent shell flour, silica fume), not the lump quartz the arc furnace burden needs, and the silica fume already goes to the leach')]
    imp = E.get('IA-SI-IMPORT')
    if imp is not None and imp['presence'] != 'retired':
        imp['presence'] = 'retired'
        imp['rate'] = {'value': 0.0, 'unit': 'kg/d', 'status': 'study', 'note': 'Retired 2026-10-29 (owner decision t58u: no imports except waste or raw ore). The CZ charge is made on site by SI_REDUCE and SI_REFINE (A-M-419).'}
    return r

if __name__ == '__main__':
    print(json.dumps({k: (round(x, 5) if isinstance(x, float) else x) for k, x in design().items()}))
