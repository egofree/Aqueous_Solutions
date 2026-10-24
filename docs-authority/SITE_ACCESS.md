# Site access: orientation, north dock, service entrance and egress

Document number: AQS-SITE-001  
Revision: E  
Date: 2026-10-24  
Basis: subordinate to AQS-BLD-001 (levels and cores) and AQS-HSE-001 (fire ratings and egress separation). Compliance themes: AQS-COMPL-001. Style: AQS-DOC-002.  
Licence: CERN-OHL-S-2.0. This is a study, not a document stamped by a professional engineer.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue: site north = +Y; north (pole-facing) L0 dock; SERVICE_ENTRY / STAIR_SERVICE; yard clearances / keep-outs / rough-ins; NFPA/OSHA egress hooks | 2026-09-28 |
| B | 1 | Compliance section (§6, now §8) pointed at AQS-COMPL-001 | 2026-10-01 |
| C | 1 | Compliance section (§6, now §8) pointed at the AQS-EGR-001 study annex | 2026-10-01 |
| D | 1 | Dock+ELEV_DOCK discrete jump; PV equator tilt evidence; yard inset | 2026-10-01 |
| E | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions; decisions and dimensions unchanged | 2026-10-24 |

## 1. Purpose and scope

This document fixes which way the building faces, where trucks are received, and how people and equipment reach the basements. It does not change `SCALE_M`, the chemistry or the locked process names.

An earlier issue of AQS-BLD-001 put the truck dock south of the core. Vertical circulation relied on the main stair `STAIR_P` (which has no door onto L-1) and the operators' stair `STAIR_MAINT`. Two site rules replaced that arrangement:

1. The main truck dock faces north (towards the pole in the northern hemisphere) at L0 grade.
2. A service entrance reaches the basements (L-1 and L-2) for equipment, and is also a secondary escape route from those levels that a code reviewer can accept. Escape from the habitation sleeping areas never passes through H-occupancy (high-hazard) areas.

This document sets the orientation, moves the dock and defines the service entrance `SERVICE_ENTRY` and its stair `STAIR_SERVICE`. The full NFPA 101 and IBC egress calculation is in AQS-EGR-001; section 8 lists what it must still cover.

## 2. Terms

Site north: the +Y direction of the model, towards the pole for a northern-hemisphere site.

Egress: the route by which occupants leave a building in an emergency (IBC chapter 10; NFPA 101).

Secondary egress: a second, independent escape route from a level or room.

Keep-out: a volume in the CAD model reserved for clearance; nothing else may be placed in it.

Rough-in: a stub showing where a utility will connect, not a routed pipe or cable.

Authority having jurisdiction (AHJ): the official or body that approves the design under the applicable codes.

Unit and object names in capitals (for example `DOCK`, `STAIR_SERVICE`) are locked CAD names. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Site orientation

Table 3.1 fixes the axes.

Table 3.1. Site axes

| Axis | Meaning | Evidence in CAD |
|---|---|---|
| **+Y** | **Site north** (pole-facing, northern hemisphere) | `ARRAY_ROOF` / `PV_ARRAY*` rotate about +X by **+SITE_LAT_DEG** so the high edge is +Y (equator / south face); `ENV_WALL_N` at `Y = PLATE_W`; life terraces on **S+E+W** |
| **+X** | Site east | `CORE_PROCESS` east half; CRYO east of CORE |
| **+Z** | Up | World Z = 0 is L0 grade FFL |

The default latitude is `SITE_LAT_DEG = 33.0`, a Dallas-class site. For a southern-hemisphere site, `building_stack.py` turns the equator-facing terrace and array rules round. The dock still faces the nearer pole, which south of the equator is −Y; a future revision of this document must say so if a southern-latitude cassette is issued. The M1 design is for the northern hemisphere. The parameter flag is `SITE_NORTH_AXIS = "+Y"`.

## 4. North dock (L0)

### 4.1 Decision

The main truck dock and receiving bay are on the north edge of the module plate at grade, with truck doors opening to +Y. The earlier south dock at `(0, 0)` is withdrawn.

Docks are added in whole steps: `DOCK_COUNT = CASSETTE_COUNT`. The M1 baseline has one dock with one freight lift (`ELEV_DOCK`). As the building grows east–west (M2 and M3 cassettes, set by `MODULE_BAYS_X`), dock and lift pairs are added along +X; a dock is never lengthened continuously. The core lift `ELEV_SVC` is separate. Table 4.1 sizes the dock objects.

Table 4.1. Dock objects

| Object | Size (m) | Plate origin (mm) | Notes |
|---|---|---|---|
| `DOCK` (× DOCK_COUNT) | 12 × 8 × slab | `(DOCK_X + n·DOCK_L, DOCK_Y)` | North-west strip; S-1 / F-1 receiving |
| `ELEV_DOCK` (× DOCK_COUNT) | 2.7 × 3.2 shaft | inside each dock bay | Freight paired with dock; L-2…L2 |
| `DOCK_APRON_N` | ≥12 × 6 | `(DOCK_X, PLATE_W)` | Exterior truck apron north of `ENV_WALL_N` |
| `DOCK_DOOR_N` | 3.6 clear × ~4.2 h | centred on north wall of each DOCK | Pole-facing loading door massing |

The manufacturing shop stays in the south-east (`MFG_X = PLATE_L/2`, `MFG_Y = 0`). The wafer fab stays in the north-east and does not overlap the west dock bay (the fab starts at `X = PLATE_L/2`). The power yard and the zinc-bromide (ZnBr2) storage stay west of the plate, aligned in Y with `DOCK_Y`, so that storage, the generator and the fuel cell sit beside the north-west apron (AQS-PWR-002, AQS-FC-001).

### 4.2 Occupancy and operation

- The dock is an S-1 or F-1 receiving occupancy (AQS-BLD-001 level table).
- No Salria, no standing hydrogen from `HDR_H2` and no bromine (Br₂) inventory inside the dock.
- The ZnBr2 storage stays outdoors (NFPA 855) and is not enclosed under the dock canopy.
- Truck numbers are not estimated in this study.

## 5. Service entrance and service stair

### 5.1 Objects

Table 5.1. Service entrance objects

| Object | Size (m) | Duty |
|---|---|---|
| `SERVICE_ENTRY` | 3.6 × 2.4 × 2.8 | L0 vestibule at north face, west strip inside DOCK Y-band |
| `SERVICE_DOOR_N` | 1.8 × 2.4 | Exterior door on north wall into SERVICE_ENTRY |
| `STAIR_SERVICE` | 2.4 × 3.6 | 2 h stair L0 ↔ L-1 ↔ L-2 |
| `STAIR_SERVICE_DOOR_Lm1` | door stub | Rated door / lobby stub at L-1 FFL |
| `STAIR_SERVICE_DOOR_Lm2` | door stub | Rated door / lobby stub at L-2 FFL |

### 5.2 Route for service and secondary egress

Figure 5.1 shows the route from the north apron to the basements.

Figure 5.1. Service and secondary egress route

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

The L0 service entrance is sized for a service cart and tool chests. Oversized freight uses the freight lift `ELEV_SVC`, which reaches L-1 only through a rated lobby (AQS-BLD-001).

### 5.3 Separation from habitation egress

Table 5.2 shows which stairs serve which occupants.

Table 5.2. Stairs and their occupants

| Stair | Levels | Hab sleeping exit? | Notes |
|---|---|---|---|
| `STAIR_P` | L2–L0 | **Yes** (primary) | **No L-1 door** — unchanged |
| `STAIR_S1` / `STAIR_S2` | L1–L0 | **Yes** (secondary) | Perimeter; opposite corners |
| `STAIR_MAINT` | L0–L-2 | **No** | Operators only; not credited as public egress |
| `STAIR_SERVICE` | L0–L-2 | **No** for hab | Basement **secondary egress** + service; discharge to exterior at L0 north — does **not** walk hab occupants through H areas |

WARNING: Escape from the habitation sleeping areas shall reach grade by `STAIR_P` or `STAIR_S*` without entering the L-1 process areas or the CRYO rooms (IBC 1016 and NFPA 101 principles; AQS-HSE-001 §10). `STAIR_SERVICE` serves basement occupants and service staff leaving outwards to the north apron. It is not a route from the habitation into the recycling aisle.

### 5.4 Fire rating

The `STAIR_SERVICE` enclosure is rated 2 h, like `STAIR_MAINT` and `SHAFT_EGRESS` (AQS-BLD-001 §5). No duct carrying process atmosphere runs in the stair. The doors at L-1 and L-2 are fire-rated stubs until the compliance pass.

## 6. Outdoor yard: generator, fuel cell and ground-source heat pump

`electrical_yard.py`, west of the north dock, models the yard objects in Table 6.1 as schematic massing.

Table 6.1. Yard objects

| Family | Examples | Intent |
|---|---|---|
| Envelope | `YARD_PAD`, `YARD_FENCE_W`, `YARD_GATE_N` | Pad / fence / dock-side gate |
| Clearances | `CLEAR_BACKUP_GEN`, `CLEAR_FUEL_CELL`, `CLEAR_GEO_HP`, `CLEAR_ZNBR_AISLE` | Service / classified extent pads |
| Keep-outs | `KO_GEN_FC`, `KO_GEO_GHEX` | Separation between H₂ consumers; off-plate GHEX bore-field marker |
| Utility rough-ins | `UTIL_ROUGH_H2`, `UTIL_ROUGH_Q4`, `UTIL_ROUGH_480V`, `UTIL_ROUGH_GHEX` | Edge stubs only — not routed isometrics |
| Equipment | `BACKUP_GEN`, `GEN_H2_BUFFER`, `GEN_EXHAUST_STUB`, `FUEL_CELL`, `FC_*`, `GEO_*` | Existing envelopes + exhaust stub |

The clearance dimensions are schematic keep-outs for clash detection. Distances required by the AHJ, NFPA 2 and NFPA 855 are left to the compliance pass, and no nameplate power is invented.

The east faces of `BACKUP_GEN`, `FUEL_CELL` and `FC_*` stay west of `ENV_WALL_W` (`YARD_WALL_CLEAR` in the parameters). No yard equipment may straddle the west wall into the plate.

## 7. Where this is modelled

Table 7.1 lists the files that implement this document.

Table 7.1. CAD and drawing files

| Layer | Path |
|---|---|
| Params | `freecad/params.py` — `SITE_NORTH_AXIS`, `DOCK_*`, `SERVICE_*`, `STAIR_SERVICE_*` |
| Solids | `freecad/building_stack.py`, `freecad/electrical_yard.py` |
| Groups | `freecad/plant_groups.py` — SERVICE_/DOCK*/YARD_/CLEAR_/KO_/UTIL_ROUGH_ |
| Building PFDs | `flow_graph/exporters/matplotlib/building_stack_pfds.py` — L0 plan + core orientation |
| Campus PFD | `flow_graph/exporters/matplotlib/campus_life_hazard_pfds.py` — north dock + yard |
| Stack authority | `BUILDING_STACK.md` AQS-BLD-001 Rev G |

To rebuild, run from the repository root:

```bash
python3 flow_graph/exporters/matplotlib/building_stack_pfds.py
python3 flow_graph/exporters/matplotlib/campus_life_hazard_pfds.py
/usr/bin/freecadcmd models/freecad/build_plant.py
```

## 8. Compliance

Theme-level compliance status is in AQS-COMPL-001. The quantitative egress study is AQS-EGR-001 (`docs-authority/EGRESS_CALC.md`): travel distance, exit width and the two exits from the basement at `SCALE_M=1.0`. The AHJ or a professional engineer must verify it. The following remain to be tracked:

1. NFPA 101 and IBC chapter 10: travel distance, common path of travel, exit and stair width, discharge, emergency lighting (NEC 700) and exit signs.
2. Two exits from the L-1 process level: `STAIR_SERVICE` and `STAIR_MAINT`, or a second rated path. Confirm that neither is the only exit from an H room without the AHJ's acceptance.
3. The CRYO room has its own egress under NFPA 2 and NFPA 55; it must not rely only on the process aisle door into `STAIR_SERVICE` without a rated lobby.
4. Horizontal exits and smoke barriers, if the basement lengthens with `BASEMENT_LEVELS` or `SCALE_M`.
5. OSHA 1910.36 and 1910.37: maintenance of the means of egress; outdoor discharge to the public way or apron clear of the ZnBr2 and hydrogen hazardous-area envelopes where practicable.
6. Accessibility under the Architectural Barriers Act (ABA) and the Americans with Disabilities Act (ADA) applies to the habitation and shop only, as AQS-HSE-001 sets out; the process aisle stays restricted.

Accessibility and truck numbers remain deferred; no truck numbers are invented.
