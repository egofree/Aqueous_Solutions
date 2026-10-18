# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev BH (`plant_flow_graph.json`)
Generated: 2026-10-15
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
| DOCK_EXPORT_TBD | NORTH_DOCK | HOPPER | S | mass | present | returned freight | 0.0 kg/d | no_S_id,high_severity_audit |
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
| IA-BMED-03 | LEACH_CSTR_1 | BMED_ACID | L | mass | present | CRU → BMED acid regen loop | 449.495 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | LEACH_CSTR_1 | BMED_BASE | L | mass | present | CRU → BMED base regen loop | 502.7933 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | 200000.0 kg/d | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec | present | Hydro turbine-pump electrical (MISSING on SLD) | 0.2917 kW | ess_layer,missing_on_sld |
| IA-ESS-ZNBR2-SRC | PV_ARRAY | SOL_ARK_60K | E | ess | present | PV share of the zinc-bromine round-trip loss | 1.6667 kW | ess_layer |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | present | ZnBr2 charge (PV/RECT surplus) | 6.6667 kW | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | present | ZnBr2 discharge to bus | 5.0 kW | ess_layer |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW overflow | 4226.04 kg/d | — |
| IA-EW-02 | EW_2 | EW_3 | L | mass | present | EW overflow | 4164.24 kg/d | — |
| IA-EW-03 | EW_3 | EW_4 | L | mass | present | EW overflow | 4141.76 kg/d | — |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR to EW-1 | 4287.8 kg/d | — |
| IA-EW-05 | EW_5 | EW_6 | L | mass | present | EW overflow | 4128.07 kg/d | — |
| IA-EW-06 | EW_6 | EW_7 | L | mass | present | EW overflow | 4122.6 kg/d | — |
| IA-EW-07 | EW_7 | EW_8 | L | mass | present | EW overflow | 4051.46 kg/d | — |
| IA-EW-08 | EW_8 | EW_9 | L | mass | present | EW overflow | 4046.41 kg/d | — |
| IA-EW-09 | EW_9 | POLISH_BANK | L | mass | present | EW tail to polish | 3971.08 kg/d | — |
| IA-EW-10 | EW_4 | EW_5 | L | mass | present | EW overflow | 4133.09 kg/d | — |
| IA-GLASS-01 | GLASS_RINSE | GLASS_MILL | S | mass | present | rinsed cullet | 36.82 kg/d | — |
| IA-GLASS-02 | GLASS_MILL | GLASS_BURNOUT | S | mass | present | milled cullet | 30.0 kg/d | — |
| IA-GLASS-03 | GLASS_BURNOUT | GLASS_DIGEST | S | mass | present | burned cullet | 30.0 kg/d | — |
| IA-HDR-H2-01 | EW_1 | HDR_H2 | G |  | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l1_topology,wp_l2_filled,ew_cascade_exploded |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 6.628752089257418 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure,ew_cascade_exploded |
| IA-HDR-H2-03 | EW_2 | HDR_H2 | G |  | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G |  | present | cathode H2 + sweep air | 2.1333 kg/d | wp_l2_filled,multi_ew_hood,ew_cascade_exploded |
| IA-HX8 | EW_1 | HX8 | heat | thermal | present | EW heat | 4.572 kW | — |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | present | Dryer → pyro | 33.0 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | present | Pyro → frac | 28.9046 kg/d | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | NCG_HEADER | G | mass | present | NCG only | 5.0 kg/d | — |
| IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | L | mass | present | raffinate (EW tail after polish) to continuous recycle | 3753.71 kg/d | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | continuous recycle liquor | 3753.71 kg/d | — |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | present | Float/sink liquor return | 343.1 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| NCG_TO_AB | NCG_HEADER | AFTERBURNER | G | mass | present | NCG | 5.0 kg/d | — |
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 67.3 kg/d | — |
| S02 | HDR_O2 | HABITATION | G | mass | present | O2 | 3.36 kg/d | — |
| S03 | HDR_N2 | WAFER_FAB | G | mass | present | N2 | 1.4998 kg/d | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 1.575188 kg/d | — |
| S05 | H2_DRYER | CRYO_H2 | G | mass | present | process H2 | 6.628752089257418 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | 0.0 kW | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals and entrained silicate (Si as SiO2) | 42.0021 kg/d | — |
| S08G | GLASS_DIGEST | MFG_SHOP | S | mass | present | glass and ceramic stock | 26.2 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S09 | BMED_ACID | WET_BENCH | L | mass | present | HCl | 9.2772 kg/d | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 79.11551173968371 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | GREY_TREAT | L/S | mass | present | grey/solids | 258.6599999999997 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | present | condensate | 3.7995 kg/d | absent_from_candidate_mvs |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 2.4 kg/d | — |
| S14X | GROW_BED | BSFL | S | mass | present | food waste to larvae | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | 0.0 kg/d | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.0 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 23.32 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | flue-carbon claim reference (no CO2 mass since Rev J) | 0.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | 0.0 kg/d | absent_from_candidate_mvs |
| S20 | SOL_ARK_60K | GROW_BED | E | elec | present | load | 2.25 kW | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 120.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | 0.4088 kW | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | 0.4088 kW | — |
| S24 | H2_DRYER | RELIEF_H2 | G | mass | present | H2 relief contingency | 0.0 kg/d | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | present | VCD distillate | 263.816 kg/d | — |
| S26 | REMIN | HABITATION | L | mass | present | potable | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | 60.0 kg/d | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | VCD brine | 17.881152089257387 kg/d | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | present | treated grey | 104.5 kg/d | absent_from_candidate_mvs |
| S30 | DIGESTER | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | 0.0 kg/d | absent_from_candidate_mvs |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | 1.5 kg/d | absent_from_candidate_mvs |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | 3.0 kg/d | absent_from_candidate_mvs |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | 3.008739154859247 kg/d | absent_from_candidate_mvs |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | 0.27 kg/d | absent_from_candidate_mvs |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | 0.0 kg/d | absent_from_candidate_mvs |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | 3.3 kg/d | absent_from_candidate_mvs |
| S38 | WET_BENCH | OIL_FRAC | L | mass | present | resist and solvent waste | 0.006 kg/d | — |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry and etch liquor | 3.31 kg/d | — |
| S39B | WAFER_FAB | OIL_FRAC | L | mass | present | solvent and photoresist | 0.0 kg/d | — |
| S40 | ROOF_TANK | TERRACE_IRRIG | L | mass | present | clean overflow | 37.176 kg/d | — |
| S41 | TERRACE_IRRIG | CATCH_TANK | L | mass | present | rain + S40 return | 0.0 kg/d | absent_from_candidate_mvs |
| S42 | TERRACE_IRRIG | GREY_TREAT | L | mass | present | dilute nutrient drain | 0.0 kg/d | absent_from_candidate_mvs |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | 0.0 kW | absent_from_candidate_mvs |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0 kW | absent_from_candidate_mvs |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | unused synthesis hydrogen | 0.6517575950373788 kg/d | — |
| S46 | BACKUP_GEN | NOX_SCRUB | L/G | mass | present | exhaust condensate / NOx | 61.80705759503738 kg/d | — |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 2.5 kW | — |
| S49 | CRYO_H2 | H2_PURIFIER | G | mass | present | H2 to purifier | 5.028752089257418 kg/d | — |
| S50 | HDR_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 3.46 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | present | PEM product H2O | 42.881652089257415 kg/d | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | 1.1419 kW | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | 0.5448 kW | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | 4.2838 kW | absent_from_candidate_mvs |
| S56 | CRYO_AHU | RELIEF_CRYO | G | mass | present | non-condensable residual after KO | 0.0 kg/d | — |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | 6.8389 kg/d | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | 3.9389 kg/d | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | 3.95 kg/d | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | 3.2 kg/d | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | 1.1971 kg/d | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | 51145.68 kg/d | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | 0.0171 kW | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 0.0 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | 37509.84 kg/d | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | 27.3623 kg/d | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | FLUE_KO | G | mass | present | flue N2/O2/CO2/NOx | 117.436188 kg/d | — |
| S67B | FLUE_KO | CRYO_CO2 | G | mass | present | CO2-rich gas after KO | 13.304 kg/d | — |
| S68 | CRYO_AHU | LEACH_CSTR_1 | L | mass | present | flue condensate | 78.9879 kg/d | — |
| S69 | ZNBR2 | ZNBR2_BR2_REGEN | G | mass | present | Br2 vapor | 852.47 kg/d | — |
| S69B | ZNBR2_BR2_REGEN | ZNBR2 | L | mass | present | NaBr after ORP | 852.47 kg/d | — |
| S70 | CRYO_AHU_COND_CONDENSABLE | FLUE_KO | L | mass | present | condensables | 0.0521 kg/d | — |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | 20458.32 kg/d | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | metal fines and aqueous scrub liquor | 2.4442 kg/d | — |
| S72B | MET_SCRUB | OIL_FRAC | L | mass | present | organic mist | 0.0158 kg/d | — |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 6.9 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | hydrogen consumed | 0.9482424049626212 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | methanol | 5.023740598513941 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | mass,ess | present | MeOH fuel | 4.579140598513943 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | 0.0146 kg/d | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | 0.36 kg/d | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec | present | MEOH DC | 0.5 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | 0.3689 kW | absent_from_candidate_mvs |
| S81 | MEOH_FC | MEOH_COND | L | mass | present | MeOH FC condensate | 1.6549096212978096 kg/d | — |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 6.875 kg/d | — |
| S83 | CRYO_O2 | HDR_O2 | G | mass | present | O2 product | 48.05 kg/d | — |
| S84 | CRYO_N2 | HDR_N2 | G | mass | present | N2 product | 243.28 kg/d | — |
| S85 | CRYO_CO2 | HDR_CO2 | G | mass | present | CO2 product after FLUE_KO | 12.17 kg/d | — |
| S86 | CRYO_AHU | RELIEF_CRYO | G | mass | present | cryo residual contingency | 0.0 kg/d | — |
| S87 | GROW_BED | CRYO_O2 | G | mass | present | surplus O2 capture | 0.0 kg/d | — |
| S88 | CRYO_N2 | GROW_BED | G | mass | present | N2 make-up | 0.0 kg/d | — |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO3 | 1.2456 kg/d | — |
| S34B | WS_PHOS | WET_BENCH | L | mass | present | H3PO4 | 0.61 kg/d | — |
| S89 | HDR_CO2 | GROW_BED | G | mass | present | CO2 enrichment dose (FARM AHU supply) | 17.071 kg/d | — |
| S90 | HABITATION | HDR_CO2 | G | mass | present | metabolic CO2 (desorbed from the HAB CO2 sorbent bed) | 4.021 kg/d | — |
| IA-GREY-01 | GREY_TREAT | LEACH_CSTR_1 | S/L | mass | present | grey sludge | 242.64719999999969 kg/d | — |
| IA-CRU-01 | CRU | LEACH_CSTR_1 | L | mass | present | sodium chlorate liquor | 27.3623 kg/d | — |
| IA-ACID-01 | EVAP_ACID | LEACH_CSTR_1 | L | mass | present | regen HCl, 20 wt% | 439.5222 kg/d | — |
| IA-BASE-01 | EVAP_BASE | GLASS_DIGEST | L | mass | present | digest NaOH, 20 wt% | 25.2964 kg/d | — |
| HL-Q4-REJ | Q4_BUS | GEO_ORC | thermal | thermal | present | Q4 surplus heat | 11.7617 kW | — |
| IA-PV-01 | PV_ARRAY | SOL_ARK_60K | electric | elec | present | PV daily average | 144.7766 kW | — |
| IA-ZNBR-BD | ZNBR2 | GREY_TREAT | L | mass | present | electrolyte bleed | 8.4872 kg/d | — |
| IA-NUT-01 | NUTRIENT_DOSE | VCD_TRAIN | L | mass | present | digest surplus | 13.93 kg/d | — |
| IA-UPW-FAB | BMED_UPW_POLISH | FAB_UPW_TANK | L | mass | present | fab UPW | 60.0 kg/d | — |
| IA-UPW-REMIN | BMED_UPW_POLISH | REMIN | L | mass | present | remineralizer | 130.4706 kg/d | — |
| IA-UPW-REJ | BMED_UPW_POLISH | LEACH_CSTR_1 | L | mass | present | polish reject | 6.045 kg/d | — |
| IA-Q4-LIFE | Q4_BUS | HABITATION | thermal | thermal | present | life heat | 3.0 kW | — |
| IA-AB-FLUE | AFTERBURNER | AFTERBURNER_FLUE | G | mass | present | flue | 6.266188 kg/d | — |
| IA-ZNBR-MU | LEACH_CSTR_1 | ZNBR2 | L | mass | present | electrolyte water make-up | 8.4872 kg/d | — |
| IA-EW-MET-1 | EW_1 | MFG_SHOP | S | mass | present | plated sheet | 59.87 kg/d | — |
| IA-EW-MET-2 | EW_2 | MFG_SHOP | S | mass | present | plated sheet | 59.89 kg/d | — |
| IA-EW-MET-3 | EW_3 | MFG_SHOP | S | mass | present | plated sheet | 22.48 kg/d | — |
| IA-EW-MET-4 | EW_4 | MFG_SHOP | S | mass | present | plated sheet | 4.85 kg/d | — |
| IA-EW-MET-5 | EW_5 | MFG_SHOP | S | mass | present | plated sheet | 5.02 kg/d | — |
| IA-EW-MET-6 | EW_6 | MFG_SHOP | S | mass | present | plated sheet | 5.47 kg/d | — |
| IA-EW-MET-7 | EW_7 | MFG_SHOP | S | mass | present | plated sheet | 71.14 kg/d | — |
| IA-EW-MET-8 | EW_8 | MFG_SHOP | S | mass | present | plated sheet | 5.05 kg/d | — |
| IA-EW-MET-9 | EW_9 | MFG_SHOP | S | mass | present | plated sheet | 61.3411 kg/d | — |
| IA-POL-CAKE | POLISH_BANK | MFG_SHOP | S | mass | present | recovered cake | 217.37 kg/d | — |
| IA-AB-AIR | HDR_N2 | AFTERBURNER_FLUE | G | mass | present | combustion air | 111.17 kg/d | — |
| IA-FLUE-EXH | FLUE_KO | NOX_SCRUB | G | mass | present | flue to the NOx scrubber | 264.396188 kg/d | — |
| IA-DIG-LIQ | GLASS_DIGEST | LEACH_CSTR_1 | L | mass | present | silicate liquor | 25.2964 kg/d | — |
| IA-MILL-LOSS | GLASS_MILL | BAGHOUSE | S | mass | present | mill dust | 6.82 kg/d | — |
| IA-MFG-OUT | MFG_SHOP | HABITATION | S | mass | present | goods in service | 596.862812 kg/d | — |
| IA-BED-H2O | ROOF_TANK | GROW_BED | L | mass | present | irrigation | 16.7 kg/d | — |
| IA-MEOH-H2O | MEOH_SYNTH | MEOH_COND | L | mass | present | synthesis water | 2.824501806448681 kg/d | — |
| IA-FC-AIR | HDR_O2 | MEOH_FC | G | mass | present | cell air | 2.481169022783867 kg/d | — |
| IA-Q3A-TRIM | RECTIFIER | Q3_A | electric | thermal | present | leach heater trim | 10.048 kW | — |
| IA-Q3B-TRIM | RECTIFIER | Q3_B | electric | thermal | present | leach heater trim | 10.048 kW | — |
| IA-LEACH-BD | LEACH_CSTR_1 | NUTRIENT_DOSE | L | mass | present | bleed salts to nutrient | 109.63 kg/d | — |
| IA-VCD-BD | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | still bottoms | 6.71 kg/d | — |
| IA-CHAR | OIL_PYRO | MFG_SHOP | S | mass | present | char reductant | 5.20014 kg/d | — |
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
| IA-TERR-VAP | TERRACE_IRRIG | CRYO_AHU | G | mass | present | greenhouse transpiration | 40.0 kg/d | — |
| IA-BED-VAP | GROW_BED | CRYO_AHU | G | mass | present | bed transpiration | 16.7 kg/d | — |
| IA-HAB-VAP | HABITATION | CRYO_AHU | G | mass | present | respired and evaporated water | 0.0 kg/d | — |
| IA-HVAC-COND | CRYO_AHU | ROOF_TANK | L | mass | present | AHU condensate to the water cycle | 56.7 kg/d | — |
| IA-PV-CURTAIL | SOL_ARK_60K | BOUNDARY_EXPORT | electric | elec | present | bus surplus | 4.645 kW | — |
| IA-AHU-AIR | HDR_N2 | CRYO_AHU | G | mass | present | outdoor air moisture | 79.04 kg/d | — |
| IA-ZNBR-LOSS | ZNBR2 | BOUNDARY_EXPORT | electric | elec,ess | present | round-trip loss | 1.67 kW | — |
| IA-GREY-RET | GREY_TREAT | ROOF_TANK | L | mass | present | treated grey to the water cycle | 0.0 kg/d | — |
| IA-RES-01 | GROW_BED | LIGNO_PRE | S/L | mass | present | lignocellulose residue | 8.69 kg/d | — |
| IA-MAN-01 | ANIMAL_PEN | DIGESTER | S/L | mass | present | pen residual | 0.0 kg/d | — |
| IA-FEC-01 | HABITATION | COMPOST_TOILET | S/L | mass | present | feces | 0.8 kg/d | — |
| IA-COMP-01 | GROW_BED | HTC | S/L | mass | present | woody trim | 3.19 kg/d | — |
| IA-DIG-GAS | DIGESTER | EMETH | S/L | mass | present | biogas from the biological feeds | 0.6254 kg/d | — |
| IA-DIG-SOL | DIGESTER | NUTRIENT_DOSE | S/L | mass | present | shop scrap and spent solvent | 0.5228295461217779 kg/d | — |
| IA-EM-CH4 | EMETH | MEOH_TANK | S/L | mass | present | methane | 0.6254 kg/d | — |
| IA-EM-DIG | EMETH | NUTRIENT_DOSE | S/L | mass | present | EM effluent | 0.0 kg/d | — |
| IA-LIG-01 | LIGNO_PRE | BOARD_MILL | S/L | mass | present | lignin | 3.87 kg/d | — |
| IA-CEL-01 | LIGNO_PRE | BOARD_MILL | S/L | mass | present | cellulose | 3.18 kg/d | — |
| IA-BOARD | BOARD_MILL | MFG_SHOP | S/L | mass | present | board, paper, cardboard | 0.69 kg/d | — |
| IA-BOARD-SCRAP | BOARD_MILL | COMPOST | S/L | mass | present | board scrap | 8.01 kg/d | — |
| IA-COMP-OUT | COMPOST | NUTRIENT_DOSE | S/L | mass | present | compost | 141.150288 kg/d | — |
| IA-MEAT | ANIMAL_PEN | HABITATION | S/L | mass | present | withdrawn | 0.0 kg/d | — |
| IA-NUT-LEACH | NUTRIENT_DOSE | LEACH_CSTR_1 | L | mass | present | nutrient surplus | 127.02966334820698 kg/d | — |
| IA-FEED-01 | HOPPER | LEACH_CSTR_1 | L | mass | present | plant feedstock, any class | 102.68 kg/d | — |
| IA-POT-01 | REMIN | ROOF_TANK | L | mass | present | potable makeup, remineralised | 120.47056170745005 kg/d | — |
| IA-HTC-01 | HTC | COMPOST | S/L | mass | present | hydrochar slurry | 3.19 kg/d | — |
| IA-COMP-CO2 | COMPOST | HDR_CO2 | S/L | mass | present | compost CO2 | 0.19 kg/d | — |
| IA-SUGAR | LIGNO_PRE | YEAST | S/L | mass | present | reducing sugars | 1.0 kg/d | — |
| IA-UPW-HAB | HDR_UPW | HABITATION | S/L | mass | present | potable makeup | 0.8 kg/d | — |
| IA-BAG-01 | BAGHOUSE | LEACH_CSTR_1 | S/L | mass | present | captured dust | 7.77 kg/d | — |
| IA-UPW-USE | HDR_UPW | WAFER_FAB | S/L | mass | present | fab UPW | 66.5 kg/d | — |
| IA-MEOH-REST | MEOH_TANK | MEOH_FC | S/L | mass | present | tank draw | 1.28 kg/d | — |
| IA-SINK-01 | LEACH_CSTR_1 | FLOAT_SINK | S/L | mass | present | sink solids | 376.1 kg/d | — |
| IA-PLAST-01 | FLOAT_SINK | OIL_DRYER | S/L | mass | present | float plastics | 33.0 kg/d | — |
| IA-CULLET | LEACH_CSTR_1 | GLASS_RINSE | S/L | mass | present | cullet | 36.82 kg/d | — |
| IA-DIG-BLK | DIGESTER | BLACK_DIGEST | S/L | mass | present | digest liquor | 0.0 kg/d | — |
| IA-SCRUB-SRC | LEACH_CSTR_1 | ACID_POLISH_SCRUB | S/L | mass | present | scrub feed | 27.3623 kg/d | — |
| IA-SIL-SRC | GLASS_DIGEST | WS_SLURRY | S/L | mass | present | silicate to slurry | 3.3 kg/d | — |
| IA-HF-SRC | LEACH_CSTR_1 | WS_HF_ED | S/L | mass | present | fluoride to HF | 1.5 kg/d | — |
| IA-NH3-SRC | HDR_N2 | WS_AMMONIA | S/L | mass | present | nitrogen to ammonia | 3.25 kg/d | — |
| IA-H2O2-SRC | HDR_O2 | WS_PEROX | S/L | mass | present | oxygen to peroxide | 0.176 kg/d | — |
| IA-AIR-IN | NORTH_DOCK | CRYO_ASU | S/L | mass | present | intake air | 0.0 kg/d | — |
| IA-NOX-H2O | NOX_SCRUB | ROOF_TANK | S/L | mass | present | scrubber condensate | 226.221758 kg/d | — |
| IA-NOX-N | NOX_SCRUB | NUTRIENT_DOSE | S/L | mass | present | nitrate liquor | 20.0 kg/d | — |
| IA-NOX-CO2 | NOX_SCRUB | CRYO_ASU | S/L | mass | present | scrubbed CO2 to the cold box | 30.466188 kg/d | — |
| IA-NOX-N2 | NOX_SCRUB | CRYO_ASU | S/L | mass | present | scrubbed flue nitrogen to the cold box | 243.89 kg/d | — |
| IA-FAB-SPENT | WAFER_FAB | LEACH_CSTR_1 | L | mass | present | spent UPW | 66.5023 kg/d | — |
| IA-GEN-AIR | HDR_N2 | BACKUP_GEN | L | mass | present | genset air | 50.0 kg/d | — |
| IA-NOX-HAB | ROOF_TANK | HABITATION | L | mass | present | scrubber water | 207.28 kg/d | — |
| IA-NUT-BED | NUTRIENT_DOSE | GROW_BED | L | mass | present | nitrate and bleed salts | 129.629 kg/d | — |
| IA-BED-COMP | GROW_BED | COMPOST | L | mass | present | salt-laden trim | 130.096188 kg/d | — |
| IA-N2-VENT | CRYO_N2 | NORTH_DOCK | G | mass | present | nitrogen vent | 0.0 kg/d | — |
| IA-HOP-01 | HOPPER | LEACH_CSTR_1 | S | mass | present | returned scrap | 530.285912 kg/d | — |
| IA-ASU-N2 | CRYO_ASU | CRYO_N2 | G | mass | present | nitrogen product | 243.28 kg/d | — |
| IA-ASU-O2 | CRYO_ASU | CRYO_O2 | G | mass | present | oxygen product | 48.05 kg/d | — |
| IA-ASU-CO2 | CRYO_ASU | CRYO_CO2 | G | mass | present | CO2 product | 30.466188 kg/d | — |
| IA-ASU-AR | CRYO_ASU | CRYO_AR | G | mass | present | argon | 5.3 kg/d | — |
| IA-H2-AIR | H2_DRYER | CRYO_ASU | G | mass | present | sweep air from the hydrogen hood | 0.0 kg/d | — |
| IA-AR-FAB | CRYO_AR | WAFER_FAB | G | mass | present | argon cover | 5.3 kg/d | — |
| IA-AR-RET | WAFER_FAB | CRYO_ASU | G | mass | present | argon return | 5.3 kg/d | — |
| IA-ASU-HE | CRYO_ASU | CRYO_HE | G | mass | present | helium | 0.01 kg/d | — |
| IA-ASU-NE | CRYO_ASU | CRYO_NE | G | mass | present | neon | 0.05 kg/d | — |
| IA-ASU-KR | CRYO_ASU | CRYO_KR | G | mass | present | krypton | 0.02 kg/d | — |
| IA-ASU-XE | CRYO_ASU | CRYO_XE | G | mass | present | xenon | 0.01 kg/d | — |
| IA-HE-RET | CRYO_HE | CRYO_ASU | G | mass | present | helium return | 0.01 kg/d | — |
| IA-NE-RET | CRYO_NE | CRYO_ASU | G | mass | present | neon return | 0.05 kg/d | — |
| IA-KR-RET | CRYO_KR | CRYO_ASU | G | mass | present | krypton return | 0.02 kg/d | — |
| IA-XE-RET | CRYO_XE | CRYO_ASU | G | mass | present | xenon return | 0.01 kg/d | — |
| IA-WEAR | HABITATION | HOPPER | S | mass | present | worn goods | 596.863812 kg/d | — |
| IA-N2-RET | HDR_N2 | CRYO_ASU | S | mass | present | nitrogen return | 0 kg/d | — |
| IA-O2-RET | HDR_O2 | CRYO_ASU | S | mass | present | oxygen return | 0 kg/d | — |
| IA-CO2-RET | CRYO_CO2 | CRYO_ASU | S | mass | present | CO2 return | 30.0 kg/d | — |
| IA-MEOH-COND | MEOH_COND | ROOF_TANK | S | mass | present | methanol condensate | 4.4794114277464905 kg/d | — |
| IA-H2-IN | H2_DRYER | HDR_H2 | S | mass | present | dried hydrogen | 0.0 kg/d | — |
| IA-EW-SHEET | EW_9 | MET_MELT | S | mass | present | cathode sheet | 13.9889 kg/d | — |
| IA-PHOS-SRC | LEACH_CSTR_1 | WS_PHOS | S | mass | present | phosphate | 0.62 kg/d | — |
| IA-FERM-RES | MEOH_FERM | DIGESTER | S | mass | present | fermenter residue | 0.3454 kg/d | — |
| IA-MELT-MILL | MET_MELT | COLD_MILL | S | mass | present | melt to the mill | 3.95 kg/d | — |
| IA-MELT-ATOM | MET_MELT | GAS_ATOMIZER | S | mass | present | melt to the atomizer | 3.2 kg/d | — |
| IA-DRAW-FUME | WIRE_DRAW | MET_SCRUB | S | mass | present | draw fume | 2.46 kg/d | — |
| IA-AHU-POT | CRYO_AHU | CRYO_AHU_COND_CONDENSABLE | S | mass | present | condensable slip | 0.0521 kg/d | — |
| IA-LEACH-NOX | LEACH_CSTR_1 | NOX_SCRUB | S/L | mass | present | leach offgas | 195.0247 kg/d | — |
| IA-LEACH-FLUE | LEACH_CSTR_1 | FLUE_KO | S/L | mass | present | leach vent | 135.9019 kg/d | — |
| IA-LEACH-HOP | LEACH_CSTR_1 | HOPPER | S/L | mass | present | returned solids | 35.355 kg/d | — |
| IA-LEACH-ASU | LEACH_CSTR_1 | CRYO_ASU | S/L | mass | present | dissolved gas | 17.44 kg/d | — |
| IA-EW1-H2 | EW_1 | HDR_H2 | S/L | mass | present | hood hydrogen | 1.89 kg/d | — |
| IA-EW2-H2 | EW_2 | HDR_H2 | S/L | mass | present | hood hydrogen | 1.91 kg/d | — |
| IA-EW4-H2 | EW_4 | HDR_H2 | S/L | mass | present | hood hydrogen | 2.82 kg/d | — |
| IA-EW4-N2 | EW_4 | HDR_N2 | S/L | mass | present | sweep nitrogen | 1.0 kg/d | — |
| IA-O2-MAKE | CRYO_O2 | HDR_O2 | S/L | mass | present | oxygen makeup | 0.0 kg/d | — |
| IA-DIG-FIX | DIGESTER | NUTRIENT_DOSE | S/L | mass | present | digestate trim | 0.0 kg/d | — |
| IA-FC-FIX | FUEL_CELL | NOX_SCRUB | S/L | mass | present | cell water | 0.0 kg/d | — |
| IA-COMP-FIX | COMPOST | HDR_CO2 | S/L | mass | present | compost CO2 trim | 0.0 kg/d | — |
| IA-AHU-FIX | CRYO_N2 | CRYO_AHU | S/L | mass | present | handler makeup | 0.0 kg/d | — |
| IA-LEACH-H2 | LEACH_CSTR_1 | HDR_H2 | S/L | mass | present | dissolved hydrogen | 0.0 kg/d | — |
| IA-FC-LEACH | FUEL_CELL | LEACH_CSTR_1 | L | mass | present | cell water | 0.5471 kg/d | — |
| IA-NOX-BOARD | NOX_SCRUB | BOARD_MILL | S | mass | present | recovered carbon | 1.65 kg/d | — |
| IA-SUGAR-ABE | LIGNO_PRE | ABE | L | mass | present | sugar to ABE | 0.64 kg/d | — |
| IA-ETOH | ETOH_STILL | ALD | L | mass | present | ethanol | 0.2 kg/d | — |
| IA-ETOH-AC | ETOH_STILL | ACETOX | L | mass | present | ethanol to acetic | 0.16 kg/d | — |
| IA-ETOH-SOL | YEAST | WS_SOLV | L | mass | present | retired direct solvent edge | 0.0 kg/d | — |
| IA-YEAST-CO2 | YEAST | HDR_CO2 | L | mass | present | fermentation CO2 | 0.44 kg/d | — |
| IA-STILL | YEAST | DIGESTER | L | mass | present | stillage | 0.1 kg/d | — |
| IA-BUOH | ABE | BUCL | L | mass | present | n-butanol | 0.0 kg/d | — |
| IA-ACETONE | ABE | WS_SOLV | L | mass | present | acetone | 0.06 kg/d | — |
| IA-ABE-ETOH | ABE | WS_SOLV | L | mass | present | ABE ethanol | 0.02 kg/d | — |
| IA-ABE-CO2 | ABE | HDR_CO2 | L | mass | present | ABE CO2 | 0.25 kg/d | — |
| IA-ABE-STILL | ABE | DIGESTER | L | mass | present | ABE stillage | 0.18 kg/d | — |
| IA-AC-O2 | HDR_O2 | ACETOX | L | mass | present | oxygen to acetic acid | 0.11 kg/d | — |
| IA-ACOH | ACETOX | ACEX | L | mass | present | acetic acid | 0.2064416526032877 kg/d | — |
| IA-AC-H2O | ACETOX | ROOF_TANK | L | mass | present | oxidation water | 0.061930433152072 kg/d | — |
| IA-ALD | ALD | GLYOXAL | L | mass | present | acetaldehyde | 0.19124791074258177 kg/d | — |
| IA-ALD-H2 | ALD | HDR_H2 | L | mass | present | dehydrogenation hydrogen | 0.00875208925741822 kg/d | — |
| IA-GLX | GLYOXAL | IMID | L | mass | present | glyoxal | 0.25195250602357333 kg/d | — |
| IA-GLX-NOX | GLYOXAL | NOX_SCRUB | L | mass | present | no NOx from this oxidation | 0.0 kg/d | — |
| IA-MEOH-FORM | MEOH_TANK | FORM | L | mass | present | methanol to formaldehyde | 0.0 kg/d | — |
| IA-CH2O | FORM | IMID | L | mass | present | formaldehyde | 0.0 kg/d | — |
| IA-FORM-H2O | FORM | ROOF_TANK | L | mass | present | formaldehyde water | 0.06746769864552775 kg/d | — |
| IA-MEOH-MEAM | MEOH_TANK | MEAM | L | mass | present | methanol to methylamine | 0.04 kg/d | — |
| IA-NH3-MEAM | WS_AMMONIA | MEAM | L | mass | present | ammonia to methylamine | 0.03 kg/d | — |
| IA-MEAM | MEAM | IMID | L | mass | present | methylamine | 0.038771612258910175 kg/d | — |
| IA-NH3-IMID | WS_AMMONIA | IMID | L | mass | present | ammonia to imidazole | 0.02 kg/d | — |
| IA-IMID | IMID | QUAT | L | mass | present | 1-methylimidazole | 0.09641947037754683 kg/d | — |
| IA-IMID-H2O | IMID | ROOF_TANK | L | mass | present | condensation water | 0.0634666196935001 kg/d | — |
| IA-HCL-BU | BMED_ACID | BUCL | L | mass | present | HCl to chlorobutane | 0.05 kg/d | — |
| IA-BUCL | BUCL | QUAT | L | mass | present | 1-chlorobutane | 0.1269488178177629 kg/d | — |
| IA-BUCL-H2O | BUCL | ROOF_TANK | L | mass | present | chlorination water | 0.024706511602391793 kg/d | — |
| IA-BMIM | QUAT | ACEX | L | mass | present | [Bmim]Cl | 0.2051224238153955 kg/d | — |
| IA-QUAT-H2O | QUAT | ROOF_TANK | L | mass | present | no quaternization water | 0.0 kg/d | — |
| IA-IL | ACEX | LIGNO_PRE | L | mass | present | [Bmim]OAc to the pretreat | 0.23282954612177795 kg/d | — |
| IA-IL-BRINE | ACEX | LEACH_CSTR_1 | L | mass | present | exchange coproducts and unused feed | 0.17873453029690525 kg/d | — |
| IA-NH3-NIT | WS_AMMONIA | HNO3 | L | mass | present | ammonia to nitric | 0.2 kg/d | — |
| IA-O2-NIT | HDR_O2 | HNO3 | L | mass | present | oxygen to nitric | 0.5 kg/d | — |
| IA-HNO3 | HNO3 | WS_NITRIC | L | mass | present | nitric acid | 0.6 kg/d | — |
| IA-NIT-H2O | HNO3 | ROOF_TANK | L | mass | present | absorber water | 0.1 kg/d | — |
| IA-PHOS-DOPE | WS_PHOS | WS_DOPE | L | mass | present | phosphate to dopant | 0.01 kg/d | — |
| IA-SOLV-WB | WS_SOLV | WET_BENCH | L | mass | present | ethanol and acetone | 0.2099725848244856 kg/d | — |
| IA-BSFL-FISH | BSFL | FISH | S | mass | present | larvae | 0.4 kg/d | — |
| IA-BSFL-HEN | BSFL | CHICKENS | S | mass | present | larvae | 0.3 kg/d | — |
| IA-BSFL-FRASS | BSFL | COMPOST | S | mass | present | frass | 2.28 kg/d | — |
| IA-WEED-FISH | DUCKWEED | FISH | S | mass | present | duckweed | 0.5 kg/d | — |
| IA-WEED-HEN | DUCKWEED | CHICKENS | S | mass | present | duckweed | 0.2 kg/d | — |
| IA-WEED-GOAT | DUCKWEED | GOATS | S | mass | present | duckweed | 0.15 kg/d | — |
| IA-WEED-HAB | DUCKWEED | HABITATION | S | mass | present | duckweed reserve | 0.05 kg/d | — |
| IA-BED-WEED | GROW_BED | DUCKWEED | S | mass | present | nutrient water | 0.9 kg/d | — |
| IA-AZOLLA | AZOLLA | FISH | S | mass | present | azolla | 0.1 kg/d | — |
| IA-RICE-AZ | GROW_BED | AZOLLA | S | mass | present | rice-bed spill | 0.1 kg/d | — |
| IA-HEN-EGG | CHICKENS | HABITATION | S | mass | present | eggs | 0.2 kg/d | — |
| IA-HEN-MAN | CHICKENS | WORMS | S | mass | present | manure | 0.3 kg/d | — |
| IA-GOAT-MILK | GOATS | HABITATION | S | mass | present | milk | 0.4 kg/d | — |
| IA-GOAT-MAN | GOATS | WORMS | S | mass | present | manure | 0.3 kg/d | — |
| IA-GOAT-TRIM | GROW_BED | GOATS | S | mass | present | browse | 0.55 kg/d | — |
| IA-FISH-HAB | FISH | HABITATION | S | mass | present | fish | 0.3 kg/d | — |
| IA-FISH-DET | FISH | CRAYFISH | S | mass | present | detritus | 0.2 kg/d | — |
| IA-CRAY-HAB | CRAYFISH | HABITATION | S | mass | present | crayfish | 0.08 kg/d | — |
| IA-CAST | WORMS | GROW_BED | S | mass | present | castings | 0.5 kg/d | — |
| IA-WORM-MAN | WORMS | COMPOST | S | mass | present | worm manure | 0.1 kg/d | — |
| IA-HONEY | BEES | HABITATION | S | mass | present | honey | 0.02 kg/d | — |
| IA-MUSH | MUSHROOM | HABITATION | S | mass | present | oyster mushroom | 0.1 kg/d | — |
| IA-MUSH-SPENT | MUSHROOM | COMPOST | S | mass | present | spent block | 0.1 kg/d | — |
| IA-LIG-MUSH | LIGNO_PRE | MUSHROOM | S | mass | present | spent fiber | 0.2 kg/d | — |
| IA-URINE | HABITATION | COMPOST_TOILET | S | mass | present | urine | 1.2 kg/d | — |
| IA-COVER | NFIX_BED | COMPOST_TOILET | S | mass | present | cover crop | 0.2 kg/d | — |
| IA-TOIL-SOL | COMPOST_TOILET | COMPOST | S | mass | present | covered solids | 0.9 kg/d | — |
| IA-TOIL-URN | COMPOST_TOILET | BIOFILTER | S | mass | present | urine to the biofilter | 1.3 kg/d | — |
| IA-NFIX-RES | NFIX_BED | COMPOST | S | mass | present | legume residue | 0.35 kg/d | — |
| IA-NFIX-FOOD | NFIX_BED | HABITATION | S | mass | present | cowpea and peanut | 0.0 kg/d | — |
| IA-BED-NFIX | GROW_BED | NFIX_BED | S | mass | present | bed spill | 0.75 kg/d | — |
| IA-STRAW | GROW_BED | MUSH_STRAW | S | mass | present | wheat straw | 0.3 kg/d | — |
| IA-OYSTER | MUSH_STRAW | HABITATION | S | mass | present | oyster | 0.12 kg/d | — |
| IA-STRAW-SPENT | MUSH_STRAW | COMPOST_MYC | S | mass | present | spent oyster spawn | 0.18 kg/d | — |
| IA-HW | LIGNO_PRE | MUSH_BLOCK | S | mass | present | hardwood and bran | 0.25 kg/d | — |
| IA-BLOCK-FOOD | MUSH_BLOCK | HABITATION | S | mass | present | shiitake and lion's mane | 0.08 kg/d | — |
| IA-BLOCK-MED | MUSH_BLOCK | HABITATION | S | mass | present | reishi and turkey tail | 0.03 kg/d | — |
| IA-BLOCK-SPENT | MUSH_BLOCK | COMPOST_MYC | S | mass | present | spent blocks | 0.14 kg/d | — |
| IA-AMF-IN | COMPOST | AMF | S | mass | present | compost inoculum | 0.05 kg/d | — |
| IA-AMF-BED | AMF | GROW_BED | S | mass | present | bed inoculum | 0.05 kg/d | — |
| IA-COMP-MYC | COMPOST | COMPOST_MYC | S | mass | present | cooled compost | 2.7 kg/d | — |
| IA-MYC-WORM | COMPOST_MYC | WORMS | S | mass | present | myceliated compost | 3.02 kg/d | — |
| IA-MYC-BED | WORMS | GROW_BED | S | mass | present | finished castings | 2.52 kg/d | — |
| IA-BED-FRUIT | GROW_BED | FRUIT_GUTTER | S | mass | present | irrigation spill | 0.4 kg/d | — |
| IA-FRUIT | FRUIT_GUTTER | HABITATION | S | mass | present | strawberry and fig | 0.25 kg/d | — |
| IA-FRUIT-TRIM | FRUIT_GUTTER | COMPOST | S | mass | present | fruit trim | 0.15 kg/d | — |
| IA-BED-VEG | GROW_BED | VEG_BED | S | mass | present | fish water | 0.8 kg/d | — |
| IA-VEG | VEG_BED | HABITATION | S | mass | present | vegetable harvest | 0 kg/d | — |
| IA-VEG-TRIM | VEG_BED | BSFL | S | mass | present | vegetable trim | 0.25 kg/d | — |
| IA-FISH-OUT | FISH | CLARIFIER | L | mass | present | tank water | 48000 kg/d | — |
| IA-CLAR-BIO | CLARIFIER | BIOFILTER | L | mass | present | clarified water | 47999 kg/d | — |
| IA-CLAR-SOL | CLARIFIER | FISH_SUMP | L | mass | present | settled solids | 1.0 kg/d | — |
| IA-BIO-VEG | BIOFILTER | VEG_BED | L | mass | present | nitrate water | 19393 kg/d | — |
| IA-BIO-WEED | BIOFILTER | DUCKWEED | L | mass | present | nitrate water | 9697 kg/d | — |
| IA-BIO-BED | BIOFILTER | GROW_BED | L | mass | present | nitrate water | 18909 kg/d | — |
| IA-VEG-SUMP | VEG_BED | FISH_SUMP | L | mass | present | bed return | 19393 kg/d | — |
| IA-WEED-SUMP | DUCKWEED | FISH_SUMP | L | mass | present | raceway return | 9697 kg/d | — |
| IA-BED-SUMP | GROW_BED | FISH_SUMP | L | mass | present | bed return | 18909 kg/d | — |
| IA-SUMP-FISH | FISH_SUMP | FISH | L | mass | present | return | 48000 kg/d | — |
| IA-CROP_TOMATO | VEG_BED | CROP_TOMATO | S | mass | present | tomato | 0.12 kg/d | — |
| IA-CROP_TOMATO-HAB | CROP_TOMATO | HABITATION | S | mass | present | harvest | 0.12 kg/d | — |
| IA-CROP_CUCUMBER | VEG_BED | CROP_CUCUMBER | S | mass | present | cucumber | 0.08 kg/d | — |
| IA-CROP_CUCUMBER-HAB | CROP_CUCUMBER | HABITATION | S | mass | present | harvest | 0.08 kg/d | — |
| IA-CROP_PEPPER | VEG_BED | CROP_PEPPER | S | mass | present | pepper | 0.06 kg/d | — |
| IA-CROP_PEPPER-HAB | CROP_PEPPER | HABITATION | S | mass | present | harvest | 0.06 kg/d | — |
| IA-CROP_LETTUCE | VEG_BED | CROP_LETTUCE | S | mass | present | lettuce | 0.08 kg/d | — |
| IA-CROP_LETTUCE-HAB | CROP_LETTUCE | HABITATION | S | mass | present | harvest | 0.08 kg/d | — |
| IA-CROP_SPINACH | VEG_BED | CROP_SPINACH | S | mass | present | spinach | 0.05 kg/d | — |
| IA-CROP_SPINACH-HAB | CROP_SPINACH | HABITATION | S | mass | present | harvest | 0.05 kg/d | — |
| IA-CROP_KALE | VEG_BED | CROP_KALE | S | mass | present | kale | 0.05 kg/d | — |
| IA-CROP_KALE-HAB | CROP_KALE | HABITATION | S | mass | present | harvest | 0.05 kg/d | — |
| IA-CROP_ALLIUM | VEG_BED | CROP_ALLIUM | S | mass | present | onion, garlic, leek | 0.06 kg/d | — |
| IA-CROP_ALLIUM-HAB | CROP_ALLIUM | HABITATION | S | mass | present | harvest | 0.06 kg/d | — |
| IA-CROP_BASIL | VEG_BED | CROP_BASIL | S | mass | present | basil | 0.03 kg/d | — |
| IA-CROP_BASIL-HAB | CROP_BASIL | HABITATION | S | mass | present | harvest | 0.03 kg/d | — |
| IA-CROP_ROSEMARY | VEG_BED | CROP_ROSEMARY | S | mass | present | rosemary | 0.02 kg/d | — |
| IA-CROP_ROSEMARY-HAB | CROP_ROSEMARY | HABITATION | S | mass | present | harvest | 0.02 kg/d | — |
| IA-HAB-WASTE | HABITATION | BSFL | S | mass | present | plate waste | 0.0 kg/d | — |
| IA-CLOSE-0 | BIOFILTER | NUTRIENT_DOSE | S/L | mass | present | biofilter bleed to the nutrient tank | 1.3 kg/d | — |
| IA-CLOSE-1 | LEACH_CSTR_1 | NOX_SCRUB | S/L | mass | present | leach vent to the NOx scrubber | 1.0 kg/d | — |
| IA-CLOSE-2 | COMPOST | GROW_BED | S/L | mass | present | compost return to the bed | 0.7305 kg/d | — |
| IA-CLOSE-3 | WORMS | HDR_N2 | S/L | mass | present | worm bin vent to the nitrogen header | 0.5 kg/d | — |
| IA-CLOSE-4 | FISH | NUTRIENT_DOSE | S/L | mass | present | fish solids liquor to the nutrient tank | 0.5 kg/d | — |
| IA-CLOSE-5 | HOPPER | LIGNO_PRE | S/L | mass | present | hopper fines to the pretreat | 0.45 kg/d | — |
| IA-CLOSE-6 | ACEX | ANIMAL_PEN | S/L | mass | present | withdrawn | 0.0 kg/d | — |
| IA-CLOSE-7 | COMPOST | MEOH_TANK | S/L | mass | present | compost condensate to the methanol tank | 0.3554 kg/d | — |
| IA-CLOSE-8 | MFG_SHOP | DIGESTER | S/L | mass | present | shop scrap to the digester | 0.29 kg/d | — |
| IA-CLOSE-9 | BSFL | HDR_N2 | S/L | mass | present | larvae bin vent to the nitrogen header | 0.1798 kg/d | — |
| IA-CLOSE-10 | LEACH_CSTR_1 | MEOH_FC | S/L | mass | present | leach condensate to the methanol cell | 0.1896 kg/d | — |
| IA-CLOSE-11 | CRAYFISH | IMID | S/L | mass | present | crayfish molt liquor to imidazole makeup | 0.1 kg/d | — |
| IA-CLOSE-12 | BSFL | NUTRIENT_DOSE | S | mass | present | frass liquor to the nutrient tank | 0.0702 kg/d | — |
| IA-CLOSE-13 | QUAT | NUTRIENT_DOSE | L | mass | present | unreacted quaternization feed | 0.01824586437991424 kg/d | — |
| IA-CAST-CLOVER | WORMS | CLOVER | S | mass | present | finished castings | 0.4 kg/d | — |
| IA-CLOVER-CUT | CLOVER | COMPOST | S | mass | present | clover cuttings | 0.38 kg/d | — |
| IA-SEED-CLOVER | CLOVER | SEED_BANK | S | mass | present | clover seed | 0.01 kg/d | — |
| IA-SEED-OUT | SEED_BANK | CLOVER | S | mass | present | seeded clover | 0.01 kg/d | — |
| IA-URN-STR | COMPOST_TOILET | STRUVITE | S | mass | present | urine slip | 0.2 kg/d | — |
| IA-STR-BED | STRUVITE | GROW_BED | S | mass | present | struvite | 0.2 kg/d | — |
| IA-STALK | GROW_BED | ASH | S | mass | present | stalks | 0.0 kg/d | — |
| IA-ASH-BED | ASH | GROW_BED | S | mass | present | ash | 0.3 kg/d | — |
| IA-I-SRC | LEACH_CSTR_1 | IODIDE | S | mass | present | iodide startup | 0.002 kg/d | — |
| IA-I-DOSE | IODIDE | HABITATION | S | mass | present | KI dose | 0.0 kg/d | — |
| IA-NPK-0 | GROW_BED | COMPOST_TOILET | S | mass | present | bed return | 0.2 kg/d | — |
| IA-NPK-1 | COMPOST | WORMS | S | mass | present | castings return | 0.4 kg/d | — |
| IA-E-SUN | CURTAIL | PV_ARRAY | E | energy | present | solar into the array | 128.527 kW | — |
| IA-E-H2 | CURTAIL | FUEL_CELL | E | energy | present | hydrogen into the cell | 4.6 kW | — |
| IA-E-RECT | CURTAIL | EW_1 | E | energy | retired | rectifier into the cell | 0.0 kW | — |
| IA-E-HABIN | CURTAIL | HABITATION | E | energy | present | bus into habitation | 3.0 kW | — |
| IA-E-ABIN | CURTAIL | AFTERBURNER | E | energy | present | fuel into the afterburner | 2.77 kW | — |
| IA-E-GENIN | CURTAIL | BACKUP_GEN | E | energy | present | fuel into the generator | 2.5 kW | — |
| IA-E-BURNIN | CURTAIL | GLASS_BURNOUT | E | energy | present | fuel into the burner | 1.86 kW | — |
| IA-E-ZNIN | CURTAIL | ZNBR2 | E | energy | present | charge into the battery | 1.67 kW | — |
| IA-E-MEIN | CURTAIL | MEOH_FC | E | energy | present | methanol into the cell | 0.87 kW | — |
| IA-E-Q4IN | CURTAIL | CRYO_HX_Q4 | E | energy | present | power into the cold box | 0.54 kW | — |
| IA-E-LEACH | LEACH_CSTR_1 | HEAT_SINK | E | energy | present | leach reject | 14.073 kW | — |
| IA-E-GEO | GEO_ORC | HEAT_SINK | E | energy | present | dry cooler | 11.76 kW | — |
| IA-E-EXP | BOUNDARY_EXPORT | HEAT_SINK | E | energy | present | export reject | 7.15 kW | — |
| IA-E-BED | GROW_BED | HEAT_SINK | E | energy | present | bed reject | 2.25 kW | — |
| IA-E-DIG | GLASS_DIGEST | HEAT_SINK | E | energy | present | digest reject | 4.16 kW | — |
| IA-E-DRY | OIL_DRYER | HEAT_SINK | E | energy | present | dryer reject | 0.6 kW | — |
| IA-E-SUNIN | BOUNDARY_EXPORT | CURTAIL | E | energy | present | solar and fuel in | 146.337 kW | — |
| IA-E-HOUT | HEAT_SINK | BOUNDARY_EXPORT | E | energy | present | heat to air | 50.25 kW | — |
| IA-E-HABOUT | HABITATION | HEAT_SINK | E | energy | present | hab reject | 6.0 kW | — |
| IA-I-RET | HABITATION | IODIDE | E | mass | present | urine iodide return | 0.002 kg/d | — |
| IA-I-MAKE | IODIDE | HABITATION | E | mass | present | KI dose return | 0.002 kg/d | — |
| IA-NFT-IN | BIOFILTER | NFT | L | mass | present | film supply | 200.0 kg/d | — |
| IA-NFT-OUT | NFT | BIOFILTER | L | mass | present | film return | 200.0 kg/d | — |
| IA-MIST-IN | VEG_BED | MISTER | L | mass | present | mister supply | 50.0 kg/d | — |
| IA-MIST-OUT | MISTER | VEG_BED | L | mass | present | mister return | 50.0 kg/d | — |
| IA-DR-IN | GROW_BED | DUAL_ROOT | L | mass | present | correction supply | 20.0 kg/d | — |
| IA-DR-OUT | DUAL_ROOT | GROW_BED | L | mass | present | correction return, not to the tank | 20.0 kg/d | — |
| IA-AZ-IN | GROW_BED | AZOLLA_BED | L | mass | present | rice-bed spill | 0.15 kg/d | — |
| IA-AZ-OUT | AZOLLA_BED | GROW_BED | L | mass | present | azolla residue | 0.15 kg/d | — |
| IA-ETOH-S | YEAST | ETOH_STILL | L | mass | present | ethanol feed | 0.46 kg/d | — |
| IA-ETOH-R | ETOH_STILL | WS_SOLV | L | mass | present | ethanol product | 0.1 kg/d | — |
| IA-BUOH-S | ABE | BUOH_STILL | L | mass | present | butanol feed | 0.13 kg/d | — |
| IA-BUOH-R | BUOH_STILL | BUCL | L | mass | present | butanol product | 0.13 kg/d | — |
| IA-FORM-S | MEOH_TANK | FORM | L | mass | present | methanol to formaldehyde | 0.12 kg/d | — |
| IA-FORM-R | FORM | IMID | L | mass | present | formaldehyde | 0.1124499094937894 kg/d | — |
| IA-PN-S | NFIX_BED | PEANUT | L | mass | present | bed spill | 0.2 kg/d | — |
| IA-PN-R | PEANUT | HABITATION | L | mass | present | peanut | 0.2 kg/d | — |
| IA-SF-S | GROW_BED | SUNFLOWER | L | mass | present | bed spill | 0.3 kg/d | — |
| IA-SF-R | SUNFLOWER | ASH | L | mass | present | stalks | 0.3 kg/d | — |
| IA-SLEEP | HABITATION | HAB_SLEEP | L | mass | present | occupancy | 0.0 kg/d | — |
| IA-SLEEP-R | HAB_SLEEP | HABITATION | L | mass | present | return | 0.0 kg/d | — |
| IA-GAL | HABITATION | HAB_GALLEY | L | mass | present | food | 1.18 kg/d | — |
| IA-GAL-R | HAB_GALLEY | BSFL | L | mass | present | plate waste | 1.18 kg/d | — |
| IA-MED | IODIDE | HAB_MED | L | mass | present | iodide stock | 0.002 kg/d | — |
| IA-MED-R | HAB_MED | HABITATION | L | mass | present | dose | 0.002 kg/d | — |
| IA-WASH | HABITATION | HAB_WASH | L | mass | present | wash water | 80.0 kg/d | — |
| IA-WASH-R | HAB_WASH | GREY_TREAT | L | mass | present | grey | 80.0 kg/d | — |
| IA-LITHO-IN | WAFER_FAB | LITHO_STUB | S | mass | present | spent resist and solvent | 0.9875 kg/d | — |
| IA-LITHO-OUT | LITHO_STUB | OIL_FRAC | S | mass | present | spent resist and solvent | 0.9875 kg/d | — |
| IA-BLOW-IN | PROD_C11_C18 | BLOW_MOLD | S | mass | present | C11-C18 to the mold | 8.4068 kg/d | — |
| IA-BLOW-OUT | BLOW_MOLD | MFG_SHOP | S | mass | present | blown parts | 8.4068 kg/d | — |
| IA-COAT-IN | EW_1 | ELECTRODE_COAT | S | mass | present | nickel sheet to the booth | 0.02 kg/d | — |
| IA-COAT-OUT | ELECTRODE_COAT | EW_1 | S | mass | present | coated anode | 0.02 kg/d | — |
| IA-PV-IN | WS_DOPE | SOLAR_PV_CELL | S | mass | present | dopant concentrate | 0.01 kg/d | — |
| IA-PV-OUT | SOLAR_PV_CELL | WAFER_FAB | S | mass | present | dopant into the wafer fab | 0.01 kg/d | — |
| IA-EXP-IN | CRYO_ASU | EXPANDER | S | mass | present | cold gas | 1575.544287 kg/d | — |
| IA-EXP-OUT | EXPANDER | CRYO_ASU | S | mass | present | expanded gas | 1575.544287 kg/d | — |
| IA-SIC-IN | GLASS_DIGEST | SIC_FURNACE | S | mass | present | silica charge | 0.5 kg/d | — |
| IA-SIC-OUT | SIC_FURNACE | MFG_SHOP | S | mass | present | fired charge | 0.333672 kg/d | — |
| IA-MET-AIR-RET | MET_SCRUB | MET_AHU | G | mass | present | scrubbed metal-aisle air returned to the hall | 71604.0 kg/d | — |
| IA-ACID-AIR-RET | ACID_POLISH_SCRUB | ALK_SCRUBBER | G | mass | present | acid-gas dilution air returned to the alkaline scrubber | 37509.84 kg/d | — |
| CUT-1-OUT | PROD_C5_C10 | BACKUP_GEN | L | mass | present | C5-C10 fuel from the tank | 11.1553 kg/d | — |
| CUT-3-OUT | PROD_C19_C28 | MFG_SHOP | L | mass | present | C19-C28 from the tank | 3.9472 kg/d | — |
| IA-NECTAR | CLOVER | BEES | L | mass | present | clover nectar | 0.02 kg/d | — |
| IA-SIC-C | OIL_PYRO | SIC_FURNACE | L | mass | present | carbon reagent | 0.29986 kg/d | — |
| IA-SIC-CO | SIC_FURNACE | AFTERBURNER | L | mass | present | carbon monoxide | 0.466188 kg/d | — |
| IA-SIC-RET | NUTRIENT_DOSE | LEACH_CSTR_1 | L | mass | present | compost carbon returned to the leach | 0.466188 kg/d | — |
| IA-CRAY-DET | CRAYFISH | COMPOST | S | mass | present | unassimilated detritus | 0.02 kg/d | — |
| IA-IL-SPENT | LIGNO_PRE | DIGESTER | L | mass | present | spent [Bmim]OAc | 0.23282954612177795 kg/d | — |
| IA-GLX-O2 | HDR_O2 | GLYOXAL | L | mass | present | oxygen to glyoxal | 0.13891336907681956 kg/d | — |
| IA-GLX-H2O | GLYOXAL | ROOF_TANK | L | mass | present | glyoxal water | 0.078208773795828 kg/d | — |
| IA-FORM-O2 | HDR_O2 | FORM | L | mass | present | oxygen to formaldehyde | 0.059917608139317145 kg/d | — |
| IA-MEAM-H2O | MEAM | ROOF_TANK | L | mass | present | methylamine water | 0.02248923288184258 kg/d | — |
| IA-NH3-RET | MEAM | WS_AMMONIA | L | mass | present | unreacted ammonia | 0.008739154859247238 kg/d | — |
| IA-AC-EX | ACETOX | WS_SOLV | L | mass | present | unreacted ethanol | 0.0016279142446402883 kg/d | — |
| IA-BUCL-EX | BUCL | WS_SOLV | L | mass | present | unreacted butanol | 0.028344670579845327 kg/d | — |
| IA-IMID-EX | IMID | NUTRIENT_DOSE | L | mass | present | unreacted reagents and molt liquor | 0.36328793770522605 kg/d | — |
| IA-NIT-VENT | WS_NITRIC | NOX_SCRUB | G | mass | present | nitric tank vent | 0.0 kg/d | — |
| IA-HNO3-VENT | HNO3 | NOX_SCRUB | G | mass | present | nitric absorber tail gas | 0.0 kg/d | — |
| IA-FLUE-QUENCH | ROOF_TANK | FLUE_KO | L | mass | present | flue quench water | 24.31 kg/d | — |
| IA-PEROX-H2O | ROOF_TANK | WS_PEROX | L | mass | present | peroxide dilution water | 2.824 kg/d | — |
| IA-BASE-PPT | EVAP_BASE | LEACH_CSTR_1 | L | mass | present | NaOH 20 wt% to hydroxide precipitation of leached Al, Ca, Mg, Fe (class A) | 482.2861 kg/d | — |
| S17-EW | SOL_ARK_60K | RECT_EW | E | elec | present | 480 V AC | 38.6629 kW | — |
| S17-BMED | SOL_ARK_60K | BMED_ACID | E | elec | present | 480 V AC | 26.9276 kW | — |
| IA-RECT-EW-LOSS | RECT_EW | HEAT_SINK | E | energy | present | heat | 7.7326 kW | — |
| IA-DC-EW_1 | RECT_EW | EW_1 | E | elec | present | DC bus bar | 5.9909 kW | — |
| IA-EWQ-EW_1 | EW_1 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 1.4189 kW | — |
| IA-DC-EW_2 | RECT_EW | EW_2 | E | elec | present | DC bus bar | 5.9929 kW | — |
| IA-EWQ-EW_2 | EW_2 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 5.9929 kW | — |
| IA-DC-EW_3 | RECT_EW | EW_3 | E | elec | present | DC bus bar | 2.2495 kW | — |
| IA-EWQ-EW_3 | EW_3 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 2.2495 kW | — |
| IA-DC-EW_4 | RECT_EW | EW_4 | E | elec | present | DC bus bar | 0.4853 kW | — |
| IA-EWQ-EW_4 | EW_4 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 0.4853 kW | — |
| IA-DC-EW_5 | RECT_EW | EW_5 | E | elec | present | DC bus bar | 0.5023 kW | — |
| IA-EWQ-EW_5 | EW_5 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 0.5023 kW | — |
| IA-DC-EW_6 | RECT_EW | EW_6 | E | elec | present | DC bus bar | 0.5474 kW | — |
| IA-EWQ-EW_6 | EW_6 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 0.5474 kW | — |
| IA-DC-EW_7 | RECT_EW | EW_7 | E | elec | present | DC bus bar | 7.1187 kW | — |
| IA-EWQ-EW_7 | EW_7 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 7.1187 kW | — |
| IA-DC-EW_8 | RECT_EW | EW_8 | E | elec | present | DC bus bar | 0.5053 kW | — |
| IA-EWQ-EW_8 | EW_8 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 0.5053 kW | — |
| IA-DC-EW_9 | RECT_EW | EW_9 | E | elec | present | DC bus bar | 7.538 kW | — |
| IA-EWQ-EW_9 | EW_9 | HEAT_SINK | E | energy | present | cell heat and deposit enthalpy | 7.538 kW | — |
| IA-BMED-03-TRIM | LEACH_CSTR_1 | GEO_GHEX | E | thermal | present | trim cooler heat from IA-BMED-03 (to BMED_ACID) | 0.78 kW | — |
| IA-BMED-04-TRIM | LEACH_CSTR_1 | GEO_GHEX | E | thermal | present | trim cooler heat from IA-BMED-04 (to BMED_BASE) | 1.027 kW | — |
| IA-GHEX-REJ | GEO_GHEX | HEAT_SINK | E | energy | present | heat to ground | 1.807 kW | — |
| IA-LEACH-VCD | LEACH_CSTR_1 | VCD_TRAIN | L | mass | present | leach liquor water bleed to vapour-compression distillation | 123.296 kg/d | — |
| S49P | H2_PURIFIER | FUEL_CELL | G | mass | present | H2 fuel | 5.028752089257418 kg/d | — |
| SF-ALK_SCRUBBER | SOL_ARK_60K | ALK_SCRUBBER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.4 kW | — |
| SQ-ALK_SCRUBBER | ALK_SCRUBBER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.4 kW | — |
| SF-BMED_UPW_POLISH | SOL_ARK_60K | BMED_UPW_POLISH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.038 kW | — |
| SQ-BMED_UPW_POLISH | BMED_UPW_POLISH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.038 kW | — |
| SF-CRYO_H2 | SOL_ARK_60K | CRYO_H2 | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.565 kW | — |
| SQ-CRYO_H2 | CRYO_H2 | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.565 kW | — |
| SF-GEO_HP | SOL_ARK_60K | GEO_HP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SQ-GEO_HP | GEO_HP | HEAT_SINK | E | energy | present | electrical input leaving as heat | 2.0 kW | — |
| SF-GLASS_DIGEST | SOL_ARK_60K | GLASS_DIGEST | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.5 kW | — |
| SQ-GLASS_DIGEST | GLASS_DIGEST | HEAT_SINK | E | energy | present | electrical input leaving as heat | 1.5 kW | — |
| SF-H2_DRYER | SOL_ARK_60K | H2_DRYER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-H2_DRYER | H2_DRYER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-LEACH_CSTR_1 | SOL_ARK_60K | LEACH_CSTR_1 | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SQ-LEACH_CSTR_1 | LEACH_CSTR_1 | HEAT_SINK | E | energy | present | electrical input leaving as heat | 2.0 kW | — |
| SF-MEOH_SYNTH | SOL_ARK_60K | MEOH_SYNTH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.5 kW | — |
| SQ-MEOH_SYNTH | MEOH_SYNTH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.5 kW | — |
| SF-MFG_SHOP | SOL_ARK_60K | MFG_SHOP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 3.98 kW | — |
| SQ-MFG_SHOP | MFG_SHOP | HEAT_SINK | E | energy | present | electrical input leaving as heat | 3.98 kW | — |
| SF-NUTRIENT_DOSE | SOL_ARK_60K | NUTRIENT_DOSE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-NUTRIENT_DOSE | NUTRIENT_DOSE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-WAFER_FAB | SOL_ARK_60K | WAFER_FAB | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 2.0 kW | — |
| SQ-WAFER_FAB | WAFER_FAB | HEAT_SINK | E | energy | present | electrical input leaving as heat | 2.0 kW | — |
| SF-WET_BENCH | SOL_ARK_60K | WET_BENCH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.0 kW | — |
| SQ-WET_BENCH | WET_BENCH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 1.0 kW | — |
| SF-LITHO_STUB | SOL_ARK_60K | LITHO_STUB | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-LITHO_STUB | LITHO_STUB | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-ELECTRODE_COAT | SOL_ARK_60K | ELECTRODE_COAT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-ELECTRODE_COAT | ELECTRODE_COAT | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-BLOW_MOLD | SOL_ARK_60K | BLOW_MOLD | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.5 kW | — |
| SQ-BLOW_MOLD | BLOW_MOLD | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.5 kW | — |
| SF-SOLAR_PV_CELL | SOL_ARK_60K | SOLAR_PV_CELL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-SOLAR_PV_CELL | SOLAR_PV_CELL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-ANIMAL_PEN | SOL_ARK_60K | ANIMAL_PEN | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-ANIMAL_PEN | ANIMAL_PEN | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-COMPOST | SOL_ARK_60K | COMPOST | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-COMPOST | COMPOST | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-DIGESTER | SOL_ARK_60K | DIGESTER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.4 kW | — |
| SQ-DIGESTER | DIGESTER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.4 kW | — |
| SF-EMETH | SOL_ARK_60K | EMETH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.5 kW | — |
| SQ-EMETH | EMETH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.5 kW | — |
| SF-LIGNO_PRE | SOL_ARK_60K | LIGNO_PRE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.8 kW | — |
| SQ-LIGNO_PRE | LIGNO_PRE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.8 kW | — |
| SF-BOARD_MILL | SOL_ARK_60K | BOARD_MILL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 1.0 kW | — |
| SQ-BOARD_MILL | BOARD_MILL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 1.0 kW | — |
| SF-HTC | SOL_ARK_60K | HTC | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.6 kW | — |
| SQ-HTC | HTC | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.6 kW | — |
| SF-CRYO_ASU | SOL_ARK_60K | CRYO_ASU | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 18.0 kW | — |
| SQ-CRYO_ASU | CRYO_ASU | HEAT_SINK | E | energy | present | electrical input leaving as heat | 18.0 kW | — |
| SF-CRYO_HE | SOL_ARK_60K | CRYO_HE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CRYO_HE | CRYO_HE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-CRYO_NE | SOL_ARK_60K | CRYO_NE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CRYO_NE | CRYO_NE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-CRYO_KR | SOL_ARK_60K | CRYO_KR | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CRYO_KR | CRYO_KR | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-CRYO_XE | SOL_ARK_60K | CRYO_XE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CRYO_XE | CRYO_XE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-CRYO_AR | SOL_ARK_60K | CRYO_AR | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CRYO_AR | CRYO_AR | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-YEAST | SOL_ARK_60K | YEAST | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-YEAST | YEAST | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-ABE | SOL_ARK_60K | ABE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-ABE | ABE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-ACETOX | SOL_ARK_60K | ACETOX | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-ACETOX | ACETOX | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-ALD | SOL_ARK_60K | ALD | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-ALD | ALD | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-GLYOXAL | SOL_ARK_60K | GLYOXAL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-GLYOXAL | GLYOXAL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-FORM | SOL_ARK_60K | FORM | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-FORM | FORM | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-MEAM | SOL_ARK_60K | MEAM | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-MEAM | MEAM | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-IMID | SOL_ARK_60K | IMID | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-IMID | IMID | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-QUAT | SOL_ARK_60K | QUAT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-QUAT | QUAT | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-ACEX | SOL_ARK_60K | ACEX | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-ACEX | ACEX | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-HNO3 | SOL_ARK_60K | HNO3 | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-HNO3 | HNO3 | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-BUCL | SOL_ARK_60K | BUCL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-BUCL | BUCL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-BSFL | SOL_ARK_60K | BSFL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-BSFL | BSFL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-DUCKWEED | SOL_ARK_60K | DUCKWEED | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-DUCKWEED | DUCKWEED | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-WORMS | SOL_ARK_60K | WORMS | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-WORMS | WORMS | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-BEES | SOL_ARK_60K | BEES | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-BEES | BEES | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-CHICKENS | SOL_ARK_60K | CHICKENS | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-CHICKENS | CHICKENS | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-GOATS | SOL_ARK_60K | GOATS | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-GOATS | GOATS | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-FISH | SOL_ARK_60K | FISH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-FISH | FISH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-CRAYFISH | SOL_ARK_60K | CRAYFISH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-CRAYFISH | CRAYFISH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-AZOLLA | SOL_ARK_60K | AZOLLA | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-AZOLLA | AZOLLA | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-MUSHROOM | SOL_ARK_60K | MUSHROOM | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.1 kW | — |
| SQ-MUSHROOM | MUSHROOM | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.1 kW | — |
| SF-COMPOST_TOILET | SOL_ARK_60K | COMPOST_TOILET | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-COMPOST_TOILET | COMPOST_TOILET | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-NFIX_BED | SOL_ARK_60K | NFIX_BED | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-NFIX_BED | NFIX_BED | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-MUSH_STRAW | SOL_ARK_60K | MUSH_STRAW | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.15 kW | — |
| SQ-MUSH_STRAW | MUSH_STRAW | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.15 kW | — |
| SF-MUSH_BLOCK | SOL_ARK_60K | MUSH_BLOCK | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.15 kW | — |
| SQ-MUSH_BLOCK | MUSH_BLOCK | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.15 kW | — |
| SF-AMF | SOL_ARK_60K | AMF | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.15 kW | — |
| SQ-AMF | AMF | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.15 kW | — |
| SF-COMPOST_MYC | SOL_ARK_60K | COMPOST_MYC | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-COMPOST_MYC | COMPOST_MYC | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-FRUIT_GUTTER | SOL_ARK_60K | FRUIT_GUTTER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.4 kW | — |
| SQ-FRUIT_GUTTER | FRUIT_GUTTER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.4 kW | — |
| SF-VEG_BED | SOL_ARK_60K | VEG_BED | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.4 kW | — |
| SQ-VEG_BED | VEG_BED | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.4 kW | — |
| SF-CLARIFIER | SOL_ARK_60K | CLARIFIER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-CLARIFIER | CLARIFIER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-BIOFILTER | SOL_ARK_60K | BIOFILTER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-BIOFILTER | BIOFILTER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-FISH_SUMP | SOL_ARK_60K | FISH_SUMP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-FISH_SUMP | FISH_SUMP | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-CROP_TOMATO | SOL_ARK_60K | CROP_TOMATO | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_TOMATO | CROP_TOMATO | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_CUCUMBER | SOL_ARK_60K | CROP_CUCUMBER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_CUCUMBER | CROP_CUCUMBER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_PEPPER | SOL_ARK_60K | CROP_PEPPER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_PEPPER | CROP_PEPPER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_LETTUCE | SOL_ARK_60K | CROP_LETTUCE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_LETTUCE | CROP_LETTUCE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_SPINACH | SOL_ARK_60K | CROP_SPINACH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_SPINACH | CROP_SPINACH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_KALE | SOL_ARK_60K | CROP_KALE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_KALE | CROP_KALE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_ALLIUM | SOL_ARK_60K | CROP_ALLIUM | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_ALLIUM | CROP_ALLIUM | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_BASIL | SOL_ARK_60K | CROP_BASIL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_BASIL | CROP_BASIL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CROP_ROSEMARY | SOL_ARK_60K | CROP_ROSEMARY | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-CROP_ROSEMARY | CROP_ROSEMARY | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| SF-CLOVER | SOL_ARK_60K | CLOVER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-CLOVER | CLOVER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-SEED_BANK | SOL_ARK_60K | SEED_BANK | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-SEED_BANK | SEED_BANK | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-STRUVITE | SOL_ARK_60K | STRUVITE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-STRUVITE | STRUVITE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-ASH | SOL_ARK_60K | ASH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-ASH | ASH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-IODIDE | SOL_ARK_60K | IODIDE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.2 kW | — |
| SQ-IODIDE | IODIDE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.2 kW | — |
| SF-NFT | SOL_ARK_60K | NFT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-NFT | NFT | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-MISTER | SOL_ARK_60K | MISTER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-MISTER | MISTER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-DUAL_ROOT | SOL_ARK_60K | DUAL_ROOT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-DUAL_ROOT | DUAL_ROOT | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-AZOLLA_BED | SOL_ARK_60K | AZOLLA_BED | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-AZOLLA_BED | AZOLLA_BED | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-ETOH_STILL | SOL_ARK_60K | ETOH_STILL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-ETOH_STILL | ETOH_STILL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-BUOH_STILL | SOL_ARK_60K | BUOH_STILL | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-BUOH_STILL | BUOH_STILL | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-PEANUT | SOL_ARK_60K | PEANUT | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-PEANUT | PEANUT | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-SUNFLOWER | SOL_ARK_60K | SUNFLOWER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-SUNFLOWER | SUNFLOWER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-HAB_SLEEP | SOL_ARK_60K | HAB_SLEEP | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-HAB_SLEEP | HAB_SLEEP | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-HAB_GALLEY | SOL_ARK_60K | HAB_GALLEY | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-HAB_GALLEY | HAB_GALLEY | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-HAB_MED | SOL_ARK_60K | HAB_MED | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-HAB_MED | HAB_MED | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-HAB_WASH | SOL_ARK_60K | HAB_WASH | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-HAB_WASH | HAB_WASH | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-EXPANDER | SOL_ARK_60K | EXPANDER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.614 kW | — |
| SQ-EXPANDER | EXPANDER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.614 kW | — |
| SF-SIC_FURNACE | SOL_ARK_60K | SIC_FURNACE | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.3 kW | — |
| SQ-SIC_FURNACE | SIC_FURNACE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.3 kW | — |
| SF-H2_PURIFIER | SOL_ARK_60K | H2_PURIFIER | E | elec | present | 480 V or 208/120 V AC (bus per AQS-ELEC-002) | 0.05 kW | — |
| SQ-H2_PURIFIER | H2_PURIFIER | HEAT_SINK | E | energy | present | electrical input leaving as heat | 0.05 kW | — |
| IA-EVAP_ACID-FEED | BMED_ACID | EVAP_ACID | L | mass | present | HCl 2 M from BMED | 1243.3443 kg/d | — |
| IA-EVAP_ACID-COND | EVAP_ACID | BMED_ACID | L | mass | present | evaporator condensate return (BMED water make-up) | 803.8221 kg/d | — |
| SF-EVAP_ACID | SOL_ARK_60K | EVAP_ACID | E | elec | present | 480 V AC | 2.4115 kW | — |
| SQ-EVAP_ACID | EVAP_ACID | HEAT_SINK | E | energy | present | electrical input leaving as heat | 2.4115 kW | — |
| IA-EVAP_BASE-FEED | BMED_BASE | EVAP_BASE | L | mass | present | NaOH 2 M from BMED | 1301.7169 kg/d | — |
| IA-EVAP_BASE-COND | EVAP_BASE | BMED_BASE | L | mass | present | evaporator condensate return (BMED water make-up) | 799.1937 kg/d | — |
| SF-EVAP_BASE | SOL_ARK_60K | EVAP_BASE | E | elec | present | 480 V AC | 2.3976 kW | — |
| SQ-EVAP_BASE | EVAP_BASE | HEAT_SINK | E | energy | present | electrical input leaving as heat | 2.3976 kW | — |
| IA-NAOH-MU | NORTH_DOCK | EVAP_BASE | S | mass | present | purchased NaOH flake make-up | 5.0593 kg/d | — |
| IA-NA-PURGE | LEACH_CSTR_1 | NORTH_DOCK | L | mass | present | sodium salt purge equal to the make-up mass | 5.0593 kg/d | — |
