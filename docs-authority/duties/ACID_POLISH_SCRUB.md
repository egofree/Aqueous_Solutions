# ACID_POLISH_SCRUB

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 37537.2 kg/d. Mass out 37537.2 kg/d. Electrical duty 0.0000 kW. In: S65 37509.8 kg/d (acid-gas residual); IA-SCRUB-SRC 27.36 kg/d (scrub feed). Out: IA-ACID-AIR-RET 37509.8 kg/d (acid-gas dilution air returned to the alkaline scrubber); S66 27.36 kg/d (scrub liquor → chlorate finish).

2. Size.
- Gas 1500.0 m³/h. Tower area at 1.5 m/s = 1500.0/3600/1.5 = 0.2778 m². Diameter 595 mm.
- Liquid in 27.36 kg/d. Sump at 10 min: V = (27.36/1000)×(10/60)/24 = 0.00019 m³.
- Packed height 3.0 m. HTU 0.5 m on 25 mm pall rings. NTU 6. Removal 1 − e^(−6) = 99.75% if the acid gas is irreversible.

3. Material. CPVC shell, sump, and packing support, per AQS-STD-002 rules M1 and M2. Packing is polymer. No metal wetted part. IA-SCRUB-SRC arrives from LEACH_CSTR_1 at up to 85 °C (X-MAT-09). Shell, sump and inlet CPVC per M5. Corrosion allowance does not apply to the polymer.

4. Nozzles. Gas duct DN250 at 10 m/s. Bore from 1500.0 m³/h is 230 mm. Drain DN15. No flange class. Atmospheric. Vent DN15 into the suction of this loop, not the room.

5. Instruments. Differential pressure across the packing, and pH if there is a liquor loop. High differential pressure trips the fan.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/ACID_POLISH_SCRUB.stl` is the box, not the internal. FreeCAD is not in this session.

8. Open items. HTU is a packing figure, not a measured transfer unit.
