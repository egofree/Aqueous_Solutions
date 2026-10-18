# Build plan

Superseded by `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). This page is kept as history; open work is tracked there only.

Document number: AQS-PLAN-002
Revision: A
Date: 2026-10-10
Authority: graph Rev AX. Not a PE stamp. This is the sequence that makes the plant buildable. Nothing in the present set is excluded.

A unit is buildable when it has a composition on the basis, a nozzle list with location and rating, internals drawn, a mesh, a relief destination, and an instrument that trips. The 204 duty pages do not have these. The work below produces them.

## 1. Basis composition

Every mass edge gets a composition. Minimum: water, acid or base, and the dominant solute, in g/L or mass fraction. The leach liquor, the electrowinning cascade, the polish cells, the oil cuts, the farm water, and the gas headers are the streams that unlock the rest. No unit is resized until its inlet composition is on the edge.

## 2. Nozzle list

Each unit gets a nozzle table. Tag, size, rating, service, and location (which face, height from the tangent). Drain and vent are included. DN from the rate is the start. The location is the missing part. Headers get a line list instead of a nozzle list.

## 3. Internals

Drawn, not described. Electrowinning cell: cathode, edge strip, anode, launder, bus. Leach tank: weir, floor auger, jacket. Scrubber: packing, distributor, demister. Column: trays or packing height. Biofilter: media volume. Still: packing and reflux. The drawing is the acceptance, not the sentence.

## 4. Mesh

One solid per present unit, compiled, not a box where the internals matter. The leach, the nine cells, the cold box, the biofilter, and the stills are first. The six existing STL boxes are replaced by the real envelope. FreeCAD is the compiler. This environment does not have it, so the meshes are produced on the operator box from the envelopes and the internals.

## 5. Checks that are still missing

Electrowinning: faradaic current from the metal actually leaving each cell, against the 25.2 A study figure. Cold box: tray count and a refrigeration balance. Habitation: fixture schedule and a heat load. Energy: a one-line diagram with conductor size and protection. Oil column: stages and reflux from the cuts. Biofilter: the 15 m² already calculated, drawn.

## 6. The fourteen IA-CLOSE edges

Each becomes a vessel or a specified pipe with a tag, or it is deleted. A named transfer with no line size is not finished.

## 7. Code and relief

A pressurized unit gets a design pressure, a relief set at 110%, and a destination that is not the room. An atmospheric unit says so and names the vent. Shop-built is allowed. Unstated is not.

## 8. Order

Composition, then nozzles, then internals, then mesh, then the five checks, then the fourteen edges, then relief. Placement is rebuilt at the revision that has the meshes. The plate stays 24 by 24 m until a unit does not fit.

Acceptance is a unit that a shop can build without asking what the nozzle is or what is inside.

Plan status, graph Rev BA. Composition on the mass edges. Nozzle list with height on every unit. Internals named. EW racks built to the sheet edge. Relief line on the duty pages. One-line, habitation fixtures, and cold-box trays written. IA-CLOSE edges tagged DN25. Meshes are envelopes. FreeCAD is not in this environment.

Meshes for the nine cells are plate racks in cad/stl. Envelope plus one plate per cathode. This is the solid. FreeCAD is not required for these nine.
