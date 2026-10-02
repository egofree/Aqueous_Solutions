# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev G (`plant_flow_graph.json`)
Generated: 2026-10-02
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.
Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.

| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |
|---|---|---|---|---|---|---|---|---|
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 95.0 kg/d | — |
| S02 | CRYO_O2 | HDR_O2 | G | mass | present | O2 | 3.4 kg/d | — |
| S03 | CRYO_N2 | WAFER_FAB | G | mass | present | N2 | 1.5 kg/d | wp_true_closure |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | 2.0 kg/d | wp_true_closure |
| S05 | H2_DRYER | CRYO_H2 | G | mass | present | process H2 | 4.8 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | 1.5 kW | wp_true_closure |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 42.0 kg/d | — |
| S09 | BMED_UPW_POLISH | WET_BENCH | L | mass | present | HCl/NaOH | 0.6 kg/d | wp_true_closure |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 10.0 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | NUTRIENT_DOSE | L/S | mass | present | grey/solids | 110.0 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | present | condensate | 15.0 kg/d | absent_from_candidate_mvs,wp_l2_filled |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 4.2 kg/d | — |
| S15 | GROW_BED | HDR_O2 | G | mass | present | photosynthetic O2 | 1.4545454545454546 kg/d | wp_true_closure |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.0 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 50.0 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | captured CO2/air | 15.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | 0.5 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S20 | GROW_BED | LOAD_AGG | E | elec | present | load | 5.0 kW | wp_true_closure |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 95.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | 0.0 kg/d | wp_true_closure |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | 0.0 kg/d | wp_true_closure |
| S24 | H2_DRYER | BOUNDARY_EXPORT | G | mass | present | H2 relief contingency | 0.0 kg/d | wp_true_closure,wp_true_closure_residuals |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | present | VCD distillate | 145.0 kg/d | wp_l2_filled,wp_true_closure_residuals |
| S26 | REMIN | HABITATION | L | mass | present | potable | 10.0 kg/d | wp_l2_filled |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | 15.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | present | VCD brine | 14.3 kg/d | wp_l2_filled,wp_true_closure_residuals |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | present | treated grey | 110.0 kg/d | absent_from_candidate_mvs,wp_l2_filled |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | 8.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | 1.5 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | 3.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | 3.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO₃ / H₃PO₄ etch suite | 1.25 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | 0.3 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | 0.01 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | 3.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S38 | LITHO_STUB | WET_BENCH | L | mass | present | resist / solvent waste | 0.006 kg/d | wp_l2_filled |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry, solvent, photoresist sludge | 12.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S40 | ROOF_TANK | TERRACE_IRRIG | L | mass | present | clean overflow | 0.0 kg/d | wp_true_closure |
| S41 | TERRACE_IRRIG | CATCH_TANK | L | mass | present | rain + S40 return | 20.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S42 | TERRACE_IRRIG | GREY_TREAT | L | mass | present | dilute nutrient drain | 5.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | 3.0 kW | absent_from_candidate_mvs,wp_true_closure |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | 3.0 kW | absent_from_candidate_mvs,wp_true_closure |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | H2 fuel | 0.72 kg/d | wp_true_closure_residuals |
| S46 | BACKUP_GEN | GREY_TREAT | G/L | mass | present | H₂O + NOx class | 0.2 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 2.5 kW | — |
| S48 | GEO_ORC | SOL_ARK_60K | E | elec | present | ORC AC | 0.0 kW | wp_l2_filled |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 3.84 kg/d | wp_true_closure_residuals |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 4.0 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | present | PEM product H2O | 34.3 kg/d | wp_l2_filled,wp_true_closure_residuals |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | 1.0 kW | absent_from_candidate_mvs,wp_true_closure |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | 0.5 kW | absent_from_candidate_mvs,wp_true_closure |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | 1.0 kW | absent_from_candidate_mvs,intentional_self_loop,wp_true_closure |
| S56 | CRYO_AHU | BOUNDARY_EXPORT | G | mass | present | non-condensable residual after KO | 0.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | 10.0 kg/d | absent_from_candidate_mvs,wp_true_closure,wp_true_closure_residuals |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | 9.0 kg/d | absent_from_candidate_mvs,wp_true_closure,wp_true_closure_residuals |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | 5.5 kg/d | absent_from_candidate_mvs,wp_true_closure,wp_true_closure_residuals |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | 3.5 kg/d | absent_from_candidate_mvs,wp_true_closure,wp_true_closure_residuals |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | 2.0 kg/d | absent_from_candidate_mvs,wp_true_closure,wp_true_closure_residuals |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | 200.0 m3/h | absent_from_candidate_mvs,wp_true_closure |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | 0.5 kW | absent_from_candidate_mvs,wp_true_closure |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER | ACID_POLISH_SCRUB | G | mass | present | acid-gas residual | 1500.0 m3/h | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | 2.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S67 | AFTERBURNER_FLUE | CRYO_CO2 | G | mass | present | captured CO₂ + condensables | 5.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S68 | CRYO_AHU | S13_CLASS_TREAT | L | mass | present | flue / AHU condensate | 2.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S69 | ZNBR2 | ZNBR2 | L | ess | present | Br⁻ makeup after ORP | 0.0 kg/d | absent_from_candidate_mvs,intentional_self_loop,wp_true_closure |
| S70 | CRYO_AHU_COND_CONDENSABLE | CRYO_H2 | G/L | mass | present | boil-off / purge condensables | 0.1 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | 200.0 m3/h | absent_from_candidate_mvs,wp_true_closure |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | fines + scrub liquor / organic mist | 1.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 6.9 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 0.24 kg/d | wp_true_closure_residuals |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 5.0 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | ess | present | MeOH fuel | 5.0 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | 0.5 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | 2.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 1.0 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | 0.3 kW | absent_from_candidate_mvs,wp_true_closure |
| S81 | MEOH_FC | GREY_TREAT | L | mass | present | product / process H₂O | 1.5 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | 1.0 kg/d | absent_from_candidate_mvs,wp_true_closure |
| S08G | GLASS_DIGEST | BOUNDARY_EXPORT | S | mass | present | glass/ceramic goods | 30.0 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox,wp_true_closure_residuals |
| S14X | GROW_BED | BOUNDARY_EXPORT | S | mass | present | food surplus export | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox,wp_true_closure_residuals |
| IA-EW-01 | EW_1 | EW_2 | L | mass | present | EW stage overflow/advance | 140.0 kg/d | intra_aisle,full_depth_now,ew_cascade undrawn S##,wp_l2_filled |
| IA-EW-02 | EW_2 | EW_9 | L | mass | present | EW cascade mid→last (proxy; stages 3–8 not exploded) | 130.0 kg/d | intra_aisle,full_depth_now,ew_cascade undrawn S##,wp_l2_filled |
| IA-EW-03 | EW_9 | POLISH_BANK | L | mass | present | EW → polish / precip | 120.0 kg/d | intra_aisle,full_depth_now,ew_cascade undrawn S##,wp_l2_filled |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | present | CSTR → EW-1 feed | 150.0 kg/d | intra_aisle,full_depth_now,ew_cascade undrawn S##,wp_l2_filled |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | present | Float/sink liquor return | 20.0 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD,wp_l2_filled |
| IA-WET-C29-01 | C29_RECYCLE | LEACH_CSTR_1 | L | mass | present | C29-class recycle | 15.0 kg/d | intra_aisle,full_depth_now,STR scope-out; ID was TBD,wp_l2_filled |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | present | Continuous recycle liquor | 25.0 kg/d | intra_aisle,full_depth_now,continuous_recycling_pfd,wp_l2_filled |
| IA-REC-Q3 | CONTINUOUS_RECYCLE | Q4_BUS | E | thermal | present | Heat ladder Q3 residual (ghost to Q4 bus for EFD-thermal) | 1.0 kW | intra_aisle,full_depth_now,heat ladder unlabeled,wp_l2_filled |
| IA-BMED-01 | BMED_ACID | BMED_UPW_POLISH | L | mass | present | BMED acid product internal | 5.0 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled,wp_l2_filled |
| IA-BMED-02 | BMED_BASE | BMED_UPW_POLISH | L | mass | present | BMED base product internal | 5.0 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled,wp_l2_filled |
| IA-BMED-03 | CRU | BMED_ACID | L | mass | present | CRU → BMED acid regen loop | 8.0 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled,wp_l2_filled |
| IA-BMED-04 | CRU | BMED_BASE | L | mass | present | CRU → BMED base regen loop | 8.0 kg/d | intra_aisle,full_depth_now,bmed_regen unlabeled,wp_l2_filled |
| IA-POL-01 | POLISH_BANK | BMED_UPW_POLISH | L | mass | present | Polish bank → UPW polish | 50.0 kg/d | intra_aisle,full_depth_now,polish_bank unlabeled,wp_l2_filled |
| IA-POL-02 | POLISH_BANK | LEACH_CSTR_1 | L | mass | present | polish raffinate / solids return | 10.0 kg/d | wp_l2_filled,was_self_loop_resolved |
| IA-GLASS-01 | GLASS_RINSE | GLASS_BURNOUT | L | mass | present | Glass rinse → burnout | 30.0 kg/d | intra_aisle,full_depth_now,glass_ceramic_pfd no S##,wp_l2_filled |
| IA-GLASS-02 | GLASS_BURNOUT | GLASS_MILL | S | mass | present | Glass burnout → mill | 28.0 kg/d | intra_aisle,full_depth_now,glass_ceramic_pfd no S##,wp_l2_filled |
| IA-GLASS-03 | GLASS_MILL | GLASS_DIGEST | S | mass | present | Glass mill → digest | 28.0 kg/d | intra_aisle,full_depth_now,glass_ceramic_pfd no S##,wp_l2_filled |
| IA-GLASS-Q2 | GLASS_BURNOUT | Q4_BUS | E | thermal | present | Q2 burnout heat (study path; not rate) | 0.5 kW | intra_aisle,full_depth_now,glass heat unlabeled,wp_l2_filled |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | present | Dryer → pyro | 8.0 kg/d | intra_aisle,full_depth_now,oil_line internals,wp_l2_filled |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | present | Pyro → frac | 7.0 kg/d | intra_aisle,full_depth_now,oil_line internals,wp_l2_filled |
| IA-OIL-03 | OIL_FRAC | AFTERBURNER | G | mass | present | Frac cut / vapor → afterburner | 6.0 kg/d | intra_aisle,full_depth_now,oil_line internals,wp_l2_filled |
| IA-OIL-Q1 | AFTERBURNER | Q4_BUS | E | thermal | present | Q1 afterburner heat (not into hab air) | 2.0 kW | intra_aisle,full_depth_now,Q1≠Q4 rule,wp_l2_filled |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | present | ZnBr2 charge (PV/RECT surplus) | 60.0 kW | ess_layer,wp_l2_filled |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | present | ZnBr2 discharge to bus | 60.0 kW | ess_layer,wp_l2_filled |
| IA-ESS-MEOH-CHG | MEOH_SYNTH | MEOH_TANK | L | mass,ess | present | MeOH synth inventory = charge-analogue | 1.0 kW | ess_layer,wp_l2_filled |
| IA-ESS-MEOH-DIS | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MeOH FC discharge (peers S79) | 1.0 kW | ess_layer,overlaps_S79_architecture,wp_l2_filled |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | 0.0 kg/d | ess_layer,wp_true_closure |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | 0.0 kg/d | ess_layer,wp_true_closure |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | present | Hydro turbine-pump electrical (MISSING on SLD) | 0.0 kW | ess_layer,missing_on_sld,wp_l2_filled |
| S83 | HDR_O2 | HABITATION | G | mass | present | O2 | 3.4 kg/d | wp_true_closure,wp_true_closure_residuals |
| IA-HDR-H2-01 | EW_1 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l1_topology,wp_l2_filled |
| IA-HDR-H2-02 | HDR_H2 | H2_DRYER | G | mass | present | process H2 | 4.8 kg/d | wp_l1_topology,arrestor_inline,wp_true_closure |
| S84 | CRYO_N2 | GROW_BED | G | mass | present | N2 | 0.5 kg/d | wp_true_closure |
| S85 | WS_SOLV | LITHO_STUB | L | mass | present | IPA / acetone / NMP class | 0.01 kg/d | wp_l2_filled,absent_from_candidate_mvs |
| IA-SALT-01 | SALT_FEED | LEACH_CSTR_1 | S/L | mass | present | salt make-up | 5.0 kg/d | wp_l1_topology,hopper_vs_tee_decided_physical,wp_true_closure |
| IA-SALT-02 | SALT_FEED | NUTRIENT_DOSE | S/L | mass | present | salt make-up | 2.0 kg/d | wp_l1_topology,hopper_vs_tee_decided_physical,wp_true_closure |
| IA-PV-01 | PV_ARRAY | SOL_ARK_60K | E | elec | present | PV DC | 70.0 kW | wp_l1_topology |
| IA-LOAD-01 | LOAD_AGG | SOL_ARK_60K | E | elec | present | aggregated AC/DC load | 5.0 kW | wp_l1_topology,logical_unmapped,wp_true_closure |
| IA-BLOW-01 | MFG_SHOP | BLOW_MOLD | S | mass | present | polymer melt / parison feed | 9.0 kg/d | wp_l2_filled |
| IA-BLOW-02 | BLOW_MOLD | MFG_SHOP | S | mass | present | formed goods + scrap to crib/S16 | 9.0 kg/d | wp_l2_filled |
| IA-ELC-01 | WIRE_DRAW | ELECTRODE_COAT | S | mass | present | wire/MET substrate | 0.5 kg/d | wp_l2_filled |
| IA-ELC-02 | ELECTRODE_COAT | MFG_SHOP | S | mass | present | coated electrode goods | 0.5 kg/d | wp_l2_filled |
| IA-ELC-03 | ELECTRODE_COAT | MET_AHU | G | mass | present | booth exhaust | 200.0 m3/h | wp_l2_filled |
| IA-SOLAR-01 | HDR_UPW | SOLAR_PV_CELL | L | mass | present | UPW (pre-remin) | 10.0 kg/d | wp_l2_filled |
| IA-SOLAR-02 | SOLAR_PV_CELL | LEACH_CSTR_1 | L | mass | present | spent etch / rinse (S10 class) | 5.0 kg/d | wp_l2_filled |
| IA-REMIN-01 | BMED_UPW_POLISH | REMIN | L | mass | present | pre-remin UPW / distillate branch | 10.0 kg/d | wp_l2_filled |
| IA-GEO-01 | GEO_HP_CLOSED_LOOP | GEO_HP | L/E | mass,thermal | present | geothermal loop fluid | 3.0 kW | wp_l1_topology,geo_survey_open,wp_true_closure |
| IA-HDR-H2-03 | EW_2 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l2_filled,multi_ew_hood |
| IA-HDR-H2-04 | EW_9 | HDR_H2 | G | mass | present | cathode H2 + sweep air | 1.6 kg/d | wp_l2_filled,multi_ew_hood |
| IA-GEO-ORC-01 | GEO_HP | GEO_ORC | E | thermal | present | surplus heat after Q4 life priority | 0.0 kW | wp_l2_filled,geo_orc_heat |
| IA-GEO-ORC-02 | GEO_ORC | Q4_BUS | E | thermal | present | ORC condenser reject via named HX | 0.0 kW | wp_l2_filled,geo_orc_heat |
| IA-SOLAR-03 | SOLAR_PV_CELL | PV_ARRAY | S | mass | present | PV cells / modules (rebuild/spare offtake) | 0.05 kg/d | wp_l2_filled,solar_offtake |
| S86 | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | present | goods / cassettes / surplus freight | 22.5 kg/d | wp_l2_filled,was_DOCK_EXPORT_TBD,open_boundary_export,wp_true_closure_residuals |
| S87 | HDR_O2 | CRYO_O2 | G | mass | present | surplus photosynthetic O2 | 1.4545454545454546 kg/d | wp_true_closure_residuals |
| IA-VCD-CATCH-01 | VCD_TRAIN | CATCH_TANK | L | mass | present | VCD inventory holdup transfer (event) | 0.0 kg/d | wp_true_closure_residuals |
| IA-MET-FEED | MFG_SHOP | MET_MELT | S | mass | present | plated metals melt charge | 20.0 kg/d | wp_true_closure_residuals |
| IA-FAB-CRIB | MFG_SHOP | WAFER_FAB | S | mass | present | Si / metals crib to FAB | 10.0 kg/d | wp_true_closure_residuals |
| IA-MFG-DOCK | MFG_SHOP | NORTH_DOCK | S | mass | present | plated goods without remelt | 12.0 kg/d | wp_true_closure_residuals |
| IA-MELT-MILL | MET_MELT | COLD_MILL | S | mass | present | billet / slab to cold mill | 6.0 kg/d | wp_true_closure_residuals |
| IA-MELT-ATOM | MET_MELT | GAS_ATOMIZER | S | mass | present | melt to atomizer | 4.0 kg/d | wp_true_closure_residuals |
| S88 | CRYO_AHU | CRYO_N2 | G | mass | present | ASU N2 make-up | 2.0 kg/d | wp_true_closure_residuals |
