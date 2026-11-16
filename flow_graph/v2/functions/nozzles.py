"""The nozzle-schedule family (family migration; reference writer
docs-authority/_nozzle_sched.py, ledger row `nozzle_sched`, section E, MIXED:
"split: coverage calc->checker; append-only CSV merge->renderer (hybrid)").

Unit task 04: nozzle schedules with full process coverage (AQS-PLAN-007;
AQS-STD-001 section 4). The issued schedules in docs-authority/nozzles/
<UNIT>.csv are hand+generated hybrid files: the hand rows (the commit 03f3ed5
era, since hand-migrated to the six-column face/height format) are preserved
verbatim and the generator only APPENDS rows missing for coverage. The
coverage rule (the T04 check, the same connection set): every present process
connection of the unit - mass kg/d edges plus HL-/thermal kW edges (cables
are not nozzles) - has a row whose service text equals the edge `carries`
(the match rule the P&ID sheets use). Utility rows (drain, vent) match no
edge and stay allowed extras.

Appended-row basis (the v1 module header, verbatim):
- size: the AQS-PIP-004 line DN of the edge (the line-list namespace's dn
  map; the piped bore is the nozzle bore basis, AQS-PIP-003 - bores are NOT
  recalculated here). Rows for non-piped transfers carry the classification
  verbatim (`cable` / `solids`).
- rating: Class 150 (the schedule class of the issued rows plant-wide).
- face: inlet / outlet, from the edge direction (to_unit = inlet).
- height_mm: the house placeholder elevations - inlet 160, outlet 600,
  drain 50, vent 800 - pending the vessel design. Not a designed elevation.

A unit whose schedule file is absent entirely gets the file created with one
row per process connection plus the drain and vent utility rows (AQS-STD-001
section 4). Vessels with no piped process connection (kettle / precip /
separator / store holds) get the utilities-only file; machines with no piped
process connection get no file.

Terminal service rows (audit 2026-11-03): every present unit fed by an SF- /
IA-DC / IA-TRIM power circuit gets one row per circuit, ZNBR2 the row for its
electric round-trip loss at the skid terminal, and the three HVAC and heat
service edges land at the terminal unit the service map names. A unit at
standby_rated carries no row (unrated standby feed), a unit with no schedule
file keeps no file, a unit whose schedule already carried a conductor or
power row keeps it (EW_1's issued conductor-row precedent), and a circuit
already scheduled stays.

Pure kernels, no graph state: schedule_rows() takes the committed-graph
structure, the line-list dn map, and the hand+generated schedule state as
{unit: rows-or-None} (rows: the full CSV rows incl. header; None: no file) -
the declared inputs['nozzle_schedules'] payload - and returns the post-merge
schedule state (None where the v1 wrote nothing). The committed tree is the
merge's own fixpoint (every file re-merges to itself: golden 1); an
enumerated change set drives the append behaviour (golden 2: drop a coverage
row, re-merge, the row re-appends at the next tag; a machine unit with no
file creates the full coverage set). The v1 stdout ledgers are session
output and do not port. Float-free: the kernel is row arithmetic and
string work only. Pure: no I/O, no wall-clock, no RNG.
"""
import collections
import re

RATING = 'Class 150'                                # the plant-wide schedule class
H = {'inlet': 160, 'outlet': 600, 'bottom': 50, 'top': 800}   # placeholder elevations, mm
HEADER = ['tag', 'size', 'rating', 'service', 'face', 'height_mm']
_VESSEL_ZERO = {'kettle', 'precip', 'separator', 'store'}     # utilities-only files where nothing is piped
_POWER_TERMINAL_UNIT = {                            # stream_id -> unit whose schedule carries the terminal
    'IA-ZNBR-LOSS': 'ZNBR2',                        # the electric round-trip loss leaves at the skid terminal
}                                                   # (the edge's other end is the export accounting node)
_HVAC_TERMINAL = {                                  # stream_id -> unit whose schedule carries the terminal
    'IA-ADS-CHW': 'HABITATION',                     # chilled water into the habitation loop
    'IA-MAU-AIR': 'HABITATION',                     # tempered make-up air into the habitation loop
    'SQ-H2O_ELYZ-Q4': 'H2O_ELYZ',                   # PEM stack heat, leaving at the skid
}
_IS_POWER_ROW = re.compile(r'rectifier|bus bar|480 V|power|terminal|conductor', re.I)


def noz_edges(g, u):
    """Connections a nozzle schedule must list: process mass kg/d edges plus
    HL-/thermal kW edges (cables are not nozzles); present edges only (the
    v1 _noz_edges over the _EU census)."""
    out = []
    for e in g['edges']:
        if e.get('presence') != 'present':
            continue
        if u not in (e['to_unit_id'], e['from_unit_id']):
            continue
        lay = e.get('layers') or []
        un = (e.get('rate') or {}).get('unit')
        if 'mass' in lay and un == 'kg/d':
            out.append(e)
        elif un == 'kW' and (e['stream_id'].startswith('HL-') or 'thermal' in lay) \
                and e.get('phase') not in ('E', 'electric') and 'elec' not in lay:
            out.append(e)
    return out


def _tag_max(body):
    """The highest issued tag number of a schedule body (N-prefixed rows)."""
    return max([int(r[0][1:]) for r in body if r and r[0].startswith('N') and r[0][1:].isdigit()] + [0])


def coverage_rows(unit_class, u, dn_map_, body, conns):
    """The rows pass 1 appends for coverage: one per (service, edge) the
    schedule lacks, in first-seen service order, edges stream_id-sorted
    within a service; a new file adds the standard drain and vent."""
    have = collections.Counter(r[3] for r in body if len(r) > 3)
    add = []
    for svc in [c for c in dict.fromkeys(e.get('carries') or '' for e in conns)]:
        k = sum(1 for e in conns if (e.get('carries') or '') == svc) - have.get(svc, 0)
        grp = sorted((e for e in conns if (e.get('carries') or '') == svc), key=lambda e: e['stream_id'])
        for e in grp[:k]:
            dn = dn_map_.get(e['stream_id'], ('MISSING', ''))[0]
            face = 'inlet' if e['to_unit_id'] == u else 'outlet'
            add.append([dn, RATING, svc, face, str(H[face])])
    if body == [] and (conns or unit_class in _VESSEL_ZERO):
        add += [['DN15', RATING, 'drain', 'bottom', str(H['bottom'])],
                ['DN15', RATING, 'vent', 'top', str(H['top'])]]
    return add


def present_units(g):
    """The present units, unit_id-sorted (the v1 pass order)."""
    return sorted((n['unit_id'] for n in g['nodes'] if n.get('presence') == 'present'))


def unit_state(g, u):
    """The node record of a unit (present set only - the v1 _node map)."""
    for n in g['nodes']:
        if n['unit_id'] == u and n.get('presence') == 'present':
            return n
    return None


def schedule_rows(g, dn_map_, hand, units=None):
    """The post-merge schedule state: {unit: rows-or-None} over the requested
    units (default every present unit). `hand` is the pre-merge state
    ({unit: rows-or-None} with rows incl. header). Pass 1 appends coverage
    rows; the terminal pass appends the power and HVAC service rows; a
    schedule with nothing to add keeps its pre-merge rows (the v1 no-write
    branch). The renderer lane resolves one unit at a time through `units`.
    Pure."""
    out = dict(hand)
    for u in (sorted(units) if units is not None else present_units(g)):
        n = unit_state(g, u)
        if n is None:
            continue                                   # a schedule of a unit not present: the v1 never touches it
        conns = noz_edges(g, u)
        rows = hand.get(u)
        if rows is not None:
            body = [r for r in rows[1:] if r and r[0].strip()]
        else:
            if not conns and n.get('class') not in _VESSEL_ZERO:
                continue                               # machine with nothing piped: no file
            body = []
        add = coverage_rows(n.get('class'), u, dn_map_, body, conns)
        if not add and rows is not None:
            continue                                   # nothing to append: no write
        tag = _tag_max(body)
        merged = (list(rows) if rows is not None else [list(HEADER)])[:]
        for a in add:
            tag += 1
            merged.append([f'N{tag}'] + a)
        out[u] = merged
    # ---- terminal service rows (the v1 second pass, over the pass-1 state) --
    power = [e for e in g['edges'] if e.get('presence') == 'present'
             and 'elec' in (e.get('layers') or [])
             and (e.get('rate') or {}).get('unit') == 'kW'
             and (e['stream_id'].startswith(('SF-', 'IA-DC', 'IA-TRIM'))
                  or e['stream_id'] in _POWER_TERMINAL_UNIT)]
    _pre_covered = set()
    for e in power:
        u = e['to_unit_id']
        if u in _pre_covered:
            continue
        rows = out.get(u)
        if rows is None:
            continue
        body = [r for r in rows[1:] if r and r[0].strip()]
        if any(_IS_POWER_ROW.search(r[3]) for r in body if len(r) > 3):
            _pre_covered.add(u)
    for e in sorted(power, key=lambda e: e['stream_id']):
        sid = e['stream_id']
        u = _POWER_TERMINAL_UNIT.get(sid, e['to_unit_id'])
        n = unit_state(g, u)
        if not n or n.get('presence') != 'present' or u in _pre_covered:
            continue
        if (n.get('params') or {}).get('envelope', {}).get('state') == 'standby_rated':
            continue                                   # hold: unrated standby feed
        rows = out.get(u)
        if rows is None:
            continue                                   # hold: the no-file rule stands
        body = [r for r in rows[1:] if r and r[0].strip()]
        if any(sid in r[3] for r in body if len(r) > 3):
            continue                                   # this circuit is already scheduled
        tag = _tag_max(body)
        size = dn_map_.get(sid, ('cable', ''))[0]      # line-list classification, verbatim
        svc = f'power terminal ({sid}, {e.get("carries") or ""})'
        if e['from_unit_id'] == u:                     # an outgoing circuit: outlet at the skid
            face, h = 'outlet', H['outlet']
        else:
            face, h = 'top', H['top']
        out[u] = rows + [[f'N{tag + 1}', size, RATING, svc, face, str(h)]]
    for sid, u in _HVAC_TERMINAL.items():
        e = next((x for x in g['edges'] if x['stream_id'] == sid and x.get('presence') == 'present'), None)
        if not e:
            continue
        rows = out.get(u)
        if rows is None:
            continue
        body = [r for r in rows[1:] if r and r[0].strip()]
        if any(sid in r[3] for r in body if len(r) > 3):
            continue                                   # already scheduled
        face = 'inlet' if e['to_unit_id'] == u else 'outlet'
        tag = _tag_max(body)
        size = dn_map_.get(sid, ('cable', ''))[0]
        svc = f'service terminal ({sid}, {e.get("carries") or ""})'
        out[u] = rows + [[f'N{tag + 1}', size, RATING, svc, face, str(H[face])]]
    return out
