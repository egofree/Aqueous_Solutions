# Design plan

Document number: AQS-PLAN-001
Revision: B
Date: 2026-10-09
Authority: graph Rev AR. Not a PE stamp.

Phase 1. Energy cut closed. Solar and fuel enter at the curtailment node. Heat leaves at the dry cooler. `loops_closed` is true. Mass nodes remain inside 0.05 kg/d.

Phase 2. The fourteen accounting edges are named transfers: biofilter bleed, leach vent, compost return, bin vents, fish liquor, hopper fines, acetate brine, compost condensate, shop scrap, molt liquor, frass liquor, quaternization brine. Solvent vessels: ethanol still 50 L 78 °C, butanol still 20 L 118 °C, formaldehyde reactor 10 L 600 °C silver, glyoxal 10 L, imidazole 20 L, quaternization 20 L 70 °C, acetate column 10 L. Glass or 316L. No iridium.

Phase 3. Film gutters, mister with 100 µm screen, dual-root channel, 15 m² biofilter, 85 m² azolla bed are nodes. Peanut and sunflower go on the yield sheet at 0.02 kg/m²/day oil seed.

Phase 4. Urine returns iodide to the resin. Store is 2 g. Dose is 0.6 mg/d.

Phase 5. Exclusions. Lithography resist, blow-mold die, electrode coat, photovoltaic cell, and the cold-box expander are not copied. Hydrofluoric acid is fluoride from the leach plus bipolar-membrane acid. Molybdenum and the rare-earth cell stay on the polish cake and the molten-salt cell. Silicon carbide is not copied. Anion-exchange membranes are cast from the solvent train only if the ionic liquid is made. Iridium stays off the anode.

Phase 6. Habitation is four rooms: sleep 16 m², galley 12 m², medical 6 m², wash 6 m². Medical stock is bandage, saline, iodide. No new chemistry.

Phase 7. Plate is 470 m² plus 85 m² azolla, 555 m², 16 bays. The issued 432 m² plate is retired. Placement rebuild is the next solid-model pass. It is not in this revision.

Phase 7 is AQS-PLAN-001 Rev B. Plate is 4 by 4 bays, 24 by 24 m, 576 m2. The 432 m2 plate is retired. Placement report is graph Rev AR. Azolla, film, mister, dual root, struvite, ash, iodide, and the seed bank are placed. Solids are not rebuilt in this pass.

Phase 8 is AQS-PLAN-001 Rev C. Envelopes for the phase 7 units and the solvent stills are in cad/phase8_envelopes.py, millimetres. FreeCAD is not in this environment. The meshes were not compiled. The operator box compiles them.

Phase 9 is AQS-PLAN-001 Rev C. Film, mister, dual root, and azolla are piped. Each line returns what it takes. Nozzles are in docs-authority/PHASE9_INTERFACES.md. Peanut and sunflower are 10 m2 each at 0.02 kg/m2/day.

Phase 10 closes the plan, AQS-PLAN-001 Rev D, graph Rev AT. Stills, peanut, sunflower, and the four rooms are nodes. Each feed has a return. Mass nodes are inside 0.05 kg/d. Not finished here: FreeCAD meshes, and the excluded copy-stoppers (lithography, blow-mold, electrode coat, photovoltaic cell, cold-box expander, silicon carbide). Iridium stays off the anode.
