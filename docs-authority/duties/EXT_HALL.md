# EXT_HALL

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 93.8389 kW. In: none. Out: none.

2. Size. Building 186 x 174 m on the 6 m bay grid (31 x 29 bays); extension 31,932 m2; eave 6 m. Loads (X-PAR-08, A-M-104, A-M-112), heating and cooling split by NOAA DFW degree days (mean heating dT 3.46 K, cooling 4.38 K):
- Lighting 28.10 kW: 8.8 W/m2 (IECC 2021 Table C405.3.2(1)) lit 10 % of hours (IECC 2021 C405.2.1).
- Fans 11.97 kW: outdoor air 0.30 L/(s m2) (ASHRAE 62.1-2019), 9580 L/s at 1.25 W/(L/s) (ISO 16798-3 SFP 3).
- Heating and cooling: conduction (roof U 0.199, walls U 0.534 on 720 m x 6 m, IECC 2021 C402), outdoor air, slab edge F 1.264 W/(m K) in the heating season (3.15 kW thermal; IECC C402 F-0.73), internal gains of lighting and fans (40.07 kW) offsetting heating and adding to cooling. Average thermal: heating 55.4 kW, cooling 111.0 kW. Peak block load 492 kW heating at -5 C design (ASHRAE 2021 Fundamentals, to verify).
- Air-source heat pumps, COP 3.3 heating / 3.22 cooling (ASHRAE 90.1-2019 Table 6.8.1-2). Total 91.34 kW.
- Ground-source was compared (90.46 kW, 32,292 m2, 227 bores x 120 m) and not adopted: owner decision 2026-10-15 (D77), 27 km of drilling for a 0.2 % footprint gain is inside input uncertainty and adds major build complexity.

3. Material. Steel portal frames on the 6 m grid; insulated metal roof and wall panels to the IECC U-factors; roof framing for LRFD 1.72 kPa (ASCE 7-22: 1.2 x 0.15 kPa PV dead + 1.6 x 0.96 kPa roof live; A-M-105). Steel sections and panels are made in-house (X-MFG-32).

4. Nozzles. None. Electrical feed SF-EXT_HALL at 480 V AC. Air-source heat pumps (D77). GEO_GHEX not coupled.

5. Instruments. Occupant sensors and lighting controls (IECC 2021 C405.2); demand-controlled ventilation on the same zones; space temperature per zone.

6. Relief. Not a pressure system. Roof PV access per IFC 2021 1205.3 / NFPA 1 11.12: 1829 mm perimeter pathway, 1219 mm interior pathways, 16 arrays.

7. Code. Building. Not stamped. NORTH_DOCK opens into EXT_HALL_N; a 6 m truck lane to the hall's north wall is reserved (accepted 2026-10-15).

8. Open items. Bin-hour load calculation on TMY3;  hall programme; egress for the hall (AQS-EGR-001 update under X-STD-01); FreeCAD massing of the extension.
