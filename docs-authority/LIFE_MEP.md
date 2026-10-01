# Life MEP — Phase D (duct / fixture / one-line study)

Document number: AQS-MEP-001  
Revision: A  
Date: 2026-10-01  
Authority: AQS-LIFE-001, AQS-EQP-HAB-001, AQS-WTR-001, AQS-NZ-002,
AQS-ELC-001 (`ELECTRICAL.md`), `params.py` life-header diameters,
AQS-EGR-001 (egress illumination hook).  
Companion bump: AQS-LIFE-001 Rev B §9 Phase D → **Partial**.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Phase D study: fixture counts, duct OD from headers, one-line | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001. **Not a PE stamp.**
No invented vendor kW.

---

## 1. Purpose

Extend life fit-out from Phase C (written plan) to Phase D **as far as
evidence allows**: fixture counts from the 4-crew AUD study, duct /
pipe OD from locked life-header params, and a one-line MEP schematic.
Shop furniture (Phase E) remains open.

## 2. Basis headcount

| Source | Value | Use |
|---|---|---|
| AQS-AUD-001 | **4 persons** pilot placeholder | Fixture & water study |
| AQS-EGR-001 | Design load HAB **12** occ (area method) | Egress / exit signs — not fixture plumbing |

Issued berth count remains **TBD**. Fixture counts below track the
**4-crew** ops study; upsize note if berths exceed 4.

---

## 3. Plumbing fixtures (study)

| Fixture | Qty (4-crew) | Location | Branch | Notes |
|---|---|---|---|---|
| Water closet | 2 | WETROOM_HAB_NW | Black → HAB_WASTE | Accessible clearances AQS-LIFE-001 §2 |
| Lavatory | 2 | WETROOM_HAB_NW | Grey | |
| Shower | 2 | WETROOM_HAB_NW | Grey | |
| Kitchen sink | 1 | GALLEY | Grey + grease capture | No open flame near farm door |
| Laundry / utility sink | 1 | HAB service strip | Grey | Optional |
| Hose bib / mop | 1 | CORR_L1_HAB | Grey | |
| Drinking / potable tap | 2 | GALLEY + SLEEP | Potable S26 / HAB_UV | ≥ 40 mJ/cm² UV class |
| Floor drains | 3 | Wetroom ×2 + galley | Grey only | No process bund tie |
| Farm hose / rinse | 2 | FARM service | Grey → FARM_SUMP / HDR_GREY | Not CATCH |
| L0 accessible toilet | 1 | TOILET_L0_* | Grey/black | AQS-LIFE-001 §7 |
| L-1 maint WC | 1 | TOILET_Lm1_MAINT | Grey/black | Near STAIR_MAINT |

Hot water: Q4-coupled or electric point-of-use — **kW TBD** (no invent).

---

## 4. Duct / pipe sizes from locked headers

Life-rack OD from `params.py` (mm) — use as **main** sizes; branches step
down one trade size unless noted:

| Service | Param | OD (mm) | Serves |
|---|---|---|---|
| Grey | LIFE_D_GREY | **50** | Wetroom / galley / farm rinse → HDR_GREY |
| UPW / potable feed | LIFE_D_UPW | **40** | HAB_WATER / farm makeup |
| Etch (fab only — not HAB) | LIFE_D_ETCH | **32** | Listed for rack completeness; **forbidden in HAB/FARM** |
| O₂ | LIFE_D_GAS | **25** | HDR_O2 → HAB_AIR / farm |
| N₂ | LIFE_D_GAS | **25** | HDR_N2 purge (fab / utility) |
| CO₂ | LIFE_D_CO2 | **40** | HAB_AIR → HDR_CO2 → farm |

### 4.1 HVAC duct study (schematic)

No vendor airflow curves. Study velocities 5–8 m/s mains:

| System | Serves | Study supply duct | Medium | Forbidden |
|---|---|---|---|---|
| HAB AHU / ERV | SLEEP, GALLEY, wetroom | **400 × 250 mm** rectangular or Ø350 equiv. | Q4 + OA | Process atmosphere; Q1 flue |
| FARM AHU | Grow / fish | **500 × 300 mm** or Ø400 | Q4 + CO₂ dose | Acid gas; oil vapor |
| Toilet exhaust | Wetroom | Ø150 | Dedicated exhaust | Tee into STAIR_P |
| Elevator lobby relief | LOBBY_ELEV_L1 | Ø200 | Smoke/pressure study | Process duct |

Fire dampers at FB_HAB_FARM / HA_L1_L0 crossings (AQS-LIFE-001 §4).

AHU cooling/heating capacity: **TBD kW** (Q4 duties not nameplated).

---

## 5. Electrical one-line (life floor)

```
Sol-Ark / module bus (AQS-ELC-001)
        │
        ├─ Life panel LP-L1 (study 120/240 V or 208Y — site TBD)
        │     ├─ HAB AHU / ERV          kW TBD
        │     ├─ FARM AHU + LED canopy  kW TBD (S20 DC preferred for LED)
        │     ├─ HAB_WATER boost / UV   kW TBD
        │     ├─ Wetroom / galley receptacles
        │     ├─ SLEEP receptacles / lighting
        │     ├─ Emergency lighting / exit signs (NEC 700)  ← AQS-EGR-001
        │     └─ ELEV_SVC feeder (freight) — separate MCC preference
        │
        └─ Not on life panel: rectifiers, MET_MELT, pyro, Sol-Ark GEN/FC
```

LED grow on **S20 DC bus** per farm docs when available; do not invent
PPFD → kW.

---

## 6. One-line MEP schematic (textual)

```
ROOF_TANK ──SHAFT_UTIL── HDR_UPW ──► HAB_WATER ──UV── taps
                              └──► FARM makeup / FISH_TANK F3
HAB wetroom/galley grey ──► HAB_WASTE / GREY_* ──► treat ──► S29/S30 / farm
Black ──► BLACK_* digest ──► nutrient / HDR_ORG
Q4 water ──► HAB AHU / FARM AHU / FC_HX / MET_HX (no HAB return of process air)
CRYO ── HDR_O2 / HDR_N2 / HDR_CO2 ── life rack tiers (LIFE_Z_*)
```

---

## 7. Phase status

| Phase | Deliverable | Status |
|---|---|---|
| A–C | Envelopes, stubs, written plan | Done (AQS-LIFE-001) |
| **D** | Duct / fixture / one-line | **This doc — Partial** |
| E | Shop interiors / furniture | Open |

Remaining Phase D gaps: vendor AHU curves, berth-count lock, emergency
lighting fixture schedule, hot-water kW.

---

## 8. Sync

Canonical: `Diagrams/aqueous_diagrams/cad/LIFE_MEP.md`  
Share: `share/aqueous-solutions/docs-authority/LIFE_MEP.md`
