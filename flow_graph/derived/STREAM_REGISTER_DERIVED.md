# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev N (`plant_flow_graph.json`)
Generated: 2026-10-09
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.
Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.

| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |
|---|---|---|---|---|---|---|---|---|
| C29_RECYCLE | PROD_C29 | C29_RECYCLE | L | mass | present | C29 heavy cut | 1.4046 kg/d | — |
| C29_TO_PYRO | C29_RECYCLE | OIL_PYRO | L | mass | present | C29 heavy cut | 1.4046 kg/d | — |
| CUT-1 | OIL_FRAC | PROD_C5_C10 | L | mass | present | fractionator cut | 11.1553 kg/d | — |
| CUT-2 | OIL_FRAC | PROD_C11_C18 | L | mass | present | fractionator cut | 8.4068 kg/d | — |
| CUT-3 | OIL_FRAC | PROD_C19_C28 | L | mass | present | fractionator cut | 3.9472 kg/d | — |
| CUT-4 | OIL_FRAC | PROD_C29 | L | mass | present | fractionator cut | 1.4046 kg/d | — |
| DOCK_EXPORT_TBD | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | present | goods / cassettes / surplus freight (ID TBD) | 28.7542 kg/d | no_S_id,high_severity_audit |
| HL-AFTERBURNER-Q1-A | AFTERBURNER | Q1_A | heat | thermal | present | Q1 flue, not Q4 | 1.383 kW | — |
| HL-AFTERBURNER-Q1-B | AFTERBURNER | Q1_B | heat | thermal | present | Q1 flue, not Q4 | 1.383 kW | — |
| HL-GLASS_BURNOUT-Q2-A | GLASS_BURNOUT | Q2_A | heat | thermal | present | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-GLASS_BURNOUT-Q2-B | GLASS_BURNOUT | Q2_B | heat | thermal | present | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-HX8-Q4-A | HX8 | Q4_A | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 2.286 kW | — |
| HL-HX8-Q4-B | HX8 | Q4_B | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 2.286 kW | — |
| HL-Q1-A-DOWN | Q1_A | Q2_A | heat | thermal | present | downhill heat pipe | 1.133 kW | — |
| HL-Q1-B-DOWN | Q1_B | Q2_B | heat | thermal | present | downhill heat pipe | 1.133 kW | — |
| HL-Q1-X | Q1_A | Q1_B | heat | thermal | present | cross-tie, hot to cold only | 1.383 kW | — |
| HL-Q1-X-BA | Q1_B | Q1_A | heat | thermal | present | cross-tie, hot to cold only | 1.383 kW | — |
| HL-Q2-A-DOWN | Q2_A | Q3_A | heat | thermal | present | downhill heat pipe | 1.888 kW | — |
| HL-Q2-B-DOWN | Q2_B | Q3_B | heat | thermal | present | downhill heat pipe | 1.888 kW | — |
| HL-Q2-X | Q2_A | Q2_B | heat | thermal | present | cross-tie, hot to cold only | 2.027 kW | — |
| HL-Q2-X-BA | Q2_B | Q2_A | heat | thermal | present | cross-tie, hot to cold only | 2.027 kW | — |
| HL-Q3-A-DOWN | Q3_A | Q4_A | heat | thermal | present | downhill heat pipe | 1.614 kW | — |
| HL-Q3-B-DOWN | Q3_B | Q4_B | heat | thermal | present | downhill heat pipe | 1.614 kW | — |
| HL-Q3-A-HX4 | Q3_A | OIL_DRYER | heat | thermal | present | HX-4 Q3 process heat (dryer jacket) | 0.302 kW | — |
| HL-Q3-A-HX5 | Q3_A | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 7.941 kW | — |
| HL-Q3-A-HX6 | Q3_A | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 2.079 kW | — |
| HL-Q3-B-HX4 | Q3_B | OIL_DRYER | heat | thermal | present | HX-4 Q3 process heat (dryer jacket) | 0.302 kW | — |
| HL-Q3-B-HX5 | Q3_B | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 7.941 kW | — |
| HL-Q3-B-HX6 | Q3_B | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 2.079 kW | — |
| HL-Q3-X | Q3_A | Q3_B | heat | thermal | present | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q3-X-BA | Q3_B | Q3_A | heat | thermal | present | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q4-A-BUS | Q4_A | Q4_BUS | heat | thermal | present | water <80 C | 5.51 kW | — |
| HL-Q4-B-BUS | Q4_B | Q4_BUS | heat | thermal | present | water <80 C | 5.51 kW | — |
| HL-Q4-X | Q4_A | Q4_B | heat | thermal | present | cross-tie, hot to cold only | 1.565 kW | — |
| HL-Q4-X-BA | Q4_B | Q4_A | heat | thermal | present | cross-tie, hot to cold only | 1.565 kW | — |
| IA-BMED-01 | BMED_ACID | WS_NITRIC | L | mass | present | HCl product | 0.6456 kg/d | — |
| IA-BMED-02 | BMED_BASE | WS_KOH | L | mass | present | NaOH product | 0.27 kg/d | — |
| IA-BMED-03 | LEACH_CSTR_1 | BMED_ACID | L | mass | present | CRU → BMED acid regen loop | 108.195 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | LEACH_CSTR_1 | BMED_BASE | L | mass | present | CRU → BMED base regen loop | 118.7 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | present | Hydro turbine-pump electrical (MISSING on SLD) | 0.2917 kW | ess_layer,missing_on_sld |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | present | ZnBr2 charge (PV/RECT surplus) | 6.6667 kW | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | present | ZnBr2 discharge to bus | 5.0 kW | ess_layer |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW overflow | 4222.22 kg/d | — |
| IA-EW-02 | EW_2 | EW_3 | L | mass | present | EW overflow | 4160.42 kg/d | — |
| IA-EW-03 | EW_3 | EW_4 | L | mass | present | EW overflow | 4137.94 kg/d | — |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR to EW-1 | 4284.0 kg/d | — |
| IA-EW-05 | EW_5 | EW_6 | L | mass | present | EW overflow | 4128.07 kg/d | — |
| IA-EW-06 | EW_6 | EW_7 | L | mass | present | EW overflow | 4122.6 kg/d | — |
| IA-EW-07 | EW_7 | EW_8 | L | mass | present | EW overflow | 4051.46 kg/d | — |
| IA-EW-08 | EW_8 | EW_9 | L | mass | present | EW overflow | 4046.41 kg/d | — |
| IA-EW-09 | EW_9 | POLISH_BANK | L | mass | present | EW tail to polish | 3983.16 kg/d | — |
| IA-EW-10 | EW_4 | EW_5 | L | mass | present | EW overflow | 4133.09 kg/d | — |
| IA-GLASS-01 | GLASS_RINSE | GLASS_MILL | S | mass | present | rinsed cullet | 36.8182 kg/d | — |
| IA-GLASS-02 | GLASS_MILL | GLASS_BURNOUT | S | mass | present | milled cullet | 30.0 kg/d | — |
| IA-GLASS-03 | GLASS_BURNOUT | GLASS_DIGEST | S | mass | present | burned cullet | 30.0 kg/d | — |
| IA-HDR-H2-01 | EW_1 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l1_topology,wp_l2_filled,ew_cascade_exploded |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 6.4 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure,ew_cascade_exploded |
| IA-HDR-H2-03 | EW_2 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HX8 | EW_1 | HX8 | heat | thermal | present | EW heat | 4.572 kW | — |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | present | Dryer → pyro | 33.0 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | present | Pyro → frac | 28.9046 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | NCG_HEADER | G | mass | present | NCG only | 5.0 kg/d | — |
| IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | L | mass | present | raffinate (EW tail after polish) to continuous recycle | 3753.71 kg/d | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | continuous recycle liquor | 3753.71 kg/d | — |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | present | Float/sink liquor return | 343.1 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| NCG_TO_AB | NCG_HEADER | AFTERBURNER | G | mass | present | NCG | 5.0 kg/d | — |
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 95.0 kg/d | — |
| S02 | CRYO_O2 | HABITATION | G | mass | present | O2 | 3.36 kg/d | — |
| S03 | CRYO_N2 | WAFER_FAB | G | mass | present | N2 | 1.4998 kg/d | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 1.109 kg/d | — |
| S05 | H2_DRYER | CRYO_H2 | G | mass | present | process H2 | 6.4 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | 0.0 kW | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 42.0 kg/d | — |
| S08G | GLASS_DIGEST | BOUNDARY_EXPORT | S | mass | present | glass/ceramic goods | 30.0 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S09 | BMED_ACID | WET_BENCH | L | mass | present | HCl | 9.2772 kg/d | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 78.3397 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | GREY_TREAT | L/S | mass | present | grey/solids | 131.38 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | present | condensate | 31.4995 kg/d | absent_from_candidate_mvs |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 2.4 kg/d | — |
| S14X | GROW_BED | BOUNDARY_EXPORT | S | mass | present | food surplus export | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | 0.0 kg/d | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.0 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 23.32 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | flue-carbon claim reference (no CO2 mass since Rev J) | 0.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | 0.75 kg/d | absent_from_candidate_mvs |
| S20 | SOL_ARK_60K | GROW_BED | E | elec | present | load | 5.0 kW | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 120.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | 0.4088 kW | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | 0.4088 kW | — |
| S24 | H2_DRYER | RELIEF_H2 | G | mass | present | H2 relief contingency | 0.0 kg/d | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | present | VCD distillate | 168.22 kg/d | — |
| S26 | REMIN | HABITATION | L | mass | present | potable | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | 60.0 kg/d | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | VCD brine | 17.8892 kg/d | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | present | treated grey | 104.5 kg/d | absent_from_candidate_mvs |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | 16.43 kg/d | absent_from_candidate_mvs |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | 1.5 kg/d | absent_from_candidate_mvs |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | 3.0 kg/d | absent_from_candidate_mvs |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | 3.0 kg/d | absent_from_candidate_mvs |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | 0.2725 kg/d | absent_from_candidate_mvs |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | 0.01 kg/d | absent_from_candidate_mvs |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | 3.3 kg/d | absent_from_candidate_mvs |
| S38 | WET_BENCH | OIL_FRAC | L | mass | present | resist and solvent waste | 0.006 kg/d | — |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry and etch liquor | 3.31 kg/d | — |
| S39B | WAFER_FAB | OIL_FRAC | L | mass | present | solvent and photoresist | 0.9875 kg/d | — |
| S40 | ROOF_TANK | TERRACE_IRRIG | L | mass | present | clean overflow | 0.0 kg/d | — |
| S41 | TERRACE_IRRIG | CATCH_TANK | L | mass | present | rain + S40 return | 0.0 kg/d | absent_from_candidate_mvs |
| S42 | TERRACE_IRRIG | GREY_TREAT | L | mass | present | dilute nutrient drain | 0.0 kg/d | absent_from_candidate_mvs |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | 0.0 kW | absent_from_candidate_mvs |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0 kW | absent_from_candidate_mvs |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | H2 fuel | 0.0 kg/d | — |
| S46 | BACKUP_GEN | NOX_SCRUB | L/G | mass | present | exhaust condensate / NOx | 250.56 kg/d | — |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 2.5 kW | — |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 4.8 kg/d | — |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 3.46 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | present | PEM product H2O | 42.8929 kg/d | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | 1.1419 kW | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | 0.5448 kW | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | 4.2838 kW | absent_from_candidate_mvs |
| S56 | CRYO_AHU | RELIEF_CRYO | G | mass | present | non-condensable residual after KO | 0.0 kg/d | — |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | 4.3789 kg/d | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | 3.941 kg/d | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | 3.9529 kg/d | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | 3.1999 kg/d | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | 1.1971 kg/d | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | 2131.07 kg/h | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0171 kW | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | placeholder | H2 normal path | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | 1562.91 kg/h | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | 27.3623 kg/d | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | FLUE_KO | G | mass | present | flue N2/O2/CO2/NOx | 241.7 kg/d | — |
| S67B | FLUE_KO | CRYO_CO2 | G | mass | present | CO2-rich gas after KO | 13.304 kg/d | — |
| S68 | CRYO_AHU | LEACH_CSTR_1 | L | mass | present | flue condensate | 173.67 kg/d | — |
| S69 | ZNBR2 | ZNBR2_BR2_REGEN | G | mass | present | Br2 vapor | 852.47 kg/d | — |
| S69B | ZNBR2_BR2_REGEN | ZNBR2 | L | mass | present | NaBr after ORP | 852.473 kg/d | — |
| S70 | CRYO_AHU_COND_CONDENSABLE | FLUE_KO | L | mass | present | condensables | 0.0521 kg/d | — |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | 852.43 kg/h | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | metal fines and aqueous scrub liquor | 2.4366 kg/d | — |
| S72B | MET_SCRUB | OIL_FRAC | L | mass | present | organic mist | 0.0158 kg/d | — |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 6.9 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 1.6 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 8.5 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | ess | present | MeOH fuel | 8.53 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | 0.0146 kg/d | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | 0.36 kg/d | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 0.5 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | 0.3689 kW | absent_from_candidate_mvs |
| S81 | MEOH_FC | MEOH_COND | L | mass | present | MeOH FC condensate | 5.6223 kg/d | — |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 6.875 kg/d | — |
| S83 | CRYO_O2 | HDR_O2 | G | mass | present | O2 product | 0.0 kg/d | — |
| S84 | CRYO_N2 | HDR_N2 | G | mass | present | N2 product | 0.0 kg/d | — |
| S85 | CRYO_CO2 | HDR_CO2 | G | mass | present | CO2 product after FLUE_KO | 12.17 kg/d | — |
| S86 | CRYO_AHU | RELIEF_CRYO | G | mass | placeholder | cryo residual contingency | 0.0 kg/d | — |
| S87 | GROW_BED | CRYO_O2 | G | mass | placeholder | surplus O2 capture | — | — |
| S88 | CRYO_N2 | GROW_BED | G | mass | placeholder | N2 make-up | — | — |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO3 | 0.65 kg/d | — |
| S34B | WS_PHOS | WET_BENCH | L | mass | present | H3PO4 | 0.625 kg/d | — |
| S89 | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment dose (FARM AHU supply) | 16.191 kg/d | — |
| S90 | HABITATION | HDR_CO2 | G | mass | present | metabolic CO2 (desorbed from the HAB CO2 sorbent bed) | 4.021 kg/d | — |
| IA-GREY-01 | GREY_TREAT | LEACH_CSTR_1 | S/L | mass | present | grey sludge | 35.3672 kg/d | — |
| IA-CRU-01 | CRU | LEACH_CSTR_1 | L | mass | present | sodium chlorate liquor | 27.3623 kg/d | — |
| IA-ACID-01 | BMED_ACID | LEACH_CSTR_1 | L | mass | present | regen HCl, 20 wt% | 98.2722 kg/d | — |
| IA-BASE-01 | BMED_BASE | GLASS_DIGEST | L | mass | present | digest NaOH, 20 wt% | 118.43 kg/d | — |
| HL-Q4-REJ | Q4_BUS | GEO_ORC | thermal | thermal | present | Q4 surplus heat | 11.7617 kW | — |
| IA-PV-01 | PV_ARRAY | SOL_ARK_60K | electric | energy | present | PV daily average | 23.235 kW | — |
| IA-ZNBR-BD | ZNBR2 | GREY_TREAT | L | mass | present | electrolyte bleed | 8.4872 kg/d | — |
| IA-NUT-01 | NUTRIENT_DOSE | VCD_TRAIN | L | mass | present | digest surplus | 13.93 kg/d | — |
| IA-UPW-FAB | BMED_UPW_POLISH | FAB_UPW_TANK | L | mass | present | fab UPW | 60.0 kg/d | — |
| IA-UPW-REMIN | BMED_UPW_POLISH | REMIN | L | mass | present | remineralizer | 10.0 kg/d | — |
| IA-UPW-REJ | BMED_UPW_POLISH | LEACH_CSTR_1 | L | mass | present | polish reject | 3.22 kg/d | — |
| IA-Q4-LIFE | Q4_BUS | HABITATION | thermal | thermal | present | life heat | 3.0 kW | — |
| IA-AB-FLUE | AFTERBURNER | AFTERBURNER_FLUE | G | mass | present | flue | 5.8 kg/d | — |
| IA-ZNBR-MU | LEACH_CSTR_1 | ZNBR2 | L | mass | present | electrolyte water make-up | 8.4872 kg/d | — |
| IA-EW-MET-1 | EW_1 | MFG_SHOP | S | mass | present | plated sheet | 59.87 kg/d | — |
| IA-EW-MET-2 | EW_2 | MFG_SHOP | S | mass | present | plated sheet | 59.89 kg/d | — |
| IA-EW-MET-3 | EW_3 | MFG_SHOP | S | mass | present | plated sheet | 22.48 kg/d | — |
| IA-EW-MET-4 | EW_4 | MFG_SHOP | S | mass | present | plated sheet | 4.85 kg/d | — |
| IA-EW-MET-5 | EW_5 | MFG_SHOP | S | mass | present | plated sheet | 5.02 kg/d | — |
| IA-EW-MET-6 | EW_6 | MFG_SHOP | S | mass | present | plated sheet | 5.47 kg/d | — |
| IA-EW-MET-7 | EW_7 | MFG_SHOP | S | mass | present | plated sheet | 71.14 kg/d | — |
| IA-EW-MET-8 | EW_8 | MFG_SHOP | S | mass | present | plated sheet | 5.05 kg/d | — |
| IA-EW-MET-9 | EW_9 | MFG_SHOP | S | mass | present | plated sheet | 61.34 kg/d | — |
| IA-POL-CAKE | POLISH_BANK | BOUNDARY_EXPORT | S | mass | present | polish cake | 229.45 kg/d | — |
| IA-AB-AIR | CRYO_N2 | AFTERBURNER_FLUE | G | mass | present | combustion air | 235.9 kg/d | — |
| IA-FLUE-EXH | FLUE_KO | BOUNDARY_EXPORT | G | mass | present | flue exhaust | 228.95 kg/d | — |
| IA-DIG-LIQ | GLASS_DIGEST | LEACH_CSTR_1 | L | mass | present | silicate liquor | 118.43 kg/d | — |
| IA-MILL-LOSS | GLASS_MILL | BOUNDARY_EXPORT | S | mass | present | mill dust | 6.82 kg/d | — |
| IA-MFG-OUT | MFG_SHOP | BOUNDARY_EXPORT | S | mass | present | finished goods | 335.0 kg/d | — |
| IA-BED-H2O | ROOF_TANK | GROW_BED | L | mass | present | irrigation | 16.7 kg/d | — |
| IA-MEOH-H2O | MEOH_SYNTH | MEOH_COND | L | mass | present | synth water | 0.0 kg/d | — |
| IA-FC-AIR | CRYO_O2 | MEOH_FC | G | mass | present | cell air | 7.5 kg/d | — |
| IA-Q3A-TRIM | RECTIFIER | Q3_A | electric | thermal | present | leach heater trim | 10.048 kW | — |
| IA-Q3B-TRIM | RECTIFIER | Q3_B | electric | thermal | present | leach heater trim | 10.048 kW | — |
| IA-LEACH-BD | LEACH_CSTR_1 | BOUNDARY_EXPORT | L | mass | present | level bleed | 106.48 kg/d | — |
| IA-VCD-BD | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | still bottoms | 6.71 kg/d | — |
| IA-CHAR | OIL_PYRO | BOUNDARY_EXPORT | S | mass | present | pyro char | 5.5 kg/d | — |
| IA-FC-EXH | MEOH_FC | BOUNDARY_EXPORT | G | mass | present | cell exhaust | 3.53 kg/d | — |
| IA-ZNBR-HEAT | ZNBR2 | Q4_BUS | thermal | thermal | present | round-trip loss | 1.67 kW | — |
| IA-Q4A-TRIM | RECTIFIER | Q4_A | electric | thermal | present | store trim | 1.61 kW | — |
| IA-Q4B-TRIM | RECTIFIER | Q4_B | electric | thermal | present | store trim | 1.61 kW | — |
| IA-FAB-LOSS | WAFER_FAB | BOUNDARY_EXPORT | S | mass | present | kerf | 0.51 kg/d | — |
| IA-WIRE-LOSS | WIRE_DRAW | BOUNDARY_EXPORT | S | mass | present | draw scrap | 0.44 kg/d | — |
| IA-Q1A-LOSS | Q1_A | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.25 kW | — |
| IA-Q1B-LOSS | Q1_B | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.25 kW | — |
| IA-Q2A-LOSS | Q2_A | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.17 kW | — |
| IA-Q2B-LOSS | Q2_B | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.17 kW | — |
