# Cryo / ALCRM equipment list

Document number: AQS-EQP-CRY-001  
Revision: E  
Date: 2026-10-01  
PFD: AQS-PFD-CRY-001 (`cryo_pfd.png`)  
Authority: AQS-CRY-002, `09-air-liquefaction-cryogenic.md`,
`freecad/cryo.py`, AQS-PHF-001, AQS-STR-001, AQS-HSE-001,
AQS-PWR-001 / AQS-FC-001 (CRYO_H2 consumers), AQS-EQP-GEO-001 (Q4 peer).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue with sector PFD generators | 2026-09-27 |
| B | 1 | CRYO_H2 sizing interface for GEN + FC + vent | 2026-09-28 |
| C | 1 | Cold-box internals tags + HVAC/Q4/dedicated cooling (AQS-CRY-002) | 2026-09-28 |
| D | 1 | CRYO_AHU_COND / S70; S64 H₂ normal; S67 flue-cap (AQS-VENT-001) | 2026-09-28 |
| E | 1 | Study Stirling/AHU_COND/holdup bounds; 9×6 envelope | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

## 1. Locked CAD units (parent + receivers)

| Tag | Duty | Status |
|---|---|---|
| COLD_BOX | Parent envelope: Stirling 77–90 K + distillation / PSA | Issued — massing |
| CRYO_H2 | Product hold / fuel (not HDR_H2) | Issued — volume TBD |
| CRYO_O2 | → HDR_O2 (S02); FC oxidizer branch (S50) | Issued |
| CRYO_N2 | → HDR_N2 (S03) | Issued |
| CRYO_CO2 | → HDR_CO2 (S04) | Issued |

Basement suffixes `_B2`… when `BASEMENT_LEVELS > 1`.

## 2. Cold-box internals (AQS-CRY-002)

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
| CRYO_AHU_COND | Condensate knockout; condensable return (S70) | Study ~2–5 kW KO (VENT-EQP §2.3); FreeCAD stub |

**NOTE**

Doc 09 primary/secondary reboiler–condenser kW and COP figures are
**legacy narrative only**. Do not invent M1 nameplates.

## 3. Separation rules

1. CRYO_H2 is not HDR_H2.
2. Acid-gas and oil vapor do not enter COLD_BOX.
3. ZnBr2 Br₂ tower does not share a cold box or header with CRYO.
4. S18 flue-cap CO₂ is Claimed — not raw AFTERBURNER into HDR_CO2.
5. No shared HVAC return HAB ↔ CRYO / process (AQS-HSE-001 §6).

## 4. CRYO_H2 consumer interface (sizing)

CRYO_H2 product hold shall be sized for concurrent consumers:

| Consumer | Stream | Authority |
|---|---|---|
| BACKUP_GEN | S45 | AQS-PWR-001 / AQS-EQP-GEN-001 |
| FUEL_CELL (PEM) | S49 | AQS-FC-001 / AQS-EQP-FC-001 |
| H₂ dryer normal | S64 | AQS-VENT-001 Partial |
| Roof contingency | S24 | AQS-VENT-001 emergency only |

Oxidizer to FC is CRYO_O2 (S50). **Study operating holdup ~5–10 kg** (1–2 d × ~4.8 kg/d H₂). MAQ design cap remains AQS-HSE-001 §3 (< 150 lb class). GEN and FC branches: separate
isolation + flame arrestors (AQS-HSE-001 §8a).

## 5. Heat rejection / utility cooling

| Path | Stream | Destination | Content |
|---|---|---|---|
| CRYO_HX_Q4 | S54 | Q4 / FARM / HAB | Warm residual < 80 °C after pinch (intercooler / sieve cool-down) |
| CRYO_DED_COOL | S55 | Dedicated cryo loop | Stirling + deep condenser / expander reject |
| CRYO_AHU / COND | S70 / S56 | COLD_BOX / residual vent | Condensable return; residual contingency only |

Peers on Q4 water: S06 (HVAC), S44 (GEO_HP), S53 (FC_HX_Q4), **S54**.
GEN exhaust (S46) never enters Q4 or CRYO_HX_Q4.

## 6. FreeCAD stubs

`freecad/cryo.py` attaches COLD_BOX + receivers and internal envelope
stubs (AIR_INTAKE, MOL_SIEVE, HEPA_BANK, STIRLING_COLD_HEAD,
DIST_COL_*, REBOILER_COND, COMP_EXPAND, CRYO_HX_Q4, CRYO_DED_COOL,
CRYO_AHU). **plant.FCStd rebuild required** before children appear in
the assembled plant — not performed this pass.

## 7. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 cryo_pfd.py
```
