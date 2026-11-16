"""engine v2: the controls/HAZOP renderer acceptance (byte-exact
reproduction).

The renderer wave: flow_graph/v2/render/controls.py - the one section J row
portable today (code_basis's CODE_BASIS.md page, composed from the EDITIONS
table of flow_graph/param/code_basis.py, the single source the landed
renderers already call for the X-STD-01 appends). The golden is the committed
document file; the acceptance is byte-exact reproduction. The proofs:

- byte-exact: the page renders from the model seeded from the committed graph
  and equals the committed file bytes exactly;
- registry: the controls DOCS list is the declared tail block of RENDERS;
- determinism and purity, as the electrical and safety waves hold them.

The section J rows whose render depends on a family that has not landed
(doc_hazop, doc_instr_index, doc_sif, doc_perf_test, doc_op_proc,
doc_plc_arch, plc_programs - the instrument/other/motor census hub and the
hazop_actions book; test_plan - the assumptions payload) are NOT ported - the
REMAINING entries in the controls module docstring record the missing family
each waits on.
"""
import ast
import json
import os

import pytest

from flow_graph.v2.render import RENDERS, render_one
from flow_graph.v2.render import controls as _controls

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}

EXPECTED_PATHS = [p for p, _ in _controls.DOCS]


def model():
    from flow_graph.v2 import solve as SL
    return SL.solve(INPUTS, REF_GRAPH)


def committed(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return f.read()


def _first_diff(want, got):
    i = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))
    lo = max(0, i - 80)
    return (f'first difference at byte {i} (committed {len(want)} B, rendered {len(got)} B)\n'
            f'committed: {want[lo:i + 120]!r}\nrendered:  {got[lo:i + 120]!r}')


def test_registry_declares_the_controls_docs():
    """The controls DOCS list is a declared contiguous block of the registry;
    every path exists and resolves through render_one."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert [p for p, _ in _controls.DOCS] == EXPECTED_PATHS
    for path, _ in _controls.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, model(), INPUTS) == committed(path)


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_render_module_pure():
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    path = _controls.__file__
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'controls.py: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'controls.py: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'controls.py:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'controls.py:{node.lineno}: file I/O in a render module')
