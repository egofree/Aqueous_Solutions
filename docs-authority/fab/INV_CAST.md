# INV_CAST fabrication

Class: caster; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1500×800×1500 mm;
service line: machine investment casting tilt-pour station; pour_kg_d 2; shell_kg_d 8; molds_per_campaign 8.

Internals: duty sheet: "shell_kg_d 8; molds_per_campaign 8. 3. Material. Graphite crucible tilt-pour + alumina shell as the mould hot " [docs-authority/duties/INV_CAST.md]
Material: Graphite crucible tilt-pour + alumina shell as the mould hot face; steel table and tilt hardware. Basis: investment casting at 2 kg/d castings through the 6-dip shell (graph design, A-M-281): the shell is a refractory hot face (SCHACHT2004); the crucible is the melt-contact part (DIETER1988). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). (continues on the duty sheet)

Nozzles: 6 process connections per docs-authority/nozzles/INV_CAST.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
