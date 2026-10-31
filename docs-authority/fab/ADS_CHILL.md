# ADS_CHILL fabrication

Class: adsorption_chiller; sector HEAT. Study route. Not stamped.
Envelope: Envelope 700×500×1200 mm;
service line: duty silica gel-water adsorption chiller: 5 kW drive at 65 C -> 2.25 kW chilled at 12 C, 7.25 kW rejected; chilled_kw 2.25; cop_thermal 0.45

Internals: issued mfg model BOM (1 internals part row): "x 500 x 1200 mm,1,304L adsorber shells with silica-gel adsorbent beds and 316L chilled-water coils and headers" [models/mfg/ADS_CHILL/bom.csv]
Material: 304L adsorber shells with silica-gel adsorbent beds and 316L chilled-water coils and headers; PP-H water legs on the P5 house water family; steel frame. Basis: silica gel-water adsorption chiller, drive 65 C, chilled 12 C (graph node params; A-M-239/240 COP class): the silica gel-water chiller drives at 55-90 C (WANG2006_ADS); bed shells are sealed vacuum-grade vessels. (continues on the duty sheet)

Nozzles: none scheduled yet (unit task 04); route carries the connections once scheduled

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Machine build: frame, coil/air side and standard rotating parts; no contacting process internals (internals register below).
2. Connections and coil/media side per the duty sheet and nozzle schedule.
3. Connections: per the scheduled nozzles when they exist; nothing invented here.
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
