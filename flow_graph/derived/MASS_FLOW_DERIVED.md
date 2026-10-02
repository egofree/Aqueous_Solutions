# Mass-flow claim excerpt — DERIVED from flow_graph

Document number: AQS-MF-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev G (`plant_flow_graph.json`)
Generated: 2026-10-02
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/MASS_FLOW.md`.
Only namespace=S and SANDBOX mass-layer edges listed (MFD campus view).

| ID | Route | Claim status | Presence | Rate | Notes |
|---|---|---|---|---|---|
| S01 | BMED_UPW_POLISH→HDR_UPW | Closed | present | 95.0 kg/d | — |
| S02 | CRYO_O2→HDR_O2 | Closed | present | 3.4 kg/d | WP-L1: insert HDR_O2 header endpoint (AQS-STR-001 S02; was CRYO_O2→HABITATION bypass) |
| S03 | CRYO_N2→WAFER_FAB | Closed | present | 1.5 kg/d | WP-L1: register mismatch fix — S03 source is CRYO_N2 (was CRYO_H2 carrying N2); AQS-STR-001 S03 | true-closure campaign steady-state equivalent |
| S04 | CRYO_CO2→GROW_BED | Closed / Claimed | present | 2.0 kg/d | true-closure method lock photosynthetic demand |
| S05 | H2_DRYER→CRYO_H2 | Claimed / Partial | present | 4.8 kg/d | — |
| S07 | NUTRIENT_DOSE→GROW_BED | Closed | present | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1→MFG_SHOP | Closed | present | 42.0 kg/d | — |
| S09 | BMED_UPW_POLISH→WET_BENCH | Closed | present | 0.6 kg/d | true-closure campaign steady-state equivalent |
| S10 | WET_BENCH→LEACH_CSTR_1 | Closed | present | 10.0 kg/d | — |
| S11 | GROW_BED→AFTERBURNER | Closed | present | 0.8 kg/d | — |
| S12 | HABITATION→NUTRIENT_DOSE | Closed | present | 110.0 kg/d | — |
| S13 | GROW_BED→VCD_TRAIN | Closed | present | 15.0 kg/d | From register: FARM SUMP + HVAC → UPW POLISH / SALT FEED / VCD_FEED | WP-L2 study rate filled. |
| S14 | GROW_BED→HABITATION | Closed | present | 4.2 kg/d | — |
| S15 | GROW_BED→HDR_O2 | Closed | present | 1.4545454545454546 kg/d | WP-L1: STR S15 GROW_BED→HDR_O2 (was bypass to HABITATION) | true-closure biomass O2 method lock |
| S16 | MFG_SHOP→LEACH_CSTR_1 | Closed | present | 12.0 kg/d | — |
| S18 | AFTERBURNER→CRYO_CO2 | Claimed | present | 15.0 kg/d | — |
| S19 | BAGHOUSE→LEACH_CSTR_1 | Closed | present | 0.5 kg/d | From register: BAGHOUSE fines → LEACH CSTR 1 |
| S21 | ROOF_TANK→HABITATION | Closed | present | 95.0 kg/d | — |
| S24 | H2_DRYER→BOUNDARY_EXPORT | Partial | present | 0.0 kg/d | zero-flow continuous by design (event) | Intentional open_boundary contingency (steady 0) — residuals WP confirm |
| S25 | VCD_TRAIN→BMED_UPW_POLISH | Closed | present | 145.0 kg/d | WP-L2 study rate filled. | residuals: full-feed recovery (was grey-primary holdup) |
| S26 | REMIN→HABITATION | Closed | present | 10.0 kg/d | WP-L2 study rate filled. |
| S27 | FAB_UPW_TANK→WET_BENCH | Closed | present | 15.0 kg/d | From register: FAB_UPW_TANK → WET_BENCH |
| S28 | VCD_TRAIN→LEACH_CSTR_1 | Closed | present | 14.3 kg/d | WP-L2 study rate filled. | residuals: brine matches full-feed balance |
| S29 | GREY_TREAT→VCD_TRAIN | Closed | present | 110.0 kg/d | From register: GREY_TREAT → VCD_FEED / SALT FEED | WP-L2 study rate filled. |
| S30 | BLACK_DIGEST→NUTRIENT_DOSE | Closed | present | 8.0 kg/d | From register: BLACK_DIGEST → NUTRIENT DOSE / SALT FEED |
| S31 | WS_HF_ED→WET_BENCH | Closed / Claimed | present | 1.5 kg/d | From register: WS_HF_ED → WET_BENCH |
| S32 | WS_PEROX→WET_BENCH | Claimed | present | 3.0 kg/d | From register: WS_PEROX → WET_BENCH |
| S33 | WS_AMMONIA→WET_BENCH | Claimed | present | 3.0 kg/d | From register: WS_AMMONIA → WET_BENCH |
| S34 | WS_NITRIC→WET_BENCH | Claimed | present | 1.25 kg/d | From register: WS_NITRIC / WS_PHOS → WET_BENCH |
| S35 | WS_KOH→WET_BENCH | Claimed | present | 0.3 kg/d | From register: WS_KOH → WET_BENCH / solar texture stub |
| S36 | WS_DOPE→WAFER_FAB | Claimed | present | 0.01 kg/d | From register: WS_DOPE / CRU polish → FAB_TOOL dopant cabinets |
| S37 | WS_SLURRY→WAFER_FAB | Claimed | present | 3.0 kg/d | From register: WS_SLURRY → LAP_CMP / FAB_PREP |
| S38 | LITHO_STUB→WET_BENCH | Claimed | present | 0.006 kg/d | WP-L2 study rate filled. |
| S39 | WAFER_FAB→LEACH_CSTR_1 | Closed | present | 12.0 kg/d | From register: LAP_CMP / WET_BENCH / FAB_TOOL → REGEN LEACH / OIL / HDR_ORG |
| S40 | ROOF_TANK→TERRACE_IRRIG | Closed | present | 0.0 kg/d | zero-flow continuous by design (event) |
| S41 | TERRACE_IRRIG→CATCH_TANK | Closed | present | 20.0 kg/d | From register: TERRACE underdrain / apron (clean) → CATCH TANK / DRAIN_SEC |
| S42 | TERRACE_IRRIG→GREY_TREAT | Closed / Claimed | present | 5.0 kg/d | From register: Enclosed terrace / GH fertigated drain → GREY treat / VCD_FEED / SALT |
| S43 | GEO_GHEX→GEO_HP_CLOSED_LOOP | Closed | present | 3.0 kW | From register: GEO_GHEX → GEO_HP (closed loop) | thermal carrier rate; design-basis not field measured |
| S45 | CRYO_H2→BACKUP_GEN | Closed | present | 0.72 kg/d | residuals: H2 schedule GEN peaks 15% |
| S46 | BACKUP_GEN→GREY_TREAT | Claimed | present | 0.2 kg/d | From register: BACKUP_GEN exhaust → condensate / scrubber |
| S49 | CRYO_H2→FUEL_CELL | Closed | present | 3.84 kg/d | residuals: H2 schedule FC baseload 80% |
| S50 | CRYO_O2→FUEL_CELL | Claimed | present | 38.4 kg/d | — |
| S52 | FUEL_CELL→VCD_TRAIN | Claimed | present | 34.3 kg/d | WP-L2 study rate filled. | residuals: S52 tracks S49 schedule |
| S55 | CRYO_DED_COOL→CRYO_DED_COOL | Closed | present | 1.0 kW | WP-L2: intentional dedicated cryo cool self-loop retained (AQS-STR/MF Closed utility). Not a topology gap. | intentional utility self-loop; continuous thermal circulating duty |
| S56 | CRYO_AHU→BOUNDARY_EXPORT | Partial | present | 0.0 kg/d | From register: CRYO_AHU / CRYO_AHU_COND residual → safe vent contingency |
| S57 | MET_MELT→WIRE_DRAW | Closed | present | 10.0 kg/d | From register: PROD_METALS / MET_MELT → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER | residuals: melt split wire 10 of 20 |
| S58 | WIRE_DRAW→MFG_SHOP | Closed | present | 9.0 kg/d | From register: WIRE_DRAW → MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB | residuals: wire product mass-conserving |
| S59 | COLD_MILL→MFG_SHOP | Closed | present | 5.5 kg/d | From register: COLD_MILL → MET_SHEET_BIN / MFG_CRIB | residuals: sheet product mass-conserving |
| S60 | GAS_ATOMIZER→MFG_SHOP | Closed / Claimed | present | 3.5 kg/d | From register: GAS_ATOMIZER → MET_POWDER_CRIB / FAB / RepRap | residuals: powder product mass-conserving |
| S61 | MFG_SHOP→HOPPER | Closed | present | 2.0 kg/d | From register: Forming swarf / trim → HOPPER / leach | residuals: swarf closes melt balance |
| S62 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 200.0 m3/h | From register: MET_AHU → MET_SCRUB / baghouse (S71) |
| S64 | H2_DRYER→CRYO_H2 | Partial | present | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER→ACID_POLISH_SCRUB | Partial / Claimed | present | 1500.0 m3/h | WP-L1: STR/MF S65 ALK residual→ACID_POLISH_SCRUB (was self-loop) |
| S66 | ACID_POLISH_SCRUB→CRU | Claimed | present | 2.0 kg/d | From register: ACID_POLISH / ALK blowdown → CRU |
| S67 | AFTERBURNER_FLUE→CRYO_CO2 | Partial / Claimed | present | 5.0 kg/d | From register: AFTERBURNER flue → FLUE_CAP / CRYO |
| S68 | CRYO_AHU→S13_CLASS_TREAT | Claimed | present | 2.0 kg/d | From register: FLUE_CAP / CRYO_AHU_COND → S13 class / treat |
| S70 | CRYO_AHU_COND_CONDENSABLE→CRYO_H2 | Partial | present | 0.1 kg/d | From register: CRYO_AHU_COND condensable → COLD_BOX / CRYO condensate return |
| S71 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 200.0 m3/h | From register: MET_AHU → MET_SCRUB / baghouse |
| S72 | MET_SCRUB→LEACH_CSTR_1 | Claimed | present | 1.0 kg/d | From register: MET_SCRUB / baghouse → CSTR 1 / OIL / HDR_ORG |
| S73 | CRYO_CO2→MEOH_SYNTH | — | present | 6.9 kg/d | — |
| S74 | CRYO_H2→MEOH_SYNTH | Closed | present | 0.24 kg/d | residuals: H2 schedule MeOH surplus 5% |
| S75 | MEOH_SYNTH→MEOH_TANK | — | present | 5.0 kg/d | — |
| S77 | MEOH_FERM→MEOH_TANK | — | present | 0.5 kg/d | From register: MEOH_FERM_STILL → MEOH_TANK |
| S78 | HABITATION→MEOH_FERM | — | present | 2.0 kg/d | From register: Farm/hab organics (S12/S30 class) → MEOH_FERM_DIG |
| S81 | MEOH_FC→GREY_TREAT | — | present | 1.5 kg/d | From register: MEOH_FC / MEOH_COND → condensate / S13 class |
| S82 | MEOH_FC→CRYO_CO2 | — | present | 1.0 kg/d | From register: MEOH_FC / MEOH_VENT_KO → CRYO_CO2 / FARM (Claimed) |
| S08G | GLASS_DIGEST→BOUNDARY_EXPORT | — | present | 30.0 kg/d | candidate_mvs extension — do not invent new register ID | Intentional glass/ceramic goods export boundary — residuals WP confirm |
| S14X | GROW_BED→BOUNDARY_EXPORT | — | present | 1.8 kg/d | candidate_mvs extension — do not invent new register ID | Intentional food surplus export boundary — residuals WP confirm |
| S83 | HDR_O2→HABITATION | Closed | present | 3.4 kg/d | WP-L1: HDR_O2→HAB after S02/S15 header insert (AQS-PLAN-LOOP-001 §4.1) | residuals: metabolic only; surplus on S87 |
| S84 | CRYO_N2→GROW_BED | Closed | present | 0.5 kg/d | WP-L1: STR S03 CRYO N2→FARM; GROW_BED is FARM sector endpoint (no separate FARM unit) |
| S85 | WS_SOLV→LITHO_STUB | Claimed | present | 0.01 kg/d | WP-L1: STR S38 supply WS_SOLV→litho/strip; S38 remains LITHO_STUB→WET_BENCH waste path |
| S86 | NORTH_DOCK→BOUNDARY_EXPORT | Closed | present | 22.5 kg/d | WP-L2: retired DOCK_EXPORT_TBD; issued S86. Peer S08G glass + S14X food remain distinct. | Intentional dock goods export boundary — residuals WP confirm |
| S87 | HDR_O2→CRYO_O2 | Closed | present | 1.4545454545454546 kg/d | Residuals: capture photosynthetic O2 surplus into cryo (not silent blend loss) |
| S88 | CRYO_AHU→CRYO_N2 | Closed | present | 2.0 kg/d | Residuals: N2 make-up closes campaign draw (no invented return SCC) |
