"""engine v2: the instrument-index census acceptance (the ledger section J
`doc_instr_index` row; reference writer docs-authority/_instr_index.py, the
306-line generator with the embedded authored-loop table).

The family: flow_graph/v2/functions/instrument_index.py. AQS-CTL-001
(X-CTL-01, A-M-193): every AQS-INV-004 instrument (gas detectors excluded) and
every authored loop of the declared AUTH table gets an ISA5_1_2022 tag, a
calibrated range from the graph, a signal and a sector PLC; SIF elements carry
the 90+ numbers (AQS-CTL-003); an inventory row of the same letters wins over
the authored row. The census writes NO graph state -- the rows are boundary
data the renderer lane lays out into INSTRUMENT_INDEX.csv and the AQS-CTL-001
page. The proofs:

- golden: the rows re-serialize to the committed
  docs-authority/inventory/INSTRUMENT_INDEX.csv bytes exactly (field order
  included), the row count matches the committed register, and the
  range-need flags re-derive the committed INSTRUMENT_INDEX.md deviation
  table;
- the v1 gates: duplicate tags raise, and the AUTH-coverage gate (every unit
  the rows do not cover is a graph-class boundary) raises loud when an
  inventory lane is dropped; the inventory-wins merge is shown by a
  synthetic AQS-INV-004 row taking a tag the AUTH table would have authored,
  for a plain and a SIF element;
- integer/string asserts: every tag matches the ISA-5.1 face, SIF-numbered
  rows are 90+, non-SIF rows are 01-89, loop is the tag minus its first
  hyphen, plc is the sector PLC;
- the no-drivers bridge contract: the census computes over the committed seed
  with no solve and no drivers payload at all (the v1 stage ran with
  depends_on (none)), and its book is identical to the full-solve book;
- determinism: two independent seed+solve+census passes, identical books;
- registry: the census registers nothing with the solve registry (the rows
  run in the renderer lane only);
- purity: no I/O, no banned imports, no float literals in the family module.

The auxiliary payload is the committed OTHER_INVENTORY.csv (the AQS-INV-004
book the v1 stage read beside the graph): this module parses it once, at the
declared I/O boundary, and every test passes it down as the inputs payload.
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

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_GRAPH = os.path.join(ROOT, 'flow_graph', 'plant_flow_graph.json')


# ---- the auxiliary payload: the committed AQS-INV-004 book ---------------------

def other_inventory_rows():
    """The committed OTHER_INVENTORY.csv rows (dict rows, the v1 DictReader
    face the census consumes)."""
    with open(os.path.join(ROOT, 'docs-authority/inventory/OTHER_INVENTORY.csv'), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def canonical_inputs():
    """The canonical payload: the declared builder supplies the drivers and
    the site profile; the AQS-INV-004 rows ride as the census key."""
    return IN.load(extra=[('other_inventory', other_inventory_rows())])


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


@pytest.fixture()
def bridge_model():
    """The committed seed with NO solve: the pure bridge builder, frozen."""
    return load(REF_GRAPH).build()


def _csv_bytes(rows):
    """The v1 csv.DictWriter face (CRLF rows, QUOTE_MINIMAL) as bytes -- the
    serialization face the reference writer used, replayed here so the golden
    comparison is the committed file itself."""
    s = io.StringIO()
    w = csv.DictWriter(s, list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    return s.getvalue().encode('utf-8')


def committed_flag_rows():
    """The deviation table of the committed INSTRUMENT_INDEX.md (the
    `Inventory ranges below the need` rows), as tuples."""
    with open(os.path.join(ROOT, 'docs-authority/INSTRUMENT_INDEX.md'), encoding='utf-8') as f:
        lines = f.read().splitlines()
    i = lines.index('## Inventory ranges below the need (should be empty: AQS-INV-004 takes its range from the design pressure)')
    rows = []
    for line in lines[i + 1:]:
        if line.startswith('## '):
            break
        c = [x.strip() for x in line.split('|')[1:-1]]
        if len(c) == 4 and c[0] != 'Tag' and not all(set(x) <= {'-'} for x in c):
            rows.append(tuple(c))
    return rows


# ---- golden: the index re-serializes to the committed CSV bytes -----------------

def test_instrument_index_matches_committed(model, inputs):
    """The AQS-CTL-001 census rows serialize to the committed
    INSTRUMENT_INDEX.csv bytes exactly, field order included."""
    book = II.instrument_book(model, inputs)
    assert list(book['rows'][0].keys()) == ['tag', 'unit', 'sector', 'type', 'spec', 'range', 'signal', 'loop', 'plc', 'basis']
    assert _csv_bytes(book['rows']) == committed_bytes('docs-authority/inventory/INSTRUMENT_INDEX.csv')


def test_row_count_matches_the_committed_register(model, inputs):
    """The book carries exactly the committed register's rows: every payload
    row that passes the filters appends one row, and the rest are the authored
    rows the merge appended (the v1 _nauth)."""
    with open(os.path.join(ROOT, 'docs-authority/inventory/INSTRUMENT_INDEX.csv'), newline='', encoding='utf-8') as f:
        n = sum(1 for _ in csv.DictReader(f))
    book = II.instrument_book(model, inputs)
    ninv = sum(1 for x in inputs['other_inventory']
               if x['category'] == 'instrument' and not x['item'].startswith('gas detector'))
    assert len(book['rows']) == n
    assert book['auth_rows'] == len(book['rows']) - ninv


def test_flags_match_the_committed_deviation_table(model, inputs):
    """The range-need flags re-derive the committed INSTRUMENT_INDEX.md
    deviation table rows."""
    book = II.instrument_book(model, inputs)
    assert [tuple(f) for f in book['flags']] == committed_flag_rows()


# ---- the merge: inventory rows of the same letters win --------------------------

def _with_extra_row(extra):
    payload = other_inventory_rows()
    return {'other_inventory': payload + [dict({'category': 'instrument', 'sector': 'LB', 'spec': 'TEST-INV-SPEC',
                                                'size': '0-2 m', 'basis': 'synthetic: the inventory lane caught up'}, **extra)]}


def test_inventory_row_wins_over_the_authored_row(bridge_model):
    """A synthetic AQS-INV-004 row for an AUTH-table unit takes the tag the
    authored row would have had: the inventory row wins wholesale (spec,
    sector, plc), the authored row is skipped, and the register row count is
    unchanged."""
    golden = II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})
    book = II.instrument_book(bridge_model, _with_extra_row(
        {'unit': 'LB_CHEM_STORE', 'item': 'level transmitter'}))
    assert len(book['rows']) == len(golden['rows'])          # one added, one authored row skipped
    win = [r for r in book['rows'] if r['tag'] == 'LB_CHEM_STORE-LT-01']
    assert len(win) == 1 and len([r for r in golden['rows'] if r['tag'] == 'LB_CHEM_STORE-LT-01']) == 1
    assert win[0]['spec'] == 'TEST-INV-SPEC'                 # the inventory row's spec, not the authored radar
    assert win[0]['sector'] == 'LB' and win[0]['plc'] == 'PLC-LB'   # the inventory row's sector
    assert win[0]['basis'] == 'A-M-182 liquid height'        # the census note, not the authored basis


def test_inventory_sif_element_wins_over_the_authored_sif(bridge_model):
    """The same for a SIF element, on an AUTH-only unit (RES_HEAT carries no
    AQS-INV-004 rows): a synthetic AQS-INV-004 SIF row takes the -90 tag and
    the authored independent element is skipped -- and with it the authored
    plain row of the same letters (the inventory lane wins per letters). The
    win is in the tag slot and the row's sector: the calibrated range and the
    element still come from the graph (the v1 band rule governs inventory rows
    too, so the spec carries the band element, not the inventory cell)."""
    golden = II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})
    book = II.instrument_book(bridge_model, _with_extra_row(
        {'unit': 'RES_HEAT', 'item': 'temperature element (SIF, independent)'}))
    assert len(book['rows']) == len(golden['rows']) - 1     # +1 synthetic, -1 authored plain, -1 authored SIF = 867
    win = [r for r in book['rows'] if r['tag'] == 'RES_HEAT-TE-90']
    assert len(win) == 1 and len([r for r in golden['rows'] if r['tag'] == 'RES_HEAT-TE-90']) == 1
    assert win[0]['sector'] == 'LB' and win[0]['plc'] == 'PLC-LB'   # the inventory row's sector wins
    assert win[0]['range'] == '0 to 1100 C' and win[0]['spec'] == 'type K thermocouple, IEC 60584, Inconel sheath'   # the graph band rules the element
    assert all(r['basis'] != 'independent high-temperature trip (AQS-CTL-003); design T_C 900 C' for r in book['rows'])
    assert not any(r['unit'] == 'RES_HEAT' and r['tag'] == 'RES_HEAT-TE-01' for r in book['rows'])   # the authored plain row of the letters is retired


# ---- the v1 gates ----------------------------------------------------------------

def test_coverage_gate_raises_when_an_inventory_lane_is_dropped(bridge_model):
    """The AUTH-coverage gate: with one unit's inventory instrument rows gone,
    that process unit has no loop and the census raises loud (the v1 assert
    against extending AUTH)."""
    payload = [r for r in other_inventory_rows() if not (r['unit'] == 'EW_1' and r['category'] == 'instrument')]
    with pytest.raises(ValueError, match='process units without a loop'):
        II.instrument_book(bridge_model, {'other_inventory': payload})


def test_no_duplicate_tags_and_the_gates_pass_on_the_committed_tree(bridge_model):
    """On the committed tree the duplicate-tag gate and the AUTH-coverage gate
    pass (instrument_book raises nothing), and the boundary set is the
    graph's four declared trade/bookkeeping boundaries."""
    book = II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})
    tags = [r['tag'] for r in book['rows']]
    assert len(tags) == len(set(tags))
    assert book['boundary_units'] == ['ATMOS', 'BOUNDARY_EXPORT', 'LB_PROD_OUTLET', 'NORTH_DOCK']


# ---- integer/string asserts over the committed book ------------------------------

def test_tag_format_and_sif_numbering(model, inputs):
    """Every tag matches the ISA-5.1 face; SIF-numbered rows are 90+, every
    other row is 01-89; loop is the tag minus its first hyphen; plc is the
    sector PLC."""
    book = II.instrument_book(model, inputs)
    for r in book['rows']:
        m = re.match(r'^([A-Z0-9_]+)-([A-Z]{2,3})-([0-9]{2})$', r['tag'])
        assert m and m.group(1) == r['unit'], r['tag']
        assert r['loop'] == r['tag'].replace('-', '', 1)
        assert r['plc'] == f"PLC-{r['sector']}"
        n = int(m.group(3))
        if '(SIF' in r['type']:
            assert n >= 90, r['tag']                          # AQS-CTL-003: SIF elements numbered 90+
        else:
            assert 1 <= n <= 89, r['tag']


def test_signal_and_range_faces(model, inputs):
    """Signals per IEC61131_2: the level switches and the relief-stack rupture
    switches are discrete, every other loop analog HART (the FEED_PREP mash
    press switch is the declared analog exception, an authored AI choice);
    the ranges are non-empty spec strings."""
    book = II.instrument_book(model, inputs)
    for r in book['rows']:
        assert r['signal'] in ('4-20 mA HART (AI)', '24 V DC discrete (DI)')
        letters = r['tag'].split('-')[-2]
        discrete = letters == 'LSH' or (letters == 'PSH' and r['unit'] in ('RELIEF_CRYO', 'RELIEF_H2'))
        assert ('DI' in r['signal']) == discrete, r['tag']
        assert r['range'] and r['spec'] and r['basis']


# ---- the no-drivers bridge contract ----------------------------------------------

def test_no_drivers_bridge_book_is_the_committed_book(bridge_model):
    """The census computes over the committed seed with no solve and a payload
    that carries no drivers key at all (the v1 stage ran with depends_on
    (none)), and the book is the committed CSV bytes."""
    book = II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})
    assert _csv_bytes(book['rows']) == committed_bytes('docs-authority/inventory/INSTRUMENT_INDEX.csv')


def test_bridge_book_equals_the_full_solve_book(bridge_model, model, inputs):
    """The bridge book (no solve) is identical to the full-solve book: the
    census reads no stamped state the solve changes."""
    assert II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})['rows'] == \
        II.instrument_book(model, inputs)['rows']


# ---- determinism -----------------------------------------------------------------

def test_determinism_two_passes_identical_books(inputs):
    """Two independent seed + solve + census passes: identical books."""
    b1 = II.instrument_book(SL.solve(inputs, REF_GRAPH), inputs)
    b2 = II.instrument_book(SL.solve(inputs, REF_GRAPH), inputs)
    assert b1 == b2


# ---- registry and purity ----------------------------------------------------------

def test_the_census_registers_nothing_with_the_solve():
    """The census stamps no graph field: no function of the family is in the
    registered solve set (the rows run in the renderer lane only)."""
    mods = {getattr(f, '__module__', '') for f in SL.FNS}
    assert not any(m.endswith('functions.instrument_index') for m in mods)


def test_census_module_pure():
    """No I/O, no banned imports, no float literals in the census module:
    constants enter as floats of their exact decimals (flo()) and file reading
    stays in the declared payload builders."""
    banned = {'datetime', 'random', 'uuid', 'time', 'tempfile'}
    with open(II.__file__, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split('.')[0] not in banned, f'instrument_index.py: banned import {a.name}'
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or '').split('.')[0] not in banned, f'instrument_index.py: banned import from {node.module}'
        elif isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f'instrument_index.py:{node.lineno}: float literal'
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'open':
            raise AssertionError(f'instrument_index.py:{node.lineno}: file I/O in a census module')


def test_auth_table_is_declared_data(bridge_model):
    """The AUTH table: one 8-field row per authored loop (unit, letters, type,
    spec, range, signal, basis, sif), every unit on the graph, letters upper
    case, sif a bool, signals on the two IEC61131_2 faces -- and the book
    carries exactly the rows the merge appends (the v1 _nauth)."""
    N = set(bridge_model.nodes)
    assert len(II.AUTH) == 189                              # the reference writer's A() row count
    for row in II.AUTH:
        u, L, typ, spec, rng, sig, basis, sif = row
        assert isinstance(u, str) and u in N, f'authored unit {u} not on the graph'
        assert isinstance(L, str) and L.isupper()
        assert isinstance(typ, str) and isinstance(spec, str)
        assert isinstance(rng, (str, tuple)) and isinstance(basis, (str, tuple))
        assert sig in (II.AI, II.DI)
        assert isinstance(sif, bool)
    book = II.instrument_book(bridge_model, {'other_inventory': other_inventory_rows()})
    ninv = sum(1 for r in other_inventory_rows()
               if r['category'] == 'instrument' and not r['item'].startswith('gas detector'))
    assert book['auth_rows'] == len(book['rows']) - ninv    # every appended row is inventory or authored
