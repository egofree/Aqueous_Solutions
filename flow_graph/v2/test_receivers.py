"""engine v2: the receivers family acceptance (the golden-value proof).

Reference writer: flow_graph/param/receivers.py --write (ledger row
`sizing_receivers`, section B, MIXED: sizing -> function, doc -> renderer).
The committed graph carries every field the stage writes; the proofs:

- exact change set: the function's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved - in
  particular the relief books (relief_mm / relief_basis / design_kPa) the v1
  receivers writer never touches stay byte-faithful (one writer per field: the
  write_graph relief family owns them);
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (the crew-reserve bank volume is a raw
  v1 float book - exact equality, zero enumerated drift);
- the B31.3 wall grid and the manifold-half rule as integer books (tubes, rows,
  whole-mm rack, the 4 dp store books);
- the seed reads: the H2/O2 store volumes, the crew reserve branch and the
  design_kPa driver fallback;
- determinism: two runs, byte-identical; the no-drivers bridge contract;
- grid purity: no float literals and no I/O in the function module.
"""
import ast
import inspect
import json
import os

import pytest

from flow_graph.v2.functions import receivers as RC
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}
UNITS = ('CRYO_H2', 'CRYO_O2', 'CRYO_CO2')

# The change-set specification: every field the function writes.
EXPECTED_NODE_FIELDS = (
    [(u, 'params.design') for u in UNITS]
    + [(u, 'params.size_mm') for u in UNITS]
    + [(u, 'params.size_note') for u in UNITS]
    + [('CRYO_CO2', 'params.store_kg'), ('CRYO_CO2', 'params.store_water_volume_m3')]
)


def run():
    b = load(REF_GRAPH)
    RC.gas_receivers(b, INPUTS)
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
    assert got_nodes == sorted(EXPECTED_NODE_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_NODE_FIELDS)),
        sorted(set(EXPECTED_NODE_FIELDS) - set(got_nodes)))
    assert not [(sid, path) for (kind, sid, path) in b.computed if kind == 'edge']

    for uid, path in EXPECTED_NODE_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_NODE_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    # no edge moves at all: the stage writes no edge state
    for sid in c_edges:
        assert c_edges[sid] == r_edges[sid], sid


def test_changed_values_spot_checks():
    """The committed design books, hand-enumerated (AQS-DUTY-065 Rev B)."""
    b = run()
    out = json.loads(render(b))
    n = {x['unit_id']: x for x in out['nodes']}
    h2 = n['CRYO_H2']['params']['design']
    o2 = n['CRYO_O2']['params']['design']
    co2 = n['CRYO_CO2']['params']['design']
    for d in (h2, o2, co2):
        assert d['P_design_MPa'] in (22.0, 2.2) and d['S_MPa'] == 115.0
        assert d['t_min_mm'] == 11.8038 and d['t_ok'] is True
        assert d['OD_mm'] == 114.3 and d['ID_mm'] == 87.32
        assert d['tube_m'] == 6.096 and d['D_mm'] == 114 and d['wall_mm'] == 13.49
        assert d['T_C'] == 25 and d['material'].startswith('SA-312 TP316L seamless DN100 Sch 160')
    assert h2['t_req_mm'] == 10.1559 and o2['t_req_mm'] == 10.1559 and co2['t_req_mm'] == 1.085
    assert h2['banks'] == [{'bank': 'main', 'V_m3': 1.21, 'tubes': 34, 'halves': 2}]
    assert o2['banks'][0] == {'bank': 'main', 'V_m3': 0.5, 'tubes': 14, 'halves': 2}
    assert o2['banks'][1]['bank'] == 'crew reserve'
    assert o2['banks'][1]['V_m3'] == 0.02379286214135759          # the raw v1 float bank book
    assert o2['banks'][1]['tubes'] == 2 and o2['banks'][1]['halves'] == 2
    assert co2['banks'] == [{'bank': 'main', 'V_m3': 0.0974, 'tubes': 4, 'halves': 2}]
    assert (h2['tubes'], o2['tubes'], co2['tubes']) == (34, 16, 4)
    assert h2['steel_kg'] == 5865.5712 and o2['steel_kg'] == 2760.2688 and co2['steel_kg'] == 690.0672
    assert h2['H_mm'] == 1050 and o2['H_mm'] == 600 and co2['H_mm'] == 450
    assert n['CRYO_H2']['params']['size_mm'] == [6696, 1500, 1050]
    assert n['CRYO_O2']['params']['size_mm'] == [6696, 1500, 600]
    assert n['CRYO_CO2']['params']['size_mm'] == [6696, 1500, 450]
    assert n['CRYO_CO2']['params']['store_kg'] == 90.437
    assert n['CRYO_CO2']['params']['store_water_volume_m3'] == 0.0974
    for u in UNITS:
        assert n[u]['params']['size_note'] == \
            'L x W x H mm tube rack, set by flow_graph/param/receivers.py (A-M-167)'


def test_b31_wall_and_manifold_grid():
    """The wall book and the manifold-half rule on integer books."""
    b = run()
    h2 = b.computed[('node', 'CRYO_H2', 'params.design')][0]
    # t_req = P D/(2(S E + P Y)) with Y 0.4: 22 x 114.3 / (2 x (115 + 8.8))
    drv = INPUTS['drivers']
    p = 22.0
    od = float(drv['CRYO.cold-box-asu-recovery-train.cold-box.rcv_tube_OD_mm']['value'])
    s = float(drv['s_316L_38C_MPa']['value'])
    t_req = p * od / (2 * (s + p * 0.4))
    assert h2['t_req_mm'] == RC.unbook(RC.book(t_req, 4, 'mm'), 4) == 10.1559
    assert h2['tubes'] % 2 == 0                          # whole manifolded halves
    assert h2['H_mm'] == 5 * 150 + 300                  # rows x pitch + rack allowance, integers
    assert RC.unbook(RC.book(2.675, 2, ''), 2) == 2.67   # exact-binary half-even


def test_co2_store_books_and_inflow_sum():
    """A-M-181: the store mass is the 2 d hold on the committed inflow books."""
    b = load(REF_GRAPH)
    inflow = RC.co2_inflow_kg_d(b)
    assert inflow == 0.0 + 13.810366 + 8.625641 + 22.782645   # S18 + S67B + S82 + IA-ASU-CO2
    b = run()
    assert b.computed[('node', 'CRYO_CO2', 'params.store_kg')][0] == 90.437
    assert b.computed[('node', 'CRYO_CO2', 'params.store_water_volume_m3')][0] == 0.0974


def test_seed_reads_crew_reserve_branch():
    """The crew-reserve bank is conditional on the X-RED-04 seed book; without
    it the main bank alone carries the store (and the main book is unchanged)."""
    b = load(REF_GRAPH)
    del b.nodes['CRYO_O2']['params']['crew_reserve_kg']
    RC.gas_receivers(b, INPUTS)
    d = b.computed[('node', 'CRYO_O2', 'params.design')][0]
    assert d['banks'] == [{'bank': 'main', 'V_m3': 0.5, 'tubes': 14, 'halves': 2}]
    assert d['tubes'] == 14 and d['H_mm'] == 600


def test_design_kpa_driver_fallback():
    """R11 Rev AC: where a node lost params.design_kPa the module basis driver
    carries the design pressure (A-M-167 22 MPa / A-M-180 2200 kPa g)."""
    b = load(REF_GRAPH)
    del b.nodes['CRYO_CO2']['params']['design_kPa']
    RC.gas_receivers(b, INPUTS)
    d = b.computed[('node', 'CRYO_CO2', 'params.design')][0]
    assert d['P_design_MPa'] == 2.2 and d['t_req_mm'] == 1.085
    b = load(REF_GRAPH)
    for u in UNITS:
        b.nodes[u]['params'].pop('design_kPa', None)
    RC.gas_receivers(b, INPUTS)
    assert b.computed[('node', 'CRYO_H2', 'params.design')][0]['P_design_MPa'] == 22.0


def test_relief_books_untouched():
    """One writer per field: the relief family owns relief_mm / relief_basis /
    design_kPa on these nodes; this stage stamps none of them."""
    committed = _committed()
    c_nodes = {n['unit_id']: n for n in committed['nodes']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    for u in UNITS:
        assert c_nodes[u]['params']['relief_basis'] == r_nodes[u]['params']['relief_basis']
        assert c_nodes[u]['params']['relief_mm'] == r_nodes[u]['params']['relief_mm']
        assert c_nodes[u]['params']['design_kPa'] == r_nodes[u]['params']['design_kPa']
        assert ('node', u, 'params.relief_basis') not in b.computed


def test_no_declared_inputs_records_nothing():
    b = load(REF_GRAPH)
    RC.gas_receivers(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'receivers' and prov.basis
    assert b.computed[('node', 'CRYO_CO2', 'params.store_kg')][1].ref == 'A-M-181'
    assert b.computed[('node', 'CRYO_H2', 'params.design')][1].ref == 'A-M-167'


def test_function_module_grid_purity():
    tree = ast.parse(inspect.getsource(RC))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
