# TI_CELL and MO_CELL duties

Document number: AQS-DUTY-TI-MO  
Revision: B  
Date: 2026-10-16  
Authority: notes/TI_MO_SELECTION.md, graph Rev J, binding requirements 2026-10-16. Not a PE stamp.  
Rates not set. loops_closed remains false.

## Process selection (locked)

- **TI_CELL:** Kroll primary. FFC Cambridge is a cold spare only (vessel envelope reserved, not a hot parallel train).
- **MO_CELL:** molten-salt electrolysis primary. Hydrogen reduction is a fallback study only; it is not a baseline edge.

See notes/TI_MO_SELECTION.md for the constraint set and comparison.

## TI_CELL — titanium metal (Kroll primary)

**Purpose.** Produce titanium metal on-site from ilmenite or rutile grit. Feeds pyrolyzer shell, anode mesh, and any titanium parts. Aqueous electrowinning is not used.

**Feed.** Dense grit fraction from FLOAT_SINK. Typical mineral: FeTiO₃ or TiO₂.

**Primary route — Kroll.**

1. **Chlorinator (sub-duty TI-CHLOR).**  
   Grit + recycled chlorine + pyro char at 800–1000 °C → TiCl₄ + iron chlorides.  
   Same vessel class already required for aluminum chlorination.  
   Chlorine is drawn from the CRU return header.

2. **TiCl₄ handling (sub-duty TI-COND).**  
   Condense and purify TiCl₄. Moisture-sensitive. Double containment. No aqueous acid contacts the condensate.

3. **Reduction retort (sub-duty TI-RETORT).**  
   TiCl₄ + 2 Mg → Ti sponge + 2 MgCl₂ in a sealed retort at 800–900 °C.  
   Magnesium metal is taken from the existing magnesium pot.  
   Vacuum distillation recovers magnesium and anhydrous MgCl₂.

4. **Magnesium recycle.**  
   Anhydrous MgCl₂ returns to the existing magnesium electrolytic pot.  
   Chlorine from that pot (and any excess from the chlorinator) returns to the CRU.  
   Net chlorine and magnesium are unchanged once the loop is closed.

**Product.** Titanium sponge or powder.  
**Returns.**  
- Slag / residual grit → LEACH_CSTR_1.  
- Chlorine → CRU.  
- MgCl₂ → existing magnesium pot (noted; no separate graph node yet).

**Cold spare — FFC Cambridge.**  
Sintered TiO₂ cathode electrolyzed in molten CaCl₂ near 900 °C. Oxygen leaves as CO/CO₂ at a graphite anode. No chlorine is generated. Vessel envelope is reserved. Not operated in parallel with Kroll. Activated only if the magnesium pot is unavailable for an extended period.

**Vessel.** Chlorinator (refractory), TiCl₄ condenser train, sealed reduction retort with vacuum distillation. Graphite or steel as appropriate.  
**Not designed.** Chlorinator MAWP and nozzle schedule, TiCl₄ purification stages, retort alloy, magnesium inventory hold-up, heat balance, FFC spare pot dimensions.

**Graph (Rev J).**  
- FLOAT_SINK → TI_CELL (dense grit)  
- TI_CELL → LEACH_CSTR_1 (slag)  
- TI_CELL → CRU (chlorine)

## MO_CELL — molybdenum metal (molten-salt primary)

**Purpose.** Recover molybdenum on-site so 316L and other Mo-bearing alloys can be made.

**Feed.** Post-EW liquor from EW_9 (or equivalent late-cascade liquor). Molybdenum present as molybdate or chloro-complex.

**Primary route — molten-salt electrolysis.**

1. Concentrate molybdenum from the acidic chloride liquor by precipitation or extraction.  
2. Dissolve the molybdenum salt in a chloride melt (NaCl–KCl or similar, consistent with the existing Al/Mg/Ca pots).  
3. Electrolyze. Molybdenum metal deposits at the cathode. Anode gas (Cl₂ or O₂, depending on salt) returns to the CRU or the existing anode-gas header.  
4. No hydrogen is consumed.

**Product.** Molybdenum metal (powder or cathode deposit).  
**Returns.**  
- Raffinate → POLISH_BANK.  
- Anode gas → CRU.

**Fallback study only — H₂ reduction.**  
MoO₃ reduced with hydrogen at 600–1100 °C. Not a baseline edge. Requires a deliberately sized hydrogen surplus that does not exist in the current methanol allocation. Documented in notes/TI_MO_SELECTION.md; not designed.

**Vessel.** Precipitation/extraction tanks + one molten-salt pot (or campaign use of existing pot geometry).  
**Not designed.** Selectivity against residual Zn/Fe/Ni, melt composition, current density, anode material, powder or deposit handling, nozzle schedule.

**Graph (Rev J).**  
- EW_9 → MO_CELL (liquor)  
- MO_CELL → POLISH_BANK (raffinate)  
- MO_CELL → CRU (anode gas)

## Shared constraints

- Both units are core. External supply of Ti or Mo metal is closed.  
- Aqueous cells do not make titanium.  
- Rates remain unset until a grit assay (FLOAT_SINK dense fraction) and a late-cascade liquor assay (EW_9) exist.  
- Chlorine and magnesium balances for the Kroll loop, and the anode-gas balance for MO_CELL, must close against the CRU and the existing magnesium pot before any rate is written.
