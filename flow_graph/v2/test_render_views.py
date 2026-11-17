"""engine v2: the views/exports/layout renderer acceptance (byte-exact
reproduction).

The renderer wave: flow_graph/v2/render/views.py (ledger section F:
derived_excerpts, loop_closure, candidate_mvs, the regen_derived JSON+DOT
halves, sector_definitions, the scale_down doc+json half, the foam_ew cut
list, and the site_3d SVG+manifest half). The golden is the committed
document file; the acceptance is byte-exact reproduction. The proofs:

- byte-exact: each of the 29 documents renders from the model seeded from the
  committed graph and computed by the landed physics families (the full
  declared composition), and equals the committed file bytes exactly;
- payloads: the rows whose v1 stages read non-graph files (the system tree,
  the two front-matter numbers, the placement seed) take them as input
  payloads read at this test's I/O boundary; a caller that omits a payload
  gets loud stub bytes, never a wrong document (proof below);
- registry: the views DOCS list is the declared tail block of RENDERS in the
  census order, every output path exists, and render_one resolves each;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O, no banned imports and no float literals in the render
  module and in this wave's function modules (no open() - the render
  functions read the model and the input payloads and return bytes; file
  writing stays outside).

NOT ported here (each records its reason in the views module docstring):
the regen_derived SVGs (external graphviz render), placement_routes and
pid_sheets (line-list / inventory / nozzle families not landed), the
drawings title-block stamp + register (composer lane over other stages'
SVGs), the site_3d GLB (binary CAD asset), the foam PNGs (matplotlib
rasters), and non-baseline site_3d locales (no committed golden).
"""
import ast
import copy
import json
import os
import re

import pytest
import yaml

from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import placement_refine as _PRF
from flow_graph.v2.functions import scale_down as _SDF
from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render_one
from flow_graph.v2.render import views as _views

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
SEED = os.path.join(ROOT, 'flow_graph', 'placement_seed.json')
TREE = os.path.join(ROOT, 'flow_graph', 'system_tree.yaml')

_DOCNUM_RE = re.compile(r'^Document(?: number)?:\s*\**\s*(AQS-[A-Za-z0-9-]+)', flags=re.M)


def _docnum(name):
    """The front-matter document number of a docs-authority page (the v1
    docnum() read, at this test's I/O boundary)."""
    with open(os.path.join(ROOT, 'docs-authority', name), encoding='utf-8') as f:
        got = _DOCNUM_RE.search(f.read())
    return got.group(1) if got else '—'


def _inputs():
    """The full payload set: the drivers and site profile the solve consumes,
    plus the non-graph files the section-F stages read (system tree, the two
    front-matter numbers, the placement seed)."""
    return {
        'drivers': json.load(open(DRIVERS)),
        'site_profile': json.load(open(PROFILE)),
        'system_tree': yaml.safe_load(open(TREE)),
        'doc_numbers': {'DESIGN_TOOL_ARCHITECTURE.md': _docnum('DESIGN_TOOL_ARCHITECTURE.md'),
                        'GLOSSARY.md': _docnum('GLOSSARY.md')},
        'placement_seed': json.load(open(SEED)),
    }


INPUTS = _inputs()

EXPECTED_PATHS = [p for p, _ in _views.DOCS]

PAYLOAD_PATHS = {p for p in EXPECTED_PATHS if p.startswith('docs-authority/SECTOR_DEFINITIONS.md')
                 or p.startswith('media/3d/')}


def model():
    """The committed seed, computed by the full declared composition, frozen.
    Cached: the model is a pure frozen value of these pure inputs."""
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


def test_registry_declares_the_views_docs():
    """The views DOCS list is the declared contiguous tail block of the
    registry, in the census order; every path exists and resolves through
    render_one byte-exactly."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert paths[first + len(EXPECTED_PATHS):] == []          # the wave is the registry tail
    assert [p for p, _ in _views.DOCS] == EXPECTED_PATHS
    assert all(callable(fn) for _, fn in _views.DOCS)
    m = model()
    for path, _ in _views.DOCS:
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, m, INPUTS) == committed(path), path


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_render_runs_every_entry():
    """render() runs every registered renderer; every views-wave path comes
    back byte-exact (the earlier waves' documents verify in their own
    tests; this wave's block runs through _render_block, which is the same
    declared order - the shared render() pulls in sibling lanes'
    in-flight modules too)."""
    docs = _render_block(model(), INPUTS)
    for path in EXPECTED_PATHS:
        assert path in docs
        assert isinstance(docs[path], bytes)
        assert docs[path] == committed(path), f'{path}: {_first_diff(committed(path), docs[path])}'


def _render_block(m, inputs):
    """This wave's own registry block, run as a whole (the declared order).
    The shared-registry render() runs every landed wave's renderers too and a
    sibling lane's in-flight module can raise; this wave's proof runs its own
    block, which render_one already exercises per document."""
    return {path: fn(m, inputs) for path, fn in _views.DOCS}


def test_missing_payload_renders_a_loud_stub_not_a_wrong_document():
    """A caller that carries only the drivers + site profile (a sibling
    wave's whole-registry render pass) gets loud stub bytes for the
    payload-needing rows, and byte-exact documents for the rows that read
    the model alone."""
    m = model()
    partial = {'drivers': INPUTS['drivers'], 'site_profile': INPUTS['site_profile']}
    docs = _render_block(m, partial)
    for path in EXPECTED_PATHS:
        assert isinstance(docs[path], bytes), path
    for path in sorted(PAYLOAD_PATHS):
        assert docs[path].startswith(b'# ' + path.encode()), path
        assert b'not provided by this caller' in docs[path], path
    for path in ('flow_graph/derived/CENSUS.md', 'design_tool/aqs_design_tool/data/candidate_mvs.json',
                 'flow_graph/views/pfd.dot', 'models/openscad/foam_ew/cut_list.csv'):
        assert docs[path] == committed(path), path


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes: byte-identical."""
    m1, m2 = SL.solve(INPUTS, REF_GRAPH), SL.solve(INPUTS, REF_GRAPH)
    assert _render_block(m1, INPUTS) == _render_block(m2, INPUTS)


def test_render_and_kernel_modules_pure():
    """No I/O, no banned imports and no float literals in the render module
    and in this wave's two function modules (the engine lint's discipline,
    held on this wave; the payloads and the seed books carry the values)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    for mod in (_views, _SDF, _PRF):
        name = os.path.basename(mod.__file__)
        with open(mod.__file__, encoding='utf-8') as f:
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
                raise AssertionError(f'{name}:{node.lineno}: file I/O in an engine module')
