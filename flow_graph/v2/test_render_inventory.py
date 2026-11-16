"""engine v2: the inventory renderer acceptance (byte-exact reproduction).

The renderer wave: flow_graph/v2/render/inventory.py (the ledger section I
documents and registers, plus the section D `inventory_wire` row the section
I censuses unlock): the motor inventory and families (AQS-INV-001), the motor
family designs and sheets (AQS-INV-005), the wire inventory and families
(AQS-INV-002), the pipe inventory and families (AQS-INV-003), the other
building blocks (AQS-INV-004), the WPS register (AQS-WLD-002), the pipe and
building-block family production plans (AQS-INV-006 / AQS-INV-009), the
plant BOM roll-up (AQS-PRO-001), the self-copy reconciliation sidecar, the
spares list (AQS-OPS-003), the priced BOM (AQS-PRO-003-BOM) and the EOL
return (AQS-END-002). Reference writers: flow_graph/inventory/*.py and the
docs-authority/_wps.py, _pipe_specs.py, _bought_specs.py,
_block_fam_plans.py, _plant_bom.py, _sc_reconcile.py, _spares.py,
_cost_estimate.py and _eol.py rollups. The golden is the committed document
file; the acceptance is byte-exact reproduction. The proofs:

- byte-exact: each document renders from the model seeded from the
  committed graph and computed by the landed physics families (the full
  declared composition), and equals the committed file bytes exactly;
- registry: the inventory DOCS list is a declared contiguous block of
  RENDERS, every output path exists, and render_one resolves each; the
  module's REMAINING dict names the rows this wave does not register, each
  with its reason;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O and no float literals in the render module (no open(), no
  banned imports -- the render functions read the model and the input
  payloads and return bytes; file writing stays outside).

The auxiliary payload rides on the canonical builder
(flow_graph.v2.inputs.load, extra keys): its parse lives at the declared
I/O boundary of flow_graph/v2/test_inventory_books.py, the census family's
own acceptance module.
"""
import ast
import os

import pytest

from flow_graph.v2 import inputs as IN
from flow_graph.v2 import solve as SL
from flow_graph.v2.render import RENDERS, render, render_one
from flow_graph.v2.render import inventory as _inv
from flow_graph.v2.test_inventory_books import REF_ROOT as ROOT, REF_GRAPH, auxiliary_payload, committed

EXPECTED_PATHS = [p for p, _ in _inv.DOCS]

REMAINING_PATHS = sorted(_inv.REMAINING)


def canonical_inputs():
    """The canonical payload: the declared builder supplies the drivers and
    the site profile; the wave's auxiliary files ride as extra keys."""
    return IN.load(extra=auxiliary_payload().items())


_INPUTS = canonical_inputs()


def model():
    """The committed seed, computed by the full declared composition, cached
    per process (the census chain memoizes its books per model)."""
    cache = getattr(model, '_cache', None)
    if cache is None:
        cache = model._cache = SL.solve(_INPUTS, REF_GRAPH)
    return cache


def test_registry_declares_the_inventory_docs():
    """The inventory DOCS list is a declared contiguous block of the
    registry; every path exists and resolves through render_one; the module
    names what it does not register."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert [p for p, _ in _inv.DOCS] == EXPECTED_PATHS
    assert all(callable(fn) for _, fn in _inv.DOCS)
    assert REMAINING_PATHS, 'the unregistered rows must stay named, each with its reason'
    for path, _ in _inv.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, model(), _INPUTS) == committed(path)


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), _INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def _first_diff(want, got):
    i = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))
    lo = max(0, i - 80)
    return (f'first difference at byte {i} (committed {len(want)} B, rendered {len(got)} B)\n'
            f'committed: {want[lo:i + 120]!r}\nrendered:  {got[lo:i + 120]!r}')


def test_render_runs_every_entry():
    """render() runs every registered renderer; every inventory path comes
    back byte-exact."""
    docs = render(model(), _INPUTS)
    for path in EXPECTED_PATHS:
        assert path in docs
        assert isinstance(docs[path], bytes)
        assert docs[path] == committed(path), f'{path}: {_first_diff(committed(path), docs[path])}'


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes over the inventory
    block: byte-identical."""
    m1 = SL.solve(_INPUTS, REF_GRAPH)
    m2 = SL.solve(_INPUTS, REF_GRAPH)
    for path, fn_r in _inv.DOCS:
        assert fn_r(m1, _INPUTS) == fn_r(m2, _INPUTS), path


def test_render_module_pure():
    """No I/O and no float literals in the inventory render module."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    path = _inv.__file__
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'inventory.py: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'inventory.py: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'inventory.py:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'inventory.py:{node.lineno}: file I/O in a render module')
