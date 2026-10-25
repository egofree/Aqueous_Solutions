# PV / storage / inverter / roof parametric derivation — Rev AC re-base

Document number: AQS-NOTE-PV-REBASE
Revision: A
Date: 2026-10-18
Authority: owner rule 2026-10-18 (D-PV / MASTER_PLAN D75), AGENTS.md "Self-sustaining plant"; graph Rev AC @ `64c8239`; machinery `docs-authority/_power_sizing.py`, `flow_graph/param/solver.py roof_close`, `flow_graph/param/sizing/power.py`, drivers in `flow_graph/param/drivers.json`. Analysis lane only: no graph edits, no commits, no derived-doc regeneration (tree left clean at `64c8239`). Study. Not a PE stamp.

Owner rule being implemented: *PV size is parametrically derived from the plant's required power at ≥ 200 % of required load (batteries still charge on cloudy days); roof area and building footprint are then derived from the PV size.* This is exactly the D75 chain already encoded in `pv_oversize_factor` (2.0) and `PW.oversized()`.

## 1. The chain (as implemented in the repo)

With drivers: `night_hours` N = 14 h, `storage_round_trip` η_rt = 0.70 (A-M-179), `pv_yield_kWh_kWp_d` × `pv_roof_yield_factor` = 5.41 × 1.0 kWh/kWp/d (AQS-SITE-002 / A-M-103), `pv_system_derate` = 0.80 (A-M-061), `pv_oversize_factor` = 2.0 (A-M-109, D75), `pv_dc_ac_ratio` = 1.2, inverter block 60 kW:

- balancing nameplate: `base = (P·(24−N) + P·N/η_rt) / (PSH·derate)` = P × 6.932 kWp/kW
- **PV = 2.0 × base**; array area = kWp / (module eff 0.19 × GCR 0.6) = **8.77 m²/kWp**
- night storage: **P × 14 h** out, P × 14/0.7 = P × 20 in
- half-yield-day check (cloudy = 0.5 × mean): array delivers base × PSH × derate = exactly the daily need (direct P·10 + store-in P·20), by construction; charge power = PV·derate/2 − P
- inverters: `ceil(max(PV/1.2, P)/60)`; export at noon (store full) = inverter AC − P; clear-day export = (2.0−1) × balancing energy
- footprint: `solver.roof_close` iterates the 6 m bay grid until the roof, after IFC 2027 1205.3 / NFPA 1 11.12 pathways, carries the PV — the extension's own loads (lighting/ventilation/envelope, air-source per D77) feed back into P.

## 2. Bounding electrical demand from the graph (Rev AC scope)

Rule used (documented per unit below): a unit's bounding load = **max(node `continuous_kw`, elec-edge rate)** where both exist; RECT-EW covers EW_1…EW_9 DC (their node values are excluded to avoid double count); storage-charge, curtailment and generation edges are not demand; the three foundry bare ints are included at face value per the lane instruction.

| Unit | node kW | edge kW | bound | note |
| --- | ---: | ---: | ---: | --- |
| IND_MELT | 25 | – | 25.00 | bare int; batch nameplate, no elec edge yet |
| VAC_IND | 15 | – | 15.00 | bare int; batch nameplate |
| RF_HEAT | 5 | – | 5.00 | bare int; batch nameplate |
| RECT-EW (AC) | – | – | 38.66 | `_rect_ew_sizing` bounding: 27.10 kW cell DC / 30.93 kW at bus / 0.80 eff (AQS-ELEC-004) |
| MFG_SHOP | 12.0 | 2.903 | 12.00 | node is Rev AA study share; edge is AQS-MFG-010 calc |
| RECTIFIER | 12.0 | 50.0 | 12.00 | **edge S17 = 50.0 is the `mvs.electrical.need_kw` seed (ELEC_NEED_KW_BASE), circular — not used**; node 12 kW is AQS-PWR-001 (48 V rails); possible ≤12 kW overlap with MFG_SHOP (ONE_LINE finding 3) |
| BMED_UPW_POLISH | 6.0 | 0.018 | 6.00 | node study vs AQS-DUTY-070 calc on edge |
| GROW_BED | 5.0 | null | 5.00 | owner 2026-10-18: keep + re-base; LED calc is 2.25 kW (load list) |
| CRYO_H2 | 4.0 | 0.884 | 4.00 | node = compressor P_peak; edge = AQS-DUTY-067 daily avg |
| HABITATION | 3.0 | – | 3.00 | |
| GEO_HP / LEACH_CSTR_1 / WAFER_FAB | 2.0 | 2.0 | 2.00 | agree |
| GLASS_DIGEST | 1.5 | 0.09 | 1.50 | |
| EVAP_ACID / EVAP_BASE | 1.497 / 1.324 | same | 1.497 / 1.324 | X-PAR values |
| CRYO_AHU | – | 4.440 | 4.44 | X-PAR-12 |
| OIL_PYRO | – | 1.664 | 1.66 | |
| MET_SCRUB / ACID_POLISH_SCRUB | – | 2.123 / 1.112 | 2.12 / 1.11 | |
| ALK_SCRUBBER | 0.4 | 1.112 | 1.11 | |
| WET_BENCH 1.0 · AFTERBURNER 0.5 · BLOW_MOLD 0.5 · SOLAR_PV_CELL 0.392 · H2_DRYER 0.3 · ELECTRODE_COAT 0.3 · MEOH_SYNTH 0.739 · LITHO_STUB 0.1 · NUTRIENT_DOSE 0.1 · BLACK_DIGEST 0.105 · MEOH_FERM 0.021 · NOX_SCRUB 0.039 | | | 5.12 | edge/node agree or edge-only |
| **Sum (process, max-envelope)** | | | **117.50** | |
| **+ RECT-EW 38.66 → P₀ base demand** | | | **156.16 kW** | |

Alternatives carried below: *calc-preferred* (edge where a calculated edge exists: CRYO_H2 0.884, MFG_SHOP 2.903, BMED_UPW 0.018, GLASS_DIGEST 0.09, RECTIFIER 12) → **136.55 kW**; *foundry duty-cycled* (see §7: batch nameplates are not 24 h loads; ~26 kg/d at 0.5–2 kWh/kg + RF ≈ 25–55 kWh/d ≈ 1–2.3 kW avg; run at 2.5 kW) → **113.66 kW**.

Foundry caveat: AQS-SIZE-FOUNDRY and notes/POWER_DUTIES.md both state these are batch furnaces (10 kg crucible, 1–3 heats/d, "average over the day far lower"); carrying 45 kW flat 24 h adds 1080 kWh/d vs a physical ~25–55 kWh/d. It is kept in the primary case per the lane instruction; the sensitivity shows the cost.

## 3. Reconciliation with `_power_sizing.py`'s own demand

`_power_sizing.py` (run today, unmodified) reports **bounding P = 487.60 kW**, PV 6759.7 kWp, 6826 kWh, 94 inverters, roof 64 152 m². Its demand comes from `_one_line.py` → **308.88 kW**, decomposed:

| Component | kW | status |
| --- | ---: | --- |
| elec edges fed by SOL_ARK (incl. **S17 RECTIFIER seed 50.0**, SF-* calc loads 26.10, ZNBR2 charge 6.67) | 89.06 | live graph |
| RECT-EW bounding AC row (fallback: RECT_EW node absent in Rev AC) | 38.66 | correct, counted once here |
| load-list rows whose units still exist in Rev AC (GROW_BED 2.25 calc, HABITATION 3.0, AFTERBURNER 0.5, VCD_TRAIN 0.279, WS_PEROX 0.031) | 6.06 | live |
| **stale Rev-BH rows for units deleted from Rev AC** (EXT_HALL 93.839, RECT_EW 38.663 **again**, H2O_ELYZ 24.593, farm swarm ≈13, CRYO_ASU 1.66, HAB_* 1.2, cryo-noble 1.0, SIC/EMETH/chem ≈1.4) | **175.10** | contamination |
| **One-line demand** | **308.88** | |

Then `_power_sizing` adds the converged extension load 178.72 kW (roof_close at the inflated demand) → 487.60 kW. Four mechanisms make it wrong:

1. `docs-authority/LOAD_LIST.md` is generated against **graph Rev BH** (its own authority line) and is 3 days stale: farm units cut in Rev AC, H2O_ELYZ, CRYO_ASU, HAB_* sub-meters, chem train rows.
2. **EXT_HALL double count**: the stale list carries the BH study share 93.839 kW, and with the EXT_HALL node absent the `_x` subtraction in `_power_sizing.py` L20-21 no-ops, so roof_close's own extension load is added on top of the stale one.
3. **RECT_EW double count**: 38.663 kW appears both as the one-line fallback row and as a stale load-list row.
4. The Rev AC **foundry additions are invisible** to the one-line (no elec edges, not in the BH-era list) — the one real scope increase is the only thing missing.

So: graph-native Rev AC base = **156.16 kW** vs `_power_sizing` chain input 308.88 kW (−152.7 kW, −49 %). The one-line path must be regenerated before it is used for sizing again.

## 4. D75 chain result — primary case (Rev AC scope)

`roof_close(156.16)` converges at 33 × 28 bays; extension 93.84 kW (lighting 28.89, ventilation 40.95, envelope 24.00; air-source, D77) → **P = 250.00 kW**, E = 6000 kWh/d.

| Quantity | Value | formula |
| --- | ---: | --- |
| Balancing nameplate | **1733 kWp** (1732.9) | P×(10+14/0.7)/(5.41×0.80) |
| **PV nameplate @ 2.0×** | **3466 kWp** (3465.8) | A-M-109 / D75 |
| Modules | **6932 × 0.5 kWp** | in-house class (ST-SOLAR-01) |
| Array area on roof | **30 444 m²** (layout) | 8.77 m²/kWp = 1/(0.19×0.60) |
| Roof capacity at that area | 3471 kWp | 20 arrays (5×4), 1829 mm perimeter paths |
| **Building footprint** | **33 264 m² = 198 × 168 m (33×28 bays, +32 832 m² extension)** | roof_close, IFC 1205.3 |
| Roof loads | 1.11 kPa service / 1.72 LRFD | ASCE 7-22 |
| Hall envelope peaks | 505 kW heat / 450 kW cool | design-day, not energy |
| **Storage** | **3500 kWh out** (5000 kWh in) | P×14; ÷0.70 |
| Storage power | charge **1137 kW**, discharge **250 kW** | charge-governed (max governs `store_kW`) |
| **Inverters** | **49 × 60 kW = 2940 kW AC** | ceil(max(3465.8/1.2, 250)/60); 5 collection sections ≤ 11 inverters (NEC 240.87) |
| Half-yield-day check | 7500 kWh delivered = 7500 kWh need (direct 2500 + store-in 5000) — **fills exactly**; charge 1136.3 kW | D75 design cloudy day |
| Export at noon, store full | 2690 kW | inverter AC − P |
| Clear-day export | 7500 kWh/d | (2.0−1)×balancing energy |
| PV average to bus (IA-PV-01) | **312.5 kW** | balancing energy / 24 h |
| Backup (unchanged) | crit 14 kW (HAB 3, CRYO_H2 4, GROW_BED 5, controls 2) → 20 kW gen, 672 kWh / 2 d | `_power_sizing` |

## 5. Comparison with the BH-era result (POWER_SIZING Rev F)

| Item | BH Rev F (2026-10-15) | Rev AC primary | Δ |
| --- | ---: | ---: | ---: |
| Base process demand | 153.5 kW (244.8 − 91.3 ext) | 156.2 kW | +2.7 |
| Converged demand P | 244.8 kW | 250.0 kW | +5.2 |
| Extension load | 91.34 kW | 93.84 kW | +2.5 |
| PV nameplate | 3394 kWp | 3466 kWp | **+72 (+2.1 %)** |
| Storage | 3428 kWh / 1113 kW chg | 3500 kWh / 1137 kW | +72 / +24 |
| Inverters | 48 × 60 = 2880 kW | 49 × 60 = 2940 kW | +1 |
| Footprint | 186 × 174 m, 32 364 m² (31×29) | 198 × 168 m, 33 264 m² (33×28) | +900 m² |
| Export peak / clear day | 2635 kW / 7344 kWh | 2690 kW / 7500 kWh | +55 / +156 |

The near-wash hides large offsetting moves. Drivers of the +2.7 kW base delta: foundry added **+45.0** (face value); Rev AA study-share node resets **+~20** (MFG_SHOP 2.9→12, BMED_UPW 0.02→6, CRYO_H2 0.9→4, GLASS_DIGEST 0.09→1.5); H2O_ELYZ cut **−24.6**; farm swarm cut **−~13**; GROW_BED 8.74→5.0 **−3.7** (LED calc 2.25); CRYO_ASU retired **−1.66** (owner 2026-10-18 orders it restored — at the AQS-DUTY-069 duty of 1.66 kW this is a wash, see §9); RECTIFIER/RECT-EW alignment and BH-row uncertainties make up the remainder (the BH one-line itself is not recoverable from the tree). The scope change (farm cut, foundry added) is **not** what doubled `_power_sizing`'s output — the stale Rev BH load list is.

## 6. Roof-area basis (owner rule: footprint derived from PV)

- Area-per-kWp basis is `roof_kWp = array_m² × pv_module_eff (0.19, NREL_PVWATTS8) × pv_roof_gcr (0.6, A-M-103)` → **8.77 m²/kWp**; identical to BH (3394 kWp / 29 783 m²).
- 0.5 kWp module at 19 % = 2.63 m² module; at GCR 0.6 → 4.39 m² roof per module, 8.77 m²/kWp; 6932 modules.
- IFC 2027 1205.3 / NFPA 1 11.12 pathways cut the gross roof to 20 arrays of ≤ 45.7 m (30 444 m² usable of 33 264 m² gross).
- The footprint is therefore **derived**: PV 3466 kWp → 30 444 m² array → 33 264 m² gross → 198 × 168 m → hall extension 32 832 m² whose own 93.84 kW load is inside P (converged).

## 7. Sensitivity

| Case | P₀ | P | PV kWp | store kWh | inv | footprint m² |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Primary (max-envelope)** | 156.16 | 250.0 | 3466 | 3500 | 49 | 33 264 |
| Calc-preferred loads | 136.55 | 219.1 | 3037 | 3067 | 43 | 29 160 |
| Foundry duty-cycled (45 → 2.5 kW) | 113.66 | 183.5 | 2544 | 2569 | 36 | 24 552 |
| Demand −20 % | 124.93 | 201.4 | 2792 | 2819 | 39 | 26 928 |
| Demand +20 % | 187.39 | 298.9 | 4144 | 4185 | 58 | 39 672 |

**PSH seasonal min** (fixed 3466 kWp design; need 7500 kWh/d):
mean-day multiple of need 2.00× at PSH 5.41 → 1.66× at 4.5 → 1.48× at 4.0 → **1.29× at 3.5** → 1.11× at 3.0. The half-yield-day cover is 1.00× at 5.41 but **0.83× / 0.74× / 0.65×** at 4.5 / 4.0 / 3.5: in a low-PSH month the design cloudy day no longer fills the store (residual covered by grid import when the utility exists, else backup — D75 island logic). Sizing *at* seasonal-min instead of annual mean would give 4167 kWp (PSH 4.5) or 5357 kWp (PSH 3.5), 58 / 75 inverters. The registered verification test (A-M-109: NSRDB TMY hourly run) must decide the PSH basis before freeze; 5.41 (annual mean) is the current driver.

**Module wattage class** (3466 kWp fixed): 0.5 kWp → 6932 modules; 0.55 → 6302; 0.6 → 5777. Roof m²/kWp is unchanged (8.77) while efficiency is 0.19 — module class moves count only. A 0.55 kWp / 21.5 % commercial class would cut area to 7.75 m²/kWp (26 866 m² array, ~28 900 m² footprint) but abandons the in-house module basis (pv_module_eff A-M and ST-SOLAR-01).

## 8. Exact numbers to encode in the graph

| Target | Value |
| --- | --- |
| `PV_ARRAY.params` | `module_kw` 0.5 · `count` 6932 · `nameplate_kw` 3466 · `area_m2` 30444 · `balance_kWp` 1733 · `oversize_factor` 2.0 · `mounting` roof only · `roof{footprint_mm [198000,168000], bays [33,28], footprint_m2 33264, extension_m2 32832, roof_capacity_kWp 3470.7, arrays 20, extension_load_kW 93.84}` |
| `PV_ARRAY.continuous_kw` | 312.5 kW (average delivered, = IA-PV-01; note "nameplate class not continuous avg" resolved) |
| IA-PV-01 edge | **312.5 kW** (set absolutely = balancing energy/24; retires the BH accumulator value 242.0676) |
| `ZNBR2.params` | `kW` 1137 · `kWh` 3500 · `charge_kW` 1137 · `discharge_kW` 250 · distributed 71.4 kWh / 23.2 kW per inverter × 49 |
| `SOL_ARK_60K.params` | `count` 49 · `kW` 2940 · `dc_ac_ratio` 1.2 · sections: 5 sections ≤ 11 inverters (`_collection_bus.py` writes exact split) · interconnection `export_peak_kW` 2690, `export_kWh_d_clear` 7500 |
| `mvs.electrical` | `need_kw` 250.0 (converged bounding demand incl. EXT_HALL) · `target_kw` 625.0 (mean-day average generation = 2.0× balancing; 2.5× need incl. round-trip) · `pv_module_kw` 0.5 · `pv_count` 6932 |
| EXT_HALL (re-created) | `continuous_kw` 93.84 kW; SF-EXT_HALL 93.84; footprint 32 832 m² added |
| Foundry elec feeds | wire SF-IND_MELT / SF-VAC_IND / SF-RF_HEAT when edges land (25 / 15 / 5 kW nameplate; duty-cycle averages ~1–2.3 kW each for energy) |
| S17 (RECTIFIER) | set 12.0 kW (node basis) or re-derive; **remove the 50.0 seed rate** |

## 9. Assumptions to register (A-M entries for the encoding commit; confirm next free numbers, register was at A-M-208)

1. **A-M-209** Rev AC bounding electrical demand basis: 156.16 kW process base / 250.0 kW converged. Max(node, edge) envelope; RECTIFIER at node 12 kW (S17 50.0 seed rejected as circular); EW DC behind RECT-EW 38.66 kW AC. Sensitivity: ±20 % → 2792/4144 kWp. Replacing test: each unit's task-02 calculated load.
2. **A-M-210** Foundry carried at face value flat (IND_MELT 25 / VAC_IND 15 / RF_HEAT 5 kW, 24 h) though AQS-SIZE-FOUNDRY rates them batch (1–3 heats/d): +1080 kWh/d vs ~25–55 kWh/d physical. Sensitivity: −922 kWp if duty-cycled. Replacing test: wired foundry elec edges at schedule averages.
3. **A-M-211** IA-PV-01 = 312.5 kW set absolutely (balancing energy/24 h), replacing the X-RSZ accumulator convention (242.0676).
4. **A-M-212** `mvs.electrical` need/target semantics: need 250.0 kW = converged bounding demand; target 625.0 kW = mean-day average generation at 2.0× balancing (D75).
5. **A-M-213** Module class 0.5 kWp × 6932 @ 19 % / GCR 0.6 → 8.77 m²/kWp, 30 444 m² array (carries A-M-103, pv_module_eff). Count-only sensitivity to 0.55/0.6 class.
6. **A-M-214** EXT_HALL 93.84 kW / +32 832 m², roof_close air-source convergence (D77 carried); replaces the stale BH 93.839 kW study share.
7. **A-M-215** ZNBR2 kW is charge-governed: 1137 kW charge / 250 kW discharge / 3500 kWh, split over 49 hybrid inverters (AQS-ELEC-008).
8. **A-M-216** ASU restore (owner 2026-10-18) enters at the AQS-DUTY-069 duty 1.66 kW — **not** the legacy 18 kW critical value; critical list 14 → 15.66 kW (generator stays 20 kW); base demand +1.66 kW → PV +~28 kWp if encoded later.

## 10. Implementation checklist (encoding commit)

1. Re-generate `LOAD_LIST.md` from the Rev AC graph (`_load_list.py` first: its CRYO_ASU / BMED_UPW_POLISH / GROW_BED / CRYO_H2 node lookups assume BH nodes and will crash/omit) → re-run `_one_line.py`. One-line demand should land ≈ 134 kW + node-only loads (foundry, MFG_SHOP node value, GROW_BED 5.0), not 308.88.
2. Resolve S17: 50.0 seed → 12.0 kW or a re-derived rail duty; kill the `mvs.electrical.need_kw` echo.
3. Add foundry elec edges (SF-*) at 25/15/5 or duty-average values, per A-M-210 decision; same commit wires or retires the bare ints.
4. Restore RECT_EW node + S17-EW / IA-DC-EW_* edges (Rev AC consolidation dropped them; `write_graph.process()` currently KeyErrors on `E['S17-EW']`, and `solver.check()` R8 fallback falsely compares RECTIFIER 12 kW against the solved 38.66 kW EW rectifier AC — a guaranteed misfit).
5. Confirm drivers unchanged (all factors already registered — nothing new to add there); run `python3 -m flow_graph.param.write_graph power` → encodes §8; `_collection_bus.py` auto-writes sections/distribution.
6. Verify encode matches §8 (3466 kWp, 49×60, 3500/1137, 33 264 m²); run `pytest flow_graph/param/test_param_misfit.py` (PV-nameplate comparison now runs against the regenerated roof need, not the contaminated 6760 kWp) and `python3 -m flow_graph.param.solver`.
7. Regenerate AQS-ELEC-002/003/007/008; POWER_SIZING new rev (Rev G: Rev AC re-base, stale-list fix, foundry); ONE_LINE/LOAD_LIST authority lines to the new graph rev; TASK_PLAN/MASTER_PLAN lines; A-M-209…216 via `_assumptions_register.py`; path-scoped commit.

## 11. Contradictions with the owner rule found in `_power_sizing.py` / graph

1. `INV = 60.0` hardcoded (L11): the block size is fine (SOL_ARK_60K class), but the graph's `SOL_ARK_60K.params` has `kW: 60` and **no `count`** → `_one_line` renders "1 × 60 kW": a single inverter for a 250 kW plant, contradicting D75 until `write_graph power()` writes count 49 / 2940 kW. Read the block size from the graph node instead of a constant.
2. Demand source: `ol['demand']` trusts a stale Rev BH load list (+175.1 kW, §3) — every PV/storage/roof number `_power_sizing.py` prints today is wrong by ~2×, and the misfit gate would force those wrong values into the graph if run now.
3. EXT_HALL handling (L20-23) assumes the node exists to subtract; it doesn't in Rev AC → double count with the stale list row.
4. `CRIT` guards (L14-15) silently adapt to CRYO_ASU/GROW_BED presence — on the 2026-10-18 ASU restore the 18 kW legacy critical value must not come back (A-M-216).
5. Graph seeds that contradict D75 until re-encoded: `mvs.electrical` need 50 / target 70 / `pv_module_kw` 70 × 1; `PV_ARRAY` 70 kWp seed; ZNBR2 60 kW/120 kWh + IA-ESS-ZNBR2-CHG 6.67 / DIS 5.0 BH-restored seeds; IA-PV-CURTAIL 4.645; S17 50.0.
6. `solver.check()` R8 RECTIFIER↔RECT_EW fallback conflates the 48 V rail unit with the EW rectifier (false −69 % misfit) — fix before the gate is meaningful.

— End of note. Tree left clean at `64c8239`; only this file written.
