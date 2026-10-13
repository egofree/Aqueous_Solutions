# Critical path against the tech tree

Document number: AQS-PLAN-003
Revision: D
Date: 2026-10-12
Authority: graph Rev BH. Tech tree egofree/TechTree. OSE GVCS. Not a PE stamp.

Revision A said the lathe, the mill, and the frame did not exist. The pages now exist: FRAME_SYSTEM.md, POWER.md, LATHE.md, MILL.md, WELDER.md, EW_MODULE.md, FURNACE.md, SILICON.md, ALIGNER.md, ELECTRONICS.md, PV_CELL_MOD.md. The side pages are SIDE_ASSAY.md, SIDE_FARM.md, SIDE_CRYO.md. What is still open is named on those pages, not a missing machine.

The end state is a set of modules that can be arranged to any node on the tech tree, and that can copy themselves. The frame standard is the parameter set in AQS-MOD-001: envelope, tube section, wall, and material. It is not one weldment that later machines bolt to. A lathe bay and a cell bay are two calls. The power connector is common. The envelope is not. The Aqueous plant is a closed mass graph. It is not that set yet.

## Completeness

Closed on paper: mass, energy, a page per unit, and a page per path machine. The frame is parametric. The 48 V shop rail is 20 kW. The farm LEDs are a second rail.

Not closed: the solids are not compiled. FreeCAD is not on this machine. VCD_TRAIN is class vessel. REMIN is class tank. LITHO_STUB, ELECTRODE_COAT, and SOLAR_PV_CELL are class tool. BLOW_MOLD is class forming. Present kg/d edges close on graph Rev BH. mvs_criteria.loops_closed stays false. On-site evidence is not in the repo.

## Critical path

1. Module standard. Frame, power connector, fluid connector, parametric envelope. Months 0-2.
2. Machine tools. Each tool is its own bay from that parameter set. The lathe and the mill are 1200 × 600 × 800. The welder is 800 × 600 × 800. Months 2-6. This is the master key.
3. Electrowinning cell as a module, with the busbar already sized. Months 1-4.
4. Induction furnace module. Months 3-5.
5. Silicon reduction module. Months 5-8.
6. Contact aligner. Months 6-9.

## Side quests

Assay and relief calculation, months 0-2. Farm bay is its own call, 2000 × 1000 × 400, months 2-4. Cold box as its own base, months 4-7. Photovoltaic line after silicon, months 8-12. Electronics bay after the aligner, months 10-16.

A GPU is not on this chart. The tech tree puts that at 50-200 years after machine tools, electricity, and chemistry.
