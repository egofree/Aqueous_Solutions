"""engine v2: the relief/vent-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/write_graph.py, commands `relief` and
`vent` (ledger rows `write_graph_relief`, `write_graph_vent` - API 520 relief
cases on the pressurised nodes, the X-SAF-05 receiver fire cases, the API 2000
normal-vent books and the A-M-174 design pressures). The committed graph
carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (11 node fields, no edge fields), and a strict whole-model
  walk (nodes and edges, same JSON types) proves nothing else moved;
- golden equality: every changed field equals the committed golden, the
  relief_basis books compared key-by-key IN the committed key order (the v1
  rb.update order is the serialized contract), numbers quantised to the
  golden's decimals (exact equality, zero enumerated drift);
- the key arithmetic re-checked on exact Decimal books with hand-derived
  values: the API 520 flow factor C(k), the critical-flow orifice area and the
  equivalent bore, the API 521 receiver fire case on both branches (gas F'
  environmental factor and liquid CO2 with the 900 s depressuring book), the
  API 2000 out/in-breathing laws, the PERRY9 open-vent orifice, the vent dP
  cap (min of driver cap and 25 % of design, with the 2 kPa design fallback),
  the A-M-174 half-kPa design-pressure ceiling, and the A-M-182 hold-up head
  (pipe only, bed depth, store hold-up at the driver H/D);
- the relief -> vent pair book: the atmospheric mark replaces relief_basis in
  full (the v1 behaviour) and the vent command rebuilds the full book in the
  v1 update order; the vent command alone on the committed seed reproduces the
  golden book and its order;
- the liquid edge census: the pump terms move with the node's liquid kg/d
  book over the transfer window (synthetic receipt, hand-derived);
- the bridge contract: no driver payload records nothing;
- determinism: two runs, byte-identical;
- grid purity: no float literals and no I/O in the family module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import relief_vent as RV
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [
    ('CRYO_ASU', 'params.design_kPa'), ('CRYO_ASU', 'params.relief_basis'),
    ('CRYO_CO2', 'params.relief_basis'), ('CRYO_CO2', 'params.relief_mm'),
    ('CRYO_H2', 'params.relief_basis'), ('CRYO_H2', 'params.relief_mm'),
    ('CRYO_O2', 'params.relief_basis'), ('CRYO_O2', 'params.relief_mm'),
    ('EVAP_ACID', 'params.relief_basis'), ('EVAP_BASE', 'params.relief_basis'),
    ('H2O_ELYZ', 'params.relief_basis'),
]
EXPECTED_EDGES = []                                            # the family stamps no edge state


def run():
    b = load(REF_GRAPH)
    RV.relief_devices(b, INPUTS)
    RV.atm_venting(b, INPUTS)
    return b


def _num_eq(gold, got):
    return Decimal(str(gold)).normalize() == Decimal(str(got)).normalize()


def _eq(gold, got):
    """Golden equality; dict key ORDER is part of the contract (the v1
    rb.update order is what the committed graph serializes)."""
    if isinstance(gold, dict):
        return isinstance(got, dict) and list(gold) == list(got) \
            and all(_eq(v, got[k]) for k, v in gold.items())
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
    enumerated fields, where equality at the golden's decimals and key order
    holds. Provenance rows, added by the serializer on touched objects, are
    excluded."""
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
    assert got_edges == EXPECTED_EDGES, got_edges

    for uid, path in EXPECTED_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields
    expected_node_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths)
    assert diffs == set(), sorted(diffs)
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, set())
    assert edge_diffs == set(), sorted(edge_diffs)


def test_relief_sizing_arithmetic_on_exact_books():
    """API 520 Part I on exact books, hand-derived: the flow factor C(k), the
    critical-flow area and the equivalent bore."""
    # gas_C(k) = 520 sqrt(k (2/(k+1))^((k+1)/(k-1))) at 28 significant digits
    assert RV.gas_C(Decimal('1.4')).quantize(Decimal('0.000001')) == Decimal('356.060357')
    assert RV.gas_C(Decimal('1.3')).quantize(Decimal('0.000001')) == Decimal('346.976423')
    assert RV.gas_C(Decimal('1.29')).quantize(Decimal('0.000001')) == Decimal('346.033316')
    # A = W/(C Kd P1) sqrt(T Z / M): W 100 lb/h, k 1.4, P1 100 psia, T 530 R, M 29
    a = RV.gas_area_in2(Decimal(100), Decimal('1.4'), Decimal(100), Decimal(530), Decimal(1), Decimal(29))
    assert a.quantize(Decimal('0.000001')) == Decimal('0.012314')
    assert RV.equiv_bore_mm(a).quantize(Decimal('0.001')) == Decimal('3.180')          # mm
    assert RV.equiv_bore_mm(Decimal(1)).quantize(Decimal('0.001')) == Decimal('28.661')  # 1 in2 orifice
    # the golden API 520 books re-derive from their own case inputs: EVAP_ACID
    seed = {n['unit_id']: n for n in json.load(open(REF_GRAPH))['nodes']}
    acid = seed['EVAP_ACID']['params']['relief_basis']
    a_in2 = RV.gas_area_in2(RV.dec(acid['W_kg_h']) * RV.LB_PER_KG, RV.dec(acid['k']),
                            RV.dec(acid['P1_kPa_abs']) / RV.KPA_TO_PSI, RV.dec(acid['T_K']) * RV.R_F,
                            Decimal(1), RV.dec(acid['M_kg_kmol']))
    assert (a_in2 * RV.IN2_MM2).quantize(Decimal('0.01')) == Decimal('34.01')          # golden A_req_mm2
    assert RV.equiv_bore_mm(a_in2).quantize(Decimal('0.01')) == Decimal('6.58')        # golden bore_req_mm
    assert _num_eq(seed['EVAP_ACID']['params']['relief_mm'], 9.51)


def test_receiver_fire_cases():
    """X-SAF-05 API 521 on the receiver banks (A-M-188): the gas branch (F'
    environmental factor) and the liquid-CO2 branch (282 kJ/kg latent, 900 s
    depressuring), on the committed designs and a hand-built bank."""
    seed = {n['unit_id']: n for n in json.load(open(REF_GRAPH))['nodes']}
    fire_gold = {u: seed[u]['params']['relief_basis']['fire_case'] for u in ('CRYO_CO2', 'CRYO_H2', 'CRYO_O2')}
    for uid in ('CRYO_CO2', 'CRYO_H2', 'CRYO_O2'):
        p = seed[uid]['params']
        fire = RV.receiver_fire(p['design'], p['relief_basis'], RV.dec(p['design_kPa']))
        for k, gold in fire_gold[uid].items():
            got = fire[k]
            if isinstance(gold, (bool, str)) or isinstance(got, (bool, str)):
                assert gold == got, (uid, k, gold, got)        # liquid flag, valve count, method text
            else:
                want = RV.q(got, 3) if isinstance(got, Decimal) else got
                assert _num_eq(gold, want), (uid, k, gold, want)
    # CRYO_CO2 is the liquid branch: gas-filled above it, the depressuring mass is 0
    assert fire_gold['CRYO_CO2']['liquid'] is True and fire_gold['CRYO_CO2']['depress_kg'] == 0.0
    assert fire_gold['CRYO_H2']['liquid'] is False and fire_gold['CRYO_H2']['depress_kg'] == 9.121
    # hand-built half bank: 2 tubes x 114.3 mm x 6.096 m, H2 case, V 1 m3
    design = {'tubes': 2, 'OD_mm': 114.3, 'tube_m': 6.096, 'banks': [{'V_m3': 1.0}]}
    rb = {'M_kg_kmol': 2.016, 'k': 1.41, 'Z': 1.13, 'T_K': 313.15, 'P1_kPa_abs': 24301.3}
    fire = RV.receiver_fire(design, rb, Decimal(22000))
    assert fire['exposed_m2'].quantize(Decimal('0.0001')) == Decimal('4.3780')         # 2 pi 0.1143 6.096
    assert fire['per_half_m2'] == fire['exposed_m2'] / 2
    assert fire['P1_kPa_abs'] == Decimal('26721.325')                                  # 121 % x 22000 + 101.325
    assert fire['T1_K'].quantize(Decimal('0.001')) == Decimal('344.335')               # Tn P1 / P1_normal
    assert fire['A_req_mm2_per_half'].quantize(Decimal('0.001')) == Decimal('7.254')
    assert fire['bore_req_mm_per_half'].quantize(Decimal('0.001')) == Decimal('3.039')
    assert fire['depress_kg'].quantize(Decimal('0.001')) == Decimal('7.538')           # 900 s to 50 % design
    assert fire['depress_bore_mm'].quantize(Decimal('0.001')) == Decimal('1.319')
    assert fire['liquid'] is False and fire['valves'] == 2
    # the whole-mm relief_mm ceiling: governing of the blocked-outlet bore and the fire bore per half
    for uid, mm in (('CRYO_CO2', 9.0), ('CRYO_H2', 13.0), ('CRYO_O2', 9.0)):
        b = run()
        assert b.computed[('node', uid, 'params.relief_mm')][0] == mm
        p = seed[uid]['params']
        fire = RV.receiver_fire(p['design'], p['relief_basis'], RV.dec(p['design_kPa']))
        governing = max(RV.dec(p['relief_basis']['bore_req_mm']), fire['bore_req_mm_per_half'])
        assert RV.qceil(governing) == int(mm)                                          # e.g. ceil(8.818) -> 9


def test_venting_arithmetic_on_exact_books():
    """API 2000 breathing, the PERRY9 open-vent orifice, the dP cap and the
    A-M-174 design pressure, hand-derived; then the CRYO_ASU golden book."""
    assert RV.out_breathing(Decimal(10), Decimal(5), Decimal('0.32')).quantize(Decimal('0.0001')) \
        == Decimal('12.5419')                                  # 2 V_pf + Y V^0.9
    assert RV.in_breathing(Decimal(10), Decimal(3), Decimal('6.5')).quantize(Decimal('0.0001')) \
        == Decimal('35.5772')                                  # V_pe + C V^0.7
    assert RV.open_vent_bore(Decimal(100), Decimal(500)).quantize(Decimal('0.001')) == Decimal('45.660')
    # the dP cap: min(driver 500 Pa, 25 % of design), with the 2 kPa design fallback
    assert RV.VENT_DP_FRAC * RV.DESIGN_DEFAULT_KPA * RV.PA_PER_KPA == Decimal('500.00')
    assert min(RV.dec(INPUTS['drivers']['vent_dP_Pa']['value']),
               RV.VENT_DP_FRAC * Decimal('0.4') * RV.PA_PER_KPA) == Decimal('100.000')
    # the half-kPa ceiling: dp 250 Pa -> vapour 1.0 kPa; hydrostatic 1.25 x 9.80665 x 2.0 m = 24.5166250 kPa
    p_vap = RV.VENT_DP_MULT * Decimal(250) / RV.PA_PER_KPA
    p_liq = Decimal('1.25') * RV.G_SITE * Decimal(2)
    assert p_vap == Decimal('1.0') and p_liq == Decimal('24.5166250')
    assert RV.qceil((p_vap + p_liq) * 2) / 2 == 26.0
    # the golden book: envelope 2460 x 592 x 2000 mm = 2.91264 m3 (the book keeps 2.913),
    # no liquid edges, in-breathing governs the 16.9 mm bore, DN 25, design 18.0 kPa g
    v_gold = Decimal(2460) * Decimal(592) * Decimal(2000) / Decimal(10) ** 9
    assert v_gold == Decimal('2.91264')
    b = run()
    book = b.computed[('node', 'CRYO_ASU', 'params.relief_basis')][0]
    assert book['V_tk_m3'] == 2.913
    assert book['pump_in_m3_h'] == 0.0 and book['pump_out_m3_h'] == 0.0
    assert book['out_breathing_Nm3_h'] == 0.838
    assert book['in_breathing_Nm3_h'] == 13.738
    out_exact = RV.out_breathing(v_gold, Decimal(0), Decimal('0.32'))
    in_exact = RV.in_breathing(v_gold, Decimal(0), Decimal('6.5'))
    assert out_exact.quantize(Decimal('0.001')) == Decimal('0.838')
    assert in_exact.quantize(Decimal('0.001')) == Decimal('13.738')
    assert book['vent_dP_Pa'] == 500 and book['vent_bore_req_mm'] == 16.9 and book['vent_DN'] == 25
    assert RV.open_vent_bore(max(out_exact, in_exact), Decimal(500)).quantize(Decimal('0.1')) == Decimal('16.9')
    assert book['thermal_term'] == 'envelope volume'
    assert book['design_case'] == ('vapour 2.0 kPa (4 x vent dP) + hydrostatic 15.5 kPa '
                                   '(1.27 m full at SG 1.25) = 18.0 kPa g (A-M-174)')
    assert b.computed[('node', 'CRYO_ASU', 'params.design_kPa')][0] == 18.0
    # DN ladder: the smallest step at or above the bore, 25 minimum
    assert next(d for d in RV.DNS if d >= RV.open_vent_bore(Decimal(100), Decimal(500))) == 50
    assert next(d for d in RV.DNS if d >= RV.open_vent_bore(Decimal(1), Decimal(500))) == 25


def test_holdup_head_derivation():
    """A-M-182: the head where the unit has no sized height, as data rows."""
    drv = INPUTS['drivers']
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'header', 'HDR_X', drv)
    assert h == 0 and hold == 'pipe only, no standing liquid'
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'farm', 'GROW_BED', drv)
    assert h == Decimal('0.3') and hold == 'bed or fixture depth 0.3 m'
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'hab', 'HAB_EAST', drv)
    assert h == Decimal('0.3') and hold == 'bed or fixture depth 0.3 m'
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'misc', 'HAB_WEST', drv)
    assert hold == 'bed or fixture depth 0.3 m'                # the HAB_ prefix rule
    # store hold-up: 2.4 m3/h x 1 h x 2 d = 4.8 m3 at H/D 1.5 -> H = 1.5 (4 V / pi H/D)^(1/3)
    v_hold = Decimal('2.4') * Decimal(1) * Decimal(2)
    assert v_hold == Decimal('4.8')
    d_equiv = (Decimal(4) * v_hold / (RV.PI * Decimal('1.5'))) ** (Decimal(1) / Decimal(3))
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'tank', 'TANK_X', drv)
    assert h == Decimal('1.5') * d_equiv
    assert hold == 'store hold-up 2 d = 4.800 m3, H/D 1.5'
    # the process class: 1 d hold
    h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'evaporator', 'EVAP_X', drv)
    assert hold == 'process hold-up 1 d = 2.400 m3, H/D 1.5'
    d_proc = (Decimal(4) * Decimal('2.4') / (RV.PI * Decimal('1.5'))) ** (Decimal(1) / Decimal(3))
    assert h == Decimal('1.5') * d_proc
    # named tanks take the store class by id
    _h, hold = RV.holdup_head_m(Decimal('2.4'), Decimal(1), 'misc', 'ROOF_TANK', drv)
    assert hold.startswith('store hold-up')


def test_vent_census_and_no_volume_branch():
    """The pump terms move with the node's liquid kg/d book over the transfer
    window; a node with no sized volume takes the pump-terms-only book."""
    b = load(REF_GRAPH)
    b.data['edges'].append({'stream_id': 'SYN-LIQ', 'from_unit_id': 'ANY', 'to_unit_id': 'CRYO_ASU',
                            'presence': 'present', 'phase': 'L',
                            'rate': {'value': 2400, 'unit': 'kg/d'}})
    RV.atm_venting(b, INPUTS)
    book = b.computed[('node', 'CRYO_ASU', 'params.relief_basis')][0]
    th = RV.dec(INPUTS['drivers']['vent_transfer_h']['value'])
    assert book['pump_in_m3_h'] == RV.q(Decimal(2400) / 1000 / th, 4) == 2.4
    assert book['out_breathing_Nm3_h'] == RV.q(RV.out_breathing(Decimal('2.91264'), Decimal('2.4'),
                                                                Decimal('0.32')), 3) == 5.638
    assert book['in_breathing_Nm3_h'] == 13.738                # the thermal term still governs the bore
    assert book['vent_bore_req_mm'] == 16.9
    # a synthetic node with no size and no design: the 2 kPa fallback, the no-H design case
    b2 = load(REF_GRAPH)
    syn = {'unit_id': 'SYN_TANK', 'class': 'misc', 'params': {'relief_basis': {'case': 'atmospheric'}}}
    b2.data['nodes'].append(syn)
    b2.nodes['SYN_TANK'] = syn                                 # the builder's node index, for _set
    RV.atm_venting(b2, INPUTS)
    book2 = b2.computed[('node', 'SYN_TANK', 'params.relief_basis')][0]
    assert book2['V_tk_m3'] == 0.0 and book2['thermal_term'] == 'no sized volume: pump terms only'
    assert book2['vent_dP_Pa'] == 500                          # 25 % of the 2 kPa fallback = the cap
    assert book2['vent_bore_req_mm'] == 0.0 and book2['vent_DN'] == 25   # DN 25 minimum
    assert book2['design_case'] == ('vapour 2.0 kPa (4 x vent dP) = 2.0 kPa g; '
                                    'no liquid inflow, no hydrostatic case (A-M-174)')
    assert b2.computed[('node', 'SYN_TANK', 'params.design_kPa')][0] == 2.0


def test_relief_mark_then_vent_book():
    """The relief -> vent pair: the atmospheric mark replaces relief_basis in
    full (v1), and vent rebuilds the committed book in the v1 update order;
    vent alone on the committed seed reproduces the golden book too."""
    b = load(REF_GRAPH)
    RV.relief_devices(b, INPUTS)
    mark = b.computed[('node', 'CRYO_ASU', 'params.relief_basis')][0]
    assert list(mark) == ['case', 'method', 'relief_mm_status']
    assert mark['case'] == 'atmospheric'
    assert mark['method'] == 'not an API 520 case; tank venting per API Std 2000 at unit task 07'
    assert mark['relief_mm_status'] == 'atmospheric; design pressure set by the vent stage (A-M-174)'
    RV.atm_venting(b, INPUTS)
    golden = _dig({n['unit_id']: n for n in json.load(open(REF_GRAPH))['nodes']},
                  'CRYO_ASU.params.relief_basis')
    assert _eq(golden, b.computed[('node', 'CRYO_ASU', 'params.relief_basis')][0])
    # vent alone on the seed: the book and its key order reproduce
    b2 = load(REF_GRAPH)
    RV.atm_venting(b2, INPUTS)
    assert _eq(golden, b2.computed[('node', 'CRYO_ASU', 'params.relief_basis')][0])
    # the mark wipes nothing else: no other node carries an atmospheric case
    assert sorted(uid for uid, n in b.nodes.items()
                  if (n.get('params') or {}).get('relief_basis', {}).get('case') == 'atmospheric'
                  and (n.get('params') or {}).get('relief_mm') is not None) == ['CRYO_ASU']


def test_no_drivers_records_nothing():
    """The bridge solve / check carry no driver payload: the family records
    nothing and the seed stands."""
    b = load(REF_GRAPH)
    RV.relief_devices(b, {})
    RV.atm_venting(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (kind, uid, path), (value, prov) in b.computed.items():
        assert prov.stage in ('relief', 'vent') and prov.basis
    for uid in ('EVAP_ACID', 'EVAP_BASE', 'H2O_ELYZ'):
        row = b.computed[('node', uid, 'params.relief_basis')][1]
        assert row.stage == 'relief' and row.ref == 'API520'
    for uid in ('CRYO_CO2', 'CRYO_H2', 'CRYO_O2'):
        row = b.computed[('node', uid, 'params.relief_basis')][1]
        assert row.stage == 'relief' and row.ref == 'A-M-188'
        assert b.computed[('node', uid, 'params.relief_mm')][1].ref == 'A-M-188'
    assert b.computed[('node', 'CRYO_ASU', 'params.relief_basis')][1].ref == 'A-M-155'
    assert b.computed[('node', 'CRYO_ASU', 'params.design_kPa')][1].ref == 'A-M-174'


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(RV))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
