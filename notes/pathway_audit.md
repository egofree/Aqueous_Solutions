# Pathway audit

Document number: AQS-AUDIT-001
Revision: A
Date: 2026-10-09
Authority: graph Rev Y, commit 0a2cfe8. Not a PE stamp. Not a construction issue.

## Mass

No present mass node is off by more than 0.05 kg/d. Boundary export is zero. Nineteen edges are placeholder. That close is not a design.

These returns were added to make the books match. They are not sized equipment:

- Leach offgas to the NOx scrubber, 189 kg/d. No nozzle, no blower, no composition.
- Leach vent to the flue knockout, 136 kg/d. Same.
- Dissolved gas from the leach to the cold box, 13 kg/d. No stripper.
- Scrubber carbon to the board mill, 1.65 kg/d. No filter, no analysis.
- Methanol cell air, 2.68 kg/d, and zero exhaust. A cell that consumes fuel has an exhaust. The zero is the balance, not the machine.

The ionic liquid in the pretreat is not copied. The 25 °C, 2.0 V, 30 min duty is the thesis summary. There is no vessel, no electrode area, and no solvent inventory.

## Energy

The energy layer is open. The largest gaps, kW:

| Unit | Gap |
|---|---|
| PV array | −27.9 |
| Leach | +15.9 |
| Organic Rankine | +11.8 |
| Boundary | +7.2 |
| Grow bed | +5.0 |
| Fuel cell | −4.6 |
| EW-1 | −4.6 |
| Glass digest | +4.2 |
| Habitation | +3.0 |

A positive gap is power arriving with nowhere to go. A negative gap is a load with no feed on this layer. GEO_ORC is the one placeholder node.

## What is not a design

One hundred twenty present nodes have no duty, no note, and no function. The farm units added in Rev P–Y are rates and a kilowatt number:

| Unit | What exists | What a build needs |
|---|---|---|
| Animal pen | 1.8 kg/d feed | Headcount, stall, water, ventilation |
| Digester | 0.4 kW | Volume, HRT, temperature, gas holder |
| Electromethanogenic cell | 1.0 V, 0.5 kW | Electrode area, current density, cathode alloy |
| Hydrothermal carbonizer | 0.6 kW | Volume, temperature, pressure, residence time |
| Ligno pretreat | 25 °C, 2.0 V, 30 min | Vessel, solvent holdup, electrode gap |
| Board mill | 1 kW | Press load, dryness, sheet size |
| Cold box | 77–90 K, 18 kW | Column diameter, stage count, exchanger duty, insulation |
| Noble-gas receivers | circulation slips | Inventory mass, cylinder rating, valve |

Wet-bench peroxide, ammonia, and hydrofluoric acid have a source edge and no generator. Phosphoric acid has no source.

## 3D models

Present as FreeCAD or OpenSCAD: leach CSTR, EW cell and cascade, wet line, hopper, shredder, grow bed, digester shell, CRU, fractionator, cold-box shell, zinc-bromine skid, wet bench, burnout rotary, vibratory split. Those are envelopes or fitouts, not fabrication models. Nozzle schedules exist for the CSTR and the life headers. They are not tied to Rev Y.

Not modeled: animal pen, hydrothermal carbonizer, electromethanogenic cell, ligno pretreat, board mill, noble-gas receivers, greenhouse enclosure, NOx scrubber as a vessel, baghouse, methanol cell.

## Layout

The placement report is graph Rev K. The graph is Rev Y. Eight units were skipped and three moves were refused at Rev K. Nothing in Rev P–Y has a coordinate. The farm block, the cold box, and the noble-gas receivers are not on a slab.

## Not constructable yet

A unit is constructable when it has a vessel, a material, a nozzle, a duty, and a coordinate. The leach CSTR and the EW cell are the closest. The farm block and the cold-box internals are not.
