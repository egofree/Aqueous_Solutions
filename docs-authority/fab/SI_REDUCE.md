# SI_REDUCE fabrication

Class: furnace; sector GLASS. Study route. Not stamped.
Envelope: Envelope 1200×1000×1600 mm;
service line: duty carbothermic silicon reduction for the PV cell line (SOLAR_PV_CELL draws 1.8 kg/d Si); si_kgd 1.8; sio2_kgd 3.85; char_kgd 1.924.

Internals: reduction furnace internals per the sizing masses: the carbothermic charge sequence (3.85 kg/d quartz + 1.924 kg/d char -> 1.8 kg/d Si) in the retort with the hot-face liner per duty section 3 [docs-authority/sizing/SI_REDUCE.md]
Material: Graphite hot-face carbothermic-reduction furnace with alumina brick backup and a mild-steel casing; dry char and silica-class feed handling; the hot face stays dry (M7). Basis: GLASS-sector furnace unit with solids-only edges (CHAR_TO_SI on the graph design day at zero): the construction material is issued here at the lining level (SCHACHT2004 ch. (continues on the duty sheet)

Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: per the scheduled nozzles when they exist; nothing invented here.
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
