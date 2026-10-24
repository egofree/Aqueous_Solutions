# Stream register — inter-block only

Document number: AQS-STR-001  
Revision: K  
Date: 2026-10-01  
Authority: AQS-MF-001, sector AQS-EQP-*; style AQS-DOC-001; compliance AQS-COMPL-001 (vent/H₂ themes).

> **WP-Ap3 derived sync:** Generated excerpt lives at
> `flow_graph/derived/STREAM_REGISTER_DERIVED.md` (from `plant_flow_graph.json`
> via `flow_graph/export_authority_md.py`). This CAD file remains the human
> narrative + inter-block S## sync target (hybrid — not overwritten wholesale).
> Do not invent DOCK S## or fill null placeholder rates.

Intra-aisle streams (EW overflow, float liquor return, C29 recycle)
stay on the line PFDs. This table is what crosses a campus block
boundary. IDs are stable. Do not reuse an ID for a different route.

Phase: S solid, L liquid, G gas, E electric / heat.

## Purpose

Provide stable inter-block stream IDs (S##) so PFDs, mass-flow claims,
and equipment lists do not reuse an ID for a different route.

## Scope

In: streams that cross a campus block boundary.  
Out: intra-aisle recycle (EW overflow, float return, C29) — remain on line PFDs.


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
| J | 1 | Study rate pointers (VENT-EQP / AUDIT); S48 method note | 2026-10-01 |

| ID | From | To | Ph | Carries | Header | Forbidden |
|---|---|---|---|---|---|---|
| S01 | BMED / UPW POLISH | FARM, WAFER FAB, HABITATION | L | UPW < 1 µS/cm (pre-remin) | HDR_UPW | leach, etch, grey |
| S02 | CRYO O2 + GROW BED | HABITATION | G | O₂ | HDR_O2 | HDR_H2, acid gas |
| S03 | CRYO N2 | WAFER FAB, FARM | G | N₂ | HDR_N2 | process headers |
| S04 | CRYO CO2 + HAB AIR | FARM | G | CO₂ | HDR_CO2 | raw AFTERBURNER flue |
| S05 | H2_DRYER | CRYO H2 or fuel | G | process H₂, dried | dedicated | HDR_O2, HDR_CO2 |
| S06 | Q4 / HVAC | FARM, HABITATION | E | heat < 80 °C | Q4 | Q1 flue in hab air |
| S07 | P-Al / P-Mg / P-Ca + BMED salts | NUTRIENT DOSE | S/L | struvite, NH₄, chelates | tote / dose line | Salria into beds |
| S08 | METALS / ELEMENTS + SILICATE | FAB PREP, MFG SHOP | S | Si, Al, Cu, Fe, acids/bases | crib | FR-4 to pyro |
| S09 | HCl PRODUCT / NaOH PRODUCT | WET BENCH, FARM pH | L | BMED acid / base | pipe | sewer |
| S10 | WET BENCH | REGEN LEACH | L | spent etch + metals | HDR_ETCH | floor drain |
| S11 | GROW BED + GALLEY | HOPPER or OIL LINE | S | plant / food waste | HDR_ORG | glass, FR-4 |
| S12 | HAB WASTE | SALT FEED / NUTRIENT DOSE / HOPPER | L/S | grey, solids | HDR_GREY + HDR_ORG | HDR_ACID_GAS |
| S13 | FARM SUMP + HVAC | UPW POLISH / SALT FEED / VCD_FEED | L | condensate | HDR_GREY | Salria |
| S14 | GROW BED | HABITATION | S | food | tote | process aisle |
| S15 | GROW BED | HDR_O2 | G | photosynthetic O₂ | HDR_O2 | — |
| S16 | MFG SHOP scrap | HOPPER | S | metal / polymer scrap | conveyor | pyro if FR-4 |
| S17 | SOL_ARK / ZNBR2 / RECTIFIER | all blocks | E | DC / 480 V | tray | battery Br₂ into CRU |
| S18 | AFTERBURNER / air | CRYO | G | flue-carbon claim reference; 0 kg/d CO₂ since graph Rev J (carbon counted once on S67 → FLUE_KO → S67B). Cold-box air is AIR_INTAKE → MOL_SIEVE | CRYO feed | acid-gas header |
| S19 | BAGHOUSE fines | LEACH CSTR 1 | S | dust | existing | farm |
| S20 | LED CANOPY, FAB TOOL, HAB AIR | SOL_ARK bus | E | load | tray | — |
| S21 | ROOF TANK | HAB WATER, FARM SUMP, UPW POLISH | L | clean tower water | gravity + HDR_UPW | Salria, grey, etch |
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
| S38 | WS_SOLV | FAB_TOOL litho / strip | L | IPA / acetone / NMP class | flammable | sewer, HDR_H2 |
| S39 | LAP_CMP / WET_BENCH / FAB_TOOL | REGEN LEACH / OIL / HDR_ORG | L/S | spent slurry, solvent, photoresist sludge | HDR_ETCH / HDR_ORG | floor drain, farm |
| S40 | OVERFLOW_SPILL_ROOF / ROOF TANK surplus | TERRACE irrig headers | L | clean tower overflow | OVERFLOW_DOWNCOMER_* | FARM_SUMP, S26 potable, Salria |
| S41 | TERRACE underdrain / apron (clean) | CATCH TANK / DRAIN_SEC | L | rain + S40 return | apron / secondary drain | L-1 process bund, HDR_GREY fertigation |
| S42 | Enclosed terrace / GH fertigated drain | GREY treat / VCD_FEED / SALT | L | dilute nutrient drain | HDR_GREY | CATCH, ROOF_TANK, sewer-as-primary |
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
| S66 | ACID_POLISH / ALK blowdown | CRU | L | scrub liquor → chlorate finish | SCRUBBER_TO_CRU | sewer, Br⁻ liquor, farm beds |
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



Heat ladder Q1–Q4 is unchanged. Q3 still serves leach, dryer, digest,
HX-8. Q4 is the only heat that enters HABITATION and FARM air.

Water purification authority: AQS-WTR-001. Roof–catch (S21–S23) is
inventory; VCD (S25/S28) is regeneration — both required.
Terrace landscape: AQS-TRR-001. S40–S41 are clean overflow / return;
S42 is fertigated greenhouse drain only (not open-landscape irrigation).
Geothermal / backup power: AQS-PWR-002. S43–S44 thermal loop; S45–S47 H₂ genset;
S48 ORC electric stub (method TBD after GHEX survey — AQS-AUD-001 §10.4; no invent kW).
PEM fuel cell: AQS-FC-001. S49–S50 H₂/O₂ to FC; S51 DC to Sol-Ark BATT;
S52 product water; S53 FC heat → Q4. FC ≠ BACKUP_GEN (S47).
CRYO cold box: AQS-CRY-002. S54 warm reject → Q4 via CRYO_HX_Q4; S55 dedicated
cryo cooling (not life air); S56 residual after CRYO_AHU_COND; S70 condensable return (AQS-VENT-001).
Metal forming: AQS-MFG-MET-001. S57 melt/billet feed; S58–S60 wire/sheet/powder;
S61 scrap → HOPPER; S62/S71 MET_AHU → MET_SCRUB; S72 returns; S63 MET_HX_Q4 → Q4. MET_MELT ≠ pyro.

Vent closure: AQS-VENT-001. S64 H₂ → CRYO_H2 (S24 contingency only); S65–S66 acid
polish → CRU; S67–S68 flue-cap → CRYO; S69 Br₂ regen → ZnBr2 pos.; S70–S72 as above.
No free outdoor dump as design intent.

Methanol train: AQS-MeOH-001. S73–S75 synth; S76–S77 fuel inventory; S78 ferment
feed; S79 MEOH_FC → BATT DC (peer to S51); S80 Q4; S81 condensate; S82 Claimed CO₂.
PEM FC (S49–S53) retained. Continuous kW: AQS-REQ-KW-001.

