# EXPANDER

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: IA-EXP-IN 0 kg/d (cold gas). Out: IA-EXP-OUT 0 kg/d (expanded gas).

2. Size.
- Bore 50 mm, stroke 80 mm, 600 rpm, displacement 1.57 L/s. Inlet 500 kPa and 150 K. Density P/RT = 11.61 kg/m³. Shaft 614.4 W at 70% of the isentropic drop from 500 kPa to 130 kPa. Torque 614.4 / (600×2π/60) = 9.8 N·m. The 5 kW figure is the cold-box load, not this cylinder.

3. Material. 316L. Condensation. No carbon steel. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Origin 17600, 6000, -6000 mm. Size 600 × 400 × 500 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EXP-IN, inlet, -Y face center, 17900, 6000, -5750 mm. Height 250 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EXP-OUT, outlet, +Y face center, 17900, 6400, -5750 mm. Height 250 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Inlet pressure, discharge pressure, and speed. Overspeed or high inlet pressure trips the drive.

6. Relief. Set point 550 kPa, 110% of the 500 kPa inlet. Destination is CRYO_ASU, on IA-EXP-OUT, not the room. The node design_kPa is 550.
- Case. Blocked discharge. Relieving load W is the whole IA-EXP-IN rate, 1575.544 / 24 = 65.65 kg/h.
- Method. API 520 Part I, gas, critical flow. A = W / (C · Kd · P1 · Kb · Kc) · √(T · Z / M), A in mm², W in kg/h, P1 in kPa absolute.
- Pressure. Set 550 kPa, taken as absolute like the 500 kPa in P/RT. Overpressure 10 %. P1 = 605 kPa a. Back pressure 130 kPa a. 130 / 605 = 0.215, below the critical ratio 0.528. Critical flow.
- Fluid, from the edge. M = ρRT/P = 11.61 × 8.314 × 150 / 500 = 28.96 kg/kmol. T = 150 K. k = 1.40 and Z = 1.0 are assumed.
- Coefficients. C = 0.03948 · √(k · (2/(k+1))^((k+1)/(k−1))) = 0.02703. Kd = 0.975. Kb = 1.0. Kc = 1.0, no rupture disk.
- Result. A = 65.65 / (0.02703 × 0.975 × 605 × 1 × 1) × √(150 / 28.96) = 9.37 mm². Bore 3.45 mm.
- relief_mm 3.6 is 10.18 mm². It meets the case with 8.6 % area margin. It stays. On a gauge basis P1 is 706 kPa a and the area is 8.03 mm², so the absolute basis governs. The smallest API 526 letter orifice, D at 71 mm², also covers it. No valve is selected.

7. Code. Shop. Not stamped. The solid is `cad/stl/EXPANDER.stl`, from `models/mfg/EXPANDER/expander.py` (AQS-PLAN-006). Drawings are not made.

8. Open items. Isentropic efficiency 70% is assumed. Relief: k, Z, the absolute set basis, and a supply that is not limited below the edge rate are assumed. IA-EXP-IN composition is the liquid stencil, water 0.97; the molar mass is taken from the edge density, not from it.
