# MVS checklist

Superseded by `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). This page is kept as history; open work is tracked there only.

Queue: `docs-authority/internal/MASTER_PLAN.md` (AQS-PLAN-004). This page is history.

Document: AQS-MVS-CHK-001
Date: 2026-10-02; updated 2026-10-08 (graph Rev M)
Plan: docs-authority/internal/MVS_PLAN.md
Graph topology is the baseline. Check an item only when the solid or the number exists.

## Nodes

- [x] WS_PHOS node added, 800×800×1100
- [x] WS_PHOS bund separate from HF
- [x] S34 split shows phosphoric etch on WS_PHOS

## EW aisle

- [x] ew_cascade_present.py run on the operator box
- [x] ew_cascade.FCStd written
- [x] plant.FCStd not opened by that run
- [x] EW-1 through EW-9, each 600×420×650, at 750 mm pitch
- [x] Overflow order EW-1 → EW-9 → polish confirmed on the solid
- [x] ew_cascade.step re-exported with the nine cells, eight launders, POLISH_BANK, and the EW-9 → polish pipe (2026-10-07)

## Machines

- [x] GLASS_RINSE 1200×600×800 and nozzles
- [x] GLASS_MILL 800×600×800 and nozzles
- [x] GLASS_BURNOUT 800×600×1200 and nozzles
- [x] Burnout off-gas on the oil-vapor header
- [x] Glass order is rinse, drain, mill, burnout, existing digest
- [x] VCD-COMP-01 1400×600×1200, 14–20 kWh/m³ at 0.11 m³/d
- [x] VCD feed re-rated: 0.283 m³/d at Rev M rates (S13 + S29 + S98); VCD-COMP-01 re-issued at 0.40 m³/d, 0.20 kW average (AQS-DUTY-011 §4.8)
- [x] VCD equipment ID issued
- [x] REMIN-01 600×400×800, hydroxide crib
- [x] REMIN 10 L/d, 25 mg/L Ca, 10 mg/L Mg
- [x] UV after the remineralizer dose
- [x] LITHO_COAT 600×500×800, ALIGN 500×500×800, DEV 500×500×800
- [x] Wafer starts/day locked in the 1–5 band
- [x] UV lamp class selected
- [x] ELC-BOOTH-01 1200×800×1800, carbon or nickel
- [x] Electrode exhaust to MET_AHU
- [x] BLOW-01 1200×800×1600, peak 2–4 kW
- [x] Blow-mold scrap to the oil line
- [x] PV-CELL-01 2400×1200×1600: texture, emitter, PSG etch, ARC, contact, fire, IV
- [x] Solar train uses WS_KOH and is not the yard array
- [x] GEO_ORC pad remains empty

## Ladder

- [x] Q1_A 800×800×1200, oil, 0.30 m³, 250 °C, 1/2 in relief
- [x] Q1_B 800×800×1200, oil, 0.30 m³, 250 °C, 1/2 in relief
- [x] Q2_A 800×800×1200, oil, 0.30 m³, 150 °C, 1/2 in relief
- [x] Q2_B 800×800×1200, oil, 0.30 m³, 150 °C, 1/2 in relief
- [x] Q3_A 800×800×1200, water, 0.40 m³, 100 °C, 1/2 in relief
- [x] Q3_B 800×800×1200, water, 0.40 m³, 100 °C, 1/2 in relief
- [x] Q4_A 800×800×1200, water, 0.60 m³, 70 °C, 1/2 in relief
- [x] Q4_B 800×800×1200, water, 0.60 m³, 70 °C, 1/2 in relief
- [x] One thermosyphon per step
- [x] Q1 fluid is oil or ceramic
- [x] Q4 fluid is water
- [x] Q1 relief is not a hab vent
- [x] HL-* edge duties, media, temperatures, flows, and line sizes (AQS-DUTY-008)
- [x] Ladder energy balance closes, both ladders and single ladder
- [x] S67B CO2-rich cut defined (VSA at FLUE_KO, 12.75 kg/d CO2)
- [x] HX-8 tier: moved to Q4 (HL-HX8-Q4-A/B), 4.57 kW, Q4 return 45 → 49 °C, 6 K approach (AQS-DUTY-008 Rev B §13.1)
- [x] S18 and S67B: S67B carries the claim (12.75 kg/d); S18 at 0 kg/d, edge kept; CRYO_CO2 balanced (§13.3)
- [x] Q3 draws HX-4/HX-5/HX-6 are graph edges with duties 0.242 / 6.353 / 1.663 kW (§13.2)
- [x] Ladder balance closes running and idle, both ladders and single ladder (residual 0.000 kW)
- [x] Cross-tie coils fit inside the stores (Q2 on low-fin tube) (§13.5)
- [x] Leach heater HX-5 rated 6.0 kW (rating case 4.60 kW × 1.25: no Q3, no Q4 preheat, no oxidant credit); normal trim 0.43 kW with HX-9 and the Cl₂/O₂ oxidant credit. R-1 not adopted (CONTINUOUS_RECYCLE lock) (AQS-DUTY-011 §4.13)
- [x] Digest heater HX-6 rated 2.5 kW (1.663 kW × 1.25); normal trim 0.80 kW with HX-10 caustic preheat; 1.5 kW study class retired (AQS-DUTY-011 §4.14)
- [x] HDR_CO2 consumer: S89 HDR_CO2 → GROW_BED 11.616 kg/d, farm enrichment at 1000 ppm, DN15 316L at 3.0 bar a; MeOH rejected (H₂-limited) (AQS-DUTY-009)
- [x] Hab metabolic CO₂ on the graph: S90 HABITATION → HDR_CO2 4.021 kg/d; S89 15.637 kg/d; farm OA 933.5 m³/h (AQS-DUTY-009 Rev B)
- [x] Q4 bus closed: sources 4.49 kW (S53 0 with the fuel cell on standby) to life 3.0 kW, HX-9 leach make-up preheat S100 0.53 kW, HX-10 caustic preheat S101 0.28 kW, borefield S102 0.67 kW. ORC pad stays at 0 kW (AQS-DUTY-011 §4.15)
- [x] Thermosyphon rise: downhill steps gravity on stepped stores (Q2 −5150, Q3 −4250, Q4 −3350), rise 0.30–0.33 m, Δp/head ≤ 0.23; cross-ties pumped loops XL-Q1..Q4, 4–29 W, normally off (AQS-DUTY-008 Rev C §14)
- [ ] Store stands (up to 2.65 m) and access platform designed
- [ ] Cross-tie pumps selected (XL-Q1/Q2 high-temperature magnetic drive)

## Edge rates and conservation (AQS-DUTY-010)

- [x] Every present edge rated with rate_basis / rate_source in params: 0 present edges unrated (graph Rev L)
- [x] Placeholders closed: 16 made present, 4 retired (IA-POL-01, S48, IA-ESS-MEOH-CHG/DIS), S87/S88 back to placeholder on HOLD with the reason on the edge
- [x] Node conservation run at ±1 %: 88 balances, 68 closed, 9 closed with one by-difference term, 11 open
- [x] H2_DRYER / CRYO_H2: S05 retired (alias of S64); Faraday H₂ 0.334 kg/d, 0.322 kg/d collected; all H₂ to MeOH, FC and GEN on standby (provisional) (AQS-DUTY-011 §4.1–4.3)
- [x] S12 → GREY_TREAT; NUTRIENT_DOSE takes S30 only (AQS-DUTY-011 §4.4)
- [x] BMED_UPW_POLISH closed: S25 from VCD covers S01, fab UPW, REMIN and reject; excess water exported as S99 (AQS-DUTY-011 §4.8)
- [x] CRU / BMED_ACID / BMED_BASE: brine bleed IA-BMED-05 to SALT_FEED; BMED 979 mol/d (6.55 kW DC); HCl IA-BMED-06 to CONTINUOUS_RECYCLE; NaOH to digest (S91), ALK (IA-BMED-07) and SALT_FEED (IA-BMED-10); Cl, Na and electron balances close (provisional Option B) (AQS-DUTY-011 §4.6)
- [x] SOL_ARK_60K: S93 PV, S94 LOAD_AGG, daily-average S17, S20 reversed; utility import 40.0 kW average closes the bus (AQS-DUTY-011 §4.9)
- [x] ZNBR2: purge-air water loss replaces the Rev L condensation; no accumulation (AQS-DUTY-011 §4.10)
- [x] AFTERBURNER CO₂: S11 carbon folded into the basis (15.554 kg/d) (AQS-DUTY-011 §4.11)
- [x] Node conservation (graph Rev M): 94 balances, 74 closed, 20 closed with one by-difference term, 0 open; 9 species checks close (AQS-DUTY-011)
- [ ] Energy surplus: utility import 40.0 kW average on the design day; MVS energy-surplus criterion not met
- [ ] REQ-MEOH-FC 0.5–2 kW not met (MEOH_FC 0.10 kW, H₂-limited)
- [ ] Required studies RS-LEACH-H2, RS-HAB-N2, RS-RESIDUE-TCLP, RS-DSP, RS-CL2-SPARGE, RS-GHEX-RECHARGE (AQS-DUTY-011 §6)

## Fab room

- [x] ISO 14644 class written on the wet bench
- [x] ISO 14644 class written on the tool row

## Placement

- [x] Generator envelope 2000×1000×1600 on the copy
- [x] Fuel-cell envelope 1800×800×1600 on the copy
- [x] Methanol skids 2200×900×1400, 2200×900×1400, 800×800×1100, 1800×800×1600 on the copy
- [x] flow_to_cad.py run against a copy
- [x] plant.FCStd unchanged
- [x] Seed Rev F: BACKUP_GEN × FUEL_CELL and MEOH_SYNTH × MEOH_TANK resolved by origin moves; issued sizes unchanged
- [x] No pair of the 65 seed unit boxes intersects (all 2080 pairs checked)
- [x] Moved boxes keep 600 mm to every neighbour; BACKUP_GEN and FUEL_CELL keep 1100 mm on all faces (NEC 110.26 figure in seed rules)
- [x] FUEL_CELL south (O2) face 7700 mm from BACKUP_GEN, above the 7620 mm oxidizer separation without a 1 h wall
- [x] GEO_ORC pad stays empty; nearest box 700 mm
- [x] Glass envelopes (rinse, mill, burnout) at issued size on the copy
- [x] Seed Rev G: Q1_A..Q4_B reissued (Rev F study origins hit LEACH_CSTR_1, BMED_REGEN and the core); ladder A west wall y 9000, ladder B north-east bay y 15000
- [x] Ladder stores ≥ 700 mm from same-level equipment and walls on the placed copy; 0 intersections; seed all-pairs 0 of 2080
- [x] Ladder stores carried as issued envelopes on `plant_placed_2026-10-07_revJ.FCStd` (`--create-issued-only`)
- [x] Seed Rev H: ladder stores stepped; rows for WS_PHOS, LITHO bench + COAT/ALIGN/DEV, VCD_TRAIN, REMIN, ELECTRODE_COAT, BLOW_MOLD, SOLAR_PV_CELL, HX8, NOX_SCRUB, MEOH_COND, RELIEF_CRYO, CONTINUOUS_RECYCLE; record rows CATCH_TANK, FLUE_KO, RELIEF_H2
- [x] Seed all-pairs: 72 boxes, 2556 pairs, 0 intersections; new and moved rows ≥ 600 mm within a level (lines and the LITHO group: no overlap); GEO_ORC pad empty
- [x] CATCH_TANK stays at L-2 (pumped-hydro lower reservoir); only slab crossing is SHAFT_PENSTOCK; no ladder drain into it
- [x] Rev K copy `plant_placed_2026-10-07_revK.FCStd`: new solids 0 intersections with the copy; plant.FCStd unchanged
- [x] Seed Rev I: the 20 seed pairs under 600 mm resolved by origin moves; WS_* and FAB_UPW_TANK out of the FAB blocks, PV stubs and core into two tote rows; H2_STACK clear of RACK_OIL; FLUE_CAP clear of VJ_001; S13_CLASS_TREAT, BMED_UPW_POLISH, MET_*, CRYO_AHU_COND, CRYO_HX_Q4, GREY_TREAT, BLACK_DIGEST clear of legacy Features
- [x] Seed all-pairs (Rev I): 71 boxes, 2485 pairs, 0 intersections, 0 pairs under 600 mm within a level (1100 mm at BACKUP_GEN / FUEL_CELL)
- [x] Rev M copy `plant_placed_2026-10-08_revM.FCStd` from the revK copy: every moved Feature lands on its seed origin; moved rows have 0 intersections and ≥ 600 mm to same-level equipment, except MET_AHU / MET_SCRUB on the mis-drawn OVERFLOW_APRON_E
- [ ] Legacy massing, all-pairs common volume on the Rev M copy: 423 solids, 1016 intersecting pairs (1075 on revK); 208 classed as clashes (245 on revK), 210 for review. Open in RS-CAD-HYDRO (CATCH_TANK, HYDRO_SET, ROOF_TANK vs cores), RS-CAD-YARD (GH_ENV_W and un-moved yard sub-features) and RS-CAD-LEGACY (L-1 corridors through the process aisle, oil-line and PK massing, FAB_PREP in CORE_PROCESS, GROW_BED in STAIR_S2, aprons inside the E/W walls)
- [ ] SOLAR_PV_CELL envelope vs the wafer_fab PV_* stubs: SOLAR_PV_CELL governs (graph node, issued envelope); PV_* stubs are superseded legacy massing, left on the copy pending removal (provisional)

## Done

- [x] Every present node has a solid, is a header, or is a logical boundary: 112 solid, 8 header, 2 boundary (BOUNDARY_EXPORT, LOAD_AGG), 0 fail (graph Rev K, copy revK)
- [x] Done test on graph Rev L, copy revK: 112 solid, 8 header, 2 boundary, 0 fail
- [ ] loops_closed still false. Graph Rev M closes every node balance and retires S87/S88; still open: energy surplus (utility import), REQ-MEOH-FC, the provisional decisions and required studies of AQS-DUTY-011, and the legacy CAD studies above
