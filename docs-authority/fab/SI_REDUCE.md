# SI_REDUCE fabrication

Class: furnace; sector GLASS. Study route. Not stamped.
Envelope: Envelope 1200×1000×1600 mm;
service line: duty carbothermic silicon reduction for the PV cell line (SOLAR_PV_CELL draws 1.8 kg/d Si); si_kgd 1.8; sio2_kgd 3.85; char_kgd 1.924.

Internals: reduction furnace internals per the sizing of the silicon route (flow_graph/param/si_refine.py design): the carbothermic charge of quartz ore and pyrolysis char in the retort with the hot-face liner per duty section 3; the charge rates are written on the graph by the silicon-route stage [docs-authority/sizing/SI_REDUCE.md]
Material: Graphite hot-face carbothermic-reduction furnace with alumina brick backup and a mild-steel casing; dry char and silica-class feed handling; the hot face stays dry (M7). Basis: GLASS-sector arc furnace reducing quartz ore with char (IA-QUARTZ-MU, CHAR_TO_SI, sized by flow_graph/param/si_refine.py, A-M-472): the construction material is issued at the lining level (SCHACHT2004 ch. (continues on the duty sheet)

Nozzles: 10 process connections per docs-authority/nozzles/SI_REDUCE.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
