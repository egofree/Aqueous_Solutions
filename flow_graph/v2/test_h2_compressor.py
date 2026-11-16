"""engine v2: the H2-compressor family acceptance (the golden-value proof).

Reference writer: flow_graph/param/h2_compressor.py --write (ledger row
`sizing_h2_compressor`, section B, MIXED: sizing -> function, doc -> renderer).
The committed graph carries every field the stage writes; the proofs:

- exact change set: the function's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (the compressor_design block is a raw
  v1 float book family - exact equality, zero enumerated drift);
- the equal-ratio stage search and the per-stage grid as integer books
  (stages, unit count, the 4 dp kW books);
- the value-only SF feed update;
- determinism: two runs, byte-identical; the no-drivers bridge contract;
- grid purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os

from flow_graph.v2.functions import h2_compressor as HC
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every field the function writes.
EXPECTED_NODE_FIELDS = [
    ('CRYO_H2', 'params.compressor_design'), ('CRYO_H2', 'params.compressor'),
    ('CRYO_H2', 'continuous_kw'),
]
EXPECTED_EDGE_FIELDS = [('SF-CRYO_H2', 'rate')]


def run():
    b = load(REF_GRAPH)
    HC.h2_compressor(b, INPUTS)
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
        cur = cur[part]
    return cur


def _strict_diffs(c_obj, r_obj, prefix, out, expected):
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
    """The committed design books, hand-enumerated (X-MFG-36 Rev C; A-M-169)."""
    b = run()
    out = json.loads(render(b))
    n = {x['unit_id']: x for x in out['nodes']}
    d = n['CRYO_H2']['params']['compressor_design']
    assert d['H2_kg_d'] == 11.455283000000001 and d['n_stages'] == 5
    assert d['T_limit_C'] == 135.0 and d['ratio_per_stage'] == 1.8205642030260802
    assert d['kWh_per_kg'] == 1.974725678896425
    assert d['P_avg_kW'] == 0.9425433957969033 and d['P_peak_kW'] == 2.8276301873907097
    assert d['units'] == 2
    assert d['material'] == ('head and plates 17-4PH H1150 / 316L (hydrogen service), triple-layer 301 SS '
                             'diaphragm with leak detection between layers')
    assert len(d['stages']) == 5
    s1, s5 = d['stages'][0], d['stages'][4]
    assert s1['stage'] == 1 and s1['P_in_bar'] == 10.0 and s1['P_out_bar'] == 18.2056420302608
    assert s1['T_out_C'] == 125.22502918535349 and s1['intercooler_W'] == 513.1878949625424
    assert s1['swept_cm3'] == 126.36738782847159 and s1['diaphragm_D_mm'] == 327.51178640174663
    assert s5['stage'] == 5 and s5['P_in_bar'] == 109.85605433061178 and s5['P_out_bar'] == 200.0
    assert s5['swept_cm3'] == 11.502997135521449 and s5['diaphragm_D_mm'] == 98.81319357225266
    assert n['CRYO_H2']['params']['compressor'] == \
        'in-house 5-stage diaphragm, 10 to 200 bar, intercooled, 2 x 100 % (X-MFG-36)'
    ck = n['CRYO_H2']['continuous_kw']
    assert ck['value'] == 0.9425 and ck['unit'] == 'kW' and ck['status'] == 'study'
    assert ck['note'] == ('X-MFG-36 (A-M-169): 11.46 kg/d x 1.97 kWh/kg; peak 2.83 kW over the run hours.')


def test_suction_mass_is_the_seed_sum():
    """H2_kg_d is the committed mass books into CRYO_H2 (storage + electrolysis)."""
    b = load(REF_GRAPH)
    m = HC.h2_mass_kg_d(b)
    assert m == 1.103286 + 10.351997                    # S64 + IA-ELY-H2, edge-list order
    d = run().computed[('node', 'CRYO_H2', 'params.compressor_design')][0]
    assert d['H2_kg_d'] == m


def test_stage_search_and_grid_books():
    """The stage search is integer combinatorics (fewest stages within the
    API618 135 C limit); the kW books quantise at 4 dp through integer books."""
    b = run()
    d = b.computed[('node', 'CRYO_H2', 'params.compressor_design')][0]
    assert isinstance(d['n_stages'], int) and d['n_stages'] == 5
    assert isinstance(d['units'], int) and d['units'] == 2
    assert all(isinstance(s['stage'], int) for s in d['stages'])
    # one stage of 20x would run at 436 C - the search had to climb to 5 stages
    drv = INPUTS['drivers']
    t1 = float(drv['CRYO.cold-box-asu-recovery-train.cold-box.CRYO_H2.h2c_T_suction_K']['value'])
    eta = float(drv['h2c_eta_ad']['value'])
    k = float(drv['h2c_k']['value'])
    x = (k - 1) / k
    t1_stage = t1 * (1 + (20.0 ** x - 1) / eta) - 273.15
    assert t1_stage > 135.0
    assert d['stages'][0]['T_out_C'] <= 135.0
    assert HC.unbook(HC.book(0.9425433957969033, 4, 'power kW'), 4) == 0.9425
    assert HC.unbook(HC.book(2.675, 2, ''), 2) == 2.67   # exact-binary half-even


def test_sf_feed_is_value_only():
    """Only the SF-CRYO_H2 value moves; the seed note passes through."""
    committed = _committed()
    c_sf = next(e for e in committed['edges'] if e['stream_id'] == 'SF-CRYO_H2')
    b = run()
    out = json.loads(render(b))
    r_sf = next(e for e in out['edges'] if e['stream_id'] == 'SF-CRYO_H2')
    assert r_sf['rate']['value'] == 0.9425
    assert r_sf['rate']['note'] == c_sf['rate']['note']


def test_no_declared_inputs_records_nothing():
    b = load(REF_GRAPH)
    HC.h2_compressor(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'h2_compressor' and prov.basis
    assert b.computed[('node', 'CRYO_H2', 'params.compressor_design')][1].ref == 'A-M-169'
    assert b.computed[('edge', 'SF-CRYO_H2', 'rate')][1].ref == 'A-M-169'


def test_function_module_grid_purity():
    tree = ast.parse(inspect.getsource(HC))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
