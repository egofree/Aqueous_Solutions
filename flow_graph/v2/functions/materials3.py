"""Duty section 3 material selections (reference writer
flow_graph/param/materials3.py).

One construction material selection per roster unit, issued from the unit duty
service per AQS-STD-002 (the materials of construction standard) and stamped on
the graph as params.sec3_material (mat / basis / alt / note / task). The selection
rules are declared data: SELECTION_TABLE carries one row per unit with the service
dimension, the governing AQS-STD-002 clause, and the issued construction
statement; the solve function is a straight table read with no conditional logic.

The row texts reproduce the issued selections the committed graph already
carries, exactly. Two units whose duty sheets still carried the pending template
are issued here from the same table, selected per AQS-STD-002 by service class:
- BRINE_CRYS, chloride-brine flash crystallizer on a hot leach side-stream
  (A-M-503): the leach is an M2 system on oxidizing chlorate liquor (M3), so the
  wetted path is the hot-leach thermoplastic family - CPVC vessel (section 12.1
  P2, M5 limit 93 C) with PVDF (P3) above it; no bare metal is wetted.
- NUT_AN, Ostwald ammonia oxidation skid (A-M-497): the oxidation bed is dry hot
  gas (M7 hot face, the house 310S tube class) with a dielectric break to the wet
  train (M6); the nitric wet train has no bare metal (M3) - PVC-U ammonia and
  dilution legs and a PVDF (P3) absorption and dosing side per section 5 (nitric
  at no more than 2 M).
"""
from flow_graph.v2.registry import fn


# The selection rules as data. One row per roster unit:
#   unit      - the graph unit the selection is issued to;
#   dimension - the duty/service class the selection answers (duty sections 1-2);
#   clause    - the governing AQS-STD-002 rule(s) or section family(s);
#   mat/basis/alt/note - the issued selection exactly as it renders to the duty
#               sheet section 3 (mat carries the AQS-END-002 classable keywords);
#   task      - the owning lane id.
# Lane order: X-MAT-22 (pot cells, metallurgy train, service units), X-FARM/X-HAB,
# X-QA-13 (acid and base regeneration line), X-QA-18 step 3 (HDR_* headers), then
# the two issued-from-pending rows.
SELECTION_TABLE = (
    {
      'unit': 'ACID_PLANT',
      'dimension': 'hot dry SOx gas and 98 wt% sulfuric acid service',
      'clause': 'M1 stream-named; section 12.1 M2 98 wt% H2SO4 family (carbon steel above 93 '
              'wt%); M7 dry hot gas (kiln and converter)',
      'mat': 'Cake kiln tube of Inconel 600 with an alumina lining and mineral-wool '
              'insulation; sulfur burner and converter shell of aluminised carbon steel with '
              'vanadium catalyst beds; absorber and product acid tank of carbon steel with '
              'PTFE-lined nozzles; dilution cooler of high-silicon iron',
      'basis': 'Hot sulfur dioxide and trioxide gas, dry, up to about 1150 C in the cake kiln '
              'and about 600 C in the converter, and 98 wt% sulfuric acid near ambient '
              '(A-M-474, flow_graph/param/sulfuric.py): strong acid above 93 wt% is carried in '
              'carbon steel at low velocity, while hot or dilute acid needs high-silicon iron, '
              'alloy or PTFE lining (ULLMANN_H2SO4; PERRY9_MAT). Selection per AQS-STD-002 '
              'with the duty section 2 environment (X-MAT-22).',
      'alt': 'Alloy 20 or PTFE-lined steel for the absorber if the acid strength falls below '
              '93 wt% in service',
      'note': 'wetted by 98 wt% sulfuric acid and dry sulfur oxides; dilution below 93 wt% is '
              'the corrosion load, held by the absorber control.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'AL_POT',
      'dimension': 'fused-chloride electrolysis pot cell (AlCl3 class)',
      'clause': 'M6 cell electrodes with section 11 bus isolation; M7 dry fused-chloride hot '
              'face (graphite wetted face, alumina backup lining)',
      'mat': 'Graphite cell liner (design allowance 10 mm on the wetted faces), graphite '
              'anodes at j 0.5 A/cm2 (A-M-282 class), steel cathode bus above the melt with '
              'copper busbar frame-isolated to AQS-STD-002 section 11; 90 % alumina brick + '
              'ceramic-fibre backup lining; mild-steel outer shell below the liner',
      'basis': 'molten NaCl-KCl-AlCl3 bath at 700 C (graph design): Fe-Cr-Ni alloys lose Cr '
              'selectively to the melt (DING2018_CL_REVIEW, KRUIZENGA2012); graphite is the '
              'standard fused-chloride wetted face; alumina backup lining per SCHACHT2004 ch. '
              '4/13; M6/M7 with the section 11 bus isolation. Selection per AQS-STD-002 with '
              'the duty section 2 environment (X-MAT-22).',
      'alt': 'SiC hot face if AlCl3 carryover concentrates beyond the dry-gas headspace '
              'design; Ni-200 baffling at the take-off',
      'note': 'dry Cl2 headspace at 700 C: the 39.4 kg/d Cl2 export leaves on a dry hot line '
              'above the AlCl3 dew point (M7) with PVDF (P3 family) only below the dew point. '
              'No measured pit rate; the anode/liner change-out is the unit task 12 work order.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'MG_POT',
      'dimension': 'fused-chloride electrolysis pot cell (MgCl2 class)',
      'clause': 'M6 cell electrodes; M7 molten-chloride hot face (graphite anodes, steel '
              'cathodes)',
      'mat': 'Graphite anodes, steel cathode plates, mullite-class alumina-silica refractory '
              'cell lining in a mild-steel shell; skim launder kept graphite-wetted',
      'basis': 'molten MgCl2 at 700 C: the industrial MgCl2-electrolysis pot class is graphite '
              'anodes + steel cathodes (ULLMANN_MAGNESIUM); alloy containment loses Cr to the '
              'melt (DING2021_ENG, KRUIZENGA2012); backup lining per SCHACHT2004. Selection '
              'per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'monolithic graphite pot if the CaCl2-brine impurity load runs above the design, '
              'at the cost of a brittle liner',
      'note': 'MgCl2 is hygroscopic: the pot-feed import leg stays PVDF (P3) and the headspace '
              'stays dry; no measured rate (unit task 12 first article).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'CA_POT',
      'dimension': 'fused-chloride electrolysis pot cell (CaCl2 class)',
      'clause': 'M6 cell electrodes; M7 molten-chloride hot face (graphite anodes, steel cathode '
              'rods)',
      'mat': 'Graphite anodes, steel cathode rods carrying the solid Ca deposit to the tap '
              'work order; 90 % alumina backup lining + ceramic-fibre in a mild-steel shell',
      'basis': 'molten CaCl2 at 700 C (graph design; Ca m.p. 842 C per GREENWOOD element '
              'chemistry - the deposit leaves as a solid at the tap work order): the same '
              'fused-chloride physics governs the selection as AL_POT (DING2018_CL_REVIEW, '
              'KRUIZENGA2012; SCHACHT2004). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'electrode upgrade to Mo dip legs if the Ca-metal contact interface becomes the '
              'unit task 12 bottleneck (cost up; Mo is in-house at MO_CELL class rates)',
      'note': 'the 0.055 kg/d Ca line feeds the grease thickener: the pot is sheet-lined '
              'rather than monolithic (cost-down variant of the pot family).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'CR_CELL',
      'dimension': 'carbochlorination melt cell (CrCl3 wetted)',
      'clause': 'M7 dry hot face (carbochlorination bed); M6 internal anode-gas loop; '
              'fused-chloride pot-cell class',
      'mat': 'Graphite liner and graphite anode for the carbochlorination melt (CrCl3 '
              'wetted), dry CO/CO2/Cl2 headspace; 90 % alumina brick backup in a mild-steel '
              'shell',
      'basis': 'Cr2O3 + 3C + 3Cl2 carbochlorination at 700 C with an internal anode-gas loop '
              '(graph design): the bed is a dry hot face (M7); the melt physics is the '
              'pot-cell class (DING2018_CL_REVIEW, KRUIZENGA2012). Selection per AQS-STD-002 '
              'with the duty section 2 environment (X-MAT-22).',
      'alt': 'SiC/SiAlON bed brick if chloride carryover drives the hot face past graphite '
              'life; Cr metal cathode-worked parts passivate in situ',
      'note': '0.25 kg/d Cr line; the CO off-gas (0.202 kg/d) leaves on the dry IA-CR-VENT '
              '(M7); no measured rate.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'MO_CELL',
      'dimension': 'carbochlorination melt cell (MoCl3 wetted)',
      'clause': 'M7 dry hot face; fused-chloride pot-cell class (graphite wetted face, alumina '
              'backup)',
      'mat': 'Graphite liner and graphite anode for the carbochlorination melt (MoCl3 '
              'wetted); 90 % alumina brick backup in a mild-steel shell; dry CO2-laden '
              'headspace',
      'basis': 'MoO3 + 1.5C + 1.5Cl2 at 650 C (graph design): same pot-cell class as CR_CELL - '
              'graphite wetted face, alumina backup (DING2018_CL_REVIEW, SCHACHT2004). '
              'Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'SiC bed brick above the design temperature class',
      'note': 'the 0.0625 kg/d Mo line is also the house Mo-rod source for cell hardware; '
              'anode gas is the internal Cl2 loop; no measured rate.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'TI_CELL',
      'dimension': 'carbochlorinator and Kroll retort train',
      'clause': 'M7 dry hot faces (chlorinator bed at 800 C, Kroll retort at 900 C); '
              'fused-chloride launder class on the salt return',
      'mat': 'Alumina-brick-lined carbochlorinator at 800 C with graphite hot face; TiCl4 '
              'take-off cooled through a 316L condensation train; Kroll reduction retort 310S '
              '(25Cr-20Ni) with a graphite crucible insert at 900 C; molten MgCl2 return '
              'through graphite/Ni-200 launder',
      'basis': 'TiO2 + 2C + 2Cl2 at 800 C and TiCl4 + 2Mg at 900 C (AQS-BAL-KROLL closure, '
              'graph design): the chlorinator bed is a dry hot face; the retort is the Kroll '
              'steel-retort class (KROLL1940, ULLMANN_TITANIUM); chloride-melt metallurgy for '
              'the launder (DING2018_CL_REVIEW). Selection per AQS-STD-002 with the duty '
              'section 2 environment (X-MAT-22).',
      'alt': 'Mo-clad retort (Kroll shipped his demonstration retort Mo-clad) if service '
              'pushes above 950 C; Hastelloy C-276 condensation if TiCl4 hydrolysis is ever '
              'traced',
      'note': 'batch 1 kg sponge class retort (graph design); the Mg recycles from MG_POT and '
              'the MgCl2 returns through the issued section 12.2 last-row launder.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'IND_MELT',
      'dimension': 'medium-frequency induction remelt furnaces',
      'clause': 'M7 melt hot face (crucible and lining refractory class)',
      'mat': 'Clay-graphite crucibles assigned per melt family (Cu/Zn/Fe/Al one each), '
              'ceramic-fibre hot face 150 mm + 4 mm CS casing; alumina castable hearth under '
              'the pour lip',
      'basis': 'coreless medium-frequency induction remelt of Cu/Fe/Zn/Al scrap + pot metal at '
              'the 10 kg class (graph design, A-M-282 energies): melting points bound the '
              'refractory class (CRC_CU/CRC_FE/CRC_ZN/CRC_AL); crucible and lining class per '
              'SCHACHT2004 ch. 8/10; coil hardware per INDUCT_SOCX. Selection per AQS-STD-002 '
              'with the duty section 2 environment (X-MAT-22).',
      'alt': 'SiC crucibles for the Al family if attack is measured (cost up, better wetting '
              'resistance); alumina-liner swap when the charge is ferrous-only',
      'note': 'crucible life is a unit task 12 first-article measurement (crucible_kg 10, '
              'heats_d 4 in graph design); no rate claimed. Slag tap is basic-oxide wetted: '
              'alumina hot face.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'RES_HEAT',
      'dimension': 'resistance radiant reheat furnace',
      'clause': 'M7 hot face (element and lining class to 1100 C)',
      'mat': 'Ceramic-fibre module lining + 80Ni-20Cr resistance elements on a mild-steel '
              'casing at the 900 C box-furnace class',
      'basis': 'resistance radiant reheating, N+1 of SHELL_BURNOUT/SINTER heating at 900 C '
              '(graph design): element and lining class to 1100 C per ASM_V1; lining design '
              'per SCHACHT2004 ch. 13. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'MoSi2 elements if the duty class moves above 1100 C (cost up)',
      'note': 'dry hot air, M7; element life rides the first-article campaign.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'RF_HEAT',
      'dimension': 'RF induction preheat and hold',
      'clause': 'M7 melt-contact refractory; the water-cooled coil is isolated from the melt '
              'space',
      'mat': 'Clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing (same '
              'melt-shop lining class as IND_MELT); the RF coil enclosure keeps the '
              'water-cooled copper coil out of the melt space',
      'basis': 'RF preheat/hold at equal melt duty of IND_MELT, 100-400 kHz through-coil (graph '
              'design, A-M-282): same refractory-chemistry environment as IND_MELT '
              '(SCHACHT2004, INDUCT_SOCX, CRC_* melting points). Selection per AQS-STD-002 '
              'with the duty section 2 environment (X-MAT-22).',
      'alt': 'quartz isolation sleeve past the crucible wall if the coil sees flux vapours',
      'note': 'N+1 diverse of IND_MELT (A-M-283); no melt contact at design-day zero.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'COMB_HEAT',
      'dimension': 'fuel-fired tertiary melt heat',
      'clause': 'M7 combustion hot face; flue path dry above the acid dew point',
      'mat': 'Alumina-silica brick + castable crown hot face on a mild-steel shell; 310S '
              'burner tube; flue path dry above the acid dew point into MET_SCRUB',
      'basis': 'tertiary N+1 fuel-fired melt heat (graph design): combustion hot-face class per '
              'SCHACHT2004 ch. 10; the fuel class is the plant C5-C10 product (duty section '
              '1); combustion stoichiometry per TURNS2012. Selection per AQS-STD-002 with the '
              'duty section 2 environment (X-MAT-22).',
      'alt': 'precast refractory module kit if relining downtime dominates the outage plan',
      'note': 'energized only on IND_MELT outage (outage_d 2); off-gas books to MET_SCRUB when '
              'hot (M7).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SINTER',
      'dimension': 'press-and-sinter consolidation furnace (reactive powders)',
      'clause': 'M7 inert/vacuum hot zone (nickel-free hot face)',
      'mat': 'Graphite resistance elements + 95 % alumina muffle under inert/vacuum '
              'atmosphere; nickel-free hot zone on a water-cooled steel jacket',
      'basis': 'Ti/Mo/Cr powder sinter at 1300 C, press-and-sinter consolidation N+1 of ROLL '
              '(graph design): reactive-powder sintering furnaces use inert/vacuum hot zones '
              'with graphite or MoSi2 elements (ASM_V7); Ti embrittles in air/N2 at the class '
              '(CRC_TI). Selection per AQS-STD-002 with the duty section 2 environment '
              '(X-MAT-22).',
      'alt': 'Mo elements if an oxidizing (air) sinter variant is ever required - a different '
              'duty class (cost up)',
      'note': 'design_case 0.5 kg/d, T_C 1300 (graph design); no wetted stream - dry hot gas '
              'above any dew point (M7).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'VAC_IND',
      'dimension': 'vacuum induction skull melt',
      'clause': 'M7 vacuum-dry service (water-cooled copper face; no refractory melt contact)',
      'mat': 'Water-cooled copper induction crucible (no wetted-refractory interface) + 304L '
              'vacuum chamber; ceramic-fibre insulation on the shell',
      'basis': 'vacuum induction skull/ISM melt of Ti sponge, N+1 diverse of IND_MELT, 2 kg '
              'batch class (graph design, A-M-282): the water-cooled copper face keeps the Ti '
              'melt out of contact with any refractory (CRC_TI melting point 1668 C; '
              'INDUCT_SOCX power class). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'graphite crucible inside the vacuum chamber if skull-melt power runs above the '
              'design (a different metal-contact duty class)',
      'note': 'no oxides, no salt: M7 vacuum-dry service; Ti sponge line is zero-rate at the '
              'design day.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'VAC_CAST',
      'dimension': 'vacuum tilt-pour casting',
      'clause': 'M7 vacuum-dry hot face (graphite crucible, alumina backup)',
      'mat': '304L vacuum tilt-pour chamber; graphite crucible + alumina backup; steel table '
              'hardware',
      'basis': 'vacuum tilt-pour N+1 of CAST_LINE/CONT_CAST at the 3 kg case (graph design, '
              'A-M-283/199): same refractory-chemistry classes as the other melt-shop units '
              '(SCHACHT2004, DIETER1988). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'pump-out with Ar sweep instead of hard vacuum if the pour sees Cu-Zn volatiles '
              '(different duty class)',
      'note': 'machines only when VAC_IND is hot (outage_d 2).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'CAST_LINE',
      'dimension': 'permanent-mould copper casting',
      'clause': 'M7 melt-contact mould hot face (graphite)',
      'mat': 'Graphite permanent moulds with steel backing platens (Cu pour, melt 1085 C per '
              'CRC_CU); graphite launder; steel tilt table',
      'basis': 'permanent-mould Cu casting at the 3 kg/d pour (graph design; A-M-199 class): '
              'graphite is the standard Cu-mould hot face at the melt temperature and is '
              'chemically indifferent to the melt (SCHACHT2004 ch. 8; DIETER1988 tool class '
              'for the platens). Selection per AQS-STD-002 with the duty section 2 environment '
              '(X-MAT-22).',
      'alt': 'cast-iron mould inserts if the run profile stays cold-metal short-batch (cost '
              'down, shorter mould life to be measured)',
      'note': 'mould change-out is a unit task 12 work order; no rate claimed.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'CONT_CAST',
      'dimension': 'water-cooled semi-continuous caster',
      'clause': 'M7 mould hot face (water-cooled copper); section 12.1 M1 316L water-loop family '
              'on the jacket side',
      'mat': 'Water-cooled copper mould (the graph-design primary), demineralized-water '
              'jacket on the issued Q3/Q4 M1 loop family; graphite feed launder; steel jacket '
              'casing',
      'basis': 'two-strand horizontal semi-continuous caster (graph design): the water-cooled '
              'copper mould is the caster hot face; the water side is already the issued M1 '
              'family (AQS-STD-002 section 12.1; A-M-199). Selection per AQS-STD-002 with the '
              'duty section 2 environment (X-MAT-22).',
      'alt': 'Cu-Cr or Cu-Zr mould alloy if mould heat-cracking shows at the 31.7 kg/d feed '
              '(cost up)',
      'note': 'slab/billet leaves on conveyors; solids only thereafter.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'INV_CAST',
      'dimension': 'investment casting through a shell mould',
      'clause': 'M7 melt-contact crucible and shell hot face',
      'mat': 'Graphite crucible tilt-pour + alumina shell as the mould hot face; steel table '
              'and tilt hardware',
      'basis': 'investment casting at 2 kg/d castings through the 6-dip shell (graph design, '
              'A-M-281): the shell is a refractory hot face (SCHACHT2004); the crucible is the '
              'melt-contact part (DIETER1988). Selection per AQS-STD-002 with the duty section '
              '2 environment (X-MAT-22).',
      'alt': 'preheat-tunnel integration with SHELL_BURNOUT flue if heat economy dominates '
              '(work-order change, same materials)',
      'note': 'fired shell arrives from SHELL_BURNOUT at temperature.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'ROLL',
      'dimension': 'two-high bench rolling of plate and sheet',
      'clause': 'M1 dry metal contact (no corrosive stream); the roll surface is the wear face',
      'mat': 'Induction-hardened H13/D2-class alloy-steel rolls on cast-steel housings; '
              'planar roller bearings; steel frame',
      'basis': 'two-high bench mill, 13 kg/d plate/sheet incl. the Cu line (graph design; '
              'A-M-177 DIETER1988 energies): hot-work tool-steel roll class per '
              'ASM_V1/DIETER1988 ch. 20. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'cast-iron roll blanks for the short Cu runs (cost down, lighter surface class)',
      'note': 'dry metal contact - no corrosive stream; roll surface is the wear face '
              '(A-M-177).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'DRAW',
      'dimension': 'wire and rod drawing bench',
      'clause': 'M1 dry service (machine lubricant programme; no wetted stream)',
      'mat': 'Tungsten-carbide drawing dies in tool-steel casings; steel bench; die capstan '
              'hardware carries the machine lubricant programme (no wetted stream)',
      'basis': 'bench wire/rod draw N+1 of ROLL (graph design): carbide die class is the '
              'wire-drawing standard at this scale (DIETER1988 ch. 20/21). Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'polished diamond die only for a fine-wire last pass if the product class '
              'demands it (cost up, exotic supply)',
      'note': 'dry process; wire stock stays inside the shop loop.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'EXTRUDE',
      'dimension': 'hot profile extrusion press',
      'clause': 'M1 dry hot-work contact (hot-work die steel class)',
      'mat': 'H13 extrusion die + tool-steel container liner on a 50 t press (graph design '
              'press_t)',
      'basis': 'horizontal profile press N+1 of ROLL (graph design): hot-work die steel class '
              'per ASM_V1 / DIETER1988. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'billet preheater induction sleeve if the profile class moves hot (a separate '
              'duty entry)',
      'note': 'Nitrided die land where galling is measured (first-article item).',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'FORGE',
      'dimension': 'open-die hydraulic forging press',
      'clause': 'M1 dry hot-work contact (die steel class)',
      'mat': 'H13 die blocks + cast-steel platens/ram on the open-die press (graph design '
              'ram_mm 200)',
      'basis': 'open-die hydraulic press N+1 of ROLL at the bar class (graph design): die-steel '
              'class per ASM_V1; platens per DIETER1988. Selection per AQS-STD-002 with the '
              'duty section 2 environment (X-MAT-22).',
      'alt': 're-cuttable cast die blocks for short die lots through the fab-shop route',
      'note': 'dry hot-work contact; no corrosive stream.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'STOCK_OUT',
      'dimension': 'bar, plate and ingot staging',
      'clause': 'M7 dry conductive dust housing where chips fly; dry solids storage (no wetted '
              'service)',
      'mat': 'Mild-steel staging rack with HDPE wear pads and PE tote carts; no piped wetted '
              'service',
      'basis': 'bar/plate/ingot staging, 1 d hold at the METAL_STORE class (graph design; '
              'AQS-DUTY-064; A-M-261): dry solids storage; machine-marker class grounding (dry '
              'dust housing conductive rule M7 where chips fly). Selection per AQS-STD-002 '
              'with the duty section 2 environment (X-MAT-22).',
      'alt': 'galvanized rack hardware for the imported-stock bay if atmospheric humidity '
              'rules',
      'note': 'no corrosion load; wear at the pads is a spares item.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'WAX_PATTERN',
      'dimension': 'pattern-wax melt tank and pattern store',
      'clause': 'M1 dry hydrocarbon melt (304/316L hot-melt practice); M5 thermoplastic limit '
              '(PP-H bins at the 80 C P4 class)',
      'mat': '304L wax melt tank with steam/hot-water manifold; PP-H storage bins; PE drain '
              'pans',
      'basis': 'pattern-wax melt at 70-90 C (dry hydrocarbon, no corrosion load; graph design '
              'A-M-281): 304/316L hot-melt practice per ULLMANN_WAX; the PP-H bins respect the '
              'house thermoplastic temperature rule (AQS-STD-002 M5 at the 80 C P4-class house '
              'limit). Selection per AQS-STD-002 with the duty section 2 environment '
              '(X-MAT-22).',
      'alt': 'PP-H melt tank for the 70 C case if the wax family is confirmed with a lower '
              'melt band',
      'note': 'wax reclaim returns to the tank; no corrosive species.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SHELL_BUILD',
      'dimension': 'colloidal silica slurry shelling',
      'clause': 'section 12.1 P4 alkaline silica slurry family (PP-H)',
      'mat': 'PP-H slurry tank and rainfall-sander housing; silica-flour wear faces in PE; PP '
              'slurry pump; steel frame isolated from the slurry',
      'basis': 'colloidal silica slurry at pH 9-10, 100 L class (graph design A-M-281; 1 d '
              'slurry staging at 1600 kg/m3): matches the issued alkaline silica slurry family '
              'PP-H (AQS-STD-002 section 12.1 P4 row). Selection per AQS-STD-002 with the duty '
              'section 2 environment (X-MAT-22).',
      'alt': '316L tank if a binder chemistry change moves the pH below neutral',
      'note': 'slurry stays in-house; reclaim dusts are the only loose silica.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SHELL_BURNOUT',
      'dimension': 'flash dewax and shell-fire kiln',
      'clause': 'M7 kiln hot face (lining and element class); dry hot off-gas above the dew point',
      'mat': 'Alumina-silica kiln hot face + castable hearth, 80Ni-20Cr elements, mild-steel '
              'casing; 304L wax condenser on the condensate leg',
      'basis': 'flash dewax + shell fire at 900 C (graph design; A-M-281): lining class per '
              'SCHACHT2004 ch. 4/13; element class to 1100 C per ASM_V1; condensate is '
              'recovered wax (ULLMANN_WAX). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'SiC elements if element-zone hot spotting appears at the first-article campaign',
      'note': 'dewax off-gas books to IA-BURNOUT-VENT (dry hot M7); no measured rate claimed.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SHELL_BREAK',
      'dimension': 'shell knock-out and stucco reclaim',
      'clause': 'M7 dry noncombustible dust housing; wear selection (UHMW-PE liner, 304 sieve)',
      'mat': 'Vibratory knock-out tray with UHMW-PE wear liner, 304 stainless reclaim sieve, '
              'open-steel frame housing the dry, noncombustible silica dust',
      'basis': 'shell knock-out + stucco reclaim, 8 kg shell/d (graph design A-M-281): wear '
              'selection per the mechanical-metallurgy wear text (DIETER1988 ch. 19); the 304 '
              'reclaim sieve keeps spent silica out of the cast surface (AQS-STD-002 '
              'silicate/ceramic class handling). Selection per AQS-STD-002 with the duty '
              'section 2 environment (X-MAT-22).',
      'alt': 'rubber-lined tray where the noise budget dominates',
      'note': 'reclaim split 7 kg stucco + 1 kg export per the graph closure.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'FLUX_PREP',
      'dimension': 'salt-flux cover preparation',
      'clause': 'M1 dry salt contact throughout (anhydrous handling of the hygroscopic '
              'drag-out); M5 PP-H day drum at ambient',
      'mat': 'PP-H day-drum metering + 304L mixing bench kept dry; sealed anhydrous handling '
              'of the MgCl2-class drag-out',
      'basis': 'salt-flux cover preparation, 0.0398 kg/d dry Kroll/MgCl2-class drag-out (graph '
              'design; A-M-280): MgCl2 hygroscopicity drives the anhydrous handling class '
              '(ULLMANN_MAGNESIUM, GREENWOOD). Selection per AQS-STD-002 with the duty section '
              '2 environment (X-MAT-22).',
      'alt': '316L drum if the salt arrives as a concentrated solution slurry (different duty '
              'class)',
      'note': 'the 0.1 kW mixer is the only powered part; dry salt contact throughout.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'F_RECOVER',
      'dimension': 'fluoride concentrate hold',
      'clause': 'section 12.1 P3 (PE ambient hold tank; PVDF hot legs to 85 C)',
      'mat': 'PE concentrate hold tank at ambient with PVDF internals and PVDF (P3-family) '
              'legs to the hot HF make-up; PE pump and PP-H frame attachments',
      'basis': 'HF-equivalent fluoride concentrate hold, 1.52 kg/d (graph design AQS-DUTY-073 '
              'sizing: the vessel row itself names PE): hot legs (85 C) are the issued P3 PVDF '
              'family (AQS-STD-002 section 12.1; ULLMANN_HF handling). Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'PTFE/PFA internals where the install layout needs a moulded part instead of '
              'sheet-fabricated PVDF',
      'note': 'static hold tank: the drain is the only wetted moving face; no corrosion '
              'allowance claimed - fluoropolymer compatibility substitutes for measured rate.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'LI_RECOVER',
      'dimension': 'lithium polish-liquor carbonation hold',
      'clause': 'section 12.1 P4 alkaline family (PP-H)',
      'mat': 'PP-H settling/carbonation vessel + PP agitator; PE slurry lines; 316L frame '
              'metal outside the wetted zone',
      'basis': 'LiOH/Li2CO3-class polish liquor from POLISH_BANK, held at ambient for the '
              'carbonation step (graph edges): matches the issued alkaline P4 PP-H family '
              'behaviour at the pH class the LiOH carbonation produces (AQS-STD-002 section '
              '12.1 alk; GREENWOOD basic-oxide chemistry behind the route). Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '316L vessel where the liquor pH crosses neutral during the batch cycle',
      'note': 'the rate is unsized (unit task 02 pending) - the selection is issued on the '
              'construction level; level control over internals.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'P_CA',
      'dimension': 'calcium hydroxide slurry precipitation',
      'clause': 'section 12.1 P4 alkaline family (PP-H); the M2/M5 non-metal spirit for the pH '
              '12.4 class liquor',
      'mat': 'PP-H precipitation vessel + PP agitator; PE slurry lines; steel frame and '
              'housing outside the wetted headspace',
      'basis': 'Ca(OH)2 slurry precipitation feeding the grease kettle: pH ~12.4 class liquor '
              'at ambient (the CA_POT duty line: the 0.055 kg/d Ca metal produces the slurry): '
              'PP-H is the house non-metal for the alkaline class (AQS-STD-002 M2/M5 spirit + '
              'P4 family; the Ca(OH)2 saturation behaviour per the duty basis). Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '316L vessel + PP agitator as a mixed-build alternative if hot-work temperatures '
              'reach the PP limit',
      'note': 'scale is knocked down mechanically at clean-out: a mechanical design note, not '
              'a material allowance.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'GREASE_CA',
      'dimension': 'calcium soap saponification kettle',
      'clause': 'M1 jacket water on the Q3/Q4 M1 316L loop family; 304/316L hot-soap contact '
              'class',
      'mat': '316L jacketed soap kettle + 316L agitator; steel frame and insulation stays '
              'dry; steam - hot-water heads keep the jacket wetted side on the issued Q3/Q4 M1 '
              'water family',
      'basis': 'calcium soap saponification of the air-oxidised wax cut with Ca(OH)2 slaked '
              'from the acid-plant residue lime, in an electrically heated campaign kettle '
              '(rates and kettle sized in flow_graph/param/grease.py, A-M-480): grease '
              'manufacture practice selects 304/316L hot-soap contact (MANG2007 ch. 14.6); the '
              'alkaline soap concentrate is hot and basic, out of the PP-H class. Selection '
              'per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '304L kettle if the wax cut proves the only wetted face at a lower '
              'saponification temperature (cost down, first-article choice)',
      'note': 'allowance: corrosion is not the limit - cleaning and soap residue set the '
              'maintenance surface; no measured pit rate.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'GREASE_LI',
      'dimension': 'lithium soap saponification kettle',
      'clause': 'M1 hot soap-contact 316L class (same kettle family as GREASE_CA)',
      'mat': '316L jacketed soap kettle + 316L agitator (same kettle class as GREASE_CA) for '
              'the lithium soap',
      'basis': 'lithium 12-hydroxystearate soap saponification, wax cut + Li source from '
              'LI_RECOVER (graph edges): Li soaps are the standard thickeners and their '
              'kettles run the same 95-120 C class (MANG2007 ch. 14). Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '304L kettle at the same trade-off as GREASE_CA',
      'note': 'Li-bearing residues drive the cleaning protocol, not corrosion.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'ADS_CHILL',
      'dimension': 'silica gel-water adsorption chiller',
      'clause': 'M1 sealed vacuum-grade vessels; section 12.1 P5 water family on the chilled legs',
      'mat': '304L adsorber shells with silica-gel adsorbent beds and 316L chilled-water '
              'coils and headers; PP-H water legs on the P5 house water family; steel frame',
      'basis': 'silica gel-water adsorption chiller, drive 65 C, chilled 12 C (graph node '
              'params; A-M-239/240 COP class): the silica gel-water chiller drives at 55-90 C '
              '(WANG2006_ADS); bed shells are sealed vacuum-grade vessels. Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '13X zeolite bed if the drive temperature class climbs above 90 C (cost up, a '
              'different duty class)',
      'note': 'seal integrity is the durability item, not corrosion; the chilled/cooling water '
              'side stays on the house water materials.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'DRY_COOLER',
      'dimension': 'dry air heat rejection coil',
      'clause': 'section 12.1 closed water-loop families on the loop side; air-sided fin-coil '
              'class',
      'mat': 'Copper-tube, aluminium-fin air coil with galvanized-steel casing; epoxy-coated '
              'headers; the rejection loop is the house HDPE-class closed water loop',
      'basis': '12 kW dry rejection at the 37.8 C design bulb (graph params; A-M-244): '
              'air-sided fin-coil construction is the air-cooled exchanger class '
              '(PERRY9_HEAT); the loop side follows the issued water-loop families '
              '(AQS-STD-002 section 12.1). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'micro-channel all-aluminium coil (cost down) if galvanic behaviour in the dry '
              'service proves neutral',
      'note': 'no wetted stream; the fan is the only moving part.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'MAU_HX',
      'dimension': 'make-up-air heating coil',
      'clause': 'section 12.1 M1 316L water loop; air side held above the dew point in heating',
      'mat': 'Aluminium-fin, copper-tube make-up-air heating coil (air side dry and above the '
              'dew point in heating), 316L headers; PP condensate tray where any defrost '
              'condensate can form; water side on the issued Q3/Q4 M1 316L loop family',
      'basis': '12 kW make-up-air coil at 1.8 K (graph params; A-M-241): heating-only coil '
              'stays above the air dew point (HAB air-handling class), so the corrosion driver '
              'is absent on the air side (PERRY9_HEAT air-cooled construction class). '
              'Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': '316L finned-tube coil if winter commissioning shows fin wetting (cost up)',
      'note': 'no wetted stream; the filter frames are the machine maintenance surface.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'H2O_ELYZ',
      'dimension': 'PEM water electrolysis stack',
      'clause': 'M6 electrode hardware with the hydride guards of AQS-REV-H2-001; section 12.1 '
              'M1 dry product lines',
      'mat': 'PEM stack: Ti porous transport layers, Ir/Ru mixed-oxide anode with Pt cathode '
              'catalyst, PTFE-class ionomer membrane, Ti cell hardware and PTFE compression '
              'seals; deoxo on a bed of 316L hardware; dry product H2/O2 lines on the issued '
              'M1 316L family',
      'basis': 'PEM water electrolysis (X-PAR-12 note; relief basis A-M-19 blocked-outlet '
              'class): cell hardware is metal-as-electrode per M6 with the '
              'hydride/reverse-current guards of the house rule; Ir dissolution is the '
              'electrode basis at the anode (BERNT2018); construction follows the electrolyser '
              'standards (IEC62282_3_100, ISO22734_2019). Selection per AQS-STD-002 with the '
              'duty section 2 environment (X-MAT-22).',
      'alt': 'carbon-composite bipolar plates as the stack replacement class (PEMFC-family '
              'hardware) with the same hydride check',
      'note': 'electrode degradation is the first-article bench basis: no rate claimed here; '
              'the P5 water feed legs are the issued house family.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'PELLET',
      'dimension': 'underwater die-face pelletising',
      'clause': 'M1 dry resin contact (polyolefin/fluoropolymer stock); the water trough is the '
              'abrasion face',
      'mat': '316L die plate and cutter hub; UHMW-PE trough liner; PE/PP water trough on the '
              'resin-cooling loop; steel frame',
      'basis': 'underwater die-face pelletising at 2-4 mm pellet (graph design AQS-DUTY-073): '
              'resin contact is inert polyolefin/fluoropolymer stock - hot-face compatibility '
              'passes but the water trough is the abrasion face (DIETER1988 wear class; '
              'PERRY9_MAT selection logic). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'tungsten-carbide-faced cutter at the die plate if wear shows on the first '
              'article (cost up)',
      'note': 'no corrosive load; pellet stock leaves dry.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'POLY_STOCK',
      'dimension': 'dry resin and powder staging',
      'clause': 'M1 dry solids storage (no process contact)',
      'mat': 'HDPE tote bins and PP powder drums; steel rack; no wetted streams',
      'basis': '1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (graph '
              'design; A-M-264): dry resin storage, no process contact (AQS-DUTY-073 class). '
              'Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'antistatic PP totes if the powder-drum fraction builds charge (a spares-check '
              'item)',
      'note': 'no corrosion load; stock loss is the managed quantity.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SI_REDUCE',
      'dimension': 'carbothermic quartz reduction furnace',
      'clause': 'M7 dry reduction hot face (carbonaceous lining; the hot face stays dry)',
      'mat': 'Graphite hot-face carbothermic-reduction furnace with alumina brick backup and '
              'a mild-steel casing; dry char and silica-class feed handling; the hot face '
              'stays dry (M7)',
      'basis': 'GLASS-sector arc furnace reducing quartz ore with char (IA-QUARTZ-MU, '
              'CHAR_TO_SI, sized by flow_graph/param/si_refine.py, A-M-472): the construction '
              'material is issued at the lining level (SCHACHT2004 ch. 8 carbonaceous hot '
              'faces; CRC_SI is the element benchmark for the reduction duty class); the CO '
              'burns in the hood and the silica fume goes to the baghouse. Selection per '
              'AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'Silicon-carbide hot face when batch chemistry reaches beyond the graphite class '
              '(a process-change decision, not a materials trade)',
      'note': 'no wetted stream on the graph; the selection is the construction class only.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'NAOH_PLANT',
      'dimension': 'caustic soda and chlor-alkali service',
      'clause': 'M1 caustic class: carbon steel dilute caustic below the cracking range, nickel '
              'hot strong caustic, titanium wet chlorine and lined brine',
      'mat': 'Lime kiln and trona calciner tubes of Inconel 600 with alumina lining and '
              'mineral-wool insulation; slaker, causticiser and white-liquor tank of carbon '
              'steel; on the chlor-alkali route, titanium anode pans, nickel cathode pans and '
              'perfluorinated membranes, with nickel catholyte piping and PVC-lined brine '
              'piping',
      'basis': 'Sodium hydroxide liquor at about 10 wt% and 90 C from the causticiser, or 32 '
              'wt% catholyte with wet chlorine and brine on the chlor-alkali route (A-M-475, '
              'flow_graph/param/caustic.py): carbon steel serves dilute caustic below the '
              'caustic-cracking range, nickel serves hot strong caustic, and wet chlorine and '
              'acid brine need titanium or lined steel (ULLMANN_NAOH; PERRY9_MAT). Selection '
              'per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'Nickel 200 for the liquor lines if the caustic runs hot and strong in service',
      'note': 'wetted by caustic liquor (and wet chlorine on the chlor-alkali route); caustic '
              'cracking of stressed carbon steel is the corrosion load.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SOLV_PLANT',
      'dimension': 'solvent stills and iodide carbonylation',
      'clause': 'section 12.1 M1 wet solvent family (316L); nickel-molybdenum alloy for hot '
              'iodide acetic acid',
      'mat': '316L batch still, reboiler and receivers; Hastelloy C-276 carbonylation '
              'autoclave for the iodide-promoted acetic acid step; 316L ketonisation and '
              'hydrogenation tube reactors; on the fermentation route, HDPE fermenters, '
              'nitrogen-blanketed',
      'basis': 'Ethanol and acetone at their boiling points in the still, and acetic acid with '
              'an iodide promoter at 150-200 C in the carbonylation (A-M-479, '
              'flow_graph/param/solvent.py): stainless steel serves the solvents and the dry '
              'reactor gases, while hot acetic acid with iodide needs a nickel-molybdenum '
              'alloy (ULLMANN_ACETIC; PERRY9_MAT). Selection per AQS-STD-002 with the duty '
              'section 2 environment (X-MAT-22).',
      'alt': 'Zirconium for the carbonylation autoclave if iodide corrosion of C-276 is seen '
              'in service',
      'note': 'wetted by ethanol, acetone and hot acetic acid with an iodide promoter; iodide '
              'pitting of the carbonylation vessel is the corrosion load.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'RESIST_SYN',
      'dimension': 'photoresist synthesis (wet acid chlorides and organics)',
      'clause': 'M3 wet acid chlorides (glass lining; no bare stainless); M1 organics and dry '
              'gases',
      'mat': 'Glass-lined steel batch reactors for the oxychlorination, nitrosation, '
              'diazotisation and esterification; 316L for the formaldehyde and ammonia '
              'oxidisers, the novolac kettle and the solvent steps; Monel 400 for the dry '
              'phosgene and chlorine lines',
      'basis': 'Wet HCl, nitrous acid and sulfuric acid at up to 100 C in the naphthol and '
              'diazonaphthoquinone steps, and phenol, formaldehyde and acetone in the novolac '
              'and formulation steps (A-M-482, flow_graph/param/fab_resist.py): glass lining '
              'serves the wet acid chlorides, stainless steel the organics and the dry gases, '
              'and nickel-copper alloy the dry chlorine and phosgene (PERRY9_MAT). Selection '
              'per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'Hastelloy C-276 reactors if the glass lining is chipped in service',
      'note': 'wetted by hot wet HCl, nitrous and sulfuric acids, phenol and acetone; chloride '
              'attack of any bare stainless steel is the corrosion load.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'SI_REFINE',
      'dimension': 'silicon refining (dry chlorosilane loop)',
      'clause': 'M1 dry chlorosilane service (moisture is the corrosion load; the loop is kept '
              'dry)',
      'mat': 'Nickel 200 hydrochlorinator and trichlorosilane distillation column, dry '
              'service; 316L chlorosilane and hydrogen chloride piping kept dry; Siemens bell '
              'jar of 316L with a cooled wall and high-purity silicon rods on graphite chucks '
              '(or a silicon-lined fluidised bed on the silane route)',
      'basis': 'Dry chlorosilanes, hydrogen chloride and hydrogen at up to about 300 C in the '
              'hydrochlorinator and a cooled wall round rods at about 1100 C (A-M-472, '
              'flow_graph/param/si_refine.py): dry hydrogen chloride and chlorosilanes are '
              'carried in nickel and stainless steel, and any moisture makes hydrochloric '
              'acid, so the loop is kept dry (ULLMANN_HCL; PERRY9_MAT). The product-contact '
              'parts are silicon or graphite so the charge stays at electronic grade. '
              'Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22).',
      'alt': 'Hastelloy C-276 for the purge and condensate lines if moisture ingress cannot '
              'be excluded',
      'note': 'wetted by dry chlorosilanes; moisture is the corrosion load, controlled by the '
              'dry loop.',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'REE_RECOVER',
      'dimension': 'REE campaign bench (HCl leach and oxide muffle)',
      'clause': 'M2/M5 thermoplastic HCl class below 60 C; M7 dry oxide muffle (316L shell)',
      'mat': 'glass-lined reactor, PTFE transfer, PP-H filter wetted (HCl service per '
              'AQS-STD-002 thermoplastic rules; no metal wetted part below 60 C); 316L muffle '
              'shell (dry oxide, 900 C)',
      'basis': 'X-MAT-22 section-3 selection for the REE_RECOVER campaign bench: HCl leach at < '
              '60 C (thermoplastic/glass class per AQS-STD-002 M-rules); the 900 C muffle is '
              'dry oxide service (316L shell). The campaign chemistry is dilute 30 wt% HCl at '
              '55 C with PTFE/PP-H wetted faces (A-M-433). Selection per AQS-STD-002 with the '
              'duty section 2 environment (X-MAT-22).',
      'alt': 'Hastelloy C-276 wetted parts if the campaign moves above 60 C (AQS-STD-002 '
              'metal-acid rule); not required at the bench campaign scale',
      'note': 'X-MAT-22 issued selection for the campaign bench; thermoplastic/glass wetted '
              'class',
     'task': 'X-MAT-22',
    },
    {
      'unit': 'AQUA_TANK',
      'dimension': 'recirculating aquaculture tank (RAS loop)',
      'clause': 'M1 wetted set named by the loop; Cu/Zn/brass excluded outright (ichthyotoxicity)',
      'mat': 'HDPE tank body with a food-grade LDPE aquaculture liner, SS316 hardware above '
              'the waterline, CPVC loop fittings',
      'basis': 'the tank holds the fish stock in the RAS loop at 26-28 C (graph design; '
              'A-M-415): ichthyotoxicity governs the wetted set, so Cu/Zn/brass are excluded '
              'outright; the liner is the aquaculture food-contact class over the 2.5 m3 '
              'envelope (203.8 kg/d loop).',
      'alt': 'FRP tank with gelcoat in place of the liner if liner abrasion ever shows',
      'note': 'loop top-up 27.4 kg/d and duckweed ration 18 kg/d in; 200 kg/d to the '
              'biofilter, 3 kg/d sludge to the BSFL bin.',
     'task': 'X-FARM-11',
    },
    {
      'unit': 'GROWBED_A',
      'dimension': 'aerobic mineralisation grow bed (RAS loop)',
      'clause': 'M1 wetted set named by the loop; Cu/Zn/brass excluded (the water returns to the '
              'fish)',
      'mat': 'HDPE tray with EPDM liner at the ponded inlet zone, expanded-clay (LECA) media '
              'on a geotextile separation cloth, CPVC loop piping',
      'basis': 'aerobic mineralisation front half of the dual root zone (A-M-229; A-M-415): '
              'oxygenated trickling water, so the sulfide exclusion of the anaerobic half does '
              'not bind - but the water returns to the fish stock, and Cu/Zn/brass stay out of '
              'every wetted face regardless (ichthyotoxicity, AQS-STD-002 with the duty '
              'section 2 environment).',
      'alt': 'PP tray if media abrasion ever shows on the HDPE floor (same polymer family, '
              'higher cost)',
      'note': 'pairs with GROWBED_B (the anaerobic half); the bed passes 202.8 kg/d loop water '
              'and 1.9 kg/d vermicompost to the beds.',
     'task': 'X-FARM-11',
    },
    {
      'unit': 'GROWBED_B',
      'dimension': 'anaerobic mineralisation grow bed (sulfidic under the ponded tail)',
      'clause': 'M1 wetted set named by the loop; sulfide plus loop-water contact excludes '
              'Cu/Zn/brass',
      'mat': 'HDPE tray with EPDM liner, expanded-clay (LECA) media on a geotextile '
              'separation cloth, CPVC loop piping',
      'basis': 'anaerobic mineralisation root zone (A-M-229; A-M-415): the bed runs sulfidic '
              'under the ponded tail, and sulfide plus loop-water contact excludes Cu/Zn/brass '
              'outright (ichthyotoxic to the fish stock the loop serves); LECA is the '
              'aquaponic media class (graph design). Selection per AQS-STD-002 with the duty '
              'section 2 environment.',
      'alt': 'PP tray if media abrasion ever shows on the HDPE floor (same polymer family, '
              'higher cost)',
      'note': 'the anaerobic half of the dual root zone; the aerobic half (GROWBED_A) carries '
              'its own issued selection.',
     'task': 'X-FARM-01',
    },
    {
      'unit': 'BSFL_BIN',
      'dimension': 'bsfl larval bin (wet acid compost substrate)',
      'clause': 'M1 wetted set for the pH 4-6 frass-acid substrate (HDPE/PP inert across the '
              'range)',
      'mat': 'HDPE tray bin, PP larval self-harvest ramp, SS316 mesh screen; no metal below '
              'the substrate line',
      'basis': 'substrate goes pH 4-6 under frass acids at 65-75 % moisture with self-heating '
              'toward 40 C (graph design; A-M-418): wet acid compost pits zinc and plate '
              'steel, HDPE/PP are inert across the whole range',
      'alt': 'FRP tray if bin scaling raises wall temperatures past the HDPE class',
      'note': 'larvae harvest is by self-separation up the ramp; the mesh is the pupa screen.',
     'task': 'X-FARM-03',
    },
    {
      'unit': 'CHICKEN_COOP',
      'dimension': 'poultry housing (wet uric-acid manure, ammonia offgas)',
      'clause': 'M1 environment-named set: ammonia plus moisture steps the wet contact points to '
              'SS316',
      'mat': 'Hot-dip galvanised steel frame and hardware cloth, SS316 feeders and waterers, '
              'HDPE drop-board liner',
      'basis': 'wet uric-acid manure with ammonia offgas and periodic wash-down (graph design; '
              'A-M-417): ammonia plus moisture pits zinc at the droppings line, so the wet '
              'contact points step up to SS316 (standard poultry-housing practice)',
      'alt': 'SS304 frame if wash-down frequency rises past the weekly class',
      'note': 'the drop board is the manure harvest surface to the BSFL bin.',
     'task': 'X-FARM-02',
    },
    {
      'unit': 'DUCK_PEN',
      'dimension': 'duck pen with a permanent wallow',
      'clause': 'M1 standing-water wet zone governs the zinc budget (EPDM liner, SS316 waterers)',
      'mat': 'Hot-dip galvanised steel frame and hardware cloth, EPDM liner in the wallow, '
              'SS316 waterers',
      'basis': 'permanently wet pen with a wallow (graph design; A-M-421): standing water '
              'governs the zinc budget, so the wet zone is EPDM-lined and drinking-water '
              'contact is SS316',
      'alt': 'FRP wet panels in place of the liner if the pen geometry changes',
      'note': 'the ducks forage the aquaponic loop water; pen drainings join the BSFL '
              'feedstock.',
     'task': 'X-FARM-05',
    },
    {
      'unit': 'QUAIL_CAGE',
      'dimension': 'quail cage battery (dry droppings tray)',
      'clause': 'M1 dry tray service (HDG weld wire); only the nipple waterers are wet (SS316)',
      'mat': 'Hot-dip galvanised weld-wire cage battery, PP feeders, SS316 nipple waterers',
      'basis': 'dry droppings-tray service at the 20-hen Coturnix unit (graph design; A-M-422): '
              'HDG weld wire is the cage-battery standard; the only wet points are the '
              'nipples, so those alone are stainless',
      'alt': 'PVC-coated wire if foot dermatitis ever shows at the cage floor',
      'note': 'the droppings tray feeds the vermi bin directly.',
     'task': 'X-FARM-06',
    },
    {
      'unit': 'RABBIT_HUTCH',
      'dimension': 'rabbit hutch (dry pellet manure on wire)',
      'clause': 'M1 dry floor service (HDG wire); the rest mats are the welfare contact surface',
      'mat': 'Hot-dip galvanised wire floor, HDPE rest mats, PP nest boxes, SS316 waterers',
      'basis': 'dry pellet manure on a wire floor with rest mats against sore hocks (graph '
              'design; A-M-423): HDG wire is the rabbitry floor standard and the rest mats are '
              'the welfare contact surface',
      'alt': 'SS wire floor if galvanising wears through at the door wear points',
      'note': 'cold manure goes direct to the soil root zones (A-M-423).',
     'task': 'X-FARM-07',
    },
    {
      'unit': 'BEE_HIVE',
      'dimension': 'honeybee hive (biology interface, closed shell)',
      'clause': 'M1 no preservatives and no copper salts on the hive; no outgassing polymer '
              'class in the habitable shell',
      'mat': 'Untreated solid-pine box bodies, SS316 screen bottom board, propolis-waxed '
              'interiors; no copper-bearing alloys and no treated lumber anywhere on the hive',
      'basis': 'Apis mellifera propolise rough untreated wood and are poisoned by lumber '
              'preservatives and copper salts (graph design; A-M-424): in the closed shell the '
              'hive may also not outgas into the habitable atmosphere, which is what excludes '
              'the polymer-hive class',
      'alt': 'none within the palette - the material is the biology interface here (a polymer '
              'hive is a process-change decision, not a materials trade)',
      'note': 'pollination service to the canopy is the primary output; honey and wax are '
              'secondary (A-M-424).',
     'task': 'X-FARM-08',
    },
    {
      'unit': 'VERMI_BIN',
      'dimension': 'vermicompost bin (wet near-neutral bedding)',
      'clause': 'M1 wetted set for the 70-80 % moisture bedding (HDPE/PP benign; no bare steel)',
      'mat': 'HDPE bin with coco-coir and shredded-paper bedding, PP working fork, SS316 '
              'harvest screen',
      'basis': 'bedding held at 70-80 % moisture near neutral pH for Eisenia fetida (graph '
              'design; A-M-425): the wet near-neutral bedding is benign to HDPE/PP and hostile '
              'to unprotected steel; no metal contact with the casting harvest',
      'alt': 'FRP bin at larger areas (same polymer-class logic as the BSFL bin)',
      'note': 'castings 1.5-2.5 % N to the soil root zones (A-M-425).',
     'task': 'X-FARM-09',
    },
    {
      'unit': 'GALLEY',
      'dimension': 'galley (food-contact sanitation)',
      'clause': 'food-contact rule (Cu alloys excluded from food paths); M1 chloride-light '
              'wipe-down service',
      'mat': 'SS304 worktops and splashbacks, food-contact PP preparation boards; no '
              'copper-bearing alloys on food paths',
      'basis': 'food-contact sanitation class with wipe-down chemistry (AQS-HAB-001; A-M-419): '
              '304 is sufficient at the chloride-light galley service; Cu alloys are excluded '
              'from food paths outright (AQS-STD-002 food-contact rule)',
      'alt': 'SS316 where chlorinated sanitisers concentrate (same family, higher cost)',
      'note': 'the galley biowaste stream feeds the BSFL bin (A-M-418).',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'WASHROOM',
      'dimension': 'washroom (continuous wet zone)',
      'clause': 'AQS-HAB-001 wet-zone fitout class (FRP and ceramic carry the standing '
              'condensate)',
      'mat': 'FRP wet-wall panels, SS304 fixtures, ceramic tile wet zones, SS drainage',
      'basis': 'continuous wet zone at habitable temperature (AQS-HAB-001; A-M-419): FRP and '
              'ceramic carry the standing condensate; 304 is the fixture class at the '
              'chloride-light service',
      'alt': 'SS316 fixtures where sanitiser chemistry concentrates',
      'note': 'grey water to the WTR loop; the washroom is the largest hab water consumer.',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'MEDICAL',
      'dimension': 'medical room (clinical sanitation)',
      'clause': 'AQS-HAB-001 sanitation class (full wipe-down surfaces, no fabric)',
      'mat': 'SS304 wipe-down surfaces and cabinets, PP instrument trays',
      'basis': 'clinical sanitation class (AQS-HAB-001; A-M-419): full wipe-down surfaces, no '
              'fabric in the room; 304 at the sanitiser service',
      'alt': 'SS316 where antiseptic chemistry ever demands it',
      'note': 'the room is 6 m2 of the AQS-HAB-001 zoning.',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'REC_DAYROOM',
      'dimension': 'recreation dayroom (hab interior fitout)',
      'clause': 'AQS-HAB-001 non-outgassing interior fitout class',
      'mat': 'Aluminium extrusion partitions, PP-fleece acoustic panels, SS kick plates',
      'basis': 'hab interior fitout class (AQS-HAB-001; A-M-419): non-outgassing, wipe-down, '
              '1-atm interior; no structural duty beyond the partitions',
      'alt': 'wood-composite panels rejected for outgassing into the shell atmosphere',
      'note': 'recreation/common zoning is 20 m2 of the AQS-HAB-001 basis.',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'COMMON_AREA',
      'dimension': 'common circulation area (hab interior fitout)',
      'clause': 'AQS-HAB-001 non-outgassing interior fitout class',
      'mat': 'Aluminium extrusion circulation framing, PP-fleece panel lining, SS kick plates',
      'basis': 'hab circulation and utility zoning (AQS-HAB-001; A-M-419): the same '
              'non-outgassing interior fitout class as the day spaces',
      'alt': 'as REC_DAYROOM',
      'note': '10 m2 circulation in the AQS-HAB-001 basis.',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'SLEEP_QUARTERS',
      'dimension': 'private quarters (hab interior fitout)',
      'clause': 'AQS-HAB-001 non-outgassing interior fitout class',
      'mat': 'Aluminium extrusion bunk framing, PP-fleece panel lining and bedding textiles, '
              'SS kick plates',
      'basis': 'private quarters at 16 m2 (AQS-HAB-001; A-M-419): interior fitout class as the '
              'day spaces; the textiles are the polymer classes from the POLYMERS sector (no '
              'animal-fibre import exists in the roster)',
      'alt': 'as REC_DAYROOM',
      'note': '4 x 4 m2 private quarters in the AQS-HAB-001 basis.',
     'task': 'X-HAB-01',
    },
    {
      'unit': 'FEED_PREP',
      'dimension': 'animal ration preparation (food-contact)',
      'clause': 'food-contact rule (Cu excluded from every feed path); M1 chloride-light service',
      'mat': 'SS304 contact surfaces and mixing troughs, PP feed bins, quartz-sleeve drier '
              'ducting; no copper-bearing alloys on any feed path',
      'basis': 'food-contact sanitation class for the animal ration line (A-M-426): 304 at the '
              'chloride-light service, PP bins resist the wet duckweed; Cu is excluded from '
              'every feed path outright',
      'alt': 'SS316 where the eggshell grinding dust ever shows pitting',
      'note': 'the reject stream returns to the BSFL bin, so the contact surfaces serve both '
              'feeds.',
     'task': 'X-FARM-10',
    },
    {
      'unit': 'AQUA_UV',
      'dimension': 'aquaculture loop UV reactor',
      'clause': 'M1 loop-water wetted set (304 tube; the lamp is isolated behind quartz)',
      'mat': 'SS304 reactor tube with a quartz UV sleeve, PP loop fittings, EPDM gasket class',
      'basis': 'loop-water service at aquaponic temperature (A-M-428): 304 tube with the lamp '
              'isolated behind quartz; the unit is normally bypassed, so wetted-time is '
              'intermittent',
      'alt': '316L tube if the loop ever runs saline (it does not at the freshwater class)',
      'note': 'quartz sleeve fouling is the maintenance item - the dose validation (X-FARM-12) '
              'covers it.',
     'task': 'X-FARM-12',
    },
    {
      'unit': 'POLY_FIBER',
      'dimension': 'polypropylene melt spinning',
      'clause': 'M1 polymer melt contact (no copper alloys at melt temperature); the die plate '
              'is the precision item',
      'mat': 'SS304 melt vessel and spin pump with heater bands, brass-free spinnerette '
              '(stainless die plate), PP quench ducting',
      'basis': 'PP melts at 160-220 C and is non-wetting to the 304 class at the bench '
              'throughput (A-M-429): the die plate is the precision item; no copper alloys '
              'touch the melt (PP degrades against copper at melt temperature)',
      'alt': 'a 316L die plate if the FR-finish chemistry ever shows die corrosion',
      'note': 'the FR finish dosing skid is PP/PTFE-contact throughout.',
     'task': 'X-POLY-01',
    },
    {
      'unit': 'MET_SYN',
      'dimension': 'methionine synthesis (Strecker reagent set)',
      'clause': 'M1 reagent-named set: glass-lined column, PTFE transfer, Hastelloy C for the '
              'acidic hydrolysis/crystallisation',
      'mat': 'Borosilicate glass-lined reactor column, PTFE-lined transfer lines, SS304 '
              'reagent feed tanks, Hastelloy C crystalliser',
      'basis': 'the three-step Strecker carries HCN, acrolein and methanethiol - all aggressive '
              'at the reagent class (A-M-416): glass-lined for the reaction column, PTFE for '
              'the transfer, Hastelloy C for the acidic hydrolysis/crystallisation',
      'alt': 'a tantalum reactor if the HCN service ever shows corrosion at the glass-lining '
              'pinholes',
      'note': 'the crystalliser is the product-quality bottleneck: DL-Met crystal habit '
              'controls the filtration rate.',
     'task': 'X-UI-002',
    },
    {
      'unit': 'GW_INTAKE',
      'dimension': 'groundwater wellhead and potable discharge',
      'clause': 'M1 potable wetted set (304 wetted; HDPE discharge run)',
      'mat': 'SS304 wellhead plate and discharge head, HDPE potable discharge line, '
              'submersible pump SS304/stainless stages',
      'basis': 'potable groundwater contact (X-LOC-13 well head): 304 wetted at the '
              'chloride-light aquifer class, HDPE for the discharge run; the pump stages are '
              'the well-class stainless',
      'alt': '316L wetted where the aquifer mineralisation ever shows pitting',
      'note': 'standby-zero at the baseline: the atmospheric harvest covers the water cycle '
              '(the T4 by-design ruling).',
     'task': 'X-LOC-13',
    },
    {
      'unit': 'BMED_ACID',
      'dimension': 'BMED stack, acid-side loop (2 M HCl)',
      'clause': 'M2 PVC-U wetted path; M3 electrode exception named by M6 (Ti/MMO anode, 316L '
              'annealed cathode per the hydrogen clause); M4 tie rods outside the wetted and '
              'vapour zone; M5 CPVC above 60 C',
      'mat': 'Wetted path of PVC-U (spacer frames, gasket seals, drip tray, nozzles; above 60 '
              'C the thermoplastic class is CPVC) with the two electrode end plates as the '
              'only wetted metal, allowed as BMED electrodes per M6: Ti/MMO anode end plate '
              'and 316L annealed cathode end plate; 316L tie rods clamping the stack from '
              'outside the wetted and vapour zone per M4',
      'basis': 'AQS-STD-002 M2 holds the chlor-alkali and acid-regeneration systems on PVC-U, '
              'and M3 bans a wetted metal part in the reducing catholyte unless M6 names it; '
              'M6 names the BMED electrodes, and its hydrogen clause decides the cathode-plate '
              'alloy between 316L and nickel: metal in wet H2 or at a cathode is austenitic '
              'stainless or titanium only with the H2 partial pressure and temperature stated, '
              'and titanium at a cathode is held for hydriding, so the plate is 316L annealed '
              '- nickel has no M6 basis, and AQS-REV-H2-001 names 316L annealed for EW '
              'cathodes, the same cathode class. The anode plate takes the Ti/MMO '
              'dimensionally-stable-anode class of section 9 (chloride, anodic Cl2). The tie '
              'rods sit outside the wetted envelope and stay isolated from the liquor path '
              '(M4). Inlets arrive trim-cooled at 35 C (X-MAT-19), inside the PVC-U M5 limits '
              'on the polymer path. X-QA-13 reselection of the former undecided 316L-or-nickel '
              'cathode-plate class. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'Nickel 200 cathode hardware only if the caustic compartment later runs hot '
              'strong caustic above the 316L class (ULLMANN_NAOH nickel practice); CPVC frames '
              'if the loop moves above 60 C',
      'note': 'wetted by the 2 M HCl acid-side loop; the electrode end plates are the M6 '
              'hardware and the tie rods the external clamp steel - no other metal is wetted.',
     'task': 'X-QA-13',
    },
    {
      'unit': 'BMED_BASE',
      'dimension': 'BMED stack, base-side loop (NaOH)',
      'clause': 'M2 PVC-U wetted path; M3 electrode exception named by M6 (Ti/MMO anode, 316L '
              'annealed cathode per the hydrogen clause); M4 tie rods outside the wetted and '
              'vapour zone; M5 CPVC above 60 C',
      'mat': 'Wetted path of PVC-U (spacer frames, gasket seals, drip tray, nozzles; above 60 '
              'C the thermoplastic class is CPVC) with the two electrode end plates as the '
              'only wetted metal, allowed as BMED electrodes per M6: Ti/MMO anode end plate '
              'and 316L annealed cathode end plate; 316L tie rods clamping the stack from '
              'outside the wetted and vapour zone per M4',
      'basis': 'AQS-STD-002 M2 holds the chlor-alkali and acid-regeneration systems on PVC-U, '
              'and M3 bans a wetted metal part in the reducing catholyte unless M6 names it; '
              'M6 names the BMED electrodes, and its hydrogen clause decides the cathode-plate '
              'alloy between 316L and nickel: metal in wet H2 or at a cathode is austenitic '
              'stainless or titanium only with the H2 partial pressure and temperature stated, '
              'and titanium at a cathode is held for hydriding, so the plate is 316L annealed '
              '- nickel has no M6 basis, and AQS-REV-H2-001 names 316L annealed for EW '
              'cathodes, the same cathode class. The anode plate takes the Ti/MMO '
              'dimensionally-stable-anode class of section 9 (chloride, anodic Cl2). The tie '
              'rods sit outside the wetted envelope and stay isolated from the liquor path '
              '(M4). Inlets arrive trim-cooled at 35 C (X-MAT-19), inside the PVC-U M5 limits '
              'on the polymer path. X-QA-13 reselection of the former undecided 316L-or-nickel '
              'cathode-plate class. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'Nickel 200 cathode hardware only if the caustic compartment later runs hot '
              'strong caustic above the 316L class (ULLMANN_NAOH nickel practice); CPVC frames '
              'if the loop moves above 60 C',
      'note': 'wetted by the NaOH base-side loop; the electrode end plates are the M6 hardware '
              'and the tie rods the external clamp steel - no other metal is wetted.',
     'task': 'X-QA-13',
    },
    {
      'unit': 'EVAP_ACID',
      'dimension': 'hot 2 M HCl evaporator and HCl column (108.6 C boil)',
      'clause': 'M3/M5 lined-part rule above the thermoplastic limits: PTFE lining, never bare '
              'metal; impregnated-graphite bundle class; borosilicate glass column',
      'mat': 'PTFE-lined carbon-steel shell and vapour separator (M5 lined-part rule; PTFE, '
              'the house fluoropolymer lining class), impregnated-graphite tube bundle, '
              'tubesheets and interchanger, borosilicate glass 3.3 packed HCl column with PTFE '
              'Pall rings and PTFE-lined flanges, PVDF piping on the cold legs; no bare metal '
              'and no stainless or nickel in the HCl circuit',
      'basis': 'hot 2 M HCl boiling at 108.6 C on the graph design (T_boil_C): M3 and M5 rule '
              'out bare metal in this acid service - above the thermoplastic limits the '
              'alternative is a lined part, never bare metal - and the lining class is PTFE, '
              'the fluoropolymer class of the AQS-STD-002 gasket rows (PERRY9_MAT '
              'impervious-graphite class for the bundle; ULLMANN_HCL). The shell of record is '
              'the PTFE-lined carbon steel of AQS-DUTY-060 and the mfg BOM, not a bare polymer '
              'shell. X-QA-13 reselection. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-MAT-22).',
      'alt': 'glass-lined steel shell if lining-repair records ever dominate; nickel 200 '
              'stays the EVAP_BASE hot-caustic class, not this acid service',
      'note': 'the PTFE lining is the corrosion surface and the steel carries the pressure; '
              'lining-integrity check rides the unit task 12 work order; the steam-side relief '
              'trim sits outside the HCl circuit.',
     'task': 'X-QA-13',
    },
    {
      'unit': 'HDR_CO2',
      'dimension': 'dry CO2 utility header',
      'clause': 'M1 dry gas held above its dew point (one-tube family); the N6 drain proves the '
              'dry claim (M3 would catch wet CO2)',
      'mat': '316L tube',
      'basis': 'dry CO2 header at the ambient class (graph design, AQS-DUTY-075): neither the '
              'M3 wet-oxidant rule nor the M7 no-polymer rule applies to a dry gas held above '
              'its dew point, so the header keeps the one-tube family shared across the dry '
              'utility gas headers (CO2, plant air / N2, O2) for spares and handling. '
              'Selection per AQS-STD-002 with the issued AQS-DUTY-075 header service (X-QA-18 '
              'step 3).',
      'alt': 'CPVC or PP-H sections if a cold spot condenses carbonic acid (M3 then catches '
              'wet CO2); the N6 drain exists to prove the dry claim',
      'note': 'the N6 drain and the N7 vent keep the header dry; no measured rate.',
     'task': 'X-QA-18',
    },
    {
      'unit': 'HDR_H2',
      'dimension': 'wet hydrogen header with sweep air and acid mist',
      'clause': 'M3 wet reducing service (no metal wetted part); M5 PVC-U to 60 C; '
              'AQS-REV-H2-001 ignition basis',
      'mat': 'PVC-U, bonded',
      'basis': 'wet H2 with sweep air and possible acid mist off the EW cathode rows (graph '
              'design, AQS-DUTY-075): wet hydrogen is the M3 reducing service, so there is no '
              'metal wetted part - ignition, not embrittlement, governs (AQS-REV-H2-001) - and '
              'PVC-U carries the acid-mist condensate to its 60 C M5 limit (ISO1452_2). '
              'Selection per AQS-STD-002 with the issued AQS-DUTY-075 header service (X-QA-18 '
              'step 3).',
      'alt': 'CPVC if the header temperature class rises above the PVC-U 60 C class (M5); FRP '
              'for an outdoor run',
      'note': 'metal parts bonded per the static rule; the dilution basis is held by the vent '
              'system; no measured rate (X-MAT-06 ruling carried).',
     'task': 'X-QA-18',
    },
    {
      'unit': 'HDR_N2',
      'dimension': 'dry oil-free plant air and nitrogen header',
      'clause': 'M1 inert dry gas (one-tube family; no wet-oxidant or no-polymer rule fires)',
      'mat': '316L tube',
      'basis': 'dry oil-free plant air and nitrogen at the ambient class (graph design, '
              'AQS-DUTY-075): N2 is inert and the air stays dried at the receiver bank, so the '
              'header keeps the one-tube family shared across the dry utility gas headers; M1 '
              'names the stream and no wet-oxidant or no-polymer rule fires. Selection per '
              'AQS-STD-002 with the issued AQS-DUTY-075 header service (X-QA-18 step 3).',
      'alt': 'CS with the AQS-STD-001 corrosion allowance if a section moves into a wet bay '
              'and M1 then names a wet stream',
      'note': 'the drain keeps the header dry; no measured rate.',
     'task': 'X-QA-18',
    },
    {
      'unit': 'HDR_O2',
      'dimension': 'dry oxygen utility header',
      'clause': 'M7 dry O2 (polymers ignite): oxygen-clean 316L, socketless joints (ASTM G93)',
      'mat': '316L tube, oxygen-clean per ASTM_G93, socketless',
      'basis': 'dry O2 header at the atmospheric tube class (graph design, AQS-DUTY-075): '
              'polymers ignite in oxygen-enriched service, so the dry-O2 M7 case applies and '
              'the metal is oxygen-clean 316L with hydrocarbon-free socketless joints '
              '(ASTM_G93 practice). Selection per AQS-STD-002 with the issued AQS-DUTY-075 '
              'header service (X-QA-18 step 3).',
      'alt': 'copper or nickel tube if a section rises above the atmospheric tube class '
              '(pressurized-oxygen design per ASTM_G93)',
      'note': 'oxygen-clean handling and capped ends ride the unit task 12 work order; no '
              'measured rate.',
     'task': 'X-QA-18',
    },
    {
      'unit': 'HDR_UPW',
      'dimension': 'high-purity water distribution header',
      'clause': 'M1 UPW named stream: PVDF SDR 21 fusion-welded for the leach-out and hygiene '
              'class',
      'mat': 'PVDF SDR 21, fusion-welded',
      'basis': 'high-purity water distribution at the ambient class (graph design, '
              'AQS-DUTY-075): UPW is the M1 named stream, and PVDF SDR 21 fusion-welded '
              '(DVS_2207) keeps the leach-out and hygiene class the polish skid is built to '
              'deliver. Selection per AQS-STD-002 with the issued AQS-DUTY-075 header service '
              '(X-QA-18 step 3).',
      'alt': '316L BA tube on valve-manifold sections that need metallic strength, with the '
              'same UPW hygiene class',
      'note': 'ambient temperature class at the polish skid outlet; no measured rate.',
     'task': 'X-QA-18',
    },
    {
      'unit': 'BRINE_CRYS',
      'dimension': 'chloride-brine flash crystallization on a hot leach side-stream',
      'clause': 'M2 leach system; M3 oxidizing chlorate liquor (no bare metal wetted); section '
              '12.1 P2 hot-leach family; M5 CPVC limit with PVDF above it',
      'mat': 'CPVC crystallizer body, hood and agitator on the leach side-stream; PVDF (P3) '
              'pump and jacket legs on any leg above the CPVC class; FKM gaskets; steel frame '
              'and jacket casing outside the wetted and vapour zone',
      'basis': 'CaCl2/MgCl2 crystallization out of the hot chloride leach liquor on a 2 kg/d '
              'side-stream, the mother liquor returned to the leach (graph design; A-M-503): '
              'the leach is an M2 system and its liquor carries the oxidizing chlorate '
              '(AQS-STD-002 section 7), so no bare metal is wetted (M3); the vessel is the '
              'hot-leach family CPVC (section 12.1 P2, M5 limit 93 C, the same liquor class '
              'that sets the 85 C CPVC wall of LEACH_CSTR_1) and PVDF (P3) carries any leg '
              'above the CPVC class. Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-QA-11).',
      'alt': 'borosilicate glass 3.3 body (the HX-5 coil class) if the flash zone runs above '
              'the CPVC 93 C limit at the crystallizer - a higher-rated thermoplastic, glass '
              'or a lined part, never bare metal (M5)',
      'note': 'the crystal slurry leaves as solids to the pot feeders and the mother-liquor '
              'line returns to LEACH_CSTR_1 on the issued P2 hot-leach family; no corrosion '
              'allowance on the polymer wetted path (AQS-STD-001 shop rule); the commissioning '
              'brine assay and salt weigh-in/weigh-out carry the verification (A-M-503).',
     'task': 'X-QA-11',
    },
    {
      'unit': 'NUT_AN',
      'dimension': 'Ostwald ammonia oxidation skid with nitrate neutralization',
      'clause': 'M7 dry hot gas hot face on the bed side (stated case; M6 dielectric break to '
              'the wet train); M3 nitric wet train (no bare metal); section 5 nitric at no '
              'more than 2 M (PVC-U legs, PVDF absorber and pump)',
      'mat': '310S reactor tube and hot-bed hardware around the platinum gauze catalyst bed '
              'on the dry NH3/O2 oxidation side, the gas held above the acid dew point to the '
              'absorption sump, with a dielectric break to the wet train; PVC-U ammonia and '
              'dilution-water legs; PVDF (P3) absorption and neutralization vessel, dosing '
              'pump and product leg on the ammonium-nitrate side; FKM gaskets',
      'basis': 'Ostwald-class oxidation of plant ammonia with plant oxygen, the acid '
              'neutralized back with ammonia to the dosing strength (graph design; A-M-497): '
              'the bed runs hot and dry, so the reactor tube takes the house 310S hot-face '
              'class of the issued COMB_HEAT burner tube (M7 dry hot gas held above the acid '
              'dew point; the case is stated per M7 and isolated from any electrolyte per M6); '
              'the wet train is nitric at the absorption class, an M3 oxidizing service with '
              'no metal wetted part - PVC-U legs and PVDF absorber and pump per section 5 '
              '(nitric at no more than 2 M). Selection per AQS-STD-002 with the duty section 2 '
              'environment (X-QA-11).',
      'alt': 'nickel-alloy (Alloy 600 class) reactor tube if the bed duty moves above the '
              '310S class; borosilicate glass 3.3 absorption if the nitrate liquor ever '
              'concentrates past the PVDF class (M5: glass or a lined part, never bare metal)',
      'note': 'the unconverted slip vents to NOX_SCRUB on the issued scrubber family and its '
              'nitrate liquor stays a booked nutrient; the gauze change-out is a unit task 12 '
              'work order; no corrosion allowance claimed - no measured rate.',
     'task': 'X-QA-11',
    },
)


@fn('sec3_material_selections',
    'duty section 3 material selections per AQS-STD-002: per-unit construction '
    'material from the duty/service, the rules declared in SELECTION_TABLE '
    '(reference writer flow_graph/param/materials3.py)')
def sec3_material_selections(b, inputs):
    """Stamp params.sec3_material on every roster unit; the row is the rule."""
    for row in SELECTION_TABLE:
        b.set_node_field(
            row['unit'], 'params.sec3_material',
            {'mat': row['mat'], 'basis': row['basis'], 'alt': row['alt'],
             'note': row['note'], 'task': row['task']},
            {'stage': 'sec3_material_selections', 'basis': row['clause'],
             'ref': 'AQS-STD-002'})
