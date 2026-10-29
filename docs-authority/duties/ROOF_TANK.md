# ROOF_TANK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 480.9 kg/d. Mass out 480.9 kg/d. Electrical duty 0.0000 kW. In: IA-ESS-HYDRO-CHG 0 kg/d (Pumped hydro charge (pump up; peers S23)); IA-HVAC-COND 67.44 kg/d (AHU condensate to the water cycle); IA-GREY-RET 0 kg/d (treated grey to the water cycle); IA-GW-MAKEUP 0 kg/d (groundwater make-up, reverse-osmosis treated); 3 more. Out: IA-ESS-HYDRO-DIS 0 kg/d (Pumped hydro discharge (penstock; peers S22)); S21 120.7 kg/d (clean tower water); IA-BED-H2O 42.14 kg/d (irrigation); IA-DC-SPRAY 0 kg/d (evaporative spray make-up); 4 more.

2. Size.
- Circulation 200384.0 kg/d. Two-minute holdup 0.2783 m³. A 20-day volume at this rate is not a tank.

3. Material. PVC-U or HDPE, per AQS-STD-002 rule M1. No metal wetted part. Corrosion allowance does not apply to the polymer. Hot LEACH draw at up to 85 °C exceeds the PVC-U limit (X-MAT-09); IA-POT-01 is cooled to 40 °C by a passive PVDF air coil (AQS-STD-002 section 10).

4. Nozzles. Inlet and outlet DN50. At 1.5 m/s and 1000 kg/m³ the bore is 44.4 mm. Drain DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/ROOF_TANK.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. If this node is also a reservoir, that volume is not the two-minute holdup.
9. Balance (AQS-PAR-003 Rev B). Shortfall from the peroxide make-up water (X-SAF-10) made up on IA-POT-01 123.295 kg/d (T4).
