# EW_8

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 4051.5 kg/d. Mass out 4051.5 kg/d. Electrical duty 0.0000 kW. In: IA-EW-07 4051.5 kg/d (EW overflow). Out: IA-EW-08 4046.4 kg/d (EW overflow); IA-EW-MET-8 5.05 kg/d (plated sheet).

2. Size.
- AQS-DUTY-051: bounding 177 A (14.1 A at the element basis); 2 cathodes, 3 anodes at 176 A/m²; tank 370 × 720 × 760 mm, 0.164 m³ liquor, 64 min; DC 0.44 kW. The 600 × 420 × 650 mm envelope is the plate; layout re-placement held (unit task 14).
- Sheet 5.05 kg/d. As copper, 0.02844 kg/d per A. Current 5.05/0.02844 = 178 A. At 200 A/m², area 178/200 = 0.89 m². Plate 0.60×0.42 m, both sides 0.504 m², 2 plates. Pitch 50 mm.
- At 2.5 V that current is 0.44 kW. The node books 0.0000 kW.
- Liquor 4051.5 kg/d. Thirty-minute holdup V = (4051.5/1000)×(0.5/24) = 0.0844 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode titanium Grade 2, 3 mm. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coated (AQS-STD-002 section 9). Tank and racks PVC/FRP; 316L frame withdrawn (AQS-STD-002 M3). Corrosion allowance 0 mm on the titanium; hydride check per AQS-STD-002 section 9. Pit rate is not measured. Cathode annealed, no cold forming after anneal; anode protected from reverse current (AQS-REV-H2-001). Cell-to-cell transfer by free-fall launder with air break; floating DC; protection current on trip (AQS-STD-002 section 11).

4. Nozzles. Origin 8300, 4000, -6000 mm. Size 600 × 420 × 650 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EW-07, inlet, -Y face center, 8600, 4000, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EW-08, outlet, +Y face center, 8600, 4420, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-EW-MET-8, outlet, +Y face center, 8600, 4420, -5675 mm. Height 325 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_8.stl` is the plate rack. FreeCAD is not in this session.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. Kilowatts at 2.5 V do not match the node.
