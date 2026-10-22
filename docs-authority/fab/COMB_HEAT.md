# COMB_HEAT fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT; connected_kW 0.05; thermal_kW 30; backup_of IND_MELT; ou

Internals: duty sheet: "FFGAS). 3. Material. Alumina-silica brick + castable crown hot face on a mild-steel shell; 310S burner tube; f" [docs-authority/duties/COMB_HEAT.md]
Material: Alumina-silica brick + castable crown hot face on a mild-steel shell; 310S burner tube; flue path dry above the acid dew point into MET_SCRUB. Basis: tertiary N+1 fuel-fired melt heat (graph design): combustion hot-face class per SCHACHT2004 ch. 10; the fuel class is the plant C5-C10 product (duty section 1); combustion stoichiometry per TURNS2012. (continues on the duty sheet)

Nozzles: 3 process connections per docs-authority/nozzles/COMB_HEAT.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
