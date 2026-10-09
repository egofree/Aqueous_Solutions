# Design plan

Document number: AQS-PLAN-001
Revision: A
Date: 2026-10-09
Authority: graph Rev AP. Not a PE stamp. This is the sequence. It is not the finished design.

Phase 1. Energy. Size the array to the load plus 20 %. Move the leach surplus and the dry-cooler reject onto a named sink. Close the other eleven energy nodes the same way. Set `loops_closed` only after the mass and energy cuts both pass.

Phase 2. Accounting edges. Replace each `IA-CLOSE` edge with a vessel or delete it. The solvent train is first: ethanol still, butanol still, formaldehyde reactor, glyoxal reactor, imidazole vessel, quaternization vessel, acetate column. Each gets a volume, a temperature, and a material.

Phase 3. Farm hardware. Vessel for the 15 m² biofilter, the film gutters, the mister with the 100 µm screen, the dual-root channel, the struvite settler, and the 550 °C ash burner. Put 85 m² of azolla on the graph. Add peanut and sunflower to the yield sheet.

Phase 4. Iodine. Urine returns to the iodide resin. The 2 g store is the inventory, not the daily feed. Dose stays 0.6 mg/d.

Phase 5. Copy-stoppers. One route each, or an explicit exclusion. Lithography, blow-mold, electrode coat, photovoltaic cell, cold box, wet-bench polymer, titanium cell, hydrofluoric acid, anion-exchange cast, molybdenum, silicon carbide, rare-earth cell. Iridium stays off the anode. A route that needs a bought catalyst is not a route.

Phase 6. Habitation. Room schedule for four people. Medical stock. Iodide recycle. No new chemistry.

Phase 7. Plate and solids. Placement file rebuilt at the current revision. Plate set to 470 m² plus the azolla area. Solids for the units in phases 3 and 4. The issued 432 m² plate is retired.

Acceptance for each phase is a duty with a vessel, a closed cut, and no accounting edge left in its scope.
