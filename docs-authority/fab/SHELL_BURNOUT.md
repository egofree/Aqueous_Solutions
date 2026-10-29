# SHELL_BURNOUT fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service flash-dewax + shell fire furnace, 900 C; shell_kg_d 8; wax_reclaim_kg_d 1.8; burned_wax_kg_d 0.2; T_C 900; kW 0.25; condenser wax co

Internals: issued mfg model BOM (1 internals part row): "2,Ceramic-fibre hot face,1,ceramic-fibre board 128 kg/m3,110.0,make,design lining; SCHACHT2004 class" [models/mfg/SHELL_BURNOUT/bom.csv]
Material: Alumina-silica kiln hot face + castable hearth, 80Ni-20Cr elements, mild-steel casing; 304L wax condenser on the condensate leg. Basis: flash dewax + shell fire at 900 C (graph design; A-M-281): lining class per SCHACHT2004 ch. 4/13; element class to 1100 C per ASM_V1; condensate is recovered wax (ULLMANN_WAX). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). (continues on the duty sheet)

Nozzles: 7 process connections per docs-authority/nozzles/SHELL_BURNOUT.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
