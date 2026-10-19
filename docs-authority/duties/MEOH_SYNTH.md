# MEOH_SYNTH

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 54.1 kg/d. Mass out 54.1 kg/d. Electrical duty 0.7388 kW. In: S73 44.42 kg/d (CO2 feedstock); S74 6.536 kg/d (H2 for MeOH); IA-HCO2-MEOH 3.139 kg/d (CO2 not taken by the bed). Out: S75 34.63 kg/d (crude MeOH); MEOH_TO_OLEFIN 0 kg/d (methanol co-feed); IA-MEOH-H2O 19.47 kg/d (synthesis water).

2. Size.
- The largest edge is gas. This class is not a scrubber. No tower diameter is calculated from 1.5 m/s.
- CO₂ + 3 H₂ → CH₃OH + H₂O. MW 44.009, 2.016, 32.042, 18.015. CO₂ limits. Methanol is S75. Water is IA-MEOH-H2O. Hydrogen that does not react does not enter; it is S45.

3. Material. Held. Pressure and temperature are not on the graph. Above 200 °C with H₂ partial pressure, API 941 applies: no carbon steel; 316L or Cr-Mo from the Nelson curves. AQS-REV-H2-001. Synthesis 50 bar a, 250 °C (study); 316L per API 941 (AQS-REV-H2-001 section 5).

4. Nozzles. Origin -4848, 1600, 0 mm. Size 2200 × 900 × 1400 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, S73, inlet, -Y face center, -3748, 1600, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S74, inlet, -Y face center, -3748, 1600, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-MEOH-H2O, outlet, +Y face center, -3748, 2500, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, S75, outlet, +Y face center, -3748, 2500, 700 mm. Height 700 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Temperature and pressure. High pressure trips the feed. Gas stays on the gas edge, not the room.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/MEOH_SYNTH.stl`.

8. Open items. No vessel diameter.
