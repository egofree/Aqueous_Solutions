"""engine v2: the si_route-family acceptance (the golden-value proof).

Reference writer: flow_graph/param/si_refine.py `--write` with its
fab_silicon.tf call, ledger row `si_route`, section B, PHYSICS - the
X-MFG-40/X-RTE-SI family-4 stage (A-M-471/472/484). The committed graph
carries every field the stage stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification, and a strict whole-model walk proves nothing else moved
  (the composer-owned topology, the pv_cell_line-owned SOLAR_PV_CELL design,
  the materials3-owned sec3_material and the foundry-seeded IA-CA-CL2-SHIP
  netting book stay byte-faithful);
- golden equality: every changed field equals the committed golden, exact at
  the golden's decimals - there are NO deviations on this family (the A-M-484
  netting delta is exactly 0 at the committed seed, so the export is not
  stamped at all);
- grid spot-checks on the integer books: the carbothermic chain (SiO2 + 2 C ->
  Si + 2 CO and the hood burn, the A-M-490 crib burden and the retired quartz,
  A-M-488 fume return), the EG chlorosilane loop (A-M-485..489 credits and
  bleed) and the CZ charge book (A-M-471 crucible least melt, A-M-484 cell
  need);
- the conditional-edge decisions recorded: the create-or-rate conditions of
  the 24 streams and 2 SF feeds, the SI_REFINE node creation, the
  IA-SI-IMPORT deletion and the A-M-484 netting are pinned as structured
  data; the CAST_MC156 cast-furnace branch is asserted to record nothing;
- determinism: two runs, byte-identical; the no-drivers bridge contract
  records nothing; grid purity: no float literals, no I/O in the module.
"""
import ast
import copy
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import si_route as SR
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

# ---- the change-set specification (hand-enumerated) ------------------------
NODE_FIELDS = (
    [('SI_REDUCE', 'continuous_kw'), ('SI_REFINE', 'continuous_kw'),
     ('SI_REDUCE', 'params.recovery'), ('SI_REFINE', 'params.recovery'),
     ('SI_REDUCE', 'params.design'), ('SI_REDUCE', 'params.sizing'),
     ('SI_REDUCE', 'params.size_mm'), ('SI_REDUCE', 'params.size_basis')]
)
RATE_EDGES = [
    # the fab silicon chain (A-M-471, fab_silicon.tf)
    'STOCK_TO_FAB', 'IA-FAB-WAFER', 'IA-LITHO-WAFER-A', 'IA-LITHO-WAFER-B',
    'IA-LITHO-WAFER-RET', 'IA-FAB-PRODUCT', 'IA-FAB-KERF', 'IA-FAB-KERF-REC',
    'IA-FAB-SCRAP', 'IA-PV-WAFER', 'IA-PV-CELL', 'IA-AR-CZ', 'IA-AR-CZ-BACK',
    # the SI_REDUCE / SI_REFINE route (A-M-472, si_refine.tf)
    'IA-QUARTZ-MU', 'IA-SI-BRIQ', 'CHAR_TO_SI', 'IA-SI-HOOD-O2', 'IA-SI-CO2',
    'IA-SI-FUME', 'IA-SI-MG', 'IA-CL2-SIREF', 'IA-SI-PURGE', 'IA-PV-EOL',
    'IA-SI-EG',
    # the SF electrical feeds
    'SF-SI_REDUCE', 'SF-SI_REFINE',
]
EDGE_FIELDS = [(sid, 'presence') for sid, _a, _z, _c, _k in SR.STREAMS_SI] \
    + [('IA-SI-PURGE', 'composition')]
# NO deviations: the golden equality is exact on every stamped field, and the
# A-M-484 netting leaves IA-CA-CL2-SHIP untouched at the committed seed.

# ---- topology mutation inventory (the composer lane's work; the seed proof) -
# Every graph-structure mutation the v1 --write pass performs, with its
# condition. The composer lane's module is landed (flow_graph/v2/functions/
# topology.py: si_route_topology carries the create-or-rate shape on these 24
# streams + 2 SF feeds, the SI_REFINE creation and the IA-SI-IMPORT deletion;
# the both-directions proof is flow_graph/v2/test_topology.py). The committed
# seed already carries all of it; the asserts pin it.
TOPOLOGY_INVENTORY = {
    'created_or_rated_edges': {sid: (a, zb) for sid, a, zb, _c, _k in SR.STREAMS_FAB + SR.STREAMS_SI},
    'created_or_rated_condition': ('an edge absent from the graph is created from the o2_close template '
                                   '(endpoints, carries, layers, composition, rate); a present edge is '
                                   're-rated in place - the seed carries every creation'),
    'created_or_rated_sf': {'SF-SI_REDUCE': ('SOL_ARK_60K', 'SI_REDUCE'),
                            'SF-SI_REFINE': ('SOL_ARK_60K', 'SI_REFINE')},
    'created_or_rated_sf_condition': ('the SF feed is created only when missing, header tray on creation; '
                                      'the seed carries both'),
    'created_node': {'SI_REFINE': ('GLASS', 'reactor',
                                   'created by v1 only when the graph predates the route; the seed carries it '
                                   'with its creation-time class/notes/params.presence')},
    'retired_edge_deleted': {'IA-SI-IMPORT': ('the dock silicon import: v1 retires it when present and not '
                                              'retired; the committed graph has it deleted outright '
                                              '(owner decision t58u, composer lane)')},
    'presence_flips': {sid: ('retired' if sid in ('IA-QUARTZ-MU', 'IA-SI-FUME') else 'present')
                       for sid, _a, _z, _c, _k in SR.STREAMS_SI},
    'presence_condition': ("presence books 'retired' exactly when the stamped rate books zero (the "
                           "recovery-first retire stamps, F-20261110-06); IA-QUARTZ-MU carries the retire "
                           "note in that state"),
    'netting': {'IA-CA-CL2-SHIP': ('rate.value + params.si_cl2_kg_d stamped only when the A-M-484 delta '
                                   'dl = seed book - recomputed make-up is non-zero; at the committed seed '
                                   'dl is 0.0 and the edge is not stamped',)},
    'fab_presence_asserted': ('the fab rates never book zero, so their presence is seed topology '
                              '(asserted, not stamped)'),
}


def run():
    b = load(REF_GRAPH)
    SR.si_route(b, INPUTS)
    return b


def _committed():
    with open(REF_GRAPH, encoding='utf-8') as f:
        return json.load(f)


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


def _strict_diffs(c_obj, r_obj, prefix, out, expected, deltas):
    """Paths where the rendered model differs from the committed graph beyond
    the expected change set: strict (same JSON types) everywhere except the
    enumerated fields (numeric equality at the golden's decimals). Provenance
    rows are excluded."""
    for k in sorted((set(c_obj) | set(r_obj)) - {'provenance'}):
        p = prefix + '.' + k if prefix else k
        if k not in c_obj or k not in r_obj:
            out.add(p)
        elif p in deltas:
            if (c_obj[k], r_obj[k]) != deltas[p]:
                out.add(p + ' (deviation pair moved)')
        elif p in expected:
            if not _eq(c_obj[k], r_obj[k]):
                out.add(p)
        elif isinstance(c_obj[k], dict) and isinstance(r_obj[k], dict):
            _strict_diffs(c_obj[k], r_obj[k], p, out, expected, deltas)
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
    assert got_nodes == sorted(NODE_FIELDS), (
        sorted(set(got_nodes) - set(NODE_FIELDS)), sorted(set(NODE_FIELDS) - set(got_nodes)))
    expected_edges = sorted([(sid, 'rate') for sid in RATE_EDGES] + EDGE_FIELDS)
    assert got_edges == expected_edges, (
        sorted(set(got_edges) - set(expected_edges)),
        sorted(set(expected_edges) - set(got_edges)))

    for uid, path in NODE_FIELDS:
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)
    for sid, path in expected_edges:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    # nothing else moves: a strict walk of every node and edge finds no drift
    # beyond the enumerated fields (no deviations on this family)
    expected_node_paths = {uid + '.' + path for uid, path in NODE_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_node_paths, {})
    assert diffs == set(), sorted(diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in expected_edges}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths, {})
    assert edge_diffs == set(), sorted(edge_diffs)


def test_carbothermic_chain():
    """The SI_REDUCE books on integer mg counts (A-M-472/488/490): the
    carbothermic stoichiometry, the hood burn, the crib burden and the retired
    quartz."""
    s = SR._core(load(REF_GRAPH), INPUTS)
    M = SR.M
    # the furnace reduces si_in from the burden: SiO2 + 2 C -> Si + 2 CO
    assert SR.book(s['si_in'], 4, '') == 2029 and SR.book(s['sio2_r'], 6, '') == 434133
    assert SR.book(s['c'], 6, '') == 173572 and SR.book(s['co'], 6, '') == 404775
    assert s['c'] == 2 * M['C'] * s['si_in'] / M['Si']
    assert s['sio2_r'] == s['si_in'] * SR.M_SIO2 / M['Si']
    assert s['co'] == 2 * SR.M_CO * s['si_in'] / M['Si']
    # the hood burn: CO + 1/2 O2 -> CO2 (A-M-472 open-top class); the identity
    # co2 - co == o2_hood holds exactly on the molar masses
    assert SR.book(s['o2_hood'], 6, '') == 231203 and SR.book(s['co2'], 6, '') == 635978
    assert s['co2'] - s['co'] == s['o2_hood']
    assert s['o2_hood'] == s['co'] * SR.M_O2 / 2 / SR.M_CO
    assert s['co2'] == s['co'] * SR.M_CO2 / SR.M_CO
    # recovery-first burden (A-M-490 crib pool covers the need; A-M-472):
    # quartz books zero and the edge retires
    assert SR.book(s['crib'], 6, '') == 6033099 and SR.book(s['burden_need'], 6, '') == 438274
    assert SR.book(s['briq'], 6, '') == 438274 and SR.book(s['quartz'], 6, '') == 0
    assert s['briq'] == min(s['crib'], s['burden_need']) and s['quartz'] == s['burden_need'] - s['briq']
    # the A-M-488 fume return is total at si_fume_burden_frac 1.0: no fume to the leach
    assert SR.book(s['fume_leach'], 6, '') == 0
    # the furnace burden closes exactly (the v1 1e-9 float assert, exact here)
    assert s['briq'] + s['quartz'] + s['c'] + s['o2_hood'] == s['mg'] + s['co2'] + s['fume_leach']
    b = run()
    assert b.computed[('edge', 'CHAR_TO_SI', 'rate')][0]['value'] == 0.173572
    assert b.computed[('edge', 'IA-SI-HOOD-O2', 'rate')][0]['value'] == 0.231203
    assert b.computed[('edge', 'IA-SI-BRIQ', 'rate')][0]['value'] == 0.438274
    assert b.computed[('edge', 'IA-QUARTZ-MU', 'rate')][0]['value'] == 0.0
    assert b.computed[('edge', 'IA-QUARTZ-MU', 'presence')][0] == 'retired'
    assert b.computed[('edge', 'IA-QUARTZ-MU', 'rate')][0]['note'] == SR.QUARTZ_RETIRED_NOTE
    assert b.computed[('edge', 'IA-SI-FUME', 'presence')][0] == 'retired'


def test_eg_chlorosilane_chain():
    """The SI_REFINE loop books on integer mg counts (A-M-472/485..489): the
    credits first, the make-up chlorine, the bleed and the loads."""
    s = SR._core(load(REF_GRAPH), INPUTS)
    # the CZ charge books (A-M-471): the crucible least melt governs the pull
    assert SR.book(s['min_kg'], 6, '') == 33521858 and SR.book(s['need_kg'], 6, '') == 9901529
    assert s['charge_kg'] == max(s['need_kg'], s['min_kg'])
    assert SR.book(s['charge_kg'], 6, '') == 33521858
    assert SR.book(s['interval_d'], 6, '') == 23698663 and SR.book(s['pull_h'], 4, '') == 101811
    assert SR.book(s['si_kg_d'], 6, '') == 1414504 and SR.book(s['wafer_kg_d'], 6, '') == 138904
    assert SR.book(s['pv_wafer_kg_d'], 6, '') == 408673
    assert SR.book(s['kerf_leach'], 6, '') == 43592 and SR.book(s['kerf_rec'], 6, '') == 392324
    assert SR.book(s['scrap_rec'], 6, '') == 431011 and SR.book(s['ar_kg_d'], 6, '') == 3348249
    # the semi-square corner book (the pv cell area on the CZ ingot, cm2)
    assert SR.book(s['a_pv'], 6, '') == 148579864
    # the loop: eg = charge - returned scrap; eol and kerf are credits (A-M-485/486)
    assert SR.book(s['eg'], 6, '') == 983493 and SR.book(s['eol_in'], 6, '') == 408673
    assert SR.book(s['eol'], 6, '') == 388239 and SR.book(s['eol_res'], 6, '') == 20434
    assert s['si_in'] == s['eg'] - s['eol'] - s['kerf_rec'] and s['si_in'] > 0
    assert s['mg'] == s['si_in'] / SR.rat('0.98') and SR.book(s['mg'], 6, '') == 207071
    assert SR.book(s['imp'], 6, '') == 4141
    # the chlorine make-up leaves only with the impurity chlorides (A-M-489
    # blend: 2.2 kg Cl per kg of metal)
    assert SR.book(s['cl2'], 6, '') == 9111 and SR.book(s['purge'], 6, '') == 33686
    assert s['cl2'] == s['imp'] * SR.rat('2.2')
    assert s['purge'] == s['imp'] + s['cl2'] + s['eol_res']
    # the A-M-489 hydrogenation books (unstamped chain values)
    assert SR.book(s['stc_rec'], 6, '') == 173558 and SR.book(s['h2'], 6, '') == 8303
    # the loop closes exactly (the v1 1e-9 float assert, exact here)
    assert s['mg'] + s['eol_in'] + s['kerf_rec'] + s['cl2'] == s['eg'] + s['purge']
    # the loads on the 0.1 mW book
    assert SR.book(s['kw_reduce'], 4, '') == 1122 and SR.book(s['kw_refine'], 4, '') == 24587
    b = run()
    assert b.computed[('edge', 'IA-SI-EG', 'rate')][0]['value'] == 0.983493
    assert b.computed[('edge', 'IA-SI-MG', 'rate')][0]['value'] == 0.207071
    assert b.computed[('edge', 'IA-CL2-SIREF', 'rate')][0]['value'] == 0.009111
    assert b.computed[('node', 'SI_REDUCE', 'continuous_kw')][0]['value'] == 0.1122
    assert b.computed[('node', 'SI_REFINE', 'continuous_kw')][0]['value'] == 2.4587
    assert b.computed[('edge', 'SF-SI_REDUCE', 'rate')][0]['value'] == 0.1122
    assert b.computed[('edge', 'SF-SI_REFINE', 'rate')][0]['value'] == 2.4587


def test_si_reduce_design_book():
    """The F-20261110-09 single-writer design stamps: 4 dp design schema."""
    s = SR._core(load(REF_GRAPH), INPUTS)
    assert SR.book(s['si_in'], 4, '') == 2029 and SR.book(s['sio2_r'], 4, '') == 4341
    assert SR.book(s['c'], 4, '') == 1736
    b = run()
    design = b.computed[('node', 'SI_REDUCE', 'params.design')][0]
    assert design['si_kgd'] == 0.2029 and design['sio2_kgd'] == 0.4341 and design['char_kgd'] == 0.1736
    assert design['duty'].startswith('carbothermic silicon reduction')
    assert b.computed[('node', 'SI_REDUCE', 'params.sizing')][0] == {'si_kgd': 0.2029}
    assert b.computed[('node', 'SI_REDUCE', 'params.size_mm')][0] == [1200, 1000, 1600]
    assert b.computed[('node', 'SI_REDUCE', 'params.size_basis')][0].startswith('graphite hot-face furnace')


def test_purge_bleed_composition():
    """The A-M-489 bleed blend: the registered Fe/Al/Ca chloride weights plus
    the separation residue, renormalised (the documented v1 float book)."""
    b = run()
    comp = b.computed[('edge', 'IA-SI-PURGE', 'composition')][0]
    assert comp == {'FeCl3': 0.424177, 'AlCl3': 0.144339, 'CaCl2': 0.053922,
                    'separation residue': 0.377563}
    assert abs(sum(comp.values()) - 1.0) < 1e-6
    assert set(comp) == {name for name, _w, _f in SR.IMP_BLEND_W} | {'separation residue'}


def test_fab_rate_books():
    """The fab-chain rate books and note texts land on the committed edges."""
    b = run()
    assert b.computed[('edge', 'STOCK_TO_FAB', 'rate')][0]['value'] == 1.414504
    assert b.computed[('edge', 'IA-FAB-SCRAP', 'rate')][0]['value'] == 0.431011
    assert b.computed[('edge', 'IA-AR-CZ', 'rate')][0]['value'] == 3.348249
    assert b.computed[('edge', 'IA-AR-CZ-BACK', 'rate')][0]['value'] == 3.348249
    assert b.computed[('edge', 'IA-PV-CELL', 'rate')][0]['value'] == 0.408673
    for sid in ('STOCK_TO_FAB', 'IA-FAB-KERF-REC', 'IA-PV-CELL'):
        note = b.computed[('edge', sid, 'rate')][0]['note']
        assert note.startswith('X-MFG-40 TF (A-M-471): ') and note.endswith('(fab_silicon.py).'), sid
    for sid in ('IA-SI-EG', 'IA-SI-MG', 'IA-SI-PURGE'):
        note = b.computed[('edge', sid, 'rate')][0]['note']
        assert 'X-MFG-40 TF, on-site silicon (A-M-472): ' in note
        assert note.endswith('(si_refine.py, route TCS_SIEMENS).'), sid
    assert 'metallurgical silicon x si_saf_kWh_kg / 24 h' in \
        b.computed[('node', 'SI_REDUCE', 'continuous_kw')][0]['note']
    assert 'electronic-grade silicon x si_refine_kWh_kg_TCS_SIEMENS / 24 h' in \
        b.computed[('node', 'SI_REFINE', 'continuous_kw')][0]['note']


def test_conditional_edge_decisions():
    """The conditional decisions recorded: the A-M-484 netting is a no-op at
    the seed, the deletions/creations are seed topology, and the CAST_MC156
    branch records nothing (the deferred-route contract)."""
    committed = _committed()
    c_edges = {e['stream_id']: e for e in committed['edges']}
    b = run()
    # the A-M-484 netting: the seed draw book equals the recomputed make-up,
    # so dl is exactly 0.0 and the family stamps nothing on the export
    seed_book = c_edges['IA-CA-CL2-SHIP']['params']['si_cl2_kg_d']
    s = SR._core(load(REF_GRAPH), INPUTS)
    assert seed_book == 0.009111121123485916
    assert s['fb']['cl2_f'] == seed_book and seed_book - s['fb']['cl2_f'] == 0.0
    assert ('edge', 'IA-CA-CL2-SHIP', 'rate') not in b.computed
    assert ('edge', 'IA-CA-CL2-SHIP', 'params.si_cl2_kg_d') not in b.computed
    # the composer inventory is pinned against the committed seed
    inv = TOPOLOGY_INVENTORY
    for sid, (a, zb) in inv['created_or_rated_edges'].items():
        e = c_edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb), sid
    for sid, (a, zb) in inv['created_or_rated_sf'].items():
        e = c_edges[sid]
        assert (e['from_unit_id'], e['to_unit_id']) == (a, zb) and e.get('header') == 'tray', sid
    assert inv['created_node']['SI_REFINE'][0] == 'GLASS'
    assert 'IA-SI-IMPORT' not in c_edges
    for sid, want in inv['presence_flips'].items():
        assert c_edges[sid].get('presence') == want, sid
    # the tcs_circ term is computed by the reference writer but stamped nowhere
    assert not any(path == 'tcs_circ_kg_d' for (_k, _i, path) in b.computed)
    # the deferred CAST_MC156 branch records nothing
    drv2 = copy.deepcopy(INPUTS['drivers'])
    drv2['pv_wafer_route']['value'] = 'CAST_MC156'
    b2 = load(REF_GRAPH)
    SR.si_route(b2, {'drivers': drv2})
    assert b2.computed == {}
    # the route guards fail loudly
    drv3 = copy.deepcopy(INPUTS['drivers'])
    drv3['si_refine_route']['value'] = 'BOGUS'
    try:
        SR.si_route(load(REF_GRAPH), {'drivers': drv3})
        raise AssertionError('the si_refine_route guard did not fire')
    except ValueError:
        pass


def test_silane_fbr_route_dispatch():
    """SILANE_FBR ports in full: the route driver selects the yield/kWh drivers
    and the note route name; the EG need and the furnace load are route-plain."""
    drv2 = copy.deepcopy(INPUTS['drivers'])
    drv2['si_refine_route']['value'] = 'SILANE_FBR'
    b = load(REF_GRAPH)
    SR.si_route(b, {'drivers': drv2})
    kw = b.computed[('node', 'SI_REFINE', 'continuous_kw')][0]
    assert kw['value'] == 0.8196                     # 0.983493 kg/d x 20.0 kWh/kg / 24 h
    assert 'si_refine_kWh_kg_SILANE_FBR / 24 h' in kw['note']
    assert b.computed[('node', 'SI_REDUCE', 'continuous_kw')][0]['value'] == 0.1122
    assert b.computed[('edge', 'SF-SI_REFINE', 'rate')][0]['value'] == 0.8196


def test_topo_composer_lane_inventory_documented():
    """The inventory names every residue class and carries the conditions."""
    inv = TOPOLOGY_INVENTORY
    assert set(inv['created_or_rated_edges']) == {sid for sid, _a, _z, _c, _k in SR.STREAMS_FAB + SR.STREAMS_SI}
    assert set(inv['created_or_rated_sf']) == {'SF-SI_REDUCE', 'SF-SI_REFINE'}
    assert inv['created_node']['SI_REFINE'][1] == 'reactor'
    assert 'dl' in inv['netting']['IA-CA-CL2-SHIP'][0]
    assert inv['created_or_rated_condition'] and inv['presence_condition']


def test_no_drivers_records_nothing():
    b = load(REF_GRAPH)
    SR.si_route(b, {})
    assert b.computed == {}


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (value, prov) in b.computed.items():
        assert prov.stage == 'si_route' and prov.basis
    assert b.computed[('node', 'SI_REDUCE', 'params.design')][1].basis.startswith(
        'the F-20261110-09 single-writer rule')
    assert 'single-writer' in b.computed[('node', 'SI_REDUCE', 'continuous_kw')][1].ref
    assert 'recovery-first retire stamp' in b.computed[('edge', 'IA-QUARTZ-MU', 'presence')][1].basis
    assert 'create-or-rate edge' in b.computed[('edge', 'IA-SI-EG', 'rate')][1].ref
    assert 'header tray' in b.computed[('edge', 'SF-SI_REDUCE', 'rate')][1].ref
    assert 'A-M-489' in b.computed[('edge', 'IA-SI-PURGE', 'composition')][1].basis


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(SR))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
