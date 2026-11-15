"""Golden proof for the migrated section-3 material-selection family (engine v2;
reference writer flow_graph/param/materials3.py).

- every roster unit's computed params.sec3_material equals the committed graph
  value exactly (the issued selections are reproduced, not re-derived);
- the two units the roster gate held open (BRINE_CRYS, NUT_AN) now carry issued
  selections with an AQS-STD-002 clause basis;
- the render diff against the committed graph is exactly the enumerated set:
  params.sec3_material on the two newly selected units plus a node-level
  provenance list on every stamped unit - nothing else changes.
"""
import json, os

from flow_graph.v2.functions import materials3 as M3
from flow_graph.v2.graph_io import bytes as render, load

REF_GRAPH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                         'flow_graph', 'plant_flow_graph.json')
PENDING = ('BRINE_CRYS', 'NUT_AN')
FIELD = 'sec3_material'
PATH = 'params.' + FIELD
MISSING = object()


def _run(inputs=None):
    with open(REF_GRAPH, 'rb') as f:
        committed_bytes = f.read()
    committed = json.loads(committed_bytes)
    b = load(REF_GRAPH)
    M3.sec3_material_selections(b, inputs or {})
    out = json.loads(render(b))
    return committed, b, out


def _stamps(b):
    return {uid: (val, prov) for (kind, uid, path), (val, prov) in b.computed.items()
            if kind == 'node' and path == PATH}


def test_golden_equality_on_committed_graph():
    committed, b, _ = _run()
    committed_sel = {n['unit_id']: n['params'][FIELD]
                     for n in committed['nodes'] if (n.get('params') or {}).get(FIELD)}
    stamps = _stamps(b)
    # every issued roster selection is reproduced exactly
    for uid, want in committed_sel.items():
        assert uid in stamps, f'{uid}: roster selection not stamped'
        val, prov = stamps[uid]
        assert val == want, f'{uid}: computed selection differs from the committed graph'
    # the roster set plus the two pending units is exactly the stamped set
    assert set(stamps) == set(committed_sel) | set(PENDING)
    # every stamp is a full selection record with the standard citation
    for uid, (val, prov) in stamps.items():
        assert set(val) == {'mat', 'basis', 'alt', 'note', 'task'}, uid
        assert all(val.values()), uid
        assert prov.stage == 'sec3_material_selections', uid
        assert prov.ref == 'AQS-STD-002' and prov.basis, uid
    # the provenance basis is the row clause, per row of the declared table
    clause = {r['unit']: r['clause'] for r in M3.SELECTION_TABLE}
    for uid, (_, prov) in stamps.items():
        assert prov.basis == clause[uid], uid
    # the two pending selections are issued, not pending, and name their service class
    for uid in PENDING:
        val, prov = stamps[uid]
        assert 'pending' not in (val['mat'] + val['basis']).lower(), uid
        marks = ('M2', 'M3') if uid == 'BRINE_CRYS' else ('M7', 'M3')
        assert all(m in prov.basis for m in marks), (uid, prov.basis)


def test_render_diff_is_exactly_the_enumerated_set():
    committed, b, out = _run()
    assert all('provenance' not in n for n in committed['nodes'])
    assert all('provenance' not in e for e in committed['edges'])
    stamped = set(_stamps(b))

    diffs = []

    def walk(old, new, path):
        if old == new:
            return
        if isinstance(old, dict) and isinstance(new, dict):
            for k in set(old) | set(new):
                walk(old.get(k, MISSING), new.get(k, MISSING), f'{path}.{k}')
        elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
            for i, (a, x) in enumerate(zip(old, new)):
                walk(a, x, f'{path}[{i}]')
        else:
            diffs.append(path)

    assert sorted(out) == sorted(committed)
    for k, v in committed.items():
        if k == 'nodes':
            continue
        walk(v, out[k], k)                       # edges, sectors, ... untouched
    cn = {n['unit_id']: n for n in committed['nodes']}
    on = {n['unit_id']: n for n in out['nodes']}
    assert sorted(cn) == sorted(on)
    for uid in cn:
        walk(cn[uid], on[uid], f'nodes[{uid}]')

    expected = {f'nodes[{uid}].provenance' for uid in stamped} | \
               {f'nodes[{uid}].{PATH}' for uid in PENDING}
    assert sorted(diffs) == sorted(expected), \
        (sorted(set(diffs) - expected), sorted(set(expected) - diffs))

    # each provenance list is exactly the family's row for that unit
    clause = {r['unit']: r['clause'] for r in M3.SELECTION_TABLE}
    for uid in stamped:
        assert on[uid]['provenance'] == [
            {'stage': 'sec3_material_selections', 'basis': clause[uid],
             'ref': 'AQS-STD-002', 'field': PATH}], uid
    # the two newly selected units carry the issued dict; every other stamped
    # unit renders the identical value it already carried
    for uid in PENDING:
        assert on[uid]['params'][FIELD] == _stamps(b)[uid][0]
    for uid, want in {n['unit_id']: n['params'][FIELD] for n in committed['nodes']
                      if (n.get('params') or {}).get(FIELD)}.items():
        assert on[uid]['params'][FIELD] == want


def test_table_is_the_roster_and_the_family_is_deterministic():
    committed, _, _ = _run()
    unit_ids = {n['unit_id'] for n in committed['nodes']}
    units = [r['unit'] for r in M3.SELECTION_TABLE]
    assert len(units) == len(set(units))              # one row per unit
    assert set(units) <= unit_ids                     # every row lands on a live unit
    assert set(PENDING) <= set(units)                 # the pending pair is issued here
    for r in M3.SELECTION_TABLE:
        assert all(r[k] for k in ('unit', 'dimension', 'clause', 'mat', 'basis', 'alt',
                                  'note', 'task'))
    # same inputs -> byte-identical serialization, and the table read ignores inputs
    r1 = render(_run()[1])
    r2 = render(_run({'site': 'variant', 'rows': 7})[1])
    assert r1 == r2
