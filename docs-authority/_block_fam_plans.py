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
  - the one fabricated family (category "fabricated part") is in-house work: its design and
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
FAB = next(f['family'] for f in FAM if f['category'] == 'fabricated part')   # the in-house family, by category (ids are stable, not positional)
NBOUGHT = sum(1 for f in FAM if f['category'] != 'fabricated part')

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
 'bearing': ('Bearings are bought to their ISO class and checked for identity and count on receipt. They are stored dry '
   'in their sealed packing and issued with the work order of the motor or fan build they were counted for. Press fits '
   'follow the ISO 15 seat that the class fixes, and spares are held under task X-OPS-03.'),
 'electronics': ('Electronic modules are bought to their IEC class and checked for identity and count on receipt. They are '
   'stored dry and protected from electrostatic discharge in their sealed packing, and issued to the panel or controller '
   'build they were counted for, using the module counts per controller of AQS-CTL-002. Their wired channels are checked '
   'against the I/O tables of AQS-CTL-002 at build and at commissioning, and spares are held under task X-OPS-03.'),
 'instrument': ('Instruments are bought to their device class. The range, signal and loop of each tag are given in '
   'AQS-CTL-001, not here. Each device is checked for identity and count on receipt, stored dry, issued with its tagged '
   'loop, checked against its range in AQS-CTL-001 when installed and checked again at commissioning. Spares are listed '
   'in AQS-INV-004 under task X-OPS-03.'),
 'protection': ('Protective devices are bought to their class, checked for identity and count on receipt and issued to '
   'the panel they were counted for. Their trip coordination is given in AQS-CTL-003, not here.'),
 'seal': ('Seals are bought to their seal class, which section 14 of AQS-STD-002 sets together with the EN 12756 '
   'mechanical-seal rule. The lines of the maker-table that are still open in AQS-STD-002 section 14, the FKM grade and '
   'the EPDM compound, must be closed before the seals are ordered. Seals are fitted under the work order of the pump or '
   'mixer they serve, and spares are held under task X-OPS-03.'),
 'support': ('Pipe supports are fitted during piping erection on the routed line they were counted from (AQS-ISO-002). '
   'Their material and coating match the class sheet of the pipe they carry (AQS-PIP-003), and spares are held under '
   'task X-OPS-03.'),
 'valve': ('Valves are bought to their valve class with the seal class named in section 14 of AQS-STD-002, and the '
   'fail-safe position of each actuator is set with AQS-CTL-003. Each valve is checked for identity and count on receipt, '
   'issued with the line it was counted from and operated open and closed during the hydrostatic test of its class. Its '
   'position switches are checked against their tag in AQS-CTL-001 at commissioning, and spares are held under task X-OPS-03.'),
 'fastener': ('Fasteners are bought to the thread standard of the joint they serve: ASME B16.5 stud bolting for the pipe '
   'classes, and machine screws to the standard of the host assembly. They are torqued at assembly to that standard, and '
   'spares are held under task X-OPS-03.'),
 'fabricated part': ('Fabricated parts are made in house, not bought. Their design and production plan are the issued '
   'sheets `models/mfg/<unit>/bom.csv` and `WORK_ORDER.md` of each unit, made by the fabrication routes of AQS-PLAN-005 '
   'with their hold, witness and review points. The shop makes the parts and the quality traveller records them; this page '
   'does not repeat those sheets.'),
}
MAKER = 'maker-table'   # the registered X-GOV-20-safe phrasing where a datasheet waits on the maker table

md = ['# Building-block family production plans', '',
      'Document number: AQS-INV-009', 'Revision: B', 'Date: 2026-10-29',
      'Generated by `docs-authority/_block_fam_plans.py` from `inventory/OTHER_FAMILIES.csv` (AQS-INV-004) and the datasheet '
      'rows of AQS-PRO-002 (`BOUGHT_SPECS.md`). Do not edit by hand; change the generator or its inputs and run '
      '`python3 -m flow_graph.param.regen`.',
      'Authority: tasks X-INV-05-OF of AQS-PLAN-007. Study. Not a PE stamp.',
      '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: one production plan per family, with the design joined by reference to AQS-PRO-002 | 2026-10-21 |',
      '| B | Purpose and scope added; the rules and the category plans written as sentences; the fixed counts of bought families and spares removed; tables numbered | 2026-10-29 |']

cnt = collections.Counter(f['category'] for f in FAM)
md += ['', '## 1. Purpose and scope', '',
       'This page gives the production plan of each building-block family in the inventory AQS-INV-004. A building-block '
       'family is a group of identical small parts used across the plant, such as fasteners, valves, instruments, bearings '
       'and seals. Pipe and wire families have their own pages, AQS-INV-006 and AQS-INV-007.', '',
       '## 2. Summary and rules', '',
       f'The inventory has {len(FAM)} families: ' + ', '.join(f'{n} {c}' for c, n in sorted(cnt.items(), key=lambda x: -x[1])) + '.',
       '',
       f'1. Each of the {NBOUGHT} bought families is designed by its standard class: it is bought to a standard class, its '
       'internals are those of the class, and no datasheet content is invented for it (the rule of AQS-PRO-002). The '
       'datasheet row of each family in AQS-PRO-002 is cited in Table 4.1 and not repeated.',
       '2. The plan of each category, given in section 3, covers the receipt check of identity and count, storage, the work '
       'order that issues the parts to an assembly or installation, and the check after installation. Shop execution stays '
       'the open part of the work; this page books no production run.',
       f'3. The fabricated family {FAB} is made in house. Its design and production plan are the issued sheets '
       '`models/mfg/<unit>/bom.csv` and `WORK_ORDER.md`, to which this page refers.']

md += ['', '## 3. Production plan by category', '']
for i, (c, n) in enumerate(sorted(cnt.items(), key=lambda x: -x[1]), 1):
    md += [f'### 3.{i} {c.capitalize()}', '', f'This category has {n} ' + ('family' if n == 1 else 'families') + '. ' + PLAN[c], '']

md += ['', '## 4. Family plans', '', 'Table 4.1 lists the families, with the design row of each and the first sentence of its category plan.', '',
       'Table 4.1. Building-block families', '',
       '| Family | Category | Item | Standard class | Qty | Units | Design row | Plan |',
       '|---|---|---|---|---|---|---|---|']
for f in FAM:
    fid = f['family']
    if fid in BS:
        design = f'AQS-PRO-002 sheet, {BS_SEC[fid]}'
    elif f['category'] == 'fabricated part':
        design = 'In-house sheets models/mfg/<unit>/bom.csv and WORK_ORDER.md'
    else:
        raise SystemExit(f'{fid}: no design row and not the fabricated family')
    md.append(f"| {fid} | {f['category']} | {f['item']} | {f['spec']} | {f['qty']} | {f['units']} | {design} | {PLAN[f['category']].split('. ')[0].rstrip('.')}. |")

md += ['', '## 5. Coverage', '',
       f'This page has one plan for each of the {len(FAM)} families of AQS-INV-004 and no other. The {NBOUGHT} bought families '
       f'take their design from AQS-PRO-002, and {FAB} refers to the in-house sheets. Two items remain open: the maker-table '
       'lines of AQS-STD-002 section 14, which must be closed before valves and mechanical seals are ordered, and the shop '
       'execution and receipt of spares.']
open('docs-authority/BLOCK_FAMILY_PLANS.md', 'w').write('\n'.join(md) + '\n')
print(len(FAM), dict(cnt))
