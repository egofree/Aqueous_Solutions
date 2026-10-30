# MG_POT fabrication

Class: cell; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 800×800×1600 mm;
service line: service molten MgCl2 electrolysis cell (Kroll Mg recycle), 700 C; chemistry MgCl2 -> Mg + Cl2; feed_kg_d 1.989; metal_kg_d 0.5078; cl2_kg_d 

Internals: issued mfg model BOM (3 internals part row): "step 1; duty section 3 CS outer shell below the liner, 700 C, dry outside the lining; envelope per" [models/mfg/MG_POT/bom.csv]
Material: Graphite anodes, steel cathode plates, mullite-class alumina-silica refractory cell lining in a mild-steel shell; skim launder kept graphite-wetted. Basis: molten MgCl2 at 700 C: the industrial MgCl2-electrolysis pot class is graphite anodes + steel cathodes (ULLMANN_MAGNESIUM); alloy containment loses Cr to the melt (DING2021_ENG, KRUIZENGA2012); backup lining per SCHACHT2004. (continues on the duty sheet)

Nozzles: 10 process connections per docs-authority/nozzles/MG_POT.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
