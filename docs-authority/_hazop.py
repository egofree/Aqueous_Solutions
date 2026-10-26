"""AQS-SAF-001 HAZOP worksheets (X-SAF-01, rev A study, A-M-195). Method IEC61882_2016: one node per unit (its P&ID), parameters flow,
pressure, temperature, level and composition, guide words No/Less, More, High, Low, Reverse, Other-than. Safeguards are read from the
design: relief case (AQS-SAF-004/005), open vent (API 2000), instruments of AQS-CTL-001, fire and gas detection (AQS-SAF-005), redundancy
(AQS-RED-001). Where no safeguard exists an action is raised with the task that closes it; trip actions go to X-CTL-03 (IEC61511_2016).
Every action leaves this generator with a disposition (2026-10-19 honesty pass): closed against a cited artifact (the unit duty sheet
section 6 for relief, AQS-CTL-001 for indication), 'open' for the SIF pass, or 'open - tracked HA-nnn' in the AQS-SAF-008 register with
its owner task in AQS-PLAN-007 terms. No row is silently open.
Writes docs-authority/HAZOP.md, docs-authority/hazop_actions.csv and docs-authority/HAZOP_ACTION_REGISTER.md (AQS-SAF-008).
Run: python3 docs-authority/_hazop.py, then _sif.py."""
import csv, json, os, re, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R)
from flow_graph.param.refs import cite
for k in ('IEC61882_2016', 'IEC61511_2016'): cite(k)
g = json.load(open('flow_graph/plant_flow_graph.json')); N = {n['unit_id']: n for n in g['nodes']}
INS = collections.defaultdict(set)
for r in csv.DictReader(open('docs-authority/inventory/INSTRUMENT_INDEX.csv')): INS[r['unit']].add(r['tag'].split('-')[-2])
CHK = {r['unit'] for r in csv.DictReader(open('docs-authority/inventory/OTHER_INVENTORY.csv')) if r['item'] == 'check valve'}
PUMPED = {r['unit'] for r in csv.DictReader(open('docs-authority/inventory/MOTOR_INVENTORY.csv')) if 'pump' in r['device'].lower()}
UP = collections.defaultdict(set)
for e in g['edges']:
    if e['presence'] == 'present' and e.get('phase') == 'L' and (e['rate']['value'] or 0) > 0: UP[e['to_unit_id']].add(e['from_unit_id'])
inflow = collections.Counter(e['to_unit_id'] for e in g['edges'] if e['presence'] == 'present' and (e['rate']['value'] or 0) > 0)
liq = {e['to_unit_id'] for e in g['edges'] if e['presence'] == 'present' and e.get('phase') == 'L' and (e['rate']['value'] or 0) > 0}
GASFIRE = {'CRYO_H2', 'CRYO_O2', 'CRYO_CO2'}; HOT = ('PYRO', 'FURNACE', 'MELT', 'AFTERBURN', 'HTC', 'SIC', 'EVAP', 'DRYER')
nodes = []; acts = []
for n in g['nodes']:
    u = n['unit_id']; p = n.get('params') or {}; c = n.get('class') or ''
    if p.get('presence') == 'absent' or c in ('boundary', 'building', 'header', 'recycle_pipe', 'farm', 'rectifier', 'inverter', 'pv', 'product') and u not in ('HNO3', 'ACEX', 'FORM', 'ALD', 'MEAM', 'HTC', 'BUCL', 'IMID'): continue
    if not inflow[u]: continue
    rb = p.get('relief_basis') or {}; I = INS[u]; W = []
    def row(par, gw, cause, cons, sg, act=None, task=None):
        W.append((par, gw, cause, cons, sg or 'none', act or '-'))
        if act: acts.append((u, par, gw, act, task))
    press = 'P1_kPa_abs' in rb
    pm = u in PUMPED
    row('flow', 'No/Less', 'upstream unit stopped, pump trip, blocked line', 'loss of duty' + ('; dry-running pump' if pm else ''), 'FT low-flow alarm' if 'FT' in I else ('no pump on this unit; loss of duty shows at the downstream flow transmitter' if not pm else None),
        None if ('FT' in I or not pm) else 'pump dry-run protection (low-flow or low-level interlock)', 'X-CTL-03')
    row('flow', 'More', 'control valve fails open, upstream surge', 'overfill or overpressure', ('LSH trip' if 'LSH' in I else '') + ('; PSV' if press else ('; open vent' if rb.get('case') == 'atmospheric' else '')) or None,
        None if ('LSH' in I or press or rb.get('case') == 'atmospheric') else 'high-level or high-flow protection', 'X-CTL-03')
    sg = (f"PSV {p.get('relief_mm')} mm, case: {str(rb.get('case'))[:60]}" if press else f"open vent DN{rb.get('vent_DN', '?')} (API 2000)") if rb else None
    row('pressure', 'High', 'blocked outlet; fire; thermal expansion', 'loss of containment', sg, None if sg else 'relief case', 'X-SAF-04')
    if u in GASFIRE: row('pressure', 'High', 'external fire on the tube bank', 'wall rupture before relief', 'fire-case PSV per half; flame detection; water spray; depressuring (AQS-SAF-005)')
    if press: row('pressure', 'Low', 'leak, PSV lift, downstream draw', 'air ingress (H2: flammable mixture) or loss of store', 'PT low alarm' + ('; H2 gas detection (AQS-SAF-005)' if u == 'CRYO_H2' else ''),
        'PT low-low trip isolating the bank' if u in GASFIRE else None, 'X-CTL-03')
    hot = any(k in u for k in HOT) or (p.get('design') or {}).get('T_C', 25) > 100
    row('temperature', 'High', 'heater control failure, loss of cooling', 'overtemperature of the wall or product', 'TE high alarm' if 'TE' in I else None,
        'independent high-temperature trip on the heater' if hot else (None if 'TE' in I else 'temperature indication'), 'X-CTL-03' if hot else 'detail P&ID')
    if u.startswith('CRYO') or c == 'cold_box': row('temperature', 'Low', 'refrigeration overrun, expansion', 'embrittlement of non-austenitic parts', '316L throughout (A-M-167); TE low alarm')
    if u in liq: row('level', 'High', 'inflow above outflow, outlet blocked', 'overflow to the bund', 'LSH trip of the feed' if 'LSH' in I else None, None if 'LSH' in I else 'high-level switch', 'X-CTL-03')
    if u in liq: row('level', 'Low', 'outlet pump runs on, leak', 'pump dry-running', 'LT low alarm' if 'LT' in I else None, None if 'LT' in I else 'level indication', 'detail P&ID')
    up_p = UP[u] & PUMPED
    if UP[u]: row('flow', 'Reverse', 'downstream pressure above upstream on a pump stop', 'back-flow of incompatible liquor', ('check valve at the pump discharge of ' + ', '.join(sorted(up_p & CHK))) if up_p & CHK else ('gravity or vented inlets: no back-pressure source' if not up_p else None),
        None if (up_p & CHK or not up_p) else 'check valve on the pumped inlet', 'X-PIP')
    row('composition', 'Other than', 'wrong reagent connected, upstream upset', 'incompatible reaction', 'incompatible storage separation (AQS-BLD-011); dedicated couplings', None)
    nodes.append((u, c, W))
# --- Disposition (X-SAF-01, 2026-10-19 honesty pass) --------------------------------------------
# relief case: closed by the unit's own duty sheet section 6 (case or atmospheric statement - the same artifact the
#   unit task 07 check reads; X-SAF-03 item C7). Tracked where no duty sheet exists yet.
# indication actions: closed by the loop tag in AQS-CTL-001 (X-CTL-01). Tracked where the unit has no loop yet.
# trip actions: stay 'open' here and close in the SIF pass (AQS-CTL-003, _sif.py).
DUTY6 = {u for u in N if os.path.exists(f'docs-authority/duties/{u}.md')
         and re.search(r'^6\. Relief', open(f'docs-authority/duties/{u}.md').read(), re.M)}
OPEN_ACT = {'relief case': 'state the relief case or atmospheric vent in the duty sheet (unit task 07)',
            'temperature indication': 'add the temperature indication loop to AQS-CTL-001 (unit task 08)',
            'level indication': 'add the level indication loop to AQS-CTL-001 (unit task 08)'}
def disposition(a):
    u, par, gw, act, task = a
    if act == 'relief case':
        return (f'closed: docs-authority/duties/{u}.md section 6 names the case or atmospheric statement (X-SAF-03 C7)'
                if u in DUTY6 else None)
    if act in ('temperature indication', 'level indication'):
        tag = 'TE' if act.startswith('temperature') else 'LT'
        return (f'closed: {tag} loop of {u} in AQS-CTL-001 (X-CTL-01)' if tag in INS[u] else None)
    return 'open'
TRK = []; ST = []
for i, a in enumerate(acts):
    s = disposition(a)
    if s is None:
        u = a[0]; k = '07' if a[1] == 'pressure' else '08'
        s = f"open - tracked HA-{len(TRK)+1:02d} (AQS-SAF-008)"
        TRK.append((f'HA-{len(TRK)+1:02d}', f'HZ-{i+1:03d}', u, f'{a[1]} / {a[2]}', OPEN_ACT.get(a[3], a[3]), f"{N[u]['sector_id']}-{u}-{k}"))
    ST.append(s)
with open('docs-authority/hazop_actions.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['action_id', 'node', 'parameter', 'guide_word', 'action', 'closing_task', 'status']); w.writerows([(f'HZ-{i+1:03d}', *a, ST[i]) for i, a in enumerate(acts)])
n_trk = len(TRK); n_cls = sum(1 for s in ST if s.startswith('closed')); n_sif = len(acts) - n_trk - n_cls
reg = ['# HAZOP action register', '', 'Document number: AQS-SAF-008', 'Revision: A', 'Date: 2026-10-19',
       'Authority: AQS-PLAN-007 X-SAF-01. Generated by `docs-authority/_hazop.py` together with `docs-authority/hazop_actions.csv`.', '',
       'Every HAZOP action is either closed against a cited artifact (the status column of hazop_actions.csv names it) or listed here',
       'with its owner task in AQS-PLAN-007 terms. No row is silently open. A register item closes when its owner task issues the',
       'artifact - duty sheet section 6 for the relief items, the AQS-CTL-001 loop for the indication items - and this generator is',
       'rerun; the row then leaves this register.', '',
       'Handoff (not writable from the docs lane): the indication items need their TE/LT loops added to AQS-CTL-001 by the X-CTL-01',
       'lane (flow_graph/inventory/other.py) once setpoints exist; the relief items need the unit duty sheets (unit tasks 01/02 first).', '',
       '| Register id | HAZOP action | Node | Deviation | Open action | Owner task (AQS-PLAN-007) |', '|---|---|---|---|---|---|']
reg += [f'| {a} | {b} | {c} | {d} | {e} | {f} |' for a, b, c, d, e, f in TRK]
tail = (f'{n_trk} open engineering actions on {len({r[2] for r in TRK})} units: ' + ', '.join(sorted({r[2] for r in TRK})) + '.') if TRK else 'No open engineering actions.'
reg += ['', tail]
open('docs-authority/HAZOP_ACTION_REGISTER.md', 'w').write('\n'.join(reg) + '\n')
A = collections.Counter(a[3] for a in acts); TK = collections.Counter(a[4] for a in acts)
md = ['# HAZOP worksheets', '', 'Document number: AQS-SAF-001', 'Revision: A (study)', 'Date: 2026-10-16', 'Authority: AQS-PLAN-007 X-SAF-01. Generated by `docs-authority/_hazop.py`; actions in `docs-authority/hazop_actions.csv`. Method IEC61882_2016. A-M-195.', '',
        '| Rev | Description | Date |', '|---|---|---|',
        '| A | First issue: study HAZOP worksheets from the generated design. | 2026-10-16 |',
        '| B | Purpose and scope added per the documentation style guide (AQS-DOC-002); sections numbered. No deviation, cause, safeguard or action changed. | 2026-10-25 |', '',
        '## 1. Purpose and scope', '',
        'This page carries the study HAZOP worksheets: for every node of the generated design, the deviations, their causes and the safeguards, with the action list. It is a design-derived study HAZOP and does not replace a facilitated team HAZOP; the team review signs off rev B of the record. Method IEC 61882 (IEC61882_2016).', '',
        '## 2. Actions by kind', '',
      'This is a design-derived study HAZOP: deviations, causes and safeguards come from the generated design. It does not replace a facilitated team HAZOP; the team review signs off rev B.', '',
      f'{len(nodes)} nodes, {sum(len(x[2]) for x in nodes)} deviations, {len(acts)} actions: {n_cls} closed at issue against cited artifacts (duty sheet section 6 relief statements, X-SAF-03 C7; AQS-CTL-001 indication loops), {n_sif} trip actions close in the SIF pass (AQS-CTL-003, `docs-authority/_sif.py`), {n_trk} tracked open in the action register AQS-SAF-008 (`docs-authority/HAZOP_ACTION_REGISTER.md`) with owner tasks in plan terms.', '', '## 2. Actions by kind', '', 'Table 2.1. Actions by kind', '', '| Action | Count | Closing task |', '|---|---|---|']
md += [f'| {k} | {v} | {", ".join(sorted({a[4] for a in acts if a[3] == k}))} |' for k, v in A.most_common()]
md += ['', '## Worksheets', '']
for u, c, W in nodes:
    md += [f'### {u} ({c})', '', '| Parameter | Guide word | Cause | Consequence | Safeguard | Action |', '|---|---|---|---|---|---|'] + [f'| {a} | {b} | {cc} | {d} | {e} | {f} |' for a, b, cc, d, e, f in W] + ['']
open('docs-authority/HAZOP.md', 'w').write('\n'.join(md) + '\n'); print(len(nodes), len(acts), dict(A), 'closed', n_cls, 'sif-pass', n_sif, 'tracked', n_trk)
