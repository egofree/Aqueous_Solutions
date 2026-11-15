"""engine v2: the heat-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/write_graph.py, command `heat` (ledger row
`write_graph_heat` - the X-THM-01 store-ledger re-solve, R10b). The committed
graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (4 node fields, 19 edge rates, 2 edge params), and a strict
  whole-model walk (nodes and edges, same JSON types) proves nothing else
  moved - the ladder layer repair and the Q3 rated-draw seed are already
  satisfied on the committed seed and record nothing;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact equality, zero enumerated drift);
- the key thermal arithmetic re-checked on exact Decimal books: the down
  transits, the Q3 supply-limited pro-rata draws, the store-bus link, the Q4
  bus close (GEO_HP idle, terminal by difference), the terminal closure
  (in-sum = out-sum at DRY_COOLER), and the dry-cooler rating at the
  AQS-DUTY-008 section 3 margin and the 0.05 kW_fan/kW_th fan class;
- the charge-window derivation table: night_hours -> window as data rows,
  including the 24 h polar-night clamp, plus the window-rate books through
  the registered function on tampered drivers;
- the bridge contracts: no driver payload records nothing; no committed store
  book records nothing (the power-family book cannot be invented); the rating
  guard keeps the terminal closure while skipping the rating;
- determinism: two runs, byte-identical;
- grid purity: no float literals and no I/O in the family module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import heat as HT
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [
    ('ZNBR2', 'params.cycling_thermal'),
    ('DRY_COOLER', 'params.rated_kW'), ('DRY_COOLER', 'params.fan_kW'), ('DRY_COOLER', 'params.basis'),
]
EXPECTED_EDGES = [
    ('HL-Q1-A-DOWN', 'rate'), ('HL-Q1-B-DOWN', 'rate'), ('HL-Q2-A-DOWN', 'rate'), ('HL-Q2-B-DOWN', 'rate'),
    ('HL-Q3-A-HX4', 'rate'), ('HL-Q3-A-HX5', 'rate'), ('HL-Q3-A-HX6', 'rate'),
    ('HL-Q3-B-HX4', 'rate'), ('HL-Q3-B-HX5', 'rate'), ('HL-Q3-B-HX6', 'rate'),
    ('HL-Q3-A-DOWN', 'rate'), ('HL-Q3-B-DOWN', 'rate'),
    ('HL-Q4-A-BUS', 'rate'), ('HL-Q4-B-BUS', 'rate'),
    ('IA-ZNBR-HEAT', 'rate'), ('S53', 'rate'), ('S44', 'rate'), ('HL-Q4-REJ', 'rate'), ('IA-DC-REJ', 'rate'),
]
EXPECTED_EDGE_FIELDS = [
    ('HL-Q4-A-BUS', 'params.duty_normal_kw'), ('HL-Q4-B-BUS', 'params.duty_normal_kw'),
]


def run():
    b = load(REF_GRAPH)
    HT.charge_window(b, INPUTS)
    HT.fuel_cell_heat(b, INPUTS)
    HT.heat_ledger(b, INPUTS)
    HT.dry_cooler(b, INPUTS)
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
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields, where numeric equality at the golden's decimals holds.
    Provenance rows, added by the serializer on touched objects, are excluded."""
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
    assert got_nodes == sorted(EXPECTED_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_FIELDS)), sorted(set(EXPECTED_FIELDS) - set(got_nodes)))
    assert got_edges == sorted(EXPECTED_EDGES + EXPECTED_EDGE_FIELDS), (
        sorted(set(got_edges) - set(EXPECTED_EDGES) - set(EXPECTED_EDGE_FIELDS)),
        sorted(set(EXPECTED_EDGES) - set(got_edges)))

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGES + EXPECTED_EDGE_FIELDS:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields
    expected_node_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths)
    assert diffs == set(), sorted(diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGES + EXPECTED_EDGE_FIELDS}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths)
    assert edge_diffs == set(), sorted(edge_diffs)


def test_thermal_arithmetic_on_exact_books():
    """The key thermal books re-derived as exact Decimal arithmetic,
    independent of the stamping."""
    b = run()
    # ladder transits: tier source less the standing loss, then + burnout - loss
    assert HT.transit_down(Decimal('1.383'), Decimal('0.25')) == Decimal('1.133')
    assert HT.transit_down(Decimal('1.133') + Decimal('0.928'), Decimal('0.17')) == Decimal('1.891')
    # Q3 supply-limited draws: 1.891 kW pro-rata on the 10.322 kW rated profile
    draws = {k: b.computed[('edge', k, 'rate')][0]['value'] for k in
             ('HL-Q3-A-HX4', 'HL-Q3-A-HX5', 'HL-Q3-A-HX6')}
    assert draws == {'HL-Q3-A-HX4': 0.0553, 'HL-Q3-A-HX5': 1.4548, 'HL-Q3-A-HX6': 0.3809}
    r3 = Decimal('0.302') + Decimal('7.941') + Decimal('2.079')
    assert r3 == Decimal('10.322')
    assert HT.pro_rata(Decimal('1.891'), Decimal('7.941'), r3).quantize(Decimal('0.0001')) == Decimal('1.4548')
    assert sum(Decimal(str(v)) for v in draws.values()) == Decimal('1.891')   # the supply is fully drawn
    # Q3 -> Q4 carries 0; the store-bus link closes on HX-8 split + trim
    assert b.computed[('edge', 'HL-Q3-A-DOWN', 'rate')][0]['value'] == 0.0
    assert b.computed[('edge', 'HL-Q4-A-BUS', 'rate')][0]['value'] == 2.286 + 1.61
    # Q4 bus close: GEO_HP idle, the terminal carries the store surplus by difference
    assert b.computed[('edge', 'S44', 'rate')][0]['value'] == 0.0
    assert b.computed[('edge', 'HL-Q4-REJ', 'rate')][0]['value'] == 49.1464
    need = Decimal('20.8144') - (Decimal('62.1688') + Decimal('7.792'))
    assert (-need).quantize(Decimal('0.0001')) == Decimal('49.1464')
    # terminal closure: the cooler passes the duty it receives to ambient air
    assert b.computed[('edge', 'IA-DC-REJ', 'rate')][0]['value'] == 56.3964
    assert Decimal('49.1464') + Decimal('7.25') == Decimal('56.3964')
    # dry-cooler rating: bounding duty = terminal book - ZNBR average + ZNBR window rate
    r = HT.cooler_rating(Decimal('56.3964'), Decimal('47.4792'), Decimal('113.95'))
    assert r['bound'] == Decimal('122.8672')
    assert r['rated'] == 154 and HT.MARGIN * r['bound'] == Decimal('153.584')   # ceil -> 154
    assert HT.FAN_CLASS * r['rated'] == Decimal('7.7')                          # the 0.05 class
    ck = b.computed[('node', 'DRY_COOLER', 'params.rated_kW')][0]
    assert ck == 154.0
    assert b.computed[('node', 'DRY_COOLER', 'params.fan_kW')][0] == 7.7


def test_fuel_cell_stack_heat():
    """F-11: the full physical stack heat - S49 LHV in less the S51 draw."""
    b = run()
    assert b.computed[('edge', 'S53', 'rate')][0]['value'] == 2.666
    lhv = Decimal(str(INPUTS['drivers']['ELEC.generation-train.BACKUP_GEN.h2_lhv_kWh_kg']['value']))
    assert Decimal('4.8') * lhv / 24 == Decimal('6.666')
    assert Decimal('6.666') - Decimal('4.0') == Decimal('2.666')
    assert b.computed[('edge', 'S53', 'rate')][0]['note'].endswith(
        'the bus ledger takes the full credit.')
    assert 'S49 4.8 kg/d H2 x 33.33 kWh/kg LHV' in b.computed[('edge', 'S53', 'rate')][0]['note']


def test_charge_window_derivation_table():
    """night_hours -> window as data rows, including the 24 h polar-night
    clamp; then the window-rate books of synthetic stores on the same rule."""
    table = [('14', '10'), ('10', '14'), ('12', '12'), ('24', '24'), ('0', '24')]  # night -> window, h
    for night, win in table:
        wk = HT.window_book(Decimal('2658.8'), Decimal('3798.3'), Decimal(night), Decimal('0.7'))
        assert wk['win_h'] == Decimal(win), (night, win)
    # the clamp keeps a real book: a zero window is never a rate denominator
    wk = HT.window_book(Decimal('100'), Decimal('150'), Decimal(24), Decimal('0.7'))
    assert wk['win_kw'] == Decimal('50') / 24 and wk['chg'] == Decimal('150') / 24
    # the committed book: loss 1139.5 kWh/d, 47.4792 kW ledger average,
    # 113.95 kW window rate against a 379.83 kW charge rate over 10 h
    wk = HT.window_book(Decimal('2658.8'), Decimal('3798.3'), Decimal('14'), Decimal('0.7'))
    assert wk['loss'] == Decimal('1139.5')
    assert wk['avg'].quantize(Decimal('0.0001')) == Decimal('47.4792')
    assert wk['win_kw'] == Decimal('113.95') and wk['chg'] == Decimal('379.83')


def test_charge_window_through_the_registered_function():
    """The window book flows through the registered function: the golden
    driver set reproduces the committed book; the polar-night and short-night
    driver sets move the window and the window rates, never the daily loss."""
    b = load(REF_GRAPH)
    HT.charge_window(b, INPUTS)
    book = b.computed[('node', 'ZNBR2', 'params.cycling_thermal')][0]
    assert book['window_h'] == 10.0 and book['loss_kwh_d'] == 1139.5
    assert book['avg_kW'] == 47.48 and book['window_kW'] == 113.95
    assert book['charge_kW_window'] == 379.83 and book['round_trip'] == 0.7
    assert b.computed[('edge', 'IA-ZNBR-HEAT', 'rate')][0]['value'] == 47.4792
    assert '2659 kWh/d out at round trip 0.7' in b.computed[('edge', 'IA-ZNBR-HEAT', 'rate')][0]['note']
    assert 'window thermal rate 114.0 kW' in b.computed[('edge', 'IA-ZNBR-HEAT', 'rate')][0]['note']
    for night, win in ((24, 24.0), (10, 14.0), (0, 24.0)):
        drv = json.loads(json.dumps(INPUTS['drivers']))
        drv['night_hours']['value'] = night
        bb = load(REF_GRAPH)
        HT.charge_window(bb, {'drivers': drv})
        bk = bb.computed[('node', 'ZNBR2', 'params.cycling_thermal')][0]
        assert bk['window_h'] == win and bk['loss_kwh_d'] == 1139.5          # the clamp, and the loss is day-invariant
        win_rate = (Decimal('1139.5') / Decimal(str(win))).quantize(Decimal('0.01'))
        chg_rate = (Decimal('3798.3') / Decimal(str(win))).quantize(Decimal('0.01'))
        assert bk['window_kW'] == float(win_rate) and bk['charge_kW_window'] == float(chg_rate)


def test_store_link_books_and_f25_note():
    """The F-25 N+1 book: the store-bus links carry the design-day normal
    flow, the note keeps the F-25 base and the earlier X-THM-01 segments."""
    b = run()
    for s in ('HL-Q4-A-BUS', 'HL-Q4-B-BUS'):
        assert b.computed[('edge', s, 'params.duty_normal_kw')][0] == 3.896
        note = b.computed[('edge', s, 'rate')][0]['note']
        assert note.startswith('N+1 pair (HEAT_LADDER.md section 3, A-M-453)')
        assert '| X-THM-01 R10b: store-bus link = HX-8 split + rectifier trim + Q3 down (store closes) ' \
            '(A-M-259).' in note
    assert '5.51 kW less 0.7619 kW of insulated line loss upstream (A-M-166)' in \
        b.computed[('edge', 'HL-Q4-A-BUS', 'rate')][0]['note']           # the earlier segment is preserved
    assert '5.51 kW less 0.8371 kW of insulated line loss upstream (A-M-166)' in \
        b.computed[('edge', 'HL-Q4-B-BUS', 'rate')][0]['note']


def test_layer_repair_and_draws_seed_fire():
    """The repair ports record only when the seed needs them: a mislabelled
    ladder layer is corrected; a missing rated-draw profile is seeded from the
    current edge books and the draws still solve to the same pro-rata book."""
    b = load(REF_GRAPH)
    b.edges['HL-Q2-X']['layers'] = ['mass']                              # the mislabel the ledger missed
    del b.nodes['Q3_A']['params']['x_thm_rated_draws']
    HT.charge_window(b, INPUTS)
    HT.fuel_cell_heat(b, INPUTS)
    HT.heat_ledger(b, INPUTS)
    assert b.computed[('edge', 'HL-Q2-X', 'layers')][0] == ['thermal']
    seed = b.computed[('node', 'Q3_A', 'params.x_thm_rated_draws')][0]
    assert seed == {'HL-Q3-A-HX4': 0.0553, 'HL-Q3-A-HX5': 1.4548, 'HL-Q3-A-HX6': 0.3809}
    assert b.computed[('edge', 'HL-Q3-A-HX5', 'rate')][0]['value'] == 1.4548   # same pro-rata book off the seed
    assert ('edge', 'HL-Q1-X', 'layers') not in b.computed                     # a correct seed records nothing


def test_no_drivers_records_nothing():
    """The bridge solve / check carry no driver payload: the family records
    nothing and the seed stands (the specialty-family contract)."""
    b = load(REF_GRAPH)
    HT.charge_window(b, {})
    HT.fuel_cell_heat(b, {})
    HT.heat_ledger(b, {})
    HT.dry_cooler(b, {})
    assert b.computed == {}


def test_store_book_bridge_guard():
    """The store book is power-family state read from the seed: without it the
    charge window records nothing, and the rating guard skips the rating while
    the terminal closure still closes."""
    b = load(REF_GRAPH)
    del b.nodes['ZNBR2']['params']['cycling_thermal']
    HT.charge_window(b, INPUTS)
    assert b.computed == {}
    HT.dry_cooler(b, INPUTS)
    assert ('edge', 'IA-DC-REJ', 'rate') in b.computed                   # F-3 is not book-dependent
    assert ('node', 'DRY_COOLER', 'params.rated_kW') not in b.computed   # F-4 needs the book


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'heat' and prov.basis
    assert b.computed[('node', 'DRY_COOLER', 'params.rated_kW')][1].ref == 'A-M-455'
    assert b.computed[('edge', 'IA-DC-REJ', 'rate')][1].ref == 'A-M-454'
    assert b.computed[('edge', 'S53', 'rate')][1].ref == 'A-M-383'
    assert b.computed[('edge', 'HL-Q4-A-BUS', 'rate')][1].ref == 'A-M-453'
    assert b.computed[('edge', 'HL-Q1-A-DOWN', 'rate')][1].ref == 'A-M-259'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(HT))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
