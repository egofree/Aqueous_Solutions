"""engine v2: the geo_loop-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/geo_loop.py `--write` (ledger row
`sizing_geo_loop`, section B - AQS-DUTY-076 unit task 02 for GEO_GHEX, GEO_HP
and GEO_HP_CLOSED_LOOP). The committed graph carries every field the family
stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (17 GEO_GHEX design fields, 11 GEO_HP design fields + its
  size_note, 8 GEO_HP_CLOSED_LOOP design fields, no edge writes), and a strict
  whole-model walk (nodes and edges, same JSON types) proves nothing else
  moved - including that the GEO_GHEX / GEO_HP_CLOSED_LOOP size notes stay the
  specialty lane's (one writer per field);
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact repr equality, zero enumerated
  drift);
- the bore-field and loop chains re-derived on exact Decimal arithmetic (the
  module runs exact books throughout): the bore metres at the per-metre
  capacity, the even 5 m split, the loop flow at the glycol books, the
  velocity diameter against the DN ladder and the circulation pump at the
  site gravity;
- grid spot-checks: the 5 m bore-split grid, the DN-minus-8 clearance rule on
  the DN ladder, driver int books that stay JSON integers;
- the seed-read contract, recorded: S44 / SF-GEO_HP are the heat family's
  fields - the family reads the seed, never the overlay (a tampered overlay
  does not move the books; the seed rate does);
- the driver-tamper table: the per-metre capacity, the COP fallback chain on
  an issued lift, the plate-U driver and the loop head;
- the bridge contracts: no driver payload records nothing; drivers without
  the site profile record nothing (the pump needs the site gravity);
- determinism: two runs, byte-identical;
- purity: no float literals and no I/O in the family module.

Integer-scale table (half-even throughout, Python round()'s tie rule): COP
2 dp, plate areas 3 dp, bore metres required / header / circulation 1 dp,
flows and lifts 4 dp; bores, bore depth, installed metres, DN, spacing, dT,
head, modules and the driver int books (q_per_m_W, spacing, dT, head) integer.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import geo_loop as GL
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')))}
G = Decimal('9.80665')                                       # the baseline profile gravity (v1 SITE.g())
PI = Decimal('3141592653589793') / Decimal('10') ** 15

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [
    ('GEO_GHEX', 'params.design.Q_ceiling_kW_th'), ('GEO_GHEX', 'params.design.k_ground_W_mK'),
    ('GEO_GHEX', 'params.design.T_source_K'), ('GEO_GHEX', 'params.design.q_per_m_W'),
    ('GEO_GHEX', 'params.design.bore_metres_req'), ('GEO_GHEX', 'params.design.bores'),
    ('GEO_GHEX', 'params.design.bore_depth_m'), ('GEO_GHEX', 'params.design.bore_metres_installed'),
    ('GEO_GHEX', 'params.design.bore_spacing_m'), ('GEO_GHEX', 'params.design.header_m'),
    ('GEO_GHEX', 'params.design.loop_DN'), ('GEO_GHEX', 'params.design.loop_flow_kg_s'),
    ('GEO_GHEX', 'params.design.loop_dT_K'), ('GEO_GHEX', 'params.design.loop_fluid'),
    ('GEO_GHEX', 'params.design.circ_pump_W'), ('GEO_GHEX', 'params.design.status'),
    ('GEO_GHEX', 'params.design.material'),
    ('GEO_HP', 'params.design.lift_kW_th'), ('GEO_HP', 'params.design.electric_kW'),
    ('GEO_HP', 'params.design.cop'), ('GEO_HP', 'params.design.modules'),
    ('GEO_HP', 'params.design.redundancy'), ('GEO_HP', 'params.design.module_kW_th'),
    ('GEO_HP', 'params.design.source_area_m2'), ('GEO_HP', 'params.design.condenser_area_m2'),
    ('GEO_HP', 'params.design.hx_class'), ('GEO_HP', 'params.design.cop_basis'),
    ('GEO_HP', 'params.design.material'), ('GEO_HP', 'params.size_note'),
    ('GEO_HP_CLOSED_LOOP', 'params.design.design_case_kW_th'),
    ('GEO_HP_CLOSED_LOOP', 'params.design.flow_kg_s'), ('GEO_HP_CLOSED_LOOP', 'params.design.DN'),
    ('GEO_HP_CLOSED_LOOP', 'params.design.dT_K'), ('GEO_HP_CLOSED_LOOP', 'params.design.head_m'),
    ('GEO_HP_CLOSED_LOOP', 'params.design.pump_W'), ('GEO_HP_CLOSED_LOOP', 'params.design.duty'),
    ('GEO_HP_CLOSED_LOOP', 'params.design.material'),
]
EXPECTED_EDGES = []                                          # no rates change on the graph


def run(inputs=None):
    b = load(REF_GRAPH)
    GL.geo_loop(b, inputs if inputs is not None else INPUTS)
    return b


def committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    if isinstance(gold, dict):
        return isinstance(got, dict) and set(gold) == set(got) and all(_eq(v, got[k]) for k, v in gold.items())
    if isinstance(gold, list):
        return isinstance(got, list) and len(gold) == len(got) and all(_eq(a, x) for a, x in zip(gold, got))
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
            if any(type(a) is not type(x) or a != x for a, x in zip(c_obj[k], r_obj[k])):
                out.add(p)
        elif type(c_obj[k]) is not type(r_obj[k]) or c_obj[k] != r_obj[k]:
            out.add(p)


def test_exact_change_set_and_golden_equality():
    c = committed()
    c_nodes = {n['unit_id']: n for n in c['nodes']}
    c_edges = {e['stream_id']: e for e in c['edges']}
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    r_edges = {e['stream_id']: e for e in out['edges']}

    got_nodes = sorted((uid, path) for (kind, uid, path) in b.computed if kind == 'node')
    got_edges = sorted((sid, path) for (kind, sid, path) in b.computed if kind == 'edge')
    assert got_nodes == sorted(EXPECTED_FIELDS), (
        sorted(set(got_nodes) - set(EXPECTED_FIELDS)), sorted(set(EXPECTED_FIELDS) - set(got_nodes)))
    assert got_edges == []

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, diffs, expected_paths)
    assert diffs == set(), sorted(diffs)


def test_one_writer_per_field_size_notes():
    """The GEO_HP size note is this family's; the GEO_GHEX and
    GEO_HP_CLOSED_LOOP notes are the specialty lane's study boxes and are not
    stamped here (one writer per field; the committed seed already carries
    them)."""
    b = run()
    assert ('node', 'GEO_HP', 'params.size_note') in b.computed
    assert ('node', 'GEO_GHEX', 'params.size_note') not in b.computed
    assert ('node', 'GEO_HP_CLOSED_LOOP', 'params.size_note') not in b.computed
    assert b.computed[('node', 'GEO_HP', 'params.size_note')][0] == \
        'sized at the survey-locked design case, GEO loop sizing (flow_graph/param/geo_loop.py, AQS-DUTY-076)'
    assert ('node', 'GEO_HP', 'continuous_kw.value') not in b.computed          # the power family's X-ELS-02 book


def test_bore_and_loop_chain_on_exact_books():
    """The bore-field and loop chains re-derived as exact Decimal books,
    independent of the stamping: bore metres at the per-metre capacity, the
    even 5 m split, the loop flow, the velocity diameter against the DN ladder
    and the circulation pump at the site gravity."""
    bore_m, n_bore, depth = GL.bore_field(Decimal('3.0'), Decimal(35), Decimal(45))
    assert bore_m == Decimal('3000') / 35                        # 85.7142857142...
    assert bore_m.quantize(Decimal('0.1')) == Decimal('85.7')
    assert n_bore == 2 and depth == 45                           # ceil(85.71/45) = 2; even split at 5 m
    assert depth == int((bore_m / 2 / 5).to_integral_value(rounding='ROUND_CEILING')) * 5
    m_loop, q_loop, id_req, dn = GL.loop_books(Decimal('3.0'), Decimal('3.9'), Decimal(3),
                                               Decimal(1030), Decimal('1.0'))
    assert m_loop == Decimal('3000') / (Decimal('3.9') * 1000 * 3)      # 0.2564102564... kg/s
    assert m_loop.quantize(Decimal('0.0001')) == Decimal('0.2564')
    assert Decimal('17') < id_req <= Decimal('24')               # DN25 fails the -8 clearance, DN32 passes
    assert dn == 32
    pump = Decimal(1030) * G * q_loop * Decimal(25) / Decimal('0.5')
    assert pump.quantize(Decimal('0.1')) == Decimal('125.7')
    b = run()
    ghx = {p.split('.', 2)[2]: b.computed[('node', 'GEO_GHEX', p)][0]
           for p in ('params.design.bore_metres_req', 'params.design.bores', 'params.design.bore_depth_m',
                     'params.design.bore_metres_installed', 'params.design.header_m',
                     'params.design.loop_DN', 'params.design.loop_flow_kg_s', 'params.design.circ_pump_W',
                     'params.design.q_per_m_W', 'params.design.bore_spacing_m', 'params.design.loop_dT_K')}
    assert ghx['bore_metres_req'] == 85.7 and ghx['bores'] == 2 and ghx['bore_depth_m'] == 45
    assert ghx['bore_metres_installed'] == 90 and ghx['header_m'] == 6
    assert ghx['loop_DN'] == 32 and ghx['loop_flow_kg_s'] == 0.2564 and ghx['circ_pump_W'] == 125.7
    closed = {p.split('.', 2)[2]: b.computed[('node', 'GEO_HP_CLOSED_LOOP', p)][0]
              for p in ('params.design.pump_W', 'params.design.head_m', 'params.design.DN')}
    assert closed['pump_W'] == 125.7 and closed['head_m'] == 25 and closed['DN'] == 32


def test_grid_spot_checks_and_types():
    """Driver int books stay JSON integers through the blanket 4 dp store; the
    DN ladder and the bore-split grid hold; the texts are verbatim."""
    b = run()
    out = json.loads(render(b))
    by_id = {n['unit_id']: n for n in out['nodes']}
    ghx, hp, cl = (by_id[u]['params']['design'] for u in ('GEO_GHEX', 'GEO_HP', 'GEO_HP_CLOSED_LOOP'))
    assert type(ghx['q_per_m_W']) is int and ghx['q_per_m_W'] == 35
    assert type(ghx['bore_spacing_m']) is int and ghx['bore_spacing_m'] == 6
    assert type(ghx['loop_dT_K']) is int and type(cl['dT_K']) is int and ghx['loop_dT_K'] == cl['dT_K'] == 3
    assert type(cl['head_m']) is int and cl['head_m'] == 25
    assert type(ghx['bores']) is int and type(ghx['bore_depth_m']) is int
    assert ghx['bore_metres_installed'] == ghx['bores'] * ghx['bore_depth_m']
    assert type(ghx['loop_DN']) is int and type(hp['modules']) is int
    assert hp['modules'] == 2 and hp['redundancy'] == '2 x 100 % (X-RED-07)'
    assert ghx['loop_fluid'] == '25 % propylene glycol'
    assert hp['hx_class'] == 'brazed plate, U 2.0 kW/m2 K at 5 K approach (PERRY9)'
    assert hp['cop_basis'] == ('graph S44/SF-GEO_HP; study COP 3.43 at 285 K (AQS-HEAT-STUDY-002 sec. 6, '
                               'KAVANAUGH2014)')
    assert ghx['status'] == 'design_survey_locked (ST-ORC-01)'
    assert cl['duty'].startswith('source loop between the bore field')
    assert hp['lift_kW_th'] == 0.0 and hp['electric_kW'] == 0.0 and hp['cop'] == 3.2   # the idle-standby books
    assert hp['module_kW_th'] == 2.2 and hp['source_area_m2'] == 0.22 and hp['condenser_area_m2'] == 0.22


def test_seed_read_contract():
    """S44 / SF-GEO_HP are the heat family's fields, read from the seed and
    recorded: a tampered overlay does not move the books, the seed rate does."""
    b = load(REF_GRAPH)
    b.computed[('edge', 'S44', 'rate')] = (
        {'value': 5.0, 'unit': 'kW', 'status': 'study', 'note': 'a heat-family stamp from this same pass'},
        None)
    GL.geo_loop(b, INPUTS)
    assert b.computed[('node', 'GEO_HP', 'params.design.lift_kW_th')][0] == 0.0   # the seed book, not the overlay
    drv = json.loads(json.dumps(INPUTS['drivers']))
    b = load(REF_GRAPH)
    b.edges['S44']['rate']['value'] = 2.1952                     # the issued winter lift of the duty sheet
    GL.geo_loop(b, {'drivers': drv, 'site_profile': INPUTS['site_profile']})
    assert b.computed[('node', 'GEO_HP', 'params.design.lift_kW_th')][0] == 2.1952
    assert b.computed[('node', 'GEO_HP', 'params.design.electric_kW')][0] == 0.686   # lift / cop_design fallback
    assert b.computed[('node', 'GEO_HP', 'params.design.cop')][0] == 3.2
    assert b.computed[('node', 'GEO_HP', 'params.design.condenser_area_m2')][0] == 0.289  # (2.2 + 0.686)/10


def test_driver_tamper_table():
    """The drivers move the books through the registered function as the exact
    chain predicts: the per-metre capacity, the plate-U driver and the loop
    head; a bigger ceiling needs more bores, never a deeper single bore beyond
    the split grid."""
    def books(tamper):
        drv = json.loads(json.dumps(INPUTS['drivers']))
        for key, val in tamper.items():
            drv['GEO.geo-loop.' + key]['value'] = val
        bb = run({'drivers': drv, 'site_profile': INPUTS['site_profile']})
        ghx = {p: bb.computed[('node', 'GEO_GHEX', p)][0]
               for p in ('params.design.bore_metres_req', 'params.design.bores', 'params.design.bore_depth_m',
                         'params.design.bore_metres_installed', 'params.design.circ_pump_W',
                         'params.design.loop_DN')}
        hp = bb.computed[('node', 'GEO_HP', 'params.design.source_area_m2')][0]
        return ghx, hp
    base, base_hp = books({})
    assert base['params.design.bore_metres_req'] == 85.7 and base['params.design.bores'] == 2
    t, t_hp = books({'ghex_q_per_m_W': 70})                      # double capacity: half the metres
    assert t['params.design.bore_metres_req'] == 42.9 and t['params.design.bores'] == 2 \
        and t['params.design.bore_depth_m'] == 25
    assert t['params.design.bore_metres_installed'] == t['params.design.bores'] * t['params.design.bore_depth_m']
    t, t_hp = books({'bp_ux_U_kW_m2K': 4.0})                     # double plate U: half the areas
    assert t_hp == 0.11
    t, _ = books({'loop_head_m': 50})                            # double the head: double the pump power
    assert t['params.design.circ_pump_W'] == 251.5               # 2 x 125.726... on the exact book
    t, _ = books({'ghex_bore_depth_m': 60})                      # the split grid: 85.7 m still 2 x 45
    assert t['params.design.bores'] == 2 and t['params.design.bore_depth_m'] == 45
    t, _ = books({'ghex_q_per_m_W': 20})                         # 150 m required: 4 bores x 40 m
    assert t['params.design.bore_metres_req'] == 150.0 and t['params.design.bores'] == 4 \
        and t['params.design.bore_depth_m'] == 40
    assert t['params.design.bore_metres_installed'] == 160


def test_bridge_contracts():
    """No driver payload records nothing; drivers without the site profile
    record nothing (the pump arithmetic needs the site gravity)."""
    b = run({})
    assert b.computed == {}
    b = run({'drivers': INPUTS['drivers']})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'sizing_geo_loop' and prov.basis
        assert prov.ref == 'AQS-DUTY-076'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(GL))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
