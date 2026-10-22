# ADS_CHILL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Node params (AQS-PAR-001): kW_c 5; derated_kW_c 3.5; COP_c 0.45; drive_C 65; recool_C 30; chilled_C 12; season summer; drive_kW_th 5; displaced_kW_e 1.5.
- Basis (graph node): AQS-HEAT-STUDY-002 Rev A 2026-10-18 §10.2 (A-M-239, A-M-240): vendor class 0.4-0.6 COP_c at 55-90 C (InvenSor/Mayekawa class; Wang & Oliveira 2006); building cooling 4.5 kW_c class, compression chiller draw 1.5 kW_e at COP 3.0 stays as N+1.

3. Material. 304L adsorber shells with silica-gel adsorbent beds and 316L chilled-water coils and headers; PP-H water legs on the P5 house water family; steel frame. Basis: silica gel-water adsorption chiller, drive 65 C, chilled 12 C (graph node params; A-M-239/240 COP class): the silica gel-water chiller drives at 55-90 C (WANG2006_ADS); bed shells are sealed vacuum-grade vessels. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 13X zeolite bed if the drive temperature class climbs above 90 C (cost up, a different duty class). seal integrity is the durability item, not corrosion; the chilled/cooling water side stays on the house water materials. (X-MAT-22)

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07).
