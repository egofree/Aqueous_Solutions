"""X-INV-05-OF building-block family production plans (AQS-INV-009).

One production plan per other-building-block family in inventory/OTHER_FAMILIES.csv
(AQS-INV-004), joined to the issued authorities instead of re-deriving them:

  - the open design of a bought family IS its standard class (AQS-PRO-002 rule: the shop buys
    to a standard class, not a marque; no internals are invented). The datasheet row per family
    is AQS-PRO-002, joined here by family id;
  - what AQS-PRO-002 deliberately does not carry - the production plan - is issued here per
    category: procurement to the class, receipt identity and count, storage, the issue path to
    the assembly or installation work order, and the post-installation tie (loop check to
    AQS-CTL-001/002, seal class to AQS-STD-002 section 14, bolting to the class standard,
    spares per X-OPS-03);
  - the one fabricated family (OF-13, fabricated part sets) is in-house work: its design and
    production plan are the issued models/mfg/<unit>/bom.csv and WORK_ORDER.md sheets, and the
    plan points there rather than duplicating.

No rate, dimension or rating is invented beyond the registered class sheets; the desk states
store/issue/receipt discipline (which is desk work) and names the shop execution as the open
part. Outputs docs-authority/BLOCK_FAMILY_PLANS.md. Run: python3 docs-authority/_block_fam_plans.py
"""
import collections, csv, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)

FAM = list(csv.DictReader(open('docs-authority/inventory/OTHER_FAMILIES.csv')))
assert FAM, 'no other families'

# the AQS-PRO-002 datasheet row per family (family id -> row tuple) and the section it sits in
BS = {}
BS_SEC = {}
for line_no, line in enumerate(open('docs-authority/BOUGHT_SPECS.md')):
    m2 = re.match(r'^## (\d+\. .*?)$', line)
    if m2:
        _sec = m2.group(1)
    m3 = re.match(r'^\| (OF-\d+) \| ', line)
    if m3:
        BS[m3.group(1)] = line.strip()
        BS_SEC[m3.group(1)] = _sec

# per-category production plan (desk work the shop executes; execution stays open)
PLAN = {
 'bearing': ('Bought to the ISO class, receipt count and identity check, stored dry in the sealed original '
   'packing, issued with the motor or fan build work order they were counted for (AQS-INV-005/A-M-126 lineage); '
   'press fits follow the ISO 15 seat the class fixes; spares carried per X-OPS-03 (900 building-block spares '
   'booked fleet-wide).'),
 'electronics': ('Bought to the IEC class, receipt count and identity check, stored dry and electrostatic-safe in '
   'the sealed original packing, issued to the panel or controller build the count was booked for (AQS-CTL-002 '
   'module counts per PLC); wired channels verified against the AQS-CTL-002 I/O tables at build and commissioning; '
   'spares per X-OPS-03.'),
 'instrument': ('Bought to the device class; the per-tag range, signal and loop stay on AQS-CTL-001 (a family here '
   'carries the physical device class and the sizes in use, not loop data). Receipt identity and count, dry storage, '
   'issue with the tagged loop, function-checked against the AQS-CTL-001 range at install and swept once more at '
   'commissioning (AQS-CTL-002/CL-004 tie). Spares: the AQS-INV-004 spares roster (X-OPS-03).'),
 'protection': ('Bought to the class, receipt identity and count, issued to the panel the count is booked on; the '
   'trip coordination itself is AQS-CTL-003, not the device sheet.'),
 'seal': ('Seal class (EPDM/FKM/PTFE seat class) and the EN 12756 mechanical-seal tie are AQS-STD-002 section 14; '
   'the maker-table lines still open there (FKM grade, EPDM Q3 compound) stay named on this sheet as gate items '
   'ahead of order. Fitted with the pump or mixer build work order; spares per X-OPS-03.'),
 'support': ('Fitted during piping erection on the routed line the count was booked from (AQS-ISO-002/CAD); '
   'material and coating match the pipe class sheet they support (AQS-PIP-003 letter); spares per X-OPS-03.'),
 'valve': ('Bought to the valve class with the seal class named (AQS-STD-002 section 14); the actuator family '
   'fail-safe orientation settled with AQS-CTL-003. Receipt identity and count, issued with the line the count was '
   'booked from, function-checked open/close at the class hydro; position-verification devices verified against '
   'their AQS-CTL-001 tag at commissioning. Spares per X-OPS-03.'),
 'fastener': ('Bought to the threaded standard of the joint they serve (B16.5 stud bolting in the pipe class '
   'sheets, machine screws per the host assembly standard); torqued at assembly to the host standard; spares per '
   'X-OPS-03.'),
 'fabricated part': ('In-house work, not a purchase: the design and production plan are the issued '
   'models/mfg/<unit>/bom.csv and WORK_ORDER.md sheets (A-M-183 unit BOMs; fabrication routes per AQS-PLAN-005 '
   'with H/W/R hold points); the shop fabricates, the QC traveller records it. This sheet points there and does '
   'not duplicate.'),
}
MAKER = 'maker-table'   # the registered X-GOV-20-safe phrasing where a datasheet waits on the maker table

md = ['# Building-block family production plans', '',
      'Document number: AQS-INV-009', 'Revision: A', 'Date: 2026-10-21',
      'Authority: AQS-PLAN-007 X-INV-05-OF-01..65. Generated by `docs-authority/_block_fam_plans.py` from '
      '`inventory/OTHER_FAMILIES.csv` (AQS-INV-004); the design side joins the AQS-PRO-002 datasheet rows. Study. Not a PE stamp.',
      '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: one production plan per family, design side joined by reference to AQS-PRO-002. | 2026-10-21 |']

cnt = collections.Counter(f['category'] for f in FAM)
md += ['', '## 1. Summary and rules', '',
       f'{len(FAM)} families: ' + ', '.join(f'{n} {c}' for c, n in sorted(cnt.items(), key=lambda x: -x[1])) + '.',
       '',
       '- **Open design, stated once**: for the 64 bought families the standard class IS the open design '
       '(AQS-PRO-002 rule: bought to a standard class, internals of the class, no invented datasheet row); the '
       'per-family datasheet row of AQS-PRO-002 is joined below by reference and not repeated.',
       '- **Production plan per category** (section 3 families, section 2 plan text): receipt identity and count, '
       'dry storage, the issue path to the assembly or installation work order, and the post-installation tie '
       '(loop check to AQS-CTL-001/002, seal class to AQS-STD-002 section 14, bolting to the joint standard, '
       'spares per X-OPS-03). Shop execution stays the open part of the work; nothing here books a run.',
       '- **The fabricated family (OF-13)**: its design and production plan are the issued '
       'models/mfg/<unit>/bom.csv and WORK_ORDER.md sheets; this sheet points there.']

md += ['', '## 2. Production plan by category', '']
for c, n in sorted(cnt.items(), key=lambda x: -x[1]):
    md += [f'### {c} ({n} families)', '', PLAN[c], '']

md += ['', '## 3. Family plans', '', '| Family | Category | Item | Standard class | Qty | Units | Design row | Plan |',
       '|---|---|---|---|---|---|---|---|']
for f in FAM:
    fid = f['family']
    if fid in BS:
        design = f'AQS-PRO-002 sheet, {BS_SEC[fid]}'
    elif f['category'] == 'fabricated part':
        design = 'in-house: models/mfg/<unit>/bom.csv + WORK_ORDER.md'
    else:
        raise SystemExit(f'{fid}: no design row and not the fabricated family')
    md.append(f"| {fid} | {f['category']} | {f['item']} | {f['spec']} | {f['qty']} | {f['units']} | {design} | {PLAN[f['category']].split(';')[0].rstrip('.')}. |")

md += ['', '## 4. Coverage', '',
       f'- One plan per family: {len(FAM)} families, exactly the AQS-INV-004 roster.',
       '- 64 bought families carry their design by reference to AQS-PRO-002; OF-13 points at the in-house sheets.',
       '- Open parts named: maker-table lines in AQS-STD-002 section 14 (ahead of valve/mseal order); shop '
       'execution and spares receipts are the open part of the work.']
open('docs-authority/BLOCK_FAMILY_PLANS.md', 'w').write('\n'.join(md) + '\n')
print(len(FAM), dict(cnt))
