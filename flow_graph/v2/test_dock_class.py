"""engine v2: the dock-class family acceptance (the golden-value proof and the
recovery-records coverage verdict).

Reference writer: flow_graph/param/recovery.py command `--stamp`, ledger row
`dock_class` (section B, MIXED - split recovery solve -> function, the
TASK_PLAN gate dies as bookkeeping). The proofs:

- exact change set: the family's overlay equals the hand-enumerated
  specification (eight live dock inputs' params.dock_class), and a strict
  whole-model walk proves nothing else moved - the retired imports keep their
  committed classes untouched (IA-ALCL3-MU's 'pending' residue among them),
  and the unclassifiable dock inputs (IA-AIR-IN at 0.0, the export
  placeholder) stay outside the census exactly as the reference writer's
  liveness rule leaves them;
- golden equality: every stamped class equals the committed golden verbatim;
- the table spot-checks: the ore/water/pending classification, the liveness
  rule, the None class for a table-miss (the gate flags it);
- the coverage verdict (the row's split decision): the committed
  params.recovery records are each transfer function's own stamps. The
  foundry family reproduces the foundry/polymers records it owns (verified
  here against the committed golden, field by field) and the si_route family
  the silicon-loop records (its own test holds that golden). The remaining
  committed records belong to families that have not landed; the ownership
  table is asserted as data. The dock-class row is therefore covered by the
  stamp port in this family plus the landed record families - the
  TASK_PLAN done-checkbox gate dies as bookkeeping;
- the bridge class: the census reads only the seed, so the family records
  regardless of the payload (asserted);
- determinism: two runs, byte-identical;
- grid purity: no float literals, no I/O in the module.
"""
import ast
import inspect
import json
import os
from decimal import Decimal

from flow_graph.v2.functions import dock_class as DK
from flow_graph.v2.functions import foundry as FD
from flow_graph.v2.graph_io import bytes as render, load

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
INPUTS = {'drivers': json.load(open(DRIVERS))}

LIVE_DOCK = ('IA-CAF2-MU', 'IA-CR2O3-MU', 'IA-FEED-MU', 'IA-H2O-MU',
             'IA-HALITE-MU', 'IA-MOO3-MU', 'IA-SULFUR-MU', 'IA-TIO2-MU')
EXPECTED_EDGE_FIELDS = [(sid, 'params.dock_class') for sid in LIVE_DOCK]

# the committed params.recovery records and the family that owns each (the
# landed record families reproduce theirs; the rest wait on their migration
# rows). The recovery --stamp stage writes none of them - the census note
# "stamps params.recovery" describes the TFs' books the stage consumes.
RECORD_OWNERS = {
    'HOPPER': 'foundry (landed: flow_graph/v2/functions/foundry.py _fe_record, A-M-499)',
    'SHELL_BUILD': 'foundry (landed: _si_record, F-20261110-06)',
    'TI_CELL': 'foundry (landed: _ore_record, A-M-284)',
    'MO_CELL': 'foundry (landed: _ore_record, A-M-284)',
    'CR_CELL': 'foundry (landed: _ore_record, A-M-284)',
    'SI_REDUCE': 'si_route (landed: flow_graph/v2/functions/si_route.py, A-M-472)',
    'SI_REFINE': 'si_route (landed, A-M-484)',
    'HF_GEN': 'fluoro_train (ledger row C, not landed)',
    'GREASE_CA': 'the grease lanes (specialty/fluoro own the GREASE_* stamps; power.grease_route records nothing)',
    'P_CA': 'the grease lanes (specialty/fluoro own the GREASE_* stamps)',
    'NAOH_PLANT': 'caustic (flow_graph/param/caustic.py TF, not landed)',
    'SOLV_PLANT': 'the solvent family (A-M-479, not landed)',
    'ACID_PLANT': 'the acid lane (not landed)',
    'RESIST_SYN': 'the fab-resist lane (flow_graph/param/fab_resist.py, A-M-482, not landed)',
}


def run():
    b = load(REF_GRAPH)
    DK.dock_class(b, INPUTS)
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
    assert got_nodes == []
    assert got_edges == sorted(EXPECTED_EDGE_FIELDS)

    for sid, path in EXPECTED_EDGE_FIELDS:
        assert _eq(_dig(c_edges[sid], path), _dig(r_edges[sid], path)), (sid, path)

    node_diffs = set()
    for uid in sorted(set(c_nodes) | set(r_nodes)):
        _strict_diffs(c_nodes[uid], r_nodes[uid], uid, node_diffs, set())
    assert node_diffs == set(), sorted(node_diffs)
    expected_edge_paths = {sid + '.' + path for sid, path in EXPECTED_EDGE_FIELDS}
    edge_diffs = set()
    for sid in sorted(set(c_edges) | set(r_edges)):
        _strict_diffs(c_edges[sid], r_edges[sid], sid, edge_diffs, expected_edge_paths)
    assert edge_diffs == set(), sorted(edge_diffs)


def test_classification_tables():
    """The stamp rule, spot-checked: the ore table, the water make-up, the
    liveness rule, the table-miss class."""
    assert DK.classify('IA-CAF2-MU') == 'raw_ore'
    assert DK.classify('IA-FEED-MU') == 'raw_ore'                  # A-M-499 raw-feed class
    assert DK.classify('IA-H2O-MU') == 'water'
    assert DK.classify('IA-AIR-IN') is None                        # no class: the gate flags it
    assert DK.classify('IA-ALCL3-MU') is None                      # off every table (X-QA-11 retired the
                                                                   # import; its stamps are committed residue)
    # the liveness rule keeps retired and non-positive edges outside the census
    seed = load(REF_GRAPH)
    assert not DK._live(seed.edges['IA-ALCL3-MU'])                 # retired: keeps its 'pending' residue
    assert not DK._live(seed.edges['IA-AIR-IN'])                   # 0.0 kg/d: outside the census
    assert not DK._live(seed.edges['DOCK_EXPORT_TBD'])             # placeholder, 0.0
    # the committed residue the family must not touch
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = {e['stream_id']: e for e in json.load(f)['edges']}
    assert committed['IA-ALCL3-MU']['params']['dock_class'] == 'pending'
    assert 'dock_class' not in (committed['IA-AIR-IN'].get('params') or {})
    # every live dock input classifies (the empty pending/waste tables, X-QA-11)
    assert DK.PENDING == {} and DK.WASTE_IN == {}
    for sid in LIVE_DOCK:
        assert DK.classify(sid) in ('raw_ore', 'water'), sid


def test_coverage_verdict_foundry_records_reproduced():
    """The coverage verdict, verified: the foundry family's fresh recovery
    records equal the committed golden field by field (the AW/ORE tables
    ported there), so the foundry share of the committed params.recovery books
    is covered. The remaining records' owners are the landed si_route family
    and the not-yet-landed rows in the ownership table."""
    b = load(REF_GRAPH)
    FD.foundry_poly(b, INPUTS)
    with open(REF_GRAPH, encoding='utf-8') as f:
        committed = {n['unit_id']: n for n in json.load(f)['nodes']}
    for uid in ('SHELL_BUILD', 'TI_CELL', 'MO_CELL', 'CR_CELL', 'HOPPER'):
        fresh = b.computed[('node', uid, 'params.recovery')][0]
        assert _eq(committed[uid]['params']['recovery'], fresh), uid
    # the ownership table covers every committed record exactly
    with open(REF_GRAPH, encoding='utf-8') as f:
        record_units = sorted(n['unit_id'] for n in json.load(f)['nodes']
                              if (n.get('params') or {}).get('recovery'))
    assert sorted(RECORD_OWNERS) == record_units, (
        sorted(set(RECORD_OWNERS) ^ set(record_units)))
    landed = ('HOPPER', 'SHELL_BUILD', 'TI_CELL', 'MO_CELL', 'CR_CELL', 'SI_REDUCE', 'SI_REFINE')
    assert all('landed' in RECORD_OWNERS[u] for u in landed)


def test_seed_only_bridge_class():
    """The census reads only the seed: the family records with any payload,
    including none (the pot-cell geometry precedent)."""
    for payloads in ({}, {'drivers': INPUTS['drivers']}):
        b = load(REF_GRAPH)
        DK.dock_class(b, payloads)
        assert sorted((k[1], k[2]) for k in b.computed) == sorted(EXPECTED_EDGE_FIELDS)


def test_provenance_rows():
    b = run()
    for (_kind, _sid, _path), (_value, prov) in b.computed.items():
        assert prov.stage == 'dock_class' and prov.basis


def test_determinism_two_runs_byte_identical():
    assert render(run()) == render(run())


def test_function_module_grid_purity():
    """The engine module holds no float literals and no I/O (the lint's rule)."""
    tree = ast.parse(inspect.getsource(DK))
    floats = [n.lineno for n in ast.walk(tree)
              if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    opens = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open']
    assert floats == [] and opens == []
