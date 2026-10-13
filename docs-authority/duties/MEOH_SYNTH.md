# MEOH_SYNTH

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 7.85 kg/d. Mass out 7.85 kg/d. Electrical duty 0.5000 kW. In: S73 6.90 kg/d (CO2 feedstock); S74 0.9482 kg/d (hydrogen consumed). Out: S75 5.02 kg/d (methanol); IA-MEOH-H2O 2.82 kg/d (synthesis water).

2. Size.
- The largest edge is gas. This class is not a scrubber. No tower diameter is calculated from 1.5 m/s.
- CO₂ + 3 H₂ → CH₃OH + H₂O. MW 44.009, 2.016, 32.042, 18.015. CO₂ limits. Methanol is S75. Water is IA-MEOH-H2O. Hydrogen that does not react does not enter; it is S45.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Origin -4848, 1600, 0 mm. Size 2200 × 900 × 1400 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, S73, inlet, -Y face center, -3748, 1600, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S74, inlet, -Y face center, -3748, 1600, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-MEOH-H2O, outlet, +Y face center, -3748, 2500, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, S75, outlet, +Y face center, -3748, 2500, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Temperature and pressure. High pressure trips the feed. Gas stays on the gas edge, not the room.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped.

8. Open items. No vessel diameter. Duct bore is not calculated. Bore was not calculated where the edge has no density and no line size.
