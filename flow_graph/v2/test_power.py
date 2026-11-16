"""engine v2: the power-family acceptance (the golden-value proof).

Reference writers: flow_graph/param/write_graph.py command `power` (ledger row
`write_graph_power` - the peak of the writer lattice) and
docs-authority/_power_sizing.py (the AQS-ELEC-007 demand census, the PV/generic
portfolio dispatch, the roof close over the bay-grid range, the ZNBR2 store
book, the critical-list books), plus the locale designed-source sizers of
flow_graph/param/site_units.py (ledger row `doc_site_units`, sizing half).
The committed graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (33 node fields, 3 edge rates), and a strict whole-model walk
  (nodes and edges, same JSON types) proves nothing else moved;
- golden equality: every changed field equals the committed golden, numbers
  quantised to the golden's decimals (exact equality) - with ONE enumerated
  deviation, the ZNBR2 store-book vehicle (params.cycling_thermal): the
  committed dict embeds the v1 heat-lane census (the F-20261110-08 grease
  override plus mid-pass demand books, 2658.8 kWh/d out); the v2 single census
  books 2679.0 kWh/d out. The deviation table pins both books and the exact
  arithmetic between them; in composition (power before heat) the heat family
  re-stamps the dict from its read and the committed block is restored
  byte-faithfully;
- the roof close as a pure derivation: same inputs -> the same fit twice; the
  fit is exact on the grid (whole bays, W/D on the 6000 mm bay grid, the need
  a whole kWp, have >= need); the aspect tie is the integer cross-product
  identical to v1's |nx/ny - 4/3| rule; the air/ground/best modes;
- the mars designed-source dispatch: the FSP_40K/MMRTG books equal the
  committed AQS-SITE-013 register rows; a tampered dust fraction moves the
  counts by the ceil rule through a data table; no locale name anywhere in
  the module (AST scan);
- the BACKUP_GEN exercise-average pin: the Q-040 rating (125 % of the live
  critical list, commercial 5 kW step) and the NFPA 110 8.4.2 exercise
  average (X-PAR-12), re-derived as exact books;
- the grease route books (A-M-480 SKF relubrication, F-20261110-08
  arithmetic): the census reads the seed's commercial-class stamps (the
  regime the committed golden embeds) while the registered route re-solve
  reproduces the heat lane's duty;
- the mvs.electrical book: the pure derivation equals the committed block
  (the overlay has no graph-level lane yet - builder work, stated);
- the composition order: power registers BEFORE heat (process -> power ->
  heat); with the heat family as landed the composition is byte-faithful
  (heat re-stamps its dict from the seed book), and the fresh read-back is
  the dry_cooler overlay-first idiom away;
- the bridge contracts: no payloads record nothing; drivers-only records
  nothing (the dispatch needs the site profile); the IA-PV-01 extension
  delta and note guard; the generic (non-PV-primary) dispatch;
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O, no locale conditionals.

Integer-scale table (the quantise at each stamp; half-even throughout,
Python round()'s tie rule): kW books 4 dp (EXT_HALL/IA-PV-01/SF-EXT_HALL,
GEO_HP/SF-GEO_HP, ZNBR2 and BACKUP_GEN continuous_kw); demand and target and
store books 2 dp (mvs need/target, the census P, the store kWh); store-book
daily energies 1 dp (cycling_thermal kWh books), its rates 2 dp; hvac and
roof-load books 3 dp; roof capacity 1 dp; interconnection peak 1 dp and
clear-day energy 0 dp; generic nameplate 1 dp; every count, nameplate,
module count, bay and footprint-mm an integer (math.ceil on the exact book).
"""
import ast
import copy
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import heat as HT
from flow_graph.v2.functions import power as PW
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
DRIVERS_PAYLOAD = json.load(open(DRIVERS))
INPUTS = {'drivers': DRIVERS_PAYLOAD,
          'site_profile': json.load(open(os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')))}
MARS_PROFILE = json.load(open(os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'mars.json')))

# The change-set specification: every (unit, field path) the family writes.
EXPECTED_FIELDS = [
    ('BACKUP_GEN', 'params.rated_kW'), ('BACKUP_GEN', 'params.rated_kW_basis'),
    ('BACKUP_GEN', 'continuous_kw.value'), ('BACKUP_GEN', 'continuous_kw.note'),
    ('EXT_HALL', 'continuous_kw.value'), ('EXT_HALL', 'continuous_kw.note'),
    ('EXT_HALL', 'params.hvac'), ('EXT_HALL', 'params.footprint_m2'),
    ('EXT_HALL', 'params.conditioned'), ('EXT_HALL', 'params.blocks'), ('EXT_HALL', 'params.duty'),
    ('PV_ARRAY', 'params.nameplate_kw'), ('PV_ARRAY', 'params.count'), ('PV_ARRAY', 'params.area_m2'),
    ('PV_ARRAY', 'params.mounting'), ('PV_ARRAY', 'params.roof'), ('PV_ARRAY', 'params.oversize_factor'),
    ('PV_ARRAY', 'params.balance_kWp'),
    ('SOL_ARK_60K', 'params.count'), ('SOL_ARK_60K', 'params.kW'), ('SOL_ARK_60K', 'params.dc_ac_ratio'),
    ('SOL_ARK_60K', 'params.interconnection'),
    ('ZNBR2', 'params.kW'), ('ZNBR2', 'params.kWh'), ('ZNBR2', 'params.charge_kW'),
    ('ZNBR2', 'params.discharge_kW'), ('ZNBR2', 'params.charge_basis'), ('ZNBR2', 'params.distribution'),
    ('ZNBR2', 'continuous_kw.value'), ('ZNBR2', 'continuous_kw.note'),
    ('ZNBR2', 'params.cycling_thermal'),
    ('GEO_HP', 'continuous_kw.value'), ('GEO_HP', 'continuous_kw.note'),
]
EXPECTED_EDGES = [
    ('SF-EXT_HALL', 'rate'), ('SF-GEO_HP', 'rate'), ('IA-PV-01', 'rate'),
]
# The one enumerated deviation (see module docstring): the store-book vehicle
# is re-based from the v1 heat-lane census to this family's single census.
DEVIATED_FIELDS = [('ZNBR2', 'params.cycling_thermal')]


def run():
    b = load(REF_GRAPH)
    PW.backup_criticals(b, INPUTS)
    PW.grease_route(b, INPUTS)
    PW.power_ledger(b, INPUTS)
    PW.pv_dispatch(b, INPUTS)
    PW.znbr2_store_book(b, INPUTS)
    PW.designed_sources(b, INPUTS)
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
    assert got_edges == sorted(EXPECTED_EDGES), (
        sorted(set(got_edges) - set(EXPECTED_EDGES)), sorted(set(EXPECTED_EDGES) - set(got_edges)))

    for uid, path in EXPECTED_FIELDS:
        if (uid, path) in DEVIATED_FIELDS:
            continue                                            # pinned by the deviation test below
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in EXPECTED_EDGES:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields (the store-book vehicle included, where the
    # walk accepts the deviation the next test pins exactly)
    expected_node_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths)
    # the store-book vehicle is the one enumerated deviation (pinned exactly
    # by test_store_book_deviation_table): its walk diff is the deviation
    assert diffs == {uid + '.' + path for uid, path in DEVIATED_FIELDS}, sorted(diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGES}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths)
    assert edge_diffs == set(), sorted(edge_diffs)
    # the graph-level mvs block is untouched by the overlay (no graph-level
    # lane yet; the derivation is pinned to the golden by test_mvs_book_golden)
    assert out['mvs']['electrical'] == committed['mvs']['electrical']


def test_store_book_deviation_table():
    """The ONE enumerated deviation, pinned exactly: the committed cycling
    book embeds the v1 heat-lane census (the F-20261110-08 grease-route
    override and the mid-pass demand books the sizing stampers re-stamped
    after it); the v2 single census books the store at this family's P. The
    window arithmetic itself is unchanged - every window book moves by the
    same census ratio, which the exact table shows."""
    b = load(REF_GRAPH)
    PW.znbr2_store_book(b, INPUTS)
    fresh = b.computed[('node', 'ZNBR2', 'params.cycling_thermal')][0]
    # the golden books at this family's census (P 191.3592 kW x night 14 h,
    # in at round trip 0.7)
    p = PW.dec('191.3592')
    store = p * 14
    store_in = store / PW.dec('0.7')
    assert PW.q(store, 2) == 2679.03 and PW.q(store_in, 2) == 3827.18
    assert fresh['kwh_d_out'] == 2679.0 and fresh['kwh_d_in'] == 3827.2
    assert fresh['loss_kwh_d'] == 1148.2 and fresh['avg_kW'] == 47.84
    assert fresh['window_h'] == 10.0 and fresh['window_kW'] == 114.82
    assert fresh['charge_kW_window'] == 382.72 and fresh['round_trip'] == 0.7
    # the committed book (the v1 heat-lane census, kept byte-identical until
    # the heat family reads the fresh store)
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = json.load(f)['nodes']
    gold = {n['unit_id']: n for n in committed}['ZNBR2']['params']['cycling_thermal']
    assert gold['kwh_d_out'] == 2658.8 and gold['kwh_d_in'] == 3798.3
    assert gold['avg_kW'] == 47.48 and gold['window_kW'] == 113.95
    # the census gap, exactly: the two lanes' P differ by 1.4449 kW (2658.8/14
    # against 191.3592); every book moves by the same 24 h/window scale
    p_heat = Decimal('2658.8') / 14
    assert (p - p_heat).quantize(Decimal('0.0001')) == Decimal('1.4449')
    assert (Decimal('2679.0') - Decimal('2658.8')) == Decimal('20.2')
    assert (PW.dec(fresh['avg_kW']) - Decimal('47.48')) == Decimal('0.36')
    assert (PW.dec(fresh['window_kW']) - Decimal('113.95')) == Decimal('0.87')
    # the ZNBR2 books the power writer owns reproduce the golden exactly - they
    # were always booked at the power census
    r_nodes = {n['unit_id']: n for n in json.loads(render(b))['nodes']}
    g_nodes = {n['unit_id']: n for n in committed}
    for path in ('params.kW', 'params.kWh', 'params.charge_kW', 'params.discharge_kW',
                 'continuous_kw.value', 'params.distribution'):
        assert _eq(_dig(r_nodes['ZNBR2'], path), _dig(g_nodes['ZNBR2'], path)), path


def test_roof_close_is_a_deterministic_pure_derivation():
    """Same inputs -> the same fit twice; the fit is exact on the grid."""
    drv = DRIVERS_PAYLOAD
    f1 = PW._roof_close(drv, Decimal('103.34'), PW.D1)
    f2 = PW._roof_close(drv, Decimal('103.34'), PW.D1)
    assert f1 == f2                                          # no convergence loop to wobble
    assert f1['bays_x'] == 31 and f1['bays_y'] == 23
    bay = PW.dec(drv['bay_mm']['value'])
    assert f1['W_mm'] == bay * 31 and f1['D_mm'] == bay * 23  # exactly on the 6000 mm bay grid
    assert f1['pv_need_kWp'] == 2653 and isinstance(f1['pv_need_kWp'], int)   # the whole-kWp need
    assert f1['pv_roof_kWp'] >= f1['pv_need_kWp']            # the fit carries the need
    assert f1['footprint_m2'] == Decimal('25668')
    assert f1['added_m2'] == Decimal('25236')                # base plate 4x3 = 432 m2 held
    assert f1['layout']['arrays'] == 12 and f1['layout']['perimeter_mm'] == PW.dec(1829)
    # the committed roof block is this fit
    with open(REF_GRAPH, encoding='utf-8') as f:
        roof = {n['unit_id']: n for n in json.load(f)['nodes']}['PV_ARRAY']['params']['roof']
    assert roof['bays'] == [f1['bays_x'], f1['bays_y']]
    assert roof['footprint_mm'] == [int(f1['W_mm']), int(f1['D_mm'])]
    assert _num_eq(roof['roof_capacity_kWp'], PW.q(f1['pv_roof_kWp'], 1))
    # the aspect tie: the integer cross-product is v1's |nx/ny - 4/3| rule
    # (|3nx-4ny|/ny < |3bx-4by|/by  <=>  |3nx-4ny|*by < |3bx-4by|*ny)
    pairs = [(31, 23, 33, 22), (31, 23, 30, 24), (16, 12, 13, 10), (12, 9, 8, 6)]
    for nx, ny, bx, by in pairs:
        lhs_float = abs(PW.dec(nx) / PW.dec(ny) - PW.dec(4) / PW.dec(3)) < \
            abs(PW.dec(bx) / PW.dec(by) - PW.dec(4) / PW.dec(3))
        lhs_int = abs(3 * nx - 4 * ny) * by < abs(3 * bx - 4 * by) * ny
        assert lhs_float == lhs_int, (nx, ny, bx, by)
    # best mode: the smaller converged footprint wins, with the comparison
    drv_best = copy.deepcopy(drv)
    drv_best['ext_hvac']['value'] = 'best'
    b = load(REF_GRAPH)
    s = PW._chain(b, {'drivers': drv_best, 'site_profile': INPUTS['site_profile']})
    fit = s['roof']
    assert fit['hvac'] == 'ground' and fit['bays_x'] == 31 and fit['bays_y'] == 22
    assert fit['footprint_m2'] < fit['compare']['air']['footprint_m2']
    assert set(fit['compare']) == {'air', 'ground'}
    assert fit['compare']['air']['bays'] == [31, 23] and fit['compare']['air']['pv_kWp'] == 2653


def _tree_of(mod):
    import inspect
    return ast.parse(inspect.getsource(mod))


tree_of_power = lambda: _tree_of(PW)


def test_mars_designed_source_dispatch():
    """The designed-source dispatch is field-driven off the profile's
    portfolio and dust-stretch design record: the books equal the committed
    AQS-SITE-013 register rows for the mars locale; a tampered dust fraction
    moves the counts by the ceil rule; no locale name exists in the module."""
    b = load(REF_GRAPH)
    PW.designed_sources(b, {'drivers': DRIVERS_PAYLOAD, 'site_profile': MARS_PROFILE})
    fsp = b.computed[('node', 'FSP_40K', 'params.site_placement')][0]
    mm = b.computed[('node', 'MMRTG', 'params.site_placement')][0]
    # the committed register rows (docs-authority/SITE_UNITS.md, table 1):
    # "count duty 3; count installed n plus 1 4; installed kW e 160; dust deficit kW 91.99"
    assert fsp['site'] == 'mars' and fsp['replaces'] == []
    assert fsp['register'] == 'AQS-SITE-013 (SITE_UNITS.md)'
    sz = fsp['sizing']
    assert sz['demand_kW'] == 103.34                          # need 191.36 less the EXT_HALL roof extension
    assert sz['dust_deficit_kW'] == 91.99 and sz['pv_dust_output_kW'] == 11.35
    assert sz['count_duty'] == 3 and sz['count_installed_n_plus_1'] == 4
    assert sz['installed_kW_e'] == 160.0 and sz['unit_kW_e'] == 40.0
    assert sz['pv_share'] == 0.35 and sz['dust_pv_output_frac'] == 0.3
    # "count 19; carries W e 2090"
    assert mm['sizing']['count'] == 19 and mm['sizing']['carries_W_e'] == 2090.0
    assert mm['sizing']['controls_trickle_kW'] == 2.0 and mm['sizing']['unit_W_e'] == 110.0
    assert mm['sizing']['critical_list_kW'] == 14.58
    # the ceil rule through a tamper table: duty = ceil(deficit / 40 kW_e),
    # installed = duty + 1 spare; the deficit book is the rounded EXACT
    # deficit (v1 site_units rounds the book, it does not re-close the rounded
    # books); no count is hard-coded
    demand = PW.dec('191.36') - PW.dec('88.0192')
    eta = PW.dec('0.7')
    h = PW.dec(MARS_PROFILE['groups']['solar']['entries']['night_hours']['value'])   # 12.33 h, the profile stretch
    phi = PW.dec('0.65') * PW.D1 + PW.dec('0.35') * PW.dec('0.3')
    g = ((PW.DAY - h) + h / eta) / (PW.DAY - phi * h + phi * h / eta) * demand
    for frac, duty, installed in ((0.0, 3, 4), (0.3, 3, 4), (0.6, 3, 4), (0.9, 2, 3)):
        prof = copy.deepcopy(MARS_PROFILE)
        prof['groups']['power_portfolio']['entries']['dust_stretch_design']['value']['pv_stretch_output_frac'] = frac
        bb = load(REF_GRAPH)
        PW.designed_sources(bb, {'drivers': DRIVERS_PAYLOAD, 'site_profile': prof})
        book = bb.computed[('node', 'FSP_40K', 'params.site_placement')][0]['sizing']
        pv_dust = PW.dec(frac) * PW.dec('0.35') * g
        deficit = demand - pv_dust
        assert book['pv_dust_output_kW'] == PW.q(pv_dust, 2), (frac, book)
        assert book['dust_deficit_kW'] == PW.q(deficit, 2), (frac, book)
        assert book['count_duty'] == duty == PW.ceil(deficit / PW.dec('40')), (frac, book)
        assert book['count_installed_n_plus_1'] == installed == duty + 1, (frac, book)
    # the baseline profile names no designed sources: the reference seed
    # records nothing (the placeholders stay placeholder)
    b0 = load(REF_GRAPH)
    PW.designed_sources(b0, INPUTS)
    assert not [k for k in b0.computed if k[0] == 'node' and k[1] in ('FSP_40K', 'MMRTG')]
    # no locale name anywhere in the module: the dispatch reads prof['site_id']
    # and the profile's dust record; no string constant in the module names a
    # locale (a docstring mention is prose, a locale CONDITIONAL would be an
    # exact constant)
    consts = [n.value for n in ast.walk(tree_of_power())
              if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert not [c for c in consts if c in ('mars', 'baseline', 'leo', 'antarctic', 'cocoa_fl',
                                           'death_valley', 'floating_island', 'lake_boehmer')]


def test_backup_gen_exercise_pin():
    """The Q-040 rating and the X-PAR-12 exercise average, re-derived as exact
    books (the arithmetic flow_graph/param/test_backup_gen_live_rating.py
    pins): 125 % of the live critical list in the 5 kW commercial step; the
    monthly exercise as a daily average."""
    b = load(REF_GRAPH)
    PW.backup_criticals(b, INPUTS)
    rating = b.computed[('node', 'BACKUP_GEN', 'params.rated_kW')][0]
    basis = b.computed[('node', 'BACKUP_GEN', 'params.rated_kW_basis')][0]
    avg = b.computed[('node', 'BACKUP_GEN', 'continuous_kw.value')][0]
    # the live critical list: HABITATION 3.0 + CRYO_H2 peak 2.83 + CRYO_ASU 1.75
    # + GROW_BED 5.0 + controls 2.0 = 14.58 kW
    crit = PW._critical_list(b, DRIVERS_PAYLOAD)
    assert [k for k, _ in crit] == ['HABITATION', 'CRYO_H2', 'CRYO_ASU', 'GROW_BED', 'controls and instruments']
    s = sum((PW.dec(v) for _, v in crit), PW.D0)
    assert s == Decimal('14.58')
    # the rating rule: ceil(s x margin / step) x step
    expect = PW.ceil(s * PW.dec('1.25') / PW.dec('5')) * PW.dec('5')
    assert rating == 20.0 and expect == Decimal('20')
    assert '125 % of the live critical list 14.58 kW, rounded up in 5 kW steps' in basis
    assert basis.endswith('written by write_graph power(), read by docs-authority/_power_sizing.py and o2_close.py.')
    # the NFPA 110 8.4.2 exercise: rated x load x h x 12/365, over 24 h
    e_ex = PW.dec('20') * PW.dec('0.3') * PW.dec('0.5') * PW.dec(12) / PW.dec(365)
    assert PW.q(e_ex / 24, 4) == 0.0041 and avg == 0.0041
    note = b.computed[('node', 'BACKUP_GEN', 'continuous_kw.note')][0]
    assert note == 'X-PAR-12 TF: standby, NFPA 110 exercise average'


def test_grease_route_books():
    """The F-20261110-08 arithmetic survives as the registered pure re-solve:
    the A-M-480 SKF relubrication chain and the kettle duty reproduce the
    heat lane's in-memory override duty, while the demand census reads the
    seed's commercial-class stamps exactly as v1's own power() call did."""
    b = load(REF_GRAPH)
    route = PW._grease_route(b, DRIVERS_PAYLOAD)
    assert route['route'] == 'CA' and route['units'] == 75
    assert route['gp_g'] == Decimal('3.9')                    # 0.005 x 52 mm x 15 mm
    assert route['interval_d'] == Decimal('182.625')          # 6 months x 365.25/12
    assert PW.q(route['grease_kg_d'], 6) == 0.003203
    assert PW.q(route['kw'], 5) == 0.00008                    # the 8e-05 class the v1 lane fed the sizing
    assert PW.q(route['loss_W'], 1) == 11.5 and route['insul_mm'] == 25
    assert PW.q(route['lime_draw_kg_d'], 6) == 0.000052       # slaked from the acid-plant residue CaO
    # the registered function records nothing (the GREASE_* stamps belong to
    # the specialty and fluoro lanes)
    b2 = load(REF_GRAPH)
    PW.grease_route(b2, INPUTS)
    assert ('node', 'GREASE_CA', 'continuous_kw.value') not in b2.computed
    assert b2.computed == {}
    # the census books the seed stamps: GREASE_CA 0.2 + GREASE_LI 0.2
    books = PW._census(b)
    assert books['GREASE_CA'] == Decimal('0.2') and books['GREASE_LI'] == Decimal('0.2')
    s = PW._chain(b, INPUTS)
    assert s['census_sum'] == Decimal('95.84629')
    assert s['p_bounding'] == Decimal('103.34') and s['p_reference'] == Decimal('104.51')
    assert PW.q(s['rect_ac'], 4) == 7.4911                    # the EW rectifier AC, counted once (A-M-255)


def test_mvs_book_golden():
    """The mvs.electrical derivation equals the committed block exactly (the
    overlay has no graph-level lane yet: pure derivation, builder stamps)."""
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = json.load(f)['mvs']['electrical']
    b = load(REF_GRAPH)
    book = PW.mvs_book(b, INPUTS)
    assert book is not None and _eq(book, committed)
    assert book['need_kw']['value'] == 191.36 and book['target_kw']['value'] == 478.4
    assert book['pv_count'] == 5306 and book['znbr_count'] == 37 and book['znbr_module_kw'] == 60.0
    assert book['rect_count'] == 1
    assert 'roof_close 31x23 bays, ext 88.02 kW' in book['need_kw']['note']
    assert book['bus_nodes'] == ['SOL_ARK_60K', 'ZNBR2', 'RECTIFIER']


def test_pv01_delta_and_note_guard():
    """IA-PV-01 carries the extension delta (fresh SF-EXT_HALL less the feed
    the bus already books); the note keeps one X-PAR-07 segment."""
    b = load(REF_GRAPH)
    b.edges['SF-EXT_HALL']['rate']['value'] = 0.0             # the feed the bus has not booked yet
    PW.power_ledger(b, INPUTS)
    pv1 = b.computed[('edge', 'IA-PV-01', 'rate')][0]
    assert pv1['value'] == PW.q(PW.dec('370.8477') + PW.dec('88.0192') - PW.D0, 4)
    assert pv1['value'] == 458.8669
    assert 'X-PAR-07 extension hall: +105.21 kW.' in pv1['note']   # the committed segment stays
    # the note guard: a seed without the segment gains exactly one
    b2 = load(REF_GRAPH)
    b2.edges['IA-PV-01']['rate']['note'] = 'A-M-233 basis without the segment.'
    PW.power_ledger(b2, INPUTS)
    note = b2.computed[('edge', 'IA-PV-01', 'rate')][0]['note']
    assert note.endswith(' X-PAR-07 extension hall: +88.02 kW.') and note.count('X-PAR-07 extension hall') == 1
    # at the committed fixed point the delta is zero and the book is untouched
    b3 = load(REF_GRAPH)
    PW.power_ledger(b3, INPUTS)
    assert _eq(b3.computed[('edge', 'IA-PV-01', 'rate')][0], b3.edges['IA-PV-01']['rate'])


def test_generic_dispatch_non_pv_primary():
    """The portfolio dispatch is field-driven: a non-PV primary books the
    generic share x demand / capacity-factor path (X-LOC-08, F-20261113-01
    share restoration) with the worst-stretch storage books, and no roof
    extension exists at such a locale."""
    prof = copy.deepcopy(INPUTS['site_profile'])
    srcs = prof['groups']['power_portfolio']['entries']['sources']['value']
    srcs[0] = {'id': 'w', 'kind': 'wind', 'unit': 'GEO_ORC', 'role': 'primary',
               'share': 0.65, 'capacity_factor': 0.9, 'stretch_output_frac': 1.0,
               'ref': 'NOAA_MCMURDO'}
    b = load(REF_GRAPH)
    PW.pv_dispatch(b, {'drivers': DRIVERS_PAYLOAD, 'site_profile': prof})
    PW.znbr2_store_book(b, {'drivers': DRIVERS_PAYLOAD, 'site_profile': prof})
    nameplate = b.computed[('node', 'GEO_ORC', 'params.nameplate_kw')][0]
    assert nameplate == 74.6                                  # round(0.65 x 103.34 / 0.9, 1)
    assert b.computed[('node', 'GEO_ORC', 'params.kind')][0] == 'wind'
    ck = b.computed[('node', 'GEO_ORC', 'continuous_kw.value')][0]
    assert ck == 103.34                                       # the census demand, no roof extension
    note = b.computed[('node', 'GEO_ORC', 'continuous_kw.note')][0]
    assert note.startswith('wind primary: 103.34 kW demand / capacity factor 0.9 = 74.6 nameplate.')
    # the worst-stretch storage books at P 103.34, night 14, rt 0.7
    store = PW.dec('103.34') * 14
    store_in = store / PW.dec('0.7')
    assert b.computed[('node', 'ZNBR2', 'params.kWh')][0] == PW.ceil(store) == 1447
    assert b.computed[('node', 'ZNBR2', 'params.charge_kW')][0] == PW.ceil(store_in / 10) == 207
    assert b.computed[('node', 'ZNBR2', 'params.discharge_kW')][0] == 104
    # no PV-primary work happened
    assert not [k for k in b.computed if k[1] == 'PV_ARRAY' or k[1] == 'EXT_HALL' or k[1] == 'SOL_ARK_60K']


def test_no_payloads_record_nothing():
    """The bridge contracts: no payloads record nothing; drivers alone record
    nothing (the dispatch needs the site profile payload)."""
    for payloads in ({}, {'drivers': DRIVERS_PAYLOAD},
                     {'site_profile': INPUTS['site_profile']}):
        b = load(REF_GRAPH)
        PW.backup_criticals(b, payloads)
        PW.grease_route(b, payloads)
        PW.power_ledger(b, payloads)
        PW.pv_dispatch(b, payloads)
        PW.znbr2_store_book(b, payloads)
        PW.designed_sources(b, payloads)
        assert b.computed == {}


def test_composition_order_power_before_heat():
    """The required composition order: process -> power -> heat. The heat
    family reads this family's store book (ZNBR2 params.cycling_thermal,
    F-20261110-08); registered before heat, the family supplies it fresh.
    With the heat family as landed the composition stays byte-faithful (its
    charge_window read-back is seed-only, so it re-stamps the committed book
    over this family's fresh dict), and the fresh computation is the
    dry_cooler overlay-first read away - the one-line heat-lane amendment."""
    b = load(REF_GRAPH)
    PW.znbr2_store_book(b, INPUTS)
    fresh = b.computed[('node', 'ZNBR2', 'params.cycling_thermal')][0]
    assert fresh['kwh_d_out'] == 2679.0                       # this family's census book
    # heat, composed after power, re-stamps the dict from its seed read-back:
    # the committed block is restored exactly (test_heat's golden survives)
    HT.charge_window(b, INPUTS)
    final = b.computed[('node', 'ZNBR2', 'params.cycling_thermal')][0]
    assert final['kwh_d_out'] == 2658.8 and final['kwh_d_in'] == 3798.3
    assert final['avg_kW'] == 47.48 and final['window_kW'] == 113.95
    assert b.computed[('edge', 'IA-ZNBR-HEAT', 'rate')][0]['value'] == 47.4792
    # the fresh computation the order unlocks, once heat's read gains the
    # overlay-first idiom its own dry_cooler already uses: the window book
    # over THIS family's store
    wk = HT.window_book(PW.dec(fresh['kwh_d_out']), PW.dec(fresh['kwh_d_in']),
                        PW.dec(DRIVERS_PAYLOAD['night_hours']['value']),
                        PW.dec(DRIVERS_PAYLOAD['storage_round_trip']['value']))
    assert PW.q(wk['avg'], 2) == 47.84 and PW.q(wk['win_kw'], 2) == 114.82
    assert PW.q(wk['chg'], 2) == 382.72 and wk['win_h'] == PW.dec(10)


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (_value, prov) in b.computed.items():
        assert prov.stage == 'power' and prov.basis
    assert b.computed[('node', 'BACKUP_GEN', 'params.rated_kW')][1].ref == 'Q-040'
    assert b.computed[('node', 'BACKUP_GEN', 'continuous_kw.value')][1].ref == 'A-M-350'
    assert b.computed[('node', 'EXT_HALL', 'continuous_kw.value')][1].ref == 'X-PAR-07'
    assert b.computed[('node', 'EXT_HALL', 'params.hvac')][1].ref == 'X-PAR-08'
    assert b.computed[('node', 'PV_ARRAY', 'params.roof')][1].ref == 'X-PAR-07'
    assert b.computed[('node', 'SOL_ARK_60K', 'params.interconnection')][1].ref == 'A-M-237'
    assert b.computed[('node', 'ZNBR2', 'params.kWh')][1].ref == 'AQS-ELEC-007'
    assert b.computed[('node', 'ZNBR2', 'params.distribution')][1].ref == 'AQS-ELEC-008'
    assert b.computed[('node', 'ZNBR2', 'params.cycling_thermal')][1].ref == 'A-M-455'
    assert b.computed[('node', 'GEO_HP', 'continuous_kw.value')][1].ref == 'A-M-275'
    assert b.computed[('edge', 'IA-PV-01', 'rate')][1].ref == 'X-PAR-07'


def test_golden_texts():
    """The committed note books this family owns, verbatim."""
    b = run()
    out = json.loads(render(b))
    r_nodes = {n['unit_id']: n for n in out['nodes']}
    note = r_nodes['EXT_HALL']['continuous_kw']['note']
    assert note.startswith('X-PAR-07 solver.roof_close: conditioned extension 25236 m2; '
                           'lighting 22.21 kW (IECC 2021 C405, 10 % lit), ventilation 37.48 kW ')
    assert 'heating 26.4 kW and cooling 155.7 kW thermal average after internal gains 31.7 kW ' \
        'and slab edge 1.56 kW (IECC F-factor); loop pumping 0.00 kW. Comparison: .' in note
    assert r_nodes['EXT_HALL']['params']['duty'] == \
        'In 0.000 kg/d, out 0.000 kg/d, 88.019 kW. Sheet docs-authority/duties/EXT_HALL.md.'
    zn = r_nodes['ZNBR2']['continuous_kw']['note']
    assert zn.startswith('X-ELS-02: solved continuous discharge rating from docs-authority/_power_sizing.py')
    assert 'discharge 191.4 kW, charge 869.8 kW, 2679 kWh over 37 hybrid inverters (AQS-ELEC-008).' in zn
    assert zn.endswith('Was the stale 60 kW study value.')
    assert r_nodes['ZNBR2']['params']['distribution'] == \
        'distributed over the 37 hybrid inverters, 72.4 kWh and 23.5 kW charge each (AQS-ELEC-008)'
    assert r_nodes['ZNBR2']['params']['charge_basis'].startswith('D75 cloudy-day case: yield 0.50 x mean')
    hv = r_nodes['EXT_HALL']['params']['hvac']
    assert hv == {'light_kW': 22.208, 'vent_kW': 37.478, 'envelope_kW': 28.334, 'total_kW': 88.019,
                  'vent_L_s': 7570.8, 'Qh_kW': 26.395, 'Qc_kW': 155.686, 'slab_kW': 1.56,
                  'gains_kW': 31.671, 'pump_kW': 0.0, 'mode': 'air', 'peak_h_kW': 397.421,
                  'peak_c_kW': 351.552}
    roof = r_nodes['PV_ARRAY']['params']['roof']
    assert roof['roof_capacity_kWp'] == 2686.9 and roof['extension_load_kW'] == 88.02
    assert roof['roof_load_kPa'] == {'service_kPa': 1.11, 'lrfd_kPa': 1.716}
    assert roof['basis'].startswith('flow_graph/param/solver.py roof_close (IFC 2027 1205.3')
    inter = r_nodes['SOL_ARK_60K']['params']['interconnection']
    assert inter['export_peak_kW'] == 2028.6 and inter['export_kWh_d_clear'] == 5741
    assert inter['decision'] == 'D75' and inter['standards'].startswith('IEEE 1547-2018 Cat. B / III')
    assert r_nodes['PV_ARRAY']['params']['balance_kWp'] == 1327
    assert r_nodes['PV_ARRAY']['params']['nameplate_kw'] == 2653
    assert r_nodes['PV_ARRAY']['params']['count'] == 5306
    assert r_nodes['ZNBR2']['params']['kW'] == 870 and r_nodes['ZNBR2']['params']['kWh'] == 2680
    assert r_nodes['ZNBR2']['params']['charge_kW'] == 870 and r_nodes['ZNBR2']['params']['discharge_kW'] == 192


def test_function_module_grid_purity():
    """The engine module holds no float literals, no I/O, and no locale
    conditional (the lint's rule, and the field-driven dispatch rule)."""
    tree = ast.parse(inspect.getsource(PW))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
