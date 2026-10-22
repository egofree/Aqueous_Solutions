# CA_POT fabrication

Class: cell; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 800×800×1600 mm;
service line: service molten CaCl2 electrolysis cell, 700 C; chemistry CaCl2 -> Ca + Cl2; feed_kg_d 0.1525; metal_kg_d 0.0551; cl2_kg_d 0.0974; I_A 3.61; 

Internals: issued mfg model BOM (1 internals part row): "5,Hood with gas offtake DN50 and dip leg,1,"CS hood, Hastelloy C-276 dip leg",0.0974 kg/d Cl2 dock export at t" [models/mfg/CA_POT/bom.csv]
Material: Graphite anodes, steel cathode rods carrying the solid Ca deposit to the tap work order; 90 % alumina backup lining + ceramic-fibre in a mild-steel shell. Basis: molten CaCl2 at 700 C (graph design; Ca m.p. (continues on the duty sheet)

Nozzles: 5 process connections per docs-authority/nozzles/CA_POT.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
