# EXPANDER

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1575.5 kg/d. Mass out 1575.5 kg/d. Electrical duty 0.6140 kW. In: IA-EXP-IN 1575.5 kg/d (cold gas). Out: IA-EXP-OUT 1575.5 kg/d (expanded gas).

2. Size.
- Bore 50 mm, stroke 80 mm, 600 rpm, displacement 1.57 L/s. Inlet 500 kPa and 150 K. Density P/RT = 11.61 kg/m³. Shaft 614.4 W at 70% of the isentropic drop from 500 kPa to 130 kPa. Torque 614.4 / (600×2π/60) = 9.8 N·m. The 5 kW figure is the cold-box load, not this cylinder.

3. Material. 316L. Condensation. No carbon steel. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Origin 17600, 6000, -6000 mm. Size 600 × 400 × 500 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EXP-IN, inlet, -Y face center, 17900, 6000, -5750 mm. Height 250 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EXP-OUT, outlet, +Y face center, 17900, 6400, -5750 mm. Height 250 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Inlet pressure, discharge pressure, and speed. Overspeed or high inlet pressure trips the drive.

6. Relief. Set point 550 kPa, 110% of the 500 kPa inlet. Destination is CRYO_ASU, on IA-EXP-OUT, not the room. The node design_kPa is 550. relief_mm is 3.6 and was not resized for that set point.

7. Code. Shop. Not stamped. The envelope is `cad/stl/EXPANDER.stl`.

8. Open items. Isentropic efficiency 70% is assumed. The relief orifice is not calculated at 550 kPa.
