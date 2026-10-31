# RES_HEAT fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating; connected_kW 12; backup_of SHELL_BURNOUT/SINTER; outage_d

Internals: furnace internals per the duty: the 12 kW connected resistance element array on the chamber walls and hearth (radiant service at 900 C, N+1 standby of SHELL_BURNOUT/SINTER) with the hot-face liner per duty section 3; hearth furniture at unit tasks 10-12 [docs-authority/sizing/RES_HEAT.md]
Material: Ceramic-fibre module lining + 80Ni-20Cr resistance elements on a mild-steel casing at the 900 C box-furnace class. Basis: resistance radiant reheating, N+1 of SHELL_BURNOUT/SINTER heating at 900 C (graph design): element and lining class to 1100 C per ASM_V1; lining design per SCHACHT2004 ch. 13. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). (continues on the duty sheet)

Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: per the scheduled nozzles when they exist; nothing invented here.
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
