# RF_HEAT fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service RF preheat/hold unit, N+1 at equal melt duty of IND_MELT; connected_kW 5; backup_of IND_MELT; outage_d 2; crucible_kg 10; freq_kHz 1

Internals: open: same hold as task 09: duty section 3 selection pending (AQS-STD-005 section 4); internals cannot be detailed before the material is selected
Material: Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close and, where named, the section 3 material selection lands):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: per the scheduled nozzles when they exist; nothing invented here.
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
