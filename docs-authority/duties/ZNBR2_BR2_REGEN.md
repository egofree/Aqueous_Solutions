# ZNBR2_BR2_REGEN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 916.2 kg/d. Mass out 916.2 kg/d. Electrical duty 0.0000 kW. In: S69 916.2 kg/d (Br2 vapor). Out: S69B 916.2 kg/d (NaBr after ORP).

2. Size.
- Gas 30.00 m³/h. Tower area at 1.5 m/s = 30.0/3600/1.5 = 0.0056 m². Diameter 84 mm.
- No liquor inlet. No sump volume is invented from the gas mass.
- Packed height 3.0 m. HTU 0.5 m on 25 mm pall rings. NTU 6. Removal 1 − e^(−6) = 99.75% if the acid gas is irreversible.

3. Material. PVC-U shell, sump, liquor piping, and Pall-ring packing; FKM gaskets. AQS-STD-002 section 3.1: 10 ppmv Br₂ in air into caustic NaBr/NaOBr liquor; PVDF excluded above pH 12, PP excluded for halogens. No metal wetted part. Hypobromite rating held for a coupon test.

4. Nozzles. Origin -6400, 10000, 0 mm. Size 400 × 400 × 1500 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, S69, inlet, -Y face center, -6200, 10000, 750 mm. Height 750 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S69B, outlet, +Y face center, -6200, 10400, 750 mm. Height 750 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Differential pressure across the packing, and pH if there is a liquor loop. High differential pressure trips the fan.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/ZNBR2_BR2_REGEN.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. HTU is a packing figure, not a measured transfer unit.
