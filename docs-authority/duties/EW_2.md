# EW_2

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 4139 kg/d. Mass out 4139 kg/d. Electrical duty 0.0000 kW. In: IA-EW-01 4139 kg/d (EW overflow). Out: IA-EW-02 3991 kg/d (EW overflow); IA-HDR-H2-03 0.3827 kg/d (cathode H2 + sweep air); IA-EW-MET-2 59.89 kg/d (plated sheet); IA-EW2-H2 0 kg/d (hood hydrogen); 1 more.

2. Size.
- AQS-DUTY-051: bounding 2105 A (0.3 A at the element basis); 21 cathodes, 22 anodes at 199 A/m²; tank 2270 × 720 × 760 mm, 1.055 m³ liquor, 396 min; DC 5.26 kW. The 600 × 420 × 650 mm envelope is the plate; layout re-placement held (unit task 14).
- Sheet 59.89 kg/d. As copper, 0.02844 kg/d per A. Current 59.89/0.02844 = 2106 A. At 200 A/m², area 2106/200 = 10.53 m². Plate 0.60×0.42 m, both sides 0.504 m², 21 plates. Pitch 50 mm.
- At 2.5 V that current is 5.26 kW. The node books 0.0000 kW.
- Liquor 4226.0 kg/d. Thirty-minute holdup V = (4226.0/1000)×(0.5/24) = 0.0880 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode titanium Grade 2, 3 mm. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coated (AQS-STD-002 section 9). Tank and racks PVC/FRP; 316L frame withdrawn (AQS-STD-002 M3). Corrosion allowance 0 mm on the titanium; hydride check per AQS-STD-002 section 9. Pit rate is not measured. Cathode annealed, no cold forming after anneal; anode protected from reverse current (AQS-REV-H2-001). Cell-to-cell transfer by free-fall launder with air break; floating DC; protection current on trip (AQS-STD-002 section 11).

4. Nozzles. Origin 6100, 6800, -6000 mm. Size 2270 × 720 × 760 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EW-01, inlet, -Y face center, 7235, 6800, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EW-02, outlet, +Y face center, 7235, 7520, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-EW-MET-2, outlet, +Y face center, 7235, 7520, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-EW2-H2, outlet, +Y face center, 7235, 7520, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-HDR-H2-03, outlet, +Y face center, 7235, 7520, -5620 mm. Height 380 mm from the bottom. Rating conductor. Not a hose.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. The vent is IA-EW2-H2 to HDR_H2. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_2.stl` is the plate rack. FreeCAD is not in this session.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. Kilowatts at 2.5 V do not match the node.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001; AQS-DUTY-051 Rev B). Current efficiency 0.85 and cell voltage 2.12 V (USBM_CL_EW chloride EW). Bounding current 2476 A; 25 cathodes / 26 anodes at 197 A/m²; tank 2670 × 720 × 760 mm; cell DC 5.25 kW; channel DC on IA-DC-EW_2 5.99 kW with 0.3 V bus drop. Figures above at 2.5 V and current efficiency 1.0 are superseded.
