# Investment casting — baseline

Document number: AQS-DUTY-INV  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev P. Not a PE stamp.  
Shell schedule (6 dips, fire 800–900 °C): notes/FOUNDRY_MFG_SIZE.md.

## Status

Baseline process. Required for self-replication of complex parts (impellers, fixtures, near-net shapes that machining alone cannot economically produce). Ceramic shell waste is reprocessed; it is not an open stream.

## Units (sector FOUNDRY)

| Unit | Duty |
|------|------|
| WAX_PATTERN | Wax pattern (injected or printed). Wax is reclaimed from burnout condensate where practical. |
| SHELL_BUILD | Repeated dip in ceramic slurry + stucco. Typical shell: silica or alumina flour, zircon where needed for reactivity, colloidal silica binder. |
| SHELL_BURNOUT | Dewax (steam or flash), then fire the shell. Wax condensate to reclaim or oil line. |
| INV_CAST | Pour from IND_MELT (Al, Cu, Fe, Ni alloys) or VAC_IND (Ti and reactive). |
| SHELL_BREAK | Knock off spent shell. Casting to STOCK_OUT. Shell solids to solids line. |

## Ceramic shell composition (design basis)

- Primary flour: silica or alumina (both producible or recoverable on-site via the glass/ceramic branch).  
- Stucco: same family, coarser grade.  
- Binder: colloidal silica (from the existing silicate liquor path).  
- Zircon: used only where metal reactivity requires it; zircon grit is already a named undigested solid in the solids line and can be recycled.

## Reclaim path (closed)

1. SHELL_BREAK → spent ceramic (silica/alumina/zircon) → GLASS_MILL.  
2. GLASS_MILL → GLASS_DIGEST (NaOH digest).  
3. Digest opens silica and alumina into the existing silicate / hydroxide split.  
4. Undigested zircon returns to the grit recycle already defined for the solids line.  
5. No shell material leaves the plant.

Wax from burnout: condense and return to WAX_PATTERN. Unrecovered wax to the oil line.

## Metals

- Air or inert pour: Al, Cu, Fe, Ni, Zn alloys from IND_MELT.  
- Vacuum pour: Ti and other reactive metals from VAC_IND (ISM/CCIM).  
- Output: near-net castings to STOCK_OUT, then to MFG or FAB as required.

## Not yet sized

- Shell layers and dry time.  
- Burnout temperature schedule.  
- Pour temperature and mold preheat per alloy.  
- Wax reclaim yield.  
- Rates.

## Graph

Rev P. Edges: WAX_PATTERN → SHELL_BUILD → SHELL_BURNOUT → INV_CAST → SHELL_BREAK → STOCK_OUT; SHELL_BREAK → GLASS_MILL → GLASS_DIGEST; IND_MELT and VAC_IND → INV_CAST.
