# AL_POT fabrication

Class: cell; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 800×800×1600 mm;
service line: service molten AlCl3-(NaCl-KCl) electrolysis cell, 700 C; chemistry 2 AlCl3 -> 2 Al + 3 Cl2; feed_kg_d 49.42; metal_kg_d 10; cl2_kg_d 39.42;

Internals: issued mfg model BOM (1 internals part row): "5,Hood with gas offtake DN150 and dip leg,1,"CS hood, Hastelloy C-276 dip leg",39.4192 kg/d Cl2 dock export at" [models/mfg/AL_POT/bom.csv]
Material: Graphite cell liner (design allowance 10 mm on the wetted faces), graphite anodes at j 0.5 A/cm2 (A-M-282 class), steel cathode bus above the melt with copper busbar frame-isolated to AQS-STD-002 section 11; 90 % alumina brick + ceramic-fibre backup lining; mild-steel outer shell below the liner. (continues on the duty sheet)

Nozzles: 6 process connections per docs-authority/nozzles/AL_POT.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
