"""X-PRO-02 gate: a datasheet row per bought AQS-INV-004 family, fabricated parts excluded."""
import csv
import os
import re

sys_dir = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(sys_dir)
FAM = os.path.join(R, 'docs-authority/inventory/OTHER_FAMILIES.csv')
SPECS = os.path.join(R, 'docs-authority/BOUGHT_SPECS.md')


def _bought_families():
    with open(FAM) as f:
        rows = [r for r in csv.DictReader(f) if r['category'] != 'fabricated part']
    return rows


def test_doc_header():
    src = open(SPECS).read()
    assert src.startswith('# Bought-item specification sheets')
    assert 'Document number: AQS-PRO-002' in src
    assert 'Revision: A' in src


def test_family_coverage():
    src = open(SPECS).read()
    for r in _bought_families():
        assert r['family'] in src and r['spec'] in src, r['family']
    fab = next(r['family'] for r in csv.DictReader(open(FAM))
               if r['category'] == 'fabricated part')
    assert f'the excluded one is {fab}' in src and 'in-house work' in src   # the excluded fabricated-part family is named


def test_totals_match_the_inventory():
    src = open(SPECS).read()
    total = sum(int(r['qty']) for r in _bought_families())
    assert f'Bought families covered: {len(_bought_families())} of {len(_bought_families()) + 1}' in src
    ## the roster table must not leak the fabricated-part qty
    assert re.search(r'\| fabricated part \|', src) is None
    ## the datasheets carry every bought item of the inventory: the family quantities add up to the inventory's bought rows
    inv = sum(int(r['qty']) for r in csv.DictReader(open(os.path.join(R, 'docs-authority/inventory/OTHER_INVENTORY.csv')))
              if r['category'] != 'fabricated part')
    assert total == inv
