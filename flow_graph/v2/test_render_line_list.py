"""engine v2: the line-list pipeline chain acceptance (part 1 - the namespace,
the routes, the nozzle merge).

The chain wave: flow_graph/v2/functions/line_list.py (the AQS-PIP-004
namespace: rows, classes, DN sizing - the module the placement_routes,
nozzle_sched and pid_sheets stages execute), flow_graph/v2/functions/routes.py
(the A-M-074 rack routing kernel) and flow_graph/v2/functions/nozzles.py (the
append-only coverage merge over the hand+generated schedules). The golden is
the committed document file; the acceptance is byte-exact reproduction. The
proofs:

- byte-exact: docs-authority/LINE_LIST.md, ISO_ROUTES.md, ISO_ROUTES.json,
  docs-authority/iso/ISO_SHEETS.csv, ISO_SHEETS.md and every committed nozzle CSV renders
  from the model seeded from the committed graph and equals the committed
  file bytes exactly (the P&ID sheets and the drawing register verify in
  test_render_pid_drawings.py);
- bridge contract: the rows namespace here equals the reference writer's own
  namespace (runpy of docs-authority/_line_list.py - its document write sits
  under its __main__ guard) on the committed tree, rows and centres;
- nozzle fixpoint golden: every committed schedule re-merges to itself
  (the committed tree is the merge's own output; hand rows preserved
  verbatim, zero appends at the fixpoint);
- enumerated change sets: dropping a coverage row re-appends exactly that row
  at the next tag; an absent schedule for a machine unit with process
  connections creates the full coverage file (every connection + the drain
  and the vent); a vessel with no piped process connection gets the
  utilities-only file; a unit at standby_rated takes no power-terminal row;
- registry: the chain DOCS list is a declared contiguous block of RENDERS in
  the chain order (line list -> routes -> nozzles -> pid -> drawings), every
  output path exists, and render_one resolves each;
- payloads: the rows whose v1 stages read non-graph files (the line
  positions, the placement datums, the graph sha, the nozzle schedules) take
  them as input payloads read at this test's I/O boundary; a caller that
  omits a payload gets loud stub bytes, never a wrong document;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O, no banned imports and no float literals in the three
  function modules and the render module.
"""
import ast
import collections
import csv
import hashlib
import io
import json
import os
import runpy
import sys

import pytest

from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import line_list as LL
from flow_graph.v2.functions import nozzles as NZ
from flow_graph.v2.functions import routes as RT
from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render_one
from flow_graph.v2.render import line_list as _RL

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
SEED = os.path.join(ROOT, 'flow_graph', 'placement_seed.json')


def _csv_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.reader(f))


def line_positions():
    """The unit-centre namespace C: docs-authority/_line_list.py's module-level
    C dict, rebuilt from the committed files it reads. Duty origins,
    placement report moves, study rows, seed units, the GA relocates, the CAD
    moves, the riding exchanger, then the block centres (the v1 build order;
    the inventory wave declares the same payload key)."""
    seed = json.load(open(SEED))
    C = {}
    for u, o in json.load(open(os.path.join(ROOT, 'docs-authority/duties/_origins.json')))['origins'].items():
        C[u] = ([o['origin_mm'][i] + o['size_mm'][i] / 2 for i in range(3)], 'duty origin')
    pr = json.load(open(os.path.join(ROOT, 'flow_graph/placement_report.json')))
    for r in pr.get('moves', []) + pr.get('create_moves', []):
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(o) == 3 and len(z) >= 2:
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_report'))
    for r in json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))['units']:
        o, z = r['origin_mm'], r['size_mm']
        C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_study (STUDY)'))
    LV = {'L-1': -6000, 'L0': 0, 'L1': 6000}
    for r in seed['units']:
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(z) >= 2:
            o = list(o) + [LV.get(r.get('level'), 0)] * (3 - len(o))
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_seed'))
    sys.path.insert(0, os.path.join(ROOT, 'models/freecad'))
    try:
        import params as _FP
        for _u, (_cx, _cy) in getattr(_FP, 'RELOCATE', {}).items():
            if _u in C:
                C[_u] = ([_cx, _cy, C[_u][0][2]], C[_u][1] + ' + GA relocate')
    except Exception:
        pass
    if os.path.exists(os.path.join(ROOT, 'docs-authority/inventory/CAD_MOVES.json')):
        for _m in json.load(open(os.path.join(ROOT, 'docs-authority/inventory/CAD_MOVES.json'))):
            if _m['unit'] in C:
                _c = C[_m['unit']][0]
                C[_m['unit']] = ([_c[0] + _m['dx_mm'], _c[1] + _m['dy_mm'], _c[2]],
                                 C[_m['unit']][1] + ' + GA move')
    if 'EVAP_ACID_VS' not in C and 'EVAP_ACID' in C:
        c = C['EVAP_ACID'][0]
        C['EVAP_ACID_VS'] = ([c[0], c[1] + 650, c[2]], 'on EVAP_ACID frame')
    for b in seed['blocks']:
        o = b['origin_mm']
        z = b['size_mm']
        c = [o[0] + z[0] / 2, o[1] + z[1] / 2, LV.get(b['level'], 0) + 500]
        for u in b.get('unit_ids', []):
            C.setdefault(u, (c, 'placement block ' + b['block_id']))
    return C


def nozzle_schedules():
    """The committed schedule files as the declared payload: {unit: bytes}
    (the nozzles family proves the committed tree is the merge's fixpoint, so
    these bytes are the product)."""
    out = {}
    d = os.path.join(ROOT, 'docs-authority/nozzles')
    for name in sorted(os.listdir(d)):
        if name.endswith('.csv'):
            with open(os.path.join(d, name), 'rb') as f:
                out[name[:-4]] = f.read()
    return out


def chain_payload(extra=()):
    """The chain payload: the canonical drivers + site profile, the line
    positions, the placement seed, the graph file sha and the merged nozzle
    schedules; extra keys extend it (the pid/drawings payloads of part 2)."""
    payload = {
        'drivers': json.load(open(DRIVERS)),
        'site_profile': json.load(open(PROFILE)),
        'line_positions': line_positions(),
        'placement_seed': json.load(open(SEED)),
        'graph_sha256': hashlib.sha256(open(REF_GRAPH, 'rb').read()).hexdigest(),
        'nozzle_schedules': nozzle_schedules(),
    }
    for k, v in extra:
        payload[k] = v
    return payload


INPUTS = chain_payload()

NOZZLE_UNITS = sorted(u for u in INPUTS['nozzle_schedules'])
CHAIN_DOCS = ['docs-authority/LINE_LIST.md',
              'docs-authority/ISO_ROUTES.md',
              'docs-authority/ISO_ROUTES.json',
              'docs-authority/iso/ISO_SHEETS.csv',
              'docs-authority/ISO_SHEETS.md']
BYTE_DOCS = CHAIN_DOCS + [f'docs-authority/nozzles/{u}.csv' for u in NOZZLE_UNITS]

_MODEL = None


def model():
    """The committed seed, computed by the full declared composition, frozen.
    Cached: the model is a pure frozen value of these pure inputs."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SL.solve(INPUTS, REF_GRAPH)
    return _MODEL


def committed(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return f.read()


def _first_diff(want, got):
    i = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))
    lo = max(0, i - 80)
    return (f'first difference at byte {i} (committed {len(want)} B, rendered {len(got)} B)\n'
            f'committed: {want[lo:i + 120]!r}\nrendered:  {got[lo:i + 120]!r}')


# ---- bridge contract: the namespace equals the reference writer's -------------

def test_rows_namespace_equals_the_reference_writer():
    """The ported rows and centres equal the reference writer's own module
    namespace (runpy: the doc write sits under its __main__ guard) - row for
    row, cell for cell. The v1 stage reads relative paths, so the runpy runs
    at the repo root (restored after)."""
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        ns = runpy.run_path(os.path.join(ROOT, 'docs-authority/_line_list.py'))
    finally:
        os.chdir(cwd)
    g = json.load(open(REF_GRAPH, encoding='utf-8'))
    mine = LL.rows(g, INPUTS['line_positions'], INPUTS['drivers'])
    assert mine == ns['rows']
    assert INPUTS['line_positions'] == ns['C']


def test_dn_map_and_class_rules():
    """The dn map agrees with the committed LINE_LIST.md cells for a spot set
    of families, and the DN ladder is honoured."""
    rows = LL.rows(json.load(open(REF_GRAPH, encoding='utf-8')),
                   INPUTS['line_positions'], INPUTS['drivers'])
    dn = LL.dn_map(rows)
    committed_dn = {}
    for line in committed('docs-authority/LINE_LIST.md').decode('utf-8').splitlines():
        if line.startswith('| ') and '|' in line[2:]:
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 9 and c[0] not in ('Line',) and not c[0].startswith('-') \
                    and not c[0].startswith('Units with'):
                committed_dn[c[0]] = (c[3], c[4])
    for sid in ('HL-Q4-REJ', 'IA-H2SO4-MU', 'S36', 'C29_RECYCLE', 'IA-DC-REJ', 'S25'):
        assert dn[sid] == committed_dn[sid], (sid, dn[sid], committed_dn[sid])
    hdr_row = next(r for r in rows if 'HDR_H2' in (r[1], r[2]))
    assert hdr_row[4] == committed_dn[hdr_row[0]][1] == 'P1'   # the wet acid header (X-MAT-06)
    sizes = {r[3] for r in rows if r[3].startswith('DN')}
    ladder = {f'DN{d}' for d in LL.DN}
    assert sizes <= ladder | {'cable', 'solids'}


# ---- golden: the chain documents, byte-exact -----------------------------------

def test_registry_declares_the_chain_block():
    """The chain DOCS list is a declared contiguous block of the registry, in
    the chain order, with the views wave still the declared tail; every path
    exists."""
    paths = [p for p, _ in RENDERS]
    expected = [p for p, _ in _RL.DOCS]
    first = paths.index(expected[0])
    assert paths[first:first + len(expected)] == expected
    assert paths[first + len(expected):first + len(expected) + 1] == \
        ['flow_graph/derived/STREAM_REGISTER_DERIVED.md']   # the views tail follows the chain block
    assert expected[0] == 'docs-authority/LINE_LIST.md' and expected[4] == 'docs-authority/ISO_SHEETS.md'
    assert expected[5].startswith('docs-authority/nozzles/')
    assert expected[-1] == 'docs-authority/DRAWING_REGISTER.md'
    assert all(callable(fn) for _, fn in _RL.DOCS)
    for path, _ in _RL.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path


@pytest.mark.parametrize('path', BYTE_DOCS, ids=[os.path.basename(p) for p in BYTE_DOCS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


# ---- golden: the nozzle merge fixpoint and the enumerated change sets ----------

def test_nozzle_merge_fixpoint_over_every_committed_schedule():
    """Every committed schedule re-merges to itself: the hand rows preserved
    verbatim, zero appends, and every committed file renders to its own
    bytes (the mixed face - hand-era LF, generator-written CRLF - is the
    v1 no-write branch's)."""
    g = json.load(open(REF_GRAPH, encoding='utf-8'))
    dn = LL.dn_map(LL.rows(g, INPUTS['line_positions'], INPUTS['drivers']))
    hand = {u: list(csv.reader(io.StringIO(raw.decode('utf-8'))))
            for u, raw in INPUTS['nozzle_schedules'].items()}
    merged = NZ.schedule_rows(g, dn, hand)
    for u, rows in hand.items():
        assert merged.get(u) == rows, u                    # the fixpoint: nothing re-appends
    absent = [u for u in NZ.present_units(g) if u not in hand]
    for u in absent:
        n = next(x for x in g['nodes'] if x['unit_id'] == u)
        conns = NZ.noz_edges(g, u)
        assert merged.get(u) is None, u                    # no file stays no file
        assert not conns and n.get('class') not in NZ._VESSEL_ZERO, u


def test_nozzle_change_set_dropped_coverage_row_reappends():
    """Enumerated change set: dropping one generated coverage row re-appends
    exactly that row, at the next tag, same cells."""
    g = json.load(open(REF_GRAPH, encoding='utf-8'))
    dn = LL.dn_map(LL.rows(g, INPUTS['line_positions'], INPUTS['drivers']))
    hand = {u: [list(r) for r in csv.reader(io.StringIO(raw.decode('utf-8')))]
            for u, raw in INPUTS['nozzle_schedules'].items()}
    target = 'ACID_PLANT'
    rows = hand[target]
    body = [r for r in rows[1:] if r and r[0].strip()]
    drop = next(r for r in body if r[3] in {e.get('carries') or '' for e in NZ.noz_edges(g, target)})
    tag = drop[0]
    hand[target] = [r for r in rows if r is not drop]
    merged = NZ.schedule_rows(g, dn, hand)
    out = merged[target]
    assert len(out) == len(rows)                           # one row back
    reappended = out[-1]
    assert reappended[0] == f'N{max(int(r[0][1:]) for r in body if r[0][1:].isdigit()) + 1}'
    assert reappended[1:] == drop[1:]                      # same cells, fresh tag
    assert tag not in {r[0] for r in out}                  # the old tag retired


def test_nozzle_change_set_absent_schedule_creates_coverage_file():
    """Enumerated change set: an absent schedule for a machine unit with
    process connections creates the full coverage file - one row per
    connection in first-seen service order, the drain and the vent, then the
    terminal service rows the unit's power circuits take."""
    g = json.load(open(REF_GRAPH, encoding='utf-8'))
    dn = LL.dn_map(LL.rows(g, INPUTS['line_positions'], INPUTS['drivers']))
    hand = {u: [list(r) for r in csv.reader(io.StringIO(raw.decode('utf-8')))]
            for u, raw in INPUTS['nozzle_schedules'].items()}
    target = 'ACID_PLANT'
    hand.pop(target)
    merged = NZ.schedule_rows(g, dn, hand)
    out = merged[target]
    conns = NZ.noz_edges(g, target)
    svc_order = list(dict.fromkeys(e.get('carries') or '' for e in conns))
    n_conn = len(conns)
    assert out[0] == NZ.HEADER
    body = out[1:]
    power = sorted((e for e in g['edges'] if e.get('presence') == 'present'
                    and 'elec' in (e.get('layers') or [])
                    and (e.get('rate') or {}).get('unit') == 'kW'
                    and e['to_unit_id'] == target
                    and e['stream_id'].startswith(('SF-', 'IA-DC', 'IA-TRIM'))),
                   key=lambda e: e['stream_id'])
    expected = svc_order + ['drain', 'vent'] + \
        [f'power terminal ({e["stream_id"]}, {e.get("carries") or ""})' for e in power]
    assert [r[3] for r in body] == expected
    assert len(body) == n_conn + 2 + len(power)
    for r in body[:n_conn]:
        e = next(e for e in conns if (e.get('carries') or '') == r[3])
        assert r[1] == dn[e['stream_id']][0] and r[2] == 'Class 150'
        assert r[4] == ('inlet' if e['to_unit_id'] == target else 'outlet')
    assert body[n_conn] == ['N11', 'DN15', 'Class 150', 'drain', 'bottom', '50']
    assert body[n_conn + 1] == ['N12', 'DN15', 'Class 150', 'vent', 'top', '800']
    for r in body[n_conn + 2:]:
        assert r[1] == 'cable'                             # the circuit classification, verbatim


def test_nozzle_change_set_standby_unit_takes_no_power_terminal_row():
    """The terminal-row holds: a standby_rated unit carries no power-terminal
    row; a unit whose schedule already carried a conductor or power row keeps
    it and takes no appended row."""
    g = json.load(open(REF_GRAPH, encoding='utf-8'))
    dn = LL.dn_map(LL.rows(g, INPUTS['line_positions'], INPUTS['drivers']))
    merged = NZ.schedule_rows(g, dn, {u: [list(r) for r in csv.reader(io.StringIO(raw.decode('utf-8')))]
                                      for u, raw in INPUTS['nozzle_schedules'].items()})
    standby = []
    for n in g['nodes']:
        if n.get('presence') != 'present':
            continue
        st = (n.get('params') or {}).get('envelope', {}).get('state')
        if st == 'standby_rated':
            standby.append(n['unit_id'])
    for u in standby:
        rows = merged.get(u)
        if rows is None:
            continue
        assert not any('power terminal' in r[3] for r in rows[1:]), u
    for r in merged['EW_1'][1:]:                           # the issued conductor-row precedent
        if 'rectifier' in r[3]:
            assert any(r == x for x in merged['EW_1'][1:])


# ---- payload discipline ---------------------------------------------------------

def test_missing_payload_renders_a_loud_stub_not_a_wrong_document():
    """A caller that carries only the canonical drivers gets loud stub bytes
    for the payload rows, and the drivers-only rows stay absent too (the line
    list reads the positions as well)."""
    m = model()
    partial = {'drivers': INPUTS['drivers'], 'site_profile': INPUTS['site_profile']}
    for path in CHAIN_DOCS:
        got = render_one(path, m, partial)
        assert got.startswith(b'# docs-authority/'), path
        assert b'not provided by this caller' in got, path


def test_missing_nozzle_payload_renders_a_stub_per_unit():
    """A nozzle row without its schedule payload is a loud stub, never an
    empty file."""
    m = model()
    got = render_one(f'docs-authority/nozzles/{NOZZLE_UNITS[0]}.csv', m,
                     {'drivers': INPUTS['drivers'], 'site_profile': INPUTS['site_profile']})
    assert got.startswith(b'# docs-authority/nozzles/')
    assert b'not provided by this caller' in got


# ---- routing kernel spot checks --------------------------------------------------

def test_routing_kernel_rack_rule():
    """The A-M-074 rack rule on a known route: rack at the source-level datum
    + 3200, at least 300 above the higher end; the legs and the committed
    ISO_ROUTES.json row agree."""
    D = INPUTS['placement_seed']['datums_mm']
    rows = LL.rows(json.load(open(REF_GRAPH, encoding='utf-8')),
                   INPUTS['line_positions'], INPUTS['drivers'])
    C = INPUTS['line_positions']
    r = next(x for x in rows if x[0] == 'C29_RECYCLE')
    ca, cb = C[r[1]], C[r[2]]
    rec, legs = RT.route_line(r, ca, cb, D)
    jrow = {'line': rec['line'], 'dn': rec['DN'], 'class': rec['cls'], 'from': r[1], 'to': r[2]}
    committed_row = next(x for x in json.load(
        open(os.path.join(ROOT, 'docs-authority/ISO_ROUTES.json'),
             encoding='utf-8'))['rows'] if x['line'] == 'C29_RECYCLE')
    zr = RT.rack_z(D, ca[0][2], cb[0][2])
    assert zr == max(D[RT.lvl(D, ca[0][2])] + RT.RACK, max(ca[0][2], cb[0][2]) + RT.MINRISE)
    assert legs == [zr - ca[0][2], cb[0][0] - ca[0][0], cb[0][1] - ca[0][1], cb[0][2] - zr]
    for k in ('line', 'dn', 'class', 'from', 'to', 'legs_mm', 'length_m', 'elbows'):
        assert jrow.get(k, committed_row[k]) == committed_row[k], k


# ---- determinism and purity -------------------------------------------------------

def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes: byte-identical over the
    chain documents."""
    m1 = SL.solve(INPUTS, REF_GRAPH)
    m2 = SL.solve(INPUTS, REF_GRAPH)
    for path in CHAIN_DOCS + [f'docs-authority/nozzles/{u}.csv' for u in NOZZLE_UNITS[:5]]:
        assert render_one(path, m1, INPUTS) == render_one(path, m2, INPUTS), path


def _module_pure(mod, name):
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(mod.__file__, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'{name}: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, \
                f'{name}: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'{name}:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'{name}:{node.lineno}: file I/O in an engine module')


def test_chain_modules_pure():
    """No I/O, no banned imports and no float literals in the three function
    modules and the render module (the engine lint's discipline)."""
    for mod in (LL, RT, NZ, _RL):
        _module_pure(mod, os.path.basename(mod.__file__))
