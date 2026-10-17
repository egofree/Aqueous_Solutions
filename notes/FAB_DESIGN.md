# FAB — item 6

Document number: AQS-DES-FAB  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev Y. Not a PE stamp.  
Rates are design assumptions.

## Tool list (present units)

| Unit | Duty |
|------|------|
| WAFER_FAB | Parent. Slicing, doping, etch, clean. |
| WET_BENCH | Clean and etch. |
| WS_HF_ED | HF (from plant HF_GEN / WS path). |
| WS_KOH | KOH etch. |
| WS_NITRIC | Nitric. |
| WS_PEROX | Peroxide clean. |
| WS_AMMONIA | Ammonia clean. |
| WS_PHOS | Phosphoric. |
| WS_DOPE | Dopant. |
| WS_SLURRY | Slice slurry. |
| WS_SOLV | Solvent. Waste to oil line (edged). |
| LITHO_COAT / ALIGN / DEV / STUB | Lithography. Dev waste to oil. |
| SOLAR_PV_CELL | Cell line. Uses plant Si and metals. |
| FAB_UPW_TANK | Ultra-pure water. |

## Balances against plant stock

| Demand | Rate (assumption) | Source |
|--------|-------------------|--------|
| Si (wafer + PV) | 0.5 kg/d | SI_REDUCE / foundry stock |
| Al, Cu fixtures | 0.2 kg/d | FOUNDRY STOCK_OUT (edged) |
| Fluoropolymer (gaskets, tanks) | 0.05 kg/d | POLY_STOCK (edged) |
| UPW | 50 L/d | HDR_UPW / BMED_UPW_POLISH |
| Solvent use | 0.5 kg/d | OIL C5–C10 + plant solvents |
| Solvent waste | 0.4 kg/d | To OIL_FRAC (S38, S39B present) |
| HF use | 0.1 kg/d | HF_GEN / WS_HF_ED. Contained. |

UPW and solvent numbers are sized for a pilot fab, not a commercial line. They fit the polymer and metal stock rates already set.

## Open

- Wafer diameter and slice yield.  
- Exact dopant species.  
- UPW resistivity spec (target <1 µS/cm from existing water-cycle note).

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
