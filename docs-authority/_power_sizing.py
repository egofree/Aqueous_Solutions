import sys
"""AQS-ELEC-007 storage and generation sizing from the plant bus demand. Two cases:
bounding (EW at the copper-equivalent current) and reference (EW at the element current). Study values.
Rev AC re-base 2026-10-18 (A-M-231, notes/pv_sizing_derivation_2026-10-18.md §2/§3): demand is derived
from the graph itself — unit bound = max(node continuous_kw, SOL_ARK_60K elec feed) — instead of the stale
Rev BH LOAD_LIST one-line rows (+175 kW contamination: EXT_HALL 93.8 twice, RECT_EW twice, retired farm/
chem rows). The EXT_HALL subtraction no-op is gone (roof_close adds the extension load itself) and the
inverter block size is read from the graph (SOL_ARK kW / count), not hardcoded."""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import power as PW
from flow_graph.param import backup_fuel as BF
_d = DR.load()   # X-PAR-03: yield, derate, round trip, night hours from drivers.json
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
rect=json.loads(subprocess.run(['python3','docs-authority/_rect_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
_g=json.load(open('flow_graph/plant_flow_graph.json')); _gc={n['unit_id']:n for n in _g['nodes']}
PSH=DR.val(_d,'pv_yield_kWh_kWp_d'); DER=DR.val(_d,'pv_system_derate'); RT=DR.val(_d,'storage_round_trip'); NIGHT=DR.val(_d,'night_hours'); AUT_CRIT=DR.val(_d,'crit_autonomy_d')   # D7: single drivers source (was a 2.0 hardcode duplicated in o2_close PSH_STORE_D); PSH from AQS-SITE-002 (NREL PVWatts)
GEN_KW=DR.val(_d,'backup_gen_rated_kW')   # D3: single governed source (AQS-ELEC-007/AQS-RED-001 NFPA 110 rule; replaces the local ceil(crit x 1.25 / 5) x 5 formula, one of four drifting BACKUP_GEN sizes)
INV=_gc['SOL_ARK_60K']['params']['kW']/max(_gc['SOL_ARK_60K']['params'].get('count',1),1)   # inverter block = graph kW / SOL_ARK count (49 x 60 kW), not a single-inverter hardcode
CRIT=BF.critical_list(_gc,_d)   # single source of the critical list (flow_graph/param/backup_fuel.py), also used for the BACKUP_GEN fallback-fuel reserve
# Graph-native bounding demand (A-M-231): max(node continuous_kw, SOL_ARK_60K elec feed) per unit;
# EW_1..EW_9 cell DC is covered by the RECT-EW bounding AC row below; storage-charge, curtailment and
# generation (bus, PV, FC, DMFC, standby genset, ZNBR2) are not demand.
NOT_DEMAND={'SOL_ARK_60K','PV_ARRAY','ZNBR2','FUEL_CELL','MEOH_FC','BACKUP_GEN','BOUNDARY_EXPORT','EXT_HALL'}   # R10b: roof_close adds the extension load itself (A-M-231); the EXT_HALL node (created by write_graph power()) must not double-count
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
from flow_graph.param import solver as SV
roof=SV.roof_close(_d,cases['bounding'])   # X-PAR-07: roof-only PV; the extension load (incl. EXT_HALL) is added by roof_close, counted once
cases={k:P+roof['ext']['total_kW'] for k,P in cases.items()}
from flow_graph.param import portfolio as PF
from flow_graph.param import site as _site_mod
PVF=PF.pv_factor(eta=RT)   # site portfolio: PV share and worst-stretch correction (1 at the baseline); scales the PV balance through its yield
# X-LOC-08: wind-primary portfolios. The wind capacity factor (in the profile) replaces the PV
# yield as the generation basis. The nameplate is demand / capacity_factor; the oversize rule
# and the worst-stretch correction apply as for PV. The roof-close function is not called for
# non-PV sites because the generation is not roof-constrained.
if PVF <= 0:
    _wind = [s for s in PF.portfolio(_site_mod.load_profile())['sources'] if s['role'] == 'primary' and s['kind'] == 'wind']
    if not _wind: raise SystemExit('site portfolio has no PV or wind primary; power sizing for other primary sources is not built yet (AQS-PLAN-011 section 5.5)')
    _cf = _wind[0].get('capacity_factor', 0.35)
    if not (0 < _cf <= 1): raise SystemExit(f'wind capacity_factor {_cf} must be above 0 and at most 1')
    _demand = sum(B.values()) + rect['Pac_kW']
    _nameplate = round(_demand / _cf, 1)
    out = {}
    for k, P in cases.items():
        E = P * 24
        out[k] = dict(P_kW=P, E_kWh_d=E, nameplate_kWp=_nameplate, nameplate_kw=_nameplate,
                      area_m2=0, kind='wind', capacity_factor=_cf,
                      note='wind primary: nameplate = demand / capacity_factor; roof-close not called (generation is not roof-constrained)')
    print(json.dumps({'roof': out, 'kind': 'wind'}))
    sys.exit(0)
out={}
for k,P in cases.items():
    E=P*24                         # flat profile, continuous process (study)
    Edirect=P*(24-NIGHT); Estore=P*NIGHT
    o=PW.oversized(P,NIGHT,RT,PSH*DR.val(_d,'pv_roof_yield_factor')/PVF,DER,DR.val(_d,'pv_oversize_factor'),DR.val(_d,'pv_dc_ac_ratio'),INV)   # D75
    out[k]=dict(P_kW=P,E_kWh_d=E,**o)
out['roof']=roof
crit=sum(CRIT.values())
out['backup']=dict(critical_kW=crit,critical_list=CRIT,gen_kW=GEN_KW,gen_kW_basis='drivers.json backup_gen_rated_kW: AQS-ELEC-007/AQS-RED-001 NFPA 110 rule (125 % of critical, 5 kW steps; 32 kW issued list -> 40 kW) - single governed source, stamped on the graph by write_graph power()',autonomy_d=AUT_CRIT,autonomy_basis='drivers.json crit_autonomy_d (AQS-ELEC-007 AUT_CRIT)',energy_kWh=crit*24*AUT_CRIT)
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
_pv=N['PV_ARRAY']['params']; _np=_pv.get('nameplate_kw') or round(_pv.get('module_kw',0)*_pv.get('count',1),2)   # Rev AC stores module_kw x count
out['graph']=dict(pv_nameplate_kW=_np,pv_avg_kW=N['PV_ARRAY']['continuous_kw']['value'],
    znbr2_peak_kW=N['ZNBR2']['params']['kW'],znbr2_kWh=N['ZNBR2']['params']['kWh'],inverter_kW=N['SOL_ARK_60K']['params']['kW'])
print(json.dumps(out))
