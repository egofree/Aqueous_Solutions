# Means of egress — study calculation (NFPA 101 / IBC Ch. 10 themes)

Document number: AQS-EGR-001  
Revision: D
Date: 2026-10-01  
Authority: AQS-BLD-001 Rev E, AQS-SITE-001 Rev B, AQS-HSE-001, AQS-CMP-001
(CMP-NFPA-04 / CMP-OSH-01), `cad/freecad/params.py` at **SCALE_M = 1.0**.  
Jurisdiction assumed: USA (Dallas-class / Texas AHJ).  
**Not a PE stamp. Not a permit set. AHJ / PE verification required.**

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Study travel / exit-width / basement two-exit calc from locked CAD dims | 2026-10-01 |
| B | 1 | Controlling-code rule (most restrictive); CRYO_EGRESS_* stubs; dock+ELEV_DOCK | 2026-10-01 |
| C | 1 | Freeze-blocker pointer to AQS-MVS-GAP-001 §4.8 | 2026-10-01 |
| D | 1 | X-STD-01: extension hall egress in AQS-EGR-002 (`HALL_EGRESS.md`); this document keeps the base plate. | 2026-10-15 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001. No invented permits.

---

## 1. Purpose

Close Rem-BLD item **NFPA 101 / IBC Ch. 10 egress calc** with a
**labeled study** using live plate, stair, and dock geometry. Record
assumptions where code factors are not locked in authority docs.
Quantitative results here are **design-intent only** until AHJ / PE
confirm edition, occupancy classification, and clear widths.

## 2. Scope

| In | Out |
|---|---|
| Travel-distance study from plate corners to credited exits | Clause quotations; PE sealed drawings |
| Exit / stair width capacity study from occupant-load assumptions | Invented truck counts (AQS-SITE-001) |
| Two basement exits: STAIR_SERVICE + STAIR_MAINT | Accessibility full ABA/ADA survey |
| North dock discharge narrative | Arc-flash / NEC 700 fixture schedule (CMP-NEC-07) |
| CRYO dedicated egress (door + lobby stubs) | Horizontal-exit smoke-barrier design |

## 2.1 Design target — most restrictive controlling code

Design intent = **most restrictive** among the themes already cited in
AQS-HSE-001 / AQS-CMP-001 / this annex:

| Family | Themes used here |
|---|---|
| NFPA 101 | Means of egress travel, exit count, discharge |
| NFPA 2 / 55 | CRYO / H₂ room dedicated egress; no sole aisle reliance |
| IBC Ch. 10 / IFC | Exit width, stair geometry, occupancy load method |
| Relevant ISO | Process-plant egress concepts where AHJ accepts (document if used) |

**Controlling code per egress dimension (study — AHJ confirms edition):**

| Dimension | Controlling theme (study) | Why most restrictive here | Plant value (study) |
|---|---|---|---|
| Hab sleeping travel | NFPA 101 / IBC 1016 theme (sprinklered R / mixed) | Sleeping must not enter H; dual stair credit | ≤ ~15 m Manhattan (OK vs 45–76 m theme) |
| Hab exit width | IBC 1005 / NFPA 101 capacity theme | Stair clear vs load | STAIR_P/S* study clear 2.10 m |
| Basement two-exit | IBC 1006 / NFPA 101 + OSHA 1910.36 | Two remote exits from L-1 | STAIR_SERVICE + STAIR_MAINT |
| Basement travel | NFPA 101 / IBC sprinklered industrial theme | Plate-corner Manhattan | ≤ ~26 m study |
| STAIR_MAINT clear | IBC 1011 min clear theme | Operators-only; not sole public H exit | 0.90 m study — **pair required** |
| North discharge | OSHA 1910.36/37 + NFPA 101 discharge | Apron free of ESS/H₂ envelopes where practicable | SERVICE_DOOR_N → DOCK_APRON_N |
| **CRYO dedicated egress** | **NFPA 2 / 55** (controls over general industrial aisle) | Cold-box / cryogen room shall not rely solely on process-aisle door | `CRYO_EGRESS_DOOR` + `CRYO_EGRESS_LOBBY` → STAIR_SERVICE path (Partial until shop clear widths) |
| Dock freight path | IBC / NFPA 101 (not hab sleeping) | Dock uses `ELEV_DOCK` + `DOCK_DOOR_N`; hab stays on STAIR_P/S* | 1 pair at M1; +pairs E–W |

When two themes conflict, **adopt the stricter numeric or path rule** and
record the controller in the table above. No invented permits.

---

## 3. Geometry basis (SCALE_M = 1.0)

From `params.py` / AQS-BLD-001 / AQS-SITE-001 (mm → m):

| Parameter | Value | Source |
|---|---|---|
| PLATE_L × PLATE_W | **24.0 × 18.0 m** (432 m²) | 4 × 3 × 6.0 m bays |
| Site north | **+Y** | AQS-SITE-001 |
| Z_L0 / Z_Lm1 / Z_Lm2 | 0 / −6.0 / −10.5 m | CLEAR_Lm1=6.0, CLEAR_Lm2=4.5 |
| Z_L1 / Z_L2 | 6.0 / 10.8 m | CLEAR_L0=6.0, LIFE_LEVELS=1, CLEAR_L1=4.8 |
| HAB envelope | 12.0 × 18.0 m (west) | HAB_L/W |
| FARM envelope | 12.0 × 18.0 m (east) | FARM_L/W |
| DOCK | 12.0 × 8.0 m at Y = PLATE_W − DOCK_W | north edge |
| DOCK_APRON_N | 6.0 m north of ENV_WALL_N | exterior |
| SERVICE_ENTRY | 3.6 × 2.4 m | north vestibule |
| SERVICE_DOOR_N | 1.8 × 2.4 m clear (massing) | north wall |

### 3.1 Stair / exit enclosures (plan massing)

| Object | Plan box (m) | Levels | Hab sleeping credit? | Basement egress credit? |
|---|---|---|---|---|
| STAIR_P | 2.4 × 4.8 | L2–L0 (**no L-1 door**) | **Yes** (primary) | No |
| STAIR_S1 | 2.4 × 2.4 | L1–L0 (NW) | **Yes** (secondary) | No |
| STAIR_S2 | 2.4 × 2.4 | L1–L0 (SE) | **Yes** (secondary; farm side) | No |
| STAIR_SERVICE | 2.4 × 3.6 | L0–L-2; doors Lm1/Lm2 | **No** | **Yes** (secondary + service) |
| STAIR_MAINT | 1.2 × 2.4 | L0–L-2 | **No** | **Yes** (operators; not sole public H exit) |
| SERVICE_DOOR_N | 1.8 m clear massing | L0 discharge to apron | N/A | Discharge for STAIR_SERVICE |

**Clear-width assumption (study):** enclosure short dimension minus
**300 mm** for two 2 h walls ≈ available clear. Until shop drawings
give rated-wall thickness and tread/handrail deductions:

| Stair | Enclosure short dim | Study clear width |
|---|---|---|
| STAIR_P | 2.4 m | **2.10 m** |
| STAIR_S1 / S2 | 2.4 m | **2.10 m** |
| STAIR_SERVICE | 2.4 m | **2.10 m** |
| STAIR_MAINT | 1.2 m | **0.90 m** |

AHJ shall verify actual clear width, rise/run, handrails, and door
leaf swings (IBC 1011 / 1010 themes).

---

## 4. Occupant-load assumptions (study)

**No issued berth count.** AQS-AUD-001 uses a **4-person** pilot-module
placeholder for water. Egress design load uses **floor-area method**
with **study factors** (IBC Table 1004.5 *theme* — confirm AHJ edition;
factors below are labeled assumptions, not clause text):

| Level / zone | Area (m²) | Study factor (m²/occ) | Study load (occ) | Notes |
|---|---|---|---|---|
| L1 HAB (R-2 analog) | 216 | 18.6 | **12** | Sleeping / dwelling class |
| L1 FARM (F-2 / U) | 216 | 9.3 | **24** | Industrial / accessory study |
| L0 MFG shop | 96 | 9.3 | **11** | 12 × 8 m |
| L0 WAFER FAB | 120 | 9.3 | **13** | 12 × 10 m |
| L0 DOCK / receiving | 96 | 27.9 | **4** | Storage / S-1 class study |
| L0 remainder / circulation | ~120 | 9.3 | **13** | Conservative catch-all |
| L-1 process + CRYO | 432 | 9.3 | **47** | Industrial; H-room MAQ may revise |
| L-2 CATCH / hydro | ~96 (tank footprint study) | 27.9 | **4** | Utility / storage class |

| Aggregate study | Occ |
|---|---|
| Life floor L1 simultaneous | 12 + 24 = **36** |
| Grade L0 simultaneous (study) | 11 + 13 + 4 + 13 ≈ **41** |
| Basement L-1 simultaneous | **47** |
| L-2 simultaneous | **4** |

Operational crew (AUD): **4** — used for life-support, **not** as the
sole egress design load.

---

## 5. Travel distance — study paths

Coordinate origin = plate SW corner. Distances are **plan Manhattan**
(conservative vs straight-line) unless noted. Sprinklered throughout
(NFPA 13 — AQS-HSE-001 / AQS-BLD-001).

### 5.1 Habitation sleeping (must not enter L-1)

Credited exits: **STAIR_P**, **STAIR_S1** (and STAIR_S2 from farm /
east life). Discharge at L0 grade; no basement walk.

| From (HAB corner) | Nearest credited stair | Manhattan (m) | Straight-line (m) |
|---|---|---|---|
| (0, 0) SW | STAIR_P ≈ (9.1, 6.1) | **15.2** | **11.0** |
| (0, 18) NW | STAIR_S1 ≈ (0.2, 15.4) | **2.8** | **2.6** |
| (12, 0) SE-of-HAB | STAIR_P | **9.0** | **6.8** |
| (12, 18) NE-of-HAB | STAIR_S1 or CORE | **≤ 6** | **≤ 5** |

**Study max hab travel ≈ 15 m** — well below typical sprinklered
exit-access limits in the 45–76 m (150–250 ft) theme range used by
many AHJs for R / mixed use. **AHJ shall confirm** applicable limit
for the final occupancy mix.

### 5.2 Farm (L1 east)

| From | Nearest | Manhattan (m) |
|---|---|---|
| (24, 0) SE | STAIR_S2 ≈ (21.4, 0.2) | **≈ 2.8** |
| (12, 18) | STAIR_P / CORE | **≈ 12** |
| (24, 18) NE | STAIR_S2 via south then east, or CORE | **≤ 20** |

### 5.3 Basement L-1 — two exits

Credited pair: **STAIR_SERVICE** (north, west strip) + **STAIR_MAINT**
(CORE). Hab stairs are **not** L-1 doors.

Approximate door locations:

| Exit | Plan centre (m) |
|---|---|
| STAIR_SERVICE | ≈ (4.0, 14.4) |
| STAIR_MAINT | ≈ (9.1, 11.0) |

| From (plate corner) | To SERVICE | To MAINT | Nearest |
|---|---|---|---|
| (0, 0) SW | 18.4 | 20.1 | SERVICE **18.4** |
| (24, 0) SE | 38.4 | 25.9 | MAINT **25.9** |
| (0, 18) NW | 7.6 | 16.1 | SERVICE **7.6** |
| (24, 18) NE | 23.6 | 21.9 | MAINT **21.9** |

**Study max L-1 travel to nearest of the two ≈ 26 m.** Separated
exits on north face vs CORE — not clustered at one wall.

**WARNING — CRYO:** Controlling theme = **NFPA 2/55** (stricter than
general industrial aisle egress). CAD now carries `CRYO_EGRESS_DOOR` +
`CRYO_EGRESS_LOBBY` stubs toward the STAIR_SERVICE path. Do **not**
rely solely on the process-aisle door. Path remains **Partial** until
AHJ confirms clear widths, rating, and lobby arrangement on shop drawings.

### 5.4 L-2 CATCH / hydro

Same two stairs serve L-2 (STAIR_SERVICE_DOOR_Lm2 + STAIR_MAINT).
Study load low (≈4); travel within tank room to nearest stair
**≤ plate half-diagonal ≈ 15 m** (study).

### 5.5 North dock discharge

STAIR_SERVICE discharges via SERVICE_ENTRY → SERVICE_DOOR_N →
**DOCK_APRON_N** (exterior). Apron shall remain free of ZnBr2 / H₂
classified envelopes where practicable (AQS-SITE-001 §6; OSHA
1910.36/37 theme). Quantitative apron staging counts **not** invented.

---

## 6. Exit width capacity — study

**Assumption (theme):** sprinklered stair capacity ≈ **7.6 mm clear
width per occupant**; other egress doors ≈ **5.1 mm/occ** (common IBC
1005 theme pair — **confirm AHJ edition**; some jurisdictions use
0.3 in / 0.2 in imperial equivalents).

| Component | Study clear (mm) | Stair capacity (occ) @ 7.6 mm/occ | Door capacity @ 5.1 mm/occ |
|---|---|---|---|
| STAIR_P | 2100 | **276** | — |
| STAIR_S1 | 2100 | **276** | — |
| STAIR_S2 | 2100 | **276** | — |
| STAIR_SERVICE | 2100 | **276** | — |
| STAIR_MAINT | 900 | **118** | — |
| SERVICE_DOOR_N | 1800 (massing) | — | **353** |

| Demand (study simultaneous) | Supply check |
|---|---|
| L1 life 36 occ → STAIR_P + STAIR_S1 (or S2) | 276 + 276 ≫ 36 — **OK study** |
| L0 grade ~41 occ → multiple grade doors / stairs | Multiple 2.1 m stairs + dock door — **OK study** |
| L-1 47 occ → SERVICE + MAINT | 276 + 118 = **394** ≫ 47 — **OK study** |

Minimum stair clear themes often cite **1120 mm** (44 in) for
occupant loads ≥50 in some editions. STAIR_MAINT study clear
**900 mm** is **marginal** if it were the sole exit from a ≥50 load
or credited as public — consistent with AQS-SITE-001: **operators
only; not sole public exit from an H room**. Pair with STAIR_SERVICE.

---

## 7. Compliance status update

| CMP ID | Was | After AQS-EGR-001 | Remaining |
|---|---|---|---|
| CMP-NFPA-04 | Partial | **Partial** (study calc issued; AHJ verify) | Clear widths; CRYO dedicated egress; illumination schedule |
| CMP-OSH-01 | Partial | **Partial** (same) | Maintenance program; outdoor discharge survey |
| CMP-NEC-07 | Partial | unchanged | Exit sign / emergency lighting fixture schedule |

Record this annex as the quantitative companion to AQS-SITE-001 §6.

---

## 8. AHJ verification checklist

**Blocks design-freeze language (not a permit invent):** until AHJ
confirms clear widths / CRYO lobby / controlling edition, do not claim
egress-closed freeze evidence. Master checklist:
local planning MVS_GAP_AUDIT (AQS-MVS-GAP-001, not published) §4.8 + AQS-CMP-001 §8.1.


1. Confirm adopted IBC / NFPA 101 editions and local amendments.
2. Confirm occupancy classifications (R-2, F-1/F-2, H-*, S-1, H-5 fab).
3. Measure as-built / shop clear widths; replace study deductions.
4. CRYO: second means or rated lobby per NFPA 2/55.
5. Common-path / dead-end aisle lengths inside wet cassette (beyond
   plate-corner Manhattan).
6. Exit signs + emergency lighting (NEC 700) fixture schedule.
7. Do not credit STAIR_MAINT as sole public exit from H rooms.

---

## 9. Sync

Canonical in this tree: `docs-authority/EGRESS_CALC.md`  
