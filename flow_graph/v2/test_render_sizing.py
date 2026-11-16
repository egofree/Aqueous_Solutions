"""engine v2: the sizing-document renderer acceptance (byte-exact reproduction).

The renderer wave: flow_graph/v2/render/ (ledger section B, the doc half of
the eight MIXED sizing rows; the reference writers' doc-render sections in
flow_graph/param/{cold_box,evap_design,receivers,h2_compressor,h2_purifier,
house_scrubbers,upw_polish,geo_loop}.py). The golden is the committed document
file; the acceptance is byte-exact reproduction. The proofs:

- byte-exact: each of the eight documents renders from the model seeded from
  the committed graph and computed by the landed physics families (their
  functions, applied in the section B order), and equals the committed file
  bytes exactly;
- registry: the declared ordered list covers exactly the eight sizing
  documents, every output path exists, and render_one resolves each;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O in the render modules (no open(), no banned imports, no
  float literals - the render functions read the model and return bytes; file
  writing stays outside).
"""
import ast
import json
import os

import pytest

from flow_graph.v2.functions import cold_box as _cb
from flow_graph.v2.functions import evap_design as _ed
from flow_graph.v2.functions import geo_loop as _gl
from flow_graph.v2.functions import h2_compressor as _hc
from flow_graph.v2.functions import h2_purifier as _hp
from flow_graph.v2.functions import house_scrubbers as _hs
from flow_graph.v2.functions import receivers as _rcv
from flow_graph.v2.functions import upw_polish as _up
from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render, render_one
from flow_graph.v2 import render as _render_pkg

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}

# The model renders from the DECLARED composition (solve.py's registered
# functions, in the reference topo order): the strongest renderer acceptance is
# that the full composed solve reproduces every committed document byte.
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}

EXPECTED_PATHS = [
    'docs-authority/sizing/COLD_BOX.md',
    'docs-authority/sizing/EVAP_DESIGN.md',
    'docs-authority/sizing/GAS_RECEIVERS.md',
    'docs-authority/sizing/H2_COMPRESSOR.md',
    'docs-authority/sizing/H2_PURIFIER_BEDS.md',
    'docs-authority/sizing/HOUSE_SCRUBBERS.md',
    'docs-authority/sizing/UPW_POLISH.md',
    'docs-authority/sizing/GEO_LOOP.md',
]


def model():
    """The committed seed, computed by the full declared composition, frozen."""
    from flow_graph.v2 import solve as SL
    return SL.solve(INPUTS, REF_GRAPH)


def committed(path):
    """The golden: the committed document file bytes."""
    with open(os.path.join(ROOT, path), 'rb') as f:
        return f.read()


def _first_diff(want, got):
    i = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))
    lo = max(0, i - 80)
    return (f'first difference at byte {i} (committed {len(want)} B, rendered {len(got)} B)\n'
            f'committed: {want[lo:i + 120]!r}\nrendered:  {got[lo:i + 120]!r}')


def test_registry_declares_the_eight_sizing_docs():
    """The registry opens with the eight sizing documents, in declared order —
    later waves append their own entries after them (position, not exclusivity)."""
    paths = [p for p, _ in RENDERS]
    assert paths[:len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert all(callable(fn) for _, fn in RENDERS)
    for path, _ in RENDERS:
        assert os.path.exists(os.path.join(ROOT, path)), path


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_render_runs_every_entry():
    """render() runs every registered renderer; the sizing wave's paths come back
    first and byte-exact (later waves' documents verify in their own tests)."""
    docs = render(model(), INPUTS)
    assert list(docs)[:len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert all(isinstance(v, bytes) for v in docs.values())
    for path in EXPECTED_PATHS:
        got = docs[path]
        assert got == committed(path), f'{path}: {_first_diff(committed(path), got)}'


def test_render_one_rejects_unknown_path():
    with pytest.raises(KeyError):
        render_one('docs-authority/sizing/NO_SUCH_DOC.md', model(), INPUTS)


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes: byte-identical."""
    m1, m2 = model(), model()
    assert render(m1, INPUTS) == render(m2, INPUTS)


def test_render_modules_pure():
    """No I/O in the render modules: no open(), no banned imports, no float
    literals (the engine lint's discipline, held on the renderer wave)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    pkg_dir = os.path.dirname(_render_pkg.__file__)
    for name in sorted(os.listdir(pkg_dir)):
        if not name.endswith('.py'):
            continue
        path = os.path.join(pkg_dir, name)
        with open(path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name.split('.')[0] not in banned, f'{name}: banned import {a.name}'
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or '').split('.')[0] not in banned, f'{name}: banned import from {node.module}'
            elif isinstance(node, ast.Constant):
                assert not isinstance(node.value, float), f'{name}:{node.lineno}: float literal'
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
                raise AssertionError(f'{name}:{node.lineno}: file I/O in a render module')
