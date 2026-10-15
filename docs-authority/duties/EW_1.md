# EW_1

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 4288 kg/d. Mass out 4288 kg/d. Electrical duty 5.2483 kW. In: IA-EW-04 4288 kg/d (CSTR to EW-1); IA-COAT-OUT 0.02 kg/d (coated anode). Out: IA-EW-01 4139 kg/d (EW overflow); IA-EW-MET-1 59.87 kg/d (plated sheet); IA-EW1-H2 0 kg/d (hood hydrogen); IA-COAT-IN 0.02 kg/d (nickel sheet to the booth); 3 more.

2. Size.
- AQS-DUTY-051: bounding 2104 A (0.1 A at the element basis); 21 cathodes, 22 anodes at 199 A/m²; tank 2270 × 720 × 760 mm, 1.055 m³ liquor, 390 min; DC 5.26 kW. The 600 × 420 × 650 mm envelope is the plate; layout re-placement held (unit task 14).
- Sheet 59.87 kg/d. As copper, 0.02844 kg/d per A. Current 59.87/0.02844 = 2105 A. At 200 A/m², area 2105/200 = 10.53 m². Plate 0.60×0.42 m, both sides 0.504 m², 21 plates. Pitch 50 mm.
- At 2.5 V that current is 2105 × 2.5 = 5263 W, 5.263 kW. The node books 5.263 kW. Current efficiency 1.0 is assumed.
- Output bar at 200 A/cm²: 2105 / 200 = 10.5 cm² copper per pole.
- Liquor 4287.8 kg/d. Thirty-minute holdup V = (4287.8/1000)×(0.5/24) = 0.0893 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode titanium Grade 2, 3 mm. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coated (AQS-STD-002 section 9). Tank and racks CPVC (X-MAT-09); 316L frame withdrawn (AQS-STD-002 M3). Corrosion allowance 0 mm on the titanium; hydride check per AQS-STD-002 section 9. Pit rate is not measured. Cathode annealed, no cold forming after anneal; anode protected from reverse current (AQS-REV-H2-001). IA-EW-04 arrives at 77.5 °C (edge conditions; X-MAT-09). EW_1 tank and racks CPVC per M5; EW_2 to EW_9 see 55 °C and stay PVC-U. Cell-to-cell transfer by free-fall launder with air break; floating DC; protection current on trip (AQS-STD-002 section 11).

4. Nozzles. Origin 3200, 6700, -6000 mm. Size 2270 × 720 × 760 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-COAT-OUT, inlet, -Y face center, 4335, 6700, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-E-RECT, inlet, -Y face center, 4335, 6700, -5620 mm. Height 380 mm from the bottom. Rating conductor. Not a hose.
- N3, IA-EW-04, inlet, -Y face center, 4335, 6700, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-COAT-IN, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-EW-01, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, IA-EW-MET-1, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N7, IA-EW1-H2, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N8, IA-HDR-H2-01, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Rating conductor. Not a hose.
- N9, IA-HX8, outlet, +Y face center, 4335, 7420, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. The vent is IA-EW1-H2 to HDR_H2. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_1.stl` is the plate rack. FreeCAD is not in this session.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. IA-E-RECT stays 4.57 kW and does not equal the 5.263 kW node. Current efficiency and cell voltage are assumed, not measured.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001; AQS-DUTY-051 Rev B). Current efficiency 0.85 and cell voltage 2.12 V (USBM_CL_EW chloride EW). Bounding current 2476 A; 25 cathodes / 26 anodes at 196 A/m²; tank 2670 × 720 × 760 mm; cell DC 5.25 kW; channel DC on IA-DC-EW_1 5.99 kW with 0.3 V bus drop. Figures above at 2.5 V and current efficiency 1.0 are superseded.
