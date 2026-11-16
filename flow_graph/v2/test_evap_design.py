"""engine v2: the evaporator-design family acceptance (the golden-value proof).

Reference writer: flow_graph/param/evap_design.py --write (ledger row
`sizing_evap_design`, section B, MIXED: sizing -> function, doc -> renderer).
The committed graph carries every field the stage writes; the proofs:

- exact change set: the function's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved (the
  EVAP continuous_kw / SF feed books of the process family, the duties, the
  materials rows and every untouched node stay byte-faithful);
- golden equality: the committed params.design blocks (the same books the
  process family seed-reads) equal the fresh computation, numbers quantised to
  the golden's decimals - zero enumerated drift;
- the relief-family residue, each delta asserted exactly, with its owner: the
  write_graph relief family re-solves the body area, bore and computed_by in
  place after this stage every pass (AQS-PAR-001 relief pass), leaving
  bore_req_mm appended; the case inputs it reads are this stage's books and
  land fresh;
- the mass books are prior-family fields: the process family's evap masses
  (solver.evap port) read through its pure kernel on the seed rates;
- determinism: two runs, byte-identical; the no-drivers bridge contract;
- grid purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os

import pytest

from flow_graph.v2.functions import evap_design as ED
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every field the function writes.
EXPECTED_NODE_FIELDS = [
    ('EVAP_ACID', 'params.design'), ('EVAP_ACID', 'params.size_mm'), ('EVAP_ACID', 'params.size_note'),
    ('EVAP_ACID', 'params.relief_mm'), ('EVAP_ACID', 'params.relief_basis'),
    ('EVAP_ACID', 'params.design_kPa'),
    ('EVAP_BASE', 'params.design'), ('EVAP_BASE', 'params.size_mm'), ('EVAP_BASE', 'params.size_note'),
    ('EVAP_BASE', 'params.relief_mm'), ('EVAP_BASE', 'params.relief_basis'),
    ('EVAP_BASE', 'params.design_kPa'),
]
EXPECTED_EDGE_FIELDS = [
    ('IA-EVAP_ACID-COND', 'params.T_C'), ('IA-EVAP_ACID-COND', 'params.T_basis'),
    ('IA-EVAP_ACID-COND', 'params.HCl_wt'), ('IA-EVAP_ACID-COND', 'params.HCl_kg_d'),
    ('IA-EVAP_ACID-COND', 'params.composition_basis'),
    ('IA-ACID-01', 'params.T_C'), ('IA-ACID-01', 'params.T_basis'),
    ('IA-EVAP_BASE-COND', 'params.T_C'), ('IA-EVAP_BASE-COND', 'params.T_basis'),
    ('IA-BASE-PPT', 'params.T_C'), ('IA-BASE-PPT', 'params.T_basis'),
    ('IA-BASE-01', 'params.T_C'), ('IA-BASE-01', 'params.T_basis'),
]

# The relief-family residue (owner: the write_graph relief family, AQS-PAR-001
# relief pass; X-SAF-05 fire case is receiver-only): it re-solves the body
# area from the ROUNDED flow book this stage stamps, rewrites computed_by and
# adequate, and appends bore_req_mm. Each (committed, mine) pair asserted.
RELIEF_RESIDUE = {
    ('EVAP_ACID', 'params.relief_basis.computed_by'):
        ('flow_graph/param/sizing/relief.py gas_area_in2 (API520)',
         'flow_graph/param/evap_design.py (ISO23251; API520)'),
    ('EVAP_ACID', 'params.relief_basis.A_req_mm2'): (34.01, 34.0),
    ('EVAP_BASE', 'params.relief_basis.computed_by'):
        ('flow_graph/param/sizing/relief.py gas_area_in2 (API520)',
         'flow_graph/param/evap_design.py (ISO23251; API520)'),
    # bore_req_mm: present on the committed tree (appended by the relief
    # family), not in this stage's dict
    ('EVAP_ACID', 'params.relief_basis.bore_req_mm'): (6.58, None),
    ('EVAP_BASE', 'params.relief_basis.bore_req_mm'): (6.58, None),
}


def run():
    b = load(REF_GRAPH)
    ED.evap_design(b, INPUTS)
    return b


def _committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    from decimal import Decimal
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(got, bool) and _num_eq(gold, got)
    return gold == got


def _dig(obj, path):
    cur = obj
    for part in path.split('.'):
        if part not in cur:
            return None
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected, deltas):
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields, the residue deltas and the residue keys this stage's
    dict does not carry. Provenance rows are excluded."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if p in deltas:
            if (c_obj.get(k) if isinstance(c_obj, dict) else None) != deltas[p][0] \
                    or (r_obj.get(k) if isinstance(r_obj, dict) else None) != deltas[p][1]:
                out.add(p + ' (residue pair moved)')
            continue
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in expected:
            if isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict) \
                    and any(dp.startswith(p + '.') for dp in deltas):
                _strict_diffs(c_obj[k], r_obj[k], p, out, expected, deltas)
            elif not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected, deltas)
        elif isinstance(c_obj[k], list) and isinstance(r_obj[k], list) and len(c_obj[k]) == len(r_obj[k]):
            if any(type(a) is not type(b) or a != b for a, b in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def test_exact_change_set_and_golden_equality():
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_NODE_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_NODE_FIELDS)),
        sorted(set(EXPECTED_NODE_FIELDS) - set(got_nodes)))
    assert got_edges == sorted(EXPECTED_EDGE_FIELDS), (
        sorted(set(got_edges) - set(EXPECTED_EDGE_FIELDS)),
        sorted(set(EXPECTED_EDGE_FIELDS) - set(got_edges)))

    # every changed field equals the committed golden...
    residue = {f'{uid}.{path}' for uid, path in RELIEF_RESIDUE}
    for uid, path in EXPECTED_NODE_FIELDS:
        if path == 'params.relief_basis':
            gold, mine = _dig(c_nodes[uid], path), _dig(r_nodes[uid], path)
            for k in gold:
                if f'{uid}.params.relief_basis.{k}' in residue:
                    continue                                   # the relief family's keys: asserted below
                assert _eq(gold[k], mine[k]), (uid, 'relief_basis.' + k)
            continue
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGE_FIELDS:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # ...and nothing else moves: a strict walk of every node and edge, with the
    # relief residue asserted as exact (committed, mine) pairs
    deltas = {uid + '.' + path: pair for (uid, path), pair in RELIEF_RESIDUE.items()}
    expected_paths = {uid + '.' + path for uid, path in EXPECTED_NODE_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths, deltas)
    assert diffs == set(), sorted(diffs)
    edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGE_FIELDS}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, edge_paths, {})
    assert edge_diffs == set(), sorted(edge_diffs)


def test_changed_values_spot_checks():
    """The committed MVR design books, hand-enumerated (X-MFG-30 Rev C)."""
    b = run()
    out = json.loads(render(b))
    n = {x['unit_id']: x for x in out['nodes']}
    a = n['EVAP_ACID']['params']['design']
    bb = n['EVAP_BASE']['params']['design']
    assert a['unit'] == 'EVAP_ACID' and bb['unit'] == 'EVAP_BASE'
    assert a['T_boil_C'] == 108.6 and bb['T_boil_C'] == 108.0
    assert a['T_cond_C'] == 114.6 and bb['T_cond_C'] == 114.0
    assert a['p_body_kPa'] == 101.325 and bb['p_body_kPa'] == 101.325
    assert a['p_shell_kPa'] == 166.98 and bb['p_shell_kPa'] == 163.73
    assert a['ratio'] == 1.648 and bb['ratio'] == 1.616
    assert a['water_kg_h'] == 36.049 and bb['water_kg_h'] == 33.8
    assert a['duty_kW'] == 22.6 and bb['duty_kW'] == 21.19
    assert a['comp_shaft_kW'] == 1.34 and bb['comp_shaft_kW'] == 1.202
    assert a['comp_elec_kW'] == 1.489 and bb['comp_elec_kW'] == 1.336
    assert a['w_kJ_kg'] == 93.7 and bb['w_kJ_kg'] == 89.6
    assert a['kWh_per_t'] == 41.5 and bb['kWh_per_t'] == 39.8
    assert a['A_ff_m2'] == 2.51 and bb['A_ff_m2'] == 2.35
    assert a['tubes'] == 22 and bb['tubes'] == 20
    assert a['tube_id_mm'] == 25.0 and a['tube_L_mm'] == 1500.0
    assert a['recirc_kg_h'] == 311.0 and bb['recirc_kg_h'] == 282.7
    assert a['pump_kW'] == 0.008 and bb['pump_kW'] == 0.008
    assert a['shell_D_mm'] == 350 and bb['shell_D_mm'] == 350
    assert a['height_mm'] == 3800 and bb['height_mm'] == 3100
    assert a['ix_Q_kW'] == 3.7 and bb['ix_Q_kW'] == 3.67
    assert a['ix_A_m2'] == 0.155 and bb['ix_A_m2'] == 0.143
    assert a['T_feed_preheat_C'] == 98.6 and bb['T_feed_preheat_C'] == 98.0
    assert a['T_out_C'] == 49.1 and bb['T_out_C'] == 51.1
    assert a['trim_kW'] == 0.0 and bb['trim_kW'] == 0.0
    assert a['total_kW'] == 1.498 and bb['total_kW'] == 1.344
    assert bb['column'] is None
    col = a['column']
    assert col['ideal_stages_incl_body'] == 5 and col['column_stages'] == 4
    assert col['cond_hcl_wt_pct'] == 0.5 and col['y_eq_feed_pct'] == 0.343
    assert col['y_eq_body_pct'] == 17.09 and col['packed_mm'] == 3000
    assert col['D_req_mm'] == 148.9 and col['DN'] == 150
    assert col['recycle_hcl_kg_d'] == 4.33 and col['height_mm'] == 3800
    assert col['material'].startswith('borosilicate glass 3.3 sections (ISO 3585)')
    assert col['placement'].startswith('free-standing beside the body on the same frame')
    for uid, size in (('EVAP_ACID', [1650, 1300, 3800]), ('EVAP_BASE', [1250, 800, 3100])):
        assert n[uid]['params']['size_mm'] == size
        assert all(isinstance(x, int) for x in n[uid]['params']['size_mm'])
        assert n[uid]['params']['size_note'] == \
            'L x W x H mm: body plus interchanger and compressor frame, in-house design X-MFG-30 (AQS-DUTY-060)'
        assert n[uid]['params']['relief_mm'] == 9.51
        assert n[uid]['params']['design_kPa'] == 100.0


def test_relief_case_inputs_are_this_stages_books():
    """The case inputs the relief family reads (P1, T, M, k, W) land fresh and
    equal the committed residue's inputs; only its re-solved keys differ."""
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    b = run()
    for uid in ('EVAP_ACID', 'EVAP_BASE'):
        rb_, _ = b.computed[('node', uid, 'params.relief_basis')]
        gold = c_nodes[uid]['params']['relief_basis']
        for k in ('case', 'A_wetted_m2', 'Q_kW', 'W_kg_h', 'P1_kPa_abs', 'T_K', 'M_kg_kmol', 'k', 'orifice',
                  'adequate', 'shell_side'):
            assert _eq(gold[k], rb_[k]), (uid, k)
        assert rb_['P1_kPa_abs'] == 222.3 and rb_['shell_side']['P1_kPa_abs'] == 486.3


def test_relief_residue_owner_pairs():
    """The relief family's committed residue, each delta exact, with the owner."""
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    b = run()
    for (uid, path), (gold, mine) in RELIEF_RESIDUE.items():
        key = path.split('.', 2)[2]
        got = b.computed[('node', uid, 'params.relief_basis')][0].get(key)
        assert got == mine, (uid, path)
        assert _dig(c_nodes[uid], path) == gold, (uid, path, 'committed residue moved')


def test_edge_temperature_stamps():
    """The outlet lines carry the interchanger outlet T and its basis; the acid
    condensate carries the column composition books."""
    b = run()
    assert b.computed[('edge', 'IA-EVAP_ACID-COND', 'params.T_C')][0] == 49.1
    assert b.computed[('edge', 'IA-ACID-01', 'params.T_C')][0] == 49.1
    assert b.computed[('edge', 'IA-EVAP_BASE-COND', 'params.T_C')][0] == 51.1
    assert b.computed[('edge', 'IA-BASE-PPT', 'params.T_C')][0] == 51.1
    assert b.computed[('edge', 'IA-BASE-01', 'params.T_C')][0] == 51.1
    for sid in ('IA-EVAP_ACID-COND', 'IA-ACID-01', 'IA-EVAP_BASE-COND', 'IA-BASE-PPT', 'IA-BASE-01'):
        assert b.computed[('edge', sid, 'params.T_basis')][0] == \
            'X-MFG-30 interchanger outlet (AQS-DUTY-060)'
    assert b.computed[('edge', 'IA-EVAP_ACID-COND', 'params.HCl_wt')][0] == 0.005
    assert b.computed[('edge', 'IA-EVAP_ACID-COND', 'params.HCl_kg_d')][0] == 4.33
    assert b.computed[('edge', 'IA-EVAP_ACID-COND', 'params.composition_basis')][0] == \
        'column top vapour, PERRY7_HCL_VLE (AQS-DUTY-060 section 7)'


def test_mass_books_are_the_process_familys():
    """The water/product/feed books are prior-family fields, read through the
    process family's pure kernel (solver.evap port) on the seed rates."""
    b = load(REF_GRAPH)
    masses = ED._masses(b, INPUTS)
    assert masses is not None
    ea, eb = masses
    from decimal import Decimal
    for book_ in (ea, eb):
        assert all(isinstance(v, Decimal) for v in book_.values())
    assert float(ea['water']) == pytest.approx(36.049 * 24, abs=1e-2)     # kg/d = water_kg_h x 24
    assert float(eb['water']) == pytest.approx(33.8 * 24, abs=1e-2)


def test_no_declared_inputs_records_nothing():
    b = load(REF_GRAPH)
    ED.evap_design(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'evap_design' and prov.basis
    assert b.computed[('node', 'EVAP_ACID', 'params.design')][1].ref == 'A-M-106'
    assert b.computed[('node', 'EVAP_ACID', 'params.relief_basis')][1].ref == 'A-M-107'
    assert b.computed[('edge', 'IA-EVAP_ACID-COND', 'params.HCl_wt')][1].ref == 'A-M-108'


def test_function_module_grid_purity():
    tree = ast.parse(inspect.getsource(ED))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
