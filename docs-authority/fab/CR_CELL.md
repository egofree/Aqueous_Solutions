# CR_CELL fabrication

Class: cell; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 800×800×1600 mm;
service line: service Cr(III) molten-salt electrolysis cell with carbochlorination loop, 700 C; chemistry Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr

Internals: issued mfg model BOM (3 internals part row): "step 1; duty section 3 CS outer shell below the liner, 700 C, dry outside the lining; envelope per" [models/mfg/CR_CELL/bom.csv]
Material: Graphite liner and graphite anode for the carbochlorination melt (CrCl3 wetted), dry CO/CO2/Cl2 headspace; 90 % alumina brick backup in a mild-steel shell. Basis: Cr2O3 + 3C + 3Cl2 carbochlorination at 700 C with an internal anode-gas loop (graph design): the bed is a dry hot face (M7); the melt physics is the pot-cell class (DING2018_CL_REVIEW, KRUIZENGA2012). (continues on the duty sheet)

Nozzles: 7 process connections per docs-authority/nozzles/CR_CELL.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
