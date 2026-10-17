# Foundry and MFG — item 4

Document number: AQS-SIZE-FOUNDRY-MFG  
Revision: A  
Date: 2026-10-17  
Authority: notes/FOUNDRY_SIZING.md, notes/INVESTMENT_CASTING.md. Not a PE stamp.  
Design assumptions. Not measured.

## Forming machines

Throughput from FOUNDRY_SIZING: ROLL 10, EXTRUDE 5, DRAW 3 kg/d. Single-shift batch, not continuous mill.

| Unit | Size | Force / power | Notes |
|------|------|---------------|-------|
| ROLL | 1 stand, 150 mm rolls, 100 mm face | 50 kN separating force; 5 kW drive | Al, Cu, Fe sheet to ~2 mm. Reversing. |
| EXTRUDE | 50 mm container | 200 kN; 7 kW | Al, Cu, Mg rod and simple profile. |
| DRAW | Single-die bench, 1–8 mm | 10 kN; 2 kW | Rod to wire. FOUNDRY DRAW is primary. MFG WIRE_DRAW is final size only. |
| FORGE | Open-die, 50 kg ram class | 100 kN; 5 kW | Billets and preforms. Not a production hammer. |

All four are electrical loads on the existing rectifier path. Peak does not stack with IND_MELT if scheduled.

## Investment shell schedule

2 kg/d finished castings. Shell mass ~0.5 kg per kg casting → ~1 kg/d spent shell to GLASS_MILL.

| Step | Schedule |
|------|----------|
| Pattern | Wax inject or print. 1 day lot. |
| Shell build | 6 dips: 2 prime (fine silica/alumina + colloidal silica), 4 stucco. Dry 2 h between dips. Total ~1 day. |
| Dewax | Steam or flash, 150–200 °C. Wax condensate to WAX_PATTERN; unrecovered to OIL_FRAC. |
| Fire | 800–900 °C, 1 h. |
| Pour | From IND_MELT or VAC_IND. Mold preheat 200–400 °C by alloy. |
| Break | Knock-off. Shell → GLASS_MILL → GLASS_DIGEST. |

Zircon only on prime coat for Ti or reactive pours. Zircon returns with undigested grit.

## Pot → foundry rates

| Source | Metal | Rate to foundry | Notes |
|--------|-------|-----------------|-------|
| AL_POT | Al | 8 kg/d | Matches Al stock |
| (Cu from EW) | Cu | 3 kg/d | Via EW_9 path |
| (Fe from EW / melt) | Fe | 10 kg/d | |
| MG_POT | Mg | 0.5 kg/d | Alloy and extrude; not a bulk product |
| CA_POT | Ca | 0.2 kg/d | Alloy and soap; bulk Ca stays in chem loop |
| TI_CELL → VAC_IND | Ti | 0.40 kg/d | DESIGN_RATES |
| CR_CELL / MO_CELL | Cr / Mo | 0.20 / 0.05 kg/d | Into stainless make-up |

These are the design rates already used. No change. Edges exist; rates are not yet written on the edges (closure pass).

## Shop machines to maintain the foundry

MFG_SHOP must be able to repair and replicate foundry tooling. Minimum set:

| Machine | Maintains |
|---------|-----------|
| Engine lathe | Coil forms, mold copper, crucible patterns |
| Knee mill | Fixtures, die blanks |
| Drill / tap | Fasteners, mounting |
| Surface grinder | Roll and die faces |
| Weld set (TIG) | Copper coil repair, steel frames |
| Furnace (small resistive, alternate) | Heat-treat of shop tools only |

These are MFG duties, not foundry units. They consume FOUNDRY stock (plate, rod, wire) and return scrap to IND_MELT (edge present).

## Open

- Roll crown and pass schedule.  
- Extrusion die library.  
- Exact shell flour mesh sizes.  
- Edge rates still await the closure pass.
