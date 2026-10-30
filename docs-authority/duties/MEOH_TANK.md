# MEOH_TANK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 34.52 kg/d. Mass out 34.52 kg/d. Electrical duty 0.0000 kW. In: S75 34.51 kg/d (crude MeOH); S77 0.0146 kg/d (biogenic MeOH). Out: S76 5 kg/d (MeOH fuel); IA-MEOH-REST 1.28 kg/d (tank draw); IA-MEOH-PROD 28.01 kg/d (methanol product); MEOH_TO_VDF 0.1501 kg/d (methanol carbon source to VDF); 2 more.

2. Size.
- Envelope 800×800×1100 mm is the shell. It is not full. Working volume, 7 days of throughput: V = (6.02/1000)×(168/24) = 0.0421 m³.

3. Material. SA-240 304L, welded (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Origin -2048, 1600, 0 mm. Size 800 × 800 × 1100 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-CLOSE-7, inlet, -Y face center, -1648, 1600, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EM-CH4, inlet, -Y face center, -1648, 1600, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, S75, inlet, -Y face center, -1648, 1600, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, S77, inlet, -Y face center, -1648, 1600, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-FORM-S, outlet, +Y face center, -1648, 2400, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, IA-MEOH-FORM, outlet, +Y face center, -1648, 2400, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N7, IA-MEOH-MEAM, outlet, +Y face center, -1648, 2400, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N8, IA-MEOH-REST, outlet, +Y face center, -1648, 2400, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N9, S76, outlet, +Y face center, -1648, 2400, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/MEOH_TANK.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. None.
