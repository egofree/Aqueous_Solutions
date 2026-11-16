"""engine v2: the methanol-train family acceptance (the golden-value proof).

Reference writer: flow_graph/param/meoh_train.py, ledger row `sizing_meoh_train`
(section B, MIXED - split sizing -> function, the MEOH_TRAIN.md page -> the
renderer wave). The committed graph carries every field the family stamps; the
proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (2 units x {params.design, params.size_note}), and a strict
  whole-model walk (nodes and edges, same JSON types) proves nothing else
  moved;
- golden equality: every changed field equals the committed golden, numbers
  exact at the golden's decimals (repr-exact), strings verbatim;
- grid spot-checks on the integer books: the knock-out pot on the 50 mm
  vessel grid (D 400 x H 600 from the 72.24 L book), the 28-cell stack at the
  IEC62282_3_100 cell point, the LMTD book from the 60-digit log, the Q-039
  continuous book riding S79 at 0.5 kW_e;
- the bridge contract: no drivers records nothing;
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O in the module.

Integer-scale table (the quantise at each stamp; half-even throughout, Python
round()'s tie rule): design floats 4 dp (water, duty, area, stack area, the
seed species reads, the S79 continuous book); LMTD 1 dp; drum volume 2 dp;
methanol LHV power 3 dp; bore, height and cell count integers (ceil rules: the
50 mm vessel grid, the installed-rating cell count).
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import meoh_train as MT
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

EXPECTED_FIELDS = [
    ('MEOH_COND', 'params.design'), ('MEOH_COND', 'params.size_note'),
    ('MEOH_FC', 'params.design'), ('MEOH_FC', 'params.size_note'),
]


def run():
    b = load(REF_GRAPH)
    MT.meoh_train(b, INPUTS)
    return b


def _num_eq(gold, got):
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
    the expected change set: strict (same JSON types) everywhere. Provenance
    rows, added by the serializer on touched objects, are excluded."""
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
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = json.load(f)
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_FIELDS)
    assert got_edges == []

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, set())
    assert edge_diffs == set(), sorted(edge_diffs)


def test_grid_spot_checks():
    """The integer books, hand-enumerated: the pot on the 50 mm grid, the
    28-cell stack, the LMTD book, the Q-039 continuous book."""
    b = load(REF_GRAPH)
    s = MT._core(b, INPUTS)
    cond, fc = s
    seed = load(REF_GRAPH)
    w1 = MT.rat(seed.edges['IA-MEOH-H2O']['rate']['value'])
    w2 = MT.rat(seed.edges['S81']['rate']['value'])
    m_h2o = w1 + w2
    assert cond['water_kg_d'] == MT.fq(m_h2o, 4, 'check') == 27.0455
    # duty: m cp dT + latent at the drivers (1.9 kJ/kgK, 20 K, 2257 kJ/kg)
    m_s = m_h2o / 86400
    assert cond['condensing_kW'] == MT.fq(m_s * (MT.rat('1.9') * 20 + 2257), 4, 'check') == 0.7184
    # LMTD: (25-15)/ln(25/15) -> 19.6 at 1 dp
    assert cond['LMTD_K'] == 19.6
    # area at U 1.2: 0.0306 m2 = one 10 mm x 1 m coil tube
    assert cond['area_m2'] == 0.0306 and cond['tube'] == '1 x 10 mm x 1 m coil'
    # knock-out pot: 30 s of vapour at rho 0.13 governs over the condensate; the
    # 72.24 L book -> D 400 x H 600 on the 50 mm grid at H/D 2
    assert cond['drum_L'] == 72.24 and cond['D_mm'] == 400 and cond['H_mm'] == 600
    assert cond['D_mm'] % 50 == 0 and cond['H_mm'] % 50 == 0
    # the fuel cell: installed 1.0 kW at 0.6 V x 200 cm2 x 0.3 A/cm2 = 28 cells
    assert fc['rated_kWe'] == 1.0 and fc['n_cells'] == 28 and fc['stack_area_m2'] == 0.56
    assert fc['cell_V'] == 0.6 and fc['j_A_cm2'] == 0.3 and fc['cell_A_cm2'] == 200
    assert MT.rat(fc['cell_V']) == MT.rat('0.6') and MT.rat(fc['j_A_cm2']) == MT.rat('0.3')
    # Q-039: the continuous book rides S79 (0.5 kW_e), the methanol LHV power at 3 dp
    assert fc['continuous_kW'] == MT.fq(MT.rat(load(REF_GRAPH).edges['S79']['rate']['value']), 4, 'check') == 0.5
    assert fc['methanol_kg_d'] == 5.0 and fc['methanol_energy_kW'] == 1.152
    assert fc['air_O2_kg_d'] == 9.4071 and fc['water_kg_d'] == 7.251
    assert fc['CO2_kg_d'] == 8.6256 and fc['heat_kW'] == 0.3689


def test_bridge_contract():
    """No drivers records nothing (the bridge contract)."""
    b = load(REF_GRAPH)
    MT.meoh_train(b, {})
    assert b.computed == {}


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (_value, prov) in b.computed.items():
        assert prov.stage == 'sizing_meoh_train' and prov.basis


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(MT))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
