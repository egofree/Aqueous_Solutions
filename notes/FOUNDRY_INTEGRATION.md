# FOUNDRY role fixes — Rev O

Document number: AQS-INT-FOUNDRY  
Revision: B  
Date: 2026-10-16  
Authority: graph Rev O. Not a PE stamp.

## Machines added

- `AL_POT`, `MG_POT`, `CA_POT` (sector MFG). Molten-salt pots. Metal to `IND_MELT`. Cl₂ from Al and Mg pots to `CRU`.

## Role conflicts resolved

| Conflict | Resolution |
|----------|------------|
| MET_MELT (MFG) vs IND_MELT (FOUNDRY) | IND_MELT is primary bulk melt. MET_MELT retained as MFG hold/transfer only. Not sized as primary. |
| WIRE_DRAW (MFG) vs DRAW (FOUNDRY) | DRAW (FOUNDRY) is primary wire/rod draw to STOCK_OUT. WIRE_DRAW (MFG) does final sizing only. Edge: STOCK_OUT → WIRE_DRAW. |
| GAS_ATOMIZER | Optional. Fed from IND_MELT when powder stock is required. Powder returns to STOCK_OUT. Not baseline. |
| Power | IND_MELT and RF_HEAT marked electrical_role = load (RECTIFIER / LOAD_AGG). |
| Heat | IND_MELT and VAC_IND waste heat → MET_HX_Q4. |
| COMB_HEAT off-gas | → MET_SCRUB when the alternate path is used. |

## Edges added (Rev O)

AL_POT / MG_POT / CA_POT → IND_MELT; AL_POT / MG_POT → CRU; IND_MELT / VAC_IND → MET_HX_Q4; COMB_HEAT → MET_SCRUB; STOCK_OUT → WIRE_DRAW; IND_MELT → GAS_ATOMIZER → STOCK_OUT.

## Investment casting

Baseline as of Rev P. See notes/INVESTMENT_CASTING.md. Spent shell returns SHELL_BREAK → GLASS_MILL → GLASS_DIGEST. Edges present. Not an open waste.

- Coil, crucible, and CONT_CAST details are in notes/FOUNDRY_SIZING.md and notes/FOUNDRY_COIL_MOLD.md.  
- Rates are design assumptions in notes/FOUNDRY_SIZING.md.  
- loops_closed remains false.
