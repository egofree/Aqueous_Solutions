# CR_CELL duty — chromium metal

Document number: AQS-DUTY-CR  
Revision: A  
Date: 2026-10-16  
Authority: binding requirements 2026-10-16, graph Rev K. Not a PE stamp.  
Rates not set. loops_closed remains false.

## Purpose

Produce chromium metal on-site from stainless scrap or chromite grit so that 304/316 grades (and any other Cr-bearing alloy) can be made. External supply is closed. Aqueous electrowinning is not used.

## Feed options

1. Stainless scrap (preferred when available): 304/316 turnings or end-of-life parts already inside the plant.  
2. Chromite grit (FeCr₂O₄) from the dense solids split, if present in the feedstock.

Missing measurement: Cr grade and co-elements (Fe, Ni, Mo) in the chosen feed. No composition is on an edge. See the same rule as notes/ASSAY_TI_MO.md.

## Primary route — molten-salt electrolysis

Consistent with the locked paths for aluminum, magnesium, and molybdenum.

1. Oxidize or chlorinate the feed to a soluble chromium salt (CrCl₃ or chromate that is then converted).  
2. Dissolve in a chloride melt (NaCl–KCl or NaCl–CaCl₂, same family as the existing pots).  
3. Electrolyze. Chromium deposits at the cathode. Anode gas (Cl₂) returns to the CRU.  
4. Iron and nickel, if present, are either pre-separated or co-deposited and later parted; the split is undefined until the feed assay exists.

**Product.** Chromium metal (powder or cathode deposit).  
**Returns.** Anode gas → CRU. Slag or residual solids → LEACH_CSTR_1.  
**Vessel.** One molten-salt pot (or campaign use of existing pot geometry). Graphite anode.  
**Not designed.** Melt composition, current density, pre-separation of Fe/Ni, deposit handling, nozzle schedule, heat balance.

## Alternate (not baseline)

Aluminothermic reduction of Cr₂O₃. Consumes aluminum metal already produced on-site and yields a Cr–Al alloy or high-carbon chromium that still requires refining. Higher reagent demand, less direct fit to the chlorine loop. Retained as a study only.

## Graph

`CR_CELL` is present (sector MFG) from Rev H. No feed or return edges are rated. When an assay exists, add:

- scrap or grit → CR_CELL  
- CR_CELL → CRU (Cl₂)  
- CR_CELL → LEACH_CSTR_1 (slag)

## Shared constraints

- Core requirement. No external chromium.  
- Same molten-salt block discipline as TI_CELL (cold spare only) and MO_CELL (primary).  
- Rate remains unset until the feed assay is on the edge or explicitly carried as missing.
