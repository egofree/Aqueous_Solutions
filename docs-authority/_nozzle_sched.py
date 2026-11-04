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

Terminal service rows (audit 2026-11-03). Electrical and HVAC service connections carry
their own row class, appended by the same pass:

- Power terminals: every present unit fed by an SF- (plant 480 V AC distribution),
  IA-DC (rectifier DC bus) or IA-TRIM (electric trim) edge gets one row per power
  circuit, and ZNBR2 gets the row for its electric round-trip loss at the skid
  terminal. A unit at standby_rated carries no row (its feed is unrated until the
  standby basis issues the rating), a unit with no schedule file keeps no file (the
  rule above), and a unit whose schedule already carries a conductor or power row
  keeps it (EW_1's "rectifier into the cell", the issued conductor-row precedent). Row basis: size carries the AQS-PIP-004 line-list
  classification verbatim (`cable` - a circuit, no bore); the rating column carries the
  plant-wide Class 150 convention verbatim with no flange, breaker or conductor rating
  implied (branch feeders are rated per load in AQS-ELEC-010; the unit feed itself is
  not separately rated); face and height are the top-face placeholder pending design,
  which leaves the issued side-face connection packs unchanged.
- HVAC terminals: three HVAC and heat service edges land where no schedule row
  existed, at the terminal unit the service map names (chilled water and tempered
  make-up air on HABITATION, PEM stack heat at the H2O_ELYZ skid). Row basis as above;
  face and height from the edge direction at the house placeholder elevations.
- ZNBR2 row N8 (round-trip loss) covers the piped heat edge IA-ZNBR-HEAT (the DN15
  heat loop per AQS-PIP-004); the electric loss IA-ZNBR-LOSS is a separate circuit and
  gets the power-terminal row. Row N4 (charge into the battery) matches no graph edge;
  it is a schedule-only row, named in the change record.
Run: python3 docs-authority/_nozzle_sched.py"""
import csv, json, os, collections, re
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

# ---------------------------------------------------------------- terminal service rows
# One row per electrical or HVAC service connection, appended to the existing schedule
# file (no new files, no standby_rated units). See the module header for the basis.
_POWER_TERMINAL_UNIT = {           # stream_id -> unit whose schedule carries the terminal
    'IA-ZNBR-LOSS': 'ZNBR2',       # the electric round-trip loss leaves at the skid terminal
}                                  # (the edge's other end is the export accounting node)
_HVAC_TERMINAL = {                 # stream_id -> unit whose schedule carries the terminal
    'IA-ADS-CHW': 'HABITATION',    # chilled water into the habitation loop
    'IA-MAU-AIR': 'HABITATION',    # tempered make-up air into the habitation loop
    'SQ-H2O_ELYZ-Q4': 'H2O_ELYZ',  # PEM stack heat, leaving at the skid
}
_IS_POWER_ROW = re.compile(r'rectifier|bus bar|480 V|power|terminal|conductor', re.I)
_node = {n['unit_id']: n for n in P}
_by_sid = {e['stream_id']: e for e in g['edges'] if e.get('presence') == 'present'}
power = [e for e in g['edges'] if e.get('presence') == 'present'
         and 'elec' in (e.get('layers') or [])
         and (e.get('rate') or {}).get('unit') == 'kW'
         and (e['stream_id'].startswith(('SF-', 'IA-DC', 'IA-TRIM'))
              or e['stream_id'] in _POWER_TERMINAL_UNIT)]
# Units whose schedule carried a conductor or power row before this pass keep it and
# take no appended row (EW_1's "rectifier into the cell", the issued precedent). The
# other units get one row per power circuit: LEACH_CSTR_1 and GLASS_DIGEST each carry
# a feed and an electric-trim circuit, and one row must not cover two edges.
_pre_covered = set()
for e in power:
    u = e['to_unit_id']
    if u in _pre_covered:
        continue
    p = f'docs-authority/nozzles/{u}.csv'
    if os.path.exists(p):
        body = [r for r in list(csv.reader(open(p)))[1:] if r and r[0].strip()]
        if any(_IS_POWER_ROW.search(r[3]) for r in body if len(r) > 3):
            _pre_covered.add(u)
n_term = 0
for e in sorted(power, key=lambda e: e['stream_id']):
    sid = e['stream_id']
    u = _POWER_TERMINAL_UNIT.get(sid, e['to_unit_id'])
    n = _node.get(u)
    if not n or n.get('presence') != 'present' or u in _pre_covered:
        continue
    if (n.get('params') or {}).get('envelope', {}).get('state') == 'standby_rated':
        continue        # hold: unrated standby feed (change record names the unit set)
    p = f'docs-authority/nozzles/{u}.csv'
    if not os.path.exists(p):
        continue        # hold: the no-file rule stands (change record names the unit set)
    rows = list(csv.reader(open(p)))
    body = [r for r in rows[1:] if r and r[0].strip()]
    if any(sid in r[3] for r in body if len(r) > 3):
        continue        # this circuit is already scheduled
    tag = max([int(r[0][1:]) for r in body if r[0].startswith('N') and r[0][1:].isdigit()] + [0])
    size = _LN.get(sid, ('cable', ''))[0]           # line-list classification, verbatim
    svc = f'power terminal ({sid}, {e.get("carries") or ""})'
    if e['from_unit_id'] == u:                      # an outgoing circuit: outlet at the skid
        face, h = 'outlet', H['outlet']
    else:
        face, h = 'top', H['top']
    with open(p, 'a', newline='') as fh:
        csv.writer(fh).writerow([f'N{tag + 1}', size, 'Class 150', svc, face, str(h)])
    n_term += 1
    print(f'term {u}: N{tag + 1} power terminal ({sid})')
for sid, u in _HVAC_TERMINAL.items():
    e = _by_sid.get(sid)
    if not e:
        continue
    p = f'docs-authority/nozzles/{u}.csv'
    if not os.path.exists(p):
        continue
    rows = list(csv.reader(open(p)))
    body = [r for r in rows[1:] if r and r[0].strip()]
    if any(sid in r[3] for r in body if len(r) > 3):
        continue        # already scheduled
    face = 'inlet' if e['to_unit_id'] == u else 'outlet'
    tag = max([int(r[0][1:]) for r in body if r[0].startswith('N') and r[0][1:].isdigit()] + [0])
    size = _LN.get(sid, ('cable', ''))[0]
    svc = f'service terminal ({sid}, {e.get("carries") or ""})'
    with open(p, 'a', newline='') as fh:
        csv.writer(fh).writerow([f'N{tag + 1}', size, 'Class 150', svc, face, str(H[face])])
    n_term += 1
    print(f'term {u}: N{tag + 1} service terminal ({sid})')
print(f'terminal service rows appended {n_term}')
