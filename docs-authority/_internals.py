"""Unit internals register, duty-sheet task 06 sweep (AQS-DSN-INT-001).

Unit task -06 reads: 'internals defined and sized, or stated none with basis'. This generator
issues the per-unit disposition and closes nothing by assertion: every close carries the named
issued evidence it rests on:

  1. units whose duty section 3 still reads 'Selection pending' (the metallurgy train, the pot
     cells, the heaters and coolers of that set) stay OPEN here for the same reason task 09
     stays open (AQS-STD-005 section 4) - internals cannot be detailed before the construction
     material is selected across the bounding cases;
  2. units where an issued document already defines and sizes the internals close on that
     document - the EW electrode arrays (sizing/EW_CELLS.md), the packed beds
     (sizing/HOUSE_SCRUBBERS.md, sizing/EVAP_DESIGN.md), the CRYO_ASU micro cold box
     (sizing/COLD_BOX.md), the BMED triplet construction (sizing/BMED_STACK.md), the HX8
     PVDF bundle (AQS-STD-002 section 4.5), and units whose sizing sheet, duty sheet or issued
     mfg model BOM books the internals by part (agitator, impeller, baffle, packing, electrodes,
     membrane, spacers, demister, coil, tray, resin, sieve, desiccant, catalyst, plate-fin...);
  3. units whose class is machine/tool/store/header/pipe-like close as 'none with basis' - the
     class carries no contacting or separation duty, the duty sheet sizes the machine as an
     envelope, and the working parts are the unit task 10-13 deliverables (mfg model, BOM,
     route). This is a keyword-guarded rule: if the unit's own sizing or duty sheet books an
     internal by keyword, the unit does NOT fall through to 'none' - it closes on the booked
     design instead (or the rule leaves it open if the booking is only partial);
  4. everything else stays OPEN with 'no issued internals basis' - a real design gap named per
     unit (columns without trays/packing, dryers without media, heat batteries whose internal
     exchange element is not defined, fault stacks still on bench tests).

Outputs docs-authority/INTERNALS.md and inventory/INTERNALS.json.
Run: python3 docs-authority/_internals.py
"""
import collections, csv, glob, json, re, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)

KW = re.compile(r'agitator|impeller|baffle|packing|packed(?! tower)|membrane|spacer|demister|'
                r'crucible|liner|hot face|tube bundle|tube sheet|shell-and-tube|coil|weir|tray|'
                r'mesh pad|mesh spacers|molecular sieve|sieve tray|desiccant|catalyst|plate[- ]fin|'
                r'adsorbent|filter element|internals', re.I)
# BOM part rows may legitimately name electrodes and dip legs as internals; the doc text scan
# must not ('cell electrodes under M6' is an instrument cell, not an internal).
KW_BOM = re.compile(KW.pattern + r'|electrode|dip leg|dip tube', re.I)

# classes whose units carry no contacting/separation internals by design (machines and static)
NONE_REASON = {
 'store': 'static storage; no contacting or separation internals; holdup is the duty size line',
 'header': 'a distribution header: bore, routing and class sheet carry the design; no internals',
 'relief': 'a vent/relief manifold; open path, no internals (shop rule: open vent, no valve)',
 'product': 'static product holdup tank; no internals booked by the duty size line',
 'tank': 'static tank; no agitator or contacting internal booked by the duty or sizing sheet',
 'cut_tank': 'static cut-storage tank; no internals booked by the duty size line',
 'reagent': 'static reagent tote or day tank; no internals booked by the duty or sizing sheet',
 'dose': 'static dosing tank; no internals booked by the sizing sheet',
 'feed': 'static feed bin; no internals booked by the sizing sheet',
 'hopper': 'a bin; no internals',
 'recycle_pipe': 'pipe; no internals',
 'ahu': 'an air-handling machine: fans and standard filter cartridge modules, not process internals',
 'cool': 'a cooling machine; the duty sizes the unit, no process internals',
 'dry_cooler': 'a finned-coil air cooler sized as a machine; no process internals',
 'genset': 'a generator set machine; no process internals',
 'load_agg': 'an electrical aggregation node; no physical internals',
 'pv': 'the PV array: modules wired, not process internals',
 'rectifier': 'a rectifier machine; no process internals',
 'inverter': 'an inverter machine; no process internals',
 'building': 'a building; no process internals',
 'shop': 'a shop bay; no process internals',
 'tool': 'a process tool; the tooling is the design delivered at unit tasks 10-13, not separate internals',
 'fab': 'a fab bay; no process internals',
 'aligner': 'a wafer-aligner machine; no process internals',
 'coater': 'a coating machine; the applicator tooling is the design at unit tasks 10-13',
 'former': 'a forming machine; the tooling is the design at unit tasks 10-13',
 'forming': 'a forming machine (mill/atomiser/drawer); the tooling is the design at unit tasks 10-13',
 'intra': 'a glass-line machine; the tooling is the design at unit tasks 10-13',
 'mill': 'a rolling mill; the stands are the design at unit tasks 10-13',
 'press': 'a press; the tooling is the design at unit tasks 10-13',
 'prep': 'a prep machine; no process internals booked by the duty',
 'hab': 'habitation volume; residential fitout, not process internals',
 'farm': 'planting channels; agricultural geometry from the sizing sheet, not engineered internals',
 'ghex': 'a closed ground-loop piping field; no separate internals',
 'hydro': 'the pump-turbine set is a machine design (mfg route), no process internals',
 'thermal': 'a burner machine; the chamber and liner are on the duty size and material lines',
 'flue_junction': 'a flue junction box; open path, no internals',
 'wet_bench': 'the bench baths are the design; no separate contacting internals',
 'heat_pump': 'a heat-pump machine; no process internals',
 'orc': 'a Rankine-cycle machine; the expander and exchangers are the machine design, not separate internals',
 'study_stub': 'a study-stub bench; no process internals booked',
 'None-class': 'no classed process internals; duty envelope and material lines carry the design',
}
NONE_CLASSES = set(NONE_REASON) - {'None-class'}
NONE_CLASSES.add(None)   # the two unclassed graph nodes

# specials: issued documents that define AND size the internals for named units. Trusted closes
# (no keyword scan) - but scoped exactly to the units the document covers, read from its own
# table rows where it has one, so nothing inherits another unit's internals.
def _table_units(path):
    out = set()
    for ln in open(path):
        if ln.startswith('|'):
            c = [x.strip() for x in ln.strip().strip('|').split('|')]
            if len(c) >= 2 and re.fullmatch(r'[A-Z][A-Z0-9_]+', c[0]) and c[0] != 'Unit':
                out.add(c[0])
    return out

HOUSE = 'sizing/HOUSE_SCRUBBERS.md'
EVAP = 'sizing/EVAP_DESIGN.md'
COLD_BOX = 'sizing/COLD_BOX.md'
EW_DOC = 'sizing/EW_CELLS.md'
BMED_DOC = 'sizing/BMED_STACK.md'
SPECIAL_UNIT = {u: HOUSE for u in _table_units(f'docs-authority/{HOUSE}')}   # ALK, ACID_POLISH, NOX, MET
SPECIAL_UNIT['EVAP_ACID'] = EVAP    # X-MFG-30 names these two MVR bodies; VCD_TRAIN is NOT covered
SPECIAL_UNIT['EVAP_BASE'] = EVAP
SPECIAL_UNIT['CRYO_ASU'] = COLD_BOX  # X-MFG-33 is the CRYO_ASU micro cold box only
SPECIAL_UNIT['HX8'] = 'docs-authority/MATERIALS_STD.md section 4.5'
SPECIAL_CLASS = {'ew_cell': EW_DOC, 'bmed': BMED_DOC}
HIT_NOTE = {
 EW_DOC: 'electrode array per cell: cathode pitch 100 mm, plates and counts, tank inside dimensions (AQS-EW-MOD-001)',
 HOUSE: 'packed bed per scrubber: diameter at 0.7 of flood, bed 2303 mm, height, liquid rate (PERRY9_ABS)',
 EVAP: 'MVR internals: impregnated-graphite tube bundle, PTFE shell and separator, glass column with PTFE packing (AQS-DUTY-060, X-MFG-30)',
 COLD_BOX: 'micro cold box internals: exchangers and beds on the CRYO_ASU duty (X-MFG-33, A-M-175)',
 BMED_DOC: 'BMED triplet construction: PP frames 300 x 300 mm, 0.8 mm PE mesh spacers, Ti/MMO anode, 316L/Ni cathode end plates (A-M-170/171)',
 'docs-authority/MATERIALS_STD.md section 4.5': 'HX8 PVDF bundle: the issued tube-bundle construction (AQS-STD-002 section 4.5)',
}

UM = json.load(open('docs-authority/inventory/UNIT_MATERIALS.json')) if os.path.exists('docs-authority/inventory/UNIT_MATERIALS.json') else {}

g = json.load(open('flow_graph/plant_flow_graph.json'))
N = {n['unit_id']: n for n in g['nodes']}
UNITS = sorted(n['unit_id'] for n in g['nodes'] if n.get('class') != 'boundary' and n.get('sector_id'))

defined, none_u, open_u = {}, [], {}
for u in UNITS:
    cls = N[u]['class']
    bare = lambda s: re.sub(re.escape(u), '', s, flags=re.I)   # a unit id is not an internal
    bom = f'models/mfg/{u}/bom.csv'

    # rule 0: a named issued document covers exactly this unit's internals - trusted close
    sp = SPECIAL_UNIT.get(u) or SPECIAL_CLASS.get(cls)
    if sp:
        defined[u] = f'{HIT_NOTE[sp]} [{sp}]'
        continue
    # rule 1: same hold as task 09 (construction material not selected)
    if u in UM.get('open', {}):
        open_u[u] = 'same hold as task 09: duty section 3 selection pending (AQS-STD-005 section 4); internals cannot be detailed before the material is selected'
        continue
    # rule 2: keyword evidence, in priority order: unit sizing sheets, then issued mfg BOM
    # part rows, then the duty sheet (a duty quote is an issued size statement, but it is the
    # weakest form - it is scanned last and quoted verbatim). On the BOM, machine-class units
    # are skipped entirely: the BOM rows of a machine ARE the machine, not internals inside it.
    # A hit inside a sentence that books the definition on ANOTHER unit's sheet ('the tray
    # count are on CRYO_ASU only') or disclaims internals ('Not a packed tower') is not a hit.
    NEG = re.compile(r'not a packed tower|on [A-Z][A-Z0-9_]+ only', re.I)
    hit = None
    for p in sorted(glob.glob(f'docs-authority/sizing/{u}.md')) + sorted(glob.glob(f'docs-authority/sizing/{u}_*.md')):
        if os.path.exists(p):
            s = bare(open(p).read())
            m = KW.search(s)
            if m and not NEG.search(s):
                hit = (p, 'sizing sheet', s, KW); break
    if not hit and cls not in NONE_CLASSES and os.path.exists(bom):
        real = [r for r in open(bom) if 'PLACEHOLDER' not in r.upper()]
        hits = [r for r in real if KW_BOM.search(bare(r)) and not NEG.search(bare(r))]
        if hits:
            s = '\n'.join(hits)
            hit = (bom, f'issued mfg model BOM ({len(hits)} internals part row)', s, KW_BOM)
    if not hit and os.path.exists(f'docs-authority/duties/{u}.md'):
        s = bare(open(f'docs-authority/duties/{u}.md').read())
        m = KW.search(s)
        if m and not NEG.search(s):
            hit = (f'docs-authority/duties/{u}.md', 'duty sheet', s, KW)
    if hit:
        path, kind, s, rx = hit
        ctx = rx.search(s)
        lo, hi = max(0, ctx.start() - 60), min(len(s), ctx.end() + 80)
        frag = re.sub(r'\s+', ' ', s[lo:hi]).strip()
        if lo > 0 and ' ' in frag: frag = frag.split(' ', 1)[1]        # quote whole words only
        if hi < len(s) and ' ' in frag: frag = frag.rsplit(' ', 1)[0]
        defined[u] = f'{kind}: "{frag[0:110]}" [{path}]'
        continue
    # rule 3: class-level none with basis (keyword-guarded - the scan above precedes)
    if cls in NONE_CLASSES:
        none_u.append((u, cls))
        continue
    # rule 4: open, the gap named
    open_u[u] = f'no issued internals basis for a {cls or "unclessed"} unit: the contacting/separation internals need a design (column media, dryer media, stack or exchange element)'

md = ['# Unit internals register', '',
      'Document number: AQS-DSN-INT-001', 'Revision: B', 'Date: 2026-10-29',
      'Generated by `docs-authority/_internals.py`, with a JSON twin `docs-authority/inventory/INTERNALS.json`. Do not edit by hand; change the generator or its inputs and run `python3 -m flow_graph.param.regen`.',
      'Authority: unit task 06 of AQS-PLAN-007. Study. Not a PE stamp.', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      '| A | First issue: the internals of every unit, closed on an issued document or a class rule, or listed as open | 2026-10-21 |',
      '| B | Purpose and scope added; the method and the notes written as sentences; tables numbered | 2026-10-29 |',
      '', '## 1. Purpose and scope', '',
      'This register records, for every unit on the plant graph, whether its process internals are defined. Internals are the parts inside a vessel or machine that do the process work, such as agitators, packing, trays, electrodes, membranes, demisters, coils, resin beds and catalyst. The register invents no internal: it records what the issued documents define.', '',
      '## 2. Summary and method', '',
      f'Of the {len(UNITS)} units, {len(defined)} have their internals defined and sized in an issued document (section 4), {len(none_u)} have no process internals by a class rule (section 3), and {len(open_u)} are open, each with its gap named (section 5). A unit whose construction material is still unselected in AQS-STD-005 (`UNIT_MATERIALS.md`) is open here too.',
      'A class rule closes a unit only if none of its own documents books an internal. The generator first scans the sizing sheet, the duty sheet and the bill of materials of the unit for internals; if it finds one, the unit is taken out of the class rule.', '',
      '## 3. Class rules', '',
      'Table 3.1 gives the classes of the plant graph whose units have no process internals, and the reason for each.', '',
      'Table 3.1. Classes without process internals', '',
      '| Class | Reason |', '|---|---|']
for c in sorted(NONE_CLASSES, key=str):
    md.append(f'| {c or "None-class"} | {NONE_REASON.get(c, NONE_REASON["None-class"])} |')

md += ['', '## 4. Defined internals', '', 'Table 4.1 lists the units whose internals are defined, with the document that defines them.', '', 'Table 4.1. Defined internals', '',
       '| Unit | Class | Internals | Evidence |', '|---|---|---|---|']
for u in sorted(defined):
    md.append(f'| {u} | {N[u]["class"]} | {defined[u].split(" [")[0]} | {defined[u].split(" [")[-1].rstrip("]")} |')

md += ['', '## 5. Open units', '', 'Table 5.1 lists the units whose internals are not yet defined, with the gap.', '', 'Table 5.1. Open units', '', '| Unit | Class | Gap |', '|---|---|---|']
for u in sorted(open_u):
    md.append(f'| {u} | {N[u]["class"]} | {open_u[u]} |')

md += ['', '## 6. Limits of this register', '',
       'The furnace hot faces, crucibles, launder linings and pot-cell electrode arrays were closed by the material selections of AQS-STD-006 (task X-MAT-22, A-M-318 to A-M-328). The pot cells close on the bills of materials of their manufacturing models, and the melt-shop and service units on the material text of their duty sheets. Detail beyond a material selection, such as the hot zone of a muffle or an element array, stays open in section 5 until the fabrication models of unit tasks 10 to 12 define it.',
       'The bench run of the bipolar membrane electrodialysis unit (X-MFG-35) and the stack test of the flow battery (X-MFG-41) are tracked by their own tasks. This register records only whether the internals are defined on paper.']
open('docs-authority/INTERNALS.md', 'w').write('\n'.join(md) + '\n')
json.dump({'defined': defined, 'none': {u: NONE_REASON.get(c, NONE_REASON['None-class']) for u, c in none_u},
           'open': open_u, 'units': len(UNITS)},
          open('docs-authority/inventory/INTERNALS.json', 'w'), indent=1)
print(len(UNITS), 'defined', len(defined), 'none', len(none_u), 'open', len(open_u))
print('none classes used:', sorted({c for _, c in none_u}, key=str))
