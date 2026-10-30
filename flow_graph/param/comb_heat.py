"""Fuel route of the fuel-fired melt backup COMB_HEAT (X-RTE-COMB-HEAT-FUEL, A-M-438).

Why the unit stays. COMB_HEAT is the third melt path of the foundry. IND_MELT and its electric alternate RF_HEAT draw on the
same electrical supply, so a fault of that supply takes out both; the fuel-fired furnace is the one melt path that does not
depend on it. That diversity of energy source is real redundancy, so the unit is kept and given a fuel route.

Rated case. COMB_HEAT is in service when IND_MELT and RF_HEAT are both out, for standby_outage_d days (A-M-283, A-M-418). It
then melts the design-day charge of IND_MELT. The heat into the metal is the IND_MELT melt energy times the coil efficiency
(melt_eta, foundry_poly.py); a fuel-fired crucible furnace passes only comb_crucible_eta of the fuel heat to the metal (BCS2005).
The fuel rate is that heat over the furnace efficiency and the lower heating value of the fuel. Oxygen is drawn from the
air at comb_excess_air over the stoichiometric need, and the off-gas (carbon dioxide, water and the excess oxygen) goes to
MET_SCRUB. On the design day the routes carry no flow.

Fuel (driver comb_heat_fuel). Two plant fuels are valid and both routes are built; the selected one is held in its store:
- C5C10 (default): the C5-C10 cut from PROD_C5_C10, burned as (CH2)n + 1.5n O2 -> n CO2 + n H2O. The cut is surplus that the
  plant ships, and it is already stored for the backup generator.
- MEOH: plant methanol from MEOH_TANK, CH3OH + 1.5 O2 -> CO2 + 2 H2O. It burns clean but is made from electrolytic hydrogen.
The chlorinator carbon monoxide of TI_CELL was evaluated and is not a valid fuel for this duty: the chlorination makes about
2 CO per Ti, less than a kilogram a day, most of it already drawn by SOLV_PLANT and RESIST_SYN, while the rated duty needs
tens of kilograms a day; holding it for the outage would mean a large store of a toxic gas filled over months (cases()).
Run: python3 -m flow_graph.param.comb_heat"""
import json
from . import drivers as DR
from .foundry_poly import MM as AW
TAG = 'X-RTE-COMB-HEAT-FUEL (A-M-438)'
FUELS = ('C5C10', 'MEOH')
from .foundry_poly import MW_CH2 as M_CH2
M_O2, M_CO2, M_H2O, M_MEOH, M_CO = 31.998, 44.009, 18.015, 32.042, 28.010
# kg O2, kg CO2, kg H2O per kg fuel, from the combustion equations in the docstring
STOICH = {'C5C10': (1.5*M_O2/M_CH2, M_CO2/M_CH2, M_H2O/M_CH2), 'MEOH': (1.5*M_O2/M_MEOH, M_CO2/M_MEOH, 2*M_H2O/M_MEOH)}
SRC = {'C5C10': 'PROD_C5_C10', 'MEOH': 'MEOH_TANK'}
SID = {'C5C10': 'IA-C5-COMB', 'MEOH': 'IA-MEOH-COMB'}
CO_LHV_MJ_KG = 10.1        # carbon monoxide lower heating value (PERRY9), used only to show why CO is not a valid fuel here

def lhv_MJ_kg(d, fuel):
    return DR.val(d, 'ELEC.generation-train.BACKUP_GEN.fuel_lhv_kWh_kg')*3.6 if fuel == 'C5C10' else DR.val(d, 'MEOH.synthesis-train.MEOH_FC.meoh_LHV_MJ_kg')

def heat_kWh_d(g, d):
    N = {n['unit_id']: n for n in g['nodes']}
    return float(N['IND_MELT']['params']['sizing']['melt_kWh_d'])*DR.val(d, 'melt_eta')

def rated(g, d, fuel):
    q = heat_kWh_d(g, d)/DR.val(d, 'comb_crucible_eta')            # kWh/d of fuel heat
    f = q*3.6/lhv_MJ_kg(d, fuel); o2, co2, h2o = STOICH[fuel]; xs = DR.val(d, 'comb_excess_air')
    return dict(fuel=fuel, fuel_kWh_d=q, fuel_kg_d=f, o2_kg_d=f*o2*(1 + xs), offgas_kg_d=f*(1 + o2*(1 + xs)),
                comp={'CO2': round(f*co2/(f*(1 + o2*(1 + xs))), 4), 'H2O': round(f*h2o/(f*(1 + o2*(1 + xs))), 4), 'O2': round(f*o2*xs/(f*(1 + o2*(1 + xs))), 4)})

def cases(g, d=None):
    d = d or DR.load(); N = {n['unit_id']: n for n in g['nodes']}
    ti = float(next(e for e in g['edges'] if e['stream_id'] == 'METALS_TO_IND_MELT')['rate']['value'] or 0)
    co_make = ti/AW['Ti']*2*M_CO; drawn = sum(float(e['rate']['value'] or 0) for e in g['edges'] if e['from_unit_id'] == 'TI_CELL' and (e.get('composition') or {}).get('CO', 0) > 0.5 and e.get('presence') == 'present')
    co_need = heat_kWh_d(g, d)/DR.val(d, 'comb_crucible_eta')*3.6/CO_LHV_MJ_KG
    return dict(C5C10=rated(g, d, 'C5C10'), MEOH=rated(g, d, 'MEOH'), CO=dict(make_kg_d=co_make, drawn_kg_d=drawn, need_kg_d=co_need,
                fill_d=co_need*DR.val(d, 'standby_outage_d')/max(co_make - drawn, 1e-9)))

def sel(d): 
    f = DR.val(d, 'comb_heat_fuel')
    if f not in FUELS: raise SystemExit(f'comb_heat: comb_heat_fuel {f!r} is not one of {FUELS}')
    return f

def ensure(g, d=None):
    """Create the fuel, oxygen and off-gas routes of COMB_HEAT (zero on the design day; standby_routes.py rates them)."""
    from flow_graph.param.o2_close import _edge
    d = d or DR.load(); N = {n['unit_id']: n for n in g['nodes']}; E = {e['stream_id']: e for e in g['edges']}
    if 'COMB_HEAT' not in N: return
    c5 = E['IA-C5-POLY'].get('composition'); me = E['MEOH_TO_OLEFIN'].get('composition')      # the same fuels as those live routes
    rows = [(SID['C5C10'], 'PROD_C5_C10', 'COMB_HEAT', 'L', 'C5-C10 cut fuel for the fuel-fired melt backup', c5),
            (SID['MEOH'], 'MEOH_TANK', 'COMB_HEAT', 'L', 'plant methanol fuel for the fuel-fired melt backup', me),
            ('IA-COMB-O2', 'ATMOS', 'COMB_HEAT', 'G', 'oxygen of the combustion air of the fuel-fired melt backup', {'O2': 1.0}),
            ('COMB_OFFGAS', 'COMB_HEAT', 'MET_SCRUB', 'G', 'combustion off-gas of the fuel-fired melt backup', rated(g, d, sel(d))['comp'])]
    for sid, a, b, ph, carries, comp in rows:
        if sid not in E:
            e = _edge(sid, a, b, ph, ['mass', 'energy'], carries, 0.0, 'kg/d', N[a]['sector_id'], N[b]['sector_id'], comp, f'{TAG}.')
            g['edges'].append(e); E[sid] = e
        E[sid].update(presence='present', carries=carries, composition=comp, from_unit_id=a, to_unit_id=b)
    sz = N['COMB_HEAT'].setdefault('params', {}).setdefault('sizing', {})
    r = rated(g, d, sel(d))
    sz.update(fuel=sel(d), rated_fuel_kg_d=round(r['fuel_kg_d'], 4), rated_fuel_kWh_d=round(r['fuel_kWh_d'], 3),
              backup_of='IND_MELT (third melt path, fuel-fired; the one path independent of the electrical supply of IND_MELT and RF_HEAT)',
              outage_basis='IND_MELT and RF_HEAT both out, for standby_outage_d (A-M-283, A-M-418, A-M-438)')

def _fuel_fn(fuel):
    def f(g, E, N, d):
        r = rated(g, d, fuel)
        return r['fuel_kg_d'], f"the IND_MELT melt heat {heat_kWh_d(g, d):.2f} kWh/d over comb_crucible_eta and the {fuel} heating value"
    return f

def _o2(g, E, N, d):
    r = rated(g, d, sel(d)); return r['o2_kg_d'], f"{r['fuel_kg_d']:.3f} kg/d of {r['fuel']} at comb_excess_air over the stoichiometric oxygen"

def _offgas(g, E, N, d):
    r = rated(g, d, sel(d)); return r['offgas_kg_d'], f"{r['fuel']} fuel plus its combustion oxygen"

def _hold(fuel):
    return lambda d: sel(d) == fuel

if __name__ == '__main__':
    import os
    R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(json.dumps(cases(json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))), default=float, indent=1))
