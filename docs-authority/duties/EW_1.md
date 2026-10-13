# EW_1

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 4287.8 kg/d. Mass out 4287.8 kg/d. Electrical duty 6.00 kW. In: IA-EW-04 4287.8 kg/d (CSTR to EW-1); IA-COAT-OUT 0.0200 kg/d (coated anode). Out: IA-EW-01 4226.0 kg/d (EW overflow); IA-EW-MET-1 59.87 kg/d (plated sheet); IA-EW1-H2 1.89 kg/d (hood hydrogen); IA-COAT-IN 0.0200 kg/d (nickel sheet to the booth).

2. Size.
- Sheet 59.87 kg/d. As copper, 0.02844 kg/d per A. Current 59.87/0.02844 = 2105 A. At 200 A/m², area 2105/200 = 10.53 m². Plate 0.60×0.42 m, both sides 0.504 m², 21 plates. Pitch 50 mm.
- At 2.5 V that current is 5.26 kW. The node books 6.00 kW.
- Liquor 4287.8 kg/d. Thirty-minute holdup V = (4287.8/1000)×(0.5/24) = 0.0893 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode 316L, 3 mm. Anode titanium mesh, 1.5 mm, with 0.5 mm PbO₂. No iridium. Tank PVC/FRP. Corrosion allowance 0 mm on the titanium. Pit rate is not measured.

4. Nozzles. Origin 3200, 5300, -6000 mm. Size 600 × 420 × 650 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-COAT-OUT, inlet, -Y face center, 3500, 5300, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-E-RECT, inlet, -Y face center, 3500, 5300, -5675 mm. Height 325 mm from the bottom. Rating conductor. Not a hose.
- N3, IA-EW-04, inlet, -Y face center, 3500, 5300, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-COAT-IN, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-EW-01, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, IA-EW-MET-1, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N7, IA-EW1-H2, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N8, IA-HDR-H2-01, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Rating conductor. Not a hose.
- N9, IA-HX8, outlet, +Y face center, 3500, 5720, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. The vent is IA-EW1-H2 to HDR_H2. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_1.stl` is the plate rack. FreeCAD is not in this session.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. Kilowatts at 2.5 V do not match the node.
