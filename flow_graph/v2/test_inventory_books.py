"""engine v2: the inventory census family acceptance (the ledger section I
PHYSICS-side censuses, backed by the section D `inventory_wire` row).

The family: flow_graph/v2/functions/inventory.py (reference writers
flow_graph/inventory/motors.py, wire.py, pipe.py, other.py,
motor_designs.py and stable_ids.py). The censuses classify and size every
motor, circuit, pipe line and building block; they write NO graph state --
the rows are boundary data the renderer wave
(flow_graph/v2/render/inventory.py, flow_graph/v2/test_render_inventory.py)
lays out into the committed registers and documents. The proofs:

- golden: each census book re-serializes to the committed census CSV bytes
  exactly (MOTOR_INVENTORY, WIRE_INVENTORY, PIPE_INVENTORY,
  OTHER_INVENTORY -- the v1 float books, reproduced by the float-replica
  doctrine the family docstring records);
- determinism: two independent seed+solve+census passes, identical books;
- bridge contracts: the payload-absence branches take the v1 absent-file
  branches; the family-id allocation is an enumerated reference (a family
  outside the committed register raises, nothing is written back); the
  collection-bus CB- rows compose in memory from the power family's
  sections book -- no COLLECTION_BUS.md parse anywhere in the family; and
  the family registers nothing with the solve registry (the censuses stamp
  no graph field, so they run in the renderer lane only);
- purity: no I/O, no banned imports, no float literals in the family
  module (constants enter as floats of their exact decimals, flo()).

The auxiliary payload (mfg BOMs and fasteners, the MFG_TOOLS tool table,
the placement block map, the ISO_SHEETS rows, the SUPPORTS span counts,
the line-list positions, the grounding-grid lengths, the gas-detector and
SIF rows, the nozzle-unit roster, the family-id registers, the motor-family
CAD BOMs, the unit envelope BOMs, the duty-sheet section 3 texts, the
piping-class sheet rows) is the committed data the v1 stages read beside
the graph. This module parses it once, at the declared I/O boundary, and
every test passes it down as inputs payloads -- the canonical builder
flow_graph.v2.inputs.load supplies the drivers and the site profile and
carries the extras through.
"""
import ast
import collections
import csv
import glob
import io
import json
import os
import re
import subprocess
import sys

import pytest

from flow_graph.v2 import inputs as IN
from flow_graph.v2 import solve as SL
from flow_graph.v2.functions import inventory as INV

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')
REF_ROOT = ROOT                                          # the render acceptance imports the repo root under its own name

# ---- the auxiliary payload: the committed files the v1 censuses read -----------

def _rd(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as f:
        return f.read()


def _csv_rows(path):
    """csv.reader rows (raw cells, the header row first)."""
    with open(os.path.join(ROOT, path), newline='', encoding='utf-8') as f:
        return [r for r in csv.reader(f)]


def _csv_dicts(path):
    with open(os.path.join(ROOT, path), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _mfg_tools_rows():
    """The MFG_TOOLS.md tool table rows, under the v1 filter (`len(c) >= 3 and
    numeric c[2]` on the `|`-split cells)."""
    out = []
    for line in _rd('docs-authority/MFG_TOOLS.md').splitlines():
        c = [x.strip() for x in line.split('|')[1:-1]]
        if len(c) >= 3 and re.match(r'^[\d.]+$', c[2]):
            out.append((c[0], c[1], float(c[2])))
    return out


def _placement_blocks():
    """The merged placement block map: seed blocks first, study rows
    setdefault (the v1 order)."""
    seed = json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json')))
    st = json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))
    blk = {}
    for b in seed['blocks']:
        for u in b.get('unit_ids', []):
            blk[u] = b['block_id']
    for r in st['units']:
        blk.setdefault(r['unit_id'], r.get('block_id'))
    return blk


def _supports_counts():
    """The SUPPORTS.md span counts (the v1 `| ` row / column 6 digit parse)."""
    sup = {}
    for line in _rd('docs-authority/SUPPORTS.md').splitlines():
        if line.startswith('| ') and line.split('|')[6].strip().isdigit():
            sup[line.split('|')[1].strip()] = int(line.split('|')[6])
    return sup


def _line_positions():
    """The unit-centre map: the docs-authority/_line_list.py module-level C
    dict, rebuilt from the committed files it reads (its doc write sits under
    that module's __main__ guard). Duty origins, placement report moves,
    study rows, seed units, the GA relocates, the CAD moves, the riding
    exchanger, then the block centres."""
    seed = json.load(open(os.path.join(ROOT, 'flow_graph/placement_seed.json')))
    st = json.load(open(os.path.join(ROOT, 'flow_graph/placement_study.json')))
    C = {}
    for u, o in json.load(open(os.path.join(ROOT, 'docs-authority/duties/_origins.json')))['origins'].items():
        C[u] = ([o['origin_mm'][i] + o['size_mm'][i] / 2 for i in range(3)], 'duty origin')
    pr = json.load(open(os.path.join(ROOT, 'flow_graph/placement_report.json')))
    for r in pr.get('moves', []) + pr.get('create_moves', []):
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(o) == 3 and len(z) >= 2:
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_report'))
    for r in st['units']:
        o, z = r['origin_mm'], r['size_mm']
        C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_study (STUDY)'))
    LV = {'L-1': -6000, 'L0': 0, 'L1': 6000}
    for r in seed['units']:
        o, z = r.get('origin_mm'), r.get('size_mm')
        if o and z and len(z) >= 2:
            o = list(o) + [LV.get(r.get('level'), 0)] * (3 - len(o))
            z = list(z) + [0] * (3 - len(z))
            C.setdefault(r['unit_id'], ([o[i] + z[i] / 2 for i in range(3)], 'placement_seed'))
    sys.path.insert(0, os.path.join(ROOT, 'models/freecad'))
    try:
        import params as _FP
        for _u, (_cx, _cy) in getattr(_FP, 'RELOCATE', {}).items():
            if _u in C:
                C[_u] = ([_cx, _cy, C[_u][0][2]], C[_u][1] + ' + GA relocate')
    except Exception:
        pass
    if os.path.exists(os.path.join(ROOT, 'docs-authority/inventory/CAD_MOVES.json')):
        for _m in json.load(open(os.path.join(ROOT, 'docs-authority/inventory/CAD_MOVES.json'))):
            if _m['unit'] in C:
                _c = C[_m['unit']][0]
                C[_m['unit']] = ([_c[0] + _m['dx_mm'], _c[1] + _m['dy_mm'], _c[2]],
                                 C[_m['unit']][1] + ' + GA move')
    if 'EVAP_ACID_VS' not in C and 'EVAP_ACID' in C:
        c = C['EVAP_ACID'][0]
        C['EVAP_ACID_VS'] = ([c[0], c[1] + 650, c[2]], 'on EVAP_ACID frame')
    for b in seed['blocks']:
        o = b['origin_mm']
        z = b['size_mm']
        c = [o[0] + z[0] / 2, o[1] + z[1] / 2, LV.get(b['level'], 0) + 500]
        for u in b.get('unit_ids', []):
            C.setdefault(u, (c, 'placement block ' + b['block_id']))
    return C


def _grounding_grid():
    """The grounding-grid study lengths: the read-only AQS-ELEC-005 study
    print (the v1 wire stage ran the same script for its lengths; it writes
    nothing), the last stdout line as JSON."""
    out = subprocess.run([sys.executable, 'docs-authority/_grounding_study.py'],
                         capture_output=True, text=True, cwd=ROOT, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def _family_registers():
    """The append-only family-id registers (the formats are the inventory
    family's): one entry per register prefix."""
    return {pre: json.load(open(os.path.join(ROOT, f'flow_graph/inventory/{name}_family_ids.json')))
            for pre, name in (('MF', 'motor'), ('WF', 'wire'), ('PF', 'pipe'), ('OF', 'other'))}


def _duty_sec3():
    """The hand-authored duty-sheet section 3 texts, whitespace-normalized as
    the v1 _eol.py duty3() read."""
    d3 = {}
    for p in glob.glob(os.path.join(ROOT, 'docs-authority/duties/*.md')):
        s = _rd(os.path.relpath(p, ROOT))
        m = re.search(r'^3\.\s*Material\.(.*?)(?=^4\.)', s, re.M | re.S)
        d3[os.path.basename(p)[:-3]] = ' '.join(m.group(1).split()) if m else None
    return d3


def auxiliary_payload():
    """The declared auxiliary payload of the inventory wave, keyed as the
    functions family reads it. The family-register key is named first: it is
    the one the censuses fail loudly without."""
    return collections.OrderedDict([
        ('family_registers', _family_registers()),
        ('mfg_boms', {p.split('/')[-2]: _csv_rows(p) for p in sorted(glob.glob(os.path.join(ROOT, 'models/mfg/*/bom.csv')))}),
        ('mfg_fasteners', {p.split('/')[-2]: _csv_dicts(p) for p in sorted(glob.glob(os.path.join(ROOT, 'models/mfg/*/fasteners.csv')))}),
        ('mfg_tools', _mfg_tools_rows()),
        ('placement', _placement_blocks()),
        ('iso_sheets', _csv_dicts('docs-authority/iso/ISO_SHEETS.csv')),
        ('supports', _supports_counts()),
        ('gas_detectors', _csv_dicts('docs-authority/inventory/GAS_DETECTORS.csv')),
        ('sif_list', _csv_dicts('docs-authority/sif_list.csv')),
        ('nozzle_units', sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, 'docs-authority/nozzles/*.csv')))),
        ('line_positions', _line_positions()),
        ('grounding_grid', _grounding_grid()),
        ('motor_family_boms', {p.split('/')[-2]: _csv_rows(p) for p in sorted(glob.glob(os.path.join(ROOT, 'models/motors/MF-*/bom.csv')))}),
        ('unit_boms', {p.split('/')[-2]: _csv_rows(p) for p in sorted(glob.glob(os.path.join(ROOT, 'models/units/*/bom.csv')))}),
        ('duty_sec3', _duty_sec3()),
        ('piping_classes', _rd('docs-authority/PIPING_CLASSES.md').splitlines()),
    ])


def canonical_inputs():
    """The canonical payload: the declared builder supplies the drivers and
    the site profile; the wave's auxiliary files ride as extra keys."""
    return IN.load(extra=auxiliary_payload().items())


@pytest.fixture(scope='session')
def inputs():
    return canonical_inputs()


def census_model(inputs):
    """The committed seed, computed by the full declared composition."""
    return SL.solve(inputs, REF_GRAPH)


@pytest.fixture(scope='session')
def model(inputs):
    return census_model(inputs)


def committed(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return f.read()


def _csv_bytes(rows, keys=None):
    """The v1 csv.DictWriter face (CRLF rows, QUOTE_MINIMAL) as bytes -- the
    serialization face the reference writers used, replayed here so the
    golden comparison is the committed file itself."""
    s = io.StringIO()
    w = csv.DictWriter(s, keys or list(rows[0].keys()), extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


# ---- golden: the census books re-serialize to the committed CSV bytes ----------

def test_motor_census_matches_committed(model, inputs):
    """The AQS-INV-001 census rows serialize to the committed
    MOTOR_INVENTORY.csv bytes exactly."""
    assert _csv_bytes(INV.motor_rows(model, inputs)) == committed('docs-authority/inventory/MOTOR_INVENTORY.csv')


def test_wire_census_matches_committed(model, inputs):
    """The AQS-INV-002 census rows (merged panels) serialize to the committed
    WIRE_INVENTORY.csv bytes exactly, and the merge book moves copper and
    panel counts the right way."""
    mot = INV.motor_rows(model, inputs)
    wc = INV.wire_census(model, inputs, mot)
    assert _csv_bytes(wc['rows']) == committed('docs-authority/inventory/WIRE_INVENTORY.csv')
    assert wc['pan1'] <= wc['pan0'] and wc['cu1'] <= wc['cu0']   # the merge never adds copper or panels


def test_pipe_census_matches_committed(model, inputs):
    """The AQS-INV-003 line rows serialize to the committed
    PIPE_INVENTORY.csv bytes exactly (the cut lists stay out of the CSV, the
    v1 extrasaction contract)."""
    rows = INV.pipe_rows(model, inputs)
    keys = [k for k in rows[0] if k != 'cuts']
    assert _csv_bytes(rows, keys) == committed('docs-authority/inventory/PIPE_INVENTORY.csv')


def test_other_census_matches_committed(model, inputs):
    """The AQS-INV-004 census rows serialize to the committed
    OTHER_INVENTORY.csv bytes exactly."""
    mot = INV.motor_rows(model, inputs)
    wire = INV.wire_census(model, inputs, mot)['rows']
    assert _csv_bytes(INV.other_rows(model, inputs, mot, wire)) == committed('docs-authority/inventory/OTHER_INVENTORY.csv')


def test_family_rollups_resolve_committed_ids(model, inputs):
    """Every family of every rollup resolves its id from the committed
    register payload -- no family outside its register, so no allocation
    would be needed on the committed tree."""
    mot = INV.motor_rows(model, inputs)
    _, mids = INV.motor_families(mot, inputs)
    wire = INV.wire_census(model, inputs, mot)['rows']
    wfam, _, _ = INV.wire_families(wire, inputs)
    pipe = INV.pipe_rows(model, inputs)
    pfam, _ = INV.pipe_families(pipe, inputs)
    other = INV.other_rows(model, inputs, mot, wire)
    ofam, _, _ = INV.other_families(other, inputs)
    reg = inputs['family_registers']
    used = {'MF': set(mids.values()),
            'WF': {r['family'] for r in wfam},
            'PF': {r['family'] for r in pfam},
            'OF': {r['family'] for r in ofam}}
    for prefix, ids in used.items():
        assert ids, prefix
        assert ids <= set(reg[prefix]['families']), prefix


# ---- determinism ----------------------------------------------------------------

def test_determinism_two_passes_identical_books(inputs):
    """Two independent seed + compute + census passes: identical books."""
    m1, m2 = census_model(inputs), census_model(inputs)
    mo1, mo2 = INV.motor_rows(m1, inputs), INV.motor_rows(m2, inputs)
    assert mo1 == mo2
    assert INV.wire_census(m1, inputs, mo1) == INV.wire_census(m2, inputs, mo2)
    p1, p2 = INV.pipe_rows(m1, inputs), INV.pipe_rows(m2, inputs)
    assert p1 == p2
    assert INV.pipe_families(p1, inputs) == INV.pipe_families(p2, inputs)
    o1, o2 = INV.other_rows(m1, inputs, mo1, INV.wire_census(m1, inputs, mo1)['rows']), \
        INV.other_rows(m2, inputs, mo2, INV.wire_census(m2, inputs, mo2)['rows'])
    assert o1 == o2
    assert INV.other_families(o1, inputs) == INV.other_families(o2, inputs)


# ---- bridge contracts ------------------------------------------------------------

def test_family_allocation_is_enumerated_not_silent(inputs, model):
    """A family key outside the committed register payload raises loudly and
    the register payload is never written back."""
    rows = INV.motor_rows(model, inputs)
    reg_copy = json.loads(json.dumps(inputs['family_registers']))
    INV.motor_families(rows, {'family_registers': reg_copy})
    assert reg_copy == json.loads(json.dumps(inputs['family_registers']))   # no write-back
    stripped = json.loads(json.dumps(inputs['family_registers']))
    stripped['MF']['families'] = {}
    with pytest.raises(KeyError):
        INV.motor_families(rows, {'family_registers': stripped})


def test_absent_payloads_take_the_v1_absent_file_branches(inputs, model):
    """The payload-absence branches: no ISO_SHEETS payload -> an empty pipe
    roster (the retired-sidecar branch); no grounding payload -> no
    grounding row while the committed payload carries one; no mfg BOM
    payload -> no BOM-sourced motor rows (the absent-directory branch); no
    placement payload -> no sub-system comes from a placement block."""
    mot = INV.motor_rows(model, inputs)
    assert INV.pipe_rows(model, {}) == []
    full_wire = INV.wire_census(model, inputs, mot)['rows']
    assert any(r['unit'] == 'GROUND_GRID' for r in full_wire)
    no_gs = {k: v for k, v in inputs.items() if k != 'grounding_grid'}
    assert not any(r['unit'] == 'GROUND_GRID' for r in INV.wire_census(model, no_gs, mot)['rows'])
    bomu = {r['basis'] for r in mot if r['basis'].startswith('BOM')}
    assert bomu
    mot_nobom = INV.motor_rows(model, {k: v for k, v in inputs.items() if k != 'mfg_boms'})
    assert not any(r['basis'].startswith('BOM') for r in mot_nobom)   # the v1 absent-directory branch
    blocks = set(inputs['placement'].values())
    assert not any(r['subsystem'] in blocks for r in INV.motor_rows(model, {k: v for k, v in inputs.items() if k != 'placement'}))


def test_collection_bus_composes_from_the_sections_book(model, inputs):
    """The CB- rows of the wire census compose in memory from the
    SOL_ARK_60K params.sections book (the power family's sections, the
    committed COLLECTION_BUS table's own basis): the breaker rating each
    CB- row cites comes from the book, not from a file parse."""
    mot = INV.motor_rows(model, inputs)
    rows = INV.wire_census(model, inputs, mot)['rows']
    sec_book = (INV._node_view(model).get('SOL_ARK_60K') or {}).get('params', {}).get('sections') or {}
    cb_units = {f'CB-{i + 1}' for i in range(len(sec_book.get('inverters', [])))}
    assert cb_units
    assert {r['unit'] for r in rows if r['subsystem'] == 'collection bus'} >= cb_units
    for i, br in enumerate(sec_book.get('breaker_A', [])[:1]):
        mains = [r for r in rows if r['unit'] == f'CB-{i + 1}' and 'section main' in r['circuit']]
        assert mains and all(str(br) + ' A main' in r['basis'] for r in mains)


def test_the_census_registers_nothing_with_the_solve():
    """The censuses stamp no graph field: no function of the family is in the
    registered solve set (the rows run in the renderer lane only)."""
    mods = {getattr(f, '__module__', '') for f in SL.FNS}
    assert not any(m.endswith('functions.inventory') for m in mods)


# ---- purity ----------------------------------------------------------------------

def test_census_module_pure():
    """No I/O, no banned imports, no float literals in the census family
    module: constants enter as floats of their exact decimals (flo()) and
    file reading stays in the declared payload builders."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(INV.__file__, encoding='utf-8') as f:
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
            raise AssertionError(f'inventory.py:{node.lineno}: file I/O in a census module')
