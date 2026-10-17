# FOUNDRY sector

Document number: AQS-DUTY-FOUNDRY  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev L. Not a PE stamp.  
Rates are design assumptions in notes/FOUNDRY_SIZING.md (~26 kg/d). Not measured.

## Purpose

Metal foundry as a distinct sector. Primary heat is inductive and RF. Resistive and combustion heat are alternates only, used when the primary path is unavailable or for a specific duty that induction/RF cannot serve.

## Units (sector FOUNDRY)

| Unit | Role | Priority |
|------|------|----------|
| IND_MELT | Coreless or channel induction melt furnace | Primary |
| RF_HEAT | RF heating for preheat, sintering, zone refining, and small-lot work | Primary |
| RES_HEAT | Resistive elements | Alternate / redundant |
| COMB_HEAT | Combustion (fuel from existing H₂ or methanol headers) | Alternate / redundant |
| CAST_LINE | Casting, alloying, and scrap return | — |

## Heat policy

- Induction is the default for bulk melt (Al, Mg, Fe-based, and alloy charges from the metal cells).  
- RF is the default for preheat, sintering of powders (Ti, Mo, Cr), and any zone or surface duty.  
- Resistive heat is energized only if induction or RF is down, or for a hold duty that does not justify an induction coil.  
- Combustion is energized only if electrical heat is unavailable, or for a duty that requires a reducing flame. Fuel is taken from existing headers; no new fuel train.  
- No combustion or resistive unit is sized as the baseline capacity. They are parallel redundant paths.

## Feeds and returns

- Metal powders and sponge from TI_CELL, MO_CELL, CR_CELL, and the existing EW/molten-salt products → IND_MELT.  
- Molten metal → CAST_LINE.  
- Foundry scrap → IND_MELT.  
- Slag → LEACH_CSTR_1 (edge present, Rev N). Rate is the sizing assumption.

## Not designed

- Coil frequency and power for IND_MELT and RF_HEAT.  
- Crucible or refractory alloy.  
- Exact alternate-path interlock logic.  
- Rates.

## Design

Full machine list, metal-class melt matrix, and outputs: notes/FOUNDRY_DESIGN.md.  
Graph Rev M adds VAC_IND, VAC_CAST, ROLL, EXTRUDE, DRAW, FORGE, SINTER, FLUX_PREP, STOCK_OUT.

Rev L. Sector FOUNDRY. Placeholder edges: IND_MELT → CAST_LINE, CAST_LINE → IND_MELT (scrap), TI_CELL → IND_MELT.
