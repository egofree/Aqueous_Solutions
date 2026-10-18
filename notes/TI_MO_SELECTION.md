# TI_CELL and MO_CELL process selection

Document number: AQS-SEL-TI-MO  
Revision: A  
Date: 2026-10-16  
Authority: analysis against graph Rev I and binding requirements 2026-10-16. Not a PE stamp.  
Rates not set. loops_closed remains false.

## Purpose

Select the production route for titanium metal (TI_CELL) and molybdenum metal (MO_CELL). Both are binding on-site requirements. Aqueous electrowinning is excluded for titanium.

## Existing constraints that govern the choice

- Chlorine is a closed loop. Aluminum chlorination consumes recycled Cl₂. The magnesium, aluminum, and calcium pots return Cl₂ to the CRU. There is no net chlorine export.
- Magnesium metal is already produced by electrolysis of anhydrous MgCl₂. The pot and the chlorine return exist.
- Hydrogen is scarce. Cathode H₂ from the electrowinning cascade is collected, dried, and allocated to methanol. Prior closure accounting showed roughly 0.3 kg/d collected, supporting on the order of 0.1 kW. It is not sized for a metal-reduction duty.
- Calcium is already produced on a contact-cathode pot. CaCl₂ is therefore an available melt constituent.
- The plant already operates multiple high-temperature molten-salt pots and one sealed retort (rare earths). An additional pot or retort is consistent with the metal block. A new bulk gas-handling train is not free.
- Aqueous cells do not make titanium, aluminum, magnesium, calcium, lithium, silicon, or the rare earths.

## TI_CELL — Kroll versus FFC Cambridge

| Factor | Kroll | FFC Cambridge |
|--------|-------|---------------|
| Chemistry | Grit + Cl₂ + C → TiCl₄. TiCl₄ + 2 Mg → Ti + 2 MgCl₂. Vacuum distillation recovers Mg and MgCl₂. | TiO₂ cathode electrolyzed in molten CaCl₂ near 900 °C. Oxygen leaves as CO/CO₂ at a graphite anode. |
| Fit to existing loops | Direct. Consumes magnesium the plant already makes. MgCl₂ returns to the existing magnesium pot. Cl₂ returns to the CRU. The chlorinator is the same class of vessel already required for aluminum. | Indirect. Uses CaCl₂ (available) but generates no Cl₂ and does not close against the Mg/Cl₂ loop. CO/CO₂ must be handled. |
| New equipment | Chlorinator, TiCl₄ condenser and purifier, sealed reduction retort, vacuum distillation. | Sintered TiO₂ cathode former, CaCl₂ electrolytic pot, anode-gas handling. |
| Energy and complexity | Multi-step, batch retort, vacuum distillation. Industrially proven. | Single electrolytic step once the cathode is formed. Higher temperature, salt-purity sensitive, limited small-scale industrial precedent. |
| Failure modes | TiCl₄ is moisture-sensitive and corrosive. Magnesium inventory must be maintained. | Salt contamination, cathode integrity, carbon contamination of the metal from the anode. |
| Redundancy value | High while the magnesium pot is available. Low if magnesium production is down. | Independent of the Mg/Cl₂ loop. Depends on CaCl₂ purity and pot availability. |

**Selection.** Kroll is the primary path. It re-uses the magnesium pot, the chlorine return, and the chlorinator class already required for aluminum. FFC Cambridge is retained as a documented cold spare (vessel envelope reserved, not a hot parallel train). The grit rate will not support two simultaneous trains at useful capacity, and the extra containment and energy load do not improve closure.

## MO_CELL — hydrogen reduction versus molten-salt electrolysis

| Factor | Precipitation + H₂ reduction | Molten-salt electrolysis |
|--------|------------------------------|---------------------------|
| Chemistry | Molybdenum cut from post-EW liquor, calcined to MoO₃, then staged hydrogen reduction to metal powder. | Molybdate or chloride dissolved in a chloride melt. Metal deposited at the cathode. |
| Fit to existing loops | Poor. Competes directly with the methanol hydrogen allocation. Collected H₂ is already marginal. | Good. Same class of pot already used for Al, Mg, and Ca. No hydrogen demand. Anode gas returns to existing headers. |
| New equipment | Precipitation or extraction tanks, multi-stage hydrogen reduction furnace, powder handling. | One additional molten-salt pot, or campaign use of an existing pot geometry. |
| Energy and complexity | Furnace is straightforward but hydrogen-limited. | Higher temperature and salt management, but consistent with the rest of the metal block. |
| Failure modes | Hydrogen shortage stops the train. Powder can be pyrophoric. | Salt purity, current efficiency, anode-gas handling. |

**Selection.** Molten-salt electrolysis is the primary path. It avoids the scarce hydrogen stream and stays inside the molten-salt block the plant already operates. Hydrogen reduction is retained in the duty note as a fallback study only if a future hydrogen surplus is deliberately sized for it. It is not a second designed train.

## Redundant pathways

- TI_CELL: asymmetric redundancy only. Kroll is primary. FFC is a cold alternate if the magnesium pot is unavailable for an extended period. Both are not built as hot, parallel trains.
- MO_CELL: single path. Molten-salt electrolysis is clearly better integrated. Hydrogen reduction remains a documented study, not a designed train.
- The plant’s existing spare philosophy (hot-swappable membranes, parallel pots) does not require full dual process trains for these two metals. The binding requirement is on-site production, not dual independent routes.

## Status

Locked in notes/TI_MO_DUTIES.md Rev B and graph Rev J (2026-10-16).  
TI_CELL: Kroll primary, FFC cold spare, Cl₂ return to CRU, MgCl₂ return to existing Mg pot.  
MO_CELL: molten-salt primary, anode-gas return to CRU. H₂ reduction is not a baseline edge.  
Rates unset pending assays.

1. Lock Kroll as primary and FFC as cold spare in the TI_CELL duty.
2. Add the chlorinator and TiCl₄ handling as named sub-duties under TI_CELL. Note the MgCl₂ return to the existing magnesium pot and the Cl₂ return to the CRU.
3. Lock molten-salt electrolysis as primary for MO_CELL. Remove any baseline assumption of a hydrogen-reduction edge.
4. Leave rates unset until a grit assay and a late-cascade liquor assay exist.

## References

- notes/TI_MO_DUTIES.md (Rev A process options)
- notes/BINDING_REQ_2026-10-16.md
- COMPLETION_DUTIES.md and notes/unit_duties.md (existing molten-salt block)
- plant_flow_graph.json revision I
