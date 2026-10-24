# Scale model: parametric building growth

Document number: AQS-SCALE-001  
Revision: D  
Date: 2026-10-24  
Basis: subordinate to AQS-BLD-001 (`BUILDING_STACK.md`) for levels, cores, shafts and fire ratings. Dimensions in millimetres are set in `models/freecad/params.py`.  
Licence: CERN-OHL-S-2.0.

| Rev | Description | Date |
|---|---|---|
| C | Parametric growth rules for plan area, cassettes, life floors, basements, tanks, electrical modules and overflow terraces | 2026-09-27 |
| D | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; rules and values unchanged | 2026-10-24 |

## 1. Purpose and scope

The plant is designed so that a larger version can be generated from the same model by changing one or two parameters. This document states how each part of the building grows when those parameters change: plan area, process cassettes, life floors, basement depth, tanks, electrical modules and overflow terraces. It gives the rules; the numbers they produce come from `models/freecad/params.py`.

Levels, cores, shafts and fire ratings are set by AQS-BLD-001 and are not changed here. Planting and irrigation of the terraces are covered by AQS-TRR-001.

## 2. Terms

Bay: one 6 × 6 m structural grid square (`BAY` = 6000 mm).

Plate: the floor area of one level, a whole number of bays in each direction (`PLATE_L` × `PLATE_W`).

Cassette: a process train sized for a set throughput. M1, M2 and M3 are the three sizes; `CASSETTE_COUNT` is 1, 2 or 3.

Continuous growth: a dimension that changes smoothly with scale, such as a tank footprint.

Discrete growth: growth by whole units, such as one more floor, one more dock or one more battery pack.

Life floor: a level holding the habitation (west) and the farm (east) side by side.

Finished-floor level (FFL): the height of a floor surface. `Z_L0` is grade.

## 3. Vertical order

The order of the floors is the same at every scale (Figure 3.1). The roof tank is always at the top and the catch tank always at the bottom; manufacturing is always at ground level; the wet process line and the cryogenic plant (CRYO) are always below ground.

Figure 3.1. Fixed vertical order, top to bottom

```
ROOF_TANK                         ← always top (continuous footprint)
── discrete LIFE floors ──        ← HAB ∥ FARM pair per floor (never mixed)
L0  MFG / WAFER_FAB / dock        ← MFG always at ground
── discrete BASEMENT levels ──    ← wet line + CRYO (always underground)
CATCH_TANK                        ← always deepest (continuous footprint)
```

Life floors are added as whole plates between the roof tank and L0; a single plate is never stretched in height. Basements are likewise added as whole process plates below grade, not only by adding bays horizontally. `CATCH_TANK` stays below every process basement.

## 4. Primary drivers

Set one of the two drivers in Table 4.1.

Table 4.1. Primary scale drivers

| Driver | Meaning | Baseline |
|---|---|---|
| `SCALE_M` | Linear module scale; 1 = 24 × 18 m plate | `1.0` |
| `MODULE_BAYS_X`, `MODULE_BAYS_Y` | Explicit 6 m bay counts (override) | 4 × 3 |

When only `SCALE_M` is set, the other quantities follow from it as shown in Figure 4.1. The bay grid and the core stay on the centreline of the plate (`CORE_X = (PLATE_L − CORE_L) / 2`, and likewise in Y).

Figure 4.1. Quantities derived from `SCALE_M`

```
MODULE_BAYS_X = max(1, round(4 × SCALE_M))
MODULE_BAYS_Y = max(1, round(3 × SCALE_M))
PLATE_L = MODULE_BAYS_X × BAY      # BAY = 6000 mm
PLATE_W = MODULE_BAYS_Y × BAY
AREA_SCALE = (PLATE_L × PLATE_W) / (24 000 × 18 000)
LIFE_LEVELS     = max(1, floor(SCALE_M))
BASEMENT_LEVELS = max(1, floor(SCALE_M))
```

Different parts of the building grow in different ways. Tank footprints grow continuously; L0 shops, life floors, basements and electrical modules grow in discrete steps. Sections 5 to 10 give each rule.

## 5. Tanks: continuous growth with plan area

The footprints of `ROOF_TANK` (top) and `CATCH_TANK` (bottom) grow in proportion to plan area, so their volumes do too at fixed height (Table 5.1).

Table 5.1. Tank scaling

| Param | Rule |
|---|---|
| `ROOF_TANK_L`, `ROOF_TANK_W` | baseline × √`AREA_SCALE` |
| `CATCH_TANK_L`, `CATCH_TANK_W` | baseline × √`AREA_SCALE` |
| `ROOF_TANK_H`, `CATCH_TANK_H` | fixed (7 m / 4 m) |

At M1 the roof tank is 16 × 12 × 7 m and the catch tank 12 × 8 × 4 m. Both are recentred on the plate. `ROOF_TANK_Z = Z_L2`; `CATCH_TANK_Z = Z_Lm2`, which is always below the lowest process basement.

## 6. Manufacturing and fab on L0: discrete growth

`MFG_SHOP` and `WAFER_FAB` are always on L0. They grow horizontally only when the plate length in X reaches the next cassette size (AQS-BLD-001 §7), as Table 6.1 shows.

Table 6.1. Cassette steps

| Cassette | `MODULE_BAYS_X` | Length | Wet feed | Envelope growth |
|---|---|---|---|---|
| M1 | 4 … 5 | 24–30 m | 150 kg/d | baseline |
| M2 | 6 … 7 | 36–42 m | 300 kg/d | +1 bay on shop/fab X |
| M3 | ≥ 8 | ≥ 48 m | 500 kg/d | +2 bays on shop/fab X |

The parameters are `CASSETTE_COUNT` (1, 2 or 3) and `CASSETTE_ID` (M1, M2 or M3). Table 6.2 gives the block rules.

Table 6.2. L0 block rules

| Block | Rule |
|---|---|
| `MFG_L` / `FAB_L` | 12 000 + (`CASSETTE_COUNT` − 1) × `BAY` |
| `MFG_Z` / `FAB_Z` | always `Z_L0` |
| `DOCK_COUNT` | `CASSETTE_COUNT` — **one dock + ELEV_DOCK pair at M1**; add pairs E–W |
| `DOCK_L` / `ELEV_DOCK_*` | one receiving bay + paired freight elevator per count |

### 6.1 Docks and freight lifts

The M1 module (`CASSETTE_COUNT = 1`) has one north dock (`DOCK`) with one freight lift (`ELEV_DOCK`) inside that bay. The core lift `ELEV_SVC` is the central shaft and does not count as a dock lift.

When `MODULE_BAYS_X` reaches M2 or M3 (`CASSETTE_COUNT` 2 or 3), whole dock and lift pairs are added along +X (`DOCK_2`, `ELEV_DOCK_2`, and so on). A single dock is never stretched along the north face without adding lifts, because freight staging and egress discharge grow with the number of receiving fronts.

## 7. Life floors: discrete growth

Whole life floors are added between the roof tank and L0. Each floor has the habitation on the west and the farm on the east, and uses are never mixed on one plate. Figure 7.1 gives the floor heights and Table 7.1 some examples.

Figure 7.1. Life floor levels

```
LIFE_LEVELS = max(1, floor(SCALE_M))
life_z(i)   = Z_L1 + i × CLEAR_L1     # i = 0 … LIFE_LEVELS−1
Z_L2        = Z_L1 + LIFE_LEVELS × CLEAR_L1
```

Table 7.1. Life floors by scale

| `SCALE_M` | `LIFE_LEVELS` | Life FFLs |
|---|---|---|
| 1.0 | 1 | `Z_L1` |
| 2.0 | 2 | `Z_L1`, `Z_L1 + CLEAR_L1` |
| 3.0 | 3 | three stacked life floors |

CAD names: floor 0 keeps `HABITATION` and `FARM`; floors n ≥ 2 are named `HABITATION_S{n}` and `FARM_S{n}`.

## 8. Basements: discrete growth

The wet line and CRYO are always below ground. Capacity grows by adding whole process basement plates, not by raising them to L0 and not only by adding bays horizontally (Figure 8.1, Table 8.1).

Figure 8.1. Basement levels

```
BASEMENT_LEVELS = max(1, floor(SCALE_M))
basement_z(i)   = −CLEAR_Lm1 × (i + 1)   # i = 0 = uppermost (classic L-1)
Z_Lm1           = basement_z(0)
Z_Lm2           = basement_z(BASEMENT_LEVELS − 1) − CLEAR_Lm2  # CATCH FFL
```

Table 8.1. Basement floor levels by scale (mm)

| `SCALE_M` | `BASEMENT_LEVELS` | Process FFLs | Catch FFL |
|---|---|---|---|
| 1.0 | 1 | −6 000 | −10 500 |
| 2.0 | 2 | −6 000, −12 000 | −16 500 |

- The main wet cassette stays on the uppermost basement (`Z_PROCESS = Z_Lm1`); `build_plant.py` shifts it once by `Z_Lm1`. Extra basements get process keep-out stubs (`PROCESS_B{n}`) and CRYO copies.
- CRYO has one cold-box bay per basement level at `(CRYO_X, CRYO_Y)`, `z = basement_z(i)`, named `CRYO`, `CRYO_B2` and so on.
- `CATCH_TANK` and `HYDRO_SET` stay on the catch plate (`Z_Lm2`), always the deepest level.

## 9. Electrical modules and surplus power

The plant's electrical need in kW and the overproduction target set the number of electrical modules; a single skid is never stretched (Table 9.1).

Table 9.1. Electrical module rules

| Param | Baseline (M1) | Role |
|---|---|---|
| `ELEC_NEED_KW_BASE` | 50 | peak plant need |
| `ELEC_OVERPROD` | 1.4 | PV overproduction target |
| `ELEC_NEED_KW` | base × cassette × (0.6 + 0.2×life + 0.2×basement) | derived |
| `ELEC_TARGET_KW` | need × overprod | PV sizing target |
| `PV_COUNT` | ceil(target / 70 kW) | PV array modules |
| `ZNBR_COUNT` | max(ceil(need/60), ceil(2 h × need/120 kWh)) | ZnBr2 packs |
| `RECT_COUNT` | `CASSETTE_COUNT` | rectifier skids |

Surplus energy is handled by control, not geometry, in this order:

1. Charge the zinc-bromide (ZnBr2) batteries.
2. When the batteries accept no more charge, pump extra clean tower water up to `ROOF_TANK` (reverse flow in the penstock, or tower fill).
3. When the tank and the batteries are both full, overflow in a controlled way to the outdoor garden terraces (`OVERFLOW_TERRACE_*` stubs), never to the process basement bund.

### 9.1 Methanol storage and pumped hydro

PV, ZnBr₂ and rectifier counts step with `ELEC_NEED` and `ELEC_TARGET` (Table 9.1). The methanol tank and fuel-cell bank have no `SCALE_M` rule here; their study sizing is in AQS-ESS-001 and AQS-SCALE-UR-001 Rev B (bank of 1 to 4 modules; synthesis in proportion to the Faraday hydrogen). Pumped-hydro energy is E = ρVgh from the roof and catch tank geometry (AQS-BLD-001 §6): at M1, 263.6 kWh ideal against 3,501 kWh of ZnBr₂ (AQS-BLD-014, Q-009). This is a deliberate asymmetry in the study sizing, not an omission. Pumped hydro becomes significant only by growing the tank volume, not the bay count alone.

## 10. Overflow terraces

The terraces slope towards the equator at the site latitude `SITE_LAT_DEG`, and wrap round the east and west edges at the same slope (Table 10.1).

Table 10.1. Terrace faces by hemisphere

| Hemisphere | Faces |
|---|---|
| Northern (`SITE_LAT_DEG` ≥ 0) | South + East + West |
| Southern (`SITE_LAT_DEG` < 0) | North + East + West |

When the ZnBr2 batteries accept no more charge and `ROOF_TANK` is full, clean water overflows in a controlled way along the path `OVERFLOW_SPILL_ROOF`, `OVERFLOW_DOWNCOMER_{S|N}`, `OVERFLOW_OUTFALL_{S|N}`, then down the stepped bands `OVERFLOW_TERRACE_{face}_B{n}`. It never reaches the process basement bund. The surplus order of section 9 applies.

The CAD model shows only the massing of the terraces (Table 10.2), not planting, irrigation or landscape.

Table 10.2. Terrace massing names

| Param / name | Role |
|---|---|
| `TERRACE_BANDS`, `TERRACE_RUN`, `TERRACE_DROP` | N stepped bands; plan run; total outer drop |
| `OVERFLOW_TERRACE_{S|N|E|W}_B{n}` | Band solids (n = 1 inner … N outer) |
| `OVERFLOW_TERRACE_{S|N|E|W}` | Family labels (locked short names) |
| `OVERFLOW_APRON_*` | Grade apron at plate face |
| `OVERFLOW_SPILL_ROOF` / `OVERFLOW_DOWNCOMER_*` | Roof-tank → terrace link stubs |

The grade reference is `Z_L0`. Planting, irrigation, open or enclosed greenhouses and drain routing are set by AQS-TRR-001 (`docs-authority/TERRACE_LANDSCAPE.md`). The massing names above remain the CAD anchors, and the landscape document does not change the band geometry.

## 11. Rebuilding the model

```bash
cd models/freecad
/usr/bin/freecadcmd build_plant.py
```

Table 11.1. Rebuild settings

| `SCALE_M` | Bays | Cassette | Life | Basement | Notes |
|---|---|---|---|---|---|
| 1.0 | 4×3 | M1 | 1 | 1 | baseline plate |
| 2.0 | 8×6 | M3 | 2 | 2 | review-only larger plant; PV/ZnBr2/RECT jumps; `CRYO_B2` / `PROCESS_B2` |

The saved `plant.FCStd` was built at `SCALE_M = 1.0` on 2026-09-27 as the manufacturing baseline: 4 × 3 bays (24 × 18 m plate; see open question Q-015), cassette M1, `LIFE_LEVELS=1`, `BASEMENT_LEVELS=1`, roof tank 16 × 12 × 7 m, catch tank 12 × 8 × 4 m, and one each of the PV, ZnBr and rectifier modules. A review build at `SCALE_M = 2.0` was made earlier that day and is no longer the saved plant. Use 2.0 only for deliberate review rebuilds (Table 11.1).

## 12. Parameter index

These names are locked: `SCALE_M`, `MODULE_BAYS_X`, `MODULE_BAYS_Y`, `BAY`, `PLATE_L`, `PLATE_W`, `AREA_SCALE`, `CASSETTE_COUNT`, `CASSETTE_ID`, `LIFE_LEVELS`, `BASEMENT_LEVELS`, `life_z()`, `basement_z()`, `Z_L0`, `Z_L1`, `Z_L2`, `Z_Lm1`, `Z_Lm2`, `ROOF_TANK_*`, `CATCH_TANK_*`, `MFG_*`, `FAB_*`, `CRYO_*`, `ELEC_NEED_KW`, `ELEC_TARGET_KW`, `PV_COUNT`, `ZNBR_COUNT`, `RECT_COUNT`, `ELEC_OVERPROD`, `TERRACE_RUN`, `TERRACE_WIDTH`, `TERRACE_BANDS`, `TERRACE_DROP`, `TERRACE_DOWNCOMER_D`, `SITE_LAT_DEG`.
