# EXT_HALL

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0.000 kg/d. Mass out 0.000 kg/d. Electrical duty 90.46 kW (SF-EXT_HALL from SOL_ARK_60K). Single-storey conditioned extension of 31,860 m2 east (EXT_HALL_E) and north (EXT_HALL_N) of the base plate. It exists so that the roof carries the full PV array at 2.0 x requirement (X-PAR-09, D75; X-PAR-07, owner decisions 2026-10-15: option A, conditioned). Sized by `flow_graph/param/solver.py` roof_close.

2. Size. Building 234 x 138 m on the 6 m bay grid (39 x 23 bays); extension 31,860 m2; eave 6 m. Loads (X-PAR-08, A-M-104, A-M-112), heating and cooling split by NOAA DFW degree days (mean heating dT 3.46 K, cooling 4.38 K):
- Lighting 28.04 kW: 8.8 W/m2 (IECC 2021 Table C405.3.2(1)) lit 10 % of hours (IECC 2021 C405.2.1).
- Fans 11.95 kW: outdoor air 0.30 L/(s m2) (ASHRAE 62.1-2019), 9558 L/s at 1.25 W/(L/s) (ISO 16798-3 SFP 3).
- Heating and cooling: conduction (roof U 0.199, walls U 0.534 on 744 m x 6 m, IECC 2021 C402), outdoor air, slab edge F 1.264 W/(m K) in the heating season (3.25 kW thermal; IECC C402 F-0.73), internal gains of lighting and fans (39.98 kW) offsetting heating and adding to cooling. Average thermal: heating 55.7 kW, cooling 111.1 kW.
- Ground-source heat pumps (adopted, X-PAR-08): COP 3.2 heating / 4.13 cooling (ASHRAE 90.1-2019 Table 6.8.1-2, ISO 13256-1); loop pumping 37 W/kW (KAVANAUGH2014) = 6.17 kW. Peak block load 494 kW heating at -5 C design (ASHRAE 2021 Fundamentals, to verify). Bore field 227 bores x 120 m (27.2 km at 55 m/kW, KAVANAUGH2014) on 6 m spacing, 8172 m2, drilled under the hall slab; GEO_GHEX params.hall_field.
- Comparison under the same model: air-source (COP 3.3 / 3.22) 91.34 kW, converged 32,364 m2 (31 x 29 bays); ground-source 90.46 kW, 32,292 m2. Ground-source is adopted by the X-PAR-08 rule (smaller footprint), margin 72 m2 (0.2 %).

3. Material. Steel portal frames on the 6 m grid; insulated metal roof and wall panels to the IECC U-factors; roof framing for LRFD 1.72 kPa (ASCE 7-22: 1.2 x 0.15 kPa PV dead + 1.6 x 0.96 kPa roof live; A-M-105). Steel sections and panels are made in-house (X-MFG-32).

4. Nozzles. None. Electrical feed SF-EXT_HALL at 480 V AC. Ground-source heat pumps on a dedicated bore field under the hall (X-PAR-08); separate from the Q4 GEO_GHEX loop.

5. Instruments. Occupant sensors and lighting controls (IECC 2021 C405.2); demand-controlled ventilation on the same zones; space temperature per zone.

6. Relief. Not a pressure system. Roof PV access per IFC 2021 1205.3 / NFPA 1 11.12: 1829 mm perimeter pathway, 1219 mm interior pathways, 15 arrays.

7. Code. Building. Not stamped. NORTH_DOCK opens into EXT_HALL_N; a 6 m truck lane to the hall's north wall is reserved (accepted 2026-10-15).

8. Open items. Bin-hour load calculation on TMY3; thermal response test for the bore field; hall programme; egress for the hall (AQS-EGR-001 update under X-STD-01); FreeCAD massing of the extension.
