"""X-ASM-02 gate: one rigging plan per >1000 kg lift, ratings verbatim from AQS-BLD-015,
arithmetic checked, lift points left as named work-order holds (no invented load paths)."""
import os
import re

sys_dir = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(sys_dir)
DOC = os.path.join(R, 'docs-authority/RIGGING_PLANS.md')
SEQ = os.path.join(R, 'docs-authority/INSTALL_SEQUENCE.md')


def test_doc_header_and_rules():
    src = open(DOC).read()
    assert src.startswith('# Rigging plans')
    assert 'Document number: AQS-ASM-003' in src and 'Revision: A' in src
    ## AQS-BLD-015 verbatim
    assert 'Rigging allowance 10 %' in src
    assert 'Load test 125 % of rated (ASME B30.2' in src
    assert 'CMAA70' in src and 'ASME B30.16' in src
    ## the honesty rule: lift points stay open, not modeled
    assert 'Lift points are named at the unit work order' in src


def test_one_plan_per_roster_lift():
    src = open(DOC).read()
    plans = re.findall(r'^### Plan (\d+): (\S+) to (L-?\d+|ROOF)$', src, re.M)
    assert len(plans) == 15
    ## roster rows agree with the plans, same order and numbering
    roster = re.findall(r'^\| (\d+) \| (L-?\d+|ROOF) \| (\S+) \| \d+ \| \d+ \| [\d.]+ \| [\d.]+ \|$', src, re.M)
    assert [(n, u, lv) for n, lv, u in roster] == plans
    ## every planned unit is a heavy lift of the AQS-ASM-002 sequence
    seq = open(SEQ).read()
    assert plans, 'no plans parsed'
    for _n, unit, _lv in plans:
        assert f'{unit} / ' in seq, unit


def test_design_load_arithmetic():
    src = open(DOC).read()
    for m in re.finditer(r'- \*\*Mass per lift\*\*: (\d+) kg.*?\n- \*\*Design load\*\*: \1 x 1\.10 = (\d+) kg\.',
                         src, re.S):
        mass, design = int(m.group(1)), int(m.group(2))
        assert abs(design - mass * 1.10) <= 0.5, (mass, design)   # doc shows the mass rounded to the kg


def test_lift_points_are_open_holds():
    src = open(DOC).read()
    plans = src.count('### Plan ')
    holds = src.count('**Lift points**: open item on the')
    assert plans == holds >= 15
