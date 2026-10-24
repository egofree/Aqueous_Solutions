# EXTRUDE fabrication

Class: press; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1500×800×1500 mm;
service line: machine horizontal profile press, N+1 former of ROLL; connected_kW 15; backup_of ROLL; outage_d 2; press_t 50; container_mm 60.

Internals: duty sheet: "3. Material. H13 extrusion die + tool-steel container liner on a 50 t press (graph design press_t). Basis: hor" [docs-authority/duties/EXTRUDE.md]
Material: H13 extrusion die + tool-steel container liner on a 50 t press (graph design press_t). Basis: horizontal profile press N+1 of ROLL (graph design): hot-work die steel class per ASM_V1 / DIETER1988. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: billet preheater induction sleeve if the profile class moves hot (a separate duty entry). (continues on the duty sheet)

Nozzles: 4 process connections per docs-authority/nozzles/EXTRUDE.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Machine build: welded frame plus standard drivetrain parts; sheet, plate and bar stock bought to the family standards (AQS-INV-004/006/007 desk packages).
2. Tooling and working parts per the duty sheet size line; the full part set is the unit task 10-12 deliverables (CadQuery model, real BOM).
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
