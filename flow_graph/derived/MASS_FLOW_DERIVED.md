# Mass-flow claim excerpt — DERIVED from flow_graph

Document number: AQS-MF-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev H (`plant_flow_graph.json`)
Generated: 2026-10-07
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/MASS_FLOW.md`.
Only namespace=S and SANDBOX mass-layer edges listed (MFD campus view).

| ID | Route | Claim status | Presence | Rate | Notes |
|---|---|---|---|---|---|
| DOCK_EXPORT_TBD | NORTH_DOCK→BOUNDARY_EXPORT | — | placeholder | — | Audit §7.1 DOCK export — sector required; no inter-block stream ID issued |
| S01 | BMED_UPW_POLISH→HDR_UPW | Closed | present | 95.0 kg/d | — |
| S02 | CRYO_O2→HABITATION | Closed | present | 3.4 kg/d | — |
| S03 | CRYO_N2→WAFER_FAB | — | present | — | Was wrongly sourced from CRYO_H2. |
| S04 | CRYO_CO2→GROW_BED | Closed / Claimed | present | — | — |
| S05 | H2_DRYER→CRYO_H2 | Claimed / Partial | present | 4.8 kg/d | — |
| S07 | NUTRIENT_DOSE→GROW_BED | Closed | present | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1→MFG_SHOP | Closed | present | 42.0 kg/d | — |
| S08G | GLASS_DIGEST→BOUNDARY_EXPORT | — | present | 30.0 kg/d | candidate_mvs extension — do not invent new register ID |
| S09 | BMED_ACID→WET_BENCH | — | present | — | Acid to bench. Polish is not this edge. |
| S10 | WET_BENCH→LEACH_CSTR_1 | Closed | present | 10.0 kg/d | — |
| S11 | GROW_BED→AFTERBURNER | Closed | present | 0.8 kg/d | — |
| S12 | HABITATION→NUTRIENT_DOSE | Closed | present | 110.0 kg/d | — |
| S13 | GROW_BED→VCD_TRAIN | Closed | placeholder | — | From register: FARM SUMP + HVAC → UPW POLISH / SALT FEED / VCD_FEED |
| S14 | GROW_BED→HABITATION | Closed | present | 4.2 kg/d | — |
| S14X | GROW_BED→BOUNDARY_EXPORT | — | present | 1.8 kg/d | candidate_mvs extension — do not invent new register ID |
| S15 | GROW_BED→HABITATION | Closed | present | — | — |
| S16 | MFG_SHOP→LEACH_CSTR_1 | Closed | present | 12.0 kg/d | — |
| S18 | AFTERBURNER→CRYO_CO2 | Claimed | present | 15.0 kg/d | — |
| S19 | BAGHOUSE→LEACH_CSTR_1 | Closed | present | — | From register: BAGHOUSE fines → LEACH CSTR 1 |
| S21 | ROOF_TANK→HABITATION | Closed | present | 95.0 kg/d | — |
| S24 | H2_DRYER→RELIEF_H2 | — | present | — | NFPA 2 relief. Not freight. |
| S25 | VCD_TRAIN→BMED_UPW_POLISH | Closed | placeholder | — | — |
| S26 | REMIN→HABITATION | Closed | placeholder | — | — |
| S27 | FAB_UPW_TANK→WET_BENCH | Closed | present | — | From register: FAB_UPW_TANK → WET_BENCH |
| S28 | VCD_TRAIN→LEACH_CSTR_1 | Closed | placeholder | — | — |
| S29 | GREY_TREAT→VCD_TRAIN | Closed | placeholder | — | From register: GREY_TREAT → VCD_FEED / SALT FEED |
| S30 | BLACK_DIGEST→NUTRIENT_DOSE | Closed | present | — | From register: BLACK_DIGEST → NUTRIENT DOSE / SALT FEED |
| S31 | WS_HF_ED→WET_BENCH | Closed / Claimed | present | — | From register: WS_HF_ED → WET_BENCH |
| S32 | WS_PEROX→WET_BENCH | Claimed | present | — | From register: WS_PEROX → WET_BENCH |
| S33 | WS_AMMONIA→WET_BENCH | Claimed | present | — | From register: WS_AMMONIA → WET_BENCH |
| S35 | WS_KOH→WET_BENCH | Claimed | present | — | From register: WS_KOH → WET_BENCH / solar texture stub |
| S36 | WS_DOPE→WAFER_FAB | Claimed | present | — | From register: WS_DOPE / CRU polish → FAB_TOOL dopant cabinets |
| S37 | WS_SLURRY→WAFER_FAB | Claimed | present | — | From register: WS_SLURRY → LAP_CMP / FAB_PREP |
| S38 | WET_BENCH→OIL_FRAC | — | present | — | Waste leaves the bench. |
| S39 | WAFER_FAB→LEACH_CSTR_1 | — | present | — | NFPA 400: no organics into chlorate leach. |
| S39B | WAFER_FAB→OIL_FRAC | — | present | — | Organics to the oil line. |
| S40 | ROOF_TANK→TERRACE_IRRIG | Closed | present | — | — |
| S41 | TERRACE_IRRIG→CATCH_TANK | Closed | present | — | From register: TERRACE underdrain / apron (clean) → CATCH TANK / DRAIN_SEC |
| S42 | TERRACE_IRRIG→GREY_TREAT | Closed / Claimed | present | — | From register: Enclosed terrace / GH fertigated drain → GREY treat / VCD_FEED / SALT |
| S43 | GEO_GHEX→GEO_HP_CLOSED_LOOP | Closed | present | — | From register: GEO_GHEX → GEO_HP (closed loop) |
| S45 | CRYO_H2→BACKUP_GEN | Claimed / Partial | present | 3.6 kg/d | — |
| S46 | BACKUP_GEN→NOX_SCRUB | — | present | — | NFPA 37 exhaust. Not life water. |
| S49 | CRYO_H2→FUEL_CELL | Claimed / Partial | present | 4.8 kg/d | — |
| S50 | CRYO_O2→FUEL_CELL | Claimed | present | 38.4 kg/d | — |
| S52 | FUEL_CELL→VCD_TRAIN | Claimed | placeholder | — | — |
| S55 | CRYO_DED_COOL→CRYO_DED_COOL | Closed | present | — | From register: CRYO_DED_COOL (loop) → CRYO_DED_COOL |
| S56 | CRYO_AHU→RELIEF_CRYO | — | present | — | NFPA 55 relief. Not freight. |
| S57 | MET_MELT→WIRE_DRAW | Closed | present | — | From register: PROD_METALS / MET_MELT → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER |
| S58 | WIRE_DRAW→MFG_SHOP | Closed | present | — | From register: WIRE_DRAW → MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB |
| S59 | COLD_MILL→MFG_SHOP | Closed | present | — | From register: COLD_MILL → MET_SHEET_BIN / MFG_CRIB |
| S60 | GAS_ATOMIZER→MFG_SHOP | Closed / Claimed | present | — | From register: GAS_ATOMIZER → MET_POWDER_CRIB / FAB / RepRap |
| S61 | MFG_SHOP→HOPPER | Closed | present | — | From register: Forming swarf / trim → HOPPER / leach |
| S62 | MET_AHU→MET_SCRUB | Partial / Claimed | present | — | From register: MET_AHU → MET_SCRUB / baghouse (S71) |
| S64 | H2_DRYER→CRYO_H2 | Partial | present | 4.8 kg/d | — |
| S65 | ALK_SCRUBBER→ACID_POLISH_SCRUB | — | present | — | Not a self-loop. Polish then CRU via S66. |
| S66 | ACID_POLISH_SCRUB→CRU | Claimed | present | — | From register: ACID_POLISH / ALK blowdown → CRU |
| S67 | AFTERBURNER_FLUE→FLUE_KO | — | present | — | Knockout before any CO2 claim. |
| S67B | FLUE_KO→CRYO_CO2 | — | study | — | Only the CO2-rich cut. Reject N2/O2/NOx. |
| S68 | CRYO_AHU→LEACH_CSTR_1 | — | present | — | Acid condensate stays process. |
| S69 | ZNBR2→ZNBR2_BR2_REGEN | — | present | — | Own tower. |
| S69B | ZNBR2_BR2_REGEN→ZNBR2 | — | present | — | Return to the bromine tank only. |
| S70 | CRYO_AHU_COND_CONDENSABLE→FLUE_KO | — | present | — | Not into the hydrogen box. |
| S71 | MET_AHU→MET_SCRUB | Partial / Claimed | present | — | From register: MET_AHU → MET_SCRUB / baghouse |
| S72 | MET_SCRUB→LEACH_CSTR_1 | — | present | — | Fines only. |
| S72B | MET_SCRUB→OIL_FRAC | — | present | — | Organics off the metal scrub, to oil. |
| S73 | CRYO_CO2→MEOH_SYNTH | — | present | 6.9 kg/d | — |
| S74 | CRYO_H2→MEOH_SYNTH | — | present | 0.94 kg/d | — |
| S75 | MEOH_SYNTH→MEOH_TANK | — | present | 5.0 kg/d | — |
| S77 | MEOH_FERM→MEOH_TANK | — | present | — | From register: MEOH_FERM_STILL → MEOH_TANK |
| S78 | HABITATION→MEOH_FERM | — | present | — | From register: Farm/hab organics (S12/S30 class) → MEOH_FERM_DIG |
| S81 | MEOH_FC→MEOH_COND | — | present | — | Methanol residual stays process. |
| S82 | MEOH_FC→CRYO_CO2 | — | present | — | From register: MEOH_FC / MEOH_VENT_KO → CRYO_CO2 / FARM (Claimed) |
| S83 | CRYO_O2→HDR_O2 | — | present | — | Life header fill. Not the dock. |
| S84 | CRYO_N2→HDR_N2 | — | present | — | Life header fill. Not the dock. |
| S85 | CRYO_CO2→HDR_CO2 | — | present | — | Life header fill. Not the dock. |
| S86 | CRYO_AHU→RELIEF_CRYO | — | present | — | Same sink as S56. Issued so the old dock edge has a number and a legal end. |
| S87 | GROW_BED→CRYO_O2 | — | present | — | Capture. Not a vent. Not hab air into a process header. |
| S88 | CRYO_N2→GROW_BED | — | present | — | Make-up from the N2 box only. |
