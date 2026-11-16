"""engine v2 core acceptance: the P1 proofs.

- determinism: identical inputs -> byte-identical serialization, always;
- byte-roundtrip: an untouched model reproduces the committed graph exactly
  (the strangler bridge: untouched fields round-trip verbatim);
- the grid is parametric data: changing the declared scales changes rendering,
  not code;
- the manifest is content-only and stable; the check fails closed.
"""
import json, os, shutil

import pytest

from flow_graph.v2 import check as CK
from flow_graph.v2 import lint as LT
from flow_graph.v2 import manifest as MF
from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import pot_cells as FN_POT
from flow_graph.v2.graph_io import bytes as render, load
from flow_graph.v2.grid import Grid, Qty

REF_GRAPH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                         'flow_graph', 'plant_flow_graph.json')


def test_grid_arithmetic_and_rounding():
    g = Grid.load()
    a = Qty(1500, 'mass_flow', g)
    b = Qty(250, 'mass_flow', g)
    assert (a + b).count == 1750 and (a - b).count == 1250
    assert (a * 3).count == 4500
    with pytest.raises(TypeError):
        a + Qty(1, 'power', g)
    with pytest.raises(TypeError):
        Qty(1.5, 'mass_flow', g)                      # floats never enter the model
    assert a.round_half_up(1000).count == 2          # 1500/1000 -> 2 (half up)
    assert Qty(1499, 'mass_flow', g).round_half_up(1000).count == 1
    assert a.display() == '1.5 kg/d'                 # exact decimal from the integer
    assert Qty(1, 'mass_flow', g).display() == '0.001 kg/d'


def test_grid_is_declared_data(tmp_path):
    spec = {'thing': {'grid_unit': 'u', 'display_unit': 'kU', 'per_display': 250}}
    p = tmp_path / 'grid.json'
    p.write_text(json.dumps(spec))
    g = Grid.load(str(p))
    assert Qty(500, 'thing', g).display() == '2 kU'   # the scale is data, not code
    with pytest.raises(KeyError):
        Qty(1, 'undeclared_dim', g)                   # an undeclared dimension fails loudly


def test_roundtrip_is_byte_exact():
    """An untouched model reproduces the committed graph bytes exactly — the bridge
    never drifts a field it has not migrated."""
    with open(REF_GRAPH, 'rb') as f:
        committed = f.read()
    assert render(load(REF_GRAPH)) == committed


def test_determinism_ten_renders_and_two_solves():
    b = load(REF_GRAPH)
    node = b.nodes['CA_POT']
    imm = node['params']['design']['anode_imm_mm']
    b.set_node_field('CA_POT', 'design.bath_top_mm', Qty(int(round(float(imm))) + 100, 'length'),
                     {'stage': 'test', 'basis': 'test arithmetic', 'ref': 'A-M-496'})
    renders = {render(b) for _ in range(10)}
    assert len(renders) == 1                          # one byte string, ten renders
    m1, m2 = b.build(), b.build()
    assert render(m1) == render(m2)
    outs = {render(SL.solve({}, REF_GRAPH)) for _ in range(2)}   # empty FNS: pure bridge solve
    assert len(outs) == 1


def test_exemplar_pot_cell_bath_top():
    """The first migrated function: the pot-cell bath top, grid-exact, provenance
    recorded at assignment."""
    b = load(REF_GRAPH)
    FN_POT.pot_cell_bath_top(b, {})
    m = b.build()
    got = m.computed[('node', 'CA_POT', 'design.bath_top_mm')]
    assert got[0].dim == 'length' and got[0].count == 350   # 250 mm immersion + 100 mm tips
    assert got[1].stage == 'pot_cell_bath_top' and got[1].ref == 'A-M-496'
    for uid, want in (('CA_POT', 350), ('CR_CELL', 350), ('MG_POT', 400), ('MO_CELL', 350)):
        assert m.computed[('node', uid, 'design.bath_top_mm')][0].count == want
    out = json.loads(render(m))
    n = next(n for n in out['nodes'] if n['unit_id'] == 'CA_POT')
    assert n['params']['design']['bath_top_mm'] == 350            # exact numeric, on the grid
    assert n['provenance'][0]['stage'] == 'pot_cell_bath_top'     # structured, not appended prose
    assert 'provenance' not in next(x for x in out['nodes'] if x['unit_id'] == 'MO_CELL') or \
        next(x for x in out['nodes'] if x['unit_id'] == 'MO_CELL')['provenance'][0]['stage'] == 'pot_cell_bath_top'


def test_manifest_content_only_and_stable():
    m1 = MF.build(SL.FNS)
    m2 = MF.build(SL.FNS)
    assert MF.dumps(m1) == MF.dumps(m2)               # no timestamps, sorted: byte-stable
    fps = dict(m1['functions'])
    assert len(set(fps.values())) == len(fps)         # distinct functions, distinct code
    assert 'flow_graph/v2/grid.json' in m1['inputs']
    assert all(len(v) == 64 for v in m1['inputs'].values())
    assert len(m1['code']) == 64                      # the package fingerprint


def test_lint_clean_and_detects(tmp_path):
    assert LT.run() == []                             # the engine as written is clean
    bad = tmp_path / 'bad.py'
    bad.write_text('import random\nimport datetime\nX = 1.5\nopen("x")\n')
    v = LT.run(str(tmp_path))
    assert any('random' in x for x in v) and any('datetime' in x for x in v)
    assert any('float literal' in x for x in v)
    assert any('outside the declared boundary' in x for x in v)


def test_check_cycle_fails_closed(tmp_path):
    """fresh after update; content-stale, code-stale, input-stale and missing-manifest
    each fail — abstentions never pass."""
    g = str(tmp_path / 'graph.json')
    m = str(tmp_path / 'manifest.json')
    # The sandbox is a miniature of the post-flip world: the committed graph is
    # the CANONICAL serialization (the composed solve's own render), so the
    # document authority hashes stay stable across the update -> check cycle.
    # (On the reference tree this shape arrives with the P4 re-issuance,
    # recorded in flow_graph/v2/MIGRATION_LEDGER.md.)
    from flow_graph.param import drivers as _DR
    import json as _json
    inputs = {'drivers': _DR.load(),
              'site_profile': _json.load(open('flow_graph/param/sites/baseline.json'))}
    from flow_graph.v2.graph_io import bytes as _render, load as _load
    from flow_graph.v2.grid import Grid as _Grid
    _b = _load(REF_GRAPH)
    for _f in SL.FNS:
        _f(_b, inputs)
    with open(g, 'wb') as _f:
        _f.write(_render(_b.build(), _Grid.load()))
    ok, lines = CK.update(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
    assert ok, lines
    ok, lines = CK.check(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
    assert ok and any('fresh' in x for x in lines)

    data = open(g, 'rb').read()
    open(g, 'wb').write(data.replace(b'"presence"', b'"presenze"', 1))
    ok, lines = CK.check(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
    assert not ok and any('stale (content)' in x for x in lines)
    open(g, 'wb').write(data)

    c = json.load(open(m))
    c['code'] = '0' * 64
    json.dump(c, open(m, 'w'))
    ok, lines = CK.check(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
    assert not ok and any('stale (code changed)' in x for x in lines)

    for p, sha in list(json.load(open(m))['inputs'].items())[:1]:
        c = json.load(open(m))
        c['inputs'][p] = '1' * 64
        json.dump(c, open(m, 'w'))
        ok, lines = CK.check(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
        assert not ok and any('stale (input changed)' in x for x in lines)
        break

    os.remove(m)
    ok, lines = CK.check(graph_path=g, manifest_path=m, inputs=inputs, artifact_root=str(tmp_path))
    assert not ok and any('no committed manifest' in x for x in lines)
