# EXPANDER work order

Plan: AQS-PLAN-006 Rev A. Graph Rev BH. Study. Not a PE stamp.
Status: M2. The source builds and exports one closed solid. Not accepted (M3): no drawings.

| Item | State |
| --- | --- |
| W1 Source | `expander.py`, CadQuery 2.8.0, cadquery-ocp 8.0.1, Python 3.13. Builds headless from `params.json` |
| W2 Parameters | `params.json`. Graph node: size 600 × 400 × 500 mm, design 550 kPa, relief 3.6 mm to CRYO_ASU, internals none, rho 11.61 kg/m³, shaft 614.4 W. Duty section 2: bore 50, stroke 80, 600 rpm. Duty section 4: N1 −Y, N2 +Y, 250 mm height. Every other dimension is in `assumptions` |
| W3 Internals | Node says none. Piston, connecting rod, shaft, and flywheel are drawn as machine parts, not process internals |
| W4 Nozzles | N1 and N2 drawn at DN15 because the bore is not calculated. Relief boss on +Z with a 3.6 mm bore |
| W5 Fasteners | `fasteners.csv`. Sizes are assumptions. Crankcase holes not drawn |
| W6 Materials | 316L throughout, corrosion allowance 0 mm, from duty section 3 |
| W7 Drawings | Not made. Needs a machine with FreeCAD TechDraw |
| W8 Exports | `export/expander.step`, 13 parts. `export/expander.stl`, ASCII, 2472 facets: the parts fused into one valid solid, closed and manifold (one outer shell, two internal cavities), 8.17 L. Stored through Git LFS. The `cad/stl/EXPANDER.stl` registry envelope was withdrawn when the unit retired from the graph |
| W9 BOM | `bom.csv`, generated, mass from 7.99 g/cm³ |
| W10 Route | F-MACH. Cut and drill baseplate, fabricate crankcase box, bore and hone cylinder, turn piston, shaft, and flywheel, weld nozzle lines, pressure test the cylinder and head at 1.3 × 550 kPa (assumption, test factor not on the graph) |
| W11 Self-copy | Not a shop tool. Lathe, mill, and welder on site make every part; the cylinder bore needs a hone that is not on the shop list |
| W12 Holds | Isentropic efficiency 70 % assumed. Cylinder wall, crankcase, connecting rod, flywheel (240 mm), and baseplate proportions are assumptions. A-P wall check: t = P·r / (S − 0.6P) = 0.55 × 25 / (115 − 0.33) = 0.12 mm required at an assumed allowable 115 MPa; 10 mm drawn. Valve gear and seals are not drawn |
