"""engine v2: the storage-sizing family acceptance (the golden-value proof).

Reference writer: docs-authority/_storage_sizing.py, ledger row `storage_sizing`
(section B, MIXED - split sizing -> function, the STORAGE_HOLDUP.md page and
the inventory/STORAGE_HOLDUP.json sidecar -> the renderer wave). The committed
graph carries every field the family stamps; the proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (23 units x {params.size_mm, params.size_note,
  params.design_storage}), and a strict whole-model walk proves nothing else
  moved;
- golden equality: 53 of the 69 changed fields equal the committed golden
  exactly; the 16 enumerated residue fields are pinned by the deviation table
  below;
- the deviation table, two classes with owners:
  * the four buffer books (METAL_STORE, AIR_RECEIVER, PROD_O2, PROD_MEOH)
    lag the seed rates their Q draws on: the v1 lattice ran this stage before
    the writers that re-rate STOCK_TO_MFG / IA-N2-VENT / IA-O2-PROD /
    IA-MEOH-PROD, so the committed stamps carry a mid-loop census (14.0 /
    3.1 / 22.8768 / 28.35 kg/d) while the seed carries the end-of-loop rates.
    The fresh v2 census is this stage's own book; both sides pinned exactly;
  * the nine FAB reagent-tank size_mm envelopes carry the CAD/GA
    style-builder wave's claimed geometry (the consolidated-lane regeneration
    overwrote 44 unit size_mm books after this stage); this function's own
    vessel book for each is [600, 600, 600];
- grid spot-checks on the integer books: the FOOD_STORE chain hand-computed
  end to end (Q 0.252 -> 350 x 450), the 50 mm vessel grid everywhere, the
  0.02 m3 nominal floor, the PROD_O2 steel wall at the 20 MPa working
  pressure;
- the bridge contract: no payloads, drivers-only or profile-only record
  nothing (the gravity comes from the site profile);
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O in the module.

Integer-scale table (the quantise at each stamp; half-even throughout, Python
round()'s tie rule): nominal volume 4 dp; wall 2 dp; bore, height and the
envelope faces integers (the 50 mm vessel grid and the +allowance driver);
hold_d is the driver passthrough the reference writer carries verbatim.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import storage_sizing as SS
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
INPUTS = {'drivers': json.load(open(DRIVERS)), 'site_profile': json.load(open(PROFILE))}

UNITS = sorted(SS.B)
EXPECTED_FIELDS = [(u, f) for u in UNITS for f in
                   ('params.size_mm', 'params.size_note', 'params.design_storage')]
# the enumerated residue (see module docstring): the buffer Q-lag books and the
# style-builder-owned reagent-tank envelopes.
Q_LAG = ('METAL_STORE', 'AIR_RECEIVER', 'PROD_O2')
DEVIATED_FIELDS = ([(u, 'params.size_mm') for u in ('WS_AMMONIA', 'WS_DOPE', 'WS_HF_ED', 'WS_KOH',
                                                    'WS_NITRIC', 'WS_PEROX', 'WS_SLURRY', 'WS_SOLV', 'WS_PHOS')]
                   + [(u, 'params.size_mm') for u in Q_LAG]
                   + [(u, 'params.design_storage') for u in Q_LAG + ('PROD_MEOH',)])


def run():
    b = load(REF_GRAPH)
    SS.storage_sizing(b, INPUTS)
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
    the expected change set: strict everywhere except the enumerated fields.
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
    assert got_edges == []

    deviated = set(DEVIATED_FIELDS)
    for uid, path in EXPECTED_FIELDS:
        if (uid, path) in deviated:
            continue
        assert _eq(_dig(c_nodes[uid], path), _dig(r_nodes[uid], path)), (uid, path)

    expected_paths = {uid + '.' + path for uid, path in EXPECTED_FIELDS}
    diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, diffs, expected_paths)
    assert diffs == {uid + '.' + path for uid, path in DEVIATED_FIELDS}, sorted(diffs)
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, set())
    assert edge_diffs == set(), sorted(edge_diffs)


def test_deviation_table():
    """The 16 residue fields pinned exactly, both sides: the four buffer books
    at the stage's own census (fresh) and the committed mid-loop census (with
    the exact Q each implies), and the nine reagent-tank envelopes at the
    style-builder wave's claimed geometry."""
    b = run()
    fresh = {uid: b.computed[('node', uid, 'params.design_storage')][0] for uid in SS.B}
    with open(REF_GRAPH, encoding='utf-8') as f:
        gold = {n['unit_id']: n for n in json.load(f)['nodes']}
    # METAL_STORE: committed Q 14.0 kg/d (the foundry stock book before the
    # X-MFG-30 resize); fresh Q 23.4217 kg/d off the seed draws. 14 d at the
    # 2000 kg/m3 staged-metal density, fill 0.8.
    assert gold['METAL_STORE']['params']['design_storage']['V_nom_m3'] == 0.1225
    assert fresh['METAL_STORE']['V_nom_m3'] == 0.2049
    q_gold = Decimal('0.1225') * Decimal('0.8') * 2000 / 14        # V_nom x fill x rho / hold
    assert q_gold == Decimal('14')
    assert SS.rat('22.0072') + SS.rat('1.414504') == SS.rat('23.421704')
    # AIR_RECEIVER: committed Q 3.1 kg/d (the A-M-273 N2 surplus export at the
    # e348e62e6 census); fresh Q 17.4029 kg/d off the seed vent rate.
    assert gold['AIR_RECEIVER']['params']['design_storage']['V_nom_m3'] == 0.3312
    assert gold['AIR_RECEIVER']['params']['design_storage']['wall_mm'] == 3.06
    assert fresh['AIR_RECEIVER']['V_nom_m3'] == 1.8593 and fresh['AIR_RECEIVER']['wall_mm'] == 5.24
    assert (Decimal('0.3312') * Decimal('0.8') * Decimal('11.7')).quantize(Decimal('0.0001')) == Decimal('3.1000')
    # PROD_O2: committed Q 22.8768 kg/d; fresh 12.7345 kg/d; steel at 20 MPa,
    # wall = P x R / (S - 0.6 P): gold R 550 mm -> 106.80, fresh R 450 -> 87.38.
    assert gold['PROD_O2']['params']['design_storage']['V_nom_m3'] == 1.3645
    assert gold['PROD_O2']['params']['design_storage']['wall_mm'] == 106.8
    assert fresh['PROD_O2']['V_nom_m3'] == 0.7596 and fresh['PROD_O2']['wall_mm'] == 87.38
    assert (Decimal('20') * 550 / (Decimal('115') - Decimal('12'))).quantize(Decimal('0.01')) == Decimal('106.80')
    assert (Decimal('20') * 450 / (Decimal('115') - Decimal('12'))).quantize(Decimal('0.01')) == Decimal('87.38')
    # PROD_MEOH: the fresh Q 28.5784 vs the committed 28.35; D/H quantise equal.
    assert gold['PROD_MEOH']['params']['design_storage']['V_nom_m3'] == 0.6267
    assert fresh['PROD_MEOH']['V_nom_m3'] == 0.6315
    assert fresh['PROD_MEOH']['D_mm'] == 850 and fresh['PROD_MEOH']['H_mm'] == 1150
    # the nine reagent tanks: the storage book is the vessel envelope; the
    # committed carry the style-builder wave's geometry.
    for u in ('WS_AMMONIA', 'WS_DOPE', 'WS_HF_ED', 'WS_KOH', 'WS_NITRIC', 'WS_PEROX',
              'WS_SLURRY', 'WS_SOLV', 'WS_PHOS'):
        own = b.computed[('node', u, 'params.size_mm')][0]
        assert own == [600, 600, 600], (u, own)
        assert gold[u]['params']['size_mm'] == [600, 600, 350], u
        # the design books agree everywhere (the floor governs)
        assert _eq(gold[u]['params']['design_storage'], fresh[u]), u


def test_grid_spot_checks():
    """The FOOD_STORE chain hand-computed end to end; the grid and floor
    rules; the wall classes."""
    b = run()
    fs = b.computed[('node', 'FOOD_STORE', 'params.design_storage')][0]
    # Q = S14 4.2 kg/d x 6 % DM = 0.252; 80 d at 600 kg/m3 = 0.0336 working;
    # / 0.8 fill = 0.042 nominal -> D 350 x H 450 on the 50 mm grid.
    assert SS.rat('4.2') * SS.rat('0.06') == SS.rat('0.252')
    assert SS.rat('0.252') * 80 / 600 / SS.rat('0.8') == SS.rat('0.042')
    assert fs == {'hold_d': 80, 'V_nom_m3': 0.042, 'D_mm': 350, 'H_mm': 450,
                  'wall_mm': 4.75, 'material': 'PE (rotomoulded / fabricated)'}
    sz = b.computed[('node', 'FOOD_STORE', 'params.size_mm')][0]
    assert sz == [650, 650, 750]                                   # +300 allowance on every face
    for uid in SS.B:
        row = b.computed[('node', uid, 'params.design_storage')][0]
        assert row['D_mm'] % 50 == 0 and row['H_mm'] % 50 == 0, uid
        assert b.computed[('node', uid, 'params.size_mm')][0] == \
            [row['D_mm'] + 300, row['D_mm'] + 300, row['H_mm'] + 300], uid
    # the 0.02 m3 floor governs wherever Q books 0 at the seed (no duty sheet
    # on the graph yet, no design capacity): the 300 x 300 class
    for uid in ('MEOH_TANK', 'WS_KOH', 'HOPPER', 'NUTRIENT_DOSE'):
        row = b.computed[('node', uid, 'params.design_storage')][0]
        assert row['V_nom_m3'] == 0.02 and row['D_mm'] == 300 and row['H_mm'] == 300, uid
    # material classes: flammables and compressed gas are welded 304L
    assert b.computed[('node', 'MEOH_TANK', 'params.design_storage')][0]['material'] == 'SA-240 304L, welded'
    assert b.computed[('node', 'PROD_O2', 'params.design_storage')][0]['material'] == 'SA-240 304L, welded'
    assert b.computed[('node', 'WS_KOH', 'params.design_storage')][0]['material'] == 'PE (rotomoulded / fabricated)'


def test_bridge_contract():
    """No payloads, drivers-only or profile-only record nothing (the bridge
    contract: the solve needs both the drivers and the site profile)."""
    for payloads in ({}, {'drivers': INPUTS['drivers']}, {'site_profile': INPUTS['site_profile']}):
        b = load(REF_GRAPH)
        SS.storage_sizing(b, payloads)
        assert b.computed == {}


def test_provenance_rows():
    b = run()
    for (_kind, _uid, _path), (_value, prov) in b.computed.items():
        assert prov.stage == 'storage_sizing' and prov.basis


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(SS))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
