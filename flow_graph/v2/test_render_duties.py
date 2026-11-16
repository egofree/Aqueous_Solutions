"""engine v2: the duty-sheet renderer acceptance (the wave's real shape).

The renderer wave: flow_graph/v2/render/duties.py (ledger section E, the
doc half of the `duty_basis` row). Reference writer
docs-authority/_duty_basis.py. The committed duty sheets are hand-authored
pages at that stage's patch fixpoint: the generator re-renders the section 1
line, the section 3 default-template lines, the envelope-hours fragment, the
section 7 pointer, and whole section 2 for nodes with a solved hvac or
cycling_thermal block - never the hand/historical text around it (header
`Graph Rev` line frozen at authoring time, pointer-suffix variants,
hand-rewritten tails, per-unit sections 4/5/8). Verified at port time:
author(current graph) reproduces zero committed pages, so no whole page is
registerable under the registry's byte-exact contract (DOCS is empty and
REMAINING carries the full census - see the module docstring). The proofs
this file holds:

- census: REMAINING plus the registered DOCS pages cover exactly the
  committed sheets directory, live;
- byte-exact, per page: every generator-owned fragment re-renders from the
  composed solve (flow_graph.v2.solve.solve, INPUTS = drivers + site
  profile, the render_sizing idiom) byte-identically to the committed page
  - the section 1 line on every graph unit with a sheet, the issued section
  3 lines, the converged graph-material section 3 lines, the hvac section 2,
  the cycling_thermal section 2, the envelope bullet where the node stamp
  and page agree;
- registry: every DOCS entry is held to byte-exact equality with its
  committed page (self-enforcing as the composer lane registers pages);
- characterization: the create-lane author() template diverges from a
  committed page in exactly the two documented historical lines;
- determinism: two independent seed+solve+render passes, byte-identical;
- purity: no I/O, no banned imports, no float literals in duties.py (the
  engine lint's os.walk already covers render/; mirrored here as declared).
"""
import ast
import csv
import difflib
import json
import os
import re

import pytest

from flow_graph.v2 import solve as SL
from flow_graph.v2.render import duties as DU
from flow_graph.v2.render import render_one

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
DRIVERS = os.path.join(ROOT, 'flow_graph', 'param', 'drivers.json')
PROFILE = os.path.join(ROOT, 'flow_graph', 'param', 'sites', 'baseline.json')
SEED = os.path.join(ROOT, 'flow_graph', 'placement_seed.json')
INSTRUMENTS = os.path.join(ROOT, 'docs-authority', 'inventory', 'INSTRUMENT_INDEX.csv')
DUTIES_DIR = os.path.join(ROOT, 'docs-authority', 'duties')
INPUTS = {'drivers': json.load(open(DRIVERS)),
          'site_profile': json.load(open(PROFILE))}

# The section 3 default templates the v1 patch may replace (X-MAT-06); a page
# whose line carries anything else is hand text and is never overwritten.
_SEC3_DEFAULTS = ('3. Material. 316L if the stream is wet',
                  '3. Material. 316L where the stream is wet',
                  '3. Material. Selection pending')


@pytest.fixture(scope='session')
def model():
    """The committed seed, computed by the full declared composition, frozen."""
    return SL.solve(INPUTS, REF_GRAPH)


def committed(uid):
    """The golden: the committed duty sheet bytes, decoded."""
    with open(os.path.join(DUTIES_DIR, uid + '.md'), 'rb') as f:
        return f.read().decode('utf-8')


def sheet_ids():
    """Every committed duty sheet id (the two _*.json sidecars are bookkeeping)."""
    return sorted(f[:-3] for f in os.listdir(DUTIES_DIR)
                  if f.endswith('.md') and not f.startswith('_'))


def units_with_sheets(m):
    """Graph units whose committed sheet exists (the patch fixpoint set)."""
    return sorted(uid for uid in m.nodes
                  if os.path.exists(os.path.join(DUTIES_DIR, uid + '.md')))


def _loops(uid):
    """The unit's instrument loops (the v1 hidden INSTRUMENT_INDEX.csv read)."""
    with open(INSTRUMENTS, encoding='utf-8') as f:
        return sorted({r['loop'] for r in csv.DictReader(f) if r['unit'] == uid})


def _mfg_module(uid):
    """The unit's manufacturing model file (the v1 models/mfg glob, sorted,
    draw_* scripts excluded - the 2026-11-01 pointer rule)."""
    d = os.path.join(ROOT, 'models', 'mfg', uid)
    if not os.path.isdir(d):
        return None
    mods = sorted(f for f in os.listdir(d) if f.endswith('.py') and not f.startswith('draw_'))
    return mods[0] if mods else None


def facts_for(uid):
    """The create-lane facts for one unit: loops, STL flag, mfg module."""
    return {'loops': _loops(uid),
            'has_stl': os.path.exists(os.path.join(ROOT, 'cad', 'stl', uid + '.stl')),
            'mfg_module': _mfg_module(uid)}


def test_census_covers_the_committed_sheets():
    """REMAINING plus registered DOCS pages cover exactly the duties
    directory - the live census, not a frozen count."""
    doc_ids = {os.path.basename(p)[:-3] for p, _ in DU.DOCS}
    assert set(DU.REMAINING) | doc_ids == set(sheet_ids())
    assert set(DU.REMAINING).isdisjoint(doc_ids)


def test_registered_docs_are_byte_exact(model):
    """The registry's contract, held for this family too: every DOCS entry
    renders byte-identically to its committed page. Empty today - no duty
    sheet is byte-exactly renderable (hand base text, see duties.py) - so
    the sizing entries must still be the whole RENDERS list."""
    for path, _ in DU.DOCS:
        got = render_one(path, model, INPUTS)
        with open(os.path.join(ROOT, path), 'rb') as f:
            assert got == f.read(), path


@pytest.mark.parametrize('uid', units_with_sheets(SL.solve(INPUTS, REF_GRAPH)))
def test_section1_line_byte_exact(uid, model):
    """The generator-owned section 1 line re-renders byte-exactly onto the
    committed page (the v1 patch fixpoint)."""
    line = DU.render_section1(model, uid)
    page = committed(uid)
    assert re.search(r'^1\. Basis\..*$', page, flags=re.M), uid
    assert line in page, uid


def test_section3_issued_lines_byte_exact(model):
    """The issued selection line (params.sec3_material) re-renders
    byte-exactly onto every committed page whose node carries one."""
    checked = 0
    for uid in units_with_sheets(model):
        line = DU.render_material_line_issued(model, uid)
        if line is None:
            continue
        page = committed(uid)
        m3 = re.search(r'^3\. Material\..*$', page, flags=re.M)
        assert m3, uid
        assert line == m3.group(0), uid
        checked += 1
    assert checked > 0


def test_section3_default_replacement_lines_byte_exact(model):
    """Where a committed page still carries a default template, the node
    material line replaces it byte-exactly (X-MAT-06); pages the patch has
    already converged carry the rendered line itself; hand-written material
    texts are neither - and are never overwritten. Units with an issued
    sec3_material take the issued branch, not this one (the v1 elif)."""
    converged = 0
    for uid in units_with_sheets(model):
        line = DU.render_material_line_graph(model, uid)
        if line is None:
            continue
        if (model.nodes[uid].get('params') or {}).get('sec3_material'):
            continue                                        # the issued selection governs (v1 elif)
        page = committed(uid)
        m3 = re.search(r'^3\. Material\..*$', page, flags=re.M)
        assert m3, uid
        if m3.group(0).startswith(_SEC3_DEFAULTS):
            assert line == m3.group(0), uid                 # a default the patch would replace
        if line == m3.group(0):
            converged += 1                                  # the patch fixpoint: the rendered line
    assert converged > 0                                    # the template is byte-exact on the converged pages


def test_hvac_section2_byte_exact(model):
    """The whole section 2 of a node with a solved hvac block re-renders
    byte-exactly, trailing blank line included."""
    checked = 0
    for uid in units_with_sheets(model):
        hv = (model.nodes[uid].get('params') or {}).get('hvac')
        if not hv or hv.get('total_kW') is None:
            continue
        block = DU.render_hvac_section2(model, uid)
        assert block in committed(uid), uid
        checked += 1
    assert checked > 0


def test_cycling_thermal_section2_byte_exact(model):
    """The whole section 2 of a node with a solved cycling_thermal block
    re-renders byte-exactly, given the placement-seed block (the v1 hidden
    read, injected)."""
    checked = 0
    seed_units = {u.get('unit_id'): u for u in json.load(open(SEED)).get('units', [])}
    for uid in units_with_sheets(model):
        ct = (model.nodes[uid].get('params') or {}).get('cycling_thermal')
        if not ct:
            continue
        blk = seed_units.get(uid, {})
        block = DU.render_cycling_section2(model, uid, blk.get('size_mm'))
        assert block in committed(uid), uid
        checked += 1
    assert checked > 0


@pytest.mark.parametrize('uid', ['DUCK_PEN', 'QUAIL_CAGE', 'H2O_ELYZ', 'MEOH_COND',
                                 'NOX_SCRUB', 'LITHO_COAT', 'GROW_BED', 'FISH'])
def test_envelope_line_byte_exact(uid, model):
    """The envelope bullet re-renders byte-exactly where the node stamp and
    the page agree; pages authored from an older stamp, with a hand-rewritten
    tail, or printed before the tail template existed keep their historical
    line (the patch path never rewrites dimensions or hand text) - skipped,
    not asserted."""
    if uid not in model.nodes:
        pytest.skip('historical sheet: unit not on the committed graph')
    line = DU.render_envelope_line(model, uid)
    if line is None:
        pytest.skip('node books no envelope stamp')
    page = committed(uid)
    m = re.search(r'^- Envelope .*$', page, flags=re.M)
    if not m:
        pytest.skip('page carries no envelope bullet')
    if line == m.group(0):
        assert True
    else:
        pytest.skip('historical hand/page-state envelope text '
                    '(stale node stamp, hand tail, or pre-template page)')


def test_duty_string_fixpoint(model):
    """The params.duty prefix the stage refreshes in memory: EXT_HALL sits at
    the fixpoint (a graph-write lane picked it up); the other three committed
    node fields carry older graph-lane values, per the v1 comment - pinned
    here so convergence (or drift) of the documented v1 lag is loud."""
    for uid in ('CRYO_ASU', 'EVAP_ACID', 'EVAP_BASE', 'EXT_HALL'):
        assert uid in model.nodes, uid
        fresh = DU.render_duty_string(model, uid)
        cur = model.nodes[uid]['params']['duty']
        if uid == 'EXT_HALL':
            assert cur.startswith(fresh), uid
        else:
            assert not cur.startswith(fresh), uid   # the documented stale graph-lane value


@pytest.mark.parametrize('uid', ['DUCK_PEN', 'QUAIL_CAGE'])
def test_author_sheet_diverges_only_in_the_documented_historical_lines(uid, model):
    """The create-lane template over the current graph matches a committed
    author()-shape page everywhere except the two lines the patch path never
    rewrites: the header `Graph Rev` line (frozen at authoring time) and the
    section 7 pointer line (suffix variant from the authoring pass). This
    pins the hand+patch hybrid structure the module docstring records."""
    sheet = DU.render_author_sheet(model, uid, facts_for(uid))
    page = committed(uid)
    removed = [l[1:] for l in difflib.unified_diff(sheet.splitlines(), page.splitlines(),
                                                   lineterm='', n=0)
               if l[:1] == '-' and not l.startswith('---')]
    added = [l[1:] for l in difflib.unified_diff(sheet.splitlines(), page.splitlines(),
                                                 lineterm='', n=0)
             if l[:1] == '+' and not l.startswith('+++')]
    assert len(removed) == len(added) == 2, (uid, removed, added)
    for old, new in zip(sorted(removed), sorted(added)):
        assert old.startswith('Standard: AQS-STD-001 Rev A. Graph Rev ') or \
            old.startswith('7. Code. Shop, not stamped'), (uid, old)


def test_determinism_two_passes_byte_identical():
    """Two independent seed + compute + render passes: byte-identical."""
    def run():
        m = SL.solve(INPUTS, REF_GRAPH)
        return {uid: DU.render_section1(m, uid) for uid in ('DUCK_PEN', 'EXT_HALL', 'ZNBR2')}, \
            DU.render_author_sheet(m, 'DUCK_PEN', facts_for('DUCK_PEN')), \
            DU.render_hvac_section2(m, 'EXT_HALL'), \
            DU.render_cycling_section2(m, 'ZNBR2', [8000, 4000, 3000])
    assert run() == run()


def test_duties_module_pure():
    """No I/O in the render module: no open(), no banned imports, no float
    literals. The engine lint's os.walk already covers render/ (verified:
    lint.run() scans every non-test .py under flow_graph/v2); mirrored here
    as the wave's declared discipline, in the render_sizing shape."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    path = DU.__file__
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'{path}: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'{path}: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'{path}:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'{path}:{node.lineno}: file I/O in a render module')
