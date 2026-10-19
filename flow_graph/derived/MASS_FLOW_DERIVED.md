# Mass-flow claim excerpt — DERIVED from flow_graph

Document number: AQS-MF-001-DERIVED
Source: AQS-FLOW-GRAPH-001 Rev AC (`plant_flow_graph.json`)
Generated: 2026-10-19
Licence: CERN-OHL-S-2.0

**Not** the legacy master while migration is incomplete — compare to `cad/MASS_FLOW.md`.
Only namespace=S and SANDBOX mass-layer edges listed (MFD campus view).

| ID | Route | Claim status | Presence | Rate | Notes |
|---|---|---|---|---|---|
| DOCK_EXPORT_TBD | NORTH_DOCK→BOUNDARY_EXPORT | — | placeholder | 0.0 kg/d | Audit §7.1 DOCK export — sector required; no inter-block stream ID issued |
| S01 | BMED_UPW_POLISH→HDR_UPW | Closed | present | 67.300214 kg/d | — |
| S02 | CRYO_O2→HABITATION | Closed | present | 3.4 kg/d | — |
| S03 | CRYO_N2→WAFER_FAB | — | present | 1.499799 kg/d | Was wrongly sourced from CRYO_H2. |
| S04 | CRYO_CO2→GROW_BED | Closed / Claimed | present | 0.0 kg/d | — |
| S07 | NUTRIENT_DOSE→GROW_BED | Closed | present | 2.5 kg/d | — |
| S08 | LEACH_CSTR_1→MFG_SHOP | Closed | present | 41.996408 kg/d | — |
| S08G | GLASS_DIGEST→MFG_SHOP | — | present | 26.7 kg/d | candidate_mvs extension — do not invent new register ID |
| S09 | BMED_ACID→WET_BENCH | — | present | 9.277184 kg/d | Acid to bench. Polish is not this edge. |
| S10 | WET_BENCH→LEACH_CSTR_1 | Closed | present | 79.115777 kg/d | — |
| S11 | GROW_BED→AFTERBURNER | Closed | present | 0.8 kg/d | — |
| S12 | HABITATION→GREY_TREAT | Closed | present | 319.60396 kg/d | — |
| S13 | GROW_BED→VCD_TRAIN | Closed | present | 3.799494 kg/d | From register: FARM SUMP + HVAC → UPW POLISH / SALT FEED / VCD_FEED |
| S14 | GROW_BED→FOOD_STORE | Closed | present | 4.2 kg/d | — |
| S15 | GROW_BED→HABITATION | Closed | present | 0.0 kg/d | — |
| S16 | MFG_SHOP→LEACH_CSTR_1 | Closed | present | 12.299499 kg/d | — |
| S18 | AFTERBURNER→CRYO_CO2 | Claimed | present | 0.0 kg/d | — |
| S19 | BAGHOUSE→LEACH_CSTR_1 | Closed | present | 0.0 kg/d | From register: BAGHOUSE fines → LEACH CSTR 1 |
| S21 | ROOF_TANK→HABITATION | Closed | present | 120.68 kg/d | — |
| S24 | H2_DRYER→RELIEF_H2 | — | present | 0.0 kg/d | NFPA 2 relief. Not freight. |
| S25 | VCD_TRAIN→BMED_UPW_POLISH | Closed | present | 308.578502 kg/d | presence placeholder->present (both endpoints live); per first-principles audit correction 1, owner rulings 2026-10-18 |
| S26 | REMIN→HABITATION | Closed | present | 10.0 kg/d | — |
| S27 | FAB_UPW_TANK→WET_BENCH | Closed | present | 60.000181 kg/d | From register: FAB_UPW_TANK → WET_BENCH |
| S28 | VCD_TRAIN→LEACH_CSTR_1 | Closed | present | 17.877059 kg/d | presence placeholder->present (both endpoints live); per first-principles audit correction 1, owner rulings 2026-10-18 |
| S29 | GREY_TREAT→VCD_TRAIN | Closed | present | 104.499999 kg/d | From register: GREY_TREAT → VCD_FEED / SALT FEED. presence placeholder->present (both endpoints live); per first-principles audit correction 1, owner rulings 2026-10-18 |
| S30 | BLACK_DIGEST→NUTRIENT_DOSE | Closed | present | — | From register: BLACK_DIGEST → NUTRIENT DOSE / SALT FEED |
| S31 | WS_HF_ED→WET_BENCH | Closed / Claimed | present | 1.5 kg/d | From register: WS_HF_ED → WET_BENCH |
| S32 | WS_PEROX→WET_BENCH | Claimed | present | 3.0 kg/d | From register: WS_PEROX → WET_BENCH |
| S33 | WS_AMMONIA→WET_BENCH | Claimed | present | 3.008739 kg/d | From register: WS_AMMONIA → WET_BENCH |
| S35 | WS_KOH→WET_BENCH | Claimed | present | 0.2701 kg/d | From register: WS_KOH → WET_BENCH / solar texture stub |
| S36 | WS_DOPE→WAFER_FAB | Claimed | present | 0.0 kg/d | From register: WS_DOPE / CRU polish → FAB_TOOL dopant cabinets |
| S37 | WS_SLURRY→WAFER_FAB | Claimed | present | 3.3 kg/d | From register: WS_SLURRY → LAP_CMP / FAB_PREP |
| S38 | WET_BENCH→OIL_FRAC | — | present | 0.006 kg/d | Waste leaves the bench. |
| S39 | WAFER_FAB→LEACH_CSTR_1 | — | present | 3.310001 kg/d | NFPA 400: no organics into chlorate leach. |
| S39B | WAFER_FAB→OIL_FRAC | — | present | 0.0 kg/d | Organics to the oil line. |
| S43 | GEO_GHEX→GEO_HP_CLOSED_LOOP | Closed | present | 0.0 kW | From register: GEO_GHEX → GEO_HP (closed loop) |
| S45 | CRYO_H2→BACKUP_GEN | Claimed / Partial | present | 0.0 kg/d | — |
| S46 | BACKUP_GEN→NOX_SCRUB | — | present | 0.267975 kg/d | NFPA 37 exhaust. Not life water. |
| S49 | CRYO_H2→FUEL_CELL | Claimed / Partial | present | 4.8 kg/d | — |
| S50 | CRYO_O2→FUEL_CELL | Claimed | present | 38.4 kg/d | — |
| S52 | FUEL_CELL→VCD_TRAIN | Claimed | present | 42.876623 kg/d | presence placeholder->present (both endpoints live); per first-principles audit correction 1, owner rulings 2026-10-18 |
| S55 | CRYO_DED_COOL→CRYO_DED_COOL | Closed | present | 4.2838 kW | From register: CRYO_DED_COOL (loop) → CRYO_DED_COOL |
| S56 | CRYO_AHU→RELIEF_CRYO | — | present | 0.0 kg/d | NFPA 55 relief. Not freight. |
| S57 | MET_MELT→WIRE_DRAW | Closed | present | 6.8389 kg/d | From register: PROD_METALS / MET_MELT → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER |
| S58 | WIRE_DRAW→MFG_SHOP | Closed | present | 3.9389 kg/d | From register: WIRE_DRAW → MET_WIRE_BIN / ELECTRODE_FAB / MFG_CRIB |
| S59 | COLD_MILL→MFG_SHOP | Closed | present | 3.950359 kg/d | From register: COLD_MILL → MET_SHEET_BIN / MFG_CRIB |
| S60 | GAS_ATOMIZER→MFG_SHOP | Closed / Claimed | present | 3.200359 kg/d | From register: GAS_ATOMIZER → MET_POWDER_CRIB / FAB / RepRap |
| S61 | MFG_SHOP→HOPPER | Closed | present | 1.197099 kg/d | From register: Forming swarf / trim → HOPPER / leach |
| S62 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 51145.68 kg/d | From register: MET_AHU → MET_SCRUB / baghouse (S71) |
| S64 | H2_DRYER→CRYO_H2 | Partial | present | 1.975408 kg/d | S05 deleted as a duplicate parallel edge (same H2_DRYER->CRYO_H2 4.8 kg/d authority pool; Rev M retired S05 as an alias of S64, CO2_HEADER_DUTY AQS-DUTY-011); per first-principles audit correction 5, owner rulings 2026-10-18 |
| S65 | ALK_SCRUBBER→ACID_POLISH_SCRUB | — | present | 37509.8546 kg/d | Not a self-loop. Polish then CRU via S66. |
| S66 | ACID_POLISH_SCRUB→CRU | Claimed | present | 27.372033 kg/d | From register: ACID_POLISH / ALK blowdown → CRU |
| S67 | AFTERBURNER_FLUE→FLUE_KO | — | present | 117.42759 kg/d | Knockout before any CO2 claim. |
| S67B | FLUE_KO→CRYO_CO2 | — | present | 14.050492 kg/d | Only the CO2-rich cut. Reject N2/O2/NOx. |
| S68 | CRYO_AHU→LEACH_CSTR_1 | — | present | 78.987901 kg/d | Acid condensate stays process. |
| S69 | ZNBR2→ZNBR2_BR2_REGEN | — | present | 752.327603 kg/d | Own tower. |
| S69B | ZNBR2_BR2_REGEN→ZNBR2 | — | present | 752.327603 kg/d | Return to the bromine tank only. |
| S70 | CRYO_AHU_COND_CONDENSABLE→FLUE_KO | — | present | 0.0521 kg/d | Not into the hydrogen box. |
| S71 | MET_AHU→MET_SCRUB | Partial / Claimed | present | 20458.32 kg/d | From register: MET_AHU → MET_SCRUB / baghouse |
| S72 | MET_SCRUB→LEACH_CSTR_1 | — | present | 2.4442 kg/d | Fines only. |
| S72B | MET_SCRUB→OIL_FRAC | — | present | 0.0158 kg/d | Organics off the metal scrub, to oil. |
| S73 | CRYO_CO2→MEOH_SYNTH | — | present | 44.423559 kg/d | — |
| S74 | CRYO_H2→MEOH_SYNTH | — | present | 6.536155 kg/d | — |
| S75 | MEOH_SYNTH→MEOH_TANK | — | present | 34.6293 kg/d | — |
| S76 | MEOH_TANK→MEOH_FC | — | present | 5.0 kg/d | — |
| S77 | MEOH_FERM→MEOH_TANK | — | present | 0.0146 kg/d | From register: MEOH_FERM_STILL → MEOH_TANK |
| S78 | HABITATION→MEOH_FERM | — | present | 0.36 kg/d | From register: Farm/hab organics (S12/S30 class) → MEOH_FERM_DIG |
| S81 | MEOH_FC→MEOH_COND | — | present | 7.251023 kg/d | Methanol residual stays process. |
| S82 | MEOH_FC→CRYO_CO2 | — | present | 8.625641 kg/d | From register: MEOH_FC / MEOH_VENT_KO → CRYO_CO2 / FARM (Claimed) |
| S83 | CRYO_O2→HDR_O2 | — | present | 33.195501 kg/d | Life header fill. Not the dock. |
| S84 | CRYO_N2→AIR_RECEIVER | — | present | 191.989014 kg/d | Life header fill. Not the dock. |
| S85 | CRYO_CO2→HDR_CO2 | — | present | 0.0 kg/d | Life header fill. Not the dock. |
| S86 | CRYO_AHU→RELIEF_CRYO | — | present | 0.0 kg/d | Same sink as S56. Issued so the old dock edge has a number and a legal end. |
| S87 | GROW_BED→CRYO_O2 | — | present | 0.641572 kg/d | Capture. Not a vent. Not hab air into a process header. |
| S88 | CRYO_N2→GROW_BED | — | present | 0.0 kg/d | Make-up from the N2 box only. |
| S34 | WS_NITRIC→WET_BENCH | — | present | 1.2456 kg/d | Nitric only. | layers/namespace restored per QA R5 (schema-required fields absent since Rev AC) |
| S34B | WS_PHOS→WET_BENCH | — | present | 0.61 kg/d | Phosphoric etch. Own bund. | layers/namespace restored per QA R5 (schema-required fields absent since Rev AC) |
| S89 | HDR_CO2→GROW_BED | Closed | present | 0.882362 kg/d | Only consumer of HDR_CO2. CO2 only: no tee to HDR_O2, hab air, the HAB return or the dock. Farm AHU is not the HAB AHU. | restored verbatim from graph Rev BH (fa1b4db) after Rev AC consolidation dropped it; both endpoint units unchanged |
| S90 | HABITATION→HDR_CO2 | Closed | present | 4.021 kg/d | Rev L. CO2 only, from the sealed-hab sorbent (S02 supplies the O2). Joins S85 on HDR_CO2; S89 carries both to the farm AHU dose. No tee to hab air or the dock. | restored verbatim from graph Rev BH (fa1b4db) after Rev AC consolidation dropped it; both endpoint units unchanged |
| S14D | FOOD_STORE→HABITATION | Closed | present | 4.2 kg/d | — |
