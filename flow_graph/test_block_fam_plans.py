"""X-INV-05-OF gate: AQS-INV-009 (BLOCK_FAMILY_PLANS.md) carries one production plan per
building-block family, the design side joined by reference to AQS-PRO-002 (the bought families),
OF-13 pointed at the in-house fabricated-part sheets, and no invented datasheet content."""
import csv
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
DOC = os.path.join(R, 'docs-authority/BLOCK_FAMILY_PLANS.md')
FAM = list(csv.DictReader(open(os.path.join(R, 'docs-authority/inventory/OTHER_FAMILIES.csv'))))
BS = open(os.path.join(R, 'docs-authority/BOUGHT_SPECS.md')).read()


def test_header_and_rules():
    src = open(DOC).read()
    assert src.startswith('# Building-block family production plans')
    assert 'Document number: AQS-INV-009' in src and re.search(r'^Revision: [A-Z]+$', src, re.M)
    assert 'tasks X-INV-05-OF of AQS-PLAN-007' in src
    ## the design rule is stated and honest: standard class is the design, reference not duplication
    assert 'is designed by its standard class' in src
    assert 'is cited in Table 4.1 and not repeated' in src
    assert '| A | First issue' in src


def test_one_row_per_family_with_plan_column():
    src = open(DOC).read()
    rows = re.findall(r'^\| (OF-\d+) \| ([a-z ]+) \| ([^|]+) \| ([^|]+) \| (\d+) \| (\d+) \| ([^|]+) \| ([^|]+) \|$', src, re.M)
    assert [r[0] for r in rows] == [f['family'] for f in FAM]
    by_csv = {f['family']: f for f in FAM}
    seen_plans = set()
    for fam, cat, item, spec, qty, units, design, plan in rows:
        f = by_csv[fam]
        assert (item.strip(), spec.strip()) == (f['item'], f['spec']), fam
        assert (qty, units) == (f['qty'], f['units']), fam
        assert plan.strip(), fam
        seen_plans.add(plan.strip())
    ## per-category plan text is shared (per truly distinct categories, not per family)
    assert len(seen_plans) <= len({f['category'] for f in FAM})


def test_design_joins_resolve():
    src = open(DOC).read()
    bought = [f for f in FAM if f['category'] != 'fabricated part']
    ## every bought family has a datasheet row, and AQS-PRO-002 has no row for a family the inventory lacks
    assert {f['family'] for f in bought} == set(re.findall(r'^\| (OF-\d+) \|', BS, re.M))
    ## every bought family must find its id as a datasheet row in AQS-PRO-002
    for f in bought:
        m = re.search(rf'^\| {f["family"]} \| {re.escape(f["item"])} \| {re.escape(f["spec"])} \|', BS, re.M)
        assert m, f['family']
        assert f'AQS-PRO-002 sheet' in src.split(f'### {f["family"]}:', 1)[-1] or \
            f'| {f["family"]} | {f["category"]} | {f["item"]} | {f["spec"]} | {f["qty"]} | {f["units"]} | AQS-PRO-002 sheet' in src, f['family']
    ## the fabricated family points at the issued in-house sheets, never at a purchase
    assert 'In-house sheets models/mfg/<unit>/bom.csv and WORK_ORDER.md' in src


def test_the_open_parts_are_named():
    src = open(DOC).read()
    ## maker-table holds stay named ahead of order (X-GOV-20-safe wording)
    assert 'maker-table' in src and 'AQS-STD-002 section 14' in src
    assert 'Shop execution stays the open part' in src
