# SINTER fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL; connected_kW 8; backup_of ROLL; outage_d 2; design_case_kg_d 0.5; T_C 130

Internals: furnace internals per the duty: the 8 kW connected element array for powder sintering at 1300 C (N+1 consolidation of ROLL) with the hot-face liner and retort furniture per duty section 3 [docs-authority/sizing/SINTER.md]
Material: Graphite resistance elements + 95 % alumina muffle under inert/vacuum atmosphere; nickel-free hot zone on a water-cooled steel jacket. Basis: Ti/Mo/Cr powder sinter at 1300 C, press-and-sinter consolidation N+1 of ROLL (graph design): reactive-powder sintering furnaces use inert/vacuum hot zones with graphite or MoSi2 elements (ASM_V7); Ti embrittles in air/N2 at the class (CRC_TI). (continues on the duty sheet)

Nozzles: 3 process connections per docs-authority/nozzles/SINTER.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
