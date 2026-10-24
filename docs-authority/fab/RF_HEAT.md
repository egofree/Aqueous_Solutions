# RF_HEAT fabrication

Class: furnace; sector FOUNDRY. Study route. Not stamped.
Envelope: Envelope 1000×1000×1500 mm;
service line: service RF preheat/hold unit, N+1 at equal melt duty of IND_MELT; connected_kW 5; backup_of IND_MELT; outage_d 2; crucible_kg 10; freq_kHz 1

Internals: sizing sheet: "connected_kW=5.0, backup_of=IND_MELT, outage_d=2.0, crucible_kg=10.0, freq_kHz=100-400 | envelope 1000 x 1000 " [docs-authority/sizing/RF_HEAT.md]
Material: Clay-graphite crucible + ceramic-fibre hot face + 4 mm CS casing (same melt-shop lining class as IND_MELT); the RF coil enclosure keeps the water-cooled copper coil out of the melt space. Basis: RF preheat/hold at equal melt duty of IND_MELT, 100-400 kHz through-coil (graph design, A-M-282): same refractory-chemistry environment as IND_MELT (SCHACHT2004, INDUCT_SOCX, CRC_* melting points). (continues on the duty sheet)

Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Shell and hearth: plate or welded vessel per the section 3 material once selected; hot- or wet-face hardware is the AQS-STD-002 family material of the streams it touches.
2. Working parts: the electrode/hearth/bottle hardware named on the sizing and duty sheets; electrode arrays stay per the internals register disposition below.
3. Connections: per the scheduled nozzles when they exist; nothing invented here.
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
