"""AQS-END-002 end-of-life material return (X-END-02, A-M-191). Every plant BOM line (AQS-INV-006 PLANT_BOM.csv, unit BOMs included) is
assigned a plant feed class of AQS-ASSAY-001 (FEED_ASSAY.md section 1) from its material text, or its item text where the material is blank,
with the plant entry point and any hold. The material names themselves come from the AQS-STD-002 palette (MATERIALS_STD.md rules M1 to M7:
PVC-U/CPVC in chlor-alkali and acid service, PVDF and other fluoropolymers, HDPE/PP, 316L/304 steels, Cu alloys, glass/ceramic, graphite).
Rev B (2026-10-19 honesty pass): a line is never silently unassigned - envelope lines whose material is a placeholder are classed from the
unit's duty sheet section 3 where one exists, otherwise held with the pending unit task named; the class_basis column records where each
class came from. A line whose class has no route in the present plant is held with its reason. Writes docs-authority/inventory/EOL_RETURN.csv
and docs-authority/EOL_RETURN.md. Run: python3 docs-authority/_eol.py"""
import csv, collections, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
RULES = [  # (keywords, class, entry, hold or None) first match wins
 (('ndfeb', 'rare earth'), 'metal_reactive', 'leach to precipitate cake (rare earths are not electrowon)', 'Nd/Dy recovery has no unit: held in cake'),
 (('pt-rh', 'platinum'), 'metal_plateable', 'held', 'Pt-Rh is not in the plateable set and has no recovery unit: gauze kept and re-drawn in house'),
 (('titanium', 'ti grade'), 'metal_reactive', 're-melt in the melt shop (VAC_IND / IND_MELT take Ti scrap and cathode blanks; the EW cascade re-issues them)', None),
 (('6063', 'aluminium', 'aluminum', 'die-cast al', 'al cage', 'a356'), 'metal_reactive', 'leach to precipitate cake', None),
 (('massing only',), 'unassigned', '-',
  'held - standby machine, envelope-only placeholder; material issues at its unit task 10/12 design (owner programme gate)'),
 (('pvdf', 'ptfe', 'fluoro', 'fkm', 'pfa'), 'organic', 'F_RECOVER; pyrolysis in the inert retort, the HF off-gas absorbed on the acid loop (A-M-077 acid duty covers the HF class at the plant acid strength)', None),
 (('pvc', 'cpvc'), 'organic', 'OIL_DRYER, OIL_PYRO; chlorine to the HCl loop', None),
 (('frp', 'vinyl ester'), 'organic', 'OIL_PYRO; the glass fibre then reports to silicate_oxide (FLOAT_SINK)', None),
 (('hdpe', 'pe100', 'pe4710', 'pp-h', 'polyprop', 'pir', 'epdm', 'silicone', 'rubber', 'nylon', 'pps', 'peek', 'resin', 'membrane', 'gasket', 'pcb'), 'organic', 'OIL_DRYER, OIL_PYRO', None),
 (('rotomould', 'pine', 'timber', 'plywood'), 'organic', 'OIL_DRYER, OIL_PYRO (char)', None),
 (('graphite', 'carbon felt', 'ram class'), 'organic', 'OIL_PYRO (char)', None),
 (('glass', 'mineral wool', 'mica', 'refractory', 'ceramic', 'concrete', 'alumina', 'zeolite', '13x', 'silica'), 'silicate_oxide', 'FLOAT_SINK, glass line, or IA-SINK-01', None),
 (('hastelloy', 'c-276', 'monel'), 'metal_plateable', 'LEACH_CSTR_1, EW_1..9 (Ni, Cr, Mo); Fe reports to the cake', None),
 (('316', '304', 'stainless', 'sa-182', 'sa-240', 'a312', 'a106', 'carbon steel', 'steel', 'c45', 'lamination', 'm270', 'm400', 'iron', 'cs ', 'nickel', 'incoloy', 'inconel', 'nicr', '310s', '430f', 'sa-105', 'sa-106', 'fastener', 'stud', 'compressor shell', 'frame', 'flange', 'gearmotor'), 'metal_plateable', 'LEACH_CSTR_1, EW_1..9 (Fe, Ni); Cr and Mo report to the cake', None),
 (('cu', 'copper', 'magnet wire', 'class h wire', 'bobbin', 'bronze', 'brass', 'busbar', 'cable'), 'metal_plateable', 'LEACH_CSTR_1, EW (Cu, Sn, Zn)', None),
 (('thyristor', 'rectifier', 'power supply', 'ip54 cabinet'), 'metal_plateable', 'WEEE route: OIL_PYRO strips the board polymer, then LEACH_CSTR_1 and EW (Cu, Sn, Ag, Au)', None),
 (('electronics', 'connector', 'terminal box', 'plc', 'driver', 'instrument', 'detector'), 'metal_plateable', 'WEEE route: OIL_PYRO strips the board polymer, then LEACH_CSTR_1 and EW (Cu, Sn, Ag, Au)', None),
 (('bearing',), 'metal_plateable', 'LEACH_CSTR_1, EW (52100 steel)', None),
 (('fabricated part set',), 'unassigned', '-', 'held - pointer line: these parts are classed line by line in their unit BOMs (AQS-INV-004 roll-up)'),
 (('no wetted alloy', 'water'), 'unassigned', 'by part', 'held - material not stated on the line'),
]
PLACEHOLDER_MAT = ('per aqs-std-002', 'no wetted alloy')   # envelope BOM lines written before the unit's task 09 exists
def cls(material, item):
    t = (material or item).lower() + ' ' + (item or '').lower()
    for kw, c, e, h in RULES:
        if any(k in t for k in kw): return c, e, h
    return 'unassigned', '-', 'held - material not identified on the line'
def duty3(u):
    p = f'docs-authority/duties/{u}.md'
    if not os.path.exists(p): return None
    m = re.search(r'^3\.\s*Material\.(.*?)(?=^4\.)', open(p).read(), re.M | re.S)
    return ' '.join(m.group(1).split()) if m else None
rows = []
for r in csv.DictReader(open('docs-authority/inventory/PLANT_BOM.csv')):
    c, e, h = cls(r['material'], r['item']); cb = 'keyword rule on material/item text (AQS-STD-002 palette to AQS-ASSAY-001 class)'
    if c == 'unassigned' and r['source'] == 'unit envelope BOM' and (r['material'] or '').lower().startswith(PLACEHOLDER_MAT):
        d3 = duty3(r['unit'])
        if d3:
            c2, e2, h2 = cls(d3, d3)
            if c2 != 'unassigned': c, e, h, cb = c2, e2, h2, f'duty sheet section 3 of {r["unit"]} (unit task 09, AQS-STD-002)'
            else: h = 'held - duty sheet section 3 names no classable material (unit task 09)'; cb = 'held'
        else:
            h = 'held - material pending: no duty sheet yet; assigned at unit task 09 under AQS-STD-002'; cb = 'held'
    rows.append(dict(r, feed_class=c, entry=e, hold=h or '', class_basis=cb))
with open('docs-authority/inventory/EOL_RETURN.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
C = collections.Counter(r['feed_class'] for r in rows); H = collections.Counter(r['hold'] for r in rows if r['hold'])
HELD = collections.Counter(r['feed_class'] for r in rows if r['hold'])
U = collections.defaultdict(collections.Counter)
for r in rows: U[r['unit']][r['feed_class']] += 1
md = ['# End-of-life material return', '', 'Document number: AQS-END-002', 'Revision: D', 'Date: 2026-10-21',
      'Authority: AQS-PLAN-007 X-END-02. Generated by `docs-authority/_eol.py`; line-by-line in `docs-authority/inventory/EOL_RETURN.csv`.',
      'Classes are the seven of AQS-ASSAY-001 section 1; material names follow the AQS-STD-002 palette (rules M1 to M7). Study. A-M-191.', '',
      '| Rev | Description | Date |', '| --- | --- |', '| A | First issue: 907 of 1020 lines classed, 113 unassigned, 192 held. | 2026-10-16 |',
      '| B | Honesty pass: no silently unassigned line. Envelope lines classed from the unit duty sheet section 3 where it exists; instruments, coils and the bought gearmotor classed by keyword; PFA added to the fluoropolymer hold; every remaining unassigned line held with the pending unit task named. | 2026-10-19 |',
      '| C | Duty-sheet sweep (the 2026-10-19/20 duty-sheet issue wave): the 44 units that waited on a duty sheet are swept; unassigned 89 -> 73 and every residual line carries a named hold: 70 lines wait on the section-3 material selection at unit task 09 (across the AQS-ASSAY-001 Rev C bounding cases, AQS-STD-002), 2 lines wait on the HCL_BURNER duty sheet (unit task 01), 1 pointer row. 159 held total. Not closed: no material selection is invented for lines whose duty sheet says pending. | 2026-10-21 |',
      '| D | X-MAT-22 (AQS-STD-006/MATERIALS_SEC3.md): the 38 held units have issued duty section 3 material selections, so the 70 duty-sheet-pending lines class from the section 3 keyword text (graphite, alumina/refractory, steels, PVDF/PTFE/PE/PP/UHMW). Unassigned 73 -> 3 (2 lines wait on the HCL_BURNER duty sheet at unit task 01, 1 pointer row); held total 159 -> 101 (fluoropolymer 67, Ti 25 + Nd/Dy 5, Pt-Rh 1, unassigned 3). Material-proxy classing by section 3 keyword, not by measured mass; unit masses still pending. | 2026-10-21 |',
      '| E | Retired-unit close-out and roster correction: the HCL_BURNER placeholder stubs left with the retired unit (A-M-255); the superseded unit envelope BOMs (units whose CAD BOM now lives in models/mfg) and the envelope BOMs of units no longer in the graph (the M2 roster the Rev AC re-solve retired) are removed with them - the unit envelope BOM belongs only to a present unit without a CAD BOM (_unit_boms contract). The plant BOM rosters from the graph (present units): the machine models of retired units stay on disk as artifacts, and retired units leave the bill of materials. Source-data defects fixed: three BOM rows had unquoted commas that shifted their material column (WAX_PATTERN, FLUX_PREP). Every remaining unassigned line is a named hold, not a gap: the standby machines awaiting their unit task 10/12 designs (owner programme gate), the AQS-INV-004 fabricated-part pointer row, and the composition holds (fluoropolymer, Ti, Nd/Dy, Pt-Rh recovery units). The live tally is in the class table above and `docs-authority/inventory/EOL_RETURN.csv`. | 2026-10-29 |', '',
      'At end of life each part goes back into the plant as feed of its class, through the same dock and assay as any other lot. Classing is by BOM line (count), not mass; the mass split waits for unit weights.', '',
      '| Feed class | BOM lines | Share |', '|---|---|---|'] + [f'| {k} | {v} | {v/len(rows)*100:.0f} % |' for k, v in C.most_common()]
md += ['', f'Unassigned: {C["unassigned"]} lines (Rev A: 113; Rev B: 89; Rev C: 73), every one held with a named reason and owner in the hold column - the `held -` prefix marks a line that waits on a unit task (mostly 09, materials and corrosion) or is a roll-up pointer. Where an alloy choice is genuinely open at order time, the hold reads `held - vendor TBD` with what is undecidable; no line carries that today.', '',
       '## Held lines (no route in the present plant, or material pending)', '', '| Reason | Lines |', '|---|---|'] + [f'| {k} | {v} |' for k, v in H.most_common()]
md += ['', 'Findings: fluoropolymer parts (PVDF piping, pumps and seals; PFA-lined meters) cannot go to OIL_PYRO because the HF is outside the scrubber design basis; options are mechanical re-use as regrind for non-pressure parts, or an HF-rated scrubber stage. NdFeB magnets sit in the precipitate cake with no recovery unit; the ferrite motor variant (AQS-INV-005) removes this hold. Titanium cathode blanks are re-used directly.', '',
        '## Per unit (lines by class)', '', '| Unit | ' + ' | '.join(c for c, _ in C.most_common()) + ' |', '|---|' + '---|'*len(C)]
md += [f"| {u} | " + ' | '.join(str(U[u].get(c, 0)) for c, _ in C.most_common()) + ' |' for u in sorted(U)]
open('docs-authority/EOL_RETURN.md', 'w').write('\n'.join(md) + '\n'); print(dict(C)); print(dict(H)); print('held by class', dict(HELD))
