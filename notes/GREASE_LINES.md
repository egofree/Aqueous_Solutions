# Ca and Li grease lines

Document number: AQS-DUTY-GREASE  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev W, notes/oil_cuts.md. Not a PE stamp.  
Rates are design assumptions. Not measured.

## Purpose

Both calcium and lithium greases are baseline. Required for self-replication (shop, conveyors, bearings, higher-temperature service). No external grease. Lithium soap is no longer excluded.

## Units

| Unit | Sector | Role |
|------|--------|------|
| P_CA | DIGESTER | Calcium hydroxide cake from pH-shift. Feed to GREASE_CA. |
| LI_RECOVER | DIGESTER | Lithium from polish-bank liquor. Feed to GREASE_LI. |
| GREASE_CA | OIL | Calcium soap kettle. |
| GREASE_LI | OIL | Lithium soap kettle. |

## Shared base

- Wax/oil: C19–C28 from `PROD_C19_C28` (~2 kg/d total wax; split between the two kettles).  
- Fatty acid: saponifiable fraction of the wax cut, or digester lipid if assayed.  
- No external fatty acid or preformed soap.

## Calcium grease

\[
2\,\mathrm{RCOOH} + \mathrm{Ca(OH)}_2 \rightarrow (\mathrm{RCOO})_2\mathrm{Ca} + 2\,\mathrm{H_2O}
\]

1. Saponify fatty acid with P-Ca (Ca(OH)₂) at ~100–150 °C with a little water.  
2. Disperse soap in molten C19–C28 (soap ~8–15 %).  
3. Cool and mill.  
Use: augers, conveyors, general shop, wet service, moderate temperature.

## Lithium grease

\[
\mathrm{RCOOH} + \mathrm{LiOH} \rightarrow \mathrm{RCOOLi} + \mathrm{H_2O}
\]

1. LI_RECOVER produces LiOH or Li₂CO₃ from polish-bank liquor (precipitation or crystallization).  
2. Saponify fatty acid with LiOH at ~100–150 °C.  
3. Disperse in molten wax (soap ~8–12 %). Optional: a small fraction of the Ca-free wax is held for the Li kettle so the higher dropping point is not diluted.  
4. Cool and mill.  
Use: bearings and any service above the Ca-grease range.

Lithium is recovered on-site. The path is no longer “unavailable.”

## Rates (assumptions)

| Product | Rate | Notes |
|---------|------|-------|
| Wax to grease | 2.0 kg/d | From C19–C28 |
| Ca grease | 1.2 kg/d | Majority of shop use |
| Li grease | 0.6 kg/d | Bearings / higher temp |
| P-Ca to kettle | ~0.1 kg/d | Stoichiometric excess |
| Li to kettle | ~0.02 kg/d | Stoichiometric; depends on polish tenor |

## Graph

Rev W. Edges: POLISH_BANK → LI_RECOVER → GREASE_LI; P_CA → GREASE_CA; PROD_C19_C28 → both kettles; both kettles → MFG_SHOP.

Fatty-acid split sized in notes/OIL_POLY_SIZE.md (0.8 kg/d saponifiable from 2.0 kg/d wax).

Locked: Li₂CO₃ precipitation, optional conversion to LiOH. See notes/DIGESTER_LI.md.
