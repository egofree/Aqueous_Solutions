"""AQS-STD-005 gate (unit task 09 sweep): UNIT_MATERIALS.md is the per-unit join of the
AQS-PIP-004 wetted census to the issued AQS-STD-002 section 12 families - no new selection,
every wetted edge resolved, no wetted row left in a catch-all, and the open set named with
reasons that match the duty sheets and the pending brine family."""
import json
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
DOC = os.path.join(R, 'docs-authority/UNIT_MATERIALS.md')
UM = json.load(open(os.path.join(R, 'docs-authority/inventory/UNIT_MATERIALS.json')))
G = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
UNITS = {n['unit_id'] for n in G['nodes'] if n.get('class') != 'boundary' and n.get('sector_id')}


def test_header_and_method():
    src = open(DOC).read()
    assert src.startswith('# Per-unit material selections')
    assert 'Document number: AQS-STD-005' in src and 'Revision: A' in src
    ## the selection is not made here - it is the issued section 12 join, with its bounding check cited
    assert 'No selection is made here' in src
    assert 'AQS-ASSAY-001 Rev C bounding cases' in src
    assert 'every one resolves to an issued family' in src
    assert '| A | First issue' in src


def test_every_roster_unit_is_accounts_for():
    src = open(DOC).read()
    issued = set(UM['issued'])
    assert issued <= UNITS, issued - UNITS
    open_units = set(UM['open'])
    assert open_units <= UNITS
    assert issued | open_units == UNITS, UNITS - (issued | open_units)
    ## every issued unit has a sheet; every open unit is in the section 4 table with a reason
    for u in issued:
        assert f'### {u}\n' in src, u
    for u in open_units:
        m = re.search(rf'^\| {u} \| [^|]+\|$', src, re.M)
        assert m, u


def test_wetted_sheets_match_the_line_list():
    src = open(DOC).read()
    # roster of wetted rows per unit, parsed the same way the generator does
    ll = open(os.path.join(R, 'docs-authority/LINE_LIST.md')).read().split('| Line |', 1)[1]
    per_unit = {}
    for ln in ll.splitlines():
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) < 6 or not c[0] or c[0] in ('Line', 'From') or set(c[0]) <= set('- '):
            continue
        line, frm, to, dn, cls, svc = c[:6]
        if svc in ('—', '-', 'Service', 'Length m'):
            continue
        for u in (frm, to):
            per_unit.setdefault(u, set()).add(line)
    no_wetted = []   # issued units with no wetted stream must say so
    for u in UM['issued']:
        s = src.split(f'### {u}\n', 1)[1].split('### ', 1)[0]
        if per_unit.get(u):
            seen = {m2.group(1) for m2 in re.finditer(r'^\| ([A-Za-z0-9_-]+) \| [^|]+ \| [^|]+ \| [^|]+ \| 12\.[12] ', s, re.M)}
            missing = per_unit[u] - seen
            assert not missing, (u, missing)
            assert any(t in s for t in ('CPVC Sch 80', 'PVC-U', '316L', 'PVDF', 'HDPE', 'PP-H', 'Carbon steel', 'FRP', 'Hastelloy', 'carbon steel', 'Not piped', 'hot face')), u
        else:
            no_wetted.append(u)
            assert 'No wetted piped stream' in s, u
    assert len(no_wetted) == len([u for u in UM['issued'] if not per_unit.get(u)])


def test_the_open_set_is_the_named_pending_work():
    src = open(DOC).read()
    ## the pot cells and the pending brine family are open, by name, and nothing closes them
    open_units = set(UM['open'])
    assert 'CA_POT' in open_units and 'MG_POT' in open_units and 'TI_CELL' in open_units
    for u in ('CA_POT', 'MG_POT', 'TI_CELL'):
        assert 'pending brine family' in src.split(f'| {u} |', 1)[1], u
    ## the open units are never rendered as issued
    for u in open_units:
        assert f'### {u}\n' not in src or src.split(f'### {u}\n', 1)[1].split('### ', 1)[0].startswith('\nNo wetted'), u
    assert 'Nothing here selects for them' in src
