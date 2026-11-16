"""engine v2: the PV cell-line family acceptance (the golden-value proof).

Reference writers: flow_graph/param/pv_cell_line.py with the pv_wafer.need()
cell rate it consumes, ledger row `sizing_pv_cell_line` (section B, MIXED -
split sizing -> function, the PV_CELL_LINE.md page -> the renderer wave). The
committed graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (SOLAR_PV_CELL continuous_kw, params.avg_kw, params.design;
  the SF-SOLAR_PV_CELL feed value-only), and a strict whole-model walk proves
  nothing else moved;
- golden equality: every changed field equals the committed golden - the
  quantised books at the golden's decimals, the params.design tool book
  repr-exact (it is the reference writer's raw float book, ported as the
  documented v1 float replica: identical expressions over identical inputs);
- grid spot-checks on the integer and derived books: 65.6 cells/d from the
  roof-array replacement need (2653 kW nameplate, 40 yr module life at the
  median degradation plus random failures), 3 batches of the 25-wafer carrier,
  the 210-slot diffusion boat, the line peak = the largest tool, the energy
  sum, the 4 dp average book;
- the SF feed books value-only (the X-RSZ-07 feed pass owns the note);
- the bridge contract: no drivers records nothing;
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O in the module.

Integer-scale table (the quantise at each stamp; half-even throughout, Python
round()'s tie rule): continuous_kw.value and params.avg_kw 4 dp on the kW
book; the SF feed 4 dp on the same book; the tool book itself is the v1 raw
float book (unrounded by design, documented in the module docstring); batches,
carrier, boat and the integer constants enter as integers.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import pv_cell_line as PV
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

EXPECTED_FIELDS = [
    ('SOLAR_PV_CELL', 'continuous_kw'), ('SOLAR_PV_CELL', 'params.avg_kw'),
    ('SOLAR_PV_CELL', 'params.design'),
]
EXPECTED_EDGES = [
    ('SF-SOLAR_PV_CELL', 'rate'),
]


def run():
    b = load(REF_GRAPH)
    PV.pv_cell_line(b, INPUTS)
    return b


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, b) for a, b in zip(gold, got))
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        return isinstance(got, (int, float)) and not isinstance(gold, bool) and _num_eq(gold, got)
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
    assert got_edges == sorted(EXPECTED_EDGES)

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGES:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    expected_node_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths)
    assert diffs == set(), sorted(diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGES}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths)
    assert edge_diffs == set(), sorted(edge_diffs)


def test_grid_spot_checks():
    """The cell-need chain and the tool books, hand-enumerated: 65.6 cells/d,
    3 batches, the 210-slot boat, peak = largest tool, the energy sum, the
    4 dp average book."""
    b = run()
    d = b.computed[('node', 'SOLAR_PV_CELL', 'params.design')][0]
    nd = d['need']
    # the replacement need: (1-0.8)/0.005 = 40 yr life; +0.0005 failures/yr;
    # 2653 kW x 1000 W/kW x 0.0255/yr / 365.25 d = 185.22 W/d of cells
    assert nd['route'] == 'CZ_PSQ125' and nd['array_kw'] == 2653.0
    dv = lambda k: INPUTS['drivers'][k]['value']                   # the getter _core hands _need
    assert PV._need(dv, 2653)['life_yr'] == 39.99999999999999
    assert PV._need(dv, 2653)['repl_per_yr'] == 0.025500000000000005
    assert nd['W_d'] == 185.2197125256674
    # the semi-square cell: 125 mm square in a 150 mm ingot -> 148.58 cm2;
    # 0.19 efficiency at 1000 W/m2 -> 2.823 W/cell -> 65.6 cells/d
    assert nd['cell_area_cm2'] == 148.5798641851732 and nd['cell_W'] == 2.823017419518291
    assert nd['cells_per_d'] == 65.61054538489975
    assert abs(round(nd['cells_per_d'], 1) - 65.6) < 1e-9
    # batches of one carrier; the boat check
    assert d['carrier'] == 25 and d['batches'] == 3
    assert int(INPUTS['drivers']['pvl_diff_L_m']['value'] * PV.K1000
               / INPUTS['drivers']['FAB.wafer-line-train.SOLAR_PV_CELL.pvl_boat_pitch_mm']['value']) == 210
    # the tool book: seven tools, the sum, the peak = the largest tool, 4 dp avg
    assert [t['id'] for t in d['tools']] == ['PV-TEX-01', 'PV-EMIT-01', 'PV-PSG-01', 'PV-ARC-01',
                                             'PV-CON-01', 'PV-FIRE-01', 'PV-IV-01']
    assert d['kWh_d'] == sum(t['kWh_d'] for t in d['tools'])
    assert d['peak_kW'] == max(t['peak_kW'] for t in d['tools'])
    assert d['peak_kW'] == d['tools'][3]['peak_kW']                        # PECVD governs the line peak
    assert d['avg_kW'] == d['kWh_d'] / PV.K24
    assert d['kWh_per_cell'] == d['kWh_d'] / d['cells_per_d']
    # the quantised stamps: 4 dp on the kW book
    assert b.computed[('node', 'SOLAR_PV_CELL', 'params.avg_kw')][0] == 1.4673
    assert b.computed[('edge', 'SF-SOLAR_PV_CELL', 'rate')][0]['value'] == 1.4673
    note = b.computed[('node', 'SOLAR_PV_CELL', 'continuous_kw')][0]['note']
    assert note == ('X-MFG-38 (A-M-178, AQS-DUTY-071): 35.22 kWh/d for 65.6 cells/d in 3 batches of one '
                    'carrier (A-M-484); peak 6.08 kW (one tool at a time).')


def test_sf_feed_books_value_only():
    """The SF feed carries this family's value; the note stays the X-RSZ-07
    feed pass's (the committed residue, not overwritten)."""
    with open(REF_GRAPH, encoding='utf-8') as f:
        gold_rate = {e['stream_id']: e for e in json.load(f)['edges']}['SF-SOLAR_PV_CELL']['rate']
    b = run()
    fresh = b.computed[('edge', 'SF-SOLAR_PV_CELL', 'rate')][0]
    assert fresh['value'] == 1.4673
    assert fresh['note'] == gold_rate['note'] == 'X-RSZ-07 feed edges for unfed loads. Equals node continuous_kw (study).'
    # the SQ heat edge died with HEAT_SINK in Rev AC: the exists-guard holds
    assert 'SQ-SOLAR_PV_CELL' not in b.edges
    assert not [k for k in b.computed if k[1] == 'SQ-SOLAR_PV_CELL']


def test_bridge_contract():
    """No drivers records nothing (the bridge contract)."""
    b = load(REF_GRAPH)
    PV.pv_cell_line(b, {})
    assert b.computed == {}


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (_value, prov) in b.computed.items():
        assert prov.stage == 'sizing_pv_cell_line' and prov.basis


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(PV))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
