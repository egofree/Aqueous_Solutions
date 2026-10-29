# VAC_CAST fabrication

Class: caster; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1500×800×1500 mm;
service line: machine vacuum tilt-pour casting station, N+1 of CAST_LINE; connected_kW 7.5; backup_of CAST_LINE; outage_d 2; design_case_kg_d 3.

Internals: duty sheet: "3. 3. Material. 304L vacuum tilt-pour chamber; graphite crucible + alumina backup; steel table hardware." [docs-authority/duties/VAC_CAST.md]
Material: 304L vacuum tilt-pour chamber; graphite crucible + alumina backup; steel table hardware. Basis: vacuum tilt-pour N+1 of CAST_LINE/CONT_CAST at the 3 kg case (graph design, A-M-283/199): same refractory-chemistry classes as the other melt-shop units (SCHACHT2004, DIETER1988). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). (continues on the duty sheet)

Nozzles: 3 process connections per docs-authority/nozzles/VAC_CAST.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
