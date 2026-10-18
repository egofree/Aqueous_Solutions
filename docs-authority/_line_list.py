"""AQS-PIP-004 plant line list, generated from the graph. Every piped edge gets DN, class (AQS-PIP-003),
estimated length and route; solids and electrical edges are listed as not piped. Study rules below."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import lines as LN
_d=DR.load()
import json, re, math, glob, os, sys
sys.path.insert(0,'docs-authority')
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
seed=json.load(open('flow_graph/placement_seed.json'))
# unit centers: duty sheet origin + size/2 (from the duties/_origins.json sidecar, U2a), else placement block centre
C={}
num=r'(−?-?\d+(?:\.\d+)?)'
try:
    for u, o in json.load(open('docs-authority/duties/_origins.json'))['origins'].items():
        C[u] = ([o['origin_mm'][i] + o['size_mm'][i]/2 for i in range(3)], 'duty origin')
except FileNotFoundError:
    # DEPRECATED markdown fallback (U2a, 2026-10-18): runs ONLY when duties/_origins.json is absent.
    # Regenerate the sidecar with: python3 docs-authority/_duty_basis.py — do not build on this path.
    for f in glob.glob('docs-authority/duties/*.md'):
        u=os.path.basename(f)[:-3]; s=open(f).read().replace('−','-')
        m=re.search(r'[Oo]rigin (-?\d+), (-?\d+), (-?\d+) mm\. Size (\d+) [×x] (\d+) [×x] (\d+)',s)
        if m:
            o=list(map(float,m.groups()[:3])); z=list(map(float,m.groups()[3:])); C[u]=([o[i]+z[i]/2 for i in range(3)],'duty origin')
pr=json.load(open('flow_graph/placement_report.json'))
for r in pr.get('moves',[])+pr.get('create_moves',[]):
    o,z=r.get('origin_mm'),r.get('size_mm')
    if o and z and len(o)==3 and len(z)>=2:
        z=list(z)+[0]*(3-len(z)); C.setdefault(r['unit_id'],([o[i]+z[i]/2 for i in range(3)],'placement_report'))
for r in json.load(open('flow_graph/placement_study.json'))['units']:
    o,z=r['origin_mm'],r['size_mm']; C.setdefault(r['unit_id'],([o[i]+z[i]/2 for i in range(3)],'placement_study (STUDY)'))
LV={'L-1':-6000,'L0':0,'L1':6000}
for r in seed['units']:   # seed units (issued table) where no duty origin
    o,z=r.get('origin_mm'),r.get('size_mm')
    if o and z and len(z)>=2:
        o=list(o)+[LV.get(r.get('level'),0)]*(3-len(o)); z=list(z)+[0]*(3-len(z)); C.setdefault(r['unit_id'],([o[i]+z[i]/2 for i in range(3)],'placement_seed'))
# GA rev C / C2 moves (A-M-215, A-M-220): CAD relocations and overlap moves carry into the line centres (X-PIP-03 rev B)
import sys as _s; _s.path.insert(0, 'models/freecad')
try:
    import params as _FP
    for _u, (_cx, _cy) in getattr(_FP, 'RELOCATE', {}).items():
        if _u in C: C[_u] = ([_cx, _cy, C[_u][0][2]], C[_u][1] + ' + GA relocate')
except Exception: pass
if os.path.exists('docs-authority/inventory/CAD_MOVES.json'):
    for _m in json.load(open('docs-authority/inventory/CAD_MOVES.json')):
        if _m['unit'] in C:
            _c = C[_m['unit']][0]; C[_m['unit']] = ([_c[0] + _m['dx_mm'], _c[1] + _m['dy_mm'], _c[2]], C[_m['unit']][1] + ' + GA move')
if 'EVAP_ACID_VS' not in C and 'EVAP_ACID' in C:   # EVAP_ACID_VS rides on the EVAP_ACID frame, north edge (X-PAR-10)
    c=C['EVAP_ACID'][0]; C['EVAP_ACID_VS']=([c[0],c[1]+650,c[2]],'on EVAP_ACID frame')
for b in seed['blocks']:
    o=b['origin_mm']; z=b['size_mm']; c=[o[0]+z[0]/2,o[1]+z[1]/2,LV.get(b['level'],0)+500]
    for u in b.get('unit_ids',[]): C.setdefault(u,(c,'placement block '+b['block_id']))
PL={u:'PVC-U' for u in 'BMED_ACID BMED_BASE POLISH_BANK CONTINUOUS_RECYCLE CRU SALT_FEED S13_CLASS_TREAT WS_KOH WS_PHOS WS_AMMONIA WET_BENCH GREY_TREAT BLACK_DIGEST MEOH_FERM MET_SCRUB ALK_SCRUBBER CATCH_TANK ROOF_TANK REMIN ZNBR2_BR2_REGEN EW_2 EW_3 EW_4 EW_5 EW_6 EW_7 EW_8 EW_9'.split()}
PL.update({u:'CPVC' for u in 'LEACH_CSTR_1 FLOAT_SINK EW_1 ACID_POLISH_SCRUB NOX_SCRUB'.split()})
PL.update({u:'PVDF' for u in 'HX8 WS_NITRIC WS_PEROX HNO3 WS_HF_ED'.split()})
WATER=set('ROOF_TANK CATCH_TANK TERRACE_IRRIG GROW_BED HABITATION HAB_WASH CROP_TOMATO REMIN NUTRIENT_DOSE HYDRO_SET FAB_UPW_TANK'.split())
def cls(e):
    a,b=e['from_unit_id'],e['to_unit_id']; p=e.get('params') or {}; T=p.get('T_C') if isinstance(p.get('T_C'),(int,float)) else None
    comp=e.get('composition') or {}; car=(e.get('carries') or '').lower(); sid=e['stream_id']
    if sid.startswith('HL-Q1') or sid.startswith('HL-Q2') or '-Q1-' in sid or '-Q2-' in sid: return 'M2','Q1/Q2 thermal oil'
    if sid.startswith('HL-') or 'Q3' in sid or 'Q4' in sid: return 'M1','Q3/Q4 water loop'
    if sid=='IA-FLUE-QUENCH': return 'P5','quench water'
    if e.get('phase')=='G':
        if comp.get('H2',0)>0.5 or 'H2' in sid or comp.get('O2',0)>0.5 or a.startswith('CRYO') or b.startswith('CRYO') or a.startswith('HDR_') : return 'M1','dry gas, H2/O2/N2/CO2'
        if 'FLUE' in sid or 'FLUE' in a or 'FLUE' in b or 'NOX' in b or 'SCRUB' in b: return 'F1','flue or acid gas'
        return 'P3','process vent gas'
    m=[PL[x] for x in (a,b) if x in PL]
    if 'HF' in sid or 'PVDF' in m or 'nitric' in car or 'perox' in car: return 'P3','oxidizer, HF or PVDF unit'
    if (T and T>60) or 'CPVC' in m: return 'P2','hot leach liquor'
    if 'naoh' in car or 'koh' in car or 'base' in car: return 'P4','alkaline'
    if 'PVC-U' in m: return 'P1','acid or brine, at or below 60 C'
    if a in WATER or b in WATER or comp.get('water',0)>=0.97 and not comp.get('HCl'): return 'P5','water'
    if any(x in car for x in ('oil','solvent','ethanol','butanol','methanol','hydrocarbon','wax')): return 'M1','organic liquid'
    return 'P1','aqueous process, default thermoplastic'
def rho(e):
    ph=e.get('phase'); comp=e.get('composition') or {}
    if ph=='G': return 0.09 if comp.get('H2',0)>0.5 else 1.2
    return 1100.0 if comp.get('HCl') else 1000.0
DN=[15,20,25,32,40,50,65,80,100,150,200,250,300,400,500]; ID={15:15.8,20:20.9,25:26.6,32:35.1,40:40.9,50:52.5,65:62.7,80:77.9,100:102.3,150:154.1,200:202.7,250:254.5,300:303.2,400:381.0,500:477.8}
rows=[]
for e in g['edges']:
    u=(e.get('rate') or {}).get('unit'); ph=e.get('phase'); sid=e['stream_id']; lay=e.get('layers') or []
    a,b=e['from_unit_id'],e['to_unit_id']
    ca,cb=C.get(a),C.get(b)
    if ca and cb:
        d=sum(abs(ca[0][i]-cb[0][i]) for i in range(3))/1000*1.2; L=round(d,1); route=f"{a} → {b}, orthogonal × 1.2 ({ca[1]}; {cb[1]})"
    else: L=None; route=f"{a} → {b}, position missing for {', '.join(x for x,c in ((a,ca),(b,cb)) if not c)}"
    if ph in ('E','electric') or 'elec' in lay or (u=='kW' and not sid.startswith('HL-') and 'thermal' not in lay):
        rows.append((sid,a,b,'cable','—','—',L,route,'electrical: cable schedule X-ELS-06')); continue
    if ph=='S':
        rows.append((sid,a,b,'solids','—','—',L,route,'solids: conveyor, bin or hand transfer; not piped')); continue
    p=e.get('params') or {}
    if p.get('line_DN'): dn=int(p['line_DN']); basis='edge line_DN'
    elif u=='kW':
        mw_=(e['rate']['value'] or 0)/(DR.val(_d,'water_cp_kJ_kgK')*DR.val(_d,'heat_loop_dT_K'))   # kg/s water, INCROPERA7 / ASHRAE_SYS2020
        need=LN.min_id_mm(mw_,1000.0,DR.val(_d,'line_velocity_liquid_m_s')) if mw_>0 else 0
        dn=next((d for d in DN if ID[d]>=need and d>=DR.val(_d,'line_min_DN')),None) or 500
        basis=f"heat loop {e['rate']['value']:g} kW at ΔT {DR.val(_d,'heat_loop_dT_K'):g} K, 1 m/s"
    else:
        m=(e['rate']['value'] or 0)/86400; r=rho(e); v=DR.val(_d,'line_velocity_gas_m_s') if ph=='G' else DR.val(_d,'line_velocity_liquid_m_s')   # R11 Rev AC regen: 80 present edges carry null rates; sized as 0 flow (min DN)
        need=LN.min_id_mm(m,r,v) if m>0 else 0
        mn=DR.val(_d,'slurry_min_DN') if ph in ('S/L','L/S') else DR.val(_d,'line_min_DN')
        dn=next((d for d in DN if ID[d]>=need and d>=mn),None)
        basis=f"velocity {v:g} m/s, ρ {r:g}; min DN{mn}"
        if dn is None: print("BIG",sid,round(need),ph,e["rate"]["value"]); dn=500
    c,why=cls(e)
    rows.append((sid,a,b,f'DN{dn}',c,why,L,route,basis))
if __name__=='__main__':
    piped=[r for r in rows if r[3].startswith('DN')]
    miss=[r for r in piped if r[6] is None]
    hdr=f"""# Plant line list

Document number: AQS-PIP-004
Revision: A
Date: 2026-10-15
Authority: graph Rev BH; AQS-PLAN-007 X-PIP-02. Generated by `docs-authority/_line_list.py`. Classes per AQS-PIP-003. Study. Not a PE stamp. Rules (study, AQS-REG-002 A-M-065 to A-M-067): DN from edge `line_DN`, else velocity 1 m/s liquid, 10 m/s gas, minimum DN15, DN50 for slurries; length is the orthogonal distance between unit centres × 1.2; class by the rules in the script.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. | 2026-10-15 |

{len(rows)} edges: {len(piped)} piped, {sum(r[3]=='solids' for r in rows)} solids transfers, {sum(r[3]=='cable' for r in rows)} electrical. Piped edges without a length (unit position missing): {len(miss)}.

| Line | From | To | DN | Class | Service | Length m | Route | DN basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |"""
    out=[hdr]+['| '+' | '.join('' if x is None else str(x) for x in r)+' |' for r in rows]
    nopos=sorted({x for r in piped if r[6] is None for x in (r[1],r[2]) if x not in C})
    out.insert(1,f"Units with no position anywhere in the repo (no duty origin, no placement row): {len(nopos)}: {', '.join(nopos)}. Their lines carry DN and class; length and route wait for X-BLD placement.\n")
    open('docs-authority/LINE_LIST.md','w').write('\n'.join(out)+'\n')
    import collections
    print(len(rows),len(piped),len(miss),collections.Counter(r[4] for r in piped),sorted(set(x for r in miss for x in re.findall(r'for (.*)',r[7]))))
