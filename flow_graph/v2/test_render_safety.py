"""engine v2: the buildings/safety renderer acceptance (byte-exact
reproduction).

The renderer wave: flow_graph/v2/render/safety.py (the portable ledger
section H rows: hall egress, water tower, enclosure egress, fire protection,
gas detection + its CSV book, ASME code intent, hydro siting, relief register,
ZnBr2 stack test) backed by the physics books of flow_graph/v2/functions/
(building, fire_book, gas_detection, protection, haz_area - golden equality
proven in flow_graph/v2/test_safety_books.py). The golden is the committed
document file; the acceptance is byte-exact reproduction. The proofs:

- byte-exact: each document renders from the model seeded from the committed
  graph and computed by the landed physics families (the full declared
  composition), and equals the committed file bytes exactly;
- registry: the safety DOCS list is the declared contiguous block of
  RENDERS, every output path exists, and render_one resolves each;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O and no float literals in the safety render module.

The section H rows whose render depends on a family that has not landed
(the placement-seed chain: ga_check, hse_sep, site_access, struct_loads and
the struct-loads chain below it, access_check, sep_check; the inventory-hub
chain: hvac, decom, startup, commissioning; the hand-authored compliance
matrix; the haz_area document and sidecar) are NOT ported - the REMAINING
entries in the safety module docstring record the missing family each waits
on.
"""
import ast
import json
import os

import pytest

from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render, render_one
from flow_graph.v2.render import safety as _safety

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}

EXPECTED_PATHS = [p for p, _ in _safety.DOCS]


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


def test_registry_declares_the_safety_docs():
    """The safety DOCS list is a declared contiguous block of the registry, in
    the census order; every path exists and resolves through render_one."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert [p for p, _ in _safety.DOCS] == EXPECTED_PATHS
    assert all(callable(fn) for _, fn in _safety.DOCS)
    for path, _ in _safety.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, model(), INPUTS) == committed(path)


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes over the safety block:
    byte-identical."""
    m1, m2 = model(), model()
    for path, fn_r in _safety.DOCS:
        assert fn_r(m1, INPUTS) == fn_r(m2, INPUTS), path


def test_render_module_pure():
    """No I/O and no float literals in the safety render module."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    path = _safety.__file__
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'safety.py: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'safety.py: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'safety.py:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'safety.py:{node.lineno}: file I/O in a render module')
