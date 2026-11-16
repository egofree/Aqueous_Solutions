"""engine v2: the electrical-chain renderer acceptance (byte-exact
reproduction).

The renderer wave: flow_graph/v2/render/electrical.py (ledger section D, the
electrical chain: load_list, one_line, ew_busbar, doc_power_sizing, plus the
section E ew_sizing_doc row the chain is coupled to, and their U2a JSON
sidecars; reference writers docs-authority/_load_list.py, _one_line.py,
_ew_busbar.py, _power_sizing_doc.py, _ew_sizing.py and the _rect_ew_sizing.py
interlock). The golden is the committed document file; the acceptance is
byte-exact reproduction. The proofs:

- byte-exact: each of the eight documents renders from the model seeded from
  the committed graph and computed by the landed physics families (the full
  declared composition), and equals the committed file bytes exactly;
- registry: the electrical DOCS list is the declared tail of RENDERS, every
  output path exists, and render_one resolves each;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O and no float literals in the electrical render module (no
  open(), no banned imports - the render functions read the model and the
  input payloads and return bytes; file writing stays outside).

The section D documents whose render depends on a physics or inventory family
that has not landed (cable_schedule, inventory_wire, doc_wire_specs,
protection, haz_area, doc_motor_fa) are NOT ported - the REMAINING entries in
the electrical module docstring record the missing family each waits on.
"""
import ast
import json
import os

import pytest

from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render, render_one
from flow_graph.v2.render import electrical as _elec

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
from flow_graph.v2.test_render_clearances import canonical_inputs

INPUTS = canonical_inputs()

EXPECTED_PATHS = [
    'docs-authority/LOAD_LIST.md',
    'docs-authority/LOAD_LIST.json',
    'docs-authority/ONE_LINE.md',
    'docs-authority/ONE_LINE.json',
    'docs-authority/BUSBAR.md',
    'docs-authority/BUSBAR.json',
    'docs-authority/POWER_SIZING.md',
    'docs-authority/sizing/EW_CELLS.md',
    'docs-authority/CABLE_SCHEDULE.md',
    'docs-authority/HAZ_AREA.md',
    'docs-authority/inventory/HAZ_AREA.csv',
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


def test_registry_declares_the_electrical_docs():
    """The electrical DOCS list is the declared contiguous block of the
    registry, in the census order; every path exists and resolves through
    render_one."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert [p for p, _ in _elec.DOCS][:len(EXPECTED_PATHS)] == EXPECTED_PATHS  # the clearances wave appends its entries
    assert all(callable(fn) for _, fn in _elec.DOCS)
    for path, _ in _elec.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, model(), INPUTS) == committed(path)


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_render_runs_every_entry():
    """render() runs every registered renderer; every electrical path comes
    back byte-exact."""
    docs = render(model(), INPUTS)
    for path in EXPECTED_PATHS:
        assert path in docs
        assert isinstance(docs[path], bytes)
        assert docs[path] == committed(path), f'{path}: {_first_diff(committed(path), docs[path])}'


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes: byte-identical."""
    m1, m2 = model(), model()
    assert render(m1, INPUTS) == render(m2, INPUTS)


def test_render_module_pure():
    """No I/O and no float literals in the electrical render module: no
    open(), no banned imports, no float constants (the engine lint's
    discipline, held on this wave; the drivers and the seed books carry the
    values)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    path = _elec.__file__
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'electrical.py: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'electrical.py: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'electrical.py:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'electrical.py:{node.lineno}: file I/O in a render module')
