"""engine v2: the scale-down analysis family acceptance (ledger section F,
the `scale_down` row, analysis half). Reference writer
flow_graph/param/scale_down.py. The proofs:

- golden: analyse() over the committed graph reproduces the committed
  design_tool/aqs_design_tool/data/scale_down.json bytes exactly (through the
  v1 writer's serialization: json, indent 1, non-ascii kept, one trailing
  newline);
- reference equivalence: the port equals the v1 analyse() output on the
  committed graph (the v1 module is the oracle);
- determinism: two passes, identical books;
- purity: no I/O, no banned imports, no float literals (held in
  test_render_views.py for the whole wave; repeated here per family).
"""
import ast
import json
import os

from flow_graph.param import scale_down as V1
from flow_graph.v2 import functions as _fns
from flow_graph.v2.functions import scale_down as SD

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
GOLDEN = os.path.join(ROOT, 'design_tool', 'aqs_design_tool', 'data', 'scale_down.json')


def committed_bytes():
    with open(GOLDEN, 'rb') as f:
        return f.read()


def serialize(a):
    """The v1 writer's serialization (json.dump indent=1, ensure_ascii=False,
    plus the appended newline)."""
    return (json.dumps(a, indent=1, ensure_ascii=False) + '\n').encode('utf-8')


def test_golden_committed_scale_down_json():
    """analyse() over the committed graph reproduces the committed bytes."""
    with open(GRAPH, encoding='utf-8') as f:
        g = json.load(f)
    got = serialize(SD.analyse(g))
    want = committed_bytes()
    assert got == want, (
        f'scale_down.json drift: committed {len(want)} B, analysed {len(got)} B')


def test_reference_equivalence_with_v1_analyse():
    """The port equals the v1 analyse() output on the committed graph."""
    with open(GRAPH, encoding='utf-8') as f:
        g = json.load(f)
    assert SD.analyse(g) == V1.analyse()


def test_determinism_two_passes_identical():
    with open(GRAPH, encoding='utf-8') as f:
        g = json.load(f)
    assert serialize(SD.analyse(g)) == serialize(SD.analyse(g))


def test_family_module_pure():
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(SD.__file__, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'{node.lineno}: file I/O in a function module')


def test_family_registered_in_the_composition_namespace():
    """The family lives in the functions package (the composition imports
    family modules by name when its solve wiring lands; placement here keeps
    the layout stable)."""
    assert hasattr(_fns, 'scale_down')
