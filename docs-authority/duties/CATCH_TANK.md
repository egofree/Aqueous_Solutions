# CATCH_TANK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: IA-ESS-HYDRO-DIS 0 kg/d (Pumped hydro discharge (penstock; peers S22)). Out: IA-ESS-HYDRO-CHG 0 kg/d (Pumped hydro charge (pump up; peers S23)).

2. Size.
- Circulation 200000.0 kg/d. Two-minute holdup 0.2778 m³. A 20-day volume at this rate is not a tank.

3. Material. PVC-U or HDPE, per AQS-STD-002 rule M1. No metal wetted part. Corrosion allowance does not apply to the polymer.

4. Nozzles. Origin 0, 5000, -10500 mm. Size 12000 × 8000 × 4000 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-ESS-HYDRO-DIS, inlet, -Y face center, 6000, 5000, -8500 mm. Height 2000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S22, inlet, -Y face center, 6000, 5000, -8500 mm. Height 2000 mm from the bottom. Rating conductor. Not a hose.
- N3, S41, inlet, -Y face center, 6000, 5000, -8500 mm. Height 2000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-ESS-HYDRO-CHG, outlet, +Y face center, 6000, 13000, -8500 mm. Height 2000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, S23, outlet, +Y face center, 6000, 13000, -8500 mm. Height 2000 mm from the bottom. Rating conductor. Not a hose.
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/CATCH_TANK.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. If this node is also a reservoir, that volume is not the two-minute holdup.
