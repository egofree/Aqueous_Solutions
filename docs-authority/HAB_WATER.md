# Habitation water — equipment list

Document number: AQS-EQP-HAB-001  
Revision: B  
Date: 2026-09-27  
PFD: AQS-PFD-HAB-001 (`habitation_pfd.png`), AQS-PFD-HAB-WTR-001
(`hab_water_pfd.png`)

Authority: AQS-WTR-001, `07-water-air-habitation.md`,
`SLINGSHOT/Water_Cycle_diagram.md`, AQS-LIFE-001 §2/§5,
`freecad/habitation.py`, AQS-STR-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Stub list; purification design is next pass | 2026-09-27 |
| B | 1 | Schedule grey / black / VCD / ED / remin; align AQS-WTR-001 | 2026-09-27 |

## 1. Locked CAD units (habitation)

| Tag | Duty |
|---|---|
| SLEEP | Crew berths |
| GALLEY | Food prep; organics path |
| HAB_AIR | AHU / ERV; O₂ in, CO₂ out; Q4 only |
| HAB_WATER | Potable delivery; point-of-use UV / polish |
| HAB_WASTE | Grey / black collect → treatment |
| WETROOM_HAB_NW | Toilet + shower bank (fitout) |

## 2. Water purification units (AQS-WTR-001)

### 2.1 Grey

| Tag | Duty |
|---|---|
| GREY_SCREEN | Solids / grease from wetroom + galley |
| GREY_BIO | Biological BOD / FOG polish |
| GREY_MED | Membrane ED stage (root-07 MED duty) |
| GREY_BUFF | Buffer → S29 VCD feed or SALT FEED |

### 2.2 Black

| Tag | Duty |
|---|---|
| BLACK_COLLECT | Toilet collect; optional urine diversion |
| BLACK_DIGEST | Digester; solids → HDR_ORG / HOPPER |
| BLACK_MED | Liquor polish → S30 nutrient / salt |

### 2.3 VCD (SLINGSHOT kept)

| Tag | Duty |
|---|---|
| VCD_FEED | S13 condensate + S29 treated grey |
| VCD_HX | Counterflow heat recovery |
| VCD_EVAP | Evaporator; brine S28 |
| VCD_COMP | Vapor compressor |
| VCD_COND | Condenser; distillate S25 |

### 2.4 Polish / potable

| Tag | Duty |
|---|---|
| HAB_ED_POLISH | Distillate → < 1 µS/cm class (UPW POLISH / S01) |
| REMIN | Ca / Mg / K from core salts → drinking |
| POTABLE_TANK | Remineralized holdup (S26) |
| HAB_UV | Point-of-use UV (≥ 40 mJ/cm² class, root 07) |
| HAB_BOOST | Booster after gravity-first roof feed |

**NOTE**

Do not confuse with EW `POLISH BANK` (metal cells). Farm nutrient dose
remains S07 — separate from REMIN.

## 3. Streams

| ID | Role |
|---|---|
| S01 / S21 | Plant UPW / roof clean in |
| S02 | O₂ in |
| S04 | CO₂ out to farm |
| S06 | Q4 heat |
| S12 | Waste collect |
| S13 | Condensate → VCD |
| S14 | Food in |
| S25 | VCD distillate |
| S26 | Remineralized potable → taps |
| S28 | VCD brine → leach / salt |
| S29 | Treated grey → VCD / salt |
| S30 | Black digest → nutrient / salt |

## 4. Regenerate

```bash
cd Diagrams/aqueous_diagrams/pfd_scripts
python3 habitation_pfd.py
python3 hab_water_pfd.py
```
