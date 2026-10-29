# CAST_LINE fabrication

Class: caster; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1500×800×1500 mm;
service line: machine permanent-mould cast line; pour_kg_d 3; moulds 2; table_L_mm 700.

Internals: issued mfg model BOM (2 internals part row): "section 3: steel backing platens around the graphite hot faces (DIETER1988 tool class) 4,"Permanent-mould" [models/mfg/CAST_LINE/bom.csv]
Material: Graphite permanent moulds with steel backing platens (Cu pour, melt 1085 C per CRC_CU); graphite launder; steel tilt table. Basis: permanent-mould Cu casting at the 3 kg/d pour (graph design; A-M-199 class): graphite is the standard Cu-mould hot face at the melt temperature and is chemically indifferent to the melt (SCHACHT2004 ch. 8; DIETER1988 tool class for the platens). (continues on the duty sheet)

Nozzles: 6 process connections per docs-authority/nozzles/CAST_LINE.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
