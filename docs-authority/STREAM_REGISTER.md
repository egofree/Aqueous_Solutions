# Stream register: streams between blocks

Document number: AQS-STR-001  
Revision: L  
Date: 2026-10-24  
Basis: AQS-MF-001 and the sector equipment lists AQS-EQP-*. Style: AQS-DOC-002. Compliance themes (vents and hydrogen): AQS-COMPL-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue S01–S24 | 2026-09-27 |
| B | 1 | Add S25–S30 water purification (AQS-WTR-001) | 2026-09-27 |
| C | 1 | Add S31–S39 fab wet-reagent forks (AQS-EQP-FAB-RGN-001) | 2026-09-27 |
| D | 1 | Add S40–S42 terrace irrigation / return (AQS-TRR-001) | 2026-09-27 |
| E | 1 | Add S43–S48 geothermal / backup genset (AQS-PWR-002) | 2026-09-27 |
| F | 1 | Add S49–S53 PEM fuel cell (AQS-FC-001) | 2026-09-28 |
| G | 1 | Add S54–S56 CRYO heat / dedicated cool / room vent (AQS-CRY-002) | 2026-09-28 |
| H | 1 | Add S57–S63 metal forming (AQS-MFG-MET-001) | 2026-09-28 |
| I | 1 | Vent closure S64–S72 (AQS-VENT-001); reclassify S24/S56/S62 | 2026-09-28 |
| J | 1 | Study rate pointers (AQS-EQP-VENT-001 and AQS-AUD-001); S48 method note | 2026-10-01 |
| K | 1 | Methanol train streams S73 to S82 (AQS-MeOH-001) | 2026-10-01 |
| L | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; streams unchanged | 2026-10-24 |

## 1. Purpose and scope

Each stream that crosses the boundary of a campus block has a stable identifier, S01, S02 and so on. Process flow diagrams, the mass-flow claims and the equipment lists all use these identifiers. This register lists them with their source, destination, contents, header and the destinations they must never reach.

In scope: streams that cross a campus block boundary. Out of scope: recycle streams inside one aisle (electrowinning overflow, float liquor return, the C29 recycle), which stay on the line process flow diagrams.

Identifiers are stable. An identifier is never reused for a different route; a retired identifier stays retired.

The rates are generated from the plant graph into `flow_graph/derived/STREAM_REGISTER_DERIVED.md` by `flow_graph/export_authority_md.py`. This page is the human-maintained register kept in step with that file. Do not invent dock stream numbers or fill placeholder rates that the graph leaves empty.

## 2. Terms

Table 3.1 has these columns:

- Ph: phase. S solid, L liquid, G gas, E electric or heat.
- Header: the shared pipe, duct or bus that carries the stream.
- Forbidden: destinations the stream must never reach, by tee, leak path or shared return.

Heat streams use the heat ladder Q1 to Q4: Q1 is the hottest (flue) and Q4 the lowest-temperature water loop. Unit and header names are plant graph names; other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Register

Table 3.1. Streams between blocks

| ID | From | To | Ph | Carries | Header | Forbidden |
|---|---|---|---|---|---|---|
| S01 | BMED / UPW POLISH | FARM, WAFER FAB, HABITATION | L | UPW < 1 µS/cm (pre-remin) | HDR_UPW | leach, etch, grey |
| S02 | CRYO O2 + GROW BED | HABITATION | G | O₂ | HDR_O2 | HDR_H2, acid gas |
| S03 | CRYO N2 | WAFER FAB, FARM | G | N₂ | HDR_N2 | process headers |
| S04 | CRYO CO2 + HAB AIR | FARM | G | CO₂ | HDR_CO2 | raw AFTERBURNER flue |
| S05 | H2_DRYER | CRYO H2 or fuel | G | process H₂, dried | dedicated | HDR_O2, HDR_CO2 |
| S06 | Q4 / HVAC | FARM, HABITATION | E | heat < 80 °C | Q4 | Q1 flue in hab air |
| S07 | P-Al / P-Mg / P-Ca + BMED salts | NUTRIENT DOSE | S/L | struvite, NH₄, chelates | tote / dose line | Salria into beds |
| S08 | METALS / ELEMENTS + SILICATE | fab preparation, MFG shop | S | Si, Al, Cu, Fe, acids/bases | crib | FR-4 to pyro |
| S09 | HCl PRODUCT / NaOH PRODUCT | WET BENCH, FARM pH | L | BMED acid / base | pipe | sewer |
| S10 | WET BENCH | REGEN LEACH | L | spent etch + metals | HDR_ETCH | floor drain |
| S11 | GROW BED + GALLEY | HOPPER or OIL LINE | S | plant / food waste | HDR_ORG | glass, FR-4 |
| S12 | HAB WASTE | SALT FEED / NUTRIENT DOSE / HOPPER | L/S | grey, solids | HDR_GREY + HDR_ORG | HDR_ACID_GAS |
| S13 | Farm sump + HVAC | UPW POLISH / SALT FEED / VCD_FEED | L | condensate | HDR_GREY | Salria |
| S14 | GROW BED | HABITATION | S | food | tote | process aisle |
| S15 | GROW BED | HDR_O2 | G | photosynthetic O₂ | HDR_O2 | — |
| S16 | MFG SHOP scrap | HOPPER | S | metal / polymer scrap | conveyor | pyro if FR-4 |
| S17 | SOL_ARK / ZNBR2 / RECTIFIER | all blocks | E | DC / 480 V | tray | battery Br₂ into CRU |
| S18 | AFTERBURNER / air | CRYO | G | flue-carbon claim reference; 0 kg/d CO₂ since graph Rev J (carbon counted once on S67 → FLUE_KO → S67B). Cold-box air is AIR_INTAKE → MOL_SIEVE | CRYO feed | acid-gas header |
| S19 | BAGHOUSE fines | LEACH CSTR 1 | S | dust | existing | farm |
| S20 | LED CANOPY, FAB TOOL, HAB AIR | SOL_ARK bus | E | load | tray | — |
| S21 | ROOF TANK | HAB WATER, farm sump, UPW POLISH | L | clean tower water | gravity + HDR_UPW | Salria, grey, etch |
| S22 | ROOF TANK | CATCH TANK via HYDRO SET | L | same clean inventory | SHAFT_PENSTOCK | process sumps |
| S23 | CATCH TANK | ROOF TANK (pump) / UPW POLISH | L | clean return | SHAFT_PENSTOCK | HDR_GREY |
| S24 | H2_DRYER / CRYO_H2 overpressure | roof contingency (SHAFT_H2) | G | process H₂ relief only | SHAFT_H2 | hab air, HDR_O2, continuous dump |
| S25 | VCD_COND | UPW POLISH / HAB_ED_POLISH | L | VCD distillate | process UPW | potable taps w/o remin + UV |
| S26 | REMIN / POTABLE_TANK | HAB taps (HAB_WATER) | L | remineralized potable | potable + RPZ | wet bench, etch |
| S27 | FAB_UPW_TANK | WET_BENCH | L | fab UPW > 18 MΩ·cm class | fab UPW loop | remin path, grey |
| S28 | VCD_EVAP | REGEN LEACH / SALT FEED | L | VCD brine | process | HDR_UPW, farm beds |
| S29 | GREY_TREAT | VCD_FEED / SALT FEED | L | treated grey | HDR_GREY branch | Salria, etch |
| S30 | BLACK_DIGEST | NUTRIENT DOSE / SALT FEED | L/S | digest liquor / nutrients | dose / HDR_ORG | VCD evaporators (solids), sewer |
| S31 | WS_HF_ED | WET_BENCH | L | HF (aq) | fab acid chase | sewer, HDR_GREY, life |
| S32 | WS_PEROX | WET_BENCH | L | H₂O₂ | fab chem | sewer |
| S33 | WS_AMMONIA | WET_BENCH | L | NH₄OH / NH₃ (aq) | fab chem | hab air |
| S34 | WS_NITRIC / WS_PHOS | WET_BENCH | L | HNO₃ / H₃PO₄ etch suite | fab acid chase | sewer |
| S35 | WS_KOH | WET_BENCH / solar texture stub | L | KOH | fab chem | sewer, farm beds |
| S36 | WS_DOPE / CRU polish | FAB_TOOL dopant cabinets | L/G | B/P/As concentrate; BBr₃ / POCl₃ class | gas cabinet / tote | hab AHU |
| S37 | WS_SLURRY | LAP_CMP / FAB_PREP | L | colloidal silica slurry | slurry loop | sewer |
| S38 | WS_SOLV | FAB_TOOL litho / strip | L | IPA / acetone / N-methyl-2-pyrrolidone class | flammable | sewer, HDR_H2 |
| S39 | LAP_CMP / WET_BENCH / FAB_TOOL | REGEN LEACH / OIL / HDR_ORG | L/S | spent slurry, solvent, photoresist sludge | HDR_ETCH / HDR_ORG | floor drain, farm |
| S40 | OVERFLOW_SPILL_ROOF / ROOF TANK surplus | TERRACE irrig headers | L | clean tower overflow | OVERFLOW_DOWNCOMER_* | FARM_SUMP, S26 potable, Salria |
| S41 | TERRACE underdrain / apron (clean) | CATCH TANK / DRAIN_SEC | L | rain + S40 return | apron / secondary drain | L-1 process bund, HDR_GREY fertigation |
| S42 | Enclosed terrace / greenhouse fertigated drain | GREY treat / VCD_FEED / SALT | L | dilute nutrient drain | HDR_GREY | CATCH, ROOF_TANK, sewer-as-primary |
| S43 | GEO_GHEX | GEO_HP (closed loop) | L/E | geothermal loop fluid | dedicated GEO loop | HDR_UPW, CATCH, Salria |
| S44 | GEO_HP | Q4 / FARM / HAB | E | heat < 80 °C | Q4 | Q1 flue in hab air |
| S45 | CRYO_H2 / H2_DRYER | BACKUP_GEN | G | dried H₂ fuel | GEN fuel manifold | HDR_O2, hab AHU |
| S46 | BACKUP_GEN exhaust | condensate / scrubber | G/L | H₂O + NOx class | S13 class + scrub branch | raw AFTERBURNER, HDR_CO2 as primary |
| S47 | BACKUP_GEN | SOL_ARK GEN port | E | 480 V 3φ AC | GEN feeder | RECT DC bus direct |
| S48 | GEO_ORC (stub) | Sol-Ark AC couple | E | ORC AC (method TBD after GHEX survey) | future AC couple | hard-coded 100 kW on M1 |
| S49 | CRYO_H2 / H2_DRYER | FUEL_CELL | G | dried H₂ fuel | FC fuel manifold | HDR_O2, hab AHU, GEN manifold w/o isolation |
| S50 | CRYO_O2 | FUEL_CELL | G | O₂ oxidizer | FC oxidizer manifold | HDR_H2, HDR_ACID_GAS |
| S51 | FUEL_CELL / FC_DCDC | Sol-Ark BATT DC | E | DC in 160–700 V window | BATT DC tray | GEN AC port, RECT process DC hard-tee |
| S52 | FUEL_CELL | condensate / S13 class | L | PEM product H₂O | S13 / grey-condensate | potable taps w/o remin + UV |
| S53 | FC_HX_Q4 | Q4 / FARM / HAB | E | heat < 80 °C | Q4 | Q1 flue / GEN exhaust in hab air |
| S54 | CRYO_HX_Q4 | Q4 / FARM / HAB | E | warm residual < 80 °C | Q4 | Stirling deep reject, GEN exhaust, flue |
| S55 | CRYO_DED_COOL (loop) | CRYO_DED_COOL | L/E | dedicated cryo utility cooling | dedicated CRYO cool | Q4 life air, HDR_UPW, CATCH, Salria |
| S56 | CRYO_AHU / CRYO_AHU_COND residual | safe vent contingency | G | non-condensable residual after KO | CRYO fire-area AHU | HAB/FARM return, acid-gas header, continuous dump |
| S57 | PROD_METALS / MET_MELT | WIRE_DRAW / COLD_MILL / GAS_ATOMIZER | S/L | billet / melt / charge | MFG metal aisle | polymer, FR-4, pyro |
| S58 | WIRE_DRAW | MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB | S | wire product | tote / crib | — |
| S59 | COLD_MILL | MET_SHEET_BIN / MFG_CRIB | S | sheet / strip | tote / crib | — |
| S60 | GAS_ATOMIZER | MET_POWDER_CRIB / FAB / RepRap | S | metal powder | N₂-blanketed crib | open ignition, HAB air |
| S61 | Forming swarf / trim | HOPPER / leach | S | metal scrap | S16 class / conveyor | FR-4, pyro |
| S62 | MET_AHU | MET_SCRUB / baghouse (S71) | G | MFG metal-aisle capture feed | dedicated MET_AHU | HAB/FARM return, acid-gas as primary |
| S63 | MET_HX_Q4 | Q4 / FARM / HAB | E | heat < 80 °C | Q4 | melt/atomizer hot gas as flue |
| S64 | H2_DRYER | CRYO_H2 | G | dried process H₂ (normal path) | dedicated / SHAFT_H2 branch | hab air, HDR_O2, continuous roof dump |
| S65 | ALK_SCRUBBER residual | ACID_POLISH_SCRUB | G | post-alkali acid-gas residual | HDR_ACID_GAS polish | Br₂ header, CRYO feed, HAB |
| S66 | ACID_POLISH / ALK_SCRUBBER blowdown | CRU | L | scrub liquor → chlorate finish | SCRUBBER_TO_CRU | sewer, Br⁻ liquor, farm beds |
| S67 | AFTERBURNER flue | FLUE_CAP / CRYO | G | captured CO₂ + condensables | CRYO feed (extends S18) | HDR_ACID_GAS, HAB air, raw HDR_CO2 |
| S68 | FLUE_CAP / CRYO_AHU_COND | S13 class / treat | L | flue / AHU condensate | condensate header | potable taps, HDR_UPW |
| S69 | ZNBR2_BR2_REGEN | ZnBr2 positive tank | L | Br⁻ makeup after ORP | Br₂ scrub liquor return | CRU, alkali scrub liquor |
| S70 | CRYO_AHU_COND condensable | COLD_BOX / CRYO condensate return | G/L | boil-off / purge condensables | CRYO return | HAB/FARM return, acid-gas |
| S71 | MET_AHU | MET_SCRUB / baghouse | G | metal-aisle fume / mist / dust | MET capture train | HAB return, HDR_ACID_GAS primary |
| S72 | MET_SCRUB / baghouse | CSTR 1 / OIL / HDR_ORG | L/S | fines + scrub liquor / organic mist | S19 class / HDR_ORG | sewer-as-primary, farm beds |
| S73 | CRYO_CO2 / S67 / air | MEOH_DAC_OR_CO2 / MEOH_SYNTH / MEOH_IEM_CELL | G | CO₂ feedstock for MeOH | MeOH train | HDR_H2, potable |
| S74 | CRYO_H2 | MEOH_SYNTH / MEOH_IEM_CELL | G | H₂ for MeOH synth (surplus vs PEM/GEN) | MeOH H₂ branch | HDR_O2, continuous dump |
| S75 | MEOH_SYNTH / MEOH_IEM_CELL | MEOH_COND / MEOH_DIST | L/G | crude MeOH + water | MeOH process | potable, CATCH |
| S76 | MEOH_TANK / MEOH_DAY_TANK | MEOH_FC | L | liquid MeOH fuel | PC-11 | HDR_UPW, HAB air |
| S77 | MEOH_FERM_STILL | MEOH_TANK | L | biogenic MeOH | MeOH polish | sewer-as-primary |
| S78 | Farm/hab organics (S12/S30 class) | MEOH_FERM_DIG | L/S | ferment feed | HDR_ORG branch | CATCH potable |
| S79 | MEOH_FC / MEOH_DCDC | Sol-Ark BATT DC | E | DC 160–700 V window | BATT DC tray | GEN port, RECT hard-tee |
| S80 | MEOH_HX_Q4 | Q4 / FARM / HAB | E | heat < 80 °C | Q4 | Q1 flue / GEN exhaust in AHU |
| S81 | MEOH_FC / MEOH_COND | condensate / S13 class | L | product / process H₂O | S13 | potable w/o remin |
| S82 | MEOH_FC / MEOH_VENT_KO | CRYO_CO2 / FARM (Claimed) | G | CO₂ return from MeOH FC | Claimed carbon | free outdoor dump, HAB return |

## 4. Notes by system

- Heat ladder: Q1 to Q4 are unchanged. Q3 still serves the leach, the dryer, the digester and HX-8. Q4 is the only heat that enters the habitation and farm air.
- Water purification (AQS-WTR-001): the roof and catch tanks (S21 to S23) are inventory; the vapour-compression distillation (S25, S28) is regeneration. Both are required.
- Terrace landscape (AQS-TRR-001): S40 and S41 are clean overflow and return; S42 is fertigated greenhouse drain only, not open-landscape irrigation.
- Geothermal and backup power (AQS-PWR-002): S43 and S44 are the thermal loop; S45 to S47 the hydrogen generator; S48 the organic Rankine cycle electrical stub, whose method waits for the ground heat exchanger survey (AQS-AUD-001 §10.4). No power rating is invented for it.
- PEM fuel cell (AQS-FC-001): S49 and S50 bring hydrogen and oxygen to the fuel cell; S51 is DC to the Sol-Ark battery port; S52 product water; S53 fuel-cell heat to Q4. The fuel cell is not `BACKUP_GEN` (S47).
- Cryogenic cold box (AQS-CRY-002): S54 is warm reject heat to Q4 through `CRYO_HX_Q4`; S55 the dedicated cryogenic cooling, not life air; S56 the residual after `CRYO_AHU_COND`; S70 the return of condensables (AQS-VENT-001).
- Metal forming (AQS-MFG-MET-001): S57 is the melt and billet feed; S58 to S60 wire, sheet and powder; S61 scrap to the hopper; S62 and S71 `MET_AHU` to `MET_SCRUB`; S72 the returns; S63 `MET_HX_Q4` to Q4. `MET_MELT` is not the pyrolysis unit.
- Vent closure (AQS-VENT-001): S64 takes hydrogen to `CRYO_H2` (S24 is a contingency only); S65 and S66 acid polish to the CRU; S67 and S68 flue capture to CRYO; S69 bromine regeneration to the positive tank of the zinc-bromide battery; S70 to S72 as above. Continuous release to open air is not design intent.
- Methanol train (AQS-MeOH-001): S73 to S75 synthesis; S76 and S77 fuel inventory; S78 fermentation feed; S79 `MEOH_FC` to the battery DC port, alongside S51; S80 heat to Q4; S81 condensate; S82 claimed carbon dioxide. The PEM fuel cell (S49 to S53) is kept. Continuous power ratings are in AQS-REQ-KW-001.
