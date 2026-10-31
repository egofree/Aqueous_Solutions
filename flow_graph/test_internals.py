"""AQS-DSN-INT-001 gate (unit task 06 sweep): INTERNALS.md is the per-unit internals
disposition register. Closes carry issued evidence (named document or quoted sized
statement), the keyword-guarded 'none' class rules never swallow a booked internal, and
the open set is named design gaps only - nothing invented. The former task 09 hold
(Selection pending) is gone since X-MAT-22 (AQS-STD-006)."""
import json
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
DOC = os.path.join(R, 'docs-authority/INTERNALS.md')
IN = json.load(open(os.path.join(R, 'docs-authority/inventory/INTERNALS.json')))
G = json.load(open(os.path.join(R, 'flow_graph/plant_flow_graph.json')))
UNITS = {n['unit_id'] for n in G['nodes'] if n.get('class') != 'boundary' and n.get('sector_id') and n.get('presence') == 'present'}


def test_header_and_method():
    src = open(DOC).read()
    assert src.startswith('# Unit internals register')
    assert 'Document number: AQS-DSN-INT-001' in src and 'Revision: A' in src
    # nothing invented: closes carry issued documents, opens are named gaps
    assert 'Nothing here invents an internal' in src
    assert '| A | First issue' in src
    assert '## 4. Open units (named gaps)' in src


def test_every_roster_unit_is_accounted_for():
    defined = set(IN['defined'])
    none_u = set(IN['none'])
    open_u = set(IN['open'])
    assert defined <= UNITS and none_u <= UNITS and open_u <= UNITS
    assert defined | none_u | open_u == UNITS, UNITS - (defined | none_u | open_u)
    src = open(DOC).read()
    for u in defined:
        assert f'| {u} |' in src, u
    for u in open_u:
        assert f'| {u} | ' in src, u


def test_closes_cite_real_issued_sources():
    # every 'defined' basis names an existing artifact (or the materials standard section)
    for u, basis in IN['defined'].items():
        m = re.search(r'\[([^\]]+)\]$', basis)
        assert m, (u, basis)
        ref = m.group(1)
        assert 'MATERIALS_STD.md' in ref or f'unit_materials' in ref or 'section 4.5' in ref or \
            os.path.exists(os.path.join(R, 'docs-authority', ref)) or \
            os.path.exists(os.path.join(R, ref)), (u, ref)
    # spot-checks: the EW electrode array, the house scrubber beds, the BMED triplet
    # construction, the HX8 bundle, and the LEACH agitator are the named evidence
    for u, needle in (('EW_1', 'cathode pitch'), ('ALK_SCRUBBER', 'packed bed per scrubber'),
                      ('BMED_ACID', 'mesh spacers'), ('HX8', 'PVDF bundle'),
                      ('LEACH_CSTR_1', 'agitator')):
        assert needle in IN['defined'][u], (u, IN['defined'][u])


def test_open_set_is_a_named_gap_after_xmat22():
    open_u = IN['open']
    # X-MAT-22 (AQS-STD-006) closed the task 09 hold: the pot cells, the metallurgy train and
    # the service units of that hold are now defined on issued section 3 / mfg-BOM evidence
    assert not any('same hold as task 09' in b for b in open_u.values())
    for u in ('AL_POT', 'MG_POT', 'CA_POT', 'TI_CELL', 'H2O_ELYZ'):
        assert u in IN['defined'], u
    # the neither-defined-nor-held units name the real design gap per class. VCD_TRAIN, Q1_A and
    # H2_DRYER left this set at the 2026-10-30 internals pass: their designs issued (the MVC
    # stack, the AQS-DUTY-008 sec. 14 battery internals, the molecular-sieve beds).
    # the open set is empty: every present unit has a disposition (the 2026-10-30
    # internals pass issued explicit dispositions for the last 6 units: BAGHOUSE,
    # CRU, CRYO_N2, GREY_TREAT, OIL_FRAC and ZNBR2)
    assert not open_u, sorted(open_u)
    # none of the open units may be rendered as closed
    src = open(DOC).read()
    for u in open_u:
        assert f'### {u}\n' not in src, u
