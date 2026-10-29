# MET_SCRUB

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 7.161e+04 kg/d. Mass out 7.161e+04 kg/d. Electrical duty 2.1232 kW. In: S62 5.115e+04 kg/d (MFG metal-aisle capture feed); S71 2.046e+04 kg/d (metal-aisle fume / mist / dust); COMB_OFFGAS 0 kg/d (combustion off-gas when alternate used); IA-DRAW-FUME 2.46 kg/d (draw fume). Out: S72 2.444 kg/d (metal fines and aqueous scrub liquor); S72B 0.0158 kg/d (organic mist); IA-MET-AIR-RET 7.16e+04 kg/d (scrubbed metal-aisle air returned to the hall).

2. Size.
- Gas 2520.0 m³/h. Tower area at 1.5 m/s = 2520.0/3600/1.5 = 0.4667 m². Diameter 771 mm.
- Liquid in 2.46 kg/d. Sump at 10 min: V = (2.46/1000)×(10/60)/24 = 0.00002 m³.
- Packed height 1.0 m plus a demister. The duty is mist and fines, not a high-NTU acid absorption.

3. Material. PVC-U shell, sump, and packing support, per AQS-STD-002 rules M1 and M2. Packing is polymer. No metal wetted part. The graph gives no temperature for this unit; above 60 °C, CPVC. Corrosion allowance does not apply to the polymer.

4. Nozzles. Origin 13600, 200, 0 mm. Size 800 × 800 × 2000 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-DRAW-FUME, inlet, -Y face center, 14000, 200, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S62, inlet, -Y face center, 14000, 200, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, S71, inlet, -Y face center, 14000, 200, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-MET-AIR-RET, outlet, +Y face center, 14000, 1000, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, S72, outlet, +Y face center, 14000, 1000, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, S72B, outlet, +Y face center, 14000, 1000, 1000 mm. Height 1000 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Differential pressure across the packing, and pH if there is a liquor loop. High differential pressure trips the fan.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/MET_SCRUB.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. None.
