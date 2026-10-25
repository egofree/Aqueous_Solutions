# ALK_SCRUBBER

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 3.751e+04 kg/d. Mass out 3.751e+04 kg/d. Electrical duty 1.1122 kW. In: IA-ACID-AIR-RET 3.751e+04 kg/d (acid-gas dilution air returned to the alkaline scrubber); IA-VS-OFF 0.0292 kg/d (scrubbed vent to the house acid-gas header). Out: S65 3.751e+04 kg/d (acid-gas residual).

2. Size.
- Gas 1500.0 m³/h. Tower area at 1.5 m/s = 1500.0/3600/1.5 = 0.2778 m². Diameter 595 mm.
- No liquor inlet. No sump volume is invented from the gas mass.
- Packed height 3.0 m. HTU 0.5 m on 25 mm pall rings. NTU 6. Removal 1 − e^(−6) = 99.75% if the acid gas is irreversible.

3. Material. PVC-U shell, sump, and packing support, per AQS-STD-002 rules M1 and M2. Packing is polymer. No metal wetted part. The graph gives no temperature for this unit; above 60 °C, CPVC. Corrosion allowance does not apply to the polymer.

4. Nozzles. Gas duct DN250 at 10 m/s. Bore from 1500.0 m³/h is 230 mm. Drain DN15. No flange class. Atmospheric. Vent DN15 into the suction of this loop, not the room.

5. Instruments. Differential pressure across the packing, and pH if there is a liquor loop. High differential pressure trips the fan.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/ALK_SCRUBBER.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. HTU is a packing figure, not a measured transfer unit.
