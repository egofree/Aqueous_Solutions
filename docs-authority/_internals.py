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
 'ferment': 'a static fermenter: headspace, heating and recirculation are the issued mfg BOM services; no contacting internals',
 'digest': 'an anaerobic digester tank: gas headspace, heating mat and flame-arrested recirculation are the issued mfg BOM services; no contacting internals',
 'melt_spin': 'a melt-spin line is a machine: extruder, quench and winder are the issued mfg model; the tooling is the unit task 10-13 deliverable',
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

# explicit desk dispositions (2026-10-30 internals pass, unit task 06): each carries its own
# sizing basis - nothing invented. These close ahead of the keyword scan.
EXPLICIT = {
 'Q1_A': 'heat-battery internals per AQS-DUTY-008 sec. 14: the thermal-oil medium (214.3 kg at 0.302 m3, Q1 tier, 80 K swing) with the internal thermosyphon downhill steps and cross-ties; no other contacting internals',
 'Q1_B': 'heat-battery internals per AQS-DUTY-008 sec. 14: the thermal-oil medium with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q1 tier); no other contacting internals',
 'Q2_A': 'heat-battery internals per AQS-DUTY-008 sec. 14: the thermal-oil medium with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q2 tier); no other contacting internals',
 'Q2_B': 'heat-battery internals per AQS-DUTY-008 sec. 14: the thermal-oil medium with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q2 tier); no other contacting internals',
 'Q3_A': 'heat-battery internals per AQS-DUTY-008 sec. 14: the water medium at the 30 K swing with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q3 tier); no other contacting internals',
 'Q3_B': 'heat-battery internals per AQS-DUTY-008 sec. 14: the water medium at the 30 K swing with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q3 tier); no other contacting internals',
 'Q4_A': 'heat-battery internals per AQS-DUTY-008 sec. 14: the water medium below 80 C with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q4 tier); no other contacting internals',
 'Q4_B': 'heat-battery internals per AQS-DUTY-008 sec. 14: the water medium below 80 C with the internal thermosyphon downhill steps and cross-ties, sized per the issued store table (Q4 tier); no other contacting internals',
 'CRYO_CO2': 'none with basis: the unit is a pressurised tube bank, not a contacting vessel - 4 + reserve tubes DN114 (87.3 mm ID, 6.096 m, 0.0953 m3 main bank) at 2.2 MPa design per the receiver sizing; the open volume is the design',
 'CRYO_H2': 'none with basis: pressurised tube bank - 32 tubes DN114 (87.3 mm ID, 6.096 m, 1.14 m3 main bank) at 22 MPa design per the receiver sizing; open volume, no internals',
 'CRYO_O2': 'none with basis: pressurised tube bank - 14 tubes DN114 (87.3 mm ID, 6.096 m, 0.47 m3 main bank) at 22 MPa design per the receiver sizing; open volume, no internals',
 'AQUA_UV': 'UV-C reactor internals: the 254 nm lamp array inside the reactor tube at the issued dose class, with the AQUA_BYPASS loop normally engaged (params.design dose/modes; A-M-428, A-M-427)',
 'BIOFILTER': 'moving-bed biofilter internals: the carrier media for the Nitrosomonas/Nitrobacter biofilm at the issued specific surface, with the outlet screen retaining the media (params.design media and O2 demand; A-M-415)',
 'FEED_PREP': 'formulation internals per the issued mfg model (models/mfg/FEED_PREP/bom.csv): the mixer paddle stage and the HP drier stack on the storage draw (A-M-426)',
 'MET_SYN': 'three-step Strecker bench internals per the reactor design (A-M-416 route A): the glass-lined reactor column (2 L working volume) with PTFE dip tubes, the reagent feed tanks and the Hastelloy C crystalliser; per-duty §3 material',
 'MEOH_FC': 'IEM fuel-cell stack internals per the sizing basis: 28 cells x 200 cm2 at 0.3 A/cm2 (0.6 V/cell), 1.0 kWe rated, with the methanol anode loop and air cathode supply (params.design)',
 'HF_GEN': 'kiln internals per the issued mfg model and design (A-M-289): the D200 x 1200 mm kiln tube at the 2 deg slope with its refractory lining, the spar-feed hopper with rotary valve, and the discharge hood with cake chute',
 'OIL_PYRO': 'none with basis: the pyrolysis retort is the shell itself (the issued mfg model books the retort, thermowell and bursting disc DN25 to the flare header); the open retort volume is the design, the char screw is a unit task 10 attachment',
 'POLY_FIBER': 'none with basis: a melt-spin line is a machine - the extruder, quench cabinet and winder are the issued mfg model (models/mfg/POLY_FIBER/bom.csv); the tooling is the unit task 10-13 deliverable, not separate internals',
 'MEOH_FERM': 'none with basis: a static anaerobic fermenter - the gas headspace, the daily recirculation and the heating mat are the issued mfg BOM services; no contacting or separation internals',
 'BLACK_DIGEST': 'none with basis: an anaerobic digester tank - the gas headspace, the 150 W heating mat with two RTDs and the flame-arrested recirculation are the issued mfg BOM services; no contacting internals',
 'VCD_TRAIN': 'MVC still-stack internals per the issued design: 2 modules with the 0.612 m2 heat-exchange bundle, the vapour separator and the scroll-class compressor, 8.574 kW latent duty (params.design)',
 'BMED_UPW_POLISH': 'UPW polish internals per the issued design: the RO membrane array at the 6.86 bar feed (membrane area per params.design) followed by the EDI stack (params EDI_A / EDI_kW), 0.955 recovery',
 'H2_DRYER': 'dryer internals per the issued sizing: the molecular-sieve beds (sieve_kg per params.design) with the guard bed (guard_kg) on the 0.92 Nm3/h H2 stream',
 'RES_HEAT': 'furnace internals per the duty: the 12 kW connected resistance element array on the chamber walls and hearth (radiant service at 900 C, N+1 standby of SHELL_BURNOUT/SINTER) with the hot-face liner per duty section 3; hearth furniture at unit tasks 10-12',
 'SINTER': 'furnace internals per the duty: the 8 kW connected element array for powder sintering at 1300 C (N+1 consolidation of ROLL) with the hot-face liner and retort furniture per duty section 3',
 'SI_REDUCE': 'reduction furnace internals per the sizing masses: the carbothermic charge sequence (3.85 kg/d quartz + 1.924 kg/d char -> 1.8 kg/d Si) in the retort with the hot-face liner per duty section 3',
 'CRYO_HX_Q4': 'Q4 recovery coil internals per the graph duty (S54 0.54 kW to Q4_BUS): an immersed water coil in the CRYO_O2 cold-box exit stream, the Q4 loop at 40-60 C (HEAT_LADDER.md); the coil is sized at the duty with the loop delta-T and carries no separate contacting internals',
 'MET_HX_Q4': 'melt off-heat recovery coil internals per the graph duties (IND_HEAT_TO_HX 1.063 kW + VAC_HEAT_TO_HX 0.638 kW, S63 0.017 kW to Q4_BUS): an immersed water coil in the melt-shop enclosure recovering induction and vacuum-furnace off-heat to the Q4 loop at 40-60 C; no separate contacting internals',
 'OIL_DRYER': 'none with basis: a heated dryer drum - the drying service is the shell itself, heated by the Q3 coil (HL-Q3-A/B-HX4 at 0.055 kW each per the heat-ladder edges); no contacting or separation internals booked',
 'FUEL_CELL': 'PEM fuel-cell stack internals per the issued sizing: the membrane-electrode assemblies at the rated 4.0 kW DC output (S51) with the Q4 heat recovery at 1.14 kW (S53), bipolar plates, end blocks and the balance of plant (humidifier, separator, deoxidiser) per the H2O_ELYZ PEM precedent',
 'FLOAT_SINK': 'none with basis: a water-bath density separator - the bath, the float weir and the sink conveyance are the shell design (the leach_cstr massing books FLOAT_DEWATER and SINK_DEWATER); the separation medium is plain water, no contacting internals',
}
# sharpened open-gap texts for the units whose missing design data is specific (overrides the
# generic 'no issued internals basis' text; still open - the gap is named, not closed)
OPEN_NOTES = {
 'BAGHOUSE': 'open: the filter-bag area and tube sheet need the capture-air volume per draw (the dust capture 7.77 kg/d is issued; the air volume is not on the graph)',
 'CRU': 'open: the Cl2 recovery contacting stages need the stage design at the 0.62 kg/d Cl2-class flows (the acid-polish liquor and the fluoropolymer HCl returns are issued)',
 'CRYO_N2': 'open: the N2 receiver bank tube count and volume need the receiver sizing (CRYO_CO2/H2/O2 banks are issued; the N2 bank is not)',
 'CRYO_HX_Q4': 'open: the Q4 recovery coil surface needs the loop design temperatures (the 0.54 kW duty is issued on the graph)',
 'MET_HX_Q4': 'open: the melt-off-heat recovery coil needs the Q4 loop design temperatures (the 1.70 kW recovered duty is issued on the graph)',
 'OIL_DRYER': 'open: the dryer media and heating circuit need the dryer design at the 33.0 kg/d plastics stream',
 'OIL_FRAC': 'open: the fractionator column packing or tray design needs issuing at the issued column duties',
 'FUEL_CELL': 'open: the PEM stack cell count and active area are not issued (the stack rating is) - the membrane/electrode/bipolar-plate construction needs the cell design',
 'ZNBR2': 'open: the ZnBr2 cell-stack internals wait on the X-MFG-41 stack test; the electrolyte tanks and balance of plant are the issued mfg BOM',
 'GREY_TREAT': 'open: the greywater treatment stage internals (screen, aeration, baffle sizing) need the stage design inside the issued skid envelope',
}
EXPLICIT_EVID = {
 'Q1_A': 'docs-authority/sizing/HEAT_BATTERY.md', 'Q1_B': 'docs-authority/sizing/HEAT_BATTERY.md',
 'Q2_A': 'docs-authority/sizing/HEAT_BATTERY.md', 'Q2_B': 'docs-authority/sizing/HEAT_BATTERY.md',
 'Q3_A': 'docs-authority/sizing/HEAT_BATTERY.md', 'Q3_B': 'docs-authority/sizing/HEAT_BATTERY.md',
 'Q4_A': 'docs-authority/sizing/HEAT_BATTERY.md', 'Q4_B': 'docs-authority/sizing/HEAT_BATTERY.md',
 'CRYO_CO2': 'docs-authority/sizing/CRYO_CO2.md', 'CRYO_H2': 'docs-authority/sizing/CRYO_H2.md',
 'CRYO_O2': 'docs-authority/sizing/CRYO_O2.md',
 'AQUA_UV': 'models/mfg/AQUA_UV/bom.csv', 'BIOFILTER': 'models/mfg/BIOFILTER/bom.csv',
 'FEED_PREP': 'models/mfg/FEED_PREP/bom.csv', 'MET_SYN': 'docs-authority/sizing/REACTOR_DESIGN.md',
 'MEOH_FC': 'docs-authority/sizing/MEOH_FC.md', 'HF_GEN': 'models/mfg/HF_GEN/bom.csv',
 'OIL_PYRO': 'models/mfg/OIL_PYRO/bom.csv', 'POLY_FIBER': 'models/mfg/POLY_FIBER/bom.csv',
 'MEOH_FERM': 'models/mfg/MEOH_FERM/bom.csv', 'BLACK_DIGEST': 'models/mfg/BLACK_DIGEST/bom.csv',
 'VCD_TRAIN': 'docs-authority/sizing/VCD_TRAIN.md', 'BMED_UPW_POLISH': 'docs-authority/sizing/BMED_UPW_POLISH.md',
 'H2_DRYER': 'docs-authority/sizing/H2_DRYER.md', 'RES_HEAT': 'docs-authority/sizing/RES_HEAT.md',
 'SINTER': 'docs-authority/sizing/SINTER.md', 'SI_REDUCE': 'docs-authority/sizing/SI_REDUCE.md',
 'FLOAT_SINK': 'docs-authority/sizing/FLOAT_SINK.md',
 'CRYO_HX_Q4': 'docs-authority/sizing/CRYO_HX_Q4.md',
 'MET_HX_Q4': 'docs-authority/sizing/MET_HX_Q4.md',
 'OIL_DRYER': 'docs-authority/sizing/OIL_DRYER.md',
 'FUEL_CELL': 'docs-authority/sizing/FUEL_CELL.md',

}
SPECIAL_CLASS = {'ew_cell': EW_DOC, 'bmed': BMED_DOC}
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
    # rule 0.5: an explicit desk disposition (unit task 06 pass) - each carries its own basis
    if u in EXPLICIT:
        defined[u] = f'{EXPLICIT[u]} [{EXPLICIT_EVID[u]}]'
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
        src = open(f'docs-authority/duties/{u}.md').read()
        # the unit-id strip governs the keyword SCAN (a unit's own name is not an
        # internal), but the quote comes from the ORIGINAL text: stripping the id
        # inside the envelope path ate the filename (cad/stl/BEE_HIVE.stl ->
        # cad/stl/. (stl) and left a dangling citation (X-UI-002 follow-up).
        m = KW.search(bare(src))
        if m and not NEG.search(src):
            hit = (f'docs-authority/duties/{u}.md', 'duty sheet', src, KW)
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
    open_u[u] = OPEN_NOTES.get(u, f'no issued internals basis for a {cls or "unclessed"} unit: the contacting/separation internals need a design (column media, dryer media, stack or exchange element)')

md = ['# Unit internals register', '',
      'Document number: AQS-DSN-INT-001', 'Revision: A', 'Date: 2026-10-21',
      'Authority: unit task 06 board items. Generated by `docs-authority/_internals.py`. Nothing here invents an '
      'internal: closes carry the issued document they rest on, the keyword-guarded "none" rules are class-level and '
      'fall through on any booked internal, and the open list is the named design gap. Study. Not a PE stamp.', '',
      '| Rev | Description | Date |', '| --- | --- | --- |',
      f'| A | First issue: {len(defined)} units with issued internals, {len(none_u)} none-with-basis, {len(open_u)} open. | 2026-10-21 |',
      '', '## 1. Summary and method', '',
      f'{len(UNITS)} roster units: **{len(defined)}** close with issued internals, **{len(none_u)}** close as '
      '"none with basis" (class rules, section 2), **' + str(len(open_u)) + ' open** with the gap named '
      '(section 4). The task 09 stake (AQS-STD-005 section 4) is respected: the units whose construction material is '
      'still unselected are open here too.', '',
      'A close means: the internals are defined AND sized in the cited issued document, or the unit provably has no '
      'process internals to define (keyword-guarded class rule; the unit\'s own sizing and duty sheets are scanned '
      'first, and any booked internal moves the unit out of the "none" rule).', '', '## 2. Class rules for "none with basis"', '',
      'The class comes from the graph. Any unit whose sizing sheet, duty sheet, or issued mfg BOM books an internal '
      '(agitator, impeller, baffle, packing, electrode, membrane, spacer, demister, coil, tray, resin, sieve, '
      'desiccant, catalyst, plate-fin, adsorbent, filter element...) is moved out of this table.', '',
      '| Class | Reason |', '|---|---|']
for c in sorted(NONE_CLASSES, key=str):
    md.append(f'| {c or "None-class"} | {NONE_REASON.get(c, NONE_REASON["None-class"])} |')

md += ['', '## 3. Issued internals', '',
       '| Unit | Class | Internals | Evidence |', '|---|---|---|---|']
for u in sorted(defined):
    md.append(f'| {u} | {N[u]["class"]} | {defined[u].split(" [")[0]} | {defined[u].split(" [")[-1].rstrip("]")} |')

md += ['', '## 4. Open units (named gaps)', '', '| Unit | Class | Gap |', '|---|---|---|']
for u in sorted(open_u):
    md.append(f'| {u} | {N[u]["class"]} | {open_u[u]} |')

md += ['', '## 5. Explicitly not claimed', '',
       '- The former task 09 open set (furnace hot faces, crucibles, launder linings, pot-cell electrode '
       'arrays) closed with the X-MAT-22 duty section 3 selections (AQS-STD-006, A-M-318..328): the pot '
       'cells close on the issued mfg-model BOMs, the melt-shop and service units on quoted duty section 3 '
       'text; the internals detail that goes past a selection (muffle-class hot zones, element arrays) '
       'stays a named open gap in section 4 and moves with the unit task 10-12 fabrication models.',
       '- The X-MFG-35 BMED bench run and X-MFG-41 ZNBR2 stack test own their testing open parts through '
       'their own tasks; this register closes only the desk-level internal definition.']
open('docs-authority/INTERNALS.md', 'w').write('\n'.join(md) + '\n')
json.dump({'defined': defined, 'none': {u: NONE_REASON.get(c, NONE_REASON['None-class']) for u, c in none_u},
           'open': open_u, 'units': len(UNITS)},
          open('docs-authority/inventory/INTERNALS.json', 'w'), indent=1)
print(len(UNITS), 'defined', len(defined), 'none', len(none_u), 'open', len(open_u))
print('none classes used:', sorted({c for _, c in none_u}, key=str))
