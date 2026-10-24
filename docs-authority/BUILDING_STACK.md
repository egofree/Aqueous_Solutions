# Building stack: the vertical campus

Document number: AQS-BLD-001  
Revision: G  
Date: 2026-10-24  
Basis: AQS-AUTH-001 (this document is the active CAD authority for levels, cores, shafts and stacked masses). Compliance themes: AQS-COMPL-001. Style: AQS-DOC-002.  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A–D | — | Prior stack issues (see git-less changelog in Rem-BLD) | 2026-09-27 |
| E | 1 | FAB/CRY layout relief (AQS-AUD-001 Rev D) | 2026-10-01 |
| F | 1 | Layout locks: equator PV tilt; life-floor terraces+doors; dock+ELEV_DOCK discrete E–W jump; yard inset (no wall punch) | 2026-10-01 |
| G | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, terms, captions and references; values unchanged | 2026-10-24 |

## 1. Purpose and scope

The plant is one structural module of stacked floors. This document fixes the levels, the fire-rated cores and shafts, and the first-cut masses that the FreeCAD model `plant.FCStd` and the building process flow diagrams (PFDs) are built from. The chemistry and the locked unit names do not change here.

In scope: level datums, fire cores, massing allowances for the dock and service entry, and the footprints of the wafer fab, cryogenic and manufacturing cassettes at `SCALE_M = 1.0`.

Out of scope: chemistry; using the flat Z = 0 origins of `PHASE_F_ENVELOPES.md` as placement authority; the narrative chapters at the repository root.

`PHASE_F_ENVELOPES.md` still supplies the keep-out sizes and utility lists of the equipment inside these floors. This document places those boxes on levels. Where the two disagree, this document controls the CAD envelope (`docs-authority/AUTHORITY.md`).

## 2. Terms

Level: a floor of the stack, named L-2 (sub-basement) to L2 (roof). World Z = 0 is the finished-floor level (FFL) of L0 at grade.

Plate: the floor area of one module, set by the structural bay grid.

Cassette: a group of process equipment sized for a given throughput (M1, M2, M3) and placed as one block.

Core: the central structural bay holding the fire-rated stairs, lift and shafts. `CORE_LIFE` serves people and clean utilities; `CORE_PROCESS` carries process gases and flues.

Horizontal assembly: a fire-rated floor and ceiling between two levels, named `HA_<upper>_<lower>`.

Occupancy groups (IBC 2024 chapter 3): R-2 residential, F-1 and F-2 factory, S-1 and S-2 storage, H-2 to H-5 high hazard, U utility. MAQ is the maximum allowable quantity of a hazardous material per control area; above it a space becomes an H occupancy. NS means non-sprinklered and NP means not permitted.

Unit names in capitals (for example `HDR_H2`, `CRYO`) are plant graph ids; stream numbers such as S24 refer to the stream register. Other abbreviations are defined in `docs-authority/GLOSSARY.md`.

## 3. Why the plant is stacked this way

The order of the floors lets gravity do work that should not depend on pumps.

- Dirty liquor cannot drain uphill into the habitation or farm floors.
- Clean water is stored above the points of use. The ultrapure water header `HDR_UPW` and the habitation and farm taps are fed by gravity first and by pump second.
- Solids arrive at grade and drop into the hopper and LEACH CSTR 1.
- Hydrogen is lighter than air. It is generated in the basement, at the electrowinning cathodes, but does not collect there: `HDR_H2` is a vertical riser with no traps to the roof vent, CRYO or fuel use. The zinc-bromide (ZnBr2) storage skid stays outdoors at grade (NFPA 855). CRYO is on L-1, east of the core, in a 2 h rated room with its own ventilation to NFPA 2 and NFPA 55. It is not a shared process pit, and no process-air duct passes through its fire barrier `FB_CRYO_PROCESS`.

The building is sprinklered throughout (NFPA 13). Table 3.1 gives the fire-resistance ratings that IBC 2024 Table 508.4 requires between a residential floor and the floors below it.

Table 3.1. Required separation between residential and other occupancies (IBC 2024 Table 508.4, sprinklered)

| Pair | Horizontal assembly |
|---|---|
| R over H-3 / H-4 | 2 h (NS = not permitted) |
| R over H-2 | 3 h (NS = NP) |
| R over F-1 / S-1 | 1 h |
| R over H-5 | 2 h (NS = NP) |

The plant standard is stricter than the H-3 requirement: a 3 h assembly between the habitation floor and the recycling basement, matching AQS-HSE-001. A residential floor over an H occupancy without sprinklers is not permitted.

## 4. Levels

The structural bay is 6.0 × 6.0 m. The module plate is 24 × 24 m (4 × 4 bays), or 576 m². The earlier 24 × 18 m plate of 432 m² is retired (AQS-PLAN-001 Rev B). Clear heights are measured to the underside of the slab above. Table 4.1 lists the levels.

Table 4.1. Levels of one module

| Level | Name | Clear | Occupancy | Holds |
|---|---|---|---|---|
| L-2 | SUB-BASEMENT | 4.5 m | F-1 / utility | CATCH TANK, hydro turbine-pump, process sumps |
| L-1 | BASEMENT | 6.0 m | F-1 + H-3 if MAQ | LEACH, EW, BMED, CRU, OIL, GLASS, scrubbers, CRYO (rated room) |
| L0 | GRADE | 6.0 m | F-1 / S-1 / H-5 pocket | Dock, MFG SHOP, WAFER FAB bay, POWER (ZnBr2 outdoor) |
| L1 | LIFE | 4.8 m | R-2 + F-2 | HABITATION, FARM (2 h between them) |
| L2 | ROOF | tank 6–8 m | S-2 water / U | ROOF TANK, PV, stacks, H2 vent |

The zinc-bromide skid, the truck apron and, at desert sites, the PV field are outdoors and not stacked.

The gross height from grade to the top of the tank is about 6 + 4.8 + 7 ≈ 18 m, with the basement 10.5 m below grade. The hydraulic head from the roof waterline to the catch-tank waterline is about 16 to 20 m.

## 5. Fire separations and shafts

Table 5.1 gives the rating of each horizontal assembly, shaft, stair and fire barrier.

Table 5.1. Fire separations and shafts

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

`CORE_LIFE` and `CORE_PROCESS` share one central 6 × 6 m bay as a zone, but they are separate 2 h rooms. People, hydrogen and flue gas never share a shaft. No duct carrying process atmosphere runs in `STAIR_P`, `ELEV_SVC`, `SHAFT_UTIL` or `SHAFT_PENSTOCK`. The escape route from the habitation sleeping areas reaches grade without passing through the basement.

### 5.1 Central core

The core is one structural bay on the centreline of the plate, split along its short axis (Figure 5.1). Site north is +Y (AQS-SITE-001), and the main truck dock faces north at L0.

Figure 5.1. Plan of the central core

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

Table 5.2 sizes the objects in the core and states what each may not carry.

Table 5.2. Core objects

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

A lift is justified at M1 for the metals crib, farm totes and tank maintenance rather than for passengers. The freight cab is about 2 000 kg.

### 5.2 Perimeter

The perimeter stairs are at opposite corners, clear of the north dock door and the service entry (Table 5.3).

Table 5.3. Perimeter objects

| Object | Location | Duty |
|---|---|---|
| STAIR_S1 | North-west corner | L1 hab + L0 secondary exit |
| STAIR_S2 | South-east corner | L1 farm + L0 secondary exit |
| DRAIN_SEC_NW/NE/SW/SE | four corners | roof gutter, tank overflow, hab secondary |
| ARRAY_E / S / W / N | facades | BIPV + solar thermal (see §8) |

The secondary drain (`DRAIN_SEC`) leaders are outside the building and do not enter `CORE_PROCESS`. Tank overflow is clean water and goes to the catch tank or `HDR_GREY`, never to the L-1 bund. The process bund stays on L-1 and L-2 and returns to CSTR 1.

## 6. Pumped hydro is a side effect, not the plant battery

The energy stored in a raised column of water is E = ρVgh, where ρ is the water density, V the volume, g the gravitational acceleration and h the head. Table 6.1 shows that a roof tank stores little energy.

Table 6.1. Ideal energy stored in the roof tank

| Roof volume | Head | Stored energy (ideal) | Round-trip ~70% |
|---|---|---|---|
| 2,707 m³ | 35.73 m | 263.6 kWh | 210.9 kWh (superseded by AQS-BLD-014, Q-009) |
| 1 000 m³ | 18 m | 49 kWh | ~34 kWh |
| 5 000 m³ (city cistern) | 25 m | 340 kWh | ~240 kWh |

The 120 kWh zinc-bromide pack remains the electrical battery. The roof tank is first a water tower (for the habitation, the farm and the ultrapure water feed to the wafer fab) and a fire reserve. Pumped hydro is worth a turbine only when V × h is large, as in city cisterns and some desert cisterns. It is not worth it for the first module, nor on the Moon, because stored energy scales with g.

The hydro loop uses clean tower water only and never mixes with Salria, grey water or etchant. Makeup comes from S01 and condensate. The catch tank is the lower reservoir, not a process sump.

## 7. Scaling the module

The full rules are in `docs-authority/SCALE_MODEL.md` (AQS-SCALE-001). Scale is set by `SCALE_M` (1 = 24 × 18 m) or by `MODULE_BAYS_X` and `MODULE_BAYS_Y`. Different parts of the plant scale in different ways (Table 7.1).

Table 7.1. How each kind of element scales

| Kind | What | Rule |
|---|---|---|
| Continuous | ROOF_TANK (top), CATCH_TANK (deepest) | footprint / volume ∝ plan area |
| Discrete L0 horizontal | MFG_SHOP, WAFER_FAB, **dock+ELEV_DOCK pairs** | unlock at cassette thresholds; always grade |
| Discrete life floors | HABITATION ∥ FARM | stacked plates between roof and L0 |
| Discrete basement depth | wet line + CRYO | always underground; add basement plates |
| Electrical discrete | PV, ZnBr2, rectifiers | module counts from need × overprod |
| Overflow stubs | garden terraces | equator-facing + E/W wrap |

The vertical order is fixed: roof tank, life floors, L0 manufacturing, process basements, catch tank. The life floors and basements grow by whole floors, not by stretching height (`SCALE_MODEL.md` Rev B). Table 7.2 gives the cassette sizes.

Table 7.2. Cassette sizes

| Cassette | `MODULE_BAYS_X` | Wet feed | Basement length | Roof tank (min) |
|---|---|---|---|---|
| M1 | 4–5 | 150 kg/d | 24–30 m | 200 m³ |
| M2 | 6–7 | 300 kg/d | 36–42 m | 350 m³ |
| M3 | ≥ 8 | 500 kg/d | ≥ 48 m | 500 m³ |

The electrical yard and the zinc-bromide storage grow west of the north dock, aligned in Y with `DOCK_Y`, not under the tank. The east faces of the generator and fuel cell stay west of `ENV_WALL_W` (`YARD_WALL_CLEAR`); see AQS-SITE-001.

Surplus PV power charges the batteries, then pumps water to the roof tank. When the tank and batteries are both full, the tank overflows in a controlled way to the grade terraces `OVERFLOW_TERRACE_*`. The life floors have balconies `TERRACE_{S,E,W}_L*` with doors `TERRACE_DOOR_*`; planting is not limited to the roof.

Docks are added in steps: `DOCK_COUNT = CASSETTE_COUNT`. The M1 baseline has one `DOCK` with its `ELEV_DOCK`. As the plate grows east–west with the M2 and M3 cassettes, dock and lift pairs are added along +X (`DOCK_2` and `ELEV_DOCK_2`, and so on). The core lift `ELEV_SVC` remains the central freight shaft and does not replace a dock lift.

## 8. Site variants

The same stack is used at every site; the envelope changes (Table 8.1).

Table 8.1. Site variants

| Variant | Changes | Do not change |
|---|---|---|
| City | larger ROOF TANK / CATCH (hydro becomes real); truck dock to street; tighter lot | headers, fire ratings |
| High desert | tank as diurnal thermal mass; more PV; evaporative loss cover; dust on HDR_DUST | Salria walls |
| Antarctica | tank *inside* insulated penthouse; no exterior hydrant dead-leg; heat first | hab over process |
| Moon | tank as radiation shield + thermal; hydro energy × 1/6; no air stacks — vacuum process vents to recovery; no NFPA 13 | closed mass loops |

At the Moon and Antarctic sites the dirty processes still sit below clean water. Those sites drop the fire-resistance hours of Earth codes only when a habitat standard replaces the IBC, and they never mix headers.

## 9. First-cut masses at M1

Table 9.1 gives the keep-out masses for the M1 plant. Origins are in metres on the plate of the stated level.

Table 9.1. First-cut masses (M1)

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
| ARRAY_ROOF | 24 × 18 projected | above tank | tilt = **+φ** about +X (equator, the south face in the northern hemisphere) |
| TERRACE_{S,E,W}_L1 | 3 m depth bands | each life FFL | door from floor; top floor first, step down |
| ELEV_DOCK | 2.7 × 3.2 shaft | L-2…L2 | paired with each DOCK; ≠ CORE ELEV_SVC |

The plate is 24 × 18 m with the `SCALE_M = 1` bay grid unchanged. CRYO is on L-1 east of the core (origin 15, 6; envelope 9 × 6 m), using the free east strip to the plate edge (Rev E). The zinc-bromide storage stays outdoors at grade, west of the dock. The offsets `PROCESS_DX` and `PROCESS_DY` in `freecad/params.py` keep the wet cassette inside `SLAB_Lm1`.

Table 9.2 records the trade-offs of the Rev E layout change (AQS-AUD-001 Rev D).

Table 9.2. Rev E layout trade-offs

| Change | Gain | Cost |
|---|---|---|
| CRYO 6×6 → 9×6 m | +18 m² cold-box keep-out | Touches scrub Y=12 band; still one basement |
| FAB W 8→10 m; MFG W 10→8 m | FAB +24 m² for CZ→tool staging | MFG depth tighter for dual polymer+metal |
| SCALE_M / bay counts | Unchanged (4×3) | Further relief = M2 cassette or BASEMENT_LEVELS |

## 10. Site orientation and access

Table 10.1 summarises the orientation and access rules of AQS-SITE-001.

Table 10.1. Orientation and access

| Item | Lock |
|---|---|
| Site north | **+Y** (pole-facing, northern hemisphere) |
| Primary dock | North edge of plate, L0; doors face +Y |
| SERVICE_ENTRY / STAIR_SERVICE | North face, west strip; L0↔L-2; basement secondary egress |
| Hab egress | STAIR_P + STAIR_S1/S2 only — no L-1 door on STAIR_P; never through H |
| STAIR_MAINT | Operators only — not credited as public egress |

The egress study is AQS-EGR-001. Its design target is the most restrictive of NFPA 101, NFPA 2, NFPA 55, the IBC and IFC and the relevant ISO standards, with the controlling code identified for each dimension. CRYO has its own egress, modelled as the stubs `CRYO_EGRESS_DOOR` and `CRYO_EGRESS_LOBBY`.

## 11. Solar arrays on the envelope

The roof above the tank is a tilted canopy, not a flat lid on the water. An air gap of at least 800 mm is left for the tank vents, the hydrogen stack and walking access. The canopy tilt equals +φ, the site latitude, as a positive rotation about +X: the north (+Y) edge rises and the array faces the equator (south in the northern hemisphere), not the north dock. The yard arrays `PV_ARRAY*` use the same sign. A seasonal ±15° adjustment is a later tracker option, not part of M1. Table 11.1 gives the tilt by site.

Table 11.1. Array tilt by site

| Site | φ | ARRAY_ROOF tilt | Facade note |
|---|---|---|---|
| City / Dallas default | 32.8° N | 33° S | S/E/W BIPV + thermal; N low yield |
| High desert ~35° N | 35° N | 35° S | dust shedding; cover tank |
| Antarctica | ~75–90° S | near-vertical, north | winter sun on the horizon; heat first |
| Moon | landing lat | no atmosphere; point at sun or park | dust; no air-cooled inverters on-skin |

Building-integrated PV (BIPV) and solar thermal panels line the outside of L0 to L2 and the canopy. The thermal loop is the Q4 water loop (habitation and farm), not the Q1 flue loop. Inverters and disconnects stay in the power yard, not in `CORE_PROCESS`.

The array structure must not hang from the tank wall, because the tank is a vessel. The canopy is a separate frame carried on the core and perimeter columns.

## 12. Drawings and rebuild

Table 12.1 lists the building process flow diagrams.

Table 12.1. Building sheets

| File | Doc | Level |
|---|---|---|
| `building_section_pfd.png` | AQS-PFD-BLD-001 | vertical section |
| `basement_pfd.png` | AQS-PFD-BLD-002 | L-2 + L-1 |
| `ground_floor_pfd.png` | AQS-PFD-BLD-003 | L0 |
| `life_floor_pfd.png` | AQS-PFD-BLD-004 | L1 |
| `roof_water_pfd.png` | AQS-PFD-BLD-005 | L2 + hydro loop |
| `core_plan_pfd.png` | AQS-PFD-BLD-006 | CORE_LIFE / CORE_PROCESS + perimeter |

Site access is covered by `docs-authority/SITE_ACCESS.md` (AQS-SITE-001).

- Rebuild the building PFDs with `python3 flow_graph/exporters/matplotlib/building_stack_pfds.py`. It reads the current `models/freecad/params.py`; do not change `SCALE_M` in that pass.
- Rebuild the campus, hazard and life sheets with `python3 flow_graph/exporters/matplotlib/campus_life_hazard_pfds.py`.
- Rebuild the plant at the baseline `SCALE_M=1` with `/usr/bin/freecadcmd models/freecad/build_plant.py`. For `SCALE_M=2` see `docs-authority/SCALE_MODEL.md` §7.

## 13. References

- International Code Council. International Building Code 2024, chapter 3 and Table 508.4.
- NFPA 13, Standard for the Installation of Sprinkler Systems.
- NFPA 2, Hydrogen Technologies Code; NFPA 55, Compressed Gases and Cryogenic Fluids Code.
- NFPA 101, Life Safety Code.
- NFPA 855, Standard for the Installation of Stationary Energy Storage Systems.
