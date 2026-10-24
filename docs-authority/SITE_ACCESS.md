# Site access — orientation, north dock, service / egress

Document number: AQS-SITE-001  
Revision: D
Date: 2026-10-01  
Authority: subordinate to AQS-BLD-001 (levels / cores) and AQS-HSE-001
(ratings / egress separation). Does **not** change SCALE_M, chemistry,
or locked process names.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue: site north = +Y; north (pole-facing) L0 dock; SERVICE_ENTRY / STAIR_SERVICE; yard clearances / keep-outs / rough-ins; NFPA/OSHA egress hooks | 2026-09-28 |
| B | 1 | Point §6 at AQS-CMP-001; Wave 2 compliance cross-ref | 2026-10-01 |
| C | 1 | §6 → AQS-EGR-001 study annex (Wave 3) | 2026-10-01 |
| D | 1 | Dock+ELEV_DOCK discrete jump; PV equator tilt evidence; yard inset | 2026-10-01 |

Style: AQS-DOC-001. Compliance: AQS-CMP-001.

Licence: CERN-OHL-S-2.0. No diffusion pictures. Not a PE stamp.

---

## 0. Why this file exists

AQS-BLD-001 placed the truck dock south of CORE and credited STAIR_P
(no L-1 door) plus STAIR_MAINT (operators only) for vertical
circulation. Project site rule for this pass:

1. Primary truck dock faces **north** (pole-facing in the northern
   hemisphere) at **L0 grade**.
2. A **service entrance** must reach the underground (L-1 / L-2) for
   equipment and must also be a **code-credible secondary egress** from
   those levels — without routing habitation sleeping egress through H
   areas.

This document locks orientation, relocates the dock, and defines
SERVICE_ENTRY / STAIR_SERVICE. Full NFPA 101 / IBC egress calculation
and travel-distance tables are **next pass** (hooks in §6).

---

## 1. Site orientation (locked)

| Axis | Meaning | Evidence in CAD |
|---|---|---|
| **+Y** | **Site north** (pole-facing, northern hemisphere) | `ARRAY_ROOF` / `PV_ARRAY*` rotate about +X by **+SITE_LAT_DEG** so the high edge is +Y (equator / south face); `ENV_WALL_N` at `Y = PLATE_W`; life terraces on **S+E+W** |
| **+X** | Site east | `CORE_PROCESS` east half; CRYO east of CORE |
| **+Z** | Up | World Z = 0 is L0 grade FFL |

Default latitude: `SITE_LAT_DEG = 33.0` (Dallas-class). Southern-
hemisphere sites flip equator-facing terrace / array rules in
`building_stack.py`; dock remains **pole-facing** (toward the nearer
celestial pole), which is **−Y** south of the equator — call that out
in a future SITE rev if a south-latitude cassette is issued. M1
authority is northern hemisphere.

Params flag: `SITE_NORTH_AXIS = "+Y"`.

---

## 2. North dock (L0)

### 2.1 Decision

Primary truck dock and receiving bay sit on the **north edge** of the
module plate at grade. Truck doors open to **+Y**. Previous south dock
at `(0, 0)` is **withdrawn**.

**Discrete jump rule:** `DOCK_COUNT = CASSETTE_COUNT`. Baseline (M1) =
**one** dock space + **one** associated freight elevator (`ELEV_DOCK`).
As the building grows E–W (M2/M3 cassette unlock on `MODULE_BAYS_X`),
add dock+elevator pairs along +X. Do not grow dock length continuously —
add whole pairs. CORE `ELEV_SVC` is separate.

| Object | Size (m) | Plate origin (mm) | Notes |
|---|---|---|---|
| `DOCK` (× DOCK_COUNT) | 12 × 8 × slab | `(DOCK_X + n·DOCK_L, DOCK_Y)` | NW strip; S-1 / F-1 receiving |
| `ELEV_DOCK` (× DOCK_COUNT) | 2.7 × 3.2 shaft | inside each dock bay | Freight paired with dock; L-2…L2 |
| `DOCK_APRON_N` | ≥12 × 6 | `(DOCK_X, PLATE_W)` | Exterior truck apron north of `ENV_WALL_N` |
| `DOCK_DOOR_N` | 3.6 clear × ~4.2 h | centred on north wall of each DOCK | Pole-facing loading door massing |

MFG SHOP remains east-south (`MFG_X = PLATE_L/2`, `MFG_Y = 0`). WAFER
FAB remains east-north and does **not** overlap the west DOCK bay
(FAB starts at `X = PLATE_L/2`). POWER yard / ZnBr2 remain **west** of
the plate, Y-aligned to `DOCK_Y` so ESS and GEN/FC sit beside the NW
apron (AQS-PWR-001 / AQS-FC-001).

### 2.2 Occupancy / ops

- Dock occupancy class: S-1 / F-1 receiving (AQS-BLD-001 L0 table).
- No Salria, no HDR_H2 dwell, no Br₂ inventory inside DOCK.
- ZnBr2 stays outdoor (NFPA 855); do not enclose the ESS under the
  dock canopy.
- Quantitative truck counts are **not** invented this pass.

---

## 3. Service entrance and STAIR_SERVICE

### 3.1 Objects

| Object | Size (m) | Duty |
|---|---|---|
| `SERVICE_ENTRY` | 3.6 × 2.4 × 2.8 | L0 vestibule at north face, west strip inside DOCK Y-band |
| `SERVICE_DOOR_N` | 1.8 × 2.4 | Exterior door on north wall into SERVICE_ENTRY |
| `STAIR_SERVICE` | 2.4 × 3.6 | 2 h stair L0 ↔ L-1 ↔ L-2 |
| `STAIR_SERVICE_DOOR_Lm1` | door stub | Rated door / lobby stub at L-1 FFL |
| `STAIR_SERVICE_DOOR_Lm2` | door stub | Rated door / lobby stub at L-2 FFL |

### 3.2 Path (service + secondary egress)

```
North apron / DOCK_APRON_N
        │
        ▼
SERVICE_DOOR_N  →  SERVICE_ENTRY (L0 vestibule)
        │
        ▼
STAIR_SERVICE (2 h) ──► L-1 door  →  process basement (not through CORE_PROCESS)
        │
        └──► L-2 door  →  CATCH / hydro utility
```

Equipment / pallet access: L0 SERVICE_ENTRY is sized for a service cart
and tool chests; oversized freight continues to use `ELEV_SVC` (freight
elevator) with L-1 only via a rated lobby (existing AQS-BLD-001 rule).

### 3.3 Separation from habitation egress

| Stair | Levels | Hab sleeping exit? | Notes |
|---|---|---|---|
| `STAIR_P` | L2–L0 | **Yes** (primary) | **No L-1 door** — unchanged |
| `STAIR_S1` / `STAIR_S2` | L1–L0 | **Yes** (secondary) | Perimeter; opposite corners |
| `STAIR_MAINT` | L0–L-2 | **No** | Operators only; not credited as public egress |
| `STAIR_SERVICE` | L0–L-2 | **No** for hab | Basement **secondary egress** + service; discharge to exterior at L0 north — does **not** walk hab occupants through H areas |

**WARNING**

Habitation sleeping egress shall land at grade via STAIR_P / STAIR_S*
without entering L-1 process or CRYO rooms (IBC 1016 / NFPA 101 concept;
AQS-HSE-001 §8). STAIR_SERVICE is for basement occupants and service
personnel discharging **out** to the north apron — not a shortcut from
HAB into the recycle aisle.

### 3.4 Rating

STAIR_SERVICE enclosure: **2 h**, same family as STAIR_MAINT /
SHAFT_EGRESS (AQS-BLD-001 §2). No process-atmosphere duct in the stair.
Doors at L-1 / L-2 are fire-rated stubs pending the compliance pass.

---

## 4. Yard stub enrichment (GEO / GEN / FC)

`electrical_yard.py` (west of north dock) now carries schematic:

| Family | Examples | Intent |
|---|---|---|
| Envelope | `YARD_PAD`, `YARD_FENCE_W`, `YARD_GATE_N` | Pad / fence / dock-side gate |
| Clearances | `CLEAR_BACKUP_GEN`, `CLEAR_FUEL_CELL`, `CLEAR_GEO_HP`, `CLEAR_ZNBR_AISLE` | Service / classified extent pads |
| Keep-outs | `KO_GEN_FC`, `KO_GEO_GHEX` | Separation between H₂ consumers; off-plate GHEX bore-field marker |
| Utility rough-ins | `UTIL_ROUGH_H2`, `UTIL_ROUGH_Q4`, `UTIL_ROUGH_480V`, `UTIL_ROUGH_GHEX` | Edge stubs only — not routed isometrics |
| Equipment | `BACKUP_GEN`, `GEN_H2_BUFFER`, `GEN_EXHAUST_STUB`, `FUEL_CELL`, `FC_*`, `GEO_*` | Existing envelopes + exhaust stub |

Clearance millimetres are **schematic keep-outs** for clash detection.
AHJ / NFPA 2 / 855 quantitative distances remain for the compliance
pass. No invented nameplate kW.

**Wall punch-through lock:** `BACKUP_GEN` / `FUEL_CELL` / `FC_*` east
faces shall remain west of `ENV_WALL_W` (`YARD_WALL_CLEAR` in params).
Do not place yard consumers straddling the west wall into the plate.

---

## 5. CAD / PFD hooks

| Layer | Path |
|---|---|
| Params | `freecad/params.py` — `SITE_NORTH_AXIS`, `DOCK_*`, `SERVICE_*`, `STAIR_SERVICE_*` |
| Solids | `freecad/building_stack.py`, `freecad/electrical_yard.py` |
| Groups | `freecad/plant_groups.py` — SERVICE_/DOCK*/YARD_/CLEAR_/KO_/UTIL_ROUGH_ |
| Building PFDs | `pfd_scripts/building_stack_pfds.py` — L0 plan + core orientation |
| Campus PFD | `pfd_scripts/campus_life_hazard_pfds.py` — north dock + yard |
| Stack authority | `BUILDING_STACK.md` AQS-BLD-001 Rev D |

Rebuild:

```bash
# Optional — run only in a local working hub (not published):
python3 pfd_scripts/building_stack_pfds.py
python3 pfd_scripts/campus_life_hazard_pfds.py
/usr/bin/freecadcmd models/freecad/build_plant.py
```

---

## 6. Compliance hooks

Theme-level compliance status: **AQS-CMP-001**. Quantitative study annex: **AQS-EGR-001** (`docs-authority/EGRESS_CALC.md`) — travel / exit width / basement two-exit at SCALE_M=1.0. **AHJ / PE verification required.** Still track:

1. **NFPA 101 / IBC Ch. 10** — travel distance, common path, exit width,
   stair width, discharge, illumination (NEC 700), exit signs.
2. **Two exits from L-1 process** — STAIR_SERVICE + STAIR_MAINT (or a
   second rated path); confirm neither is the sole exit from an H room
   without AHJ acceptance.
3. **CRYO room** — dedicated egress per NFPA 2/55; do not rely solely on
   the process aisle door into STAIR_SERVICE without a rated lobby.
4. **Horizontal exits / smoke barriers** — if basement length grows with
   `BASEMENT_LEVELS` / SCALE_M.
5. **OSHA 1910.36 / 1910.37** — means of egress maintenance; outdoor
   discharge to public way / apron free of ZnBr2 / H₂ classified
   envelopes where practicable.
6. **Dock accessibility** — ABA/ADA on hab and shop only remains the
   AQS-HSE-001 rule; process aisle stays restricted.

Quantitative study results: **AQS-EGR-001**. Accessibility / truck-count
items remain deferred (no invented truck counts).

---

## 7. Sync

Canonical in this tree: `docs-authority/SITE_ACCESS.md`  
