# Habitation and farm fit-out plan

Document number: AQS-LIFE-001  
Revision: B
Date: 2026-10-01

Authority: AQS-BLD-001 Rev B (`BUILDING_STACK.md`), AQS-HSE-001
(`HAZARD_SEPARATION.md`), AQS-CMP-001 (`CAMPUS_PLAN.md`). This file
replaces empty placeholder notes for L1 life systems. Full MEP is
phased; CAD today carries corridor / wet-room / partition stubs
(`freecad/fitout.py`, `habitation.py`, `farm.py`).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Phase A–C fit-out plan | 2026-09-27 |
| B | 1 | Phase D → AQS-MEP-001 (Partial); STAIR_SERVICE note | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-002.

---

## 1. Occupancy and fire

| Block | Level | Occupancy | Barrier |
|---|---|---|---|
| HABITATION | L1 | R-2 analog | FB_HAB_FARM 2 h to FARM; HA_L1_L0 3 h to grade; no process air |
| FARM | L1 | F-2 / U accessory | same party wall; no HDR_ACID_GAS / HDR_H2 / HDR_OIL_VAPOR |
| CORE_LIFE | all | egress + util | STAIR_P, ELEV_SVC, SHAFT_UTIL, SHAFT_PENSTOCK — 2 h room |

Hab sleeping egress lands at L0 via STAIR_P / STAIR_S1 without walking
L-1. Process operators use STAIR_MAINT. No shared HVAC return between
HABITATION and the recycle aisle (AQS-HSE-001 §8).

---

## 2. Habitation rooms (L1 west plate)

Plate origin SW. HAB envelope 12 000 × 18 000 × 3 200 mm at Z_L1.

| Room / zone | CAD stub | Program |
|---|---|---|
| SLEEP | `SLEEP` | Crew berths; quiet side toward NW stair |
| GALLEY | `GALLEY` | Food prep; grease capture; no open flame near farm door |
| HAB_AIR | `HAB_AIR` | AHU / ERV on Q4 water only; CO₂ to HDR_CO2 |
| HAB_WATER | `HAB_WATER` | Potable from HDR_UPW / roof tank; point-of-use polish |
| HAB_WASTE | `HAB_WASTE` | Black / grey to HDR_GREY → treatment → farm or discharge permit |
| WETROOM_HAB_NW | `WETROOM_HAB_NW` | Toilet + shower bank; IBC accessible clearances |
| CORR_L1_HAB | `CORR_L1_HAB` | 1 800 mm spine to CORE_LIFE / STAIR_S1 |
| PART_HAB_SLEEP_GALLEY | partition stub | Acoustic / smoke partition |

Accessible route: clear width ≥ 915 mm on secondary routes; main spine
1 800 mm. Toilet room latch-side clear ≥ 1 525 mm. Elevator lobby
`LOBBY_ELEV_L1` ≥ 1 500 × 1 500 mm clear.

---

## 3. Farm rooms (L1 east plate)

FARM envelope 12 000 × 18 000 × 4 500 mm at Z_L1.

| Unit | CAD stub | Duty |
|---|---|---|
| FISH_TANK | `FISH_TANK` | Aquaculture; solids to digest / nutrient |
| BIOFILTER | `BIOFILTER` | Nitrification; no oxidizer storage |
| GROW_BED | `GROW_BED` | Hydroponic / media beds |
| LED_CANOPY | `LED_CANOPY` | DC LED; heat to Q4 |
| FARM_SUMP | `FARM_SUMP` | Nutrient sump; double-wall or drain to HDR_GREY only |
| NUTRIENT_DOSE | `NUTRIENT_DOSE` | Struvite / NH4 / chelates from STREAM_REGISTER |
| CORR_L1_FARM | corridor | Service aisle to CORE / STAIR_S2 |
| PART_FARM_SERVICE | partition | Separates grow volume from west service strip |

Farm air is separate from hab sleeping. CO₂ makeup from CRYO / HAB_AIR
(S04). O₂ from CRYO / grow (S02) may serve hab. No Salria, etch, or
process H₂ in farm headers.

---

## 4. HVAC

| System | Serves | Medium | Forbidden |
|---|---|---|---|
| HAB AHU / ERV | SLEEP, GALLEY, wet rooms | Q4 water + outdoor air | Q1 flue, process atmosphere |
| FARM AHU | grow / fish | Q4 + CO₂ dosing | acid gas, oil vapor |
| Process aisle AHU | L-1 wet line | dedicated; exhaust to scrubbers | tee into STAIR_P / ELEV_SVC / SHAFT_UTIL |
| CRYO room vent | L-1 CRYO | NFPA 2 / 55 mechanical; H₂ detection | shared return with hab or process aisle |

Fire dampers where ducts cross FB_* / HA_*. Energy recovery across a
fire area is listed damper + separate AHU or Q4-only recovery.

---

## 5. Water

| Stream | Source | Use | Return |
|---|---|---|---|
| Potable / UPW | ROOF TANK via SHAFT_UTIL / HDR_UPW | Hab taps, farm makeup, fab polish | Grey to HDR_GREY |
| Grey | Hab wet rooms, farm rinse | Treatment | Farm nutrient or permitted discharge |
| Black | Toilets | Digester / treatment | Solids to nutrient path per CAMPUS_PLAN |
| Fire reserve | ROOF TANK | NFPA 13 | Not process bund |
| Penstock | ROOF TANK → CATCH | Clean tower water only | Hydro set on L-2 |

Dirty liquor cannot drain uphill into HABITATION or FARM
(AQS-BLD-001 §3).

---

## 6. Waste

| Waste | Path |
|---|---|
| Human black / grey | HAB_WASTE → HDR_GREY → treatment |
| Farm plant waste / fish solids | FARM_SUMP / totes → nutrient or digest — not LEACH without AHJ review |
| Hab trash organics | May enter HOPPER only as documented feedstock; no FR-4 / batteries |
| Medical / hazardous | Out of plant; not to Salria |

Spill path on L-1 remains bund → CSTR 1 / CRU. Never to storm, farm, or
hab drains.

---

## 7. Circulation

| Element | Levels | Note |
|---|---|---|
| CORR_*_EW / NS | L-2 … L0 | Bay-grid spines south / west of CORE |
| CORR_Lm1_PROCESS | L-1 | Process to CORE; stops at FB_CRYO_PROCESS |
| CORR_Lm1_CRYO_APPROACH | L-1 | CRYO access; no process-air duct through wall |
| STAIR_P | L2–L0 | Hab primary; no L-1 door |
| STAIR_S1 / S2 | L1–L0 | Perimeter secondary |
| STAIR_MAINT | L0–L-2 | Operators only |
| ELEV_SVC + LOBBY_ELEV_* | L-2, L0, L1, L2 | Freight; L-1 via rated lobby only |
| TOILET_L0_* / TOILET_L1_* | L0, L1 | Accessible toilet rooms |
| TOILET_Lm1_MAINT | L-1 | Operator WC near STAIR_MAINT |

---

## 8. Farm systems (ops summary)

1. Fish metabolism → biofilter → grow beds; LED photoperiod on DC bus.
2. Nutrient makeup from P-Al / P-Mg / P-Ca cakes, struvite, BMED salts
   (CAMPUS_PLAN §1 rule 5) — not a second EW aisle.
3. Condensate and plant waste return per STREAM_REGISTER; etch never
   enters farm.
4. O₂ / CO₂ / N₂ from CRYO life headers only (HDR_O2 / HDR_CO2 / HDR_N2).

---

## 9. Phasing

| Phase | Deliverable | Status |
|---|---|---|
| A | Envelopes + cores + shafts | Done (AQS-BLD-001 CAD) |
| B | Corridor / toilet / lobby / partition stubs | This pass (`fitout.py`) |
| C | Written life fit-out plan | This file |
| D | Detailed MEP (duct sizes, fixture counts, one-line) | **Partial** — `docs-authority/LIFE_MEP.md` (AQS-MEP-001) |
| E | Shop interiors / furniture | Open |

---

## 10. Rebuild

```bash
cd models/freecad
/usr/bin/freecadcmd build_plant.py
```

Verify wet-line XY inside `SLAB_Lm1`, CRYO on L-1 at (18 000, 6 000),
`FB_CRYO_PROCESS` present, slabs/envelopes translucent.
