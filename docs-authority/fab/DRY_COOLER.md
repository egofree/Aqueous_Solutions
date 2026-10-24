# DRY_COOLER fabrication

Class: dry_cooler; sector HEAT. Study route. Not stamped.
Envelope: not booked on the duty sheet - the physical build size is the unit task 10-11 scope;
service line: see the duty sheet section 1 basis

Internals: duty sheet: "with margin. 3. Material. Copper-tube, aluminium-fin air coil with galvanized-steel casing; epoxy-coated heade" [docs-authority/duties/DRY_COOLER.md]
Material: Copper-tube, aluminium-fin air coil with galvanized-steel casing; epoxy-coated headers; the rejection loop is the house HDPE-class closed water loop. Basis: 12 kW dry rejection at the 37.8 C design bulb (graph params; A-M-244): air-sided fin-coil construction is the air-cooled exchanger class (PERRY9_HEAT); the loop side follows the issued water-loop families (AQS-STD-002 section 12.1). (continues on the duty sheet)

Nozzles: 3 process connections per docs-authority/nozzles/DRY_COOLER.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Machine build: frame, coil/air side and standard rotating parts; no contacting process internals (internals register below).
2. Connections and coil/media side per the duty sheet and nozzle schedule.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
