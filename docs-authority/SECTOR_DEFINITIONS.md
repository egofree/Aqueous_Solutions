# Sector Definitions catalogue — plant sector_id map

Document number: AQS-SEC-001  
Revision: G  
Date: 2026-10-01  
Authority: AQS-AUTH-001; **class list owned by AQS-UI-001 Rev C §3.1**
(`cad/DESIGN_TOOL_ARCHITECTURE.md`); hierarchy examples AQS-UI-001 §3.5;
scale AQS-SCALE-001 (`SCALE_M = 1.0` candidate MVS); streams AQS-STR-001;
mass-flow AQS-MF-001; capacity study AQS-AUD-001; style AQS-DOC-001.  
**Stage = catalogue lock.** Not FastAPI / JSON Schema code. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Census every known plant sector_id; map each to exactly one Sector Definition; MVS-closure flags | 2026-10-01 |
| B | A2 decision closed; FAB and MFG required | Project decision 2026-10-01: goods surplus requires FAB and MFG; set both `required_for_mvs_closure` to true. | 2026-10-01 |
| C | A3 decision closed; ESS ≥1 peer | Project decision 2026-10-01: electrical MVS requires ≥1 enabled ESS among ZNBR2 / MEOH / PUMPED_HYDRO; individual ESS peers stay `required_for_mvs_closure` false; all off → gap (do not claim closure). | 2026-10-01 |
| D | A3 reframed; all three ESS in MVS | Project reframe 2026-10-01: MVS requires **all three** ESS peers (ZNBR2, MEOH, PUMPED_HYDRO) `required_for_mvs_closure: true`; redundancy is a core tenet; MeOH also feeds processes; sandbox off → unreclaimed-resource / incomplete-closure gaps (not accepted emissions). | 2026-10-01 |
| E | A4–A9 catalogue defaults | Reasoned defaults for ELEC split, WTR, NUT, GEO, GAS, FUEL_CELL; operator-decision TBD only where truly ambiguous (none blocking). | 2026-10-01 |
| F | Sector cross-use note | Boundaries organisational not absolute; missing-sector parts may live inside present sectors (Project decision 2026-10-01) | 2026-10-01 |
| G | Framing | Cross-use ≠ accepted gap; open studies queued; sandbox tracks MVS progress | 2026-10-01 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/SECTOR_DEFINITIONS.md`  
---

## 1. Purpose

Give the design-tool / MVS schema a single authority table that maps every
known plant `sector_id` to **exactly one** Sector Definition from
AQS-UI-001 §3.1, with `required_for_mvs_closure` and notes for dual-role
blocks. Schema / solver workers **shall** reconcile typed fields to this
table; they **shall not** add a tenth Sector Definition class without
Project decision (see §5).

---

## 2. Scope

| In | Out |
|---|---|
| One row per known `sector_id` (locked CAD / PFD / audit names) | FastAPI, JSON Schema files, solver implementation |
| Primary Sector Definition + optional secondary note | Rewriting AQS-UI-001 §3.1 class list |
| `required_for_mvs_closure` = true / false / study | Vendor nameplates; PE / AHJ permits |
| Alias / non-sector / TBD rows for orphans | Overwriting MVS gold; fabricating closure |

Census sources (deduplicated): `freecad/params.py`, `freecad/plant_groups.py`,
`SYSTEM_MODEL_PLAN.md`, `STREAM_REGISTER.md`, `BUILDING_STACK.md`,
`MASS_FLOW.md`, local planning SECTOR_CAPACITY_AUDIT (not published), `CAMPUS_PLAN.md`,
`ELECTRICAL.md`, `MEOH_TRAIN.md`, `FUEL_CELL.md`, `GEOTHERMAL_BACKUP.md`,
`WATER_PURIFICATION.md`, `TERRACE_LANDSCAPE.md`, `SCALE_MODEL.md`,
AQS-UI-001 §3.5 / §6 schema sketch, line PFDs under `pfd_scripts/`.

---

## 3. Sector Definition class list (pointer only)

**AQS-UI-001 Rev C §3.1 owns the class list.** This catalogue does not
extend it. Classes:

1. Energy Storage System (Gravity)
2. Energy Storage System (Electrochemical)
3. Energy Production (Electrical)
4. Energy Production (Combustion Engine)
5. Energy Production (Electrochemical)
6. Process (Mass transform)
7. Life support / habitat
8. Utility / header
9. Export / dock

Rules echoed from §3.1 / §3.2: any sector may be off in a sandbox with
**gap / unclosed-stream flags** (missing required ESS → **unreclaimed-
resource / incomplete-closure** language); MVS = self-sustaining colony
+ closed loops **plus** surplus export (food, clean water, materials/
goods, energy); **all three** ESS peers required in MVS; physical
`SCALE_M` remains the layout driver.

### 3.1 Sector cross-use (Project decision 2026-10-01)

Sector boundaries are **organisational, not absolute**. A design may host
parts of a capability that “belongs” to a missing or deferred sector
**inside** present sectors when physics and HSE allow — example: electrode
coating (required for MVS) lives in **MFG** with MET substrates and may
borrow FAB wet-bench practice without adding a new Sector Definition
class. Catalogue rows still name a **primary** `sector_id` for toggles/gaps;
UI / sandbox models combinations/footprints and **tracks progress toward
MVS**. Missing capability inside a present sector is still an **open study
queued in the plan** — not an accepted unreclaimed or sub-MVS endpoint.
Document cross-use in unit notes / BOM.

---

## 4. Catalogue table

`required_for_mvs_closure`: **true** = gold MVS needs the sector (or an
equivalent peer noted) to close loops and meet surplus; **false** =
optional / peer redundancy (gaps flagged if referenced streams remain);
**study** = architecture present but operator / evidence table still decides
MVS inclusion.

**ESS peer set (MVS — all three required):** ZNBR2, MEOH, and
PUMPED_HYDRO are each `required_for_mvs_closure` = **true**. Project reframe
2026-10-01 (A3 → Rev D): **redundancy is a core tenet**; MeOH also feeds
other process streams. Sandbox **may** disable any peer; the design-tool /
solver **shall** then emit gap reason `unreclaimed_resource` for **each**
disabled required ESS (incomplete closure — **not** accepted pollution /
emissions) and **shall not** claim electrical-storage or mass closure without evidence.

Rows marked **[catalogue-proposed]** are stable strings chosen here to
match plant names where AQS-UI-001 §6 sketch did not yet list them;
schema worker **shall** reconcile IDs, not silently rename CAD units.

| sector_id | Sector Definition | required_for_mvs_closure | Notes | Authority refs |
|---|---|---|---|---|
| WET | Process (Mass transform) | true | L-1 leach / EW / BMED / CRU / polish; 150 kg/d feed basis; primary mass recycle. | AQS-BLD-001; AQS-MF-001; AQS-AUD-001 §4.1; AQS-UI-001 §6 |
| OIL | Process (Mass transform) | true | Dryer → pyro → frac → cuts; AFTERBURNER flue → CRYO (S67). Closes organics / oil loop. | AQS-STR-001; AQS-MF-001; AQS-VENT-001; SYSTEM_MODEL A3 |
| GLASS | Process (Mass transform) | true | Rinse → burnout → mill → digest; silicate / ceramic products. Materials surplus path. | AQS-STR-001; SYSTEM_MODEL A4; AQS-AUD-001 |
| GAS | Process (Mass transform) | true | Scrub / demister / baghouse / stacks; closes acid-gas and dust returns (S65–S66, S19). Secondary: Utility / header (HDR_*). **Rev E lock:** Process primary (A8). | AQS-VENT-001; AQS-EQP-VENT-001; FAN_STACK; AQS-AUD-001 §4.2 |
| FAB | Process (Mass transform) | true | WAFER_FAB + UPW + WS_* reagents + solar-cell stub. Goods surplus path; wafers/d and UPW L/d TBD. Required by Project decision 2026-10-01 for MVS goods surplus. | AQS-EQP-FAB-001; AQS-EQP-FAB-UPW-001; AQS-EQP-FAB-RGN-001; AQS-AUD-001 §4.4 |
| MFG | Process (Mass transform) | true | MFG_SHOP + polymer line + MET forming (S57–S63). Goods surplus path; kg/h TBD. Required by Project decision 2026-10-01 for MVS goods surplus. MET is **not** a separate sector_id. | AQS-EQP-MFG-001; AQS-MFG-MET-001; AQS-AUD-001 §4.5 |
| NUT | Process (Mass transform) | true | NUTRIENT_DOSE / P-Al·Mg·Ca / BMED salts → farm (S07). Secondary: Life support / habitat (serves FARM). **Rev E lock:** keep as sector (A6). | AQS-EQP-NUT-001; AQS-AUD-001 §4.6; AQS-STR-001 |
| FARM | Life support / habitat | true | Grow beds / fish / LED; food surplus (S14). CAD name `FARM` (not FRM). | AQS-LIFE-001; AQS-EQP-FRM-001; AQS-AUD-001 §4.7; AQS-UI-001 §3.1 |
| HAB | Life support / habitat | true | Habitation / galley / sleep / grey-waste return; crew load driver. | AQS-LIFE-001; AQS-MEP-001; AQS-AUD-001 §4.8 |
| CRYO | Utility / header | true | Cold box + product receivers (O₂/N₂/CO₂/H₂); S64 H₂ normal; S54–S56 / S70. Not a generation class. | AQS-CRY-002; AQS-EQP-CRY-001; AQS-VENT-001; AQS-UI-001 §3.1 |
| WTR | Utility / header | true | Roof / catch tanks, VCD / remin / UPW polish, grey treat (AQS-WTR-001). Clean-water surplus + fab/hab water. **Rev E lock:** keep as sector (A5). | AQS-WTR-001; AQS-SCALE-001; AQS-AUD-001 §4.10 |
| TRR | Utility / header | false | Terrace overflow / irrigation (S40–S42); optional GH envelopes. Event-driven surplus water; not required for loop closure. Secondary: Life support if enclosed GH enabled. | AQS-TRR-001; AQS-TRR-GH-001; AQS-UI-001 §3.5 |
| ELEC | Utility / header | true | Sol-Ark / ATS / RECT / MCC / trays — electrical **distribution** hub. Distinct from ELEC_PV generation. **Rev E lock:** keep split (A4); reject composite POWER. | AQS-ELC-001; ELECTRICAL.md; FLOW_BATTERY.md; AQS-UI-001 §3.5 |
| ELEC_PV | Energy Production (Electrical) | true | PV_ARRAY / ARRAY_ROOF; discrete `PV_COUNT`. Primary electrical source for match + energy surplus. | AQS-ELC-001; AQS-SCALE-001; AQS-UI-001 §3.1 / §6 |
| ZNBR2 | Energy Storage System (Electrochemical) | true | ZnBr₂ flow battery + Br₂ scrub/regen (S69). **Required** ESS peer in MVS (redundancy). Sandbox off → gap `unreclaimed_resource` (incomplete closure). | FLOW_BATTERY.md; AQS-VENT-001; AQS-UI-001 §3.1 / §6 |
| MEOH | Energy Storage System (Electrochemical) | true | MeOH store + IEM/DMFC path (S73–S82). **Required** ESS peer in MVS; also feeds other processes. Secondary: Process (Mass transform); Energy Production (Electrochemical) on MEOH_FC discharge. Sandbox off → `unreclaimed_resource`. Not a 10th class. | AQS-MeOH-001; AQS-EQP-MEOH-001; AQS-REQ-KW-001; AQS-UI-001 §3.1 |
| PUMPED_HYDRO | Energy Storage System (Gravity) | true | Roof↔CATCH turbine-pump; side effect of water tower (AQS-BLD-001 §3). **Required** ESS peer in MVS (redundancy). Unit tag `HYDRO_SET` / hydro formula. Sandbox off → `unreclaimed_resource`. | AQS-BLD-001 §3; AQS-SCALE-001; AQS-AUD-001 §4.10; AQS-UI-001 §6 |
| BACKUP_GEN | Energy Production (Combustion Engine) | false | H₂ genset on Sol-Ark GEN (S45/S47). Island / redundancy; not required if PV+ESS close electrical match. | AQS-PWR-001; AQS-EQP-GEN-001; AQS-REQ-KW-001; AQS-UI-001 §6 |
| FUEL_CELL | Energy Production (Electrochemical) | false | PEM FC on BATT DC (S49–S53). ≠ BACKUP_GEN; ≠ MEOH_FC (MEOH sector). Optional generation peer. **Rev E lock:** own sector_id (A9). | AQS-FC-001; AQS-EQP-FC-001; ELECTRICAL.md |
| GEO | Utility / header | study | GEO_GHEX / GEO_HP → Q4 (S43–S44). Secondary: Energy Production (Electrical) **only if** GEO_ORC (S48) enabled — ORC rating TBD (no unverified kW). | AQS-PWR-001; AQS-EQP-GEO-001; AQS-AUD-001 §10.4; [catalogue-proposed] |
| DOCK | Export / dock | true | North dock + `ELEV_DOCK` pairs (`DOCK_COUNT = CASSETTE_COUNT`). Boundary for surplus goods / freight export. | AQS-SITE-001; AQS-BLD-001 §4; AQS-UI-001 §3.1 / §3.2 |

### 4.1 Alias / non-sector rows (not toggleable sector_ids)

| Name | Status | Notes | Authority refs |
|---|---|---|---|
| POWER | alias (composite) | Physical yard west of north dock. **Not** a sector_id — split into ELEC, ELEC_PV, ZNBR2, BACKUP_GEN, FUEL_CELL, GEO (and MEOH when sited in yard). Schema worker: reject `POWER` as sector_id or map→children. | AQS-AUD-001 §4.9; AQS-BLD-001; ELECTRICAL.md |
| LIFE | alias (composite) | Narrative life plate — use FARM + HAB (+ WTR/TRR as listed). | AQS-BLD-001; AQS-LIFE-001 |
| OIL_GLASS | alias (FreeCAD group) | `plant_groups.py` Process/Oil_Glass — catalogue keeps **OIL** and **GLASS** separate per AQS-UI-001 §3.5. | freecad/plant_groups.py |
| FRM | alias | Audit shorthand → **FARM**. | AQS-AUD-001 |
| CRY | alias | Audit shorthand → **CRYO**. | AQS-AUD-001 |
| MET | folded | Metal forming under **MFG** (AQS-MFG-MET-001). | AQS-MFG-MET-001 |
| SLINGSHOT | non-sector | Interface / legacy water-cycle decisions only; no envelope. Do not emit as sector_id. | AQS-AUD-001 §4.11; AQS-WTR-001; AQS-GAP-001 |
| CORE | non-sector (building) | CORE_PROCESS / shafts / stairs — building distribution, not a mass–energy sector toggle. Shaft streams remain on owning process/utility sectors. | AQS-BLD-001; AQS-HSE-001 |

---

## 5. Ambiguities / catalogue locks (schema reconcile)

Do **not** add a 10th Sector Definition. Prefer deciding among existing
nine classes or confirming the primary below.

| # | Topic | Status (Rev E) | Decision / default | Blocking? |
|---|---|---|---|---|
| A1 | MEOH dual role | **Closed** | Keep primary ESS (Electrochemical); synth/FC Notes secondary. | No |
| A2 | FAB / MFG MVS required | **Closed — true** | Project decision 2026-10-01: both required for goods surplus. | No |
| A3 | ESS required set | **Closed — all three** | Project Rev D: ZNBR2/MEOH/PUMPED_HYDRO each required; off → unreclaimed. | No |
| A4 | ELEC vs ELEC_PV | **Locked default** | **Keep split:** ELEC = Utility/header (distribution hub); ELEC_PV = Energy Production (Electrical). Rationale: toggles/gaps and electrical match need generation distinct from bus. Schema shall reject composite `POWER`. Operator TBD only if a future UI forces a single switch — not required now. | No |
| A5 | WTR sector | **Locked default** | **Keep WTR** as Utility/header sector_id. Rationale: clean-tower / VCD / UPW / surplus-water ontology is shared across HAB+FAB+SCALE tanks; folding hides WTR-off unreclaimed on S01/S21–S23/S40. [catalogue-proposed] tag retired as ambiguity. | No |
| A6 | NUT vs FARM | **Locked default** | **Keep NUT** as Process (Mass transform) sector. Rationale: dose chemistry (S07) is mass-transform of BMED salts ≠ life plate; FARM-off and NUT-off must flag different unreclaimed streams. | No |
| A7 | GEO primary | **Study — default retained** | Primary remains **Utility / header** (GEO_HP→Q4) until ORC rated. `required_for_mvs_closure: study` / seed false. If GEO_ORC ships with issued kW, the project may re-primary to Energy Production (Electrical) or keep Utility + secondary note — **operator-decision TBD** only at that evidence gate. | Study (ORC TBD) |
| A8 | GAS vs Utility | **Locked default** | Primary **Process (Mass transform)** — scrub transforms liquor/gas (S65–S66, S19). Secondary Utility/header note retained. | No |
| A9 | FUEL_CELL sector | **Locked default** | **Own sector_id** (AQS-FC-001 Present). Rationale: optional generation peer toggles/gaps distinct from ELEC hub and from MEOH_FC. `required_for_mvs_closure: false`. | No |

---

## 6. Census summary

| Metric | Count |
|---|---|
| Mapped sector_id rows (§4) | **21** |
| Alias / non-sector rows (§4.1) | **8** |
| `required_for_mvs_closure` = true | **17** — WET, OIL, GLASS, GAS, FAB, MFG, NUT, FARM, HAB, CRYO, WTR, ELEC, ELEC_PV, ZNBR2, MEOH, PUMPED_HYDRO, DOCK |
| = false | **3** — TRR, BACKUP_GEN, FUEL_CELL |
| = study | **1** — GEO |
| [catalogue-proposed] IDs (Rev E defaults locked) | NUT, WTR, ELEC (hub split), FUEL_CELL kept; GEO remains study |

---

## 7. Related documents

| Doc | ID | Role |
|---|---|---|
| DESIGN_TOOL_ARCHITECTURE.md | AQS-UI-001 Rev C | **Owns** Sector Definition class list §3.1; colony MVS + ESS redundancy rules |
| AUTHORITY.md | AQS-AUTH-001 | Hub pointer |
| Local planning (not published): SECTOR_CAPACITY_AUDIT | AQS-AUD-001 | Footprint / throughput study at SCALE_M=1.0 |
| STREAM_REGISTER.md | AQS-STR-001 | Inter-block `S##` |
| MASS_FLOW.md | AQS-MF-001 | Closed-loop claims |
| SCALE_MODEL.md | AQS-SCALE-001 | Growth / discrete jumps |
| BUILDING_STACK.md | AQS-BLD-001 | Levels / masses / dock |
| MeOH_TRAIN.md | AQS-MeOH-001 | MEOH ESS / process peer |
| FUEL_CELL.md | AQS-FC-001 | PEM path |
| GEOTHERMAL_BACKUP.md | AQS-PWR-001 | GEO + BACKUP_GEN |
| ELECTRICAL.md | AQS-ELC-001 | Hub / PV / ZnBr2 / GEN / FC interconnect |
| DOCUMENTATION_STYLE.md | AQS-DOC-001 | House style |
