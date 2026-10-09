# Building stack — vertical campus

Document number: AQS-BLD-001  
Revision: F
Date: 2026-10-01  
Authority: AQS-AUTH-001 (active CAD levels/cores/shafts). Compliance themes: AQS-CMP-001. Style: AQS-DOC-001.

One structural module. Chemistry and locked names do not change.
Horizontal campus envelopes in `PHASE_F_ENVELOPES.md` remain the
keep-out sizes *inside* these floors. This file places those boxes
on levels.

Licence: CERN-OHL-S-2.0. No diffusion pictures.

## Authority (locked 2026-09-27)

This file (AQS-BLD-001 Rev F) is the **active CAD authority** for
levels, cores, shafts, and stacked masses. See `cad/AUTHORITY.md`.
`PHASE_F_ENVELOPES.md` supplies keep-out sizes and utilities only;
its flat Z=0 origins are not placement authority.

---

## Purpose

Lock the vertical campus: levels, cores, shafts, and stacked masses for
FreeCAD `plant.FCStd` and building PFDs.

## Scope

In: level datums, fire cores, dock/service massing hooks, FAB/CRY/MFG
cassette footprints at `SCALE_M = 1.0`.  
Out: chemistry locks; PHASE_F flat Z=0 origins as placement authority;
root narrative chapters.

| Rev | Change | Description | Date |
|---|---|---|---|
| A–D | — | Prior stack issues (see git-less changelog in Rem-BLD) | 2026-09-27 |
| E | 1 | FAB/CRY layout relief (AQS-AUD-001 Rev D) | 2026-10-01 |
| F | 1 | Layout locks: equator PV tilt; life-floor terraces+doors; dock+ELEV_DOCK discrete E–W jump; yard inset (no wall punch) | 2026-10-01 |

## 0. Why stack this way

Gravity does the work that pumps should not be trusted with:

- Dirty liquor cannot drain uphill into HABITATION or FARM.
- Clean water sits above demand. HDR_UPW and hab/farm taps are
  gravity-first, pumped-second.
- Solids arrive at grade and drop into HOPPER / LEACH CSTR 1.
- H₂ is lighter than air. It is *generated* in the basement (EW
  cathodes) but it does not *dwell* there: HDR_H2 is a vertical
  riser with no traps to a roof vent / CRYO / fuel. ZnBr2 skid stays
  outdoor at grade (NFPA 855). CRYO sits on L-1 east of CORE in a
  2 h rated room with dedicated NFPA 2/55 ventilation (not a shared
  process pit; no process-air duct through FB_CRYO_PROCESS).

IBC 2024 Table 508.4, sprinklered throughout (NFPA 13):

| Pair | Horizontal assembly |
|---|---|
| R over H-3 / H-4 | 2 h (NS = not permitted) |
| R over H-2 | 3 h (NS = NP) |
| R over F-1 / S-1 | 1 h |
| R over H-5 | 2 h (NS = NP) |

Plant standard is stricter than the H-3 cell: **3 h** between
HABITATION and the recycle basement, matching AQS-HSE-001.
Building is NFPA 13 throughout. Non-sprinklered R over H is NP.

---

## 1. Levels (one module)

Structural bay **6.0 × 6.0 m**. Module plate **24 × 24 m**
(4 × 4 bays) = 576 m². The 24 × 18 m, 432 m² plate is retired. AQS-PLAN-001 Rev B.
Clear heights are to underside of the next slab.

| Level | Name | Clear | Occupancy | Holds |
|---|---|---|---|---|
| L-2 | SUB-BASEMENT | 4.5 m | F-1 / utility | CATCH TANK, hydro turbine-pump, process sumps |
| L-1 | BASEMENT | 6.0 m | F-1 + H-3 if MAQ | LEACH, EW, BMED, CRU, OIL, GLASS, scrubbers, CRYO (rated room) |
| L0 | GRADE | 6.0 m | F-1 / S-1 / H-5 pocket | Dock, MFG SHOP, WAFER FAB bay, POWER (ZnBr2 outdoor) |
| L1 | LIFE | 4.8 m | R-2 + F-2 | HABITATION, FARM (2 h between them) |
| L2 | ROOF | tank 6–8 m | S-2 water / U | ROOF TANK, PV, stacks, H2 vent |

Outdoor, not stacked: ZnBr2 skid, truck apron, PV field if desert.

Gross height grade-to-tank-top ≈ 6 + 4.8 + 7 ≈ 18 m plus basement
10.5 m below grade. Hydro head ≈ 16–20 m roof waterline to CATCH
TANK waterline.

---

## 2. Fire / shaft rules

| Assembly | Rating | Notes |
|---|---|---|
| HA_L2_L1 | 1 h | tank / life. Tank is noncombustible. |
| HA_L1_L0 | 3 h | life / grade manufacturing |
| HA_L0_Lm1 | 3 h | grade / basement process |
| HA_Lm1_Lm2 | 2 h | basement / hydro + catch (same dirty-side family; catch is *clean* water — keep the tank room dry) |
| SHAFT_H2 | 2 h | HDR_H2 only, top vent, no connection to hab air |
| SHAFT_ACID | 2 h | HDR_ACID_GAS to roof stack |
| SHAFT_OIL | 2 h | AFTERBURNER flue |
| SHAFT_PENSTOCK | 2 h | clean water only. Not a process drain. |
| SHAFT_EGRESS / STAIR_P | 2 h | hab primary stair, L2–L0. No door onto L-1 |
| STAIR_MAINT | 2 h | operator L0–L-2. Not a hab exit |
| STAIR_SERVICE | 2 h | L0–L-2 service + basement secondary egress; north face; not hab sleeping exit |
| STAIR_S1 / STAIR_S2 | 2 h | perimeter secondary, L1–L0 |
| ELEV_SVC | 2 h | freight. L-2, L0, L1, L2. L-1 only via rated lobby |
| SHAFT_UTIL | 2 h | HDR_UPW, HDR_GREY, Q4 water, power, comms |
| DRAIN_SEC | exterior | roof / tank overflow / hab secondary. Not Salria |
| FB_HAB_CORE | 3 h | HAB ↔ CORE_PROCESS / recycle (CORE enclosure + centreline through CORE Y-band; T=300 mm massing) |
| FB_HAB_FARM | 2 h | HAB ↔ FARM party wall outside CORE Y-band (T=200 mm massing) |
| CORE_LIFE | zone | STAIR_P + ELEV_SVC + SHAFT_UTIL + SHAFT_PENSTOCK |
| CORE_PROCESS | zone | SHAFT_H2 + SHAFT_ACID + SHAFT_OIL + HDR_DUST riser |

CORE_LIFE and CORE_PROCESS share a central 6 × 6 m bay *as a zone*.
They are separate 2 h rooms. People, H2, and flue never share a
sleeve. No process-atmosphere duct in STAIR_P, ELEV_SVC, SHAFT_UTIL,
or SHAFT_PENSTOCK. Hab sleeping egress lands at grade without walking
the basement.

---

## 2.1 Central column (CORE)

One structural bay on the plate centreline, split on the short axis.

```
        N (dock / SERVICE_ENTRY)   ← pole-facing; site +Y
   +---------+---------+
   | CORE_   | CORE_   |
 W | LIFE    | PROCESS | E
   | stair P | H2      |
   | elev    | acid    |
   | util    | oil     |
   | penstock| dust    |
   +---------+---------+
        S (equator terraces / farm-hab south apron)
```
Site north = **+Y** (AQS-SITE-001). Primary truck dock faces north at L0.

| Object | Size (m) | Serves | Forbidden |
|---|---|---|---|
| STAIR_P | 2.4 × 4.8 | L2 maint, L1, L0 | L-1 door, process gas |
| ELEV_SVC | 2.7 × 3.2 shaft | freight L-2 / L0 / L1 / L2 | opening raw into H-3 |
| SHAFT_UTIL | 1.2 × 2.4 | S01, S12, S21, Q4, 480 V, comms | HDR_H2, acid, oil |
| SHAFT_PENSTOCK | 0.8 × 0.8 | S22 / S23 | process sump |
| SHAFT_H2 | 0.8 × 0.8 | S24, no traps, top vent | hab air, elevator |
| SHAFT_ACID | 0.8 × 0.8 | HDR_ACID_GAS to stack | life core |
| SHAFT_OIL | 0.8 × 0.8 | AFTERBURNER flue | life core |
| STAIR_MAINT | 1.2 × 2.4 | L0–L-2 operators | hab discharge |
| SERVICE_ENTRY | 3.6 × 2.4 | L0 north vestibule (dock strip) | hab sleeping path |
| STAIR_SERVICE | 2.4 × 3.6 | L0–L-2 service + L-1/L-2 egress doors | hab sleeping path; process duct |

Elevator is warranted on M1: metals crib, farm totes, tank
maintenance, not passenger traffic. Cab ~2 000 kg freight.

---

## 2.2 Perimeter

Opposite corners, clear of the **north** dock door and SERVICE_ENTRY.

| Object | Location | Duty |
|---|---|---|
| STAIR_S1 | NW corner | L1 hab + L0 secondary exit |
| STAIR_S2 | SE corner | L1 farm + L0 secondary exit |
| DRAIN_SEC_NW/NE/SW/SE | four corners | roof gutter, tank overflow, hab secondary |
| ARRAY_E / S / W / N | facades | BIPV + solar thermal (see §8) |

DRAIN_SEC leaders are exterior. They do not enter CORE_PROCESS.
Tank overflow is clean water → CATCH TANK or HDR_GREY, never L-1 bund.
Process bund stays on L-1 / L-2 and returns to CSTR 1.

---

## 3. Hydro is a side effect, not the plant battery

Energy in a water column: \(E = \rho V g h\).

| Roof volume | Head | Stored energy (ideal) | Round-trip ~70% |
|---|---|---|---|
| 200 m³ | 18 m | 9.8 kWh | ~7 kWh |
| 1 000 m³ | 18 m | 49 kWh | ~34 kWh |
| 5 000 m³ (city cistern) | 25 m | 340 kWh | ~240 kWh |

The 120 kWh ZnBr2 pack remains the electrical battery. The roof
tank is first a **water tower** (hab, farm, FAB UPW feed) and a
**fire reserve**. Pumped hydro is enabled once \(V \times h\) is
worth a turbine — city and some desert cisterns, not the first
module, not the Moon (energy scales with \(g\)).

Loop water is **clean tower water only**. It never mixes with
Salria, grey, or etch. Makeup is S01 / condensate. CATCH TANK is
the lower reservoir, not a process sump.

---

## 4. Module scaling

Full rules: `cad/SCALE_MODEL.md` (AQS-SCALE-001). Drivers:
`SCALE_M` (1 = 24 × 18 m) or `MODULE_BAYS_X` / `MODULE_BAYS_Y`.

**Not everything scales the same way.**

| Kind | What | Rule |
|---|---|---|
| Continuous | ROOF_TANK (top), CATCH_TANK (deepest) | footprint / volume ∝ plan area |
| Discrete L0 horizontal | MFG_SHOP, WAFER_FAB, **dock+ELEV_DOCK pairs** | unlock at cassette thresholds; always grade |
| Discrete life floors | HABITATION ∥ FARM | stacked plates between roof and L0 |
| Discrete basement depth | wet line + CRYO | always underground; add basement plates |
| Electrical discrete | PV, ZnBr2, rectifiers | module counts from need × overprod |
| Overflow stubs | garden terraces | equator-facing + E/W wrap |

Vertical order is locked: roof tank → life floors → L0 MFG → process
basements → catch tank. Life and basement growth are discrete floors,
not continuous height stretch. See `SCALE_MODEL.md` Rev B.

| Cassette | `MODULE_BAYS_X` | Wet feed | Basement length | Roof tank (min) |
|---|---|---|---|---|
| M1 | 4–5 | 150 kg/d | 24–30 m | 200 m³ |
| M2 | 6–7 | 300 kg/d | 36–42 m | 350 m³ |
| M3 | ≥ 8 | 500 kg/d | ≥ 48 m | 500 m³ |

Electrical yard and ZnBr2 grow west of the **north** dock (Y-aligned to DOCK_Y), not under the tank. GEN/FC east faces stay west of `ENV_WALL_W` (`YARD_WALL_CLEAR`). See AQS-SITE-001.
Surplus PV → charge batteries → pump roof tank → controlled overflow
to grade `OVERFLOW_TERRACE_*` when tank and batteries are full. Life
balconies are `TERRACE_{S,E,W}_L*` with `TERRACE_DOOR_*` (not roof-only beds).

**Dock discrete jump:** `DOCK_COUNT = CASSETTE_COUNT`. Baseline M1 = **one**
`DOCK` + associated `ELEV_DOCK`. As the plate grows E–W (M2/M3 cassette
unlock), add dock+elevator pairs along +X (`DOCK_2` / `ELEV_DOCK_2`, …).
CORE `ELEV_SVC` remains the central freight shaft — not a dock substitute.

---

## 5. Site variants (same stack, different envelope)

| Variant | Changes | Do not change |
|---|---|---|
| City | larger ROOF TANK / CATCH (hydro becomes real); truck dock to street; tighter lot | headers, fire ratings |
| High desert | tank as diurnal thermal mass; more PV; evaporative loss cover; dust on HDR_DUST | Salria walls |
| Antarctica | tank *inside* insulated penthouse; no exterior hydrant dead-leg; heat first | hab over process |
| Moon | tank as radiation shield + thermal; hydro energy × 1/6; no air stacks — vacuum process vents to recovery; no NFPA 13 | closed mass loops |

Moon and Antarctica still keep dirty processes below clean water.
They drop Earth fire-code hours only when a habitat standard
replaces IBC; they do not mix headers.

---

## 6. First-cut masses (M1)

| Block | L × W × H (m) | Level | mm origin on that plate |
|---|---|---|---|
| LEACH + EW aisle | 12 × 8 × 4.5 | L-1 | 0, 4 |
| BMED / CRU / precip | 8 × 6 × 3.5 | L-1 | 12, 4 |
| OIL + GLASS | 10 × 6 × 4.5 | L-1 | 0, 12 |
| Scrubbers / stacks base | 6 × 6 × 5 | L-1 | 18, 12 |
| CATCH TANK | 12 × 8 × 4 | L-2 | 0, 4 |
| Hydro set | 6 × 6 × 3.5 | L-2 | 12, 4 |
| Dock + receiving (× DOCK_COUNT) | 12 × 8 × slab | L0 | 0, 10 (north); **ELEV_DOCK** paired inside each bay |
| MFG SHOP | 12 × 8 × 5 | L0 | 12, 0 |
| WAFER FAB bay | 12 × 10 × 4 | L0 | 12, 8 |
| CRYO | 9 × 6 × 4 | L-1 | 15, 6 |
| HABITATION | 12 × 18 × 3.2 | L1 | 0, 0 |
| FARM | 12 × 18 × 4.5 | L1 | 12, 0 |
| ROOF TANK | 16 × 12 × 7 | L2 | 4, 3 |
| CORE_LIFE + CORE_PROCESS | 6 × 6 × full height | all | 9, 6 |
| ARRAY_ROOF | 24 × 18 projected | above tank | tilt = **+φ** about +X (equator / south face NH) |
| TERRACE_{S,E,W}_L1 | 3 m depth bands | each life FFL | door from floor; top floor first, step down |
| ELEV_DOCK | 2.7 × 3.2 shaft | L-2…L2 | paired with each DOCK; ≠ CORE ELEV_SVC |

Plate 24 × 18 m (SCALE_M=1 bay grid unchanged). CRYO is on L-1 east of
CORE (origin 15, 6; envelope 9 × 6 m — Rev E layout relief using free
east strip to plate edge). ZnBr2 remains outdoor at grade west of the
dock. Wet cassette XY nudge: `PROCESS_DX` / `PROCESS_DY` in
`freecad/params.py` keep the line inside SLAB_Lm1.

**Rev E layout relief tradeoffs (AQS-AUD-001 Rev D):**

| Change | Gain | Cost |
|---|---|---|
| CRYO 6×6 → 9×6 m | +18 m² cold-box keep-out | Touches scrub Y=12 band; still one basement |
| FAB W 8→10 m; MFG W 10→8 m | FAB +24 m² for CZ→tool staging | MFG depth tighter for dual polymer+metal |
| SCALE_M / bay counts | Unchanged (4×3) | Further relief = M2 cassette or BASEMENT_LEVELS |

---

## 7. Site orientation and access (AQS-SITE-001)

| Item | Lock |
|---|---|
| Site north | **+Y** (pole-facing, northern hemisphere) |
| Primary dock | North edge of plate, L0; doors face +Y |
| SERVICE_ENTRY / STAIR_SERVICE | North face, west strip; L0↔L-2; basement secondary egress |
| Hab egress | STAIR_P + STAIR_S1/S2 only — no L-1 door on STAIR_P; never through H |
| STAIR_MAINT | Operators only — not credited as public egress |

Egress study: AQS-EGR-001 (design target = most restrictive among NFPA 101/2/55, IBC/IFC, relevant ISO — controlling code per dimension). CRYO dedicated egress: `CRYO_EGRESS_DOOR` / `CRYO_EGRESS_LOBBY` stubs.

---

## 8. Envelope arrays

Roof above the tank is a tilted canopy, not a flat lid on the water.
Air gap ≥ 800 mm for tank vents, H2 stack, and walking. Canopy tilt
equals **+φ** (positive rotation about +X) so the **north (+Y) edge
rises** and the array faces the **equator / south** in the northern
hemisphere — **not** north/dock. Yard `PV_ARRAY*` use the same sign.
Seasonal ±15° is a later tracker option, not M1.

| Site | φ | ARRAY_ROOF tilt | Facade note |
|---|---|---|---|
| City / Dallas default | 32.8° N | 33° S | S/E/W BIPV + thermal; N low yield |
| High desert ~35° N | 35° N | 35° S | dust shedding; cover tank |
| Antarctica | ~75–90° S | near-vertical, north | winter sun on the horizon; heat first |
| Moon | landing lat | no atmosphere; point at sun or park | dust; no air-cooled inverters on-skin |

Facades: PV and thermal line the *outside* of L0–L2 and the canopy.
Thermal loop is Q4 water (hab/farm), not Q1 flue. Inverters and
disconnects stay in POWER YARD, not in CORE_PROCESS.

Do not hang array structure from the tank wall. Tank is a vessel.
Canopy is a separate frame to the core and perimeter columns.

---

## 9. Sheets

| File | Doc | Level |
|---|---|---|
| `building_section_pfd.png` | AQS-PFD-BLD-001 | vertical section |
| `basement_pfd.png` | AQS-PFD-BLD-002 | L-2 + L-1 |
| `ground_floor_pfd.png` | AQS-PFD-BLD-003 | L0 |
| `life_floor_pfd.png` | AQS-PFD-BLD-004 | L1 |
| `roof_water_pfd.png` | AQS-PFD-BLD-005 | L2 + hydro loop |
| `core_plan_pfd.png` | AQS-PFD-BLD-006 | CORE_LIFE / CORE_PROCESS + perimeter |

Site access: `cad/SITE_ACCESS.md` (AQS-SITE-001).
Rebuild PFDs: `python3 pfd_scripts/building_stack_pfds.py`
(reads live `cad/freecad/params.py`; do not change SCALE_M in that pass).
Campus / hazard / life sheets: `python3 pfd_scripts/campus_life_hazard_pfds.py`.
Rebuild plant (baseline `SCALE_M=1`): `/usr/bin/freecadcmd cad/freecad/build_plant.py`.
For `SCALE_M=2` see `cad/SCALE_MODEL.md` §7.
