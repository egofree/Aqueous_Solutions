"""engine v2: the cold-box family acceptance (the golden-value proof).

Reference writer: flow_graph/param/cold_box.py --write (ledger row
`sizing_cold_box`, section B, MIXED: sizing -> function, doc -> renderer). The
committed graph carries every field the stage writes; the proofs:

- exact change set: the function's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved (the
  relief family's books, the duty books and every untouched node and edge stay
  byte-faithful);
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact equality, zero enumerated drift);
- the API618 stage search and the skid-extent grid as integer books (beds,
  stages, the whole-mm vessel books, the 1 dp skid extents);
- the seed-contract guards: EXPANDER and the expander loop edges left the graph
  (Q-010 / Rev AC), so the idle bookkeeping records nothing;
- the value-only SF feed update (the restoration note passes through);
- determinism: two runs, byte-identical; the no-drivers bridge contract;
- grid purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os

import pytest

from flow_graph.v2.functions import cold_box as CB
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every field the function writes.
EXPECTED_NODE_FIELDS = [
    ('CRYO_ASU', 'continuous_kw'), ('CRYO_ASU', 'internals'), ('CRYO_ASU', 'params.internals'),
    ('CRYO_ASU', 'params.design'), ('CRYO_ASU', 'params.size_mm'), ('CRYO_ASU', 'params.size_basis'),
]
EXPECTED_EDGE_FIELDS = [('SF-CRYO_ASU', 'rate')]


def run():
    b = load(REF_GRAPH)
    CB.cold_box_asu(b, INPUTS)
    return b


def _committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    """Equal quantised to the golden's decimals: exact numeric equality."""
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
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected):
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields. Provenance rows are excluded."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected)
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
    assert got_edges == sorted(EXPECTED_EDGE_FIELDS)

    for uid, path in EXPECTED_NODE_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGE_FIELDS:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # nothing else moves: a strict walk of every node and edge
    expected_paths = {uid + '.' + path for uid, path in EXPECTED_NODE_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGE_FIELDS}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, edge_paths)
    assert edge_diffs == set(), sorted(edge_diffs)


def test_changed_values_spot_checks():
    """The committed design books, hand-enumerated (X-MFG-33 Rev C)."""
    b = run()
    out = json.loads(render(b))
    n = {x['unit_id']: x for x in out['nodes']}
    d = n['CRYO_ASU']['params']['design']
    assert d['feed_N2_kg_d'] == 215.397605 and d['feed_CO2_kg_d'] == 22.782645
    assert d['x_CO2'] == 0.06307759824294379
    assert d['CO2_mol_per_cycle'] == 172.55657805044308
    assert d['sorbent_kg_per_bed'] == 115.03771870029539 and d['beds'] == 3
    assert d['bed_D_mm'] == 421.92823541437093 and d['bed_L_mm'] == 1265.7847062431126
    assert d['regen_kW'] == 1.4771801728773764 and d['blower_kW'] == 0.04803407798071272
    assert d['co2_comp_kW'] == 0.08561130897577333 and d['co2_chill_kW'] == 0.03467497473958333
    assert d['getter_kW'] == 0.1 and d['total_kW'] == 1.7455005345734458
    assert d['comp_stages'] == 4 and d['comp_ratio_per_stage'] == 2.114742526881128
    assert d['comp_T_out_C'] == 121.93064278721914
    ex = d['expander_backup']
    assert ex['cold_kW'] == 0.08668743684895833 and ex['T_out_C'] == -56.08836699924316
    assert ex['loop_kg_d'] == 231.65338735906764 and ex['shaft_kW'] == 0.23126703476505048
    assert ex['net_kW'] == 0.46641918337245225 and ex['COP'] == 0.18585735737145986
    assert ex['chiller_kW'] == 0.03467497473958333
    assert d['bed_pitch_mm'] == 521.9 and d['skid_l_mm'] == 2460.0
    assert d['machinery_row_x0_mm'] == 1700.0 and d['machinery_row_len_mm'] == 740.0
    assert d['skid_w_mm'] == 560.0 and d['hose_lap_mm'] == 32.0 and d['top_datum_mm'] == 2000.0
    assert d['H_mm'] == 1266 and d['D_mm'] == 422
    assert n['CRYO_ASU']['params']['size_mm'] == [2460.0, 592.0, 2000.0]
    assert n['CRYO_ASU']['params']['size_basis'].startswith('X-MFG-33 (A-M-175, AQS-DUTY-069) skid extents')
    assert n['CRYO_ASU']['params']['internals'] == n['CRYO_ASU']['internals']
    ck = n['CRYO_ASU']['continuous_kw']
    assert ck['value'] == 1.7455 and ck['unit'] == 'kW' and ck['status'] == 'study'
    assert ck['note'] == ('X-MFG-33 (A-M-175, AQS-DUTY-069): 13X TSA regeneration 1.48 + blower 0.048 + '
                          'CO2 compressor 0.086 + condenser chiller 0.035 + Ar getter 0.10 kW; no cryogenic '
                          'column (no air intake).')


def test_sf_feed_is_value_only():
    """The R11 Rev AC restoration note passes through; only the value moves."""
    committed = _committed()
    c_sf = next(e for e in committed['edges'] if e['stream_id'] == 'SF-CRYO_ASU')
    b = run()
    out = json.loads(render(b))
    r_sf = next(e for e in out['edges'] if e['stream_id'] == 'SF-CRYO_ASU')
    assert r_sf['rate']['value'] == 1.7455
    assert r_sf['rate']['note'] == c_sf['rate']['note']
    assert r_sf['rate']['unit'] == c_sf['rate']['unit'] and r_sf['rate']['status'] == c_sf['rate']['status']


def test_stage_search_and_grid_books():
    """The API618 stage search is integer combinatorics; the quantise points
    are integer books on the named grid."""
    b = run()
    d = b.computed[('node', 'CRYO_ASU', 'params.design')][0]
    assert isinstance(d['beds'], int) and d['beds'] == 3
    assert isinstance(d['comp_stages'], int) and d['comp_stages'] == 4
    assert isinstance(d['H_mm'], int) and isinstance(d['D_mm'], int)
    # the stage search reproduces: 4 stages of 2.1147 keep the discharge at
    # 121.9 C, 3 stages would breach the 150 C limit
    drv = INPUTS['drivers']
    v = lambda k: float(drv['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_ASU.' + k]['value'])
    k = float(drv['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_ASU.co2_k']['value'])
    x = (k - 1) / k
    ratio = 2.114742526881128
    t3 = v('feed_T_K') * (1 + ((20.0 ** (x / 3)) - 1) / v('comp_eta')) - 273.15
    assert t3 > 150.0                                   # three stages breach the limit
    assert d['comp_T_out_C'] <= 150.0                   # four stages hold it
    # the integer book helpers: exact-binary half-even, the v1 round() tie rule
    assert CB.book(2.675, 2, '') == 267                 # 2.675 binary is 2.6749..., rounds down
    assert CB.unbook(17455, 4) == 1.7455
    assert CB.unbook(CB.book(1.7455005345734458, 4, 'power kW'), 4) == 1.7455


def test_seed_contract_guards_record_nothing():
    """EXPANDER and the expander loop edges left the graph (Q-010 / Rev AC);
    the idle bookkeeping guards record nothing on this seed."""
    b = load(REF_GRAPH)
    assert 'EXPANDER' not in b.nodes
    assert 'IA-EXP-IN' not in b.edges and 'IA-EXP-OUT' not in b.edges
    assert 'SQ-CRYO_ASU' not in b.edges
    CB.cold_box_asu(b, INPUTS)
    assert all(uid != 'EXPANDER' for _k, uid, _p in b.computed)


def test_no_declared_inputs_records_nothing():
    """The bridge solve / check carry no driver payload: the stage records
    nothing and the seed stands."""
    b = load(REF_GRAPH)
    CB.cold_box_asu(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'cold_box' and prov.basis
    assert b.computed[('node', 'CRYO_ASU', 'params.design')][1].ref == 'A-M-175'
    assert b.computed[('node', 'CRYO_ASU', 'params.size_basis')][1].ref == 'A-M-175'
    assert b.computed[('edge', 'SF-CRYO_ASU', 'rate')][1].ref == 'A-M-175'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O."""
    tree = ast.parse(inspect.getsource(CB))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
