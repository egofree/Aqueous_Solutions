"""X-INV-03-WF gate: AQS-INV-007 (WIRE_SPECS.md) carries one specification and production
plan per wire family, arithmetic traced to WIRE_SPECS.json, every standard key registered,
and the open part (production runs, type tests) named rather than claimed."""
import csv
import json
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(here)
DOC = os.path.join(R, 'docs-authority/WIRE_SPECS.md')
ROWS = json.load(open(os.path.join(R, 'docs-authority/inventory/WIRE_SPECS.json')))
FAM = list(csv.DictReader(open(os.path.join(R, 'docs-authority/inventory/WIRE_FAMILIES.csv'))))


def test_header_and_rev_history():
    src = open(DOC).read()
    assert src.startswith('# Wire family specifications and production plans')
    assert 'Document number: AQS-INV-007' in src and 'Revision: C' in src
    assert 'X-INV-03-WF-01..26' in src
    assert '| A | First issue' in src and '| C | Board evidence issue' in src
    ## the open part of the Done-when is named, not claimed
    assert 'production runs and type tests are the open part' in src


def test_one_sheet_per_family_with_all_elements():
    src = open(DOC).read()
    sheets = re.findall(r'^### (WF-\d+): ', src, re.M)
    assert sheets == [r['family'] for r in FAM] == [r['fam'] for r in ROWS]
    ## every sheet covers the Done-when elements: drawing, stranding, insulation extrusion, test
    for r in ROWS:
        s = src.split(f"### {r['fam']}:", 1)[1].split('###')[0]
        assert f"drawings/wire/{r['fam']}.svg" in s, r['fam']
        assert f"{r['n']} x {r['ds']:.3f} mm soft Cu" in s, r['fam']
        if 'bare' in r['ins']:
            assert abs(r['D'] - r['Dc']) < 0.01 and 'insulation' not in s, r['fam']
        else:
            assert f"{r['D']:.2f} mm" in s and r['D'] > r['Dc'], r['fam']
        assert 'passes from 8 mm rod' in s, r['fam']
    ## the common production plan names the WIRE_DRAW line steps end to end
    plan = src.split('## 2. Production plan', 1)[1].split('## 3.', 1)[0]
    for step in ('Rod:', 'Drawing:', 'Anneal:', 'Strand:', 'Insulate:', 'Spark test', 'Routine tests per reel'):
        assert step in plan, step


def test_arithmetic_and_roster_match_the_csv_and_json():
    src = open(DOC).read()
    by_fam = {r['fam']: r for r in ROWS}
    for f in FAM:
        r = by_fam[f['family']]
        assert r['L'] == float(f['conductor_m']) and r['size'] == f['size']
        m = re.search(rf'^### {r["fam"]}:.*?\n', src, re.S)
        ## the sheet's conflated length and circuit counts match the CSV roster
        use = re.search(rf"### {r['fam']}:[^\n]*\n\nUse: {int(f['circuits'])} circuits", src)
        assert use, r['fam']
        assert r['R20'] > 0 and r['a'] > 0
    ## summary totals
    tot = re.search(r'(\d+) families, ([\d.]+) km of conductor, ([\d,]+) kg copper', src)
    assert int(tot.group(1)) == len(FAM)
    assert abs(float(tot.group(2)) - sum(r['L'] for r in ROWS) / 1000) < 0.05
    assert int(tot.group(3).replace(',', '')) == round(sum(r['cu'] for r in ROWS))
    ## drawings exist for every family and are committed
    for r in ROWS:
        assert os.path.exists(os.path.join(R, f'docs-authority/drawings/wire/{r["fam"]}.svg'))


def test_standard_keys_registered():
    from flow_graph.param import refs
    stds = set()
    for r in ROWS:
        stds.update(k.strip() for k in r['std'].split('/'))
    missing = {k for k in stds if k not in refs.REFS}
    assert not missing, missing
