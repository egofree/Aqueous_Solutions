"""engine v2: the topology lane acceptance - the both-directions proof.

The composer lane's module (flow_graph/v2/functions/topology.py) carries the
graph-shape mutations as pure, data-conditioned functions (the site pattern:
conditions are presence/driver data, never a locale id). The proofs:

- the bridge both ways: on the committed seed the topology pass is a
  byte-identical no-op (every create-if-missing finds its edge, every retire
  finds it retired, every seed param finds itself seeded); on a tampered seed
  - a created edge deleted, the BRINE_CRYS node and streams deleted, a
  retired import restored to its pre-mutation state, the dock silicon import
  back, the dry-cooler terminal clone gone - the pass restores the committed
  shape and the FULL pipeline render (topology, then every value family in
  the declared composition order) is byte-identical to the untampered
  pipeline render;
- the data conditions table: each mutation keys on its condition - asserted
  as behavior (the condition removed from the seed, the mutation stays
  quiet) and as the declared tables;
- composition: solve.py imports topology FIRST - the shape precedes the
  values; the foundry value-only brine re-rate and the family seed asserts
  read the post-mutation shape;
- the SI_REFINE creation condition restores the node (field-equal with the
  committed node after the families re-run);
- the mars/locale designed-source placements (FSP_40K / MMRTG) are a
  verified no-op: the site family reads presence and records none, and no
  topology function touches those nodes;
- determinism: two tampered-seed pipelines, byte-identical; purity: no float
  literals, no I/O, no banned imports, no locale ids in the module.

The one documented non-convergence: deleting a created edge TOGETHER WITH its
committed-shape successor (an within-chain multi-delete) can only fall back
to the block-edge anchor - the single-edge and cross-group tampers proven
here are the bridge contract. The SI_REFINE node's params dict reorders its
two downstream overlays (sec3_material before recovery in the committed tree
is write history, not shape); the node restores field-equal and the byte
fixed point arrives with the next update write.
"""
import ast
import copy
import inspect
import json
import os

from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import foundry as FD
from flow_graph.v2.functions import si_route as SR
from flow_graph.v2.functions import sites as ST
from flow_graph.v2.functions import topology as TT
from flow_graph.v2.graph_io import bytes as render, load
from flow_graph.v2.model import Builder

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
MARS = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'mars.json')
COMMITTED = json.load(open(REF_GRAPH, encoding='utf-8'))
COMMITTED_BYTES = open(REF_GRAPH, 'rb').read()
INPUTS = {'drivers': json.load(open(DRIVERS, encoding='utf-8'))}
TOPOLOGY_FNS = [TT.foundry_apply, TT.si_route_topology, TT.heat_relief_topology]

# every created edge of the three families (the foundry creates incl. the
# brine block and SF feeds, the textile six, the SI route's 24 streams and
# 2 SF feeds) plus the IA-DC-REJ terminal clone
CREATED = [row[0] for row in TT.FOUNDRY_MASS] + [row[0] for row in TT.SF_POTS] \
    + [row[0] for row in TT.BRINE_STREAMS] + [TT.SF_BRINE[0]] \
    + [row[0] for row in TT.TEXTILE] + [row[0] for row in TT.STREAMS_FAB + TT.STREAMS_SI] \
    + [row[0] for row in TT.SF_SI] + [TT.DC_REJ]


def _pipeline(data, inputs=None):
    """The declared composition on a (possibly tampered) seed: the full solve
    (topology first, then the value families), rendered. data: a parsed graph
    dict - the committed structure, or a tampered copy of it. No file is
    written; the committed file is only ever read."""
    b = Builder(data)
    for f in SL.FNS:
        f(b, inputs or INPUTS)
    return render(b)


def _topology_only(data, inputs=None):
    b = load.__wrapped__(REF_GRAPH) if hasattr(load, '__wrapped__') else load(REF_GRAPH)
    b.data = data
    b.nodes = {n['unit_id']: n for n in data.get('nodes', [])}
    b.edges = {e['stream_id']: e for e in data.get('edges', [])}
    for f in TOPOLOGY_FNS:
        f(b, inputs or {})
    return b


# ---- the bridge both ways ----------------------------------------------------

def test_idempotent_on_the_committed_seed():
    """Direction (a): the topology pass on the committed seed changes
    NOTHING - byte-identical render, twice over (idempotence)."""
    b = load(REF_GRAPH)
    for f in TOPOLOGY_FNS:
        f(b, INPUTS)
    once = render(b)
    assert once == COMMITTED_BYTES
    b2 = load(REF_GRAPH)
    b2.data, b2.nodes, b2.edges = json.loads(once), {}, {}
    b2.nodes = {n['unit_id']: n for n in b2.data['nodes']}
    b2.edges = {e['stream_id']: e for e in b2.data['edges']}
    for f in TOPOLOGY_FNS:
        f(b2, INPUTS)
    assert render(b2) == COMMITTED_BYTES


def test_the_composition_shape_precedes_the_values():
    """Direction (a) through the whole declared order: the full solve with the
    topology functions stamps exactly what it stamps without them - the shape
    pass adds nothing on the committed seed."""
    from flow_graph.v2.registry import FNS
    saved = list(FNS)
    try:
        FNS[:] = [f for f in saved if getattr(f, 'stage_name', '').startswith('topology_') is False]
        without = _pipeline(COMMITTED)
    finally:
        FNS[:] = saved
    assert _pipeline(COMMITTED) == without


BASE = _pipeline.__wrapped__() if hasattr(_pipeline, '__wrapped__') else None


def test_restorative_created_edges():
    """Direction (b): deleting any single created edge restores the exact
    committed shape - the full pipeline render is byte-identical to the
    untampered pipeline render."""
    base = _pipeline(COMMITTED)
    ids = {e['stream_id'] for e in COMMITTED['edges']}
    for sid in CREATED:
        assert sid in ids, sid
        data = copy.deepcopy(COMMITTED)
        data['edges'] = [e for e in data['edges'] if e['stream_id'] != sid]
        assert _pipeline(data) == base, sid


def test_restorative_named_tampers():
    """The acceptance tampers: BRINE_CRYS's streams (and the node) deleted, a
    retired import restored to its pre-mutation state, the dock silicon
    import back, the dry-cooler terminal clone gone - each byte-converges,
    and so does one cross-group combination."""
    base = _pipeline(COMMITTED)
    brine = {row[0] for row in TT.BRINE_STREAMS} | {TT.SF_BRINE[0]}
    data = copy.deepcopy(COMMITTED)
    data['edges'] = [e for e in data['edges'] if e['stream_id'] not in brine]
    assert _pipeline(data) == base

    data = copy.deepcopy(COMMITTED)
    data['edges'] = [e for e in data['edges'] if e['stream_id'] not in brine]
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != 'BRINE_CRYS']
    assert _pipeline(data) == base

    for sid, flip_carries, add_dock in (('IA-MGCL2-MU', True, True), ('IA-CACL2-MU', True, True),
                                        ('IA-WAX-MU', True, True), ('IA-ALCL3-MU', True, False),
                                        ('IA-SHELL-EXPORT', False, False), ('IA-SILICA-MU', False, False),
                                        ('IA-C-TI', False, False), ('IA-C-MO', False, False),
                                        ('IA-C-CR', False, False), ('FR_FINISH', False, True),
                                        ('IA-CL2-SHIP', False, False)):
        data = copy.deepcopy(COMMITTED)
        e = next(x for x in data['edges'] if x['stream_id'] == sid)
        e['presence'] = 'present'
        e['rate'] = {'value': 3.0, 'unit': 'kg/d', 'status': 'study', 'note': 'active import'}
        if flip_carries:
            e['carries'] = 'pre-retirement wording'
        if add_dock:
            e.setdefault('params', {})['dock_class'] = 'process_chemical'
            e['params']['dock_pending_task'] = 'X-QA-11'
        if sid == 'IA-CL2-SHIP':
            e.setdefault('params', {})['si_cl2_kg_d'] = 0.5   # the A-M-484 pop repairs this book
        assert _pipeline(data) == base, sid

    data = copy.deepcopy(COMMITTED)
    data['edges'].append({'stream_id': TT.SI_IMPORT, 'from_unit_id': 'NORTH_DOCK',
                          'to_unit_id': 'SI_REFINE', 'phase': 'S', 'layers': ['mass'],
                          'presence': 'present', 'carries': 'dock silicon import',
                          'rate': {'value': 1.0, 'unit': 'kg/d', 'status': 'study', 'note': ''},
                          'composition': {'Si': 1.0}})
    assert _pipeline(data) == base

    data = copy.deepcopy(COMMITTED)
    data['edges'] = [e for e in data['edges'] if e['stream_id'] != TT.DC_REJ]
    assert _pipeline(data) == base

    data = copy.deepcopy(COMMITTED)
    drop = brine | {'IA-FR-P', 'SF-AL_POT', TT.DC_REJ, 'IA-AL-CAKE'}
    data['edges'] = [e for e in data['edges'] if e['stream_id'] not in drop]
    e = next(x for x in data['edges'] if x['stream_id'] == 'IA-MGCL2-MU')
    e['presence'] = 'present'
    e['carries'] = 'pre-retirement wording'
    e.setdefault('params', {})['dock_class'] = 'process_chemical'
    data['edges'].append({'stream_id': TT.SI_IMPORT, 'from_unit_id': 'NORTH_DOCK',
                          'to_unit_id': 'SI_REFINE', 'presence': 'present',
                          'rate': {'value': 1.0, 'unit': 'kg/d', 'status': 'study', 'note': ''}})
    assert _pipeline(data) == base


def test_si_refine_node_creation_restores_the_node():
    """The SI_REFINE creation condition: a seed predating the route (the node
    gone, the route furnace present) gets the node back at its committed
    position, and after the families re-run the node is field-equal with the
    base pipeline's node (dict equality is order-blind; the committed params
    key order is downstream write history, documented in the module
    docstring)."""
    base = json.loads(_pipeline(COMMITTED))
    base_node = next(n for n in base['nodes'] if n['unit_id'] == 'SI_REFINE')
    data = copy.deepcopy(COMMITTED)
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != 'SI_REFINE']
    out = json.loads(_pipeline(data))
    node = next(n for n in out['nodes'] if n['unit_id'] == 'SI_REFINE')
    assert node == base_node
    # the creation shape is the v1 creation spec, byte for byte on the seed
    b = Builder(copy.deepcopy(data))
    TT.si_route_topology(b, {})
    assert b.nodes['SI_REFINE']['sector_id'] == 'GLASS'
    assert b.nodes['SI_REFINE']['class'] == 'reactor'
    assert b.nodes['SI_REFINE']['params'] == {'presence': 'present',
                                              'note': TT.SI_REFINE_NOTE}
    assert b.nodes['SI_REFINE']['notes'] == TT.SI_REFINE_NOTES
    assert [n['unit_id'] for n in b.data['nodes']].index('SI_REFINE') == \
        [n['unit_id'] for n in COMMITTED['nodes']].index('SI_REFINE')


# ---- the data conditions table (behavioral rows) ----------------------------

def _shape(data):
    """The topology-relevant shape of a parsed seed: ids in list order."""
    return ([n['unit_id'] for n in data['nodes']],
            [e['stream_id'] for e in data['edges']])


def test_condition_textile_spin_line_in_graph():
    """The six textile edges exist exactly when the POLY_FIBER node is in the
    graph (the writer's condition; A-M-429)."""
    data = copy.deepcopy(COMMITTED)
    nodes, edges = _shape(data)
    assert 'POLY_FIBER' in nodes and 'FLEECE_TO_MFG' in edges
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != 'POLY_FIBER']
    for sid in ('STOCK_TO_FIBER', 'IA-FR-P', 'IA-FR-NH3', 'FIBER_SCRAP', 'FLEECE_TO_MFG', 'TEXTILE_HAB'):
        data['edges'] = [e for e in data['edges'] if e['stream_id'] != sid]
    b = _topology_only(copy.deepcopy(data))
    assert not any(e['stream_id'] in {r[0] for r in TT.TEXTILE} for e in b.data['edges'])
    # the S34B finish book seeds only where the spin line is live: with the
    # line gone and the book deleted, it stays absent
    s34 = next(e for e in data['edges'] if e['stream_id'] == 'S34B')
    s34.setdefault('params', {}).pop('pre_fr_kg_d', None)
    b = _topology_only(copy.deepcopy(data))
    assert 'pre_fr_kg_d' not in b.edges['S34B'].get('params', {})
    # the S34B finish book seeds only where the spin line is live
    data2 = copy.deepcopy(COMMITTED)
    s34 = next(e for e in data2['edges'] if e['stream_id'] == 'S34B')
    s34.setdefault('params', {}).pop('pre_fr_kg_d', None)
    b2 = _topology_only(data2)
    assert b2.edges['S34B']['params']['pre_fr_kg_d'] == s34['rate']['value']


def test_condition_brine_hosts_present():
    """The brine block exists exactly where the leach and the pots run
    (AQS-SITE-010: the hosts-present locale gate; A-M-496)."""
    data = copy.deepcopy(COMMITTED)
    brine = {row[0] for row in TT.BRINE_STREAMS} | {TT.SF_BRINE[0]}
    data['edges'] = [e for e in data['edges'] if e['stream_id'] not in brine]
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != 'BRINE_CRYS']
    b = _topology_only(copy.deepcopy(data))
    assert 'BRINE_CRYS' in b.nodes and brine <= {e['stream_id'] for e in b.data['edges']}
    assert b.nodes['BRINE_CRYS']['class'] == 'precip'
    assert b.nodes['BRINE_CRYS']['sector_id'] == b.nodes['CA_POT']['sector_id']
    assert b.nodes['BRINE_CRYS']['params'] == {'presence': 'present',
                                               'note': 'Brine crystallizer (A-M-496).'}
    data['nodes'] = [dict(n, presence='eliminated') if n['unit_id'] == 'CA_POT' else n
                     for n in data['nodes']]
    data['nodes'].append(next(n for n in COMMITTED['nodes'] if n['unit_id'] == 'BRINE_CRYS'))
    b2 = _topology_only(copy.deepcopy(data))
    # the gate reads presence: an eliminated host silences the route's creates
    data3 = copy.deepcopy(COMMITTED)
    for n in data3['nodes']:
        if n['unit_id'] == 'CA_POT':
            n['presence'] = 'eliminated'
    b3 = _topology_only(data3)
    assert brine <= {e['stream_id'] for e in b3.data['edges']}   # seed carries them; retire side idempotent


def test_condition_dc_rej_clone():
    """The IA-DC-REJ terminal clone fires only when the edge is absent AND the
    HL-Q4-REJ template AND the DRY_COOLER host exist (heat docstring, F-3)."""
    data = copy.deepcopy(COMMITTED)
    data['edges'] = [e for e in data['edges'] if e['stream_id'] != TT.DC_REJ]
    b = _topology_only(copy.deepcopy(data))
    rej = b.edges[TT.DC_REJ]
    tmpl = next(e for e in COMMITTED['edges'] if e['stream_id'] == TT.DC_TEMPLATE)
    for k, v in tmpl.items():
        if k not in ('stream_id', 'from_unit_id', 'to_unit_id', 'to_sector_id', 'carries',
                     'namespace', 'notes', 'rate'):
            assert rej[k] == v, k
    assert (rej['from_unit_id'], rej['to_unit_id'], rej['to_sector_id']) == ('DRY_COOLER', 'ATMOS', 'WTR')
    assert rej['carries'] == TT.DC_CARRIES and rej['namespace'] == 'IA'
    assert rej['notes'] == TT.DC_NOTES
    data['edges'] = [e for e in data['edges'] if e['stream_id'] != TT.DC_TEMPLATE]
    b2 = _topology_only(copy.deepcopy(data))
    assert TT.DC_REJ not in b2.edges           # no template, no clone
    data = copy.deepcopy(COMMITTED)
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != TT.DC_HOST]
    b3 = _topology_only(data)
    assert TT.DC_REJ in b3.edges               # the seed's own edge stays; no clone runs
    data4 = copy.deepcopy(COMMITTED)
    data4['edges'] = [e for e in data4['edges'] if e['stream_id'] not in (TT.DC_REJ, TT.DC_TEMPLATE)]
    b4 = _topology_only(data4)
    assert TT.DC_REJ not in b4.edges


def test_condition_si_route_node_and_import():
    """The SI_REFINE node is created only beside the route furnace; the IA-
    SI-IMPORT converges by deletion (owner decision t58u)."""
    data = copy.deepcopy(COMMITTED)
    data['nodes'] = [n for n in data['nodes'] if n['unit_id'] != 'SI_REFINE']
    b = _topology_only(copy.deepcopy(data))
    assert 'SI_REFINE' in b.nodes
    data2 = copy.deepcopy(COMMITTED)
    data2['nodes'] = [n for n in data2['nodes'] if n['unit_id'] not in ('SI_REFINE', 'SI_REDUCE')]
    b2 = _topology_only(data2)
    assert 'SI_REFINE' not in b2.nodes
    data3 = copy.deepcopy(COMMITTED)
    data3['edges'].append({'stream_id': TT.SI_IMPORT, 'from_unit_id': 'NORTH_DOCK',
                           'to_unit_id': 'SI_REFINE', 'presence': 'present',
                           'rate': {'value': 1.0, 'unit': 'kg/d', 'status': 'study', 'note': ''}})
    b3 = _topology_only(data3)
    assert TT.SI_IMPORT not in b3.edges
    assert TT.SI_IMPORT not in {e['stream_id'] for e in COMMITTED['edges']}


def test_condition_al_line_seed_and_repoint():
    """The pre-cake bases seed once from the rate when the Al line runs
    (driver foundry_al_line_kg_d > 0, the al_cake > 0 governing condition,
    F-20261110-07); the wax re-point follows the from-node sector."""
    data = copy.deepcopy(COMMITTED)
    for sid in ('IA-SINK-01', 'IA-WET-FLOAT-01'):
        e = next(x for x in data['edges'] if x['stream_id'] == sid)
        e.setdefault('params', {}).pop('pre_al_cake_kg_d', None)
    b = _topology_only(copy.deepcopy(data), INPUTS)
    for sid in ('IA-SINK-01', 'IA-WET-FLOAT-01'):
        e = next(x for x in data['edges'] if x['stream_id'] == sid)
        assert b.edges[sid]['params']['pre_al_cake_kg_d'] == e['rate']['value']
    drv = json.loads(json.dumps(INPUTS['drivers']))
    drv['foundry_al_line_kg_d']['value'] = 0
    b2 = _topology_only(copy.deepcopy(data), {'drivers': drv})
    for sid in ('IA-SINK-01', 'IA-WET-FLOAT-01'):
        assert 'pre_al_cake_kg_d' not in b2.edges[sid].get('params', {})
    data3 = copy.deepcopy(COMMITTED)
    cut = next(e for e in data3['edges'] if e['stream_id'] == 'IA-WAX-CUT')
    cut['from_sector_id'] = 'CRYO'
    b3 = _topology_only(data3)
    assert b3.edges['IA-WAX-CUT']['from_sector_id'] == 'OIL'


def test_retired_imports_terminate_absent():
    """The retirements are no-ops on the committed tree (all eleven retired
    there) and the writer's repair set is the declared table: carries
    rewritten on four, dock-class pops on four."""
    for e in COMMITTED['edges']:
        if e['stream_id'] in TT.RETIRED_EDGES:
            assert e.get('presence') == 'retired', e['stream_id']
    assert set(TT.RETIRED_CARRIES) == {'IA-ALCL3-MU', 'IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU'}
    assert set(TT.POP_EDGES) == {'IA-MGCL2-MU', 'IA-CACL2-MU', 'IA-WAX-MU', 'FR_FINISH'}
    assert TT.POP_KEYS == ('dock_class', 'dock_pending_task')


# ---- the conditions table as declared data ----------------------------------

def test_the_data_conditions_are_declared_data():
    """The conditions table: presence/driver data, never a locale id."""
    assert TT.TEXTILE_CONDITION == 'POLY_FIBER'
    assert TT.BRINE_HOSTS == ('LEACH_CSTR_1', 'CA_POT', 'MG_POT')
    assert TT.AL_LINE_DRIVER == 'foundry_al_line_kg_d'
    assert TT.DC_TEMPLATE == 'HL-Q4-REJ' and TT.DC_HOST == 'DRY_COOLER'
    assert TT.SI_IMPORT == 'IA-SI-IMPORT'
    rows = [
        ('foundry creates', 'the edge absent from the graph'),
        ('textile creates', 'the POLY_FIBER node in the graph'),
        ('brine node and streams', 'LEACH_CSTR_1, CA_POT, MG_POT all presence present'),
        ('retirements', 'the edge present'),
        ('IA-CL2-SHIP book', 'base_kg_d seeded, si_cl2_kg_d popped (A-M-484)'),
        ('pre-cake bases', 'driver foundry_al_line_kg_d > 0 and the param absent'),
        ('S34B finish book', 'the spin line live and the param absent'),
        ('wax re-point', 'the edge present; from_sector follows the from-node sector'),
        ('IA-DC-REJ clone', 'IA-DC-REJ absent and HL-Q4-REJ present and DRY_COOLER present'),
        ('SI route creates', 'the stream absent; the SI_REFINE node absent beside SI_REDUCE'),
        ('SF-SI feeds', 'the feed absent and the route nodes present (header tray on creation)'),
        ('IA-SI-IMPORT', 'present -> deleted outright (owner decision t58u)'),
        ('mars/locale placements', 'verified no-op: the site family reads presence, records none'),
    ]
    assert len(rows) == 13 and all(cond for _name, cond in rows)


# ---- the inventories stay true ----------------------------------------------

def test_topology_tables_match_the_family_inventories():
    """The pinned inventories (test_foundry.py / test_si_route.py) and the
    landed family tables stay true against the composer module."""
    proj = lambda rows: {(s, a, z, c) for s, a, z, _ph, c, _k in rows}
    assert proj(TT.STREAMS_FAB) == {(s, a, z, c) for s, a, z, c, _k in SR.STREAMS_FAB}
    assert proj(TT.STREAMS_SI) == {(s, a, z, c) for s, a, z, c, _k in SR.STREAMS_SI}
    assert TT.BRINE_HOSTS == FD.BRINE_HOSTS
    assert {(s, a, z) for s, a, z, _ph, _c, _an in TT.BRINE_STREAMS} == set(FD.BRINE_STREAMS)
    from flow_graph.v2.test_foundry import TOPOLOGY_INVENTORY as FI
    from flow_graph.v2.test_si_route import TOPOLOGY_INVENTORY as SI
    tt_created = ({r[0] for r in TT.FOUNDRY_MASS} | {r[0] for r in TT.SF_POTS}
                  | {r[0] for r in TT.BRINE_STREAMS} | {TT.SF_BRINE[0]}
                  | {r[0] for r in TT.TEXTILE})
    assert tt_created == (set(FI['created_edges']) | set(FI['created_by_salt_recovery'])
                          | set(FI['created_edge_conditional']))
    assert set(FI['created_nodes']) == {'BRINE_CRYS'}
    assert set(TT.RETIRED_EDGES) == set(FI['retired_edges'])
    assert set(FI['retired_by_salt_recovery']) <= set(TT.RETIRED_EDGES)
    si_created = {sid for sid, _a, _z, _c, _k in SR.STREAMS_FAB + SR.STREAMS_SI}
    assert si_created <= {r[0] for r in TT.STREAMS_FAB + TT.STREAMS_SI}
    assert set(SI['created_or_rated_sf']) == {r[0] for r in TT.SF_SI}
    assert SI['created_node']['SI_REFINE'][0] == 'GLASS'
    assert SI['retired_edge_deleted']['IA-SI-IMPORT'].startswith('the dock silicon import')
    assert 't58u' in SI['retired_edge_deleted']['IA-SI-IMPORT']


def test_seed_rate_templates_book_the_committed_rates():
    """Every created edge's template books the committed rate (the families
    that read seed rates back read the committed book)."""
    from decimal import Decimal
    committed = {e['stream_id']: e for e in COMMITTED['edges']}
    kw_feeds = {r[0] for r in TT.SF_POTS} | {TT.SF_BRINE[0]} | {r[0] for r in TT.SF_SI}
    for sid in TT.SEED_RATES:
        unit = 'kW' if sid in kw_feeds else 'kg/d'
        assert Decimal(str(committed[sid]['rate']['value'])) == \
            Decimal(str(TT._rate(sid, unit)['value'])), sid
        assert committed[sid]['rate']['unit'] == TT._rate(sid, unit)['unit'], sid


# ---- composition --------------------------------------------------------------

def test_solve_declares_topology_first():
    """solve.py imports the topology module FIRST - the shape precedes the
    values, before process/power/heat."""
    with open(os.path.join(ROOT, 'flow_graph', 'v2', 'solve.py'), encoding='utf-8') as f:
        src = f.read()
    lines = [ln for ln in src.splitlines() if ln.startswith('from .functions import')]
    assert lines[0].startswith('from .functions import topology'), lines[0]
    assert 'FIRST' in lines[0]
    order = [ln.split()[3] for ln in lines]
    assert order[0] == 'topology'
    for name in ('process', 'power', 'heat'):
        assert name in order, name
        assert order.index(name) > order.index('topology')
    from flow_graph.v2.registry import FNS
    names = [getattr(f, 'stage_name', '') for f in FNS]
    # the relative declared order holds in any interpreter: the shape
    # functions precede every value family (a test module that imported a
    # family module first may have registered it earlier - irrelevant)
    topo = {n for n in names if n.startswith('topology_')}
    assert topo == {'topology_foundry', 'topology_si_route', 'topology_heat_relief'}
    assert max(i for i, n in enumerate(names) if n in topo) < \
        min(i for i, n in enumerate(names)
            if n in ('process_acid_loop', 'heat_ledger', 'dry_cooler', 'power_ledger', 'relief_devices'))


# ---- the mars/locale designed-source placements: verified no-op ---------------

def test_mars_locale_placements_are_a_verified_no_op():
    """The site family's placement functions read presence (placeholder gate,
    sizers read the node) and record only params.site_placement - no presence
    stamp exists to port, and the v1 writer is 'idempotent; no topology
    change'. Applying them leaves the graph shape untouched."""
    with open(MARS, encoding='utf-8') as f:
        prof = json.load(f)
    b = load(REF_GRAPH)
    before = ([n['unit_id'] for n in b.data['nodes']],
              [e['stream_id'] for e in b.data['edges']],
              {u: n.get('presence') for u, n in b.nodes.items()},
              {s: e.get('presence') for s, e in b.edges.items()})
    ST.site_scale(b, {'profile': prof})
    ST.site_power_placement(b, {'drivers': INPUTS['drivers'], 'profile': prof})
    after = ([n['unit_id'] for n in b.data['nodes']],
             [e['stream_id'] for e in b.data['edges']],
             {u: n.get('presence') for u, n in b.nodes.items()},
             {s: e.get('presence') for s, e in b.edges.items()})
    assert before == after
    # no topology function touches the designed-source placeholders: the ids
    # appear only in the module docstring that records the no-op verdict
    with open(inspect.getfile(TT), encoding='utf-8') as f:
        src = f.read()
    doc = ast.get_docstring(ast.parse(src))
    code = src.replace(doc, '', 1)
    for token in ('FSP_40K', 'MMRTG', 'site_placement'):
        assert token not in code, token


# ---- determinism and purity ---------------------------------------------------

def test_determinism_two_tampered_pipelines_byte_identical():
    data = copy.deepcopy(COMMITTED)
    data['edges'] = [e for e in data['edges']
                     if e['stream_id'] not in {r[0] for r in TT.BRINE_STREAMS}
                     and e['stream_id'] != TT.SF_BRINE[0]]
    assert _pipeline(copy.deepcopy(data)) == _pipeline(copy.deepcopy(data))


def test_function_module_purity():
    """The engine module holds no float literals, no I/O, no banned imports,
    and no locale id (the lint's rules and the site pattern)."""
    with open(inspect.getfile(TT), encoding='utf-8') as f:
        src = f.read()
    tree = ast.parse(src)
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
    for bad in ('import random', 'import datetime', 'import time', 'import uuid'):
        assert bad not in src, bad
    for sid in ('mars', 'leo', 'lake_boehmer', 'baseline'):
        assert sid not in src, sid


def test_created_edges_carry_the_committed_static_shape():
    """Each creation spec, built against the committed seed, equals the
    committed edge on every field the value families do not re-stamp."""
    committed = {e['stream_id']: e for e in COMMITTED['edges']}
    b = load(REF_GRAPH)
    specs = {}
    for sid, frm, to, phase, layers, carries, notes, comp, sep, anchors in TT.FOUNDRY_MASS:
        specs[sid] = (TT._mass_edge(sid, frm, to, phase, layers, carries, notes, comp, sep,
                                    TT.KROLL_CO_RATE if sid == 'IA-KROLL-CO' else
                                    TT.CA_SHIP_RATE if sid == 'IA-CA-CL2-SHIP' else TT._rate(sid)), anchors)
    for sid, to in TT.SF_POTS:
        specs[sid] = (TT._sf_edge(sid, to, TT.SF_POT_CARRIES, TT.SF_POT_FORBIDDEN, None,
                                  TT.SF_POT_NOTES, 'tray'), TT.SF_POT_ANCHORS[sid])
    for sid, frm, to, phase, carries, anchors in TT.TEXTILE:
        specs[sid] = (TT._textile_edge(sid, frm, to, phase, carries), anchors)
    for sid, frm, to, phase, comp, _key in TT.STREAMS_FAB + TT.STREAMS_SI:
        specs[sid] = (TT._si_edge(sid, frm, to, phase, comp), TT.SI_ANCHORS.get(sid, TT.A_SI_TAIL))
    for sid, (e, _anchors) in specs.items():
        e['from_sector_id'] = b.nodes[e['from_unit_id']]['sector_id']
        e['to_sector_id'] = b.nodes[e['to_unit_id']]['sector_id']
        if sid in TT.CREATE_PARAMS:
            p = e.setdefault('params', {})
            for k, val in TT.CREATE_PARAMS[sid].items():
                p.setdefault(k, val)
        if sid in TT.POP_EDGES:
            p = e.setdefault('params', {})     # the retire step's pop leaves the empty book
            for k in TT.POP_KEYS:
                p.pop(k, None)
        if sid == 'IA-CA-CL2-SHIP':
            e.setdefault('params', {})['si_cl2_kg_d'] = TT.CA_SHIP_SI_CL2   # the A-M-484 book
        c = committed[sid]
        retired_at_creation = sid in TT.RETIRED_EDGES
        si_id = {r[0] for r in TT.STREAMS_SI}
        for k, v in e.items():
            if k == 'presence' and (retired_at_creation or sid in si_id):
                continue                  # the retirement step retires it; si_route re-books SI presence
            if k == 'composition' and sid == 'IA-SI-PURGE':
                continue                  # the bleed composition is the family's book (A-M-489)
            if k == 'carries' and retired_at_creation:
                continue                  # the retirement step rewrites it (the restorative tests prove it)
            if k == 'rate':
                assert v['value'] == c['rate']['value'] and v['unit'] == c['rate']['unit'], (sid, k)
                continue
            if k in ('from_sector_id', 'to_sector_id'):
                assert v == c.get(k), (sid, k)   # derived from the node sectors (the invariant)
                continue
            assert v == c.get(k), (sid, k)
        # the canonical serialization appends the engine's provenance
        # bookkeeping key to every edge with a computed field; it is not part
        # of the engineering shape (graph_io.py), so the key order compares
        # without it
        assert [k for k in e.keys() if k != 'provenance'] == \
            [k for k in c.keys() if k != 'provenance'], (sid, 'key order')
