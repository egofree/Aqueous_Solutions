# Stream register excerpt — DERIVED from flow_graph

Document number: AQS-STR-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev B (`plant_flow_graph.json`)
Generated: 2026-10-01
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/STREAM_REGISTER.md`.
Intra-aisle (IA-*) and TBD namespaces included for full_depth_now visibility.

| ID | From | To | Ph | Layers | Presence | Carries | Rate | Gap flags |
|---|---|---|---|---|---|---|---|---|
| S01 | BMED_UPW_POLISH | HDR_UPW | L | mass | present | UPW | 95.0 kg/d | — |
| S02 | CRYO_O2 | HABITATION | G | mass | present | O2 | 3.4 kg/d | — |
| S03 | CRYO_H2 | WAFER_FAB | G | mass | present | N2 | — | — |
| S04 | CRYO_CO2 | GROW_BED | G | mass | present | CO2 | — | — |
| S05 | H2_DRYER | CRYO_H2 | G | mass | present | process H2 | 4.8 kg/d | — |
| S06 | GEO_HP | GROW_BED | E | thermal | present | heat Q4 | — | — |
| S07 | NUTRIENT_DOSE | GROW_BED | S/L | mass | present | nutrients | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1 | MFG_SHOP | S | mass | present | metals/Si | 42.0 kg/d | — |
| S09 | BMED_UPW_POLISH | WET_BENCH | L | mass | present | HCl/NaOH | — | — |
| S10 | WET_BENCH | LEACH_CSTR_1 | L | mass | present | spent etch | 10.0 kg/d | — |
| S11 | GROW_BED | AFTERBURNER | S | mass | present | organics | 0.8 kg/d | — |
| S12 | HABITATION | NUTRIENT_DOSE | L/S | mass | present | grey/solids | 110.0 kg/d | — |
| S13 | GROW_BED | VCD_TRAIN | L | mass | placeholder | condensate | — | absent_from_candidate_mvs |
| S14 | GROW_BED | HABITATION | S | mass | present | food | 4.2 kg/d | — |
| S15 | GROW_BED | HABITATION | G | mass | present | photosynthetic O2 | — | — |
| S16 | MFG_SHOP | LEACH_CSTR_1 | S | mass | present | scrap | 12.0 kg/d | — |
| S17 | SOL_ARK_60K | RECTIFIER | E | elec | present | DC/480V | 50.0 kW | — |
| S18 | AFTERBURNER | CRYO_CO2 | G | mass | present | captured CO2/air | 15.0 kg/d | — |
| S19 | BAGHOUSE | LEACH_CSTR_1 | S | mass | present | dust | — | absent_from_candidate_mvs |
| S20 | GROW_BED | SOL_ARK_60K | E | elec | present | load | — | — |
| S21 | ROOF_TANK | HABITATION | L | mass | present | clean tower water | 95.0 kg/d | — |
| S22 | ROOF_TANK | CATCH_TANK | L | ess | present | penstock | — | — |
| S23 | CATCH_TANK | ROOF_TANK | L | ess | present | pump return | — | — |
| S24 | H2_DRYER | BOUNDARY_EXPORT | G | mass | present | H2 relief contingency | — | — |
| S25 | VCD_TRAIN | BMED_UPW_POLISH | L | mass | placeholder | VCD distillate | — | — |
| S26 | REMIN | HABITATION | L | mass | placeholder | potable | — | — |
| S27 | FAB_UPW_TANK | WET_BENCH | L | mass | present | fab UPW > 18 MΩ·cm class | — | absent_from_candidate_mvs |
| S28 | VCD_TRAIN | LEACH_CSTR_1 | L | mass | placeholder | VCD brine | — | — |
| S29 | GREY_TREAT | VCD_TRAIN | L | mass | placeholder | treated grey | — | absent_from_candidate_mvs |
| S30 | BLACK_DIGEST | NUTRIENT_DOSE | L/S | mass | present | digest liquor / nutrients | — | absent_from_candidate_mvs |
| S31 | WS_HF_ED | WET_BENCH | L | mass | present | HF (aq) | — | absent_from_candidate_mvs |
| S32 | WS_PEROX | WET_BENCH | L | mass | present | H₂O₂ | — | absent_from_candidate_mvs |
| S33 | WS_AMMONIA | WET_BENCH | L | mass | present | NH₄OH / NH₃ (aq) | — | absent_from_candidate_mvs |
| S34 | WS_NITRIC | WET_BENCH | L | mass | present | HNO₃ / H₃PO₄ etch suite | — | absent_from_candidate_mvs |
| S35 | WS_KOH | WET_BENCH | L | mass | present | KOH | — | absent_from_candidate_mvs |
| S36 | WS_DOPE | WAFER_FAB | L/G | mass | present | B/P/As concentrate; BBr₃ / POCl₃ class | — | absent_from_candidate_mvs |
| S37 | WS_SLURRY | WAFER_FAB | L | mass | present | colloidal silica slurry | — | absent_from_candidate_mvs |
| S38 | LITHO_STUB | WET_BENCH | L | mass | placeholder | resist / solvent waste | — | — |
| S39 | WAFER_FAB | LEACH_CSTR_1 | L/S | mass | present | spent slurry, solvent, photoresist sludge | — | absent_from_candidate_mvs |
| S40 | ROOF_TANK | TERRACE_IRRIG | L | mass | present | clean overflow | — | — |
| S41 | TERRACE_IRRIG | CATCH_TANK | L | mass | present | rain + S40 return | — | absent_from_candidate_mvs |
| S42 | TERRACE_IRRIG | GREY_TREAT | L | mass | present | dilute nutrient drain | — | absent_from_candidate_mvs |
| S43 | GEO_GHEX | GEO_HP_CLOSED_LOOP | L/E | mass,thermal | present | geothermal loop fluid | — | absent_from_candidate_mvs |
| S44 | GEO_HP | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S45 | CRYO_H2 | BACKUP_GEN | G | mass | present | H2 fuel | 3.6 kg/d | — |
| S46 | BACKUP_GEN | GREY_TREAT | G/L | mass | present | H₂O + NOx class | — | absent_from_candidate_mvs |
| S47 | BACKUP_GEN | SOL_ARK_60K | E | elec | present | GEN AC | 2.5 kW | — |
| S48 | GEO_ORC | SOL_ARK_60K | E | elec | placeholder | ORC AC | — | orc_stub_kw_tbd |
| S49 | CRYO_H2 | FUEL_CELL | G | mass | present | H2 fuel | 4.8 kg/d | — |
| S50 | CRYO_O2 | FUEL_CELL | G | mass | present | O2 oxidizer | 38.4 kg/d | — |
| S51 | FUEL_CELL | SOL_ARK_60K | E | elec | present | FC DC | 4.0 kW | — |
| S52 | FUEL_CELL | VCD_TRAIN | L | mass | placeholder | PEM product H2O | — | — |
| S53 | FUEL_CELL | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S54 | CRYO_HX_Q4 | Q4_BUS | E | thermal | present | warm residual < 80 °C | — | absent_from_candidate_mvs |
| S55 | CRYO_DED_COOL | CRYO_DED_COOL | L/E | mass,thermal | present | dedicated cryo utility cooling | — | absent_from_candidate_mvs |
| S56 | CRYO_AHU | BOUNDARY_EXPORT | G | mass | present | non-condensable residual after KO | — | absent_from_candidate_mvs |
| S57 | MET_MELT | WIRE_DRAW | S/L | mass | present | billet / melt / charge | — | absent_from_candidate_mvs |
| S58 | WIRE_DRAW | MFG_SHOP | S | mass | present | wire product | — | absent_from_candidate_mvs |
| S59 | COLD_MILL | MFG_SHOP | S | mass | present | sheet / strip | — | absent_from_candidate_mvs |
| S60 | GAS_ATOMIZER | MFG_SHOP | S | mass | present | metal powder | — | absent_from_candidate_mvs |
| S61 | MFG_SHOP | HOPPER | S | mass | present | metal scrap | — | absent_from_candidate_mvs |
| S62 | MET_AHU | MET_SCRUB | G | mass | present | MFG metal-aisle capture feed | — | absent_from_candidate_mvs |
| S63 | MET_HX_Q4 | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S64 | H2_DRYER | CRYO_H2 | G | mass | present | H2 normal path | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER | ALK_SCRUBBER | G | mass | present | acid-gas residual | 1500.0 m3/h | — |
| S66 | ACID_POLISH_SCRUB | CRU | L | mass | present | scrub liquor → chlorate finish | — | absent_from_candidate_mvs |
| S67 | AFTERBURNER_FLUE | CRYO_CO2 | G | mass | present | captured CO₂ + condensables | — | absent_from_candidate_mvs |
| S68 | CRYO_AHU | S13_CLASS_TREAT | L | mass | present | flue / AHU condensate | — | absent_from_candidate_mvs |
| S69 | ZNBR2 | ZNBR2 | L | ess | present | Br⁻ makeup after ORP | — | absent_from_candidate_mvs |
| S70 | CRYO_AHU_COND_CONDENSABLE | CRYO_H2 | G/L | mass | present | boil-off / purge condensables | — | absent_from_candidate_mvs |
| S71 | MET_AHU | MET_SCRUB | G | mass | present | metal-aisle fume / mist / dust | — | absent_from_candidate_mvs |
| S72 | MET_SCRUB | LEACH_CSTR_1 | L/S | mass | present | fines + scrub liquor / organic mist | — | absent_from_candidate_mvs |
| S73 | CRYO_CO2 | MEOH_SYNTH | G | mass | present | CO2 feedstock | 6.9 kg/d | — |
| S74 | CRYO_H2 | MEOH_SYNTH | G | mass | present | H2 for MeOH | 0.94 kg/d | — |
| S75 | MEOH_SYNTH | MEOH_TANK | L | mass | present | crude MeOH | 5.0 kg/d | — |
| S76 | MEOH_TANK | MEOH_FC | L | ess | present | MeOH fuel | 5.0 kg/d | — |
| S77 | MEOH_FERM | MEOH_TANK | L | mass | present | biogenic MeOH | — | absent_from_candidate_mvs |
| S78 | HABITATION | MEOH_FERM | L/S | mass | present | ferment feed | — | absent_from_candidate_mvs |
| S79 | MEOH_FC | SOL_ARK_60K | E | elec,ess | present | MEOH DC | 1.0 kW | — |
| S80 | MEOH_FC | Q4_BUS | E | thermal | present | heat < 80 °C | — | absent_from_candidate_mvs |
| S81 | MEOH_FC | GREY_TREAT | L | mass | present | product / process H₂O | — | absent_from_candidate_mvs |
| S82 | MEOH_FC | CRYO_CO2 | G | mass | present | CO₂ return from MeOH FC | — | absent_from_candidate_mvs |
| S08G | GLASS_DIGEST | BOUNDARY_EXPORT | S | mass | present | glass/ceramic goods | 30.0 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| S14X | GROW_BED | BOUNDARY_EXPORT | S | mass | present | food surplus export | 1.8 kg/d | sandbox_extra_not_in_STREAM_REGISTER,reconcile_or_keep_sandbox |
| DOCK_EXPORT_TBD | NORTH_DOCK | BOUNDARY_EXPORT | S | mass | placeholder | goods / cassettes / surplus freight (ID TBD) | — | no_S_id,do_not_invent_route_or_rate,high_severity_audit |
| IA-EW-01 | EW_1 | EW_2 | L | mass | placeholder | EW stage overflow/advance | — | intra_aisle,full_depth_now,ew_cascade undrawn S## |
| IA-EW-02 | EW_2 | EW_9 | L | mass | placeholder | EW cascade mid→last (proxy; stages 3–8 not exploded) | — | intra_aisle,full_depth_now,ew_cascade undrawn S## |
| IA-EW-03 | EW_9 | POLISH_BANK | L | mass | placeholder | EW → polish / precip | — | intra_aisle,full_depth_now,ew_cascade undrawn S## |
| IA-EW-04 | LEACH_CSTR_1 | EW_1 | L | mass | placeholder | CSTR → EW-1 feed | — | intra_aisle,full_depth_now,ew_cascade undrawn S## |
| IA-WET-FLOAT-01 | FLOAT_SINK | LEACH_CSTR_1 | L | mass | placeholder | Float/sink liquor return | — | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| IA-WET-C29-01 | C29_RECYCLE | LEACH_CSTR_1 | L | mass | placeholder | C29-class recycle | — | intra_aisle,full_depth_now,STR scope-out; ID was TBD |
| IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | L | mass | placeholder | Continuous recycle liquor | — | intra_aisle,full_depth_now,continuous_recycling_pfd |
| IA-REC-Q3 | CONTINUOUS_RECYCLE | Q4_BUS | E | thermal | placeholder | Heat ladder Q3 residual (ghost to Q4 bus for EFD-thermal) | — | intra_aisle,full_depth_now,heat ladder unlabeled |
| IA-BMED-01 | BMED_ACID | BMED_UPW_POLISH | L | mass | placeholder | BMED acid product internal | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-02 | BMED_BASE | BMED_UPW_POLISH | L | mass | placeholder | BMED base product internal | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-03 | CRU | BMED_ACID | L | mass | placeholder | CRU → BMED acid regen loop | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-BMED-04 | CRU | BMED_BASE | L | mass | placeholder | CRU → BMED base regen loop | — | intra_aisle,full_depth_now,bmed_regen unlabeled |
| IA-POL-01 | POLISH_BANK | BMED_UPW_POLISH | L | mass | placeholder | Polish bank → UPW polish | — | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-POL-02 | POLISH_BANK | POLISH_BANK | L | mass | placeholder | Polish series internals (self-loop stub) | — | intra_aisle,full_depth_now,polish_bank unlabeled |
| IA-GLASS-01 | GLASS_RINSE | GLASS_BURNOUT | L | mass | placeholder | Glass rinse → burnout | — | intra_aisle,full_depth_now,glass_ceramic_pfd no S## |
| IA-GLASS-02 | GLASS_BURNOUT | GLASS_MILL | S | mass | placeholder | Glass burnout → mill | — | intra_aisle,full_depth_now,glass_ceramic_pfd no S## |
| IA-GLASS-03 | GLASS_MILL | GLASS_DIGEST | S | mass | placeholder | Glass mill → digest | — | intra_aisle,full_depth_now,glass_ceramic_pfd no S## |
| IA-GLASS-Q2 | GLASS_BURNOUT | Q4_BUS | E | thermal | placeholder | Q2 burnout heat (study path; not rate) | — | intra_aisle,full_depth_now,glass heat unlabeled |
| IA-OIL-01 | OIL_DRYER | OIL_PYRO | S | mass | placeholder | Dryer → pyro | — | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-02 | OIL_PYRO | OIL_FRAC | L | mass | placeholder | Pyro → frac | — | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-03 | OIL_FRAC | AFTERBURNER | G | mass | placeholder | Frac cut / vapor → afterburner | — | intra_aisle,full_depth_now,oil_line internals |
| IA-OIL-Q1 | AFTERBURNER | Q4_BUS | E | thermal | placeholder | Q1 afterburner heat (not into hab air) | — | intra_aisle,full_depth_now,Q1≠Q4 rule |
| IA-ESS-ZNBR2-CHG | SOL_ARK_60K | ZNBR2 | E | elec,ess | placeholder | ZnBr2 charge (PV/RECT surplus) | — | ess_layer |
| IA-ESS-ZNBR2-DIS | ZNBR2 | SOL_ARK_60K | E | elec,ess | placeholder | ZnBr2 discharge to bus | — | ess_layer |
| IA-ESS-MEOH-CHG | MEOH_SYNTH | MEOH_TANK | L | mass,ess | placeholder | MeOH synth inventory = charge-analogue | — | ess_layer |
| IA-ESS-MEOH-DIS | MEOH_FC | SOL_ARK_60K | E | elec,ess | placeholder | MeOH FC discharge (peers S79) | — | ess_layer,overlaps_S79_architecture |
| IA-ESS-HYDRO-CHG | CATCH_TANK | ROOF_TANK | L | mass,ess | present | Pumped hydro charge (pump up; peers S23) | — | ess_layer |
| IA-ESS-HYDRO-DIS | ROOF_TANK | CATCH_TANK | L | mass,ess | present | Pumped hydro discharge (penstock; peers S22) | — | ess_layer |
| IA-ESS-HYDRO-ELEC | HYDRO_SET | SOL_ARK_60K | E | elec,ess | placeholder | Hydro turbine-pump electrical (MISSING on SLD) | — | ess_layer,missing_on_sld |
