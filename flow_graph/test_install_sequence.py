"""X-ASM-01 gate: the install sequence covers every structural row, agrees with the
AQS-BLD-015 hoist book, and the built-in-place rule matches the lifting generator verbatim."""
import ast
import collections
import json
import os
import re

sys_dir = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(sys_dir)
DOC = os.path.join(R, 'docs-authority/INSTALL_SEQUENCE.md')
ROWS = os.path.join(R, 'docs-authority/inventory/STRUCT_ROWS.json')

LEVELS = ['L-2', 'L-1', 'L0', 'L1', 'R1', 'R2', 'R3', 'ROOF']


def test_doc_header_and_rules():
    src = open(DOC).read()
    assert src.startswith('# Install sequence')
    assert 'Document number: AQS-ASM-002' in src and 'Revision: A' in src
    ## the registered rules are carried in section 1
    assert 'next standard size at or above the heaviest lift + 10 %' in src
    assert 'load test 125 % of rated (ASME B30.2)' in src
    assert 'Built-in-place classes are assembled on the level' in src


def test_all_units_sequenced_per_level():
    rows = json.load(open(ROWS))
    per_level = collections.Counter(r['level'] for r in rows)
    src = open(DOC).read()
    seq_units = []
    for lv in LEVELS:
        if per_level[lv] == 0:
            continue
        m = re.search(rf'^## {re.escape(lv)} \((\d+) units?, ', src, re.M)
        assert m, f'no section for {lv}'
        assert int(m.group(1)) == per_level[lv], f'{lv}: {m.group(1)} booked {per_level[lv]}'
    ## the seat tables list every booked unit exactly once
    seq_units = re.findall(r'^\| \d+ \| ([A-Za-z0-9_/]+) \| \d+ \| \d+ \| (built in place|hoist) \|', src, re.M)
    assert len(seq_units) == len(rows)
    assert {u for u, _p in seq_units} == {r['unit'] for r in rows}


def test_hoist_book_cross_check_clean():
    src = open(DOC).read()
    assert 'Cross-check mismatch' not in src


def test_heavy_lift_roster():
    src = open(DOC).read()
    assert 'AQS-ASM-002' in src      # the roster is declared as the AQS-ASM-002 work order
    ## every roster entry under the 1.0 t cut is declared as such, no silent gaps
    assert src.count('(level book; under the 1.0 t roster cut)') == 1   # L-2 only
    l1 = re.search(r'^\| L1 \| (.+) \| 10\.0 \| 12\.5 \|$', src, re.M)
    assert l1 and 'AZOLLA_BED / 5400' in l1.group(1)


def test_inplace_rule_matches_lifting_generator():
    """The built-in-place classes must stay identical between this generator and _lifting.py
    (AQS-BLD-015): two copies of a hoist-classification rule drift otherwise."""
    def _set(path):
        src = open(path).read()
        m = re.search(r'^INPLACE = (\{.*?\})$', src, re.M)
        assert m, path
        return ast.literal_eval(m.group(1))
    a = _set(os.path.join(R, 'docs-authority/_install_seq.py'))
    b = _set(os.path.join(R, 'docs-authority/_lifting.py'))
    assert a == b


def test_no_booking_marker_in_covered_edges():
    """Every '(no structural booking)' connect names a partner outside the AQS-BLD-013 census."""
    src = open(DOC).read()
    rows = json.load(open(ROWS))
    booked = {r['unit'] for r in rows}
    g = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
    markers = re.findall(r'(\S+) -> (\S+) \(no structural booking\)', src)
    assert markers, 'roster expects unbooked partners to be named, none found'
    for _stream, p in markers:
        assert p not in booked, p
