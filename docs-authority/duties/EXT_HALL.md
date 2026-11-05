# EXT_HALL

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 85.2290 kW. In: none. Out: none.

2. Size.
- Envelope and loads are solved in the graph (X-PAR-07/X-PAR-08, A-M-104, A-M-112) from the location-neutral bounding climate of AQS-SITE-002 Rev C; a site design re-solves them.
- Electrical, average: lighting 21.48 kW (IECC 2021 C405, 10 % lit), ventilation 36.25 kW (ASHRAE 62.1-2025), envelope service 27.50 kW; total 85.23 kW on the bus.
- Thermal, average: heating 25.61 kW and cooling 150.81 kW after internal gains 30.63 kW and slab edge 1.53 kW (IECC C402 F-factor); heat pumps per ASHRAE 90.1-2025 Table 6.8.1-2, loop pumping 0.00 kW.
- Peak block load: heating 385.3 kW, cooling 340.6 kW at the bounding design temperatures.

3. Material. Steel portal frames on the 6 m grid; insulated metal roof and wall panels to the IECC U-factors; roof framing for LRFD 1.72 kPa (ASCE 7-22: 1.2 x 0.15 kPa PV dead + 1.6 x 0.96 kPa roof live; A-M-105). Steel sections and panels are made in-house (X-MFG-32).

4. Nozzles. None. Electrical feed SF-EXT_HALL at 480 V AC. Air-source heat pumps (D77). GEO_GHEX not coupled.

5. Instruments. Occupant sensors and lighting controls (IECC 2021 C405.2); demand-controlled ventilation on the same zones; space temperature per zone.

6. Relief. Not a pressure system. Roof PV access per IFC 2027 1205.3 / NFPA 1 11.12: 1829 mm perimeter pathway, 1219 mm interior pathways, 16 arrays.

7. Code. Building. Not stamped. NORTH_DOCK opens into EXT_HALL_N; a 6 m truck lane to the hall's north wall is reserved (accepted 2026-10-15). Manufacturing model `models/mfg/EXT_HALL/ext_hall.py` (AQS-PLAN-006).

8. Open items. Bin-hour load calculation on TMY3;  hall programme; egress for the hall (AQS-EGR-001 update under X-STD-01); FreeCAD massing of the extension.
