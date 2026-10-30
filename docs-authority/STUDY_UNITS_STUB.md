# Study units: first-principles duty record and current status

Document number: AQS-EQP-STUDY-001  
Revision: G  
Date: 2026-10-30  
Authority: AQS-WTR-001, AQS-EQP-GEO-001, AQS-EQP-FAB-001, AQS-EQP-FAB-PV-001, AQS-EQP-MFG-001 and AQS-MFG-ELC-001 for the units; the plant flow graph `flow_graph/plant_flow_graph.json` for the current duties. Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: the deferred capabilities named as study units and streams in the candidate graph. | 2026-10-01 |
| B | Table of what blocks each study unit from becoming present. | 2026-10-01 |
| C | First-principles duty of the vapour-compression still, mineral balance of REMIN, Carnot-limited band of GEO_ORC, solar cell line steps, and the lithography, blow-mould and electrode-coat units brought into scope. | 2026-10-01 |
| D | Open gaps framed as studies queued toward the minimum viable system. | 2026-10-01 |
| E | First-principles duty of the lithography, blow-mould and electrode-coat units. | 2026-10-01 |
| F | Pointer to the equipment specification gap register AQS-EQ-GAP-001. | 2026-10-01 |
| G | Rewritten to the documentation style guide (AQS-DOC-002). Each unit now states where its current duty is set: the study units were activated on the graph (A-M-287 to A-M-296), the lithography stub was replaced by three tools, and the solar cell line was sized from its tools (A-M-178). The study methods are kept as the record of how the first duties were found. | 2026-10-30 |

## Purpose and scope

This page records how the first duties of a group of units were estimated from first principles, before each unit had its own sizing page, and it states where each unit's current duty is set. The units are the vapour-compression still VCD_TRAIN, the drinking-water remineraliser REMIN, the geothermal organic Rankine cycle GEO_ORC, the lithography tools, the solar cell line SOLAR_PV_CELL, the blow-mould machine BLOW_MOLD and the electrode coating booth ELECTRODE_COAT.

The current duties are not repeated here. They are the values on the plant flow graph and on the sizing pages named in Table 1, and those pages are regenerated with the graph. The figures in sections 2 to 7 are the study values of revision F, kept so that the method behind each first estimate can be checked.

## 1. Current status

Table 1. Where each unit's duty is set now

| Unit | Status on the graph | Duty set by |
| --- | --- | --- |
| VCD_TRAIN | Present, with its feed and product flows solved | `docs-authority/sizing/VCD_TRAIN.md` (A-M-149) |
| REMIN | Present, activated from the study at the drinking-water basis of section 3 | the graph note on REMIN (A-M-287 to A-M-296) |
| GEO_ORC | Placeholder: no power is claimed until the ground survey of section 4 is done | this page, section 4 |
| LITHO_COAT, LITHO_ALIGN, LITHO_DEV | Present: the three tools replaced the retired LITHO_STUB | `docs-authority/sizing/LITHO_COAT.md`, `docs-authority/sizing/LITHO_ALIGN.md` and `docs-authority/sizing/LITHO_DEV.md` (A-M-287); the resist is made on site (A-M-432) |
| SOLAR_PV_CELL | Present, sized from its in-house tools | `docs-authority/sizing/SOLAR_PV_CELL.md` (X-MFG-38, A-M-178) |
| BLOW_MOLD | Present, activated from the study at its campaign basis | `docs-authority/sizing/BLOW_MOLD.md` |
| ELECTRODE_COAT | Present, activated from the study at its campaign basis | `docs-authority/sizing/ELECTRODE_COAT.md` |

A study duty never made a unit present by itself. Each unit became present when its tools, its feed and its place on the graph were set, and the graph note on each unit names the assumption that did so.

## 2. Vapour-compression still

The still recovers distillate from treated grey water and clean condensates. The distillate is not drinking water until it has passed the ultrapure-water polish and REMIN (AQS-WTR-001).

The method is the compressor work of single-effect mechanical vapour compression. The ideal specific work is about the latent heat times the temperature lift divided by the absolute evaporator temperature. The actual specific energy is the ideal work divided by the compressor and motor efficiencies, plus a small pump share. Published single-effect machines use about 10 to 25 kWh per cubic metre of product, the lower end for low salinity and a small lift.

Table 2. Study values of revision F for the still

| Quantity | Study value |
| --- | --- |
| Feed | about 0.110 m3/d |
| Temperature lift | 4 to 8 K |
| Evaporator temperature | 70 to 100 C |
| Ideal work at mid values | about 33 kJ/kg, or 9.2 kWh/m3 |
| Combined efficiency of a small machine | 0.5 to 0.7 |
| Specific energy | 14 to 20 kWh/m3 |
| Average electrical duty | 0.06 to 0.09 kW |

The study replaced an earlier allocation of 5 to 10 kW for fresh water. The current still is sized on the larger solved feed of the graph at the midpoint of the same specific-energy band (A-M-149).

## 3. Remineraliser

REMIN doses calcium, magnesium and potassium into drinking water after the polish. It does not draw the farm nutrient dose, which serves a separate path.

The World Health Organization gives no single mandatory value, but its guidance on demineralised and desalinated water discusses about 20 to 30 mg/L of calcium and about 10 mg/L of magnesium as desirable for remineralised drinking water. Potassium has no limit and comes mainly from the diet.

Table 3. Study mineral balance of revision F

| Case | Water | Calcium at 25 mg/L | Magnesium at 10 mg/L | Potassium at 5 mg/L |
| --- | --- | --- | --- | --- |
| Drinking water only | 10 L/d | 0.25 g/d | 0.10 g/d | 0.05 g/d |
| All potable water | about 130 L/d | 3.25 g/d | 1.3 g/d | 0.65 g/d |

The study default remineralises the drinking stream only. The salts are grams a day, taken from the plant's own salt inventory, and the electrical load is the metering pumps and the ultraviolet lamp.

## 4. Geothermal organic Rankine cycle

GEO_ORC would turn surplus ground-loop heat into electricity after the heat pump has served the life-support heat duty. Its power is the cycle efficiency times the surplus heat. The Carnot limit between the source and sink temperatures caps the efficiency, and binary cycles on low-temperature sources reach about 5 to 12 % in published work.

The ground loop of the reference site is shallow and close to ambient temperature, and the heat pump uses it first, so the surplus is about zero. The study therefore claims no power: 1 kW would need a surveyed surplus of about 10 kW of heat at 10 % efficiency. The unit stays on the graph as a placeholder so that the power path is tracked, and the open work is the ground survey ST-ORC-01 of the source temperature and the surplus heat. A fixed power figure for this unit is not allowed until that survey is done.

## 5. Lithography tools

The study of revision E sized the coat, align and develop steps for 1 to 5 wafer starts a day on 150 mm wafers. It took about 2 mL of resist dispensed per wafer, at about 10 % solids, and an average electrical duty of about 0.1 kW, because the spin coater, the bake plates and the aligner stand idle most of the day.

The single stub LITHO_STUB has since been retired. The three tools LITHO_COAT, LITHO_ALIGN and LITHO_DEV carry their own duties at the plant's wafer starts (A-M-287). The resist is no longer an estimate: it is sized from the coats per day and made on site by RESIST_SYN, and the spent resist returns to the solvent still (A-M-432).

## 6. Solar cell line

The steps are alkaline texturing, phosphorus emitter diffusion, glass etch, silicon nitride antireflection coating, screen-printed contacts with a firing furnace, and the current-voltage test. The texturing, diffusion and etch steps used standard practice, and the study held the coating and firing furnaces as open until their tools were designed.

That work closed on 2026-10-16. The cell line is now sized from its in-house tools (X-MFG-38, A-M-178). The cell rate is now the replacement need of the roof array, and the wafers come from the plant by a selectable route (A-M-437).

## 7. Blow-mould machine and electrode coating booth

The blow-mould study took a polymer extruder of 2.2 to 4 kW with the clamp and blowing air, run in a campaign of 2 to 4 hours a day, for an average of about 0.5 kW. It refused the 14 to 28 kW averages of industrial extrusion blow-moulding lines as a basis, because those machines run continuously at far higher output.

The electrode coating study chose non-precious conductive coats of carbon, nickel or passivated stainless steel for the replaceable electrodes. Mixed ruthenium and iridium oxide anodes stay deferred. The booth exhaust and the infrared cure oven, run about 2 hours a day, gave an average of about 0.3 kW.

Both units are now present at their campaign duties, and the basis is in their sizing pages.

## 8. Equipment specification

The equipment specification gap register AQS-EQ-GAP-001 holds the maker and model shortlists for underspecified units. A commercial interim choice is never the final authority for a present unit.

## 9. References

- DESWARE, Mechanical Vapor Compression Distillation, sample chapter D08-053: ideal work and small-machine efficiencies.
- World Health Organization, Nutrients in Drinking-water (WHO/SDE/WSH/05.09), and Safe Drinking Water from Desalination (WHO/HSE/WSH/11.03).
- Hettiarachchi and co-authors, Energy: organic Rankine cycle efficiency on low-temperature geothermal sources.
- Cengel and Boles, Thermodynamics: An Engineering Approach: the Carnot efficiency.
- AQS-AUD-001 sections 10.4 and 11; AQS-REQ-KW-001; AQS-BOM-SC-001 section 3.
