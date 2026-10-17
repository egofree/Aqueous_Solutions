# FOUNDRY sector — inputs and outputs

Document number: AQS-IO-FOUNDRY  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev R, notes/FOUNDRY_SIZING.md. Not a PE stamp.  
Rates are design assumptions.

## Inputs

| From | Sector | To | Carries |
|------|--------|----|---------|
| EW_9 | DIGESTER | IND_MELT | Cathode/powder metals |
| AL_POT, MG_POT, CA_POT | MFG | IND_MELT | Al, Mg, Ca metal |
| TI_CELL | MFG | VAC_IND / IND_MELT | Ti sponge/powder |
| MO_CELL, CR_CELL | MFG | IND_MELT | Mo, Cr metal |
| SALT_FEED | DIGESTER | FLUX_PREP | Flux salts |
| MFG_SHOP | MFG | IND_MELT | Manufacturing scrap |
| (internal) | FOUNDRY | IND_MELT | Foundry scrap from CAST_LINE |

## Outputs

| From | To | Sector | Carries |
|------|----|--------|---------|
| STOCK_OUT | MFG_SHOP | MFG | Plate, rod, wire stock |
| STOCK_OUT | WIRE_DRAW | MFG | Rod/wire for final sizing |
| STOCK_OUT | WAFER_FAB | FAB | Specialty stock |
| IND_MELT | GAS_ATOMIZER | MFG | Melt when powder required (optional path) |
| GAS_ATOMIZER | STOCK_OUT | FOUNDRY | Powder stock return |
| SHELL_BREAK | GLASS_MILL | GLASS | Spent ceramic shell |
| GLASS_MILL | GLASS_DIGEST | GLASS | Milled shell |
| IND_MELT | LEACH_CSTR_1 | DIGESTER | Slag |
| SHELL_BURNOUT | WAX_PATTERN | FOUNDRY | Wax condensate reclaim |
| SHELL_BURNOUT | OIL_FRAC | OIL | Unrecovered wax |
| IND_MELT, VAC_IND | MET_HX_Q4 | MFG | Waste heat |
| COMB_HEAT | MET_SCRUB | MFG | Off-gas when alternate used |
| AL_POT, MG_POT | CRU | DIGESTER | Cl₂ (pot return, not foundry proper) |

## Electrical

IND_MELT (25 kW) and RF_HEAT (5 kW) are electrical loads on the existing RECTIFIER / LOAD_AGG path. No separate power edge; role is set on the node.

## Not connected (intentional)

- Rheocasting, HPDC, squeeze casting: not baseline.  
- Direct farm or habitation feed: none.  
- New fuel train for COMB_HEAT: uses existing headers only when energized.

## Graph

Rev R. Mass edges listed above are present. Rates remain the assumptions in notes/FOUNDRY_SIZING.md.
