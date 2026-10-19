# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev AC (`plant_flow_graph.json`)
Generated: 2026-10-19
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.
Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.

| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |
|---|---|---|---|---|---|---|---|---|
| C29_RECYCLE | PROD_C29 | C29_RECYCLE | L | mass | present | C29 heavy cut | 5.873266 kg/d | — |
| C29_TO_PYRO | C29_RECYCLE | OIL_PYRO | L | mass | present | C29 heavy cut | 5.873266 kg/d | — |
| CUT-1 | OIL_FRAC | PROD_C5_C10 | L | mass | present | fractionator cut | 7.424773 kg/d | — |
| CUT-2 | OIL_FRAC | PROD_C11_C18 | L | mass | present | fractionator cut | 9.918821 kg/d | — |
| CUT-3 | OIL_FRAC | PROD_C19_C28 | L | mass | present | fractionator cut | 6.165705 kg/d | — |
| CUT-4 | OIL_FRAC | PROD_C29 | L | mass | present | fractionator cut | 5.873266 kg/d | — |
| DOCK_EXPORT_TBD | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | placeholder | goods / cassettes / surplus freight (ID TBD) | 0.0 kg/d | no_S_id,do_not_invent_route_or_rate,high_severity_audit |
| HL-AFTERBURNER-Q1-A | AFTERBURNER | Q1_A | heat | thermal | study | Q1 flue, not Q4 | 1.383 kW | — |
| HL-AFTERBURNER-Q1-B | AFTERBURNER | Q1_B | heat | thermal | study | Q1 flue, not Q4 | 1.383 kW | — |
| HL-GLASS_BURNOUT-Q2-A | GLASS_BURNOUT | Q2_A | heat | thermal | study | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-GLASS_BURNOUT-Q2-B | GLASS_BURNOUT | Q2_B | heat | thermal | study | Q2 burnout, not Q4 | 0.928 kW | — |
| HL-HX8-Q3-A | HX8 | Q3_A | heat | mass | retired | HX-8 residual | — | — |
| HL-HX8-Q3-B | HX8 | Q3_B | heat | mass | retired | HX-8 residual | — | — |
| HL-Q1-A-DOWN | Q1_A | Q2_A | heat | thermal | study | downhill heat pipe | 1.133 kW | — |
| HL-Q1-B-DOWN | Q1_B | Q2_B | heat | thermal | study | downhill heat pipe | 1.133 kW | — |
| HL-Q1-X | Q1_A | Q1_B | heat | thermal | study | cross-tie, hot to cold only | 1.383 kW | — |
| HL-Q1-X-BA | Q1_B | Q1_A | heat | thermal | study | cross-tie, hot to cold only | 1.383 kW | — |
| HL-Q2-A-DOWN | Q2_A | Q3_A | heat | thermal | study | downhill heat pipe | 1.891 kW | — |
| HL-Q2-B-DOWN | Q2_B | Q3_B | heat | thermal | study | downhill heat pipe | 1.891 kW | — |
| HL-Q2-X | Q2_A | Q2_B | heat | thermal | study | cross-tie, hot to cold only | 2.027 kW | — |
| HL-Q2-X-BA | Q2_B | Q2_A | heat | thermal | study | cross-tie, hot to cold only | 2.027 kW | — |
| HL-Q3-A-DOWN | Q3_A | Q4_A | heat | thermal | study | downhill heat pipe | 0.0 kW | — |
| HL-Q3-B-DOWN | Q3_B | Q4_B | heat | thermal | study | downhill heat pipe | 0.0 kW | — |
| HL-Q3-X | Q3_A | Q3_B | heat | thermal | study | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q3-X-BA | Q3_B | Q3_A | heat | thermal | study | cross-tie, hot to cold only | 1.831 kW | — |
| HL-Q4-A-BUS | Q4_A | Q4_BUS | heat | thermal | study | water <80 C | 3.896 kW | — |
| HL-Q4-B-BUS | Q4_B | Q4_BUS | heat | thermal | study | water <80 C | 3.896 kW | — |
| HL-Q4-X | Q4_A | Q4_B | heat | thermal | study | cross-tie, hot to cold only | 1.565 kW | — |
| HL-Q4-X-BA | Q4_B | Q4_A | heat | thermal | study | cross-tie, hot to cold only | 1.565 kW | — |
| IA-BMED-01 | BMED_ACID | WS_NITRIC | L | mass | present | HCl product | 1.2456 kg/d | — |
| IA-BMED-02 | BMED_BASE | WS_KOH | L | mass | present | NaOH product | 0.2701 kg/d | — |
| IA-BMED-03 | LEACH_CSTR_1 | BMED_ACID | L | mass | present | CRU → BMED acid regen loop | 450.163884 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | LEACH_CSTR_1 | BMED_BASE | L | mass | present | CRU → BMED base regen loop | 500.1311 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | 0.0 kg/d | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | 0.0 kg/d | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | placeholder | Hydro turbine-pump electrical (MISSING on SLD) | 0.0 kW | ess_layer,missing_on_sld |
| IA-ESS-MEOH-CHG | MEOH_SYNTH | MEOH_TANK | L | mass,ess | placeholder | MeOH synth inventory = charge-analogue | — | ess_layer |
| IA-ESS-MEOH-DIS | MEOH_FC | SOL_ARK_60K | E | elec,ess | placeholder | MeOH FC discharge (peers S79) | — | ess_layer,overlaps_S79_architecture |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | present | ZnBr2 charge (PV/RECT surplus) | 6.6667 kW | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | present | ZnBr2 discharge to bus | 5.0 kW | ess_layer |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW overflow | 4139.222213 kg/d | — |
| IA-EW-02 | EW_2 | EW_3 | L | mass | present | EW overflow | 3990.594815 kg/d | — |
| IA-EW-03 | EW_3 | EW_4 | L | mass | present | EW overflow | 3934.805911 kg/d | — |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR to EW-1 | 4287.799997 kg/d | — |
| IA-EW-05 | EW_5 | EW_6 | L | mass | present | EW overflow | 3909.915497 kg/d | — |
| IA-EW-06 | EW_6 | EW_7 | L | mass | present | EW overflow | 3896.339738 kg/d | — |
| IA-EW-07 | EW_7 | EW_8 | L | mass | present | EW overflow | 3719.792521 kg/d | — |
| IA-EW-08 | EW_8 | EW_9 | L | mass | present | EW overflow | 3707.26014 kg/d | — |
| IA-EW-09 | EW_9 | POLISH_BANK | L | mass | present | EW tail to polish | 3520.31431 kg/d | — |
| IA-EW-10 | EW_4 | EW_5 | L | mass | present | EW overflow | 3922.373456 kg/d | — |
| IA-GLASS-01 | GLASS_RINSE | GLASS_MILL | S | mass | present | rinsed cullet | 36.82 kg/d | — |
| IA-GLASS-02 | GLASS_MILL | GLASS_BURNOUT | S | mass | present | milled cullet | 30.0 kg/d | — |
| IA-GLASS-03 | GLASS_BURNOUT | GLASS_DIGEST | S | mass | present | burned cullet | 30.0 kg/d | — |
| IA-HDR-H2-01 | EW_1 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 0.382615 kg/d | wp_l1_topology,wp_l2_filled,ew_cascade_exploded |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 1.975396 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure,ew_cascade_exploded |
| IA-HDR-H2-03 | EW_2 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 0.382743 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 0.481422 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HX8 | EW_1 | HX8 | heat | thermal | present | EW heat | 4.572 kW | — |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | present | Dryer → pyro | 33.0 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | present | Pyro → frac | 33.373266 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | NCG_HEADER | G | mass | present | NCG only | 5.0 kg/d | — |
| IA-POL-01 | POLISH_BANK | BMED_UPW_POLISH | L | mass | placeholder | Polish bank → UPW polish | — | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | L | mass | present | Polish bank liquor return to the continuous recycle | 3302.944317 kg/d | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | continuous recycle liquor | 3302.944317 kg/d | — |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | present | Float/sink liquor return | 343.1 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| NCG_TO_AB | NCG_HEADER | AFTERBURNER | G | mass | present | NCG | 5.0 kg/d | — |
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 67.300214 kg/d | — |
| S02 | CRYO_O2 | HABITATION | G | mass | present | O2 | 3.4 kg/d | — |
| S03 | CRYO_N2 | WAFER_FAB | G | mass | present | N2 | 1.499799 kg/d | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 0.0 kg/d | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 41.996408 kg/d | — |
| S08G | GLASS_DIGEST | MFG_SHOP | S | mass | present | glass/ceramic goods | 26.7 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S09 | BMED_ACID | WET_BENCH | L | mass | present | HCl | 9.277184 kg/d | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 79.115777 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | GREY_TREAT | L/S | mass | present | grey/solids | 319.60396 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | present | condensate | 3.799494 kg/d | absent_from_candidate_mvs |
| S14 | GROW_BED | FOOD_STORE | S | mass | present | food | 4.2 kg/d | — |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | 0.0 kg/d | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.299499 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 12.0 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | captured CO2/air | 0.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | 0.0 kg/d | absent_from_candidate_mvs |
| S20 | SOL_ARK_60K | GROW_BED | E | elec | present | load | 2.0463 kW | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 120.68 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | 0.0 kg/d | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | 0.0 kg/d | — |
| S24 | H2_DRYER | RELIEF_H2 | G | mass | present | H2 relief contingency | 0.0 kg/d | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | present | VCD distillate | 308.578609 kg/d | — |
| S26 | REMIN | HABITATION | L | mass | present | potable | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | 60.000181 kg/d | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | VCD brine | 17.877059 kg/d | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | present | treated grey | 104.499999 kg/d | absent_from_candidate_mvs |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | — | absent_from_candidate_mvs |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | 1.5 kg/d | absent_from_candidate_mvs |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | 3.0 kg/d | absent_from_candidate_mvs |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | 3.008739 kg/d | absent_from_candidate_mvs |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | 0.2701 kg/d | absent_from_candidate_mvs |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | 0.0 kg/d | absent_from_candidate_mvs |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | 3.3 kg/d | absent_from_candidate_mvs |
| S38 | WET_BENCH | OIL_FRAC | L | mass | present | resist and solvent waste | 0.006 kg/d | — |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry and etch liquor | 3.310001 kg/d | — |
| S39B | WAFER_FAB | OIL_FRAC | L | mass | present | solvent and photoresist | 0.0 kg/d | — |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | 0.0 kW | absent_from_candidate_mvs |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | 2.1952 kW | absent_from_candidate_mvs |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | H2 fuel | 0.0 kg/d | — |
| S46 | BACKUP_GEN | NOX_SCRUB | L/G | mass | present | exhaust condensate / NOx | 0.267975 kg/d | — |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 0.008219 kW | — |
| S48 | GEO_ORC | SOL_ARK_60K | E | elec | placeholder | ORC AC | — | orc_stub_kw_tbd |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 4.8 kg/d | — |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 4.0 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | present | PEM product H2O | 42.876623 kg/d | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | 1.1419 kW | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | 0.5448 kW | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | 4.2838 kW | absent_from_candidate_mvs |
| S56 | CRYO_AHU | RELIEF_CRYO | G | mass | present | non-condensable residual after KO | 0.0 kg/d | — |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | 6.8389 kg/d | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | 3.9389 kg/d | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | 3.950359 kg/d | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | 3.200359 kg/d | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | 1.197099 kg/d | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | 51145.68 kg/d | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0171 kW | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 1.975396 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | 37509.8546 kg/d | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | 27.372033 kg/d | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | FLUE_KO | G | mass | present | flue N2/O2/CO2/NOx | 117.42759 kg/d | — |
| S67B | FLUE_KO | CRYO_CO2 | G | mass | present | CO2-rich gas after KO | 14.050492 kg/d | — |
| S68 | CRYO_AHU | LEACH_CSTR_1 | L | mass | present | flue condensate | 78.987901 kg/d | — |
| S69 | ZNBR2 | ZNBR2_BR2_REGEN | G | mass | present | Br2 vapor | 1093.561663 kg/d | — |
| S69B | ZNBR2_BR2_REGEN | ZNBR2 | L | mass | present | NaBr after ORP | 1093.561663 kg/d | — |
| S70 | CRYO_AHU_COND_CONDENSABLE | FLUE_KO | L | mass | present | condensables | 0.0521 kg/d | — |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | 20458.32 kg/d | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | metal fines and aqueous scrub liquor | 2.4442 kg/d | — |
| S72B | MET_SCRUB | OIL_FRAC | L | mass | present | organic mist | 0.0158 kg/d | — |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 44.423559 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 6.536155 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 34.6293 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | mass,ess | present | MeOH fuel | 5.0 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | 0.0146 kg/d | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | 0.36 kg/d | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 1.0 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | 0.3689 kW | absent_from_candidate_mvs |
| S81 | MEOH_FC | MEOH_COND | L | mass | present | MeOH FC condensate | 7.251023 kg/d | — |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 8.625641 kg/d | absent_from_candidate_mvs |
| S83 | CRYO_O2 | HDR_O2 | G | mass | present | O2 product | 33.195596 kg/d | — |
| S84 | CRYO_N2 | AIR_RECEIVER | G | mass | present | N2 product | 191.989014 kg/d | — |
| S85 | CRYO_CO2 | HDR_CO2 | G | mass | present | CO2 product after FLUE_KO | 0.0 kg/d | — |
| S86 | CRYO_AHU | RELIEF_CRYO | G | mass | present | cryo residual contingency | 0.0 kg/d | — |
| S87 | GROW_BED | CRYO_O2 | G | mass | present | surplus O2 capture | 0.641572 kg/d | — |
| S88 | CRYO_N2 | GROW_BED | G | mass | present | N2 make-up | 0.0 kg/d | — |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO3 | 1.2456 kg/d | — |
| S34B | WS_PHOS | WET_BENCH | L | mass | present | H3PO4 | 0.61 kg/d | — |
| F_RECOVER_TO_HF_GEN | F_RECOVER | HF_GEN | L | mass | present | fluoride concentrate | 0.0 kg/d | — |
| HF_GEN_TO_VDF | HF_GEN | VDF_SYN | L | mass | present | aqueous HF | 0.0 kg/d | — |
| HF_GEN_TO_TFE | HF_GEN | TFE_SYN | L | mass | present | aqueous HF | 0.0 kg/d | — |
| VDF_TO_POLY_F | VDF_SYN | POLY_F | L | mass | present | VDF monomer | 0.0 kg/d | — |
| TFE_TO_POLY_F | TFE_SYN | POLY_F | L | mass | present | TFE monomer | 0.0 kg/d | — |
| TI_CELL_SLAG_RETURN | TI_CELL | LEACH_CSTR_1 | S | mass | present | slag / residual grit | 0.0 kg/d | — |
| MO_CELL_RAFFINATE | MO_CELL | POLISH_BANK | L | mass | present | raffinate after Mo cut | 0.0 kg/d | — |
| FLOAT_SINK_GRIT_TO_TI | FLOAT_SINK | TI_CELL | S | mass | present | dense grit (ilmenite/rutile fraction) | 0.0 kg/d | — |
| EW9_LIQUOR_TO_MO | EW_9 | MO_CELL | L | mass | present | post-EW liquor for Mo cut | 0.0 kg/d | — |
| TI_CELL_CL2_TO_CRU | TI_CELL | CRU | G | mass | present | chlorine from Kroll chlorinator / Mg recycle | 0.0 kg/d | — |
| MO_CELL_ANODE_GAS_TO_CRU | MO_CELL | CRU | G | mass | present | anode gas (Cl2 or O2) from molten-salt pot | 0.0 kg/d | — |
| IND_MELT_TO_CAST | IND_MELT | CAST_LINE | L | mass | present | molten metal | 3.0 kg/d | — |
| CAST_SCRAP_TO_IND | CAST_LINE | IND_MELT | S | mass | present | foundry scrap | 0.0 kg/d | — |
| METALS_TO_IND_MELT | TI_CELL | IND_MELT | S | mass | present | Ti and other metal powders/sponge | 0.0 kg/d | — |
| VAC_IND_TO_VAC_CAST | VAC_IND | VAC_CAST | L | mass | present | vacuum melt to cast | 0.0 kg/d | — |
| CAST_TO_ROLL | CAST_LINE | ROLL | S | mass | present | billet to roll | 3.0 kg/d | — |
| CAST_TO_EXTRUDE | CAST_LINE | EXTRUDE | S | mass | present | billet to extrude | 0.0 kg/d | — |
| ROLL_TO_STOCK | ROLL | STOCK_OUT | S | mass | present | plate/sheet | 13.0 kg/d | — |
| EXTRUDE_TO_STOCK | EXTRUDE | STOCK_OUT | S | mass | present | rod/profile | 0.0 kg/d | — |
| DRAW_TO_STOCK | DRAW | STOCK_OUT | S | mass | present | wire | 0.0 kg/d | — |
| SINTER_TO_STOCK | SINTER | STOCK_OUT | S | mass | present | sintered stock | 0.0 kg/d | — |
| FLUX_TO_IND | FLUX_PREP | IND_MELT | S | mass | present | flux | 0.0 kg/d | — |
| EW_METALS_TO_IND | EW_9 | IND_MELT | S | mass | present | EW cathode/powder metals | 0.0 kg/d | — |
| MO_TO_IND | MO_CELL | IND_MELT | S | mass | present | Mo metal | 0.0 kg/d | — |
| CR_TO_IND | CR_CELL | IND_MELT | S | mass | present | Cr metal | 0.0 kg/d | — |
| IND_TO_CONT | IND_MELT | CONT_CAST | L | mass | present | melt to continuous caster | 11.0 kg/d | — |
| CONT_TO_ROLL | CONT_CAST | ROLL | S | mass | present | continuous billet/slab | 10.0 kg/d | — |
| CONT_TO_STOCK | CONT_CAST | STOCK_OUT | S | mass | present | as-cast stock | 1.0 kg/d | — |
| VAC_IND_TI | TI_CELL | VAC_IND | S | mass | present | Ti sponge/powder to vacuum melt | 0.0 kg/d | — |
| STOCK_TO_MFG | METAL_STORE | MFG_SHOP | S | mass | present | plate/rod/wire to manufacturing | 14.0 kg/d | — |
| STOCK_TO_FAB | METAL_STORE | WAFER_FAB | S | mass | present | specialty stock to fab | 0.0 kg/d | — |
| FOUNDRY_SLAG_TO_LEACH | IND_MELT | LEACH_CSTR_1 | S | mass | present | slag return | 0.141414 kg/d | — |
| SALT_TO_FLUX | SALT_FEED | FLUX_PREP | S | mass | present | digester/leach salts to flux | 0.0 kg/d | — |
| AL_POT_TO_IND | AL_POT | IND_MELT | S | mass | present | Al metal | 0.0 kg/d | — |
| MG_POT_TO_IND | MG_POT | IND_MELT | S | mass | present | Mg metal | 0.0 kg/d | — |
| CA_POT_TO_IND | CA_POT | IND_MELT | S | mass | present | Ca metal | 0.0 kg/d | — |
| AL_POT_CL2 | AL_POT | CRU | G | mass,energy | present | Cl2 return | 0.0 kg/d | — |
| MG_POT_CL2 | MG_POT | CRU | G | mass,energy | present | Cl2 return | 0.0 kg/d | — |
| IND_HEAT_TO_HX | IND_MELT | MET_HX_Q4 | E | thermal | present | furnace coil + shell cooling water 40-60 C | 1.063 kW | — |
| VAC_HEAT_TO_HX | VAC_IND | MET_HX_Q4 | E | thermal | present | furnace coil + shell cooling water 40-60 C | 0.638 kW | — |
| COMB_OFFGAS | COMB_HEAT | MET_SCRUB | G | mass,energy | present | combustion off-gas when alternate used | 0.0 kg/d | — |
| STOCK_TO_WIRE_DRAW | METAL_STORE | WIRE_DRAW | S | mass | present | rod/wire for final sizing | 0.0 kg/d | — |
| IND_TO_ATOM | IND_MELT | GAS_ATOMIZER | L | mass | present | melt to atomizer when powder required | 0.0 kg/d | — |
| ATOM_TO_STOCK | GAS_ATOMIZER | STOCK_OUT | S | mass | present | powder stock | 0.0 kg/d | — |
| WAX_TO_SHELL | WAX_PATTERN | SHELL_BUILD | S | mass | present | wax pattern | 0.0 kg/d | — |
| SHELL_TO_BURNOUT | SHELL_BUILD | SHELL_BURNOUT | S | mass | present | green shell | 0.0 kg/d | — |
| BURNOUT_TO_CAST | SHELL_BURNOUT | INV_CAST | S | mass | present | fired shell | 0.0 kg/d | — |
| IND_TO_INV | IND_MELT | INV_CAST | L | mass | present | melt for investment pour | 0.0 kg/d | — |
| VAC_TO_INV | VAC_IND | INV_CAST | L | mass | present | reactive melt for investment pour | 0.0 kg/d | — |
| INV_TO_BREAK | INV_CAST | SHELL_BREAK | S | mass | present | cast + shell | 0.0 kg/d | — |
| BREAK_TO_STOCK | SHELL_BREAK | STOCK_OUT | S | mass | present | investment casting | 0.0 kg/d | — |
| SHELL_TO_GLASS | SHELL_BREAK | GLASS_MILL | S | mass | present | spent ceramic shell to solids line | 0.0 kg/d | — |
| GLASS_MILL_TO_DIGEST | GLASS_MILL | GLASS_DIGEST | S | mass | present | milled shell into digest | — | — |
| MFG_SCRAP_TO_IND | MFG_SHOP | IND_MELT | S | mass | present | manufacturing scrap return | 14.141414 kg/d | — |
| WAX_RECLAIM_TO_PATTERN | SHELL_BURNOUT | WAX_PATTERN | L | mass | present | wax condensate reclaim | 0.0 kg/d | — |
| WAX_TO_OIL | SHELL_BURNOUT | OIL_FRAC | L | mass | present | unrecovered wax to oil line | 0.0 kg/d | — |
| OIL_TO_OLEFIN | OIL_FRAC | POLY_OLEFIN | L | mass | present | light cuts to polyolefin | 0.0 kg/d | — |
| MEOH_TO_OLEFIN | MEOH_SYNTH | POLY_OLEFIN | L | mass | present | methanol co-feed | 0.0 kg/d | — |
| DIGEST_TO_POLY | BLACK_DIGEST | POLY_COND | L | mass | present | digester organics | 0.0 kg/d | — |
| OLEFIN_TO_PELLET | POLY_OLEFIN | PELLET | S | mass | present | polyolefin resin | 0.414905 kg/d | — |
| POLYF_TO_PELLET | POLY_F | PELLET | S | mass | present | PVDF/PTFE resin | 0.0 kg/d | — |
| POLYF_TO_POWDER | POLY_F | POWDER_RESIN | S | mass | present | fluoropolymer powder | 0.0 kg/d | — |
| PELLET_TO_STOCK | PELLET | POLY_STOCK | S | mass | present | pellet stock | 0.414905 kg/d | — |
| POWDER_TO_STOCK | POWDER_RESIN | POLY_STOCK | S | mass | present | powder stock | 0.0 kg/d | — |
| FILM_TO_STOCK | FILM_CAST | POLY_STOCK | S | mass | present | film stock | 0.0 kg/d | — |
| POLY_TO_MFG | POLY_STOCK | MFG_SHOP | S | mass | present | polymer feedstock to manufacturing | 0.377186 kg/d | — |
| POLY_TO_FAB | POLY_STOCK | WAFER_FAB | S | mass | present | polymer feedstock to fab | 0.0 kg/d | — |
| POLY_TO_WET | POLY_STOCK | LEACH_CSTR_1 | S | mass | present | lining/gasket stock return path | 0.037719 kg/d | — |
| CRU_TO_VDF | CRU | VDF_SYN | G | mass | present | chlorine | 0.0 kg/d | — |
| CRU_TO_TFE | CRU | TFE_SYN | G | mass | present | chlorine | 0.0 kg/d | — |
| POLISH_TO_LI | POLISH_BANK | LI_RECOVER | L | mass | present | Li-bearing polish liquor | — | — |
| WAX_TO_GREASE_CA | PROD_C19_C28 | GREASE_CA | L | mass | present | wax cut | — | — |
| WAX_TO_GREASE_LI | PROD_C19_C28 | GREASE_LI | L | mass | present | wax cut | — | — |
| PCA_TO_GREASE | P_CA | GREASE_CA | S | mass | present | calcium hydroxide | — | — |
| LI_TO_GREASE | LI_RECOVER | GREASE_LI | S | mass | present | lithium hydroxide or carbonate | — | — |
| GREASE_CA_TO_MFG | GREASE_CA | MFG_SHOP | S | mass | present | Ca grease | — | — |
| GREASE_LI_TO_MFG | GREASE_LI | MFG_SHOP | S | mass | present | Li grease | — | — |
| CHAR_TO_SI | OIL_PYRO | SI_REDUCE | S | mass | present | pyro char | — | — |
| CO2_TO_FARM | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment | 0.0 kg/d | — |
| FARM_O2_TO_HAB | GROW_BED | HABITATION | G | mass | present | farm O2 | 0.0 kg/d | — |
| HAB_CO2_TO_HDR | HABITATION | HDR_CO2 | G | mass | present | habitation CO2 | — | — |
| HAB_GREY | HABITATION | GREY_TREAT | L | mass | present | grey water | — | — |
| HAB_BLACK | HABITATION | BLACK_DIGEST | L | mass | present | black water | — | — |
| NUT_TO_BED | NUTRIENT_DOSE | GROW_BED | L | mass | present | nutrient solution | 0.0 kg/d | — |
| UPW_TO_FAB | HDR_UPW | FAB_UPW_TANK | L | mass | present | UPW | — | — |
| HL-HX8-Q4-A | HX8 | Q4_A | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 2.286 kW | — |
| HL-HX8-Q4-B | HX8 | Q4_B | heat | thermal | present | HX-8 EW reject, Q4 return preheat | 2.286 kW | — |
| HL-Q3-A-HX4 | Q3_A | OIL_DRYER | heat | thermal | present | HX-4 Q3 process heat (dryer jacket) | 0.0553 kW | — |
| HL-Q3-A-HX5 | Q3_A | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 1.4548 kW | — |
| HL-Q3-A-HX6 | Q3_A | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 0.3809 kW | — |
| HL-Q3-B-HX4 | Q3_B | OIL_DRYER | heat | thermal | present | HX-4 Q3 process heat (dryer jacket) | 0.0553 kW | — |
| HL-Q3-B-HX5 | Q3_B | LEACH_CSTR_1 | heat | thermal | present | HX-5 Q3 process heat (leach CSTR jacket) | 1.4548 kW | — |
| HL-Q3-B-HX6 | Q3_B | GLASS_DIGEST | heat | thermal | present | HX-6 Q3 process heat (NaOH digest jacket) | 0.3809 kW | — |
| IA-ESS-ZNBR2-SRC | PV_ARRAY | SOL_ARK_60K | E | ess | present | PV share of the zinc-bromine round-trip loss | 1.6667 kW | ess_layer |
| S89 | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment dose (FARM AHU supply) | 0.882362 kg/d | — |
| S90 | HABITATION | HDR_CO2 | G | mass | present | metabolic CO2 (desorbed from the HAB CO2 sorbent bed) | 4.021 kg/d | — |
| IA-GREY-01 | GREY_TREAT | LEACH_CSTR_1 | S/L | mass | present | grey sludge | 244.641602 kg/d | — |
| IA-CRU-01 | CRU | LEACH_CSTR_1 | L | mass | present | sodium chlorate liquor | 27.372033 kg/d | — |
| HL-Q4-REJ | Q4_BUS | DRY_COOLER | thermal | thermal | present | Q4 surplus heat | 0.0 kW | — |
| IA-PV-01 | PV_ARRAY | SOL_ARK_60K | electric | elec | present | PV daily average | 405.4928 kW | — |
| IA-ZNBR-BD | ZNBR2 | GREY_TREAT | L | mass | present | electrolyte bleed | 8.486841 kg/d | — |
| IA-NUT-01 | NUTRIENT_DOSE | VCD_TRAIN | L | mass | present | digest surplus | 13.930007 kg/d | — |
| IA-UPW-FAB | BMED_UPW_POLISH | FAB_UPW_TANK | L | mass | present | fab UPW | 60.000181 kg/d | — |
| IA-UPW-REMIN | BMED_UPW_POLISH | REMIN | L | mass | present | remineralizer | 175.233209 kg/d | — |
| IA-UPW-REJ | BMED_UPW_POLISH | LEACH_CSTR_1 | L | mass | present | polish reject | 6.045005 kg/d | — |
| IA-Q4-LIFE | Q4_BUS | HABITATION | thermal | thermal | present | life heat | 3.0 kW | — |
| IA-AB-FLUE | AFTERBURNER | AFTERBURNER_FLUE | G | mass | present | flue | 7.096878 kg/d | — |
| IA-ZNBR-MU | LEACH_CSTR_1 | ZNBR2 | L | mass | present | electrolyte water make-up | 8.486482 kg/d | — |
| IA-EW-MET-1 | EW_1 | MFG_SHOP | S | mass | present | plated sheet | 59.869999 kg/d | — |
| IA-EW-MET-2 | EW_2 | MFG_SHOP | S | mass | present | plated sheet | 59.889999 kg/d | — |
| IA-EW-MET-3 | EW_3 | MFG_SHOP | S | mass | present | plated sheet | 22.480359 kg/d | — |
| IA-EW-MET-4 | EW_4 | MFG_SHOP | S | mass | present | plated sheet | 4.85 kg/d | — |
| IA-EW-MET-5 | EW_5 | MFG_SHOP | S | mass | present | plated sheet | 5.020359 kg/d | — |
| IA-EW-MET-6 | EW_6 | MFG_SHOP | S | mass | present | plated sheet | 5.470359 kg/d | — |
| IA-EW-MET-7 | EW_7 | MFG_SHOP | S | mass | present | plated sheet | 71.139999 kg/d | — |
| IA-EW-MET-8 | EW_8 | MFG_SHOP | S | mass | present | plated sheet | 5.050359 kg/d | — |
| IA-EW-MET-9 | EW_9 | MFG_SHOP | S | mass | present | plated sheet | 61.341099 kg/d | — |
| IA-POL-CAKE | POLISH_BANK | MFG_SHOP | S | mass | present | recovered cake | 217.369993 kg/d | — |
| IA-AB-AIR | HDR_N2 | AFTERBURNER_FLUE | G | mass | present | combustion air | 110.330712 kg/d | — |
| IA-FLUE-EXH | FLUE_KO | NOX_SCRUB | G | mass | present | flue to the NOx scrubber | 263.641098 kg/d | — |
| IA-DIG-LIQ | GLASS_DIGEST | LEACH_CSTR_1 | L | mass | present | silicate liquor | 21.968 kg/d | — |
| IA-MILL-LOSS | GLASS_MILL | BAGHOUSE | S | mass | present | mill dust | 6.82 kg/d | — |
| IA-MFG-OUT | MFG_SHOP | HABITATION | S | mass | present | goods in service | 596.862802 kg/d | — |
| IA-BED-H2O | ROOF_TANK | GROW_BED | L | mass | present | irrigation | 42.138417 kg/d | — |
| IA-MEOH-H2O | MEOH_SYNTH | MEOH_COND | L | mass | present | synthesis water | 19.469052 kg/d | — |
| IA-FC-AIR | HDR_O2 | MEOH_FC | G | mass | present | cell air | 9.407064 kg/d | — |
| IA-LEACH-BD | LEACH_CSTR_1 | NUTRIENT_DOSE | L | mass | present | bleed salts to nutrient | 109.63 kg/d | — |
| IA-VCD-BD | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | still bottoms | 6.709424 kg/d | — |
| IA-CHAR | OIL_PYRO | MFG_SHOP | S | mass | present | char reductant | 5.5 kg/d | — |
| IA-FC-EXH | MEOH_FC | NOX_SCRUB | G | mass | present | cell exhaust | 0 kg/d | — |
| IA-ZNBR-HEAT | ZNBR2 | Q4_BUS | thermal | thermal | present | round-trip loss | 1.67 kW | — |
| IA-Q4A-TRIM | RECTIFIER | Q4_A | electric | thermal | present | store trim | 1.61 kW | — |
| IA-Q4B-TRIM | RECTIFIER | Q4_B | electric | thermal | present | store trim | 1.61 kW | — |
| IA-FAB-LOSS | WAFER_FAB | BAGHOUSE | S | mass | present | kerf | 0.51 kg/d | — |
| IA-WIRE-LOSS | WIRE_DRAW | BAGHOUSE | S | mass | present | draw scrap | 0.44 kg/d | — |
| IA-Q1A-LOSS | Q1_A | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.25 kW | — |
| IA-Q1B-LOSS | Q1_B | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.25 kW | — |
| IA-Q2A-LOSS | Q2_A | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.17 kW | — |
| IA-Q2B-LOSS | Q2_B | BOUNDARY_EXPORT | thermal | thermal | present | store loss | 0.17 kW | — |
| IA-BED-VAP | GROW_BED | CRYO_AHU | G | mass | present | bed transpiration | 67.443215 kg/d | — |
| IA-HAB-VAP | HABITATION | CRYO_AHU | G | mass | present | respired and evaporated water | 0.0 kg/d | — |
| IA-HVAC-COND | CRYO_AHU | ROOF_TANK | L | mass | present | AHU condensate to the water cycle | 67.443215 kg/d | — |
| IA-PV-CURTAIL | SOL_ARK_60K | BOUNDARY_EXPORT | electric | elec | present | bus surplus | 4.645 kW | — |
| IA-AHU-AIR | HDR_N2 | CRYO_AHU | G | mass | present | outdoor air moisture | 79.040001 kg/d | — |
| IA-ZNBR-LOSS | ZNBR2 | BOUNDARY_EXPORT | electric | elec,ess | present | round-trip loss | 1.67 kW | — |
| IA-GREY-RET | GREY_TREAT | ROOF_TANK | L | mass | present | treated grey to the water cycle | 0.0 kg/d | — |
| IA-NUT-LEACH | NUTRIENT_DOSE | LEACH_CSTR_1 | L | mass | present | nutrient surplus | 82.317318 kg/d | — |
| IA-FEED-01 | HOPPER | LEACH_CSTR_1 | L | mass | present | plant feedstock, any class | 102.680001 kg/d | — |
| IA-POT-01 | REMIN | ROOF_TANK | L | mass | present | potable makeup, remineralised | 165.23317 kg/d | — |
| IA-UPW-HAB | HDR_UPW | HABITATION | S/L | mass | present | potable makeup | 0.800001 kg/d | — |
| IA-BAG-01 | BAGHOUSE | LEACH_CSTR_1 | S/L | mass | present | captured dust | 7.77 kg/d | — |
| IA-UPW-USE | HDR_UPW | WAFER_FAB | S/L | mass | present | fab UPW | 66.500213 kg/d | — |
| IA-MEOH-REST | MEOH_TANK | MEOH_FC | S/L | mass | present | tank draw | 1.28 kg/d | — |
| IA-SINK-01 | LEACH_CSTR_1 | FLOAT_SINK | S/L | mass | present | sink solids | 376.1 kg/d | — |
| IA-PLAST-01 | FLOAT_SINK | OIL_DRYER | S/L | mass | present | float plastics | 33.0 kg/d | — |
| IA-CULLET | LEACH_CSTR_1 | GLASS_RINSE | S/L | mass | present | cullet | 36.82 kg/d | — |
| IA-SCRUB-SRC | LEACH_CSTR_1 | ACID_POLISH_SCRUB | S/L | mass | present | scrub feed | 27.342833 kg/d | — |
| IA-SIL-SRC | GLASS_DIGEST | WS_SLURRY | S/L | mass | present | silicate to slurry | 3.3 kg/d | — |
| IA-HF-SRC | LEACH_CSTR_1 | WS_HF_ED | S/L | mass | present | fluoride to HF | 1.5 kg/d | — |
| IA-NH3-SRC | HDR_N2 | WS_AMMONIA | S/L | mass | present | nitrogen to ammonia | 3.008739 kg/d | — |
| IA-H2O2-SRC | HDR_O2 | WS_PEROX | S/L | mass | present | oxygen to peroxide | 0.176 kg/d | — |
| IA-NOX-H2O | NOX_SCRUB | ROOF_TANK | S/L | mass | present | scrubber condensate | 221.48381 kg/d | — |
| IA-NOX-N | NOX_SCRUB | NUTRIENT_DOSE | S/L | mass | present | nitrate liquor | 20.047016 kg/d | — |
| IA-FAB-SPENT | WAFER_FAB | LEACH_CSTR_1 | L | mass | present | spent UPW | 66.502511 kg/d | — |
| IA-GEN-AIR | HDR_N2 | BACKUP_GEN | L | mass | present | genset air | 0.006137 kg/d | — |
| IA-NOX-HAB | ROOF_TANK | HABITATION | L | mass | present | scrubber water | 207.279999 kg/d | — |
| IA-NUT-BED | NUTRIENT_DOSE | GROW_BED | L | mass | present | nitrate and bleed salts | 31.363502 kg/d | — |
| IA-N2-VENT | CRYO_N2 | NORTH_DOCK | G | mass | present | nitrogen vent | 3.099779 kg/d | — |
| IA-HOP-01 | HOPPER | LEACH_CSTR_1 | S | mass | present | returned scrap | 530.73594 kg/d | — |
| IA-WEAR | HABITATION | HOPPER | S | mass | present | worn goods | 596.863842 kg/d | — |
| IA-MEOH-COND | MEOH_COND | ROOF_TANK | S | mass | present | methanol condensate | 26.720075 kg/d | — |
| IA-H2-IN | H2_DRYER | HDR_H2 | S | mass | present | dried hydrogen | 0.0 kg/d | — |
| IA-EW-SHEET | EW_9 | MET_MELT | S | mass | present | cathode sheet | 13.9889 kg/d | — |
| IA-PHOS-SRC | LEACH_CSTR_1 | WS_PHOS | S | mass | present | phosphate | 0.62 kg/d | — |
| IA-MELT-MILL | MET_MELT | COLD_MILL | S | mass | present | melt to the mill | 3.949641 kg/d | — |
| IA-MELT-ATOM | MET_MELT | GAS_ATOMIZER | S | mass | present | melt to the atomizer | 3.555954 kg/d | — |
| IA-DRAW-FUME | WIRE_DRAW | MET_SCRUB | S | mass | present | draw fume | 2.46 kg/d | — |
| IA-AHU-POT | CRYO_AHU | CRYO_AHU_COND_CONDENSABLE | S | mass | present | condensable slip | 0.052101 kg/d | — |
| IA-LEACH-NOX | LEACH_CSTR_1 | NOX_SCRUB | S/L | mass | present | leach offgas | 195.024701 kg/d | — |
| IA-LEACH-FLUE | LEACH_CSTR_1 | FLUE_KO | S/L | mass | present | leach vent | 135.9019 kg/d | — |
| IA-LEACH-HOP | LEACH_CSTR_1 | HOPPER | S/L | mass | present | returned solids | 35.355 kg/d | — |
| IA-EW1-H2 | EW_1 | HDR_H2 | S/L | mass | present | hood hydrogen | 0.0 kg/d | — |
| IA-EW2-H2 | EW_2 | HDR_H2 | S/L | mass | present | hood hydrogen | 0.0 kg/d | — |
| IA-EW4-H2 | EW_4 | HDR_H2 | S/L | mass | present | hood hydrogen | 0.030994 kg/d | — |
| IA-EW4-N2 | EW_4 | HDR_N2 | S/L | mass | present | sweep nitrogen | 0.396575 kg/d | — |
| IA-O2-MAKE | CRYO_O2 | HDR_O2 | S/L | mass | present | oxygen makeup | 0.0 kg/d | — |
| IA-FC-FIX | FUEL_CELL | NOX_SCRUB | S/L | mass | present | cell water | 0.0 kg/d | — |
| IA-AHU-FIX | CRYO_N2 | CRYO_AHU | S/L | mass | present | handler makeup | 1e-06 kg/d | — |
| IA-LEACH-H2 | LEACH_CSTR_1 | HDR_H2 | S/L | mass | present | dissolved hydrogen | 0.0 kg/d | — |
| IA-FC-LEACH | FUEL_CELL | LEACH_CSTR_1 | L | mass | present | cell water | 0.323377 kg/d | — |
| IA-PHOS-DOPE | WS_PHOS | WS_DOPE | L | mass | present | phosphate to dopant | 0.01 kg/d | — |
| IA-SOLV-WB | WS_SOLV | WET_BENCH | L | mass | present | ethanol and acetone | 0.209973 kg/d | — |
| IA-CLOSE-1 | LEACH_CSTR_1 | NOX_SCRUB | S/L | mass | present | leach vent to the NOx scrubber | 1.0 kg/d | — |
| IA-CLOSE-10 | LEACH_CSTR_1 | MEOH_FC | S/L | mass | present | leach condensate to the methanol cell | 0.1896 kg/d | — |
| IA-LITHO-IN | WAFER_FAB | LITHO_STUB | S | mass | present | spent resist and solvent | 0.987499 kg/d | — |
| IA-LITHO-OUT | LITHO_STUB | OIL_FRAC | S | mass | present | spent resist and solvent | 0.987499 kg/d | — |
| IA-BLOW-IN | PROD_C11_C18 | BLOW_MOLD | S | mass | present | C11-C18 to the mold | 8.407159 kg/d | — |
| IA-BLOW-OUT | BLOW_MOLD | MFG_SHOP | S | mass | present | blown parts | 8.407518 kg/d | — |
| IA-COAT-IN | EW_1 | ELECTRODE_COAT | S | mass | present | nickel sheet to the booth | 0.02 kg/d | — |
| IA-COAT-OUT | ELECTRODE_COAT | EW_1 | S | mass | present | coated anode | 0.02 kg/d | — |
| IA-PV-IN | WS_DOPE | SOLAR_PV_CELL | S | mass | present | dopant concentrate | 0.01 kg/d | — |
| IA-PV-OUT | SOLAR_PV_CELL | WAFER_FAB | S | mass | present | dopant into the wafer fab | 0.009999 kg/d | — |
| IA-MET-AIR-RET | MET_SCRUB | MET_AHU | G | mass | present | scrubbed metal-aisle air returned to the hall | 71604.0 kg/d | — |
| IA-ACID-AIR-RET | ACID_POLISH_SCRUB | ALK_SCRUBBER | G | mass | present | acid-gas dilution air returned to the alkaline scrubber | 37509.8254 kg/d | — |
| CUT-1-OUT | PROD_C5_C10 | BACKUP_GEN | L | mass | present | C5-C10 fuel from the tank | 0.053896 kg/d | — |
| CUT-3-OUT | PROD_C19_C28 | MFG_SHOP | L | mass | present | C19-C28 from the tank | 3.947559 kg/d | — |
| IA-SIC-RET | NUTRIENT_DOSE | LEACH_CSTR_1 | L | mass | present | compost carbon returned to the leach | 0.466189 kg/d | — |
| IA-NIT-VENT | WS_NITRIC | NOX_SCRUB | G | mass | present | nitric tank vent | 0.0 kg/d | — |
| IA-FLUE-QUENCH | ROOF_TANK | FLUE_KO | L | mass | present | flue quench water | 24.31 kg/d | — |
| IA-PEROX-H2O | ROOF_TANK | WS_PEROX | L | mass | present | peroxide dilution water | 2.824 kg/d | — |
| S17-BMED | SOL_ARK_60K | BMED_ACID | E | elec | present | 480 V AC | 5.6267 kW | — |
| IA-BMED-03-TRIM | LEACH_CSTR_1 | GEO_GHEX | E | thermal | present | trim cooler heat from IA-BMED-03 (to BMED_ACID) | 0.78 kW | — |
| IA-BMED-04-TRIM | LEACH_CSTR_1 | GEO_GHEX | E | thermal | present | trim cooler heat from IA-BMED-04 (to BMED_BASE) | 1.027 kW | — |
| IA-LEACH-VCD | LEACH_CSTR_1 | VCD_TRAIN | L | mass | present | leach liquor water bleed to vapour-compression distillation | 168.058609 kg/d | — |
| SF-ALK_SCRUBBER | SOL_ARK_60K | ALK_SCRUBBER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.1123 kW | — |
| SF-BMED_UPW_POLISH | SOL_ARK_60K | BMED_UPW_POLISH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.018 kW | — |
| SF-CRYO_H2 | SOL_ARK_60K | CRYO_H2 | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.9327 kW | — |
| SF-GEO_HP | SOL_ARK_60K | GEO_HP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SF-GLASS_DIGEST | SOL_ARK_60K | GLASS_DIGEST | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.09 kW | — |
| SF-H2_DRYER | SOL_ARK_60K | H2_DRYER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.0205 kW | — |
| SF-LEACH_CSTR_1 | SOL_ARK_60K | LEACH_CSTR_1 | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SF-MEOH_SYNTH | SOL_ARK_60K | MEOH_SYNTH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.7388 kW | — |
| SF-MFG_SHOP | SOL_ARK_60K | MFG_SHOP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.903 kW | — |
| SF-NUTRIENT_DOSE | SOL_ARK_60K | NUTRIENT_DOSE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SF-WAFER_FAB | SOL_ARK_60K | WAFER_FAB | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SF-WET_BENCH | SOL_ARK_60K | WET_BENCH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.0 kW | — |
| SF-LITHO_STUB | SOL_ARK_60K | LITHO_STUB | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SF-ELECTRODE_COAT | SOL_ARK_60K | ELECTRODE_COAT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SF-BLOW_MOLD | SOL_ARK_60K | BLOW_MOLD | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.5 kW | — |
| SF-SOLAR_PV_CELL | SOL_ARK_60K | SOLAR_PV_CELL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3917 kW | — |
| IA-NA-PURGE | LEACH_CSTR_1 | NORTH_DOCK | L | mass | present | sodium salt purge equal to the make-up mass | 4.3936 kg/d | — |
| SF-OIL_PYRO | SOL_ARK_60K | OIL_PYRO | E | elec | present | 480 V AC | 1.664 kW | — |
| IA-BLK-01 | HABITATION | BLACK_DIGEST | L | mass | present | vacuum-toilet blackwater | 19.644 kg/d | — |
| IA-BLK-GAS | BLACK_DIGEST | AFTERBURNER | G | mass | present | digester biogas, flared in the afterburner | 0.0986 kg/d | — |
| SF-BLACK_DIGEST | SOL_ARK_60K | BLACK_DIGEST | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1052 kW | — |
| IA-GEN-O2 | HDR_O2 | BACKUP_GEN | G | mass | present | combustion O2, 10 % excess | 0.207942 kg/d | — |
| IA-AB-O2 | HDR_O2 | AFTERBURNER | G | mass | present | combustion O2, 10 % excess | 0.528278 kg/d | — |
| IA-HCO2-MEOH | HDR_CO2 | MEOH_SYNTH | G | mass | present | CO2 not taken by the bed | 3.138638 kg/d | — |
| IA-H2O-MU | NORTH_DOCK | LEACH_CSTR_1 | L | mass | present | water make-up for H and O leaving as product | 64.813443 kg/d | — |
| IA-EW1-CL2 | EW_1 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 88.32517 kg/d | — |
| IA-EW2-CL2 | EW_2 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 88.354656 kg/d | — |
| IA-EW3-CL2 | EW_3 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 33.164878 kg/d | — |
| IA-EW4-CL2 | EW_4 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 7.154886 kg/d | — |
| IA-EW5-CL2 | EW_5 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 7.40552 kg/d | — |
| IA-EW6-CL2 | EW_6 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 8.07044 kg/d | — |
| IA-EW7-CL2 | EW_7 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 104.952575 kg/d | — |
| IA-EW8-CL2 | EW_8 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 7.44975 kg/d | — |
| IA-EW9-CL2 | EW_9 | LEACH_CSTR_1 | G | mass | present | anode Cl2 (+ O2 side) to leach oxidation | 111.134409 kg/d | — |
| IA-C5-SHIP | PROD_C5_C10 | NORTH_DOCK | L | mass | present | C5-C10 product shipped | 6.955972 kg/d | — |
| IA-C11-SHIP | PROD_C11_C18 | NORTH_DOCK | L | mass | present | C11-C18 surplus shipped | 1.511662 kg/d | — |
| IA-C19-SHIP | PROD_C19_C28 | NORTH_DOCK | L | mass | present | C19-C28 surplus shipped | 2.218146 kg/d | — |
| IA-ATOM-REMELT | GAS_ATOMIZER | MET_MELT | S | mass | present | off-spec powder to remelt | 0.355595 kg/d | — |
| SF-CRYO_AHU | SOL_ARK_60K | CRYO_AHU | E | elec | present | AHU coil chiller | 0.6472 kW | — |
| SF-MEOH_FERM | SOL_ARK_60K | MEOH_FERM | E | elec | present | 480 V AC | 0.0207 kW | — |
| SF-ACID_POLISH_SCRUB | SOL_ARK_60K | ACID_POLISH_SCRUB | E | elec | present | 480 V AC | 1.1123 kW | — |
| SF-NOX_SCRUB | SOL_ARK_60K | NOX_SCRUB | E | elec | present | 480 V AC | 0.0385 kW | — |
| SF-MET_SCRUB | SOL_ARK_60K | MET_SCRUB | E | elec | present | 480 V AC | 2.1234 kW | — |
| IA-ACID-01 | EVAP_ACID | LEACH_CSTR_1 | L | mass | present | regen HCl, 20 wt% | 439.6125 kg/d | — |
| IA-BASE-01 | EVAP_BASE | GLASS_DIGEST | L | mass | present | digest NaOH, 20 wt% | 21.968 kg/d | — |
| IA-BASE-PPT | EVAP_BASE | LEACH_CSTR_1 | L | mass | present | NaOH 20 wt% to hydroxide precipitation of leached Al, Ca, Mg, Fe (class A) | 482.2861 kg/d | — |
| IA-EVAP_ACID-FEED | BMED_ACID | EVAP_ACID | L | mass | present | HCl 2 M from BMED | 1304.786 kg/d | — |
| IA-EVAP_ACID-COND | EVAP_ACID | BMED_ACID | L | mass | present | evaporator condensate return (BMED water make-up) | 865.1442 kg/d | — |
| SF-EVAP_ACID | SOL_ARK_60K | EVAP_ACID | E | elec | present | 480 V AC | 1.498 kW | — |
| IA-EVAP_BASE-FEED | BMED_BASE | EVAP_BASE | L | mass | present | NaOH 2 M from BMED | 1301.7164 kg/d | — |
| IA-EVAP_BASE-COND | EVAP_BASE | BMED_BASE | L | mass | present | evaporator condensate return (BMED water make-up) | 801.8559 kg/d | — |
| SF-EVAP_BASE | SOL_ARK_60K | EVAP_BASE | E | elec | present | 480 V AC | 1.328 kW | — |
| IA-NAOH-MU | NORTH_DOCK | EVAP_BASE | S | mass | present | purchased NaOH flake make-up | 4.3936 kg/d | — |
| IA-AIR-IN | NORTH_DOCK | CRYO_ASU | S/L | mass | present | intake air | 0.0 kg/d | — |
| IA-NOX-CO2 | NOX_SCRUB | CRYO_ASU | S/L | mass | present | scrubbed CO2 to the cold box | 21.747426 kg/d | — |
| IA-NOX-N2 | NOX_SCRUB | CRYO_ASU | S/L | mass | present | scrubbed flue nitrogen to the cold box | 196.655522 kg/d | — |
| IA-ASU-N2 | CRYO_ASU | CRYO_N2 | G | mass | present | nitrogen product | 196.588593 kg/d | — |
| IA-ASU-O2 | CRYO_ASU | CRYO_O2 | G | mass | present | oxygen product | 0.066929 kg/d | — |
| IA-ASU-CO2 | CRYO_ASU | CRYO_CO2 | G | mass | present | CO2 product | 21.747426 kg/d | — |
| IA-H2-AIR | H2_DRYER | CRYO_ASU | G | mass | present | sweep air from the hydrogen hood | 0.0 kg/d | — |
| IA-N2-RET | HDR_N2 | CRYO_ASU | S | mass | present | nitrogen return | 0.0 kg/d | — |
| IA-O2-RET | HDR_O2 | CRYO_ASU | S | mass | present | oxygen return | 0.0 kg/d | — |
| IA-CO2-RET | CRYO_CO2 | CRYO_ASU | S | mass | present | CO2 return | 0.0 kg/d | — |
| IA-LEACH-ASU | LEACH_CSTR_1 | CRYO_ASU | S/L | mass | present | dissolved gas | 0.0 kg/d | — |
| SF-CRYO_ASU | SOL_ARK_60K | CRYO_ASU | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.6689 kW | — |
| IA-ELY-H2O | ROOF_TANK | H2O_ELYZ | L | mass | present | electrolyser feed water | 83.647854 kg/d | — |
| IA-ELY-H2 | H2O_ELYZ | CRYO_H2 | G | mass | present | electrolyser H2 | 9.360759 kg/d | — |
| IA-ELY-O2 | H2O_ELYZ | CRYO_O2 | G | mass | present | electrolyser O2 | 74.287095 kg/d | — |
| SF-H2O_ELYZ | SOL_ARK_60K | H2O_ELYZ | E | elec | present | 480 V AC (daily average) | 21.4517 kW | — |
| IA-O2-PROD | HDR_O2 | PROD_O2 | G | mass | present | surplus O2 to product cylinders | 22.876312 kg/d | — |
| IA-O2-SHIP | PROD_O2 | NORTH_DOCK | G | mass | present | O2 cylinders shipped at the dock | 22.876312 kg/d | — |
| SF-IND_MELT | SOL_ARK_60K | IND_MELT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 25.0 kW | — |
| SF-VAC_IND | SOL_ARK_60K | VAC_IND | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 15.0 kW | — |
| SF-RF_HEAT | SOL_ARK_60K | RF_HEAT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 5.0 kW | — |
| SF-HF_GEN | SOL_ARK_60K | HF_GEN | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.0 kW | — |
| S100 | Q4_BUS | LEACH_CSTR_1 | E | thermal | present | Q4 water to HX-9 leach make-up preheater | 0.5322 kW | — |
| S101 | Q4_BUS | GLASS_DIGEST | E | thermal | present | Q4 water to HX-10 digest caustic preheater | 0.2822 kW | — |
| IA-Q4-ADS | Q4_BUS | ADS_CHILL | E | thermal | present | Q4 water 65 C drive (summer design) | 5.0 kW | — |
| IA-ADS-CHW | ADS_CHILL | HABITATION | E | thermal | present | chilled water 12 C (kW_c cooling service) | 2.25 kW | — |
| IA-ADS-REJ | ADS_CHILL | DRY_COOLER | E | thermal | present | recooling (absorber + condenser) via the shared terminal | 7.25 kW | — |
| IA-Q4-MAU | Q4_BUS | MAU_HX | E | thermal | present | Q4 water 65/45 C (winter design) | 12.0 kW | — |
| IA-MAU-AIR | MAU_HX | HABITATION | E | thermal | present | tempered make-up air (+1.8 K) | 12.0 kW | — |
| IA-RECT-Q4 | RECTIFIER | Q4_BUS | E | thermal | present | rectifier electronics reject <= 60 C | 1.0 kW | — |
| IA-TRIM-HX5 | RECTIFIER | LEACH_CSTR_1 | E | elec,thermal | present | HX-5 electric trim at the process | 15.882 kW | — |
| IA-TRIM-HX6 | RECTIFIER | GLASS_DIGEST | E | elec,thermal | present | HX-6 electric trim at the process | 4.158 kW | — |
| SQ-H2O_ELYZ-Q4 | H2O_ELYZ | Q4_BUS | E | thermal | present | PEM stack heat above Q4 return | 6.0845 kW | — |
| IA-URINE | HABITATION | BLACK_DIGEST | L | mass | present | urine to the blackwater barrier train | 1.42 kg/d | — |
| IA-FEC-01 | HABITATION | BLACK_DIGEST | S | mass | present | fecal solids to the blackwater barrier train | 0.13 kg/d | — |
| IA-GAL | HABITATION | BLACK_DIGEST | S | mass | present | galley food waste to the blackwater barrier train | 1.18 kg/d | — |
| IA-BLK-CAKE | BLACK_DIGEST | AFTERBURNER | S | mass | present | dewatered digestate cake to incineration (barrier 2) | 0.67 kg/d | — |
| IA-BLK-NUT | BLACK_DIGEST | NUTRIENT_DOSE | L | mass | present | released digest-liquor nutrient split | 0.9 kg/d | — |
| IA-BLK-GREY | BLACK_DIGEST | GREY_TREAT | L | mass | present | released digest liquor to grey treatment | 21.0508 kg/d | — |
| IA-MEOH-PROD | MEOH_TANK | PROD_MEOH | L | mass | present | methanol product | 28.3639 kg/d | — |
| IA-MEOH-SHIP | PROD_MEOH | NORTH_DOCK | L | mass | present | methanol shipped at the dock | 28.3639 kg/d | — |
| IA-DC-EW_1 | RECTIFIER | EW_1 | E | elec | present | DC bus bar | 5.9909 kW | — |
| IA-DC-EW_2 | RECTIFIER | EW_2 | E | elec | present | DC bus bar | 5.9929 kW | — |
| IA-DC-EW_3 | RECTIFIER | EW_3 | E | elec | present | DC bus bar | 2.2495 kW | — |
| IA-DC-EW_4 | RECTIFIER | EW_4 | E | elec | present | DC bus bar | 0.4853 kW | — |
| IA-DC-EW_5 | RECTIFIER | EW_5 | E | elec | present | DC bus bar | 0.5024 kW | — |
| IA-DC-EW_6 | RECTIFIER | EW_6 | E | elec | present | DC bus bar | 0.5474 kW | — |
| IA-DC-EW_7 | RECTIFIER | EW_7 | E | elec | present | DC bus bar | 7.1187 kW | — |
| IA-DC-EW_8 | RECTIFIER | EW_8 | E | elec | present | DC bus bar | 0.5054 kW | — |
| IA-DC-EW_9 | RECTIFIER | EW_9 | E | elec | present | DC bus bar | 7.538 kW | — |
| IA-EW3-H2B | EW_3 | HDR_H2 | G | mass | present | cathode H2 to the H2 pool | 0.143667 kg/d | — |
| IA-EW5-H2B | EW_5 | HDR_H2 | G | mass | present | cathode H2 to the H2 pool | 0.03208 kg/d | — |
| IA-EW6-H2B | EW_6 | HDR_H2 | G | mass | present | cathode H2 to the H2 pool | 0.03496 kg/d | — |
| IA-EW7-H2B | EW_7 | HDR_H2 | G | mass | present | cathode H2 to the H2 pool | 0.454643 kg/d | — |
| IA-EW8-H2B | EW_8 | HDR_H2 | G | mass | present | cathode H2 to the H2 pool | 0.032272 kg/d | — |
| SF-EXT_HALL | SOL_ARK_60K | EXT_HALL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 97.486 kW | — |
| IA-C5-POLY | PROD_C5_C10 | POLY_OLEFIN | L | mass | present | C5-C10 naphtha olefin feed | 0.414905 kg/d | — |
| SQ-EVAP_ACID | EVAP_ACID | HEAT_SINK | E | energy | present | electrical input leaving as heat | 1.498 kW | — |
| SQ-EVAP_BASE | EVAP_BASE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 1.328 kW | — |
| IA-EVAP_ACID-VENT | EVAP_ACID | EVAP_ACID_VS | G | mass | present | column vent: non-condensables, water vapour, trace HCl | 0.0293 kg/d | — |
| IA-VS-NAOH | BMED_BASE | EVAP_ACID_VS | L | mass | present | NaOH 2 M bleed | 0.0005 kg/d | — |
| IA-VS-SPENT | EVAP_ACID_VS | BMED_ACID | L | mass | present | spent scrub liquor (NaCl in NaOH) to the BMED brine | 0.0006 kg/d | — |
| IA-VS-OFF | EVAP_ACID_VS | ALK_SCRUBBER | G | mass | present | scrubbed vent to the house acid-gas header | 0.0292 kg/d | — |
| SF-EVAP_ACID_VS | SOL_ARK_60K | EVAP_ACID_VS | E | elec | present | 480 V AC | 0.0238 kW | — |
| SQ-EVAP_ACID_VS | EVAP_ACID_VS | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.0238 kW | — |
| IA-H2P-H2O | H2_DRYER | VCD_TRAIN | L | mass | present | TSA regeneration condensate | 0.0 kg/d | — |
| S14D | FOOD_STORE | HABITATION | S | mass | present | food | 4.2 kg/d | — |
| IA-STOCK-STORE | STOCK_OUT | METAL_STORE | S | mass | present | formed metal product to the store | 14.0 kg/d | — |
| IA-AIR-RX-OUT | AIR_RECEIVER | HDR_N2 | G | mass | present | plant air from the receiver bank | 191.989014 kg/d | — |
| IA-FERM-DIG | MEOH_FERM | BLACK_DIGEST | S | mass | present | fermenter digestate (water + spent solids) | 0.3454 kg/d | — |
| IA-SOLV-MU | NORTH_DOCK | WS_SOLV | L | mass | present | solvent resupply (ethanol and acetone) | 0.209973 kg/d | — |
