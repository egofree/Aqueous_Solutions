# Self-copy critical-path BOM — parts × feedstock (RepRap-class)

Document number: AQS-BOM-SC-001  
Revision: E  
Date: 2026-10-01  
Authority: AQS-AUTH-001; MVS AQS-UI-001 Rev C §3.2 / §11; AQS-GAP-001;
AQS-MFG-MET-001; AQS-EQP-MFG-001; AQS-EQP-FAB-001; AQS-EQP-FAB-PV-001;
AQS-MFG-ELC-001; AQS-MeOH-001; AQS-MF-001; AQS-STR-001; AQS-EQP-STUDY-001;
Project decision 2026-10-01 (litho / blow-mold / electrode coating in MVS);
shopping lists under hub `manufacturing_bom.xlsx` / `materials_shopping_list.xlsx`
(procurement ≠ this).  
Style: AQS-DOC-001.  
**Stage = Partial critical-path map toward MVS (Rev E study duties issued).** Not a complete RepRap BOM
yet. Not vendor purchase orders. **MVS is the ideal we pursue** (AQS-UI-001);
the sandbox is the **live model** that stays modular/extensible as studies
close gaps — **not** an accepted “sub-MVS product.” Every Missing/Partial
path is an **open study queued in the plan** before proceeding; solver may
flag incomplete physics, but those flags are work queue — **not** accepted
emissions or closed unreclaimed endpoints.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Critical-path parts × on-site feedstock; Partial vs Closed flags | 2026-10-01 |
| B | 1 | Litho deferred-with-unreclaimed; blow-mold out-of-MVS-at-M1; deepen Partial next-measurement (WP-A3) | 2026-10-01 |
| C | 2 | Project decision: litho **IN SCOPE** Present-path study schedule; blow-mold **in MFG / in MVS**; electrode coating **IN SCOPE**; `reprap_bom_complete` stays false (Partial) | 2026-10-01 |
| D | 3 | Framing: MVS is the pursued ideal; sandbox tracks progress; gaps = **open studies queued in plan** (not accepted unreclaimed/sub-MVS endpoints) | 2026-10-01 |
| E | 4 | Side quests: ST-LITHO/BLOW/ELC first-principles duty issued (0.1 / 0.5 / 0.3 kW_e); Present CAD still external | 2026-10-01 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/SELF_COPY_BOM.md`  
(Hub BOM authority — not `cad/` planning fluff; not mirrored as planning.)  
Share: copy into `docs-authority/` on sync pass when listed; prefer hub path until freeze.

---

## 1. Purpose

Evidence table for MVS “make own parts + copy itself (RepRap-class)”:
map **critical-path** assemblies to on-site streams / units. Rows marked
**Partial** or **Missing** block claiming complete self-copy.

---

## 2. Status key

| Flag | Meaning |
|---|---|
| **Closed (doc)** | Path named in MF / EQP; feedstock stream exists |
| **Partial** | Path named; rate / CAD / tool incomplete |
| **Missing** | No on-site path yet — **open study required** (plan queue); not an accepted design outcome |
| **Study** | First-principles / schedule issued; Present CAD or rates still open |
| **In-scope study** | Required for MVS; Present CAD / nameplate not yet issued — study queued |

---

## 3. Critical-path matrix (SCALE_M = 1.0)

| Part / capability | On-site feedstock / stream | Making unit / sector | Flag | Next measurement |
|---|---|---|---|---|
| Structural metal stock / fasteners | S08 metals crib; S57–S63 MET forming | MFG / MET_MELT / draw / mill | Partial | kg/h campaign; powder S60 rate |
| RepRap / CNC frames + printed parts | Polymer line (oil cuts); scrap S16 | MFG polymer + CNC/MILL massing | Partial | Precious Plastic kit ≠ full BOM; print volume TBD |
| Metal powder (S60) | Plated / melt atomize | MFG MET | Partial | FreeCAD stubs; kg/h TBD |
| Wire / mill / melt | S08 → MET | MFG | Partial | Continuous share 0.2–2 kg/h study (AQS-AUD-001 §10.6) |
| IEM / membrane film | Prefer SI-IEM-01 open membrane fab; oil-line recycle narrative | MEOH / WET polish | Partial | Confirm oil-recycle vs full EDC→PVC (AQS-GAP-001 §7.7) |
| Electrodes / coating | Substrate MET mesh/plate; coat booth → MET_AHU/SCRUB | MFG **ELECTRODE_COAT** (AQS-MFG-ELC-001) | **Study** (duty+class) | ST-ELC-01: 0.3 kW_e avg; non-precious M1 class; booth CAD + lab formula external |
| Seals / elastomers | Oil cuts / polymer | MFG | Partial | Spec sheet class TBD |
| Sensors / power electronics | FAB wafers + assemble | FAB + MFG | Partial | Litho Present-path schedule issued (below); CAD breakout still Incomplete |
| CZ puller / wafer tools | Si from S08; FAB train | FAB | Partial | Tool copy of itself not proven |
| Cold-box / CRYO internals | Metals + vacuum fab | MFG + CRYO | Partial | ASME MAWP TBD — not self-copy claim |
| ZnBr₂ stack / Br₂ scrub | Electrolyte make-up study; S69 regen | ZNBR2 + GAS | Partial | Listing / BMS; regen hardware finish |
| MeOH synth / DMFC | S73/S74/S76; SI-DMFC / SI-IEM stand-ins | MEOH | Partial | Stand-in ≠ purchase; bank sizing AQS-ESS-001 |
| Hydro turbine-pump | Metals + seals | MFG + PUMPED_HYDRO | Partial | M1 energy symbolic (AQS-ESS-001) |
| PV cells (campus renew) | Solar-cell branch AQS-EQP-FAB-PV-001 | FAB PV_* / SOLAR_PV_CELL | **Study** (bands locked) | ST-SOLAR-01: 1.0 kW share; REQ-PECVD/BELT bands; vendor datasheets + PV_COUNT external |
| Photolithography (coat/align/develop) | WS_SOLV S38 class; resist | FAB / **LITHO_STUB** | **Study** (duty+mass) | ST-LITHO-01: 0.1 kW_e; resist dry 0.2–1 g/d; FreeCAD children + UV datasheet external; `lithography_on_site=false` |
| Blow mold / shoe mold | Polymer melt from EXTRUSION / oil cuts | MFG **BLOW_MOLD** (in MVS) | **Study** (duty) | ST-BLOW-01: 0.5 kW_e avg / 2–4 peak; mold FreeCAD + datasheet external |
| Textiles / HEPA | AQS-MFG-TEX-001 stub | MFG optional | Partial | Optional for MVS electrical |
| VCD / remin potable train | Grey S12; condensate; Ca/Mg/K | WTR VCD_TRAIN + REMIN | **Study** (physics closed) | ST-VCD-01/ST-REMIN-01: 0.08 kW_e + Ca/Mg g/d; Present IDs external |
| GEO_ORC | GEO loop heat reject | GEO | Study | Carnot-limited kW_e band (AQS-EQP-STUDY-001 Rev C); GHEX survey before freeze |

---

## 3.1 Photolithography Present-path study schedule (Rev C)

**Lock (Project decision 2026-10-01):** Photolithography is **IN SCOPE** for realistic
self-sustaining tech — not an accepted omission.

| Step | Study tag | Duty | Streams / utilities | Status |
|---|---|---|---|---|
| 1 | LITHO_COAT | Spin / spray photoresist coat + softbake | Resist; WS_SOLV S38; N₂ S03 | Study schedule — inside FAB envelope |
| 2 | LITHO_ALIGN | Align / expose (contact or projection class) | Optical / UV; no invented lamp kW | Study schedule |
| 3 | LITHO_DEV | Develop + hardbake; rinse | Developer → organics / oil path; UPW | Study schedule |
| 4 | → FAB_TOOL etch / implant / metal | Existing L0 train (AQS-EQP-FAB-001) | S10 etch return | Partial massing |

Seed keeps single unit `LITHO_STUB` with `present_path=in_scope_study_schedule`
until FreeCAD children exist. Disabling litho in sandbox **queues an open
study** (must close before claiming MVS progress on electronics) — not an
accepted omission. Electronic self-copy remains **Incomplete** until
schedule → Present.

## 3.2 Blow mold — in MFG / in MVS (Rev C)

**Lock (Project decision 2026-10-01):** Blow mold / shoe mold **brought into MFG** and
**required for MVS**. Rev B “out-of-MVS-at-M1” is **superseded** (was wrong
framing — gaps are studies, not out-of-scope acceptance).

| Item | Decision |
|---|---|
| Sector | **MFG** (polymer aisle beside INJECTION / EXTRUSION) |
| Seed unit | `BLOW_MOLD` study stub |
| Authority | AQS-EQP-MFG-001 Rev C row; this BOM |
| Present CAD | Not yet — Partial / study |
| If disabled in sandbox | Solver flags **open study queued** (self-copy / MFG polymer) — not accepted unreclaimed endpoint |

## 3.3 Electrode coating — IN SCOPE (Rev C)

**Lock (Project decision 2026-10-01):** Electrode coating **IN SCOPE**; MFG or FAB as
process needs. Sector boundaries are **not absolute** (AQS-SEC-001 §3.1
cross-use note): coating lives in **MFG** with MET substrates; wet
chemistry may borrow FAB wet-bench practice without requiring a new sector.

| Item | Decision |
|---|---|
| Seed unit | `ELECTRODE_COAT` (sector_id MFG) |
| Exhaust | MET_AHU → MET_SCRUB (S71–S72) — not afterburner primary |
| `electrode_coating_on_site` | **false** until Present booth CAD / formulation |
| Precious-metal RuO₂–IrO₂ claim | Deferred — no fake nameplate |

## 3.4 WP-A3 deepen notes (Rev C)

| Topic | Decision | Blockers if Partial |
|---|---|---|
| Litho | **IN SCOPE** Present-path study schedule | Equipment IDs; residual resist mass; CAD breakout |
| Blow mold | **In MFG / in MVS** | Mold tooling; duty kW; polymer feedstock campaign |
| Electrode coating | **IN SCOPE** (MFG primary) | Coating formulation; curing; scrub duty |
| MET powder / membranes | Remain **Partial** | kg/h; oil-recycle vs EDC→PVC |
| `reprap_bom_complete` | Stays **false** | Matrix still Partial — many next-measurements open; do **not** claim complete |

## 4. Completeness checklist (solver / schema flags)

| Flag id | Meaning | Seed default |
|---|---|---|
| `self_copy.critical_path_documented` | This matrix exists | true |
| `self_copy.reprap_bom_complete` | Every colony part has feedstock row **and** rates warrant complete | **false** (Partial — Rev C) |
| `self_copy.lithography_on_site` | LITHO path **Present** CAD | **false** (in-scope study schedule only) |
| `self_copy.lithography_in_mvs` | Litho required for MVS (pursue to Present) | **true** |
| `self_copy.blow_mold_in_mvs` | Blow mold required for MVS (pursue to Present) | **true** |
| `self_copy.vcd_remin_on_site` | Potable train Present | **false** (study duty issued; Present IDs open) |
| `self_copy.electrode_coating_on_site` | Coating Present | **false** (in-scope study unit) |
| `self_copy.shopping_list_only` | xlsx procurement without feedstock map | false (map exists; xlsx still study) |

---

## 5. Gap summary → plan study queue

Rev E: litho/blow/electrode/VCD/REMIN/ORC/SOLAR **first-principles issued**; Present CAD/surveys remain.

M1 seed does not yet reproduce **every** critical path (membranes, sensors,
power electronics, seals, CZ puller, cold-box, Present litho tools, Present
blow-mold CAD, Present electrode booth) from on-site streams alone.
`reprap_bom_complete=false` means **open studies remain** — each Partial/
Missing row is work that **must happen before** claiming that path closed.
Sandbox tracks progress toward MVS as those studies finish; it is **not**
locked to a sub-MVS intended product state.

---

## 6. Related / licence

AQS-MVS-GAP-001 §4.3; AQS-GAP-001; AQS-EQP-STUDY-001; planning/DECISION_LOG_A3_A5.md;
CERN-OHL-S-2.0.
