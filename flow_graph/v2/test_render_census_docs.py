"""engine v2: the census-fed controls documents acceptance (the four landed
ledger section J rows: doc_hazop, doc_instr_index, doc_sif, doc_plc_arch).

The renderer wave: flow_graph/v2/render/controls.py. The goldens are the
committed document files; the acceptance is byte-exact reproduction:

- docs-authority/HAZOP.md, HAZOP_ACTION_REGISTER.md, hazop_actions.csv (the
  AQS-SAF-001 worksheets, the AQS-SAF-008 register and the actions CSV at
  its committed post-SIF face - the v1 doc_sif amend composed in memory);
- docs-authority/INSTRUMENT_INDEX.md and inventory/INSTRUMENT_INDEX.csv
  (AQS-CTL-001, over the landed census book of
  flow_graph/v2/functions/instrument_index.py);
- docs-authority/CAUSE_EFFECT.md and sif_list.csv (AQS-CTL-003);
- docs-authority/CONTROL_ARCH.md (AQS-CTL-002).

The payloads the pages consume (the inventory-family face idiom): the
committed OTHER_INVENTORY.csv rows (the census lane, the check-valve set and
the electronics points), the committed MOTOR_INVENTORY.csv rows (the
pumped-unit set) and the committed duty-sheet section-6 relief ids (the
hand-authored duties pages - the duties wave's REMAINING census; the v1
stage read the pages, so the face rides the payload). The proofs:

- byte-exact: each of the eight files renders from the model seeded from the
  committed graph and computed by the full declared composition, and equals
  the committed file bytes exactly;
- the registered CSV face is the census book: the instrument book the pages
  compose re-serializes to the committed INSTRUMENT_INDEX.csv bytes (the
  test_instrument_index.py golden, wired through the DOCS lane);
- the committed census stats re-derive from the books: the HAZOP worksheet
  and disposition counts, the post-SIF status counts, the SIF SIL
  distribution and the two X-PIP actions that stay open;
- soft absent faces: dropping any payload face (or all of them - the
  drivers+profile shape the engine's update/check cycle passes) renders
  every page without raising (the v1 absent-file branch); a present but
  incomplete census lane stays loud through the family's coverage gate;
- the duty_relief6 face is load-bearing: removing one relief-cited unit
  moves the dispositions (actions CSV, HAZOP page, register, CAUSE_EFFECT
  open count) and leaves the SIF list and the instrument index untouched;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O, no banned imports, no float literals in the render module.
"""
import ast
import csv
import io
import os
import re

import pytest

from flow_graph.v2 import inputs as IN
from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import instrument_index as II
from flow_graph.v2.graph_io import load
from flow_graph.v2.render import RENDERS, render_one
from flow_graph.v2.render import controls as _controls

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')

EXPECTED_PATHS = [p for p, _ in _controls.DOCS if p != 'docs-authority/CODE_BASIS.md']


# ---- the auxiliary payload: the committed faces the v1 stages read --------------

def _csv_dicts(path):
    """A committed CSV as dict rows (the v1 DictReader face)."""
    with open(os.path.join(ROOT, path), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _duty_relief6():
    """The unit ids whose committed duty sheet carries the section-6 relief
    statement - the DUTY6 set of docs-authority/_hazop.py, read here at the
    declared I/O boundary (the pages are hand-authored; the duties wave's
    REMAINING census)."""
    duties = os.path.join(ROOT, 'docs-authority', 'duties')
    out = []
    for name in sorted(os.listdir(duties)):
        if not name.endswith('.md') or name.startswith('_'):
            continue
        with open(os.path.join(duties, name), encoding='utf-8') as f:
            if re.search(r'^6\. Relief', f.read(), re.M):
                out.append(name[:-3])
    return out


def canonical_inputs():
    """The canonical payload: the declared builder supplies the drivers and
    the site profile; the three faces ride as the census keys."""
    return IN.load(extra=[('other_inventory', _csv_dicts('docs-authority/inventory/OTHER_INVENTORY.csv')),
                          ('motor_inventory', _csv_dicts('docs-authority/inventory/MOTOR_INVENTORY.csv')),
                          ('duty_relief6', _duty_relief6())])


def committed_bytes(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return f.read()


@pytest.fixture(scope='session')
def inputs():
    return canonical_inputs()


@pytest.fixture(scope='session')
def model(inputs):
    """The committed seed, computed by the full declared composition."""
    return SL.solve(inputs, REF_GRAPH)


@pytest.fixture(scope='session')
def bridge_model():
    """The committed seed with NO solve (the census pages read no stamped
    state the solve changes - the no-drivers bridge contract of the
    instrument family)."""
    return load(REF_GRAPH).build()


# ---- registry and byte-exact acceptance -----------------------------------------

def test_registry_declares_the_census_docs():
    """The census-doc block is a declared contiguous block of the registry
    after the CODE_BASIS entry; every path exists and resolves through
    render_one."""
    paths = [p for p, _ in RENDERS]
    first = paths.index(EXPECTED_PATHS[0])
    assert paths[first:first + len(EXPECTED_PATHS)] == EXPECTED_PATHS
    assert paths[first - 1] == 'docs-authority/CODE_BASIS.md'
    for path in EXPECTED_PATHS:
        assert os.path.exists(os.path.join(ROOT, path)), path


@pytest.mark.parametrize('path', EXPECTED_PATHS, ids=[os.path.basename(p) for p in EXPECTED_PATHS])
def test_document_byte_exact(path, model, inputs):
    """The page renders from the model and the canonical payload and equals
    the committed file bytes exactly."""
    got = render_one(path, model, inputs)
    want = committed_bytes(path)
    assert got == want, f'{path}: first difference at byte {next((i for i, (x, y) in enumerate(zip(want, got)) if x != y), min(len(want), len(got)))}'


def _csv_bytes(rows, keys):
    s = io.StringIO()
    w = csv.DictWriter(s, keys)
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def test_the_registered_csv_face_is_the_census_book(bridge_model):
    """The census book the pages compose re-serializes to the committed
    INSTRUMENT_INDEX.csv bytes - the family golden, wired through the DOCS
    lane (the bridge model suffices: the census reads no stamped state)."""
    book = II.instrument_book(bridge_model, {'other_inventory': _csv_dicts('docs-authority/inventory/OTHER_INVENTORY.csv')})
    keys = ['tag', 'unit', 'sector', 'type', 'spec', 'range', 'signal', 'loop', 'plc', 'basis']
    assert list(book['rows'][0].keys()) == keys
    assert _csv_bytes(book['rows'], keys) == committed_bytes('docs-authority/inventory/INSTRUMENT_INDEX.csv')


# ---- the committed census stats re-derive from the books -------------------------

def test_hazop_disposition_counts(model, inputs):
    """The HAZOP census counts match the committed page's own figures: the
    worksheets, the deviations, the actions and the three disposition
    buckets (the two open rows are the X-PIP check-valve actions, which no
    artifact closes)."""
    book = _controls._hazop_census(model, inputs, inputs['duty_relief6'],
                                   _controls._instr_book(model, inputs)['rows'])
    n_cls, n_sif, n_trk = _controls._hazop_counts(book)
    assert (len(book['nodes']), sum(len(x[2]) for x in book['nodes']), len(book['acts'])) == (157, 1018, 246)
    assert (n_cls, n_sif, n_trk) == (150, 96, 0)
    opens = [a for a in book['actions'] if a['status'] == 'open']
    assert sum(1 for a in opens if a['closing_task'] == 'X-CTL-03') == 94      # the trip actions, pre-SIF pass
    assert [a for a in opens if a['closing_task'] != 'X-CTL-03'] == \
        [dict(action_id='HZ-102', node='WS_SOLV', parameter='flow', guide_word='Reverse',
              action='check valve on the pumped inlet', closing_task='X-PIP', status='open'),
         dict(action_id='HZ-161', node='CA_POT', parameter='flow', guide_word='Reverse',
              action='check valve on the pumped inlet', closing_task='X-PIP', status='open')]


def test_sif_pass_counts_and_the_post_sif_face(model, inputs):
    """The SIF book: 187 functions with the committed SIL distribution; the
    actions CSV status column carries the committed post-SIF face (94
    closed-by-SIF trip actions, the closed-at-issue dispositions, the two
    open X-PIP rows)."""
    book, sifs = _controls._ctl_books(model, inputs)
    assert len(sifs) == 187
    sil = {k: sum(1 for s in sifs if s['SIL'] == k) for k in (0, 1, 2)}
    assert sil[2] == 10 and sil[1] == 88 and sil[0] == 89
    st = [a['status'] for a in book['actions']]
    assert sum(1 for s in st if s.startswith('closed by SIF-')) == 94
    assert sum(1 for s in st if s.startswith('closed: docs-authority/duties/')) == 150
    assert sum(1 for s in st if s.startswith('open - tracked')) == 0
    assert sum(1 for s in st if s == 'open') == 2                              # the two X-PIP rows, post-SIF face


# ---- the absent-file branches stay soft, the incomplete lane stays loud ---------

@pytest.mark.parametrize('drop', ['other_inventory', 'motor_inventory', 'duty_relief6', 'ALL'],
                         ids=['no-other', 'no-motor', 'no-duty6', 'no-faces'])
def test_absent_payload_faces_render_soft(bridge_model, drop):
    """Every census page renders to bytes with any payload face absent (the
    v1 absent-file branch - the drivers+profile shape the engine's
    update/check cycle passes must not raise)."""
    payload = canonical_inputs()
    if drop == 'ALL':
        payload = {k: v for k, v in payload.items() if k not in ('other_inventory', 'motor_inventory', 'duty_relief6')}
    else:
        payload.pop(drop)
    for path in EXPECTED_PATHS:
        assert isinstance(render_one(path, bridge_model, payload), bytes)


def test_incomplete_census_lane_stays_loud(bridge_model):
    """A present but incomplete inventory lane raises through the family's
    coverage gate (a dropped unit's instrument rows leave a process unit
    without a loop) - the census never renders a wrong page silently."""
    rows = [r for r in _csv_dicts('docs-authority/inventory/OTHER_INVENTORY.csv')
            if not (r['unit'] == 'EW_1' and r['category'] == 'instrument')]
    with pytest.raises(ValueError, match='process units without a loop'):
        render_one('docs-authority/INSTRUMENT_INDEX.md', bridge_model, {'other_inventory': rows})


# ---- the duty_relief6 face is load-bearing ---------------------------------------

def test_duty_relief6_face_is_load_bearing(model, inputs):
    """Removing one relief-cited unit from the face moves its relief-case
    disposition to the tracked register (the actions CSV, the HAZOP page and
    the CAUSE_EFFECT open count change); the SIF list and the instrument
    index are untouched - the hand-authored duty pages gate exactly the
    disposition half."""
    book = _controls._hazop_census(model, inputs, inputs['duty_relief6'],
                                   _controls._instr_book(model, inputs)['rows'])
    u0 = next(a[0] for a in book['acts'] if a[3] == 'relief case')
    slim = [u for u in inputs['duty_relief6'] if u != u0]
    payload = dict(inputs)
    payload['duty_relief6'] = slim
    moved = render_one('docs-authority/hazop_actions.csv', model, payload)
    assert moved != committed_bytes('docs-authority/hazop_actions.csv')
    assert (u0.encode() in moved) and (f'closed: docs-authority/duties/{u0}.md'.encode() not in moved)
    assert render_one('docs-authority/HAZOP.md', model, payload) != committed_bytes('docs-authority/HAZOP.md')
    assert render_one('docs-authority/HAZOP_ACTION_REGISTER.md', model, payload) != \
        committed_bytes('docs-authority/HAZOP_ACTION_REGISTER.md')
    assert render_one('docs-authority/CAUSE_EFFECT.md', model, payload) != \
        committed_bytes('docs-authority/CAUSE_EFFECT.md')
    assert render_one('docs-authority/sif_list.csv', model, payload) == committed_bytes('docs-authority/sif_list.csv')
    assert render_one('docs-authority/INSTRUMENT_INDEX.md', model, payload) == \
        committed_bytes('docs-authority/INSTRUMENT_INDEX.md')


# ---- determinism and purity -------------------------------------------------------

def test_determinism_two_passes_identical_bytes(inputs):
    """Two independent seed + solve + render passes: byte-identical pages."""
    outs1 = {p: render_one(p, SL.solve(inputs, REF_GRAPH), inputs) for p in EXPECTED_PATHS}
    outs2 = {p: render_one(p, SL.solve(inputs, REF_GRAPH), inputs) for p in EXPECTED_PATHS}
    assert outs1 == outs2
    assert all(outs1[p] == committed_bytes(p) for p in EXPECTED_PATHS)


def test_render_module_pure():
    """No I/O, no banned imports, no float literals in the render module
    (constants enter as floats of their exact decimals)."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(_controls.__file__, encoding='utf-8') as f:
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
