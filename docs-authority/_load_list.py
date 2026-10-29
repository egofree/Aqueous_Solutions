"""AQS-ELEC-003 load list, Rev C (X-ELS-02). Every present node with continuous_kw is classified by the
basis its own graph stamp cites (authoritative census): 'calculated' when the note names the sizing
module / drivers key / transfer function / duty sheet that produced the kW; 'standby-zero' for the N+1
alternate rows that carry the A-M-283 policy basis (design-day zero apart from stated controls
parasitics; the connected rating rides params.design); 'owner-lock' for the AQS-REQ-KW-001 owner
requirement locks (FUEL_CELL, MEOH_FC) - requirement inputs, not calculations, the only census rows that
are documented without a calculation behind them (A-M-301); 'study share - basis pending <reason>' for
any residual that has none of the above (want: none); 'null by design' for stores with no continuous kW.
Rev C closes the census: the 2026-10-19 pending list collapses to the two owner locks plus the A-M-283
standby policy rows, and the classifier catches the A-M-297/299 tool-train and dosing-skid calculations
via their document-number citation tokens. Rev B had promoted the node stamps through write_graph
X-ELS-02 load-basis stamping (A-M-275), so the graph value IS the calculated value where classified
calculated; Rev A showed graph and calc side by side. EW cells are listed from _ew_sizing (DC behind
RECTIFIER, not in the AC sum). Writes docs-authority/LOAD_LIST.md (display) and docs-authority/
LOAD_LIST.json (machine sidecar read by _one_line.py; U2a interlock transport)."""
import json, subprocess, hashlib, collections
g=json.load(open('flow_graph/plant_flow_graph.json'))
N={n['unit_id']:n for n in g['nodes']}
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['rows']
DC_BEHIND={r['cell'] for r in ew}
# Citation tokens: a graph continuous_kw note carrying one of these names its calculation (X-ELS-02 rule,
# A-M-275). LOCKS/standby-zero take precedence, so a lock or policy note that names a document does not
# misclassify. Rev C adds the A-M-297/299 document numbers (FAB tool train, NUT dosing skid) and the CRC_SI
# driver key the CZ charge cites.
TOK=('AQS-DUTY-','AQS-DSN-','AQS-NOTE-PV-REBASE','X-PAR-','X-MFG-','X-SAN-','roof_close','Faraday','DLI',
     'kWh/m3','kWh/kg','/ 24 h','house_scrubbers','NFPA 110','AQS-ELEC-008','AQS-ELEC-004','AQS-PWR-001','latent','COP',
     'AQS-EQP-FAB','AQS-EQP-NUT','CRC_SI')
# Owner requirement locks (AQS-REQ-KW-001): owner-stated continuous ratings, calculation opens with the
# owning unit task. The only census rows documented without a calculation behind them (A-M-301).
LOCKS={
 'FUEL_CELL':'AQS-REQ-KW-001 REQ-FC-CONT owner requirement lock; not a vendor nameplate (ELEC unit task 02)',
 'MEOH_FC':'AQS-REQ-KW-001 REQ-MEOH-FC-CONT owner requirement lock: 0.5-2 kW_dc mid-band stand-in (SI-DMFC-01 class)',
}
NULL_OK={'HYDRO_SET':'charge/discharge kW model incomplete - honest incomplete (WP-A4, AQS-ESS-001)',
         'MEOH_TANK':'inventory store; no continuous kW (fuel to MEOH_FC)'}
def classify(u, kw, note):
    if kw is None: return ('null', NULL_OK.get(u, 'no continuous kW by design'))
    if u in LOCKS: return ('owner-lock', 'owner requirement lock (AQS-REQ-KW-001): '+LOCKS[u])
    if note and 'standby-zero on the design day' in note: return ('standby-zero', note)
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
    rows.append({'unit':r['cell'],'sector':N.get(r['cell'],{}).get('sector_id') or 'DIGESTER','role':'load','kw':(N.get(r['cell'],{}).get('continuous_kw') or {}).get('value') if isinstance(N.get(r['cell'],{}).get('continuous_kw'),dict) else None,
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
nc=sum(1 for r in rows if r['cls']=='calculated'); nn=sum(1 for r in rows if r['cls']=='null')
cen=collections.Counter(); cens=collections.defaultdict(lambda: collections.Counter())
for r in rows:
    cen[r['cls']]+=1; cens[r['sector']][r['cls']]+=1
nsb=cen['standby-zero']; nol=cen['owner-lock']; npr=[r for r in rows if r['cls']=='pending']
# connected AC load: non-null rows that are loads (generation/storage/bus excluded; EW DC behind RECTIFIER excluded)
loads=[r for r in rows if r['cls']!='null' and r['role'] not in ('generation','storage','bus') and r['unit'] not in DC_BEHIND and (r['kw'] or 0)>0]
conn=sum(r['kw'] for r in loads); ckw=sum(r['kw'] for r in loads if r['cls']=='calculated'); skw=sum(r['kw'] for r in loads if r['cls']=='standby-zero'); pkw=conn-ckw-skw
if -0.005<pkw<0.005: pkw=0.0   # float residue; the class split is exhaustive on the loads
gsum=sum(r['kw'] or 0 for r in loads); csum=sum((r['calc'] if r['calc'] is not None else r['kw'] or 0) for r in loads)
pct=100.0*ckw/conn if conn else 0.0
lock_list='; '.join(f"{r['unit']} {r['kw']:.3f} kW" for r in sorted([r for r in rows if r['cls']=='owner-lock'],key=lambda r:-(r['kw'] or 0)))
out=[f"""# Load list

Document number: AQS-ELEC-003
Revision: D
Date: 2026-10-29
Generated by `docs-authority/_load_list.py` from the plant graph (sha256 {hashlib.sha256(open('flow_graph/plant_flow_graph.json','rb').read()).hexdigest()[:12]}), with a JSON twin `docs-authority/LOAD_LIST.json`. Do not edit by hand; change the generator or the graph and run `python3 -m flow_graph.param.regen`.
Authority: AQS-PLAN-007 task X-ELS-02. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: the graph load of each unit beside its calculated load where a sizing exists | 2026-10-15 |
| B | Graph loads aligned to their calculations; the basis of each load classified from the graph notes; open residuals listed (X-ELS-02, A-M-275) | 2026-10-19 |
| C | Remaining residuals closed: tool-train and dosing-skid loads calculated, standby units classified as policy rows, the fuel cells recorded as owner requirements, the ground loop circulator added (A-M-301, A-M-283, A-M-317) | 2026-10-21 |
| D | Purpose and scope added; the status written as sentences; tables numbered | 2026-10-29 |

## 1. Purpose and scope

This page lists the continuous electrical load of every unit on the plant graph and states the basis of each load. It is the load input to the power sizing AQS-ELEC-007 (`POWER_SIZING.md`) and the one-line diagram AQS-ELEC-002 (`ONE_LINE.md`).

Each row has one of five bases. A calculated row takes its load from a sizing calculation, and the graph value is that calculated value (A-M-275). A standby row belongs to a standby unit of an N+1 pair; it draws nothing on the design day except its stated control load, and its connected rating is in the design parameters of the unit (A-M-283). An owner requirement row takes a load the owner has set in AQS-REQ-KW-001 (`CONTINUOUS_KW_REQUIREMENTS.md`) and has no calculation behind it (A-M-301). A null row has no load by design. A pending row has none of these bases.

## 2. Status

Of the {len(rows)} rows, {nc} are calculated, {nsb} are standby rows, {nol} are owner requirements and {nn} are null. {('No row is pending.' if not npr else f'{len(npr)} rows are pending.')} The owner requirements are: {lock_list}.

The connected alternating-current load is {conn:.1f} kW. Of this, {ckw:.1f} kW ({pct:.1f} %) is calculated, {skw:.2f} kW is the control load of standby units, and {pkw:.2f} kW is pending. The graph loads sum to {gsum:.2f} kW, and the sum with each calculated value in place of the graph value is {csum:.2f} kW.

## 3. Census by sector

Table 3.1 counts the rows of each basis in each sector of the graph.

Table 3.1. Rows by sector and basis

| Sector | Calculated | Standby | Owner requirement | Pending | Null | Rows |
| --- | --- | --- | --- | --- | --- | --- |"""]
for s in sorted(cens):
    c=cens[s]; out.append(f"| {s} | {c['calculated']} | {c['standby-zero']} | {c['owner-lock']} | {c['pending']} | {c['null']} | {sum(c.values())} |")
out.append(f"| Total | {cen['calculated']} | {cen['standby-zero']} | {cen['owner-lock']} | {cen['pending']} | {cen['null']} | {len(rows)} |")
out += ["", "## 4. Loads by unit", "", "Table 4.1 gives the graph load and, where one exists, the calculated load of each unit, with its basis.", "", "Table 4.1. Loads by unit", ""]
out.append("| Unit | Role | Graph load (kW) | Calculated load (kW) | Basis |")
out.append("| --- | --- | --- | --- | --- |")
for r in rows:
    cs = '' if r['calc'] is None else f"{r['calc']:.3f}"
    bs = (r['basis'] or '').replace('|', '/')   # stamp notes may carry ' | ' separators; keep the table cell single-column
    out.append(f"| {r['unit']} | {r['role']} | {(r['kw'] or 0):.3f} | {cs} | {bs} |")
# JSON sidecar (U2a): the machine face of the same table. kW values are quantised to the 3 decimals
# the markdown table publishes, so consumers of the json reproduce the markdown-derived numbers exactly.
sidecar={'_generated_from': {'graph_sha256': hashlib.sha256(open('flow_graph/plant_flow_graph.json','rb').read()).hexdigest(), 'generator': 'docs-authority/_load_list.py'},
         'rows': [{'unit': r['unit'], 'role': r['role'], 'kw': round(r['kw'] or 0, 3), 'calc_kw': (None if r['calc'] is None else round(r['calc'], 3)),
                   'basis': (r['basis'] or '').replace('|', '/'), 'class': r['cls'], 'sector': r['sector']} for r in rows],
         'summary': {'calculated': nc, 'pending': len(npr), 'standby_zero': nsb, 'owner_lock': nol, 'null': nn, 'rows': len(rows),
                     'graph_sum_kW': round(gsum, 2), 'calc_sum_kW': round(csum, 2),
                     'connected_load_kW': round(conn, 1), 'connected_calculated_kW': round(ckw, 1),
                     'connected_standby_kW': round(skw, 1), 'connected_study_kW': round(pkw, 1),
                     'connected_calculated_pct': round(pct, 1),
                     'by_sector': {s: dict(cens[s]) for s in sorted(cens)}}}
json.dump(sidecar, open('docs-authority/LOAD_LIST.json', 'w'), indent=1)
open('docs-authority/LOAD_LIST.md','w').write('\n'.join(out)+'\n')
print(f"{nc}/{len(rows)} calculated; standby-zero {nsb}; owner locks {nol}; pending {len(npr)} ({pkw:.1f} kW); connected {conn:.1f} kW, {pct:.1f}% calculated, {skw:.1f} kW standby parasitics")
for s in sorted(cens): print(f"  {s:6s} calc {cens[s]['calculated']:3d} standby {cens[s]['standby-zero']:2d} locks {cens[s]['owner-lock']:2d} pending {cens[s]['pending']:2d} null {cens[s]['null']:2d}")
