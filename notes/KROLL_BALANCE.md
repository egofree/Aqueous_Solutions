# Kroll loop — placeholder balance

Document number: AQS-BAL-KROLL  
Revision: A  
Date: 2026-10-16  
Authority: notes/TI_MO_DUTIES.md Rev B, notes/ASSAY_TI_MO.md. Not a PE stamp.  
This is a stoichiometric check only. It is not a design rate. The grit assay is missing.

## Basis (assumption, not a measurement)

- 1.0 kg Ti metal produced.  
- Feed treated as TiO₂ equivalent (rutile or upgraded ilmenite). Real grit assay will change the Fe and gangue terms.  
- Chlorination: TiO₂ + 2 C + 2 Cl₂ → TiCl₄ + 2 CO.  
- Reduction: TiCl₄ + 2 Mg → Ti + 2 MgCl₂.  
- Magnesium recycle: MgCl₂ electrolyzed in the existing magnesium pot → Mg + Cl₂. Cl₂ returns to the CRU.

## Mass per kg Ti

| Stream | kg per kg Ti | Notes |
|--------|--------------|-------|
| TiO₂ equivalent feed | 1.67 | 79.9/47.9 |
| Carbon (pyro char) | 0.50 | 24/47.9 |
| Cl₂ to chlorinator | 2.96 | 141.8/47.9; returned from Mg pot |
| TiCl₄ intermediate | 3.96 | 189.7/47.9 |
| Mg metal to retort | 1.01 | 48.6/47.9; from existing Mg pot |
| MgCl₂ from retort | 3.97 | returns to Mg pot |
| Cl₂ from Mg pot | 2.96 | closes the chlorine loop |
| Ti metal product | 1.00 | |
| CO from chlorinator | 1.17 | 56/47.9; to existing gas handling |

## Closure statement

- Chlorine: 2.96 kg consumed = 2.96 kg returned. Net zero once the Mg pot is in the loop.  
- Magnesium: 1.01 kg consumed = 1.01 kg regenerated. Net zero.  
- The existing CRU and magnesium pot can absorb the Kroll duty without a new chlorine or magnesium source, provided the pot has spare capacity equal to 1.01 kg Mg (and 2.96 kg Cl₂) per kg Ti.  
- CO and any unreacted chlorides are incremental loads on the existing gas and leach returns. They are not sized here.

## What this does not do

- It does not set a kg/d rate. The dense-grit assay is missing (notes/ASSAY_TI_MO.md).  
- It does not size the chlorinator, condenser, or retort.  
- It does not address iron from ilmenite. An ilmenite feed produces additional FeClₓ that must be separated before the TiCl₄ condenser; that split is undefined until the assay exists.  
- FFC Cambridge is not in this balance. It remains the cold spare.

## MO_CELL note

No analogous balance is written. The EW_9 liquor assay (Mo, Zn, Fe, Ni) is missing. Anode-gas return to the CRU is noted on the graph but has no rate.
