# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev K (`plant_flow_graph.json`)
Generated: 2026-10-07
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.
Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.

| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |
|---|---|---|---|---|---|---|---|---|
| C29_RECYCLE | PROD_C29 | C29_RECYCLE | L | mass | present | C29 heavy cut | — | — |
| C29_TO_PYRO | C29_RECYCLE | OIL_PYRO | L | mass | present | C29 heavy cut | — | — |
| CUT-1 | OIL_FRAC | PROD_C5_C10 | L | mass | present | fractionator cut | — | — |
| CUT-2 | OIL_FRAC | PROD_C11_C18 | L | mass | present | fractionator cut | — | — |
| CUT-3 | OIL_FRAC | PROD_C19_C28 | L | mass | present | fractionator cut | — | — |
| CUT-4 | OIL_FRAC | PROD_C29 | L | mass | present | fractionator cut | — | — |
| DOCK_EXPORT_TBD | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | placeholder | goods / cassettes / surplus freight (ID TBD) | — | no_S_id,do_not_invent_route_or_rate,high_severity_audit |
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
| IA-BMED-01 | BMED_ACID | WS_NITRIC | L | mass | present | HCl product | — | — |
| IA-BMED-02 | BMED_BASE | WS_KOH | L | mass | present | NaOH product | — | — |
| IA-BMED-03 | CRU | BMED_ACID | L | mass | placeholder | CRU → BMED acid regen loop | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | CRU | BMED_BASE | L | mass | placeholder | CRU → BMED base regen loop | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | — | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | — | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | placeholder | Hydro turbine-pump electrical (MISSING on SLD) | — | ess_layer,missing_on_sld |
| IA-ESS-MEOH-CHG | MEOH_SYNTH | MEOH_TANK | L | mass,ess | placeholder | MeOH synth inventory = charge-analogue | — | ess_layer |
| IA-ESS-MEOH-DIS | MEOH_FC | SOL_ARK_60K | E | elec,ess | placeholder | MeOH FC discharge (peers S79) | — | ess_layer,overlaps_S79_architecture |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | placeholder | ZnBr2 charge (PV/RECT surplus) | — | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | placeholder | ZnBr2 discharge to bus | — | ess_layer |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW overflow | — | — |
| IA-EW-02 | EW_2 | EW_3 | L | mass | present | EW overflow | — | — |
| IA-EW-03 | EW_3 | EW_4 | L | mass | present | EW overflow | — | — |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR to EW-1 | — | — |
| IA-EW-05 | EW_5 | EW_6 | L | mass | present | EW overflow | — | — |
| IA-EW-06 | EW_6 | EW_7 | L | mass | present | EW overflow | — | — |
| IA-EW-07 | EW_7 | EW_8 | L | mass | present | EW overflow | — | — |
| IA-EW-08 | EW_8 | EW_9 | L | mass | present | EW overflow | — | — |
| IA-EW-09 | EW_9 | POLISH_BANK | L | mass | present | EW tail to polish | — | — |
| IA-EW-10 | EW_4 | EW_5 | L | mass | present | EW overflow | — | — |
| IA-GLASS-01 | GLASS_RINSE | GLASS_MILL | S | mass | present | rinsed cullet | — | — |
| IA-GLASS-02 | GLASS_MILL | GLASS_BURNOUT | S | mass | present | milled cullet | — | — |
| IA-GLASS-03 | GLASS_BURNOUT | GLASS_DIGEST | S | mass | present | burned cullet | — | — |
| IA-HDR-H2-01 | EW_1 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l1_topology,wp_l2_filled,ew_cascade_exploded |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 4.8 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure,ew_cascade_exploded |
| IA-HDR-H2-03 | EW_2 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HX8 | EW_1 | HX8 | heat | thermal | present | EW heat | 4.572 kW | — |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | placeholder | Dryer → pyro | — | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | placeholder | Pyro → frac | — | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | NCG_HEADER | G | mass | present | NCG only | — | — |
| IA-POL-01 | POLISH_BANK | BMED_UPW_POLISH | L | mass | placeholder | Polish bank → UPW polish | — | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-POL-02 | POLISH_BANK | POLISH_BANK | L | mass | placeholder | Polish series internals (self-loop stub) | — | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | continuous recycle liquor | — | — |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | placeholder | Float/sink liquor return | — | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| NCG_TO_AB | NCG_HEADER | AFTERBURNER | G | mass | present | NCG | — | — |
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 95.0 kg/d | — |
| S02 | CRYO_O2 | HABITATION | G | mass | present | O2 | 3.4 kg/d | — |
| S03 | CRYO_N2 | WAFER_FAB | G | mass | present | N2 | — | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 1.109 kg/d | — |
| S05 | H2_DRYER | CRYO_H2 | G | mass | present | process H2 | 4.8 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | — | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 42.0 kg/d | — |
| S08G | GLASS_DIGEST | BOUNDARY_EXPORT | S | mass | present | glass/ceramic goods | 30.0 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S09 | BMED_ACID | WET_BENCH | L | mass | present | HCl | — | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 10.0 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | NUTRIENT_DOSE | L/S | mass | present | grey/solids | 110.0 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | placeholder | condensate | — | absent_from_candidate_mvs |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 4.2 kg/d | — |
| S14X | GROW_BED | BOUNDARY_EXPORT | S | mass | present | food surplus export | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | — | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.0 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 50.0 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | flue-carbon claim reference (no CO2 mass since Rev J) | 0.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | — | absent_from_candidate_mvs |
| S20 | GROW_BED | SOL_ARK_60K | E | elec | present | load | — | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 95.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | — | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | — | — |
| S24 | H2_DRYER | RELIEF_H2 | G | mass | present | H2 relief contingency | — | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | placeholder | VCD distillate | — | — |
| S26 | REMIN | HABITATION | L | mass | placeholder | potable | — | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | — | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | placeholder | VCD brine | — | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | placeholder | treated grey | — | absent_from_candidate_mvs |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | — | absent_from_candidate_mvs |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | — | absent_from_candidate_mvs |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | — | absent_from_candidate_mvs |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | — | absent_from_candidate_mvs |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | — | absent_from_candidate_mvs |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | — | absent_from_candidate_mvs |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | — | absent_from_candidate_mvs |
| S38 | WET_BENCH | OIL_FRAC | L | mass | present | resist and solvent waste | — | — |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry and etch liquor | — | — |
| S39B | WAFER_FAB | OIL_FRAC | L | mass | present | solvent and photoresist | — | — |
| S40 | ROOF_TANK | TERRACE_IRRIG | L | mass | present | clean overflow | — | — |
| S41 | TERRACE_IRRIG | CATCH_TANK | L | mass | present | rain + S40 return | — | absent_from_candidate_mvs |
| S42 | TERRACE_IRRIG | GREY_TREAT | L | mass | present | dilute nutrient drain | — | absent_from_candidate_mvs |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | — | absent_from_candidate_mvs |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | H2 fuel | 3.6 kg/d | — |
| S46 | BACKUP_GEN | NOX_SCRUB | L/G | mass | present | exhaust condensate / NOx | — | — |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 2.5 kW | — |
| S48 | GEO_ORC | SOL_ARK_60K | E | elec | placeholder | ORC AC | — | orc_stub_kw_tbd |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 4.8 kg/d | — |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 4.0 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | placeholder | PEM product H2O | — | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | — | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | — | absent_from_candidate_mvs |
| S56 | CRYO_AHU | RELIEF_CRYO | G | mass | present | non-condensable residual after KO | — | — |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | — | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | — | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | — | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | — | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | — | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | — | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | — | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | — | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | FLUE_KO | G | mass | present | flue N2/O2/CO2/NOx | 241.7 kg/d | — |
| S67B | FLUE_KO | CRYO_CO2 | G | mass | present | CO2-rich gas after KO | 12.75 kg/d | — |
| S68 | CRYO_AHU | LEACH_CSTR_1 | L | mass | present | flue condensate | — | — |
| S69 | ZNBR2 | ZNBR2_BR2_REGEN | G | mass | present | Br2 vapor | — | — |
| S69B | ZNBR2_BR2_REGEN | ZNBR2 | L | mass | present | NaBr after ORP | — | — |
| S70 | CRYO_AHU_COND_CONDENSABLE | FLUE_KO | L | mass | present | condensables | — | — |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | — | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | metal fines and aqueous scrub liquor | — | — |
| S72B | MET_SCRUB | OIL_FRAC | L | mass | present | organic mist | — | — |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 6.9 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 0.94 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 5.0 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | ess | present | MeOH fuel | 5.0 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | — | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | — | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 1.0 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S81 | MEOH_FC | MEOH_COND | L | mass | present | MeOH FC condensate | — | — |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 6.875 kg/d | — |
| S83 | CRYO_O2 | HDR_O2 | G | mass | present | O2 product | — | — |
| S84 | CRYO_N2 | HDR_N2 | G | mass | present | N2 product | — | — |
| S85 | CRYO_CO2 | HDR_CO2 | G | mass | present | CO2 product after FLUE_KO | 11.616 kg/d | — |
| S86 | CRYO_AHU | RELIEF_CRYO | G | mass | present | cryo residual contingency | — | — |
| S87 | GROW_BED | CRYO_O2 | G | mass | present | surplus O2 capture | — | — |
| S88 | CRYO_N2 | GROW_BED | G | mass | present | N2 make-up | — | — |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO3 | — | — |
| S34B | WS_PHOS | WET_BENCH | L | mass | present | H3PO4 | — | — |
| S89 | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment dose (FARM AHU supply) | 11.616 kg/d | — |
