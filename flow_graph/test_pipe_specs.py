"""X-INV-04-PF gate: AQS-INV-006 (PIPE_SPECS.md) carries one production plan per pipe family,
joined to the issued class sheets (AQS-PIP-003) and WPS register (AQS-WLD-002), arithmetic
traced to PIPE_FAMILIES.csv, and the making-route disposition honest (no pipe line booked)."""
import csv
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
DOC = os.path.join(R, 'docs-authority/PIPE_SPECS.md')
FAM = list(csv.DictReader(open(os.path.join(R, 'docs-authority/inventory/PIPE_FAMILIES.csv'))))


def test_header_and_dispositions():
    src = open(DOC).read()
    assert src.startswith('# Pipe family production plans')
    assert 'Document number: AQS-INV-006' in src and re.search(r'^Revision: [A-Z]+$', src, re.M)
    assert 'tasks X-INV-04-PF of AQS-PLAN-007' in src
    ## the honesty core: the making route is a named disposition, not an assumed machine
    assert 'No unit on the plant graph extrudes plastic pipe or forms metal tube' in src
    assert 'open capital option' in src
    assert '| A | First issue' in src


def sheet_of(src, fam):
    return src.split(f'### {fam}:', 1)[1].split('###')[0]


def test_one_sheet_per_family_with_the_fixed_elements():
    src = open(DOC).read()
    sheets = re.findall(r'^### (PF-\d+): ', src, re.M)
    assert sheets == [f['family'] for f in FAM]
    for f in FAM:
        s = sheet_of(src, f['family'])
        for needle in ('m of pipe in', 'mill stock', 'elbows to', 'joints are made to', 'It is tested to'):
            assert needle in s, (f['family'], needle)
        assert f"{f['pipe_m']} m of pipe in {f['lines']} lines" in s
        assert f"{f['stock_lengths_6m']} stock lengths of 6.096 m" in s
        assert f"cutting allowance of {f['offcut_m']} m" in s
        assert f['elbow_std'] in s and f['flange_std'] in s, f['family']
        assert f"{f['joints']} joints" in s


def test_class_and_wps_joins_resolve():
    src = open(DOC).read()
    pip = open(os.path.join(R, 'docs-authority/PIPING_CLASSES.md')).read()
    ## roster rows: family | class | DN | material in the desk's own roster
    for f in FAM:
        assert f'### {f["family"]}: {f["cls"]} DN{f["DN"]}, {f["material"]}' in src, f['family']
        s = sheet_of(src, f['family'])
        assert f"class sheet {f['cls']} of AQS-PIP-003" in s
        assert f['cls'] in {m.group(1) for m in re.finditer(r'^\| (P[1-5]|M[12]|F1) \|', pip, re.M)}
        assert f"\n| {f['family']} | {f['cls']} | {f['DN']} | {f['material']} |" in src
    ## every sheet names an issued WPS id that exists in the register
    wps = open(os.path.join(R, 'docs-authority/WPS_REGISTER.md')).read()
    ids = set(re.findall(r'^\| (WPS-\d+) \|', wps, re.M))
    for f in FAM:
        w = re.search(r'joints are made to (WPS-\d+):', sheet_of(src, f['family']))
        assert w and w.group(1) in ids, f['family']


def test_totals_reconcile_to_the_csv():
    src = open(DOC).read()
    summary = src.split('## 2. Summary and rules', 1)[1].split('## 3.', 1)[0]
    tot_m = sum(float(f['pipe_m']) for f in FAM)
    tot_len = sum(int(f['stock_lengths_6m']) for f in FAM)
    tot_j = sum(int(f['joints']) for f in FAM)
    tot_el = sum(int(f['elbows_90']) for f in FAM)
    m = re.search(rf'{len(FAM)} families with ([\d,.]+) m of pipe in (\d+) lines\. The pipe is delivered as (\d+) stock lengths', summary)
    assert m and float(m.group(1).replace(',', '')) == tot_m, 'pipe m total'
    assert int(m.group(3)) == tot_len, 'stock-length total'
    j = re.search(r'(\d+) elbows and (\d+) flange sets and have (\d+) joints', summary)
    assert j and int(j.group(1)) == tot_el and int(j.group(3)) == tot_j
