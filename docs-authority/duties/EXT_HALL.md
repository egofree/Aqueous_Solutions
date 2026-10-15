# EXT_HALL

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0.000 kg/d. Mass out 0.000 kg/d. Electrical duty 13.92 kW (SF-EXT_HALL from SOL_ARK_60K). Single-storey extension of 11,088 m2 east (EXT_HALL_E) and north (EXT_HALL_N) of the base plate. It exists so that the roof carries the full PV array (X-PAR-07, owner option A, 2026-10-15). Sized by `flow_graph/param/solver.py` roof_close.

2. Size. Building 120 x 96 m on the 6 m bay grid (20 x 16 bays); extension 11,088 m2. Loads, unconditioned hall (A-M-104, owner review open):
- Lighting 9.76 kW: 8.8 W/m2 (IECC 2021 Table C405.3.2(1), manufacturing facility) lit 10 % of hours with occupant-sensor control (IECC 2021 C405.2.1).
- Ventilation fans 4.16 kW: 0.30 L/(s m2) (ASHRAE 62.1-2019 Table 6.2.2.1), 3326 L/s at 1.25 W/(L/s) (ISO 16798-3 SFP 3).
- Heating and cooling 0 kW (unconditioned). If conditioned, the solver needs about 33,500 m2 of roof.

3. Material. Steel portal frames on the 6 m grid; roof framing for LRFD 1.72 kPa (ASCE 7-22: 1.2 x 0.15 kPa PV dead + 1.6 x 0.96 kPa roof live; A-M-105). Steel sections are made in-house (X-MFG-32).

4. Nozzles. None. Electrical feed SF-EXT_HALL at 480 V AC.

5. Instruments. Occupant sensors and lighting controls (IECC 2021 C405.2); ventilation run on the same zones.

6. Relief. Not a pressure system. Roof PV access per IFC 2021 1205.3 / NFPA 1 11.12: 1829 mm perimeter pathway, 1219 mm interior pathways, 6 arrays.

7. Code. Building. Not stamped. NORTH_DOCK opens into EXT_HALL_N; a 6 m truck lane to the hall's north wall is reserved (accepted 2026-10-15).

8. Open items. Hall conditioning (owner review). Egress for the hall (AQS-EGR-001 update under X-STD-01). FreeCAD massing of the extension.
