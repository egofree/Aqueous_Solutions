# Mass-flow claim excerpt — DERIVED from flow_graph

Document number: AQS-MF-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev M (`plant_flow_graph.json`)
Generated: 2026-10-08
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/MASS_FLOW.md`.
Only namespace=S and SANDBOX mass-layer edges listed (MFD campus view).

| ID | Route | Claim status | Presence | Rate | Notes |
|---|---|---|---|---|---|
| DOCK_EXPORT_TBD | NORTH_DOCK→BOUNDARY_EXPORT | — | present | 40.7542 kg/d | Audit §7.1 DOCK export — sector required; no inter-block stream ID issued |
| S01 | BMED_UPW_POLISH→HDR_UPW | Closed | present | 77.2764 kg/d | — |
| S02 | CRYO_O2→HABITATION | Closed | present | 3.36 kg/d | — |
| S03 | CRYO_N2→WAFER_FAB | — | present | 1.4998 kg/d | Was wrongly sourced from CRYO_H2. |
| S04 | CRYO_CO2→GROW_BED | Closed / Claimed | present | 1.109 kg/d | — |
| S07 | NUTRIENT_DOSE→GROW_BED | Closed | present | 22.1949 kg/d | — |
| S08 | LEACH_CSTR_1→MFG_SHOP | Closed | present | 42.0 kg/d | — |
| S08G | GLASS_DIGEST→BOUNDARY_EXPORT | — | present | 4.5 kg/d | candidate_mvs extension — do not invent new register ID |
| S09 | BMED_ACID→WET_BENCH | — | present | 9.2772 kg/d | Acid to bench. Polish is not this edge. |
| S10 | WET_BENCH→LEACH_CSTR_1 | Closed | present | 78.3397 kg/d | — |
| S11 | GROW_BED→AFTERBURNER | Closed | present | 0.8 kg/d | — |
| S12 | HABITATION→GREY_TREAT | Closed | present | 114.9 kg/d | Rev M: retargeted from NUTRIENT_DOSE. Grey and AHU condensate go to grey treat -> VCD (S29); solids and nutrients reach the farm via BLACK_DIGEST (S30). |
| S13 | GROW_BED→VCD_TRAIN | Closed | present | 29.9068 kg/d | From register: FARM SUMP + HVAC → UPW POLISH / SALT FEED / VCD_FEED |
| S14 | GROW_BED→HABITATION | Closed | present | 2.4 kg/d | — |
| S14X | GROW_BED→BOUNDARY_EXPORT | — | present | 1.8 kg/d | candidate_mvs extension — do not invent new register ID |
| S15 | GROW_BED→HABITATION | Closed | present | 0.0 kg/d | — |
| S16 | MFG_SHOP→LEACH_CSTR_1 | Closed | present | 12.6 kg/d | — |
| S18 | AFTERBURNER→CRYO_CO2 | Retired (Rev J): carbon counted once on S67 -> FLUE_KO -> S67B | present | 0.0 kg/d | Retired carbon credit (AQS-DUTY-008 Rev B s13.3). Not deleted: other locks name S18. |
| S19 | BAGHOUSE→LEACH_CSTR_1 | Closed | present | 0.75 kg/d | From register: BAGHOUSE fines → LEACH CSTR 1 |
| S21 | ROOF_TANK→HABITATION | Closed | present | 120.0 kg/d | — |
| S24 | H2_DRYER→RELIEF_H2 | — | present | 0.0 kg/d | NFPA 2 relief. Not freight. |
| S25 | VCD_TRAIN→BMED_UPW_POLISH | Closed | present | 150.28 kg/d | — |
| S26 | REMIN→HABITATION | Closed | present | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK→WET_BENCH | Closed | present | 60.0 kg/d | From register: FAB_UPW_TANK → WET_BENCH |
| S28 | VCD_TRAIN→LEACH_CSTR_1 | Closed | present | 28.3179 kg/d | — |
| S29 | GREY_TREAT→VCD_TRAIN | Closed | present | 109.15 kg/d | From register: GREY_TREAT → VCD_FEED / SALT FEED |
| S30 | BLACK_DIGEST→NUTRIENT_DOSE | Closed | present | 22.1749 kg/d | From register: BLACK_DIGEST → NUTRIENT DOSE / SALT FEED |
| S31 | WS_HF_ED→WET_BENCH | Closed / Claimed | present | 1.5 kg/d | From register: WS_HF_ED → WET_BENCH |
| S32 | WS_PEROX→WET_BENCH | Claimed | present | 3.0 kg/d | From register: WS_PEROX → WET_BENCH |
| S33 | WS_AMMONIA→WET_BENCH | Claimed | present | 3.0 kg/d | From register: WS_AMMONIA → WET_BENCH |
| S35 | WS_KOH→WET_BENCH | Claimed | present | 0.2725 kg/d | From register: WS_KOH → WET_BENCH / solar texture stub |
| S36 | WS_DOPE→WAFER_FAB | Claimed | present | 0.01 kg/d | From register: WS_DOPE / CRU polish → FAB_TOOL dopant cabinets |
| S37 | WS_SLURRY→WAFER_FAB | Claimed | present | 3.3 kg/d | From register: WS_SLURRY → LAP_CMP / FAB_PREP |
| S38 | WET_BENCH→OIL_FRAC | — | present | 0.006 kg/d | Waste leaves the bench. |
| S39 | WAFER_FAB→LEACH_CSTR_1 | — | present | 3.31 kg/d | NFPA 400: no organics into chlorate leach. |
| S39B | WAFER_FAB→OIL_FRAC | — | present | 0.9875 kg/d | Organics to the oil line. |
| S40 | ROOF_TANK→TERRACE_IRRIG | Closed | present | 0.0 kg/d | — |
| S41 | TERRACE_IRRIG→CATCH_TANK | Closed | present | 0.0 kg/d | From register: TERRACE underdrain / apron (clean) → CATCH TANK / DRAIN_SEC |
| S42 | TERRACE_IRRIG→GREY_TREAT | Closed / Claimed | present | 0.0 kg/d | From register: Enclosed terrace / GH fertigated drain → GREY treat / VCD_FEED / SALT |
| S43 | GEO_GHEX→GEO_HP_CLOSED_LOOP | Closed | present | 0.0 kW | From register: GEO_GHEX → GEO_HP (closed loop) |
| S45 | CRYO_H2→BACKUP_GEN | Claimed / Partial | present | 0.0 kg/d | — |
| S46 | BACKUP_GEN→NOX_SCRUB | — | present | 0.0 kg/d | NFPA 37 exhaust. Not life water. |
| S49 | CRYO_H2→FUEL_CELL | Claimed / Partial | present | 0.0 kg/d | — |
| S50 | CRYO_O2→FUEL_CELL | Claimed | present | 0.0 kg/d | — |
| S52 | FUEL_CELL→VCD_TRAIN | Claimed | present | 0.0 kg/d | — |
| S55 | CRYO_DED_COOL→CRYO_DED_COOL | Closed | present | 4.0606 kW | From register: CRYO_DED_COOL (loop) → CRYO_DED_COOL |
| S56 | CRYO_AHU→RELIEF_CRYO | — | present | 0.0 kg/d | NFPA 55 relief. Not freight. |
| S57 | MET_MELT→WIRE_DRAW | Closed | present | 4.3789 kg/d | From register: PROD_METALS / MET_MELT → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER |
| S58 | WIRE_DRAW→MFG_SHOP | Closed | present | 3.941 kg/d | From register: WIRE_DRAW → MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB |
| S59 | COLD_MILL→MFG_SHOP | Closed | present | 3.9529 kg/d | From register: COLD_MILL → MET_SHEET_BIN / MFG_CRIB |
| S60 | GAS_ATOMIZER→MFG_SHOP | Closed / Claimed | present | 3.1999 kg/d | From register: GAS_ATOMIZER → MET_POWDER_CRIB / FAB / RepRap |
| S61 | MFG_SHOP→HOPPER | Closed | present | 1.1971 kg/d | From register: Forming swarf / trim → HOPPER / leach |
| S62 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 2131.07 kg/h | From register: MET_AHU → MET_SCRUB / baghouse (S71) |
| S64 | H2_DRYER→CRYO_H2 | Partial | present | 0.3221 kg/d | — |
| S65 | ALK_SCRUBBER→ACID_POLISH_SCRUB | — | present | 1562.91 kg/h | Not a self-loop. Polish then CRU via S66. |
| S66 | ACID_POLISH_SCRUB→CRU | Claimed | present | 0.3868 kg/d | From register: ACID_POLISH / ALK blowdown → CRU |
| S67 | AFTERBURNER_FLUE→FLUE_KO | — | present | 242.48 kg/d | Knockout before any CO2 claim. |
| S67B | FLUE_KO→CRYO_CO2 | Claimed | present | 13.2209 kg/d | Only the CO2-rich cut. Reject N2/O2/NOx. AQS-DUTY-008. |
| S68 | CRYO_AHU→LEACH_CSTR_1 | — | present | 173.67 kg/d | Rev M: text corrected. Coil condensate from the cryo room AHU; may carry acid trace from the flue-cap zone, so it stays process (to leach). Not flue condensate (flue condensate is the FLUE_KO knockout). |
| S69 | ZNBR2→ZNBR2_BR2_REGEN | — | present | 854.85 kg/d | Own tower. |
| S69B | ZNBR2_BR2_REGEN→ZNBR2 | — | present | 0.0473 kg/d | Return to the bromine tank only. |
| S70 | CRYO_AHU_COND_CONDENSABLE→FLUE_KO | — | present | 0.0521 kg/d | Not into the hydrogen box. |
| S71 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 852.43 kg/h | From register: MET_AHU → MET_SCRUB / baghouse |
| S72 | MET_SCRUB→LEACH_CSTR_1 | — | present | 2.4366 kg/d | Fines only. |
| S72B | MET_SCRUB→OIL_FRAC | — | present | 0.0158 kg/d | Organics off the metal scrub, to oil. |
| S73 | CRYO_CO2→MEOH_SYNTH | — | present | 2.3436 kg/d | — |
| S74 | CRYO_H2→MEOH_SYNTH | — | present | 0.3221 kg/d | — |
| S75 | MEOH_SYNTH→MEOH_TANK | — | present | 1.7063 kg/d | — |
| S77 | MEOH_FERM→MEOH_TANK | — | present | 0.0146 kg/d | From register: MEOH_FERM_STILL → MEOH_TANK |
| S78 | HABITATION→MEOH_FERM | — | present | 0.36 kg/d | From register: Farm/hab organics (S12/S30 class) → MEOH_FERM_DIG |
| S81 | MEOH_FC→MEOH_COND | — | present | 1.935 kg/d | Methanol residual stays process. |
| S82 | MEOH_FC→CRYO_CO2 | — | present | 2.3636 kg/d | From register: MEOH_FC / MEOH_VENT_KO → CRYO_CO2 / FARM (Claimed) |
| S83 | CRYO_O2→HDR_O2 | — | present | 4.3108 kg/d | Life header fill. Not the dock. |
| S84 | CRYO_N2→HDR_N2 | — | present | 0.0 kg/d | Life header fill. Not the dock. |
| S85 | CRYO_CO2→HDR_CO2 | — | present | 12.0799 kg/d | Life header fill. Not the dock. |
| S34 | WS_NITRIC→WET_BENCH | — | present | 0.665 kg/d | Nitric only. |
| S34B | WS_PHOS→WET_BENCH | — | present | 0.625 kg/d | Phosphoric etch. Own bund. |
| S89 | HDR_CO2→GROW_BED | Closed | present | 16.1009 kg/d | Only consumer of HDR_CO2. CO2 only: no tee to HDR_O2, hab air, the HAB return or the dock. Farm AHU is not the HAB AHU. |
| S90 | HABITATION→HDR_CO2 | Closed | present | 4.021 kg/d | Rev L. CO2 only, from the sealed-hab sorbent (S02 supplies the O2). Joins S85 on HDR_CO2; S89 carries both to the farm AHU dose. No tee to hab air or the dock. |
| S91 | BMED_BASE→GLASS_DIGEST | Closed | present | 320.76 kg/d | Rev M. Was off-graph in Rev L (DUTY-008 593 mol/d). |
| S92 | GLASS_DIGEST→SALT_FEED | Closed | present | 325.96 kg/d | Rev M. Joins the bleed before the silica drop (aem_bank.md). |
| S95 | HDR_O2→LEACH_CSTR_1 | Closed | present | 4.3108 kg/d | Rev M. Process O2 from HDR_O2 only; no tee to hab air. Supplies the oxidant the anode Cl2 and chlorate do not. |
| S96 | GLASS_RINSE→BOUNDARY_EXPORT | Closed | present | 34.2915 kg/d | Rev M. TCLP / leachate characterization required before disposal or sale (REV_M_CLOSURE_DUTY.md). |
| S97 | SALT_FEED→BOUNDARY_EXPORT | Closed | present | 91.0768 kg/d | Rev M. Filter cake from the silica / hydroxide drop at pH 9. |
| S98 | SALT_FEED→VCD_TRAIN | Closed | present | 144.12 kg/d | Rev M. Water exit of the chloride loop; VCD distils it, brine returns on S28. |
| S99 | VCD_TRAIN→BOUNDARY_EXPORT | Closed | present | 104.58 kg/d | Rev M. Distillate above the UPW polish demand (AQS-SUR-001 clean water). |
