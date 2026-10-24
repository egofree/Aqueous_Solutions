"""Unit task 04: nozzle schedules with full process coverage (AQS-PLAN-007; AQS-STD-001 section 4).

The issued schedules in docs-authority/nozzles/<UNIT>.csv (hand rows, commit 03f3ed5 era) are
preserved verbatim; this generator only APPENDS rows missing for coverage. Coverage rule (the
T04 check in _task_plan_gen.py, the same connection set): every present process connection of
the unit - mass kg/d edges plus HL-/thermal kW edges (cables are not nozzles) - has a row whose
service text equals the edge `carries` (the match rule _pid_sheets.py uses). Utility rows
(drain, vent) match no edge and stay allowed extras.

Appended-row basis:
- size: the AQS-PIP-004 line DN of the edge. AQS-PIP-003 basis: the piped bore is the nozzle
  bore basis; bores are NOT recalculated here. Rows for non-piped transfers carry the line
  list classification verbatim (e.g. `solids`: conveyor, bin or hand transfer; not piped).
- rating: Class 150 (the schedule class of the issued rows plant-wide).
- face: inlet / outlet, from the edge direction (to_unit = inlet).
- height_mm: the house placeholder elevations already used across the issued schedules -
  inlet 160, outlet 600, drain 50, vent 800 - pending the vessel design (unit tasks 02/06).
  Not a designed nozzle elevation.

A unit whose schedule file is absent entirely gets the file created with one row per process
connection plus the drain and vent utility rows (AQS-STD-001 section 4 "include the drain and
the vent"). Vessels with no piped process connection (kettle / precip / separator holds) get
the utilities-only file so the T04 note reads truthfully; machines with no piped process
connection get no file - nothing to schedule, nothing invented.
Run: python3 docs-authority/_nozzle_sched.py"""
import csv, json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
g = json.load(open('flow_graph/plant_flow_graph.json'))
P = [n for n in g['nodes'] if n.get('presence') == 'present']
_EU = collections.defaultdict(list)   # present edges touching each unit (the _task_plan_gen rule)
for _e in g['edges']:
    if _e.get('presence') == 'present':
        _EU[_e['to_unit_id']].append(_e); _EU[_e['from_unit_id']].append(_e)
def _noz_edges(u):   # connections a nozzle schedule must list: process mass edges + thermal kW edges (cables are not nozzles)
    out = []
    for e in _EU.get(u, ()):
        lay = e.get('layers') or []; un = (e.get('rate') or {}).get('unit')
        if 'mass' in lay and un == 'kg/d': out.append(e)
        elif un == 'kW' and (e['stream_id'].startswith('HL-') or 'thermal' in lay) and e.get('phase') not in ('E', 'electric') and 'elec' not in lay: out.append(e)
    return out
_LN = {}   # stream_id -> (DN, class) from AQS-PIP-004
for _l in open('docs-authority/LINE_LIST.md'):
    if _l.startswith('|'):
        _c = [x.strip() for x in _l.strip().strip('|').split('|')]
        if len(_c) >= 9 and _c[0] != 'Line' and not _c[0].startswith('-') and _c[0] not in _LN:
            _LN[_c[0]] = (_c[3], _c[4])
_VESSEL_ZERO = {'kettle', 'precip', 'separator', 'store'}   # utilities-only files where nothing is piped
H = {'inlet': 160, 'outlet': 600, 'bottom': 50, 'top': 800}
n_new = n_add = 0
for n in sorted(P, key=lambda n: n['unit_id']):
    u = n['unit_id']; p = f'docs-authority/nozzles/{u}.csv'
    conns = _noz_edges(u)
    rows = list(csv.reader(open(p))) if os.path.exists(p) else None
    if rows is not None:
        body = [r for r in rows[1:] if r and r[0].strip()]
    else:
        if not conns and n.get('class') not in _VESSEL_ZERO: continue   # machine with nothing piped: no file
        body = []
    have = collections.Counter(r[3] for r in body if len(r) > 3)
    need = collections.Counter(e.get('carries') or '' for e in conns)
    add = []
    for svc in [c for c in dict.fromkeys(e.get('carries') or '' for e in conns)]:   # first-seen order
        k = need[svc] - have.get(svc, 0)
        grp = sorted((e for e in conns if (e.get('carries') or '') == svc), key=lambda e: e['stream_id'])
        for e in grp[:k]:
            dn = _LN.get(e['stream_id'], ('MISSING', ''))[0]
            face = 'inlet' if e['to_unit_id'] == u else 'outlet'
            add.append([dn, 'Class 150', svc, face, str(H[face])])
    if body == [] and (conns or n.get('class') in _VESSEL_ZERO):   # new file: the standard's drain and vent are part of every issued schedule
        add += [['DN15', 'Class 150', 'drain', 'bottom', str(H['bottom'])], ['DN15', 'Class 150', 'vent', 'top', str(H['top'])]]
    if not add and rows is not None: continue
    tag = max([int(r[0][1:]) for r in body if r and r[0].startswith('N') and r[0][1:].isdigit()] + [0])
    out = (rows if rows is not None else [['tag', 'size', 'rating', 'service', 'face', 'height_mm']])[:]
    for a in add:
        tag += 1; out.append([f'N{tag}'] + a)
    w = csv.writer(open(p, 'w', newline='')); w.writerows(out)
    if rows is None: n_new += 1
    n_add += len(add)
    print(f'{"new " if rows is None else "add "}{u}: +{len(add)} rows ({sum(need.values())} process connections)')
print(f'files created {n_new}, rows appended {n_add}')
