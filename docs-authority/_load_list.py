"""AQS-ELEC-003 load list, Rev B (X-ELS-02). Every present node with continuous_kw is classified by the
basis its own graph stamp cites (authoritative census): 'calculated' when the note names the sizing
module / drivers key / transfer function / duty sheet that produced the kW, 'study share - basis pending
<reason>' for the explicit residuals (owner requirement locks, unbuilt trains, stubs, A-M-232 face-value
foundry nameplates), 'null by design' for stores with no continuous kW. Rev B promotes the node stamps
through write_graph X-ELS-02 load-basis stamping (A-M-275), so the graph value IS the calculated value
where classified calculated; Rev A showed graph and calc side by side. EW cells are listed from
_ew_sizing (DC behind RECTIFIER, not in the AC sum). Writes docs-authority/LOAD_LIST.md (display) and
docs-authority/LOAD_LIST.json (machine sidecar read by _one_line.py; U2a interlock transport)."""
import json, subprocess, hashlib, collections
g=json.load(open('flow_graph/plant_flow_graph.json'))
N={n['unit_id']:n for n in g['nodes']}
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['rows']
DC_BEHIND={r['cell'] for r in ew}
# Citation tokens: a graph continuous_kw note carrying one of these names its calculation (X-ELS-02 rule,
# A-M-275). PENDING below takes precedence, so a pending note that mentions a module does not misclassify.
TOK=('AQS-DUTY-','AQS-DSN-','AQS-NOTE-PV-REBASE','X-PAR-','X-MFG-','X-SAN-','roof_close','Faraday','DLI',
     'kWh/m3','kWh/kg','/ 24 h','house_scrubbers','NFPA 110','AQS-ELEC-008','AQS-ELEC-004','AQS-PWR-001','latent','COP')
# Explicit residuals: honest study shares with the reason no calculation exists yet. X-ELS-02 stays open on these.
# Rev C (A-M-286): every 2026-10-19 residual except the owner requirement locks now carries a calculated/cited
# basis on its graph stamp (write_graph x_els_residuals: foundry duty cycles at the X-MFG-37 trial basis,
# HABITATION equipment list, WAFER_FAB/WET_BENCH tool lists, AFTERBURNER blower, NUTRIENT_DOSE pumps) or moved
# onto real units (litho tools A-M-284; REMIN/BLOW_MOLD/ELECTRODE_COAT designs A-M-285). Owner locks stay.
PENDING={
 'FUEL_CELL':'owner requirement lock AQS-REQ-KW-001 REQ-FC-CONT; not a vendor nameplate (ELEC unit task 02)',
 'MEOH_FC':'owner requirement lock AQS-REQ-KW-001 REQ-MEOH-FC-CONT 0.5-2 kW_dc mid-band stand-in (SI-DMFC-01 class)',
}
NULL_OK={'HYDRO_SET':'charge/discharge kW model incomplete - honest incomplete (WP-A4, AQS-ESS-001)',
         'MEOH_TANK':'inventory store; no continuous kW (fuel to MEOH_FC)'}
def classify(u, kw, note):
    if kw is None: return ('null', NULL_OK.get(u, 'no continuous kW by design'))
    if u in PENDING: return ('pending', 'study share - basis pending: '+PENDING[u])
    if note and any(t in note for t in TOK): return ('calculated', note)
    return ('pending', 'study share - basis pending: no calculation cited on the graph stamp (unit task 02)')
rows=[]
for n in g['nodes']:
    ck=n.get('continuous_kw')
    if n.get('presence')!='present' or not isinstance(ck,dict): continue   # scalar bare ints were converted by write_graph X-ELS-02
    u=n['unit_id']; kw=ck.get('value'); note=ck.get('note') or ''
    cls,b=classify(u,kw,note)
    rows.append({'unit':u,'sector':n.get('sector_id') or '—','role':n.get('electrical_role') or '—','kw':kw,
                 'calc':(kw if cls=='calculated' else None),'cls':cls,'basis':b})
for r in ew:   # EW cells: DC at the electrode, behind the RECTIFIER bounding AC row (AQS-ELEC-004)
    rows.append({'unit':r['cell'],'sector':'WET','role':'load','kw':(N.get(r['cell'],{}).get('continuous_kw') or {}).get('value') if isinstance(N.get(r['cell'],{}).get('continuous_kw'),dict) else None,
                 'calc':r['P_kW'],'cls':'calculated','basis':'AQS-DUTY-051 DC at the bounding current; fed from RECTIFIER (DC, not in the AC sum)'})
have={r['unit'] for r in rows}
for e in g['edges']:   # bus-fed loads whose node carries no continuous_kw stamp (study stubs): visible via their SF-* feed
    u=e.get('to_unit_id')
    if (e.get('from_unit_id')!='SOL_ARK_60K' or e.get('presence')!='present' or 'elec' not in (e.get('layers') or [])
            or u in have or u=='BOUNDARY_EXPORT' or u in DC_BEHIND): continue
    r=(e.get('rate') or {}).get('value')
    if not isinstance(r,(int,float)) or r<=0: continue
    n=N.get(u) or {}
    cls,b=classify(u,r,(n.get('continuous_kw') or {}).get('note') if isinstance(n.get('continuous_kw'),dict) else None)
    rows.append({'unit':u,'sector':n.get('sector_id') or '—','role':n.get('electrical_role') or 'load','kw':float(r),
                 'calc':(float(r) if cls=='calculated' else None),'cls':cls,'basis':b+'; kW from the '+e['stream_id']+' feed (node has no continuous_kw stamp)'})
    have.add(u)
rows.sort(key=lambda r:(r['calc'] is None,-(r['calc'] if r['calc'] is not None else (r['kw'] or 0))))
nc=sum(1 for r in rows if r['cls']=='calculated'); npr=[r for r in rows if r['cls']=='pending']; nn=sum(1 for r in rows if r['cls']=='null')
# connected AC load: calculated + pending rows that are loads (generation/storage/bus excluded; EW DC behind RECTIFIER excluded)
loads=[r for r in rows if r['cls']!='null' and r['role'] not in ('generation','storage','bus') and r['unit'] not in DC_BEHIND and (r['kw'] or 0)>0]
conn=sum(r['kw'] for r in loads); ckw=sum(r['kw'] for r in loads if r['cls']=='calculated'); pkw=conn-ckw
cen=collections.Counter(); cens=collections.defaultdict(lambda: collections.Counter())
for r in rows:
    cen[r['cls']]+=1; cens[r['sector']][r['cls']]+=1
gsum=sum(r['kw'] or 0 for r in loads); csum=sum((r['calc'] if r['calc'] is not None else r['kw'] or 0) for r in loads)
pct=100.0*ckw/conn if conn else 0.0
pending_list='; '.join(f"{r['unit']} {r['kw']:.3f} kW" for r in sorted(npr,key=lambda r:-(r['kw'] or 0)))
out=[f"""# Load list

Document number: AQS-ELEC-003
Revision: B
Date: 2026-10-19
Authority: AQS-PLAN-007 X-ELS-02; graph sha256 {hashlib.sha256(open('flow_graph/plant_flow_graph.json','rb').read()).hexdigest()[:12]}. Generated by `docs-authority/_load_list.py`. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Graph values beside calculated values where a sizing exists. | 2026-10-15 |
| B | X-ELS-02 promotion pass (A-M-275): node stamps aligned to their calculations by write_graph load-basis stamping (MFG_SHOP tool list, LEACH_CSTR_1 agitator, reactor/sanitation feeds, WS_PEROX cell, ZNBR2 discharge rating, GEO_HP lift/COP, foundry notes); provenance classified from the graph notes; explicit pending residuals listed. | 2026-10-19 |

Status. {nc} of {len(rows)} rows carry a calculated basis. Connected AC load {conn:.1f} kW: {ckw:.1f} kW calculated ({pct:.1f} %), {pkw:.1f} kW explicit study shares. {len(npr)} rows are study shares - basis pending and keep X-ELS-02 OPEN: {pending_list}. {nn} rows are null by design. Where a row is calculated the graph continuous_kw IS the calculated value (Rev B promotion, A-M-275); pending rows keep their study value with the reason in the Basis column.

Loads: graph sum {gsum:.1f} kW; calculated-substituted sum {csum:.1f} kW.

## Census by sector

| Sector | calculated | pending | null | rows |
| --- | --- | --- | --- | --- |"""]
for s in sorted(cens):
    c=cens[s]; out.append(f"| {s} | {c['calculated']} | {c['pending']} | {c['null']} | {sum(c.values())} |")
out.append(f"| **total** | **{cen['calculated']}** | **{cen['pending']}** | **{cen['null']}** | **{len(rows)}** |")
out.append("")
out.append("| Unit | Role | Graph kW | Calculated kW | Basis |")
out.append("| --- | --- | --- | --- | --- |")
for r in rows:
    cs = '' if r['calc'] is None else f"{r['calc']:.3f}"
    out.append(f"| {r['unit']} | {r['role']} | {(r['kw'] or 0):.3f} | {cs} | {r['basis']} |")
# JSON sidecar (U2a): the machine face of the same table. kW values are quantised to the 3 decimals
# the markdown table publishes, so consumers of the json reproduce the markdown-derived numbers exactly.
sidecar={'_generated_from': {'graph_sha256': hashlib.sha256(open('flow_graph/plant_flow_graph.json','rb').read()).hexdigest(), 'generator': 'docs-authority/_load_list.py'},
         'rows': [{'unit': r['unit'], 'role': r['role'], 'kw': round(r['kw'] or 0, 3), 'calc_kw': (None if r['calc'] is None else round(r['calc'], 3)),
                   'basis': r['basis'], 'class': r['cls'], 'sector': r['sector']} for r in rows],
         'summary': {'calculated': nc, 'pending': len(npr), 'null': nn, 'rows': len(rows),
                     'graph_sum_kW': round(gsum, 1), 'calc_sum_kW': round(csum, 1),
                     'connected_load_kW': round(conn, 1), 'connected_calculated_kW': round(ckw, 1),
                     'connected_calculated_pct': round(pct, 1),
                     'by_sector': {s: dict(cens[s]) for s in sorted(cens)}}}
json.dump(sidecar, open('docs-authority/LOAD_LIST.json', 'w'), indent=1)
open('docs-authority/LOAD_LIST.md','w').write('\n'.join(out)+'\n')
print(f"{nc}/{len(rows)} calculated; pending {len(npr)} ({pkw:.1f} kW); connected {conn:.1f} kW, {pct:.1f}% calculated")
for s in sorted(cens): print(f"  {s:6s} calc {cens[s]['calculated']:3d} pending {cens[s]['pending']:2d} null {cens[s]['null']:2d}")
