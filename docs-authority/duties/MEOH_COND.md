# MEOH_COND

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 26.72 kg/d. Mass out 26.72 kg/d. Electrical duty 0.0000 kW. In: S81 7.251 kg/d (MeOH FC condensate); IA-MEOH-H2O 19.47 kg/d (synthesis water). Out: IA-MEOH-COND 26.72 kg/d (methanol condensate).

2. Size.
- Envelope 400×400×600 mm, 0.0960 m³. That box over this flow would be 86.2 h if it were full. It is not a residence time.
- Seven-day charge V = (4.48/1000)×(168/24) = 0.0314 m³.

3. Material. 316L shell and coil (methanol/water traces) (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Origin -2448, 200, 0 mm. Size 400 × 400 × 600 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-MEOH-H2O, inlet, -Y face center, -2248, 200, 300 mm. Height 300 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S81, inlet, -Y face center, -2248, 200, 300 mm. Height 300 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-MEOH-COND, outlet, +Y face center, -2248, 600, 300 mm. Height 300 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/MEOH_COND.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. None.
