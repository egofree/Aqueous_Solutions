# EXT_HALL

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0.000 kg/d. Mass out 0.000 kg/d. Electrical duty 90.01 kW (SF-EXT_HALL from SOL_ARK_60K). Single-storey conditioned extension of 31,860 m2 east (EXT_HALL_E) and north (EXT_HALL_N) of the base plate. It exists so that the roof carries the full PV array at 2.0 x requirement (X-PAR-09, D75; X-PAR-07, owner decisions 2026-10-15: option A, conditioned). Sized by `flow_graph/param/solver.py` roof_close.

2. Size. Building 234 x 138 m on the 6 m bay grid (39 x 23 bays); extension 31,860 m2; eave 6 m. Loads (A-M-104):
- Lighting 28.04 kW: 8.8 W/m2 (IECC 2021 Table C405.3.2(1), manufacturing facility) lit 10 % of hours with occupant-sensor control (IECC 2021 C405.2.1).
- Ventilation 40.43 kW: outdoor air 0.30 L/(s m2) (ASHRAE 62.1-2019 Table 6.2.2.1), 9558 L/s, conditioned through 7.9 K mean |dT| at heat-pump COP 3.2 (ASHRAE 90.1-2019 Table 6.8.1-2), fans at 1.25 W/(L/s) (ISO 16798-3 SFP 3).
- Envelope 21.54 kW: roof U 0.199 W/(m2 K) on 31,860 m2 and wall U 0.534 W/(m2 K) on the full 744 m perimeter x 6 m (IECC 2021 Table C402.1.4, climate zone 3), 7.9 K mean |dT| (NOAA 1991-2020 DFW: HDD65 2272, CDD65 2878 F-d), COP 3.2.
- Not counted: slab losses, internal gains (both to the bin-hour calculation).

3. Material. Steel portal frames on the 6 m grid; insulated metal roof and wall panels to the IECC U-factors; roof framing for LRFD 1.72 kPa (ASCE 7-22: 1.2 x 0.15 kPa PV dead + 1.6 x 0.96 kPa roof live; A-M-105). Steel sections and panels are made in-house (X-MFG-32).

4. Nozzles. None. Electrical feed SF-EXT_HALL at 480 V AC. Heat pumps air-source; GEO_GHEX not coupled (bore field sized for Q4).

5. Instruments. Occupant sensors and lighting controls (IECC 2021 C405.2); demand-controlled ventilation on the same zones; space temperature per zone.

6. Relief. Not a pressure system. Roof PV access per IFC 2021 1205.3 / NFPA 1 11.12: 1829 mm perimeter pathway, 1219 mm interior pathways, 15 arrays.

7. Code. Building. Not stamped. NORTH_DOCK opens into EXT_HALL_N; a 6 m truck lane to the hall's north wall is reserved (accepted 2026-10-15).

8. Open items. Bin-hour load calculation with internal gains; hall programme; egress for the hall (AQS-EGR-001 update under X-STD-01); FreeCAD massing of the extension.
