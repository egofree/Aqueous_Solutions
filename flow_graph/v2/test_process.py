"""engine v2: the process-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/write_graph.py, command `process` (ledger
row `write_graph_process` - the flagship P2 family, the heart of the plant
solve). The committed graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (56 node fields, 67 edge fields), and a strict whole-model
  walk (nodes and edges, same JSON types) proves nothing else moved - the
  deferred X-ELS-02 load-basis block, the note-owned books, the product-edge
  topology and the bus seed stay byte-faithful;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact equality, zero enumerated drift);
- the key balances re-checked on grid integers: the BMED SEC energy, the
  evaporator mass closures, the vent-scrubber absorption book, the Faraday
  cell currents, the rectifier channel sum, the IA-BMED-04 brine closure and
  the SOL_ARK bus delta (zero at the golden);
- the bridge contracts: no driver payload records nothing; the IA-BAG-01
  note-owner guard keeps the fab_resist note and moves the value only; the
  goods-ship seed sits inside the A-M-491 band; the CAUSTICIZE branch of the
  caustic TF (deferred) records nothing;
- determinism: two runs, byte-identical;
- grid purity: no float literals and no I/O in the family module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import process as PR
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (unit, field path) the family writes.
EW = [f'EW_{n}' for n in range(1, 10)]
EXPECTED_FIELDS = [
    ('BMED_ACID', 'continuous_kw.value'), ('BMED_ACID', 'continuous_kw.note'),
    ('CRYO_O2', 'params.x_par_12_base.BMED_kW'), ('CRYO_O2', 'params.x_par_12_base.S17-BMED'),
    ('NAOH_PLANT', 'continuous_kw.value'), ('NAOH_PLANT', 'continuous_kw.note'),
    ('EVAP_ACID', 'notes'), ('EVAP_ACID', 'continuous_kw.value'), ('EVAP_ACID', 'continuous_kw.note'),
    ('EVAP_ACID', 'params.presence'), ('EVAP_ACID', 'params.water_off_kg_d'),
    ('EVAP_ACID', 'params.feed_wt'), ('EVAP_ACID', 'params.product_wt'),
    ('EVAP_ACID', 'params.mvr_kWh_per_t'),
    ('EVAP_BASE', 'notes'), ('EVAP_BASE', 'continuous_kw.value'), ('EVAP_BASE', 'continuous_kw.note'),
    ('EVAP_BASE', 'params.presence'), ('EVAP_BASE', 'params.water_off_kg_d'),
    ('EVAP_BASE', 'params.feed_wt'), ('EVAP_BASE', 'params.product_wt'),
    ('EVAP_BASE', 'params.mvr_kWh_per_t'),
    ('EVAP_ACID_VS', 'notes'), ('EVAP_ACID_VS', 'continuous_kw.value'),
    ('EVAP_ACID_VS', 'continuous_kw.note'), ('EVAP_ACID_VS', 'params.presence'),
    ('EVAP_ACID_VS', 'params.DN'), ('EVAP_ACID_VS', 'params.packed_mm'),
    ('EVAP_ACID_VS', 'params.height_mm'), ('EVAP_ACID_VS', 'params.sump_L'),
    ('EVAP_ACID_VS', 'params.material'), ('EVAP_ACID_VS', 'params.y_in_ppm_design'),
    ('EVAP_ACID_VS', 'params.y_out_ppm'), ('EVAP_ACID_VS', 'params.design_case'),
    ('EVAP_ACID_VS', 'params.size_mm'), ('EVAP_ACID_VS', 'params.size_note'),
    # only EW_1 carries a continuous_kw dict in the seed (the v1 isinstance
    # guard keeps the other eight at None); every cell re-books its sizing;
    # none carries cell_voltage_V
    ('EW_1', 'continuous_kw.value'), ('EW_1', 'continuous_kw.note'),
] + [(uid, 'params.sizing') for uid in EW] + [
    ('RECTIFIER', 'params.rated_A'), ('RECTIFIER', 'params.nameplate_kw_dc'),
    ('RECTIFIER', 'params.rect_ac_input_kW'), ('RECTIFIER', 'params.rect_loss_kW'),
    ('RECTIFIER', 'params.rect_basis'), ('RECTIFIER', 'notes'),
    ('RECTIFIER', 'continuous_kw.value'), ('RECTIFIER', 'continuous_kw.note'),
    ('PV_ARRAY', 'continuous_kw.value'),
]
EXPECTED_EDGES = [
    ('S17-BMED', 'rate'), ('IA-BASE-PPT', 'rate'), ('IA-BASE-01', 'rate'), ('IA-DIG-LIQ', 'rate'),
    ('IA-HALITE-MU', 'rate'), ('IA-NA-RECYCLE', 'rate'), ('IA-NAOH-CL2-SHIP', 'rate'),
    ('IA-NAOH-H2', 'rate'), ('IA-NAOH-H2O', 'rate'), ('IA-NAOH-RESIDUE', 'rate'),
    ('IA-NAOH-LIQ', 'rate'), ('IA-NA-PURGE', 'rate'), ('IA-NAOH-MU', 'rate'),
    ('SF-NAOH_PLANT', 'rate'),
    ('IA-EVAP_ACID-FEED', 'rate'), ('SF-EVAP_ACID', 'rate'), ('SQ-EVAP_ACID', 'rate'),
    ('IA-EVAP_BASE-FEED', 'rate'), ('IA-EVAP_BASE-COND', 'rate'), ('SF-EVAP_BASE', 'rate'),
    ('SQ-EVAP_BASE', 'rate'), ('IA-BMED-04', 'rate'),
    ('IA-EVAP_ACID-VENT', 'rate'), ('IA-VS-NAOH', 'rate'), ('IA-VS-SPENT', 'rate'),
    ('IA-VS-OFF', 'rate'), ('SF-EVAP_ACID_VS', 'rate'), ('SQ-EVAP_ACID_VS', 'rate'),
    ('IA-EVAP_ACID-COND', 'rate'),
] + [(f'IA-EW-MET-{n}', 'rate') for n in range(1, 10)] + [
    ('IA-EW-SHEET', 'rate'), ('S57', 'rate'), ('S58', 'rate'), ('S59', 'rate'), ('S60', 'rate'),
    ('IA-WIRE-LOSS', 'rate'), ('IA-DRAW-FUME', 'rate'),
    ('IA-BAG-01', 'rate'), ('IA-MET-AIR-MU', 'rate'), ('IA-MET-AIR-RET', 'rate'),
    ('IA-WEAR', 'rate'), ('IA-MFG-OUT', 'rate'), ('IA-FEED-MU', 'rate'), ('S16', 'rate.note'),
] + [(f'IA-DC-EW_{n}', 'rate') for n in range(1, 10)] + [
    ('S17', 'rate'), ('IA-RECT-Q4', 'rate'), ('IA-PV-01', 'rate'),
]
EXPECTED_EDGE_FIELDS = [
    ('IA-VS-NAOH', 'params.NaOH_mol_d'), ('IA-NAOH-LIQ', 'params.NaOH_kg_d'),
    ('IA-NAOH-LIQ', 'params.NaOH_wt'),
]


def run():
    b = load(REF_GRAPH)
    PR.process_acid_loop(b, INPUTS)
    PR.process_caustic_tf(b, INPUTS)
    PR.process_evaporators(b, INPUTS)
    PR.process_vent_scrubber(b, INPUTS)
    PR.process_ew_cascade(b, INPUTS)
    PR.process_rectifier(b, INPUTS)
    PR.process_bus_delta(b, INPUTS)
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


def test_core_balances_on_grid_integers():
    """The key balances re-checked as exact integer/Decimal books, independent
    of the stamping (BMED/EVAP kW arithmetic, vent absorption masses, Faraday
    currents, rectifier channels, brine closure, bus delta)."""
    s = PR._core(load(REF_GRAPH), INPUTS)
    # BMED: 96.46 kg/d NaOH x 6.7 kWh/kg / 24 h; the leach acid demand
    assert s['kw_bmed'].quantize(Decimal('0.0001')) == Decimal('26.9276')
    assert s['hcl_mol'].quantize(Decimal('0.001')) == Decimal('2411.612')
    assert s['v_design'].quantize(Decimal('0.01')) == Decimal('1.67')      # the pilot SEC governs (F-5)
    # evaporator mass closures: feed + make-up liquor = product + water off
    for key in ('ea', 'eb'):
        e = s[key]
        assert e['feed'] + e['added'] + e['added_water'] - e['product'] - e['water'] == 0
    assert s['ea']['feed'].quantize(Decimal('0.0001')) == Decimal('1304.7866')
    assert s['eb']['feed'].quantize(Decimal('0.0001')) == Decimal('1301.7164')
    # vent scrubber: bleed = 2 x HCl absorbed as 2 M base; spent = bleed + HCl;
    # offgas = vent - HCl (the 1 ppmv slip is below the 4th decimal)
    up = s['up']
    hcl_kg = up['naoh_mol_d'] / s['v']('vs_naoh_excess') * PR.MHCL / 1000
    assert (up['naoh_soln_kg_d'] - up['naoh_mol_d'] * Decimal(40) / 1000 / Decimal('0.0741')).copy_abs() < Decimal('1e-24')
    assert (up['spent_kg_d'] - up['naoh_soln_kg_d'] - hcl_kg).copy_abs() < Decimal('1e-24')
    assert (up['offgas_kg_d'] - (up['vent_kg_d'] - hcl_kg)).copy_abs() < Decimal('1e-6')
    assert up['vent_kg_d'].quantize(Decimal('0.0001')) == Decimal('0.0293')
    assert up['offgas_kg_d'].quantize(Decimal('0.0001')) == Decimal('0.0292')
    assert up['pump_kW'].quantize(Decimal('0.0001')) == Decimal('0.0238')
    # EW Faraday book: the Cu cell and the nine-channel DC sum
    ew3 = s['ew'][3]
    assert ew3['I'].quantize(Decimal('0.001')) == Decimal('679.323')
    assert ew3['P'].quantize(Decimal('0.0001')) == Decimal('1.4402')
    assert ew3['P_bus'].quantize(Decimal('0.000001')) == Decimal('1.643961')
    assert sum((s['ew'][n]['P_bus'] for n in range(1, 10)), Decimal(0)) == s['dc_total']
    assert s['rect']['P_ac'].quantize(Decimal('0.001')) == Decimal('7.491')
    assert (s['rect']['P_ac'] - s['rect']['P_dc']).quantize(Decimal('0.001')) == Decimal('1.498')
    # IA-BMED-04 brine closure: base feed + BMED-02 + scrub bleed - condensate
    bm04 = s['eb']['feed'] + s['R']['IA-BMED-02'] + s['up']['naoh_soln_kg_d'] - s['eb']['water']
    assert bm04.quantize(Decimal('0.0001')) == Decimal('490.7946')
    # bus delta: at the golden the acid-loop feeds already sit in IA-PV-01, so
    # the close moves nothing (delta zero, PV unchanged)
    b = run()
    out = json.loads(render(b))
    pv = next(e for e in out['edges'] if e['stream_id'] == 'IA-PV-01')
    assert pv['rate']['value'] == 370.8477
    assert ('edge', 'IA-GOODS-SHIP', 'rate') not in b.computed           # inside the A-M-491 band


def test_cell_books_and_rectifier_stamps():
    b = run()
    sz = {uid: b.computed[('node', uid, 'params.sizing')][0] for uid in EW}
    assert sz['EW_1'] == {'size_mm': [270, 720, 760], 'I_bounding_A': 0, 'cathodes': 1, 'anodes': 2,
                          'j_A_m2': 1, 'V_liq_m3': 0.117, 'P_dc_kW': 0.0, 'status': 'study',
                          'source': 'AQS-DUTY-051'}
    assert sz['EW_7']['cathodes'] == 12 and sz['EW_7']['size_mm'] == [1370, 720, 760]
    assert sz['EW_7']['j_A_m2'] == 200 and sz['EW_7']['V_liq_m3'] == 0.633
    assert sz['EW_3']['I_bounding_A'] == 679 and sz['EW_3']['j_A_m2'] == 193
    # the sub-watt cells: EW_1 keeps its kW stamp only because the seed carries
    # a dict there (the v1 guard); the others stay None
    assert b.computed[('node', 'EW_1', 'continuous_kw.value')][0] == 0.0007
    for uid in EW[1:]:
        assert ('node', uid, 'continuous_kw.value') not in b.computed
    rect = {p: b.computed[('node', 'RECTIFIER', 'params.' + p)][0]
            for p in ('rated_A', 'nameplate_kw_dc', 'rect_ac_input_kW', 'rect_loss_kW')}
    assert rect == {'rated_A': 4250, 'nameplate_kw_dc': 25.5, 'rect_ac_input_kW': 7.491,
                    'rect_loss_kW': 1.498}
    assert b.computed[('edge', 'IA-RECT-Q4', 'rate')][0]['value'] == 1.4982
    assert b.computed[('edge', 'IA-DC-EW_9', 'rate')][0]['value'] == 0.399462
    assert b.computed[('edge', 'IA-DC-EW_1', 'rate')][0]['value'] == 0.000746


def test_note_owner_and_value_only_books():
    """IA-BAG-01 keeps the fab_resist note and moves the value only; IA-FEED-MU
    keeps its first-creation note; S16 moves its note only."""
    b = run()
    assert b.edges['IA-BAG-01']['rate']['note'].startswith('X-RTE TF: fab photoresist')
    assert b.computed[('edge', 'IA-BAG-01', 'rate')][0]['value'] == 7.1783
    committed = json.load(open(REF_GRAPH))
    c_edges = {e['stream_id']: e for e in committed['edges']}
    assert b.computed[('edge', 'IA-FEED-MU', 'rate')][0]['value'] == 65.549411
    assert b.computed[('edge', 'IA-FEED-MU', 'rate')][0]['note'] == c_edges['IA-FEED-MU']['rate']['note']
    assert b.computed[('edge', 'S16', 'rate.note')][0] == c_edges['S16']['rate']['note']
    assert b.computed[('edge', 'S16', 'rate.note')][0].endswith('this line holds its band basis.')


def test_no_drivers_records_nothing():
    """The bridge solve / check carry no driver payload: the family records
    nothing and the seed stands (the specialty-family contract)."""
    b = load(REF_GRAPH)
    PR.process_acid_loop(b, {})
    PR.process_caustic_tf(b, {})
    PR.process_evaporators(b, {})
    PR.process_vent_scrubber(b, {})
    PR.process_ew_cascade(b, {})
    PR.process_rectifier(b, {})
    PR.process_bus_delta(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage == 'process' and prov.basis
    assert b.computed[('node', 'RECTIFIER', 'params.rect_basis')][1].ref == 'A-M-255'
    assert b.computed[('node', 'RECTIFIER', 'continuous_kw.note')][1].ref == 'A-M-231'
    assert b.computed[('node', 'EW_1', 'params.sizing')][1].basis.endswith('A-M-029, A-M-036..040)')


def test_caustic_route_guard():
    """A CAUSTICIZE driver (the deferred branch) records nothing rather than a
    wrong book; the committed design is CHLOR_ALKALI."""
    drv = json.loads(json.dumps(INPUTS['drivers']))
    drv['naoh_route']['value'] = 'CAUSTICIZE'
    b = load(REF_GRAPH)
    PR.process_caustic_tf(b, {'drivers': drv})
    assert ('node', 'NAOH_PLANT', 'continuous_kw.value') not in b.computed


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(PR))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
