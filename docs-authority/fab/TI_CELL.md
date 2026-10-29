# TI_CELL fabrication

Class: cell; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 800×800×1600 mm;
service line: service Kroll chlorinator + Mg-reduction retort train; chemistry TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL)

Internals: duty sheet: "carbochlorinator at 800 C with graphite hot face; TiCl4 take-off cooled through a 316L condensation train;" [docs-authority/duties/TI_CELL.md]
Material: Alumina-brick-lined carbochlorinator at 800 C with graphite hot face; TiCl4 take-off cooled through a 316L condensation train; Kroll reduction retort 310S (25Cr-20Ni) with a graphite crucible insert at 900 C; molten MgCl2 return through graphite/Ni-200 launder. (continues on the duty sheet)

Nozzles: 15 process connections per docs-authority/nozzles/TI_CELL.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
