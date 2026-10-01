# Scale model — parametric building growth

Document number: AQS-SCALE-001  
Revision: C
Date: 2026-09-27

Authority: subordinate to AQS-BLD-001 (`BUILDING_STACK.md`) for levels,
cores, shafts, and fire ratings. This file defines *how* plan area,
cassette count, life floors, basement depth, tanks, electrical modules,
and overflow terraces grow. Millimetre truth: `cad/freecad/params.py`.

Licence: CERN-OHL-S-2.0.

---

## 0. Locked vertical order (top → bottom)

Always, regardless of scale:

```
ROOF_TANK                         ← always top (continuous footprint)
── discrete LIFE floors ──        ← HAB ∥ FARM pair per floor (never mixed)
L0  MFG / WAFER_FAB / dock        ← MFG always at ground
── discrete BASEMENT levels ──    ← wet line + CRYO (always underground)
CATCH_TANK                        ← always deepest (continuous footprint)
```

Life floors are **discrete plates** stacked between the roof tank and
L0 — not a continuous height stretch of one plate. Basement growth is
**discrete process plates** added below grade — not only horizontal
bay jumps. `CATCH_TANK` stays under every process basement.

---

## 1. Primary drivers

Set **one** of:

| Driver | Meaning | Baseline |
|---|---|---|
| `SCALE_M` | Linear module scale; 1 = 24 × 18 m plate | `1.0` |
| `MODULE_BAYS_X`, `MODULE_BAYS_Y` | Explicit 6 m bay counts (override) | 4 × 3 |

Derivation when only `SCALE_M` is set:

```
MODULE_BAYS_X = max(1, round(4 × SCALE_M))
MODULE_BAYS_Y = max(1, round(3 × SCALE_M))
PLATE_L = MODULE_BAYS_X × BAY      # BAY = 6000 mm
PLATE_W = MODULE_BAYS_Y × BAY
AREA_SCALE = (PLATE_L × PLATE_W) / (24 000 × 18 000)
LIFE_LEVELS     = max(1, floor(SCALE_M))
BASEMENT_LEVELS = max(1, floor(SCALE_M))
```

Bay grid and CORE stay on the plate centreline
(`CORE_X = (PLATE_L − CORE_L) / 2`, same for Y).

**NOTE**

Not everything scales the same way. Continuous tank footprint, discrete
L0 horizontal jumps, discrete life floors, discrete basement depth, and
electrical module counts are separate rules below.

---

## 2. Continuous with footprint (tanks)

`ROOF_TANK` (top) and `CATCH_TANK` (deepest) footprint — and therefore
volume at fixed height — scale **∝ plan area** at the same rate:

| Param | Rule |
|---|---|
| `ROOF_TANK_L`, `ROOF_TANK_W` | baseline × √`AREA_SCALE` |
| `CATCH_TANK_L`, `CATCH_TANK_W` | baseline × √`AREA_SCALE` |
| `ROOF_TANK_H`, `CATCH_TANK_H` | fixed (7 m / 4 m) |

Baseline M1: roof 16 × 12 × 7 m; catch 12 × 8 × 4 m. Tank XY recentred
on the plate. `ROOF_TANK_Z = Z_L2`; `CATCH_TANK_Z = Z_Lm2` (always
below the lowest process basement).

---

## 3. Discrete jumps — L0 horizontal (MFG / FAB)

`MFG_SHOP` and `WAFER_FAB` stay on **L0 ground** always. They expand
horizontally only when X-bay length unlocks the next cassette
(AQS-BLD-001 §4):

| Cassette | `MODULE_BAYS_X` | Length | Wet feed | Envelope growth |
|---|---|---|---|---|
| M1 | 4 … 5 | 24–30 m | 150 kg/d | baseline |
| M2 | 6 … 7 | 36–42 m | 300 kg/d | +1 bay on shop/fab X |
| M3 | ≥ 8 | ≥ 48 m | 500 kg/d | +2 bays on shop/fab X |

Params: `CASSETTE_COUNT` ∈ {1,2,3}, `CASSETTE_ID` ∈ {M1,M2,M3}.

| Block | Rule |
|---|---|
| `MFG_L` / `FAB_L` | 12 000 + (`CASSETTE_COUNT` − 1) × `BAY` |
| `MFG_Z` / `FAB_Z` | always `Z_L0` |
| `DOCK_COUNT` | `CASSETTE_COUNT` — **one dock + ELEV_DOCK pair at M1**; add pairs E–W |
| `DOCK_L` / `ELEV_DOCK_*` | one receiving bay + paired freight elevator per count |

### 3.1 Discrete jumps — dock + freight elevator

Baseline manufacturing module (M1, `CASSETTE_COUNT = 1`): **one** north
dock space (`DOCK`) and **one** associated freight elevator
(`ELEV_DOCK`) inside that bay. CORE `ELEV_SVC` remains the central
shaft and is **not** counted as the dock pair.

When `MODULE_BAYS_X` unlocks M2 / M3 (`CASSETTE_COUNT` 2 / 3), add
whole **dock + ELEV_DOCK** pairs along +X (`DOCK_2`, `ELEV_DOCK_2`, …).
Do not stretch a single dock continuously across the north face without
adding elevator pairs — freight staging and egress discharge scale with
receiving fronts.


---

## 4. Discrete life floors (HAB ∥ FARM)

Between roof tank and L0, add whole **life floors** — each floor is
HAB west + FARM east, side-by-side, never mixed uses on one plate.
Not a continuous stretch of a single plate height.

```
LIFE_LEVELS = max(1, floor(SCALE_M))
life_z(i)   = Z_L1 + i × CLEAR_L1     # i = 0 … LIFE_LEVELS−1
Z_L2        = Z_L1 + LIFE_LEVELS × CLEAR_L1
```

| `SCALE_M` | `LIFE_LEVELS` | Life FFLs |
|---|---|---|
| 1.0 | 1 | `Z_L1` |
| 2.0 | 2 | `Z_L1`, `Z_L1 + CLEAR_L1` |
| 3.0 | 3 | three stacked life floors |

CAD names: floor 0 keeps `HABITATION` / `FARM`; floors n≥2 use
`HABITATION_S{n}` / `FARM_S{n}`.

---

## 5. Discrete basement levels (wet + CRYO)

Wet line and CRYO are **always underground**. Capacity / depth grows by
adding discrete process basement plates under grade — not by raising
them to L0, and not only by horizontal bay jumps.

```
BASEMENT_LEVELS = max(1, floor(SCALE_M))
basement_z(i)   = −CLEAR_Lm1 × (i + 1)   # i = 0 = uppermost (classic L-1)
Z_Lm1           = basement_z(0)
Z_Lm2           = basement_z(BASEMENT_LEVELS − 1) − CLEAR_Lm2  # CATCH FFL
```

| `SCALE_M` | `BASEMENT_LEVELS` | Process FFLs | Catch FFL |
|---|---|---|---|
| 1.0 | 1 | −6 000 | −10 500 |
| 2.0 | 2 | −6 000, −12 000 | −16 500 |

- Primary wet cassette stays on uppermost basement (`Z_PROCESS = Z_Lm1`);
  `build_plant.py` shifts once by `Z_Lm1`. Extra basements get process
  keep-out stubs (`PROCESS_B{n}`) plus CRYO replicas.
- CRYO: one cold-box bay per basement level at `(CRYO_X, CRYO_Y)`,
  `z = basement_z(i)`. Names: `CRYO`, `CRYO_B2`, …
- `CATCH_TANK` and `HYDRO_SET` remain on the catch plate (`Z_Lm2`),
  always deepest.

---

## 6. Electrical discrete jumps + surplus water

Building electrical need (kW) and overproduction target drive module
**counts** (not continuous stretch of one skid):

| Param | Baseline (M1) | Role |
|---|---|---|
| `ELEC_NEED_KW_BASE` | 50 | peak plant need |
| `ELEC_OVERPROD` | 1.4 | PV overproduction target |
| `ELEC_NEED_KW` | base × cassette × (0.6 + 0.2×life + 0.2×basement) | derived |
| `ELEC_TARGET_KW` | need × overprod | PV sizing target |
| `PV_COUNT` | ceil(target / 70 kW) | PV array modules |
| `ZNBR_COUNT` | max(ceil(need/60), ceil(2 h × need/120 kWh)) | ZnBr2 packs |
| `RECT_COUNT` | `CASSETTE_COUNT` | rectifier skids |

Surplus energy policy (control, not geometry):

1. Prefer charge ZnBr2.
2. If batteries accept no more charge → pump extra clean tower water
   toward `ROOF_TANK` (penstock reverse / tower fill).
3. If tank **and** batteries are full → controlled overflow to external
   **garden terraces** (`OVERFLOW_TERRACE_*` stubs). Never to process
   basement bund.

---


### 6.1 MeOH and pumped-hydro vs SCALE_M (study — 2026-10-01)

PV / ZnBr₂ / RECT jump with `ELEC_NEED` / `ELEC_TARGET` (§6). **MeOH** tank and
FC bank have **no** SCALE_M discrete formula here — study sizing lives in
**AQS-ESS-001** / **AQS-SCALE-UR-001** Rev B (bank 1–4 modules; synth ∝ Faraday
H₂). **Pumped hydro** energy is \(E=\rho V g h\) from roof/catch geometry
(AQS-BLD-001 §3): M1 ~**9.8 kWh** ideal ≪ ZnBr₂ **120 kWh** — documented
**study sizing asymmetry**, not a silent omission. Growing tank volume (not
bay count alone) is the path to material hydro energy.

## 7. Overflow terraces (sloped band massing)

Equator-facing slope follows site latitude `SITE_LAT_DEG`. Wrap the
east and west edges at the same slope. Hemisphere rule:

| Hemisphere | Faces |
|---|---|
| Northern (`SITE_LAT_DEG` ≥ 0) | South + East + West |
| Southern (`SITE_LAT_DEG` < 0) | North + East + West |

**Path (conceptual):** when ZnBr2 will accept no more charge and
`ROOF_TANK` is full → controlled clean-water overflow
`OVERFLOW_SPILL_ROOF` → `OVERFLOW_DOWNCOMER_{S|N}` →
`OVERFLOW_OUTFALL_{S|N}` → stepped `OVERFLOW_TERRACE_{face}_B{n}`
bands. Never to process basement bund. Same surplus policy as §6.

CAD massing (not planting / irrigation / full landscape):

| Param / name | Role |
|---|---|
| `TERRACE_BANDS`, `TERRACE_RUN`, `TERRACE_DROP` | N stepped bands; plan run; total outer drop |
| `OVERFLOW_TERRACE_{S|N|E|W}_B{n}` | Band solids (n = 1 inner … N outer) |
| `OVERFLOW_TERRACE_{S|N|E|W}` | Family labels (locked short names) |
| `OVERFLOW_APRON_*` | Grade apron at plate face |
| `OVERFLOW_SPILL_ROOF` / `OVERFLOW_DOWNCOMER_*` | Roof-tank → terrace link stubs |

Grade reference `Z_L0`. Planting, irrigation, open vs enclosed
greenhouse, and drain routing: **AQS-TRR-001**
(`cad/TERRACE_LANDSCAPE.md`) — massing names above remain the CAD
anchors; landscape authority does not change band geometry.

---

## 8. Rebuild

```bash
cd cad/freecad
/usr/bin/freecadcmd build_plant.py
```

| `SCALE_M` | Bays | Cassette | Life | Basement | Notes |
|---|---|---|---|---|---|
| 1.0 | 4×3 | M1 | 1 | 1 | baseline plate |
| 2.0 | 8×6 | M3 | 2 | 2 | review-only larger plant; PV/ZnBr2/RECT jumps; `CRYO_B2` / `PROCESS_B2` |

**Current on-disk `plant.FCStd`:** built and saved at **`SCALE_M = 1.0`**
(2026-09-27, manufacturing baseline). M1 bay counts: **4 × 3**
(24 × 18 m plate), cassette **M1**, `LIFE_LEVELS=1`, `BASEMENT_LEVELS=1`,
tanks roof 16 × 12 × 7 m / catch 12 × 8 × 4 m, electrical PV/ZnBr/RECT = 1.
`SCALE_M = 2.0` was a review-only on-disk pass earlier the same day and
is no longer the saved plant; restore to 2.0 only for intentional review
rebuilds (`SCALE_MODEL.md` §8 table).

---

## 9. Param index (locked names)

`SCALE_M`, `MODULE_BAYS_X`, `MODULE_BAYS_Y`, `BAY`, `PLATE_L`,
`PLATE_W`, `AREA_SCALE`, `CASSETTE_COUNT`, `CASSETTE_ID`,
`LIFE_LEVELS`, `BASEMENT_LEVELS`, `life_z()`, `basement_z()`,
`Z_L0`, `Z_L1`, `Z_L2`, `Z_Lm1`, `Z_Lm2`, `ROOF_TANK_*`,
`CATCH_TANK_*`, `MFG_*`, `FAB_*`, `CRYO_*`, `ELEC_NEED_KW`,
`ELEC_TARGET_KW`, `PV_COUNT`, `ZNBR_COUNT`, `RECT_COUNT`,
`ELEC_OVERPROD`, `TERRACE_RUN`, `TERRACE_WIDTH`, `TERRACE_BANDS`,
`TERRACE_DROP`, `TERRACE_DOWNCOMER_D`, `SITE_LAT_DEG`.
