"""engine v2: the census-document clearance acceptance (the REMAINING rows the
inventory landing unblocked).

The wave: the five census documents that waited on the inventory census family
(flow_graph/v2/functions/inventory.py, golden in test_inventory_books.py) now
render byte-exactly from the landed books:

- render/electrical.py: cable_schedule (AQS-ELEC-010, the power circuits of the
  wire census over the one-line and busbar books) and haz_area (AQS-ELEC-009,
  the release rows of functions/haz_area plus the two inventory-count columns);
- render/inventory.py: doc_wire_specs (AQS-INV-007, the wire family
  specification page, WF-nn.svg cross-sections and WIRE_SPECS.json) and
  doc_motor_fa (AQS-INV-008, the first-article page, MF-nn.svg drawings and
  MOTOR_FA.json) over the wire families and motor design books and the
  composed MF sheet texts, with the WIRE_DRAW and mfa_* drivers.

The doc_gas_det row of the brief needed no port: the safety wave already
landed it (render/safety.py GAS_DETECTION.md + GAS_DETECTORS.csv); this module
holds the verification. The electrical REMAINING keeps protection (its
committed page is hand-authored, no generated reference), and the controls
REMAINING rows keep their instrument-index / hazop-book / commissioning /
assumptions-payload blockers with refreshed reasons.

Payload dispositions (the inventory wave's, declared at this module's I/O
boundary): the canonical builder flow_graph.v2.inputs.load supplies drivers
and site profile; the auxiliary payload rides as extra keys exactly as
test_inventory_books.py builds it; the haz_area instrument counts read the
committed INSTRUMENT_INDEX.csv rows as one more declared key (required -- the
v1 stage hard-read the file) until the instrument-index census family lands.
The golden is the committed document file; the acceptance is byte-exact
reproduction. The proofs:

- byte-exact: every cleared document renders from the model seeded from the
  committed graph and computed by the landed families, and equals the
  committed file bytes exactly;
- registry: the electrical and inventory DOCS lists stay declared contiguous
  blocks of RENDERS; the REMAINING censuses keep the genuinely-blocked rows
  and no longer name the cleared ones;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O and no float literals in the three touched render modules.
"""
import ast
import csv
import os

import pytest

from flow_graph.v2 import inputs as IN
from flow_graph.v2 import solve as SL
from flow_graph.v2.render import RENDERS, render, render_one
from flow_graph.v2.render import controls as _controls
from flow_graph.v2.render import electrical as _elec
from flow_graph.v2.render import inventory as _inv
from flow_graph.v2.render import safety as _safety
from flow_graph.v2.test_inventory_books import REF_GRAPH, REF_ROOT as ROOT, auxiliary_payload, committed

# ---- the payload: the census wave's auxiliaries plus the instrument index -----

EXPECTED_PATHS = [
    'docs-authority/CABLE_SCHEDULE.md',
    'docs-authority/HAZ_AREA.md',
    'docs-authority/inventory/HAZ_AREA.csv',
    'docs-authority/WIRE_SPECS.md',
    'docs-authority/inventory/WIRE_SPECS.json',
    'docs-authority/MOTOR_FIRST_ARTICLE.md',
    'docs-authority/inventory/MOTOR_FA.json',
] \
    + ['docs-authority/drawings/wire/' + f + '.svg' for f in _inv._WF_SHEETS] \
    + ['docs-authority/drawings/motor_fa/' + f + '.svg' for f in _inv._FA_SHEETS]

GAS_DET_PATHS = ['docs-authority/GAS_DETECTION.md', 'docs-authority/inventory/GAS_DETECTORS.csv']


def _instrument_index_rows():
    """The committed INSTRUMENT_INDEX.csv rows (the declared payload of the
    haz_area renderer until the instrument-index census family lands)."""
    with open(os.path.join(ROOT, 'docs-authority/inventory/INSTRUMENT_INDEX.csv'),
              newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def canonical_inputs():
    """The canonical payload: the declared builder supplies the drivers and
    the site profile; the census wave's auxiliary files and the instrument
    index ride as extra keys."""
    extra = dict(auxiliary_payload())
    extra['instrument_index'] = _instrument_index_rows()
    return IN.load(extra=extra.items())


_INPUTS = canonical_inputs()


def model():
    """The committed seed, computed by the full declared composition, cached
    per process (the census chain memoizes its books per model)."""
    cache = getattr(model, '_cache', None)
    if cache is None:
        cache = model._cache = SL.solve(_INPUTS, REF_GRAPH)
    return cache


def _first_diff(want, got):
    i = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))
    lo = max(0, i - 80)
    return (f'first difference at byte {i} (committed {len(want)} B, rendered {len(got)} B)\n'
            f'committed: {want[lo:i + 120]!r}\nrendered:  {got[lo:i + 120]!r}')


# ---- registry: the cleared entries are declared blocks, the goldens exist ------

def test_cleared_docs_are_registered_and_resolve():
    """Every cleared path is a registry entry (in the electrical or inventory
    DOCS block), the committed file exists, and render_one resolves it
    byte-exactly."""
    declared = [p for p, _ in _elec.DOCS] + [p for p, _ in _inv.DOCS]
    for path in EXPECTED_PATHS:
        assert path in declared, path
        assert os.path.exists(os.path.join(ROOT, path)), path
        assert render_one(path, model(), _INPUTS) == committed(path), path


def test_registry_blocks_stay_contiguous():
    """The electrical and inventory DOCS lists remain declared contiguous
    blocks of RENDERS (the aggregate composition order is unchanged)."""
    paths = [p for p, _ in RENDERS]
    for mod in (_elec, _inv):
        block = [p for p, _ in mod.DOCS]
        first = paths.index(block[0])
        assert paths[first:first + len(block)] == block


# ---- the REMAINING censuses: cleared rows off, blocked rows kept ----------------

def test_electrical_remaining_keeps_only_protection():
    """The electrical REMAINING census no longer names the cleared rows; the
    one genuinely-blocked row (protection, hand-authored page) stays named."""
    remaining = _elec.__doc__.split('REMAINING')[1].split('Cleared by')[0]
    assert 'protection' in remaining
    for cleared in ('cable_schedule (docs-authority', 'inventory_wire (', 'doc_wire_specs (',
                    'haz_area (docs-authority', 'doc_motor_fa (docs-authority'):
        assert cleared not in remaining, cleared


def test_inventory_remaining_drops_motor_fa():
    """The inventory REMAINING dict no longer names doc_motor_fa; the
    hand-authored and roster-enumeration rows stay named with their reasons."""
    assert not any('MOTOR_FIRST_ARTICLE' in k or 'doc_motor_fa' in k for k in _inv.REMAINING)
    assert len(_inv.REMAINING) == 2
    assert all(isinstance(v, str) and v for v in _inv.REMAINING.values())


def test_controls_remaining_reasons_track_the_landed_censuses():
    """The controls REMAINING census keeps its rows but no longer cites the
    landed other/motor census families as missing."""
    assert 'inventory_other, not landed' not in _controls.__doc__
    assert 'instrument' in _controls.__doc__                # the remaining census blocker, named


# ---- byte-exact: every cleared document -----------------------------------------

@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path):
    """The rendered document equals the committed file bytes exactly."""
    got = render_one(path, model(), _INPUTS)
    want = committed(path)
    assert got == want, f'{path}: {_first_diff(want, got)}'


def test_render_runs_every_entry_with_the_new_blocks():
    """render() runs every registered renderer; every cleared path comes back
    byte-exact from the aggregate pass."""
    docs = render(model(), _INPUTS)
    for path in EXPECTED_PATHS:
        assert isinstance(docs[path], bytes)
        assert docs[path] == committed(path), f'{path}: {_first_diff(committed(path), docs[path])}'


# ---- payload contract of the haz_area instrument counts -------------------------

def test_haz_area_instrument_payload_absence_branch():
    """The payload-absence branch (the census-payload convention): without the
    instrument-index payload the render still runs -- the counts drop to zero
    and the bytes leave the committed golden, which the canonical payload
    reproduces."""
    no_idx = {k: v for k, v in _INPUTS.items() if k != 'instrument_index'}
    got = _elec.render_haz_area_md(model(), no_idx)          # runs, no KeyError
    assert got != committed('docs-authority/HAZ_AREA.md')
    assert b'In total, 0 instruments' in got


def test_haz_area_counts_are_load_bearing():
    """A payload with one release-source unit's instrument count perturbed
    renders a different document -- the golden equality pins the committed
    counts."""
    perturbed = [dict(r) for r in _INPUTS['instrument_index']]
    row = next(r for r in perturbed if r['unit'] == 'ZNBR2')     # a committed release source
    row['unit'] = 'ZZ_PERTURBED'
    inputs = dict(_INPUTS)
    inputs['instrument_index'] = perturbed
    assert _elec.render_haz_area_md(model(), inputs) != committed('docs-authority/HAZ_AREA.md')


# ---- doc_gas_det: already cleared by the safety wave (verification) -------------

@pytest.mark.parametrize('path', GAS_DET_PATHS, ids=[os.path.basename(p) for p in GAS_DET_PATHS])
def test_doc_gas_det_already_cleared(path):
    """GAS_DETECTION.md and GAS_DETECTORS.csv are registered safety-wave
    renderers and reproduce the committed bytes from this module's model --
    the doc_gas_det row needed no port in this wave."""
    declared = [p for p, _ in _safety.DOCS]
    assert path in declared, path
    assert render_one(path, model(), _INPUTS) == committed(path)


# ---- determinism -----------------------------------------------------------------

def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes over the cleared block:
    byte-identical."""
    m1 = SL.solve(_INPUTS, REF_GRAPH)
    m2 = SL.solve(_INPUTS, REF_GRAPH)
    fns = dict(RENDERS)
    for path in EXPECTED_PATHS:
        assert fns[path](m1, _INPUTS) == fns[path](m2, _INPUTS), path


# ---- purity ------------------------------------------------------------------------

@pytest.mark.parametrize('mod', [_elec, _inv, _controls],
                         ids=['electrical', 'inventory', 'controls'])
def test_render_module_pure(mod):
    """No I/O and no float literals in the touched render modules: no open(),
    no banned imports (the engine lint's discipline; the drivers, the seed
    books and the payload builders carry the values)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(mod.__file__, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'{mod.__name__}: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, \
                f'{mod.__name__}: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'{mod.__name__}:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'{mod.__name__}:{node.lineno}: file I/O in a render module')
