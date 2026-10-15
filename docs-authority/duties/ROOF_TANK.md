# ROOF_TANK

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 200408.3 kg/d. Mass out 200408.3 kg/d. Electrical duty 0.0000 kW. In: IA-ESS-HYDRO-CHG 200000.0 kg/d (Pumped hydro charge (pump up; peers S23)); IA-NOX-H2O 226.2 kg/d (scrubber condensate); IA-POT-01 120.5 kg/d (potable makeup, remineralised); IA-HVAC-COND 56.70 kg/d (AHU condensate to the water cycle); 10 more. Out: IA-ESS-HYDRO-DIS 200000.0 kg/d (Pumped hydro discharge (penstock; peers S22)); IA-NOX-HAB 207.3 kg/d (scrubber water); S21 120.0 kg/d (clean tower water); S40 37.18 kg/d (clean overflow); 3 more.

2. Size.
- Circulation 200384.0 kg/d. Two-minute holdup 0.2783 m³. A 20-day volume at this rate is not a tank.

3. Material. PVC-U or HDPE, per AQS-STD-002 rule M1. No metal wetted part. Corrosion allowance does not apply to the polymer. Hot LEACH draw at up to 85 °C exceeds the PVC-U limit (X-MAT-09); IA-POT-01 is cooled to 40 °C by a passive PVDF air coil (AQS-STD-002 section 10).

4. Nozzles. Inlet and outlet DN50. At 1.5 m/s and 1000 kg/m³ the bore is 44.4 mm. Drain DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/ROOF_TANK.stl` is the box, not the internal. FreeCAD is not in this session.

8. Open items. If this node is also a reservoir, that volume is not the two-minute holdup.
