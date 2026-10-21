"""X-MAT-09. Liquor temperature on every liquid edge into a thermoplastic unit, checked against the
material limit (AQS-STD-002 M5). Writes params.T_C and params.T_basis on edges that lack T_C when run
with --write. Prints a markdown table."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param.drivers import load as _dl; _D=_dl()
import json, re, sys
LIM={'PVC-U':60,'CPVC':93,'PVDF':120}
U={**{u:'PVC-U' for u in 'BMED_ACID BMED_BASE POLISH_BANK CONTINUOUS_RECYCLE CRU S13_CLASS_TREAT SALT_FEED WS_KOH WS_PHOS WS_AMMONIA WET_BENCH GREY_TREAT BLACK_DIGEST MEOH_FERM ALK_SCRUBBER MET_SCRUB CATCH_TANK ROOF_TANK REMIN ZNBR2_BR2_REGEN EW_2 EW_3 EW_4 EW_5 EW_6 EW_7 EW_8 EW_9'.split()},
   **{u:'CPVC' for u in 'LEACH_CSTR_1 FLOAT_SINK EW_1 ACID_POLISH_SCRUB NOX_SCRUB'.split()},
   **{u:'PVDF' for u in 'HX8 WS_NITRIC WS_PEROX HNO3 WS_HF_ED'.split()}}
# Unit materials per AQS-STD-002 Rev L section 12 (2026-10-21): the CPVC members are the section 8
# resolution (85 C hot-LEACH draws: FLOAT_SINK, EW_1, ACID_POLISH_SCRUB, NOX_SCRUB) and section 7
# (LEACH_CSTR_1); earlier revisions had them as PVC-U, which printed false EXCEEDS rows.
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
lt=N['LEACH_CSTR_1']['params'].get('liquor_T_C', 77.5); leachT=lt.get('value',77.5) if isinstance(lt,dict) else lt   # R11 Rev AC regen: liquor_T_C param dropped from the graph; design basis 77.5 C (AQS-DUTY-050)
def parse(e):
    p=e.get('params') or {}
    if isinstance(p.get('T_C'),(int,float)): return p['T_C'],'edge T_C'
    for k in ('conditions','carries','notes'):
        s=str(p.get(k) if k in p else e.get(k) or '')
        m=re.search(r'(\d+(?:\.\d+)?)\s*°?\s*C\b',s)
        if m: return float(m.group(1)),f'edge {k}'
    return None,None
def upstream(u):
    if u=='LEACH_CSTR_1': return 85.0,'LEACH liquor band maximum 85 C (liquor_T_C band)'
    for e in g['edges']:
        if e['from_unit_id']==u:
            t,b=parse(e)
            if t is not None: return t,f'upstream {u} outlet {e["stream_id"]} ({b})'
    return None,None
# X-MAT-19 trim coolers (section 10, resize X-RSZ-04): in-line water-cooled trim exchangers booked as
# "{stream}-TRIM" kW edges. The delivered inlet to the receiving unit is the upstream T minus
# W86400/(m*cp), cp per driver (cp_hcl20_kJ_kgK 3.0 for acid liquors, cp_naoh20_kJ_kgK 3.6 for base).
TRIM={}   # base stream id -> (unit kW, receiving unit)
for e in g['edges']:
    m=re.match(r'^(.+)-TRIM$',e['stream_id'] or '')
    if m and e.get('presence')=='present' and (e.get('rate') or {}).get('unit')=='kW' and e['rate']['value']:
        m2=re.match(r'trim cooler heat from (\S+)',e.get('carries') or '')
        if m2: TRIM[m2.group(1)]=(e['rate']['value'],e['to_unit_id'])
CP={'BMED_ACID':'cp_hcl20_kJ_kgK','BMED_BASE':'cp_naoh20_kJ_kgK'}
rows=[]; W='--write' in sys.argv
for e in g['edges']:
    u=e['to_unit_id']
    if u not in U or e.get('presence')=='absent' or (e.get('rate') or {}).get('unit')!='kg/d': continue
    if e.get('phase') not in ('L','S/L','L/G'): continue
    t,b=parse(e)
    if t is None: t,b=upstream(e['from_unit_id'])
    if t is None: t,b=_D['storage.default_no_heat_input_T_C']['value'],'assumption: no heat input stated upstream; 40 C, the 0.4 % site dry bulb 37.8 C (AQS-SITE-002) rounded up (A-M-269)'
    tr=TRIM.get(e['stream_id'])
    if tr and isinstance(t,(int,float)):
        kw,_sink=tr; cpk=CP.get(u)
        if cpk and e['rate']['value']:
            cpv=_D[cpk]['value']; dT=kw*86400.0/(e['rate']['value']*cpv); t=round(t-dT,1)
            b=f'{b}; in-line water-cooled trim {e["stream_id"]}-TRIM ({kw} kW, cp {cpv} kJ/(kg K) per {cpk}, dT {dT:.1f} K; X-MAT-19 section 10)'
    lim=LIM[U[u]]; ok=t<=lim
    rows.append((e['stream_id'],e['from_unit_id'],u,U[u],t,lim,'ok' if ok else 'EXCEEDS',b))
    if W and not isinstance((e.get('params') or {}).get('T_C'),(int,float)):
        e.setdefault('params',{}) ; e['params'] = e['params'] or {}; e['params']['T_C']=t; e['params']['T_basis']='X-MAT-09: '+b
if W: json.dump(g,open('flow_graph/plant_flow_graph.json','w'),indent=2,ensure_ascii=True)
print('| Edge | From | To | Material | T °C | Limit °C | Check | Basis |\n| --- | --- | --- | --- | --- | --- | --- | --- |')
for r in sorted(rows,key=lambda r:(r[6]=='ok',r[2])): print('| '+' | '.join(str(x) for x in r)+' |')
print(f"\n{len(rows)} edges; {sum(r[6]!='ok' for r in rows)} exceed; {sum(r[7].startswith('assumption') for r in rows)} on the ambient assumption.")
