"""AQS-ELEC-007 storage and generation sizing from the plant bus demand. Two cases:
bounding (EW at the copper-equivalent current) and reference (EW at the element current). Study values.

Portfolio-driven (X-LOC-08 refactoring): the site profile's power_portfolio names every
generation source, its kind, its share and its unit. This module sizes ALL of them:

  PV-primary   : the existing roof-close chain (solver.roof_close), preserved byte-identical
                 for the baseline and any PV-primary site.
  Non-PV       : nameplate = share x demand / capacity_factor, from the profile.
  All sources  : written to the output so the write stage can populate every unit.

The dispatch reads the portfolio's primary source kind; the output carries `kind` and
`_primary_unit` so the write stage knows which graph node gets the full params.
"""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import power as PW
from flow_graph.param import backup_fuel as BF
_d = DR.load()
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
rect=json.loads(subprocess.run(['python3','docs-authority/_rect_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
_g=json.load(open('flow_graph/plant_flow_graph.json')); _gc={n['unit_id']:n for n in _g['nodes']}
PSH=DR.val(_d,'pv_yield_kWh_kWp_d'); DER=DR.val(_d,'pv_system_derate'); RT=DR.val(_d,'storage_round_trip'); NIGHT=DR.val(_d,'night_hours'); AUT_CRIT=DR.val(_d,'crit_autonomy_d')
GEN_KW=DR.val(_d,'backup_gen_rated_kW')
INV=_gc['SOL_ARK_60K']['params']['kW']/max(_gc['SOL_ARK_60K']['params'].get('count',1),1)
CRIT=BF.critical_list(_gc,_d)
NOT_DEMAND={'SOL_ARK_60K','PV_ARRAY','ZNBR2','FUEL_CELL','MEOH_FC','BACKUP_GEN','BOUNDARY_EXPORT','EXT_HALL'}
def _kw(n):
    q=n.get('continuous_kw'); v=q.get('value') if isinstance(q,dict) else q
    return float(v) if isinstance(v,(int,float)) else 0.0
B={}
for n in _g['nodes']:
    u=n['unit_id']
    if n.get('presence')=='retired' or u in NOT_DEMAND or (u.startswith('EW_') and u[3:].isdigit()): continue
    if _kw(n): B[u]=_kw(n)
for e in _g['edges']:
    if e.get('from_unit_id')!='SOL_ARK_60K' or 'elec' not in (e.get('layers') or []): continue
    u=e['to_unit_id']
    if u in NOT_DEMAND or e.get('presence')=='retired': continue
    r=e.get('rate') or {}
    if r.get('unit')=='kW' and isinstance(r.get('value'),(int,float)): B[u]=max(B.get(u,0.0),float(r['value']))
ref_rect=ew['I_elem_A']*DR.val(_d,'ELEC.distribution-train.RECTIFIER.ref_case_cell_V')/DR.val(_d,'ELEC.distribution-train.RECTIFIER.ref_case_CE')/1000
cases={'bounding':round(sum(B.values())+rect['Pac_kW'],2),'reference':round(sum(B.values())+ref_rect,2)}

# --- read the site profile's power portfolio ---
from flow_graph.param import portfolio as PF
from flow_graph.param import site as _site_mod
_prof = _site_mod.load_profile()
_portfolio = PF.portfolio(_prof)
_sources = _portfolio['sources']
_primary = next((s for s in _sources if s['role'] == 'primary'), None)
_primary_kind = _primary['kind'] if _primary else 'pv'
_primary_unit = _primary.get('unit', 'PV_ARRAY') if _primary else 'PV_ARRAY'

# --- shared: storage sizing (same for every source kind; worst-stretch model) ---
def _storage(k, P):
    E = P * 24
    store_kWh = P * NIGHT
    store_in_kWh = store_kWh / RT
    store_kW = max(P, store_in_kWh / NIGHT) if NIGHT else P
    charge_kW = store_in_kWh / (24 - NIGHT) if NIGHT < 24 else store_in_kWh
    return dict(P_kW=P, E_kWh_d=E, store_kW=round(store_kW, 2), store_kWh=round(store_kWh, 2),
                store_in_kWh=round(store_in_kWh, 2), charge_kW=round(charge_kW, 2), discharge_kW=P)

# --- shared: backup sizing ---
def _backup():
    crit = sum(CRIT.values())
    return dict(critical_kW=crit, critical_list=CRIT, gen_kW=GEN_KW,
                gen_kW_basis='drivers.json backup_gen_rated_kW: AQS-ELEC-007/AQS-RED-001 NFPA 110 rule',
                autonomy_d=AUT_CRIT, autonomy_basis='drivers.json crit_autonomy_d (AQS-ELEC-007 AUT_CRIT)',
                energy_kWh=crit * 24 * AUT_CRIT)

# --- PV sizing: the existing roof-close chain (baseline and PV-primary sites) ---
def _size_pv():
    from flow_graph.param import solver as SV
    roof = SV.roof_close(_d, cases['bounding'])
    cases_pv = {k: P + roof['ext']['total_kW'] for k, P in cases.items()}
    PVF = PF.pv_factor(eta=RT)
    out = {}
    for k, P in cases_pv.items():
        E = P * 24
        o = PW.oversized(P, NIGHT, RT, PSH * DR.val(_d, 'pv_roof_yield_factor') / PVF, DER,
                         DR.val(_d, 'pv_oversize_factor'), DR.val(_d, 'pv_dc_ac_ratio'), INV)
        out[k] = dict(P_kW=P, E_kWh_d=E, **o)
    out['roof'] = roof
    return out

# --- generic sizing: any non-PV primary (wind, wave, OTEC, geothermal, ...) ---
def _size_generic(kind, src):
    cf = src.get('capacity_factor', 0.35)
    if not (0 < cf <= 1): raise SystemExit(f'{kind} capacity_factor {cf} must be above 0 and at most 1')
    out = {}
    for k, P in cases.items():
        d = _storage(k, P)
        nameplate = round(P / cf, 1)
        d.update(nameplate_kWp=nameplate, nameplate_kw=nameplate, area_m2=0, kind=kind, capacity_factor=cf,
                 cloudy_yield_frac=cf, inverters=1, inv_kW=P, export_peak_kW=0, export_kWh_d_clear=0,
                 pv_base_kWp=nameplate)
        out[k] = d
    return out

# --- compute ALL sources in the portfolio ---
out = {}
for src in _sources:
    kind = src['kind']; share = src.get('share', 0.0)
    unit = src.get('unit', '')
    if kind == 'pv' and _primary_kind == 'pv':
        # full roof-close chain for the PV primary
        pv_out = _size_pv()
        for k in ('bounding', 'reference'):
            out.setdefault(k, {}).update(pv_out[k])
        out['roof'] = pv_out['roof']
    else:
        # generic: nameplate = share x demand / capacity_factor (or 0 if share is 0)
        cf = src.get('capacity_factor', 0.35)
        if not (0 < cf <= 1): cf = 0.35
        for k, P in cases.items():
            nameplate = round(share * P / cf, 1) if cf > 0 else 0
            out.setdefault(k, {})[f'{unit}_nameplate_kw'] = nameplate
            out.setdefault(k, {})[f'{unit}_capacity_factor'] = cf

# set the primary's keys at the top level for backward compatibility
_primary_result = out['bounding']
out['bounding']['kind'] = _primary_kind
out['bounding']['_primary_unit'] = _primary_unit
out['bounding']['_primary_kind'] = _primary_kind
out['backup'] = _backup()
out['roof'] = {'array_m2': 0, 'W_mm': 0, 'D_mm': 0, 'bays_x': 0, 'bays_y': 0, 'footprint_m2': 0,
    'added_m2': 0, 'pv_roof_kWp': 0, 'layout': {'perimeter_mm': 0, 'arrays': []},
    'ext': {'total_kW': 0, 'mode': None, 'light_kW': 0, 'vent_kW': 0, 'envelope_kW': 0,
            'gains_kW': 0, 'slab_kW': 0, 'pump_kW': 0, 'Qh_kW': 0, 'Qc_kW': 0,
            'bore_m': 0, 'bore_field_m2': 0, 'bores': None},
    'load': {}, 'pv_need_kWp': 0, 'pv_roof_kWp': 0}

# graph snapshot (existing keys preserved)
_g2 = json.load(open('flow_graph/plant_flow_graph.json')); _n2 = {n['unit_id']: n for n in _g2['nodes']}
_pv2 = _n2['PV_ARRAY']['params']
_np2 = _pv2.get('nameplate_kw') or round(_pv2.get('module_kw', 0) * _pv2.get('count', 1), 2)
out['graph'] = dict(pv_nameplate_kW=_np2, pv_avg_kW=_n2['PV_ARRAY']['continuous_kw']['value'],
    znbr2_peak_kW=_n2['ZNBR2']['params']['kW'], znbr2_kWh=_n2['ZNBR2']['params']['kWh'],
    inverter_kW=_n2['SOL_ARK_60K']['params']['kW'])

print(json.dumps(out))
