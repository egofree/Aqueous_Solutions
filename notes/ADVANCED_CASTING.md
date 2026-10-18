# Advanced casting techniques — foundry applicability

Document number: AQS-NOTE-CAST  
Revision: A  
Date: 2026-10-16  
Authority: literature review against notes/FOUNDRY_DESIGN.md. Not a PE stamp.

## Scope

Techniques beyond gravity pour into a permanent mold or sand ingot. Evaluated for the metals the plant produces and for induction/RF as primary heat.

## Techniques reviewed

### 1. Vacuum / inert casting (already partially specified)
- **Vacuum induction melting (VIM)** and **induction skull melting (ISM) / cold-crucible induction melting (CCIM)**.  
- ISM/CCIM holds the melt in a solidified skull of the same metal inside a water-cooled copper crucible. No refractory contact. Required for Ti; useful for other reactive metals.  
- **Vacuum arc remelting (VAR)** is the industrial standard for Ti ingot but needs a consumable electrode and is a secondary melt. Not the first choice when the feed is sponge or powder and induction is preferred.  
- Fit: high. `VAC_IND` + `VAC_CAST` already named. ISM/CCIM should be the explicit method inside `VAC_IND` for Ti.

### 2. Investment (lost-wax) casting
- Wax or printed pattern, ceramic shell, burnout, pour.  
- Excellent surface and dimensional tolerance. Used for complex shapes in Al, steel, superalloys, and (with vacuum) Ti.  
- Fit: medium. Useful for Fab fixtures and complex MFG parts. Adds a wax/ceramic loop that must be reclaimed or the ceramic becomes a solids-line feed. Not required for bulk stock.

### 3. Low-pressure and vacuum die casting
- Controlled fill of a metal die under low pressure or vacuum. Reduces porosity versus high-pressure die casting.  
- Common for Al and Mg structural parts.  
- Fit: medium for Al/Mg near-net shapes. Requires die steel and a pressure system. Not needed for ingot/billet stock.

### 4. Semi-solid (rheocasting / thixocasting)
- Metal processed in the semi-solid range (globular solid in liquid). Lower porosity, better properties, heat-treatable versus conventional high-pressure die casting.  
- Rheocasting makes slurry from liquid (fits an induction furnace). Thixocasting needs special billets.  
- Fit: low-to-medium. Relevant only if the plant casts complex Al/Mg structural parts. Not required for plate/rod/wire stock. Rheocasting is the better of the two if added later.

### 5. Squeeze casting
- Melt poured into a die and solidified under high pressure. Low porosity, good properties.  
- Fit: low. Specialized dies; not needed for stock production.

### 6. Continuous / semi-continuous casting
- Steady withdrawal of billet, slab, or rod from a water-cooled mold. Dominant for Al, Cu, and steel primary stock.  
- Recent work shows vacuum semi-continuous induction melting for Ti ingot with good homogeneity.  
- Fit: high for bulk stock. A small horizontal or vertical continuous caster fed from `IND_MELT` (and a vacuum version from `VAC_IND`) would replace much batch ingot casting for Al, Cu, Fe, and possibly Ti.

### 7. Centrifugal casting
- Rotating mold for tubes, rings, and cylindrical parts. Good for Fe, Cu, and some alloys.  
- Fit: low unless tubular stock is a defined product.

### 8. Electromagnetic stirring (EMS) in continuous casting
- Induction stirring of the sump to reduce porosity and segregation.  
- Fit: natural extension if continuous casting is added; uses the same induction power class.

## Recommendation for this plant

| Priority | Technique | Action |
|----------|-----------|--------|
| Baseline | Induction skull / cold-crucible for Ti | Specify ISM/CCIM as the method inside `VAC_IND` |
| Baseline | Continuous or semi-continuous casting for Al, Cu, Fe stock | Add as a named option under `CAST_LINE` or a new `CONT_CAST` unit |
| Baseline | Investment casting | Required for self-replication of complex parts. Units and shell reclaim in notes/INVESTMENT_CASTING.md. Graph Rev P. |
| Optional | Rheocasting | Add only if complex low-porosity Al/Mg parts are required |
| Not baseline | High-pressure die casting, squeeze casting, full VAR electrode route | Documented alternates; not sized |

## Status

Investment casting is baseline (Rev P). Shell reclaim edged. Continuous casting added as CONT_CAST. ISM/CCIM locked for Ti. Rates are design assumptions in notes/FOUNDRY_SIZING.md.
