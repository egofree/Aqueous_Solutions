"""X-MAT-22 duty section 3 material selections (unit task 09 batch, AQS-STD-002 across the
AQS-ASSAY-001 Rev C bounding cases). The 38 units that held task 09 on the generic
'Selection pending' template - the pot cells, the metallurgy train, the service units - get their
construction material selections here, written to graph node params as a top-level
params.sec3_material dict (mat / basis / alt / note / task). docs-authority/_duty_basis.py
renders section 3 from it; AQS-STD-001 section 3 sheet text, the AQS-END-002 EOL matrix and the
AQS-DSN-INT-001 internals register all recompute from the same keys in one regen.

Method (first-principles, per AQS-STD-002 M1-M7): every selection is individual to the unit's own
process environment - the bounding temperature and chemistry come from the unit's duty sheet
sections 1-2 (graph design/sizing rows), the degradation mechanism is named where the house
selection differs from the issued section 12 families, the family palette and rule follow
AQS-STD-002, and alternatives are stated with the condition that would switch them. Longevity and
cost are reasoned qualitatively; no rate of loss is claimed anywhere (first-article work orders
carry the measured-rate basis). Sources cite only published references from refs.py - the 13 new
entries of this lane were web-verified before citation; no pending-metadata row is cited.

Molten-chloride physics for the pot-cell family: at 650-700 C an Fe-Cr-Ni alloy immersed in a
dry neutral chloride melt loses chromium selectively (CrCl4 vapor pressure under the salt) while
a graphite hot face is essentially inert to a dry neutral chloride melt; corrosion is impurity
(oxyhydroxide/oxygen) driven, so the pots also carry dry-breath headspaces and anhydrous-feed
rules (DING2018_CL_REVIEW, DING2021_ENG, KRUIZENGA2012). This is why Al_POT, MG_POT, CA_POT,
CR_CELL and MO_CELL select graphite wetted faces + alumina backup linings and keep the steel shell
below the liner, instead of the wet-stainless families of section 12.1.

Run: python3 -m flow_graph.param.materials3  (writes_graph: graph stage of regen_manifest.json)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(os.path.dirname(HERE), 'plant_flow_graph.json')

# unit: (mat, basis, alt, note).  mat strings carry the AQS-END-002 classable keywords.
_TAG = 'Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22).'
SEL = {
 'AL_POT': (
  'Graphite cell liner (design allowance 10 mm on the wetted faces), graphite anodes at j 0.5 A/cm2 '
  '(A-M-282 class), steel cathode bus above the melt with copper busbar frame-isolated to AQS-STD-002 '
  'section 11; 90 % alumina brick + ceramic-fibre backup lining; mild-steel outer shell below the liner',
  'molten NaCl-KCl-AlCl3 bath at 700 C (graph design): Fe-Cr-Ni alloys lose Cr selectively to the melt '
  '(DING2018_CL_REVIEW, KRUIZENGA2012); graphite is the standard fused-chloride wetted face; alumina '
  'backup lining per SCHACHT2004 ch. 4/13; M6/M7 with the section 11 bus isolation. ' + _TAG,
  'SiC hot face if AlCl3 carryover concentrates beyond the dry-gas headspace design; Ni-200 baffling at '
  'the take-off',
  'dry Cl2 headspace at 700 C: the 39.4 kg/d Cl2 export leaves on a dry hot line above the AlCl3 dew point (M7) '
  'with PVDF (P3 family) only below the dew point. No measured pit rate; the anode/liner change-out is '
  'the unit task 12 work order.'),
 'MG_POT': (
  'Graphite anodes, steel cathode plates, mullite-class alumina-silica refractory cell lining in a '
  'mild-steel shell; skim launder kept graphite-wetted',
  'molten MgCl2 at 700 C: the industrial MgCl2-electrolysis pot class is graphite anodes + steel '
  'cathodes (ULLMANN_MAGNESIUM); alloy containment loses Cr to the melt (DING2021_ENG, KRUIZENGA2012); '
  'backup lining per SCHACHT2004. ' + _TAG,
  'monolithic graphite pot if the CaCl2-brine impurity load runs above the design, at the cost of a '
  'brittle liner',
  'MgCl2 is hygroscopic: the pot-feed import leg stays PVDF (P3) and the headspace stays dry; no '
  'measured rate (unit task 12 first article).'),
 'CA_POT': (
  'Graphite anodes, steel cathode rods carrying the solid Ca deposit to the tap work order; 90 % alumina '
  'backup lining + ceramic-fibre in a mild-steel shell',
  'molten CaCl2 at 700 C (graph design; Ca m.p. 842 C per GREENWOOD element chemistry - the deposit '
  'leaves as a solid at the tap work order): the same fused-chloride physics governs the selection as '
  'AL_POT (DING2018_CL_REVIEW, '
  'KRUIZENGA2012; SCHACHT2004). ' + _TAG,
  'electrode upgrade to Mo dip legs if the Ca-metal contact interface becomes the unit task 12 '
  'bottleneck (cost up; Mo is in-house at MO_CELL class rates)',
  'the 0.055 kg/d Ca line feeds the grease thickener: the pot is sheet-lined rather than monolithic '
  '(cost-down variant of the pot family).'),
 'CR_CELL': (
  'Graphite liner and graphite anode for the carbochlorination melt (CrCl3 wetted), dry CO/CO2/Cl2 '
  'headspace; 90 % alumina brick backup in a mild-steel shell',
  'Cr2O3 + 3C + 3Cl2 carbochlorination at 700 C with an internal anode-gas loop (graph design): the bed '
  'is a dry hot face (M7); the melt physics is the pot-cell class (DING2018_CL_REVIEW, KRUIZENGA2012). '
  + _TAG,
  'SiC/SiAlON bed brick if chloride carryover drives the hot face past graphite life; Cr metal '
  'cathode-worked parts passivate in situ',
  '0.25 kg/d Cr line; the CO off-gas (0.202 kg/d) leaves on the dry IA-CR-VENT (M7); no measured rate.'),
 'MO_CELL': (
  'Graphite liner and graphite anode for the carbochlorination melt (MoCl3 wetted); 90 % alumina brick '
  'backup in a mild-steel shell; dry CO2-laden headspace',
  'MoO3 + 1.5C + 1.5Cl2 at 650 C (graph design): same pot-cell class as CR_CELL - graphite wetted face, '
  'alumina backup (DING2018_CL_REVIEW, SCHACHT2004). ' + _TAG,
  'SiC bed brick above the design temperature class',
  'the 0.0625 kg/d Mo line is also the house Mo-rod source for cell hardware; anode gas is the internal '
  'Cl2 loop; no measured rate.'),
 'TI_CELL': (
  'Alumina-brick-lined carbochlorinator at 800 C with graphite hot face; TiCl4 take-off cooled through a '
  '316L condensation train; Kroll reduction retort 310S (25Cr-20Ni) with a graphite crucible insert at '
  '900 C; molten MgCl2 return through graphite/Ni-200 launder',
  'TiO2 + 2C + 2Cl2 at 800 C and TiCl4 + 2Mg at 900 C (AQS-BAL-KROLL closure, graph design): the '
  'chlorinator bed is a dry hot face; the retort is the Kroll steel-retort class (KROLL1940, '
  'ULLMANN_TITANIUM); chloride-melt metallurgy for the launder (DING2018_CL_REVIEW). ' + _TAG,
  'Mo-clad retort (Kroll shipped his demonstration retort Mo-clad) if service pushes above 950 C; '
  'Hastelloy C-276 condensation if TiCl4 hydrolysis is ever traced',
  'batch 1 kg sponge class retort (graph design); the Mg recycles from MG_POT and the MgCl2 returns '
  'through the issued section 12.2 last-row launder.'),
 # ---- melt-shop furnaces and N+1 alternates ------------------------------------------------
 'IND_MELT': (
  'Clay-graphite crucibles assigned per melt family (Cu/Zn/Fe/Al one each), ceramic-fibre hot face '
  '150 mm + 4 mm CS casing; alumina castable hearth under the pour lip',
  'coreless medium-frequency induction remelt of Cu/Fe/Zn/Al scrap + pot metal at the 10 kg class '
  '(graph design, A-M-282 energies): melting points bound the refractory class (CRC_CU/CRC_FE/CRC_ZN/'
  'CRC_AL); crucible and lining class per SCHACHT2004 ch. 8/10; coil hardware per INDUCT_SOCX. ' + _TAG,
  'SiC crucibles for the Al family if attack is measured (cost up, better wetting resistance); '
  'alumina-liner swap when the charge is ferrous-only',
  'crucible life is a unit task 12 first-article measurement (crucible_kg 10, heats_d 4 in graph '
  'design); no rate claimed. Slag tap is basic-oxide wetted: alumina hot face.'),
 'RES_HEAT': (
  'Ceramic-fibre module lining + 80Ni-20Cr resistance elements on a mild-steel casing at the 900 C '
  'box-furnace class',
  'resistance radiant reheating, N+1 of SHELL_BURNOUT/SINTER heating at 900 C (graph design): element '
  'and lining class to 1100 C per ASM_V1; lining design per SCHACHT2004 ch. 13. ' + _TAG,
  'MoSi2 elements if the duty class moves above 1100 C (cost up)',
  'dry hot air, M7; element life rides the first-article campaign.'),
 'RF_HEAT': (
  'Clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing (same melt-shop lining class as '
  'IND_MELT); the RF coil enclosure keeps the water-cooled copper coil out of the melt space',
  'RF preheat/hold at equal melt duty of IND_MELT, 100-400 kHz through-coil (graph design, A-M-282): '
  'same refractory-chemistry environment as IND_MELT (SCHACHT2004, INDUCT_SOCX, CRC_* melting '
  'points). ' + _TAG,
  'quartz isolation sleeve past the crucible wall if the coil sees flux vapours',
  'N+1 diverse of IND_MELT (A-M-283); no melt contact at design-day zero.'),
 'COMB_HEAT': (
  'Alumina-silica brick + castable crown hot face on a mild-steel shell; 310S burner tube; flue path '
  'dry above the acid dew point into MET_SCRUB',
  'tertiary N+1 fuel-fired melt heat (graph design): combustion hot-face class per SCHACHT2004 ch. 10; '
  'the fuel class is the plant C5-C10 product (duty section 1); combustion stoichiometry per '
  'TURNS2012. ' + _TAG,
  'precast refractory module kit if relining downtime dominates the outage plan',
  'energized only on IND_MELT outage (outage_d 2); off-gas books to MET_SCRUB when hot (M7).'),
 'SINTER': (
  'Graphite resistance elements + 95 % alumina muffle under inert/vacuum atmosphere; nickel-free hot '
  'zone on a water-cooled steel jacket',
  'Ti/Mo/Cr powder sinter at 1300 C, press-and-sinter consolidation N+1 of ROLL (graph design): '
  'reactive-powder sintering furnaces use inert/vacuum hot zones with graphite or MoSi2 elements '
  '(ASM_V7); Ti embrittles in air/N2 at the class (CRC_TI). ' + _TAG,
  'Mo elements if an oxidizing (air) sinter variant is ever required - a different duty class '
  '(cost up)',
  'design_case 0.5 kg/d, T_C 1300 (graph design); no wetted stream - dry hot gas above any dew '
  'point (M7).'),
 'VAC_IND': (
  'Water-cooled copper induction crucible (no wetted-refractory interface) + 304L vacuum chamber; '
  'ceramic-fibre insulation on the shell',
  'vacuum induction skull/ISM melt of Ti sponge, N+1 diverse of IND_MELT, 2 kg batch class (graph '
  'design, A-M-282): the water-cooled copper face keeps the Ti melt out of contact with any refractory '
  '(CRC_TI melting point 1668 C; INDUCT_SOCX power class). ' + _TAG,
  'graphite crucible inside the vacuum chamber if skull-melt power runs above the design (a different '
  'metal-contact duty class)',
  'no oxides, no salt: M7 vacuum-dry service; Ti sponge line is zero-rate at the design day.'),
 'VAC_CAST': (
  '304L vacuum tilt-pour chamber; graphite crucible + alumina backup; steel table hardware',
  'vacuum tilt-pour N+1 of CAST_LINE/CONT_CAST at the 3 kg case (graph design, A-M-283/199): same '
  'refractory-chemistry classes as the other melt-shop units (SCHACHT2004, DIETER1988). ' + _TAG,
  'pump-out with Ar sweep instead of hard vacuum if the pour sees Cu-Zn volatiles (different duty '
  'class)',
  'machines only when VAC_IND is hot (outage_d 2).'),
 # ---- casters and forming ------------------------------------------------------------------ 24
 'CAST_LINE': (
  'Graphite permanent moulds with steel backing platens (Cu pour, melt 1085 C per CRC_CU); graphite '
  'launder; steel tilt table',
  'permanent-mould Cu casting at the 3 kg/d pour (graph design; A-M-199 class): graphite is the '
  'standard Cu-mould hot face at the melt temperature and is chemically indifferent to the melt '
  '(SCHACHT2004 ch. 8; DIETER1988 tool class for the platens). ' + _TAG,
  'cast-iron mould inserts if the run profile stays cold-metal short-batch (cost down, shorter '
  'mould life to be measured)',
  'mould change-out is a unit task 12 work order; no rate claimed.'),
 'CONT_CAST': (
  'Water-cooled copper mould (the graph-design primary), demineralized-water jacket on the issued '
  'Q3/Q4 M1 loop family; graphite feed launder; steel jacket casing',
  'two-strand horizontal semi-continuous caster (graph design): the water-cooled copper mould is the '
  'caster hot face; the water side is already the issued M1 family (AQS-STD-002 section 12.1; '
  'A-M-199). ' + _TAG,
  'Cu-Cr or Cu-Zr mould alloy if mould heat-cracking shows at the 31.7 kg/d feed (cost up)',
  'slab/billet leaves on conveyors; solids only thereafter.'),
 'INV_CAST': (
  'Graphite crucible tilt-pour + alumina shell as the mould hot face; steel table and tilt hardware',
  'investment casting at 2 kg/d castings through the 6-dip shell (graph design, A-M-281): the shell is '
  'a refractory hot face (SCHACHT2004); the crucible is the melt-contact part (DIETER1988). ' + _TAG,
  'preheat-tunnel integration with SHELL_BURNOUT flue if heat economy dominates (work-order change, '
  'same materials)',
  'fired shell arrives from SHELL_BURNOUT at temperature.'),
 'ROLL': (
  'Induction-hardened H13/D2-class alloy-steel rolls on cast-steel housings; planar roller bearings; '
  'steel frame',
  'two-high bench mill, 13 kg/d plate/sheet incl. the Cu line (graph design; A-M-177 DIETER1988 '
  'energies): hot-work tool-steel roll class per ASM_V1/DIETER1988 ch. 20. ' + _TAG,
  'cast-iron roll blanks for the short Cu runs (cost down, lighter surface class)',
  'dry metal contact - no corrosive stream; roll surface is the wear face (A-M-177).'),
 'DRAW': (
  'Tungsten-carbide drawing dies in tool-steel casings; steel bench; die capstan hardware carries the '
  'machine lubricant programme (no wetted stream)',
  'bench wire/rod draw N+1 of ROLL (graph design): carbide die class is the wire-drawing standard at '
  'this scale (DIETER1988 ch. 20/21). ' + _TAG,
  'polished diamond die only for a fine-wire last pass if the product class demands it (cost up, '
  'exotic supply)',
  'dry process; wire stock stays inside the shop loop.'),
 'EXTRUDE': (
  'H13 extrusion die + tool-steel container liner on a 50 t press (graph design press_t)',
  'horizontal profile press N+1 of ROLL (graph design): hot-work die steel class per ASM_V1 / '
  'DIETER1988. ' + _TAG,
  'billet preheater induction sleeve if the profile class moves hot (a separate duty entry)',
  'Nitrided die land where galling is measured (first-article item).'),
 'FORGE': (
  'H13 die blocks + cast-steel platens/ram on the open-die press (graph design ram_mm 200)',
  'open-die hydraulic press N+1 of ROLL at the bar class (graph design): die-steel class per ASM_V1; '
  'platens per DIETER1988. ' + _TAG,
  're-cuttable cast die blocks for short die lots through the fab-shop route',
  'dry hot-work contact; no corrosive stream.'),
 'STOCK_OUT': (
  'Mild-steel staging rack with HDPE wear pads and PE tote carts; no piped wetted service',
  'bar/plate/ingot staging, 1 d hold at the METAL_STORE class (graph design; AQS-DUTY-064; A-M-261): '
  'dry solids storage; machine-marker class grounding (dry dust housing conductive rule M7 where '
  'chips fly). ' + _TAG,
  'galvanized rack hardware for the imported-stock bay if atmospheric humidity rules',
  'no corrosion load; wear at the pads is a spares item.'),
 # ---- investment train ---------------------------------------------------------------------
 'WAX_PATTERN': (
  '304L wax melt tank with steam/hot-water manifold; PP-H storage bins; PE drain pans',
  'pattern-wax melt at 70-90 C (dry hydrocarbon, no corrosion load; graph design A-M-281): '
  '304/316L hot-melt practice per ULLMANN_WAX; the PP-H bins respect the house thermoplastic '
  'temperature rule (AQS-STD-002 M5 at the 80 C P4-class house limit). ' + _TAG,
  'PP-H melt tank for the 70 C case if the wax family is confirmed with a lower melt band',
  'wax reclaim returns to the tank; no corrosive species.'),
 'SHELL_BUILD': (
  'PP-H slurry tank and rainfall-sander housing; silica-flour wear faces in PE; PP slurry pump; steel '
  'frame isolated from the slurry',
  'colloidal silica slurry at pH 9-10, 100 L class (graph design A-M-281; 1 d slurry staging at 1600 '
  'kg/m3): matches the issued alkaline silica slurry family PP-H (AQS-STD-002 section 12.1 P4 row). '
  + _TAG,
  '316L tank if a binder chemistry change moves the pH below neutral',
  'slurry stays in-house; reclaim dusts are the only loose silica.'),
 'SHELL_BURNOUT': (
  'Alumina-silica kiln hot face + castable hearth, 80Ni-20Cr elements, mild-steel casing; 304L wax '
  'condenser on the condensate leg',
  'flash dewax + shell fire at 900 C (graph design; A-M-281): lining class per SCHACHT2004 ch. 4/13; '
  'element class to 1100 C per ASM_V1; condensate is recovered wax (ULLMANN_WAX). ' + _TAG,
  'SiC elements if element-zone hot spotting appears at the first-article campaign',
  'dewax off-gas books to IA-BURNOUT-VENT (dry hot M7); no measured rate claimed.'),
 'SHELL_BREAK': (
  'Vibratory knock-out tray with UHMW-PE wear liner, 304 stainless reclaim sieve, open-steel frame '
  'housing the dry, noncombustible silica dust',
  'shell knock-out + stucco reclaim, 8 kg shell/d (graph design A-M-281): wear selection per the '
  'mechanical-metallurgy wear text (DIETER1988 ch. 19); the 304 reclaim sieve keeps spent silica '
  'out of the cast surface (AQS-STD-002 silicate/ceramic class handling). ' + _TAG,
  'rubber-lined tray where the noise budget dominates',
  'reclaim split 7 kg stucco + 1 kg export per the graph closure.'),
 'FLUX_PREP': (
  'PP-H day-drum metering + 304L mixing bench kept dry; sealed anhydrous handling of the MgCl2-class '
  'drag-out',
  'salt-flux cover preparation, 0.0398 kg/d dry Kroll/MgCl2-class drag-out (graph design; A-M-280): '
  'MgCl2 hygroscopicity drives the anhydrous handling class (ULLMANN_MAGNESIUM, GREENWOOD). ' + _TAG,
  '316L drum if the salt arrives as a concentrated solution slurry (different duty class)',
  'the 0.1 kW mixer is the only powered part; dry salt contact throughout.'),
 # ---- service units -------------------------------------------------------------------------
 'F_RECOVER': (
  'PE concentrate hold tank at ambient with PVDF internals and PVDF (P3-family) legs to the hot HF '
  'make-up; PE pump and PP-H frame attachments',
  'HF-equivalent fluoride concentrate hold, 1.52 kg/d (graph design AQS-DUTY-073 sizing: the vessel row '
  'itself names PE): hot legs (85 C) are the issued P3 PVDF family (AQS-STD-002 section 12.1; '
  'ULLMANN_HF handling). ' + _TAG,
  'PTFE/PFA internals where the install layout needs a moulded part instead of sheet-fabricated PVDF',
  'static hold tank: the drain is the only wetted moving face; no corrosion allowance claimed - '
  'fluoropolymer compatibility substitutes for measured rate.'),
 'LI_RECOVER': (
  'PP-H settling/carbonation vessel + PP agitator; PE slurry lines; 316L frame metal outside the '
  'wetted zone',
  'LiOH/Li2CO3-class polish liquor from POLISH_BANK, held at ambient for the carbonation step '
  '(graph edges): matches the issued alkaline P4 PP-H family behaviour at the pH class the LiOH '
  'carbonation produces (AQS-STD-002 section 12.1 alk; GREENWOOD basic-oxide chemistry behind the '
  'route). ' + _TAG,
  '316L vessel where the liquor pH crosses neutral during the batch cycle',
  'the rate is unsized (unit task 02 pending) - the selection is issued on the construction level; '
  'level control over internals.'),
 'P_CA': (
  'PP-H precipitation vessel + PP agitator; PE slurry lines; steel frame and housing outside the '
  'wetted headspace',
  'Ca(OH)2 slurry precipitation feeding the grease kettle: pH ~12.4 class liquor at '
  'ambient (the CA_POT duty line: the 0.055 kg/d Ca metal produces the slurry): PP-H is the house '
  'non-metal for the alkaline class (AQS-STD-002 M2/M5 spirit + P4 family; the Ca(OH)2 saturation '
  'behaviour per the duty basis). ' + _TAG,
  '316L vessel + PP agitator as a mixed-build alternative if hot-work temperatures reach the PP limit',
  'scale is knocked down mechanically at clean-out: a mechanical design note, not a '
  'material allowance.'),
 'GREASE_CA': (
  '316L jacketed soap kettle + 316L agitator; steel frame and insulation stays dry; steam - hot-water '
  'heads keep the jacket wetted side on the issued Q3/Q4 M1 water family',
  'calcium soap saponification at the 95-120 C kettle class, wax cut + Ca(OH)2 (graph edges/duty '
  'AQS-DUTY-GREASE 0.1 kg/d Ca(OH)2): grease manufacture practice selects 304/316L hot-soap contact '
  '(MANG2007 ch. 14.6); the alkaline soap concentrate is hot and basic, out of the PP-H class. ' + _TAG,
  '304L kettle if the wax cut proves the only wetted face at a lower saponification temperature '
  '(cost down, first-article choice)',
  'allowance: corrosion is not the limit - cleaning and soap residue set the maintenance surface; no '
  'measured pit rate.'),
 'GREASE_LI': (
  '316L jacketed soap kettle + 316L agitator (same kettle class as GREASE_CA) for the lithium soap',
  'lithium 12-hydroxystearate soap saponification, wax cut + Li source from LI_RECOVER (graph edges): '
  'Li soaps are the standard thickeners and their kettles run the same 95-120 C class (MANG2007 ch. '
  '14). ' + _TAG,
  '304L kettle at the same trade-off as GREASE_CA',
  'Li-bearing residues drive the cleaning protocol, not corrosion.'),
 'ADS_CHILL': (
  '304L adsorber shells with silica-gel adsorbent beds and 316L chilled-water coils and '
  'headers; PP-H water legs on the P5 house water family; steel frame',
  'silica gel-water adsorption chiller, drive 65 C, chilled 12 C (graph node params; A-M-239/240 COP '
  'class): the silica gel-water chiller drives at 55-90 C (WANG2006_ADS); bed shells are sealed '
  'vacuum-grade vessels. ' + _TAG,
  '13X zeolite bed if the drive temperature class climbs above 90 C (cost up, a different duty '
  'class)',
  'seal integrity is the durability item, not corrosion; the chilled/cooling water side stays on the '
  'house water materials.'),
 'DRY_COOLER': (
  'Copper-tube, aluminium-fin air coil with galvanized-steel casing; epoxy-coated headers; the '
  'rejection loop is the house HDPE-class closed water loop',
  '12 kW dry rejection at the 37.8 C design bulb (graph params; A-M-244): air-sided fin-coil '
  'construction is the air-cooled exchanger class (PERRY9_HEAT); the loop side follows the issued '
  'water-loop families (AQS-STD-002 section 12.1). ' + _TAG,
  'micro-channel all-aluminium coil (cost down) if galvanic behaviour in the dry service proves '
  'neutral',
  'no wetted stream; the fan is the only moving part.'),
 'MAU_HX': (
  'Aluminium-fin, copper-tube make-up-air heating coil (air side dry and above the dew point in '
  'heating), 316L headers; PP condensate tray where any defrost condensate can form; water side on '
  'the issued Q3/Q4 M1 316L loop family',
  '12 kW make-up-air coil at 1.8 K (graph params; A-M-241): heating-only coil stays above the air '
  'dew point (HAB air-handling class), so the corrosion driver is absent on the air side (PERRY9_HEAT '
  'air-cooled construction class). ' + _TAG,
  '316L finned-tube coil if winter commissioning shows fin wetting (cost up)',
  'no wetted stream; the filter frames are the machine maintenance surface.'),
 'H2O_ELYZ': (
  'PEM stack: Ti porous transport layers, Ir/Ru mixed-oxide anode with Pt cathode catalyst, PTFE-class '
  'ionomer membrane, Ti cell hardware and PTFE compression seals; deoxo on a bed of 316L hardware; '
  'dry product H2/O2 lines on the issued M1 316L family',
  'PEM water electrolysis (X-PAR-12 note; relief basis A-M-19 blocked-outlet class): cell hardware is '
  'metal-as-electrode per M6 with the hydride/reverse-current guards of the house rule; Ir dissolution '
  'is the electrode basis at the anode (BERNT2018); construction follows the electrolyser standards '
  '(IEC62282_3_100, ISO22734_2019). ' + _TAG,
  'carbon-composite bipolar plates as the stack replacement class (PEMFC-family hardware) with the '
  'same hydride check',
  'electrode degradation is the first-article bench basis: no rate claimed here; the P5 water feed '
  'legs are the issued house family.'),
 'PELLET': (
  '316L die plate and cutter hub; UHMW-PE trough liner; PE/PP water trough on the resin-cooling '
  'loop; steel frame',
  'underwater die-face pelletising at 2-4 mm pellet (graph design AQS-DUTY-073): resin contact is '
  'inert polyolefin/fluoropolymer stock - hot-face compatibility passes but the water trough is the '
  'abrasion face (DIETER1988 wear class; PERRY9_MAT selection logic). ' + _TAG,
  'tungsten-carbide-faced cutter at the die plate if wear shows on the first article (cost up)',
  'no corrosive load; pellet stock leaves dry.'),
 'POLY_STOCK': (
  'HDPE tote bins and PP powder drums; steel rack; no wetted streams',
  '1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (graph design; A-M-264): dry '
  'resin storage, no process contact (AQS-DUTY-073 class). ' + _TAG,
  'antistatic PP totes if the powder-drum fraction builds charge (a spares-check item)',
  'no corrosion load; stock loss is the managed quantity.'),
 'SI_REDUCE': (
  'Graphite hot-face carbothermic-reduction furnace with alumina brick backup and a mild-steel '
  'casing; dry char and silica-class feed handling; the hot face stays dry (M7)',
  'GLASS-sector arc furnace reducing quartz ore with char (IA-QUARTZ-MU, CHAR_TO_SI, sized by '
  'flow_graph/param/si_refine.py, A-M-419): the construction material is issued at the lining level '
  '(SCHACHT2004 ch. 8 carbonaceous hot faces; CRC_SI is the element benchmark for the reduction duty class); '
  'the CO burns in the hood and the silica fume goes to the baghouse. ' + _TAG,
  'Silicon-carbide hot face when batch chemistry reaches beyond the graphite class (a process-change '
  'decision, not a materials trade)',
  'no wetted stream on the graph; the selection is the construction class only.'),
 'SI_REFINE': (
  'Nickel 200 hydrochlorinator and trichlorosilane distillation column, dry service; 316L chlorosilane and hydrogen '
  'chloride piping kept dry; Siemens bell jar of 316L with a cooled wall and high-purity silicon rods on graphite '
  'chucks (or a silicon-lined fluidised bed on the silane route)',
  'Dry chlorosilanes, hydrogen chloride and hydrogen at up to about 300 C in the hydrochlorinator and a cooled '
  'wall round rods at about 1100 C (A-M-419, flow_graph/param/si_refine.py): dry hydrogen chloride and '
  'chlorosilanes are carried in nickel and stainless steel, and any moisture makes hydrochloric acid, so the '
  'loop is kept dry (ULLMANN_HCL; PERRY9_MAT). The product-contact parts are silicon or graphite so the charge '
  'stays at electronic grade. ' + _TAG,
  'Hastelloy C-276 for the purge and condensate lines if moisture ingress cannot be excluded',
  'wetted by dry chlorosilanes; moisture is the corrosion load, controlled by the dry loop.'),
}

def main():
    g = json.load(open(GP))
    N = {n['unit_id']: n for n in g['nodes']}
    missing = [u for u in SEL if u not in N]
    assert not missing, f'{missing}: selection units absent from the graph'
    wrote = 0
    for u, (mat, basis, alt, note) in SEL.items():
        p = N[u].setdefault('params', {})
        cur = p.get('sec3_material') or {}
        new = dict(mat=mat, basis=basis, alt=alt, note=note, task='X-MAT-22')
        if cur != new:
            p['sec3_material'] = new
            wrote += 1
    json.dump(g, open(GP, 'w'), indent=1)
    print(f'materials3: {len(SEL)} selections issued, {wrote} changed (X-MAT-22)')

if __name__ == '__main__':
    main()
