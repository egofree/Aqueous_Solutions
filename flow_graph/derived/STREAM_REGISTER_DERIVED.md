# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev M (`plant_flow_graph.json`)
Generated: 2026-10-08
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
| DOCK_EXPORT_TBD | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | present | goods / cassettes / surplus freight (ID TBD) | 40.7542 kg/d | no_S_id,high_severity_audit |
| HL-AFTERBURNER-Q1-A | AFTERBURNER | Q1_A | heat | thermal | present | Q1 flue, not Q4 | 1.383 kW | — |
| HL-AFTERBURNER-Q1-B | AFTERBURNER | Q1_B | heat | thermal | present | Q1 flue, not Q4 | 1.383 kW | — |
| HL-GLASS_BURNOUT-Q2-A | GLASS_BURNOUT | Q2_A | heat | thermal | present | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-GLASS_BURNOUT-Q2-B | GLASS_BURNOUT | Q2_B | heat | thermal | present | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-HX8-Q4-A | HX8 | Q4_A | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 5.715 kW | — |
| HL-HX8-Q4-B | HX8 | Q4_B | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 5.715 kW | — |
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
| HL-Q3-A-HX5 | Q3_A | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 5.753 kW | — |
| HL-Q3-A-HX6 | Q3_A | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 2.079 kW | — |
| HL-Q3-B-HX4 | Q3_B | OIL_DRYER | heat | thermal | present | HX-4 Q3 process heat (dryer jacket) | 0.302 kW | — |
| HL-Q3-B-HX5 | Q3_B | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 5.753 kW | — |
| HL-Q3-B-HX6 | Q3_B | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 2.079 kW | — |
| HL-Q3-X | Q3_A | Q3_B | heat | thermal | present | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q3-X-BA | Q3_B | Q3_A | heat | thermal | present | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q4-A-BUS | Q4_A | Q4_BUS | heat | thermal | present | water <80 C | 5.51 kW | — |
| HL-Q4-B-BUS | Q4_B | Q4_BUS | heat | thermal | present | water <80 C | 5.51 kW | — |
| HL-Q4-X | Q4_A | Q4_B | heat | thermal | present | cross-tie, hot to cold only | 1.565 kW | — |
| HL-Q4-X-BA | Q4_B | Q4_A | heat | thermal | present | cross-tie, hot to cold only | 1.565 kW | — |
| IA-BMED-01 | BMED_ACID | WS_NITRIC | L | mass | present | HCl product | 0.6456 kg/d | — |
| IA-BMED-02 | BMED_BASE | WS_KOH | L | mass | present | NaOH product | 0.27 kg/d | — |
| IA-BMED-03 | SALT_FEED | BMED_ACID | L | mass | present | salt-loop transfer to the BMED acid compartment (Cl- + product water) | 505.77 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | SALT_FEED | BMED_BASE | L | mass | present | salt-loop transfer to the BMED base compartment (Na+ + product water) | 528.78 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | present | Hydro turbine-pump electrical (MISSING on SLD) | 0.2917 kW | ess_layer,missing_on_sld |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | present | ZnBr2 charge (PV/RECT surplus) | 6.6667 kW | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | present | ZnBr2 discharge to bus | 5.0 kW | ess_layer |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW overflow | 4280.1 kg/d | — |
| IA-EW-02 | EW_2 | EW_3 | L | mass | present | EW overflow | 4276.17 kg/d | — |
| IA-EW-03 | EW_3 | EW_4 | L | mass | present | EW overflow | 4250.95 kg/d | — |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR to EW-1 | 4284.0 kg/d | — |
| IA-EW-05 | EW_5 | EW_6 | L | mass | present | EW overflow | 4240.81 kg/d | — |
| IA-EW-06 | EW_6 | EW_7 | L | mass | present | EW overflow | 4235.05 kg/d | — |
| IA-EW-07 | EW_7 | EW_8 | L | mass | present | EW overflow | 4150.83 kg/d | — |
| IA-EW-08 | EW_8 | EW_9 | L | mass | present | EW overflow | 4145.63 kg/d | — |
| IA-EW-09 | EW_9 | POLISH_BANK | L | mass | present | EW tail to polish | 4139.97 kg/d | — |
| IA-EW-10 | EW_4 | EW_5 | L | mass | present | EW overflow | 4245.99 kg/d | — |
| IA-GLASS-01 | GLASS_RINSE | GLASS_MILL | S | mass | present | rinsed cullet | 36.8182 kg/d | — |
| IA-GLASS-02 | GLASS_MILL | GLASS_BURNOUT | S | mass | present | milled cullet | 30.0 kg/d | — |
| IA-GLASS-03 | GLASS_BURNOUT | GLASS_DIGEST | S | mass | present | burned cullet | 30.0 kg/d | — |
| IA-HDR-H2-01 | EW_7 | HDR_H2 | G | mass | present | cathode-hood H2, water-saturated (Fe cell) | 0.7087 kg/d | wp_l1_topology,wp_l2_filled,ew_cascade_exploded |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 0.8536 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure,ew_cascade_exploded |
| IA-HDR-H2-03 | EW_3 | HDR_H2 | G | mass | present | cathode-hood H2, water-saturated (Cu cell) | 0.1303 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G | mass | present | cathode-hood H2, water-saturated (Zn cell) | 0.0145 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HX8 | EW_1 | HX8 | heat | thermal | present | EW heat | 4.572 kW | — |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | present | Dryer → pyro | 33.0 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | present | Pyro → frac | 28.9046 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | NCG_HEADER | G | mass | present | NCG only | 5.0 kg/d | — |
| IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | L | mass | present | raffinate (EW tail after polish) to continuous recycle | 3357.8 kg/d | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | continuous recycle liquor | 3903.78 kg/d | — |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | present | Float/sink liquor return | 343.1 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| NCG_TO_AB | NCG_HEADER | AFTERBURNER | G | mass | present | NCG | 5.0 kg/d | — |
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 77.2764 kg/d | — |
| S02 | CRYO_O2 | HABITATION | G | mass | present | O2 | 3.36 kg/d | — |
| S03 | CRYO_N2 | WAFER_FAB | G | mass | present | N2 | 1.4998 kg/d | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 1.109 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | 0.0 kW | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 22.1949 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 42.0 kg/d | — |
| S08G | GLASS_DIGEST | BOUNDARY_EXPORT | S | mass | present | glass/ceramic goods | 4.5 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S09 | BMED_ACID | WET_BENCH | L | mass | present | HCl | 9.2772 kg/d | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 78.3397 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | GREY_TREAT | L/S | mass | present | grey water + hab AHU condensate | 114.9 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | present | condensate | 29.9068 kg/d | absent_from_candidate_mvs |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 2.4 kg/d | — |
| S14X | GROW_BED | BOUNDARY_EXPORT | S | mass | present | food surplus export | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | 0.0 kg/d | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.6 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 13.4755 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | flue-carbon claim reference (no CO2 mass since Rev J) | 0.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | 0.75 kg/d | absent_from_candidate_mvs |
| S20 | SOL_ARK_60K | GROW_BED | E | elec | present | LED canopy load | 5.0 kW | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 120.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | 0.4088 kW | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | 0.4088 kW | — |
| S24 | H2_DRYER | RELIEF_H2 | G | mass | present | H2 relief contingency | 0.0 kg/d | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | present | VCD distillate | 150.28 kg/d | — |
| S26 | REMIN | HABITATION | L | mass | present | potable | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | 60.0 kg/d | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | VCD brine | 28.3179 kg/d | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | present | treated grey | 109.15 kg/d | absent_from_candidate_mvs |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | 22.1749 kg/d | absent_from_candidate_mvs |
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
| S46 | BACKUP_GEN | NOX_SCRUB | L/G | mass | present | exhaust condensate / NOx | 0.0 kg/d | — |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 0.0 kW | — |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 0.0 kg/d | — |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 0.0 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 0.0 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | present | PEM product H2O | 0.0 kg/d | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0 kW | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | 0.1001 kW | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | 4.0606 kW | absent_from_candidate_mvs |
| S56 | CRYO_AHU | RELIEF_CRYO | G | mass | present | non-condensable residual after KO | 0.0 kg/d | — |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | 4.3789 kg/d | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | 3.941 kg/d | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | 3.9529 kg/d | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | 3.1999 kg/d | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | 1.1971 kg/d | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | 2131.07 kg/h | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0171 kW | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 0.3221 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | 1562.91 kg/h | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | 0.3868 kg/d | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | FLUE_KO | G | mass | present | flue N2/O2/CO2/NOx | 242.48 kg/d | — |
| S67B | FLUE_KO | CRYO_CO2 | G | mass | present | CO2-rich gas after KO | 13.2209 kg/d | — |
| S68 | CRYO_AHU | LEACH_CSTR_1 | L | mass | present | CRYO AHU coil condensate (acid trace, flue-cap zone) | 173.67 kg/d | — |
| S69 | ZNBR2 | ZNBR2_BR2_REGEN | G | mass | present | Br2 vapor | 854.85 kg/d | — |
| S69B | ZNBR2_BR2_REGEN | ZNBR2 | L | mass | present | NaBr after ORP | 0.0473 kg/d | — |
| S70 | CRYO_AHU_COND_CONDENSABLE | FLUE_KO | L | mass | present | condensables | 0.0521 kg/d | — |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | 852.43 kg/h | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | metal fines and aqueous scrub liquor | 2.4366 kg/d | — |
| S72B | MET_SCRUB | OIL_FRAC | L | mass | present | organic mist | 0.0158 kg/d | — |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 2.3436 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 0.3221 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 1.7063 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | ess | present | MeOH fuel | 1.7209 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | 0.0146 kg/d | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | 0.36 kg/d | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 0.1007 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | 0.127 kW | absent_from_candidate_mvs |
| S81 | MEOH_FC | MEOH_COND | L | mass | present | MeOH FC condensate | 1.935 kg/d | — |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 2.3636 kg/d | — |
| S83 | CRYO_O2 | HDR_O2 | G | mass | present | O2 product | 4.3108 kg/d | — |
| S84 | CRYO_N2 | HDR_N2 | G | mass | present | N2 product | 0.0 kg/d | — |
| S85 | CRYO_CO2 | HDR_CO2 | G | mass | present | CO2 product after FLUE_KO | 12.0799 kg/d | — |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO3 | 0.665 kg/d | — |
| S34B | WS_PHOS | WET_BENCH | L | mass | present | H3PO4 | 0.625 kg/d | — |
| S89 | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment dose (FARM AHU supply) | 16.1009 kg/d | — |
| S90 | HABITATION | HDR_CO2 | G | mass | present | metabolic CO2 (desorbed from the HAB CO2 sorbent bed) | 4.021 kg/d | — |
| IA-BMED-05 | POLISH_BANK | SALT_FEED | L | mass | present | raffinate brine bleed (loop level control) | 782.18 kg/d | — |
| IA-BMED-06 | BMED_ACID | CONTINUOUS_RECYCLE | L | mass | present | BMED HCl 2 M (REGEN LEACH acid make-up) | 495.84 kg/d | — |
| IA-BMED-07 | BMED_BASE | ALK_SCRUBBER | L | mass | present | BMED NaOH 2 M to the alkaline Cl2 scrubber | 46.6852 kg/d | — |
| IA-BMED-08 | ALK_SCRUBBER | CRU | L | mass | present | hypochlorite / chloride scrub liquor | 49.7503 kg/d | — |
| IA-BMED-09 | CRU | CONTINUOUS_RECYCLE | L | mass | present | chlorate / chloride liquor (REGEN LEACH oxidant) | 50.1371 kg/d | — |
| IA-BMED-10 | BMED_BASE | SALT_FEED | L | mass | present | BMED NaOH 2 M for the pH-shift (metal hydroxide / silica drop) | 161.6 kg/d | — |
| S91 | BMED_BASE | GLASS_DIGEST | L | mass | present | BMED NaOH 2 M digest caustic | 320.76 kg/d | — |
| S92 | GLASS_DIGEST | SALT_FEED | L | mass | present | spent digest liquor (sodium silicate) | 325.96 kg/d | — |
| S93 | PV_ARRAY | SOL_ARK_60K | E | elec | present | PV DC (daily average) | 12.3858 kW | — |
| S94 | SOL_ARK_60K | LOAD_AGG | E | elec | present | AC loads aggregate (daily average) | 31.1339 kW | — |
| S95 | HDR_O2 | LEACH_CSTR_1 | G | mass | present | O2 sparge (leach oxidant make-up) | 4.3108 kg/d | — |
| S96 | GLASS_RINSE | BOUNDARY_EXPORT | S | mass | present | sink residue reject (inert, unleached metal and fillers) | 34.2915 kg/d | — |
| S97 | SALT_FEED | BOUNDARY_EXPORT | S | mass | present | pH-shift cake: precipitated silica, Al(OH)3, sodium aluminosilicate, metal hydroxides | 91.0768 kg/d | — |
| S98 | SALT_FEED | VCD_TRAIN | L | mass | present | BMED salt-loop diluate bleed | 144.12 kg/d | — |
| S99 | VCD_TRAIN | BOUNDARY_EXPORT | L | mass | present | distillate surplus (clean water export) | 104.58 kg/d | — |
| S100 | Q4_BUS | LEACH_CSTR_1 | E | thermal | present | Q4 water to HX-9 leach make-up preheater | 0.5322 kW | — |
| S101 | Q4_BUS | GLASS_DIGEST | E | thermal | present | Q4 water to HX-10 digest caustic preheater | 0.2822 kW | — |
| S102 | Q4_BUS | GEO_GHEX | E | thermal | present | Q4 surplus to borefield recharge | 0.6738 kW | — |
