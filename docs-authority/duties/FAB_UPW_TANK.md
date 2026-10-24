# FAB_UPW_TANK

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 60 kg/d. Mass out 60 kg/d. Electrical duty 0.0000 kW. In: IA-UPW-FAB 60 kg/d (fab UPW). Out: S27 60 kg/d (fab UPW > 18 MΩ·cm class).

2. Size.
- V = (60.00/1000)×(168/24) = 0.4200 m³. 7 days of throughput.

3. Material. PE (rotomoulded / fabricated) (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Origin 21000, 8200, 0 mm. Size 500 × 500 × 800 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-UPW-FAB, inlet, -Y face center, 21250, 8200, 400 mm. Height 400 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S27, outlet, +Y face center, 21250, 8700, 400 mm. Height 400 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/FAB_UPW_TANK.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. The vessel has not been built, so this is not a measured volume.
