# Cryogenic equipment list

Document number: AQS-EQP-CRY-001  
Revision: G  
Date: 2026-10-29  
Process flow diagram: AQS-PFD-CRY-001 (`cryo_pfd.png`)  
Basis: AQS-CRY-002; `models/freecad/cryo.py`; AQS-PHF-001; AQS-STR-001; AQS-HSE-001; AQS-PWR-002 and AQS-FC-001 (users of `CRYO_H2`); AQS-EQP-GEO-001 (Q4 header).  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with sector PFD generators | 2026-09-27 |
| B | 1 | CRYO_H2 sizing interface for GEN + FC + vent | 2026-09-28 |
| C | 1 | Cold-box internals tags + HVAC/Q4/dedicated cooling (AQS-CRY-002) | 2026-09-28 |
| D | 1 | CRYO_AHU_COND / S70; S64 H₂ normal; S67 flue-cap (AQS-VENT-001) | 2026-09-28 |
| E | 1 | Study Stirling/AHU_COND/holdup bounds; 9×6 envelope | 2026-10-01 |
| F | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; sections renumbered (the hydrogen store interface is now §6). Tags, ratings and rules unchanged. | 2026-10-24 |
| G | 1 | References to documents outside this repository removed; the FreeCAD script cited by its path in the repository. Tags, ratings and rules unchanged. | 2026-10-29 |

## 1. Purpose and scope

The cryogenic plant separates air and process gases at 77–90 K into oxygen, nitrogen, carbon dioxide and hydrogen products, and holds them in receivers for the rest of the plant. This page lists the cryogenic units (the cold box, its internals and the product receivers), the separation rules, the sizing interface of the hydrogen store, the heat rejection paths and the FreeCAD stubs.

Ratings marked TBD are still to be determined. No reboiler, condenser or coefficient-of-performance rating is taken from earlier narrative documents, and no M1 nameplate is invented.

## 2. Terms

- Cold box: the insulated enclosure that holds the cryocoolers, columns and heat exchangers.
- Stirling cryocooler (cold head): a small closed-cycle refrigerator that reaches 77–90 K.
- PSA, TSA: pressure-swing and temperature-swing adsorption, ways of removing gases with an adsorbent bed.
- Receiver: a product hold vessel.
- Q4: the lowest-temperature water header, the only heat that enters life-support air.
- VJ: vacuum-jacketed (pipe).
- M1: the first module of the plant at the baseline size.

Stream numbers (S02 and so on) are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Cold box and receivers

Table 3.1. Cold box and product receivers

| Tag | Duty | Status |
|---|---|---|
| COLD_BOX | Parent envelope: Stirling 77–90 K + distillation / PSA | Issued — massing |
| CRYO_H2 | Product hold / fuel (not HDR_H2) | Issued — volume TBD |
| CRYO_O2 | → HDR_O2 (S02); FC oxidizer branch (S50) | Issued |
| CRYO_N2 | → HDR_N2 (S03) | Issued |
| CRYO_CO2 | → HDR_CO2 (S04) | Issued |

When `BASEMENT_LEVELS` is greater than 1, units on further basements take the suffix `_B2` and so on.

## 4. Cold-box internals (AQS-CRY-002)

Table 4.1. Cold-box internals

| Tag | Duty | Status |
|---|---|---|
| AIR_INTAKE | Ambient centrifugal + demister (doc 09 §2.2) | Issued — rating TBD |
| MOL_SIEVE | CO₂ / H₂O molecular sieves (5Å TSA class) | Issued — capacity TBD |
| HEPA_BANK | Final particulate polish before cold box | Issued |
| STIRLING_COLD_HEAD | Cryocooler 77–90 K | Issued — **REQ-CRY-STIR-CONT ≈ 4 kW_e** (2–8); SI-CRY-01 (AQS-REQ-KW-001) |
| DIST_COL_PRI | Primary cryogenic distillation column | Issued — duty TBD |
| DIST_COL_SEC | Secondary column (hot-swap / maintenance class) | Issued — duty TBD |
| DIST_COL_TER | Tertiary column train | Issued — duty TBD |
| REBOILER_COND | Reboiler / condenser heat integration | Issued — duty TBD |
| COMP_EXPAND | Variable-speed compressors + expanders (VFD) | Issued — duty TBD |
| VJ_LINES | Vacuum-jacketed transfer lines to receivers | Schedule — CAD stub optional |
| CRYO_HX_Q4 | Named HX: warm reject → Q4 (S54) | Issued |
| CRYO_DED_COOL | Dedicated cryo utility cooling loop (S55) | Issued — rating TBD |
| CRYO_AHU | CRYO room mechanical ventilation (NFPA 2/55; S56 residual) | Issued — study 6–12 ACH on 216 m³ |
| CRYO_AHU_COND | Condensate knockout; condensable return (S70) | Study ~2–5 kW KO (AQS-EQP-VENT-001 §4.3); FreeCAD stub |

## 5. Separation rules

1. `CRYO_H2` is not `HDR_H2`.
2. Acid gas and oil vapour do not enter `COLD_BOX`.
3. The bromine tower of the zinc-bromide battery does not share a cold box or header with the cryogenic plant.
4. The S18 flue-capture carbon dioxide is claimed; raw afterburner flue does not enter `HDR_CO2`.
5. No HVAC return air is shared between habitation and the cryogenic or process areas (AQS-HSE-001 §8).

## 6. Hydrogen store interface (sizing)

The `CRYO_H2` product hold shall be sized for its users running at the same time (Table 6.1).

Table 6.1. Users of the hydrogen store

| Consumer | Stream | Authority |
|---|---|---|
| BACKUP_GEN | S45 | AQS-PWR-002 / AQS-EQP-GEN-001 |
| FUEL_CELL (PEM) | S49 | AQS-FC-001 / AQS-EQP-FC-001 |
| H₂ dryer normal | S64 | AQS-VENT-001 Partial |
| Roof contingency | S24 | AQS-VENT-001 emergency only |

The fuel cell's oxidant is `CRYO_O2` (S50). The study operating hold-up is about 5–10 kg (1–2 days at about 4.8 kg/d of hydrogen). The design cap on the maximum allowable quantity remains AQS-HSE-001 §5 (under the 150 lb class). The generator and fuel-cell branches have separate isolation and flame arrestors (AQS-HSE-001 §11).

## 7. Heat rejection and utility cooling

Table 7.1. Heat rejection paths

| Path | Stream | Destination | Content |
|---|---|---|---|
| CRYO_HX_Q4 | S54 | Q4 / FARM / HAB | Warm residual < 80 °C after pinch (intercooler / sieve cool-down) |
| CRYO_DED_COOL | S55 | Dedicated cryo loop | Stirling + deep condenser / expander reject |
| CRYO_AHU / CRYO_AHU_COND | S70 / S56 | COLD_BOX / residual vent | Condensable return; residual contingency only |

The other users of the Q4 water header are S06 (HVAC), S44 (`GEO_HP`), S53 (`FC_HX_Q4`) and S54. Generator exhaust (S46) never enters Q4 or `CRYO_HX_Q4`.

## 8. FreeCAD stubs

`models/freecad/cryo.py` attaches `COLD_BOX`, the receivers and envelope stubs for the internals (`AIR_INTAKE`, `MOL_SIEVE`, `HEPA_BANK`, `STIRLING_COLD_HEAD`, `DIST_COL_*`, `REBOILER_COND`, `COMP_EXPAND`, `CRYO_HX_Q4`, `CRYO_DED_COOL`, `CRYO_AHU`). The assembled plant (`plant.FCStd`) must be rebuilt before these children appear in it.

## 9. Rebuilding the drawing

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 cryo_pfd.py
```
