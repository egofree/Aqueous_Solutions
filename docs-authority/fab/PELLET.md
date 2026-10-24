# PELLET fabrication

Class: former; sector POLYMERS. Study route. Not stamped.
Envelope: Envelope 1500×800×1500 mm;
service line: machine underwater die-face pelletizer; rate_kg_d 0.2941; pellet_mm 2-4.

Internals: duty sheet: "Material. 316L die plate and cutter hub; UHMW-PE trough liner; PE/PP water trough on the resin-cooling loop; s" [docs-authority/duties/PELLET.md]
Material: 316L die plate and cutter hub; UHMW-PE trough liner; PE/PP water trough on the resin-cooling loop; steel frame. Basis: underwater die-face pelletising at 2-4 mm pellet (graph design AQS-DUTY-073): resin contact is inert polyolefin/fluoropolymer stock - hot-face compatibility passes but the water trough is the abrasion face (DIETER1988 wear class; PERRY9_MAT selection logic). (continues on the duty sheet)

Nozzles: 5 process connections per docs-authority/nozzles/PELLET.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Machine build: welded frame plus standard drivetrain parts; sheet, plate and bar stock bought to the family standards (AQS-INV-004/006/007 desk packages).
2. Tooling and working parts per the duty sheet size line; the full part set is the unit task 10-12 deliverables (CadQuery model, real BOM).
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
