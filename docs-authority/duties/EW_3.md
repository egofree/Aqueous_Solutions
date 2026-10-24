# EW_3

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 3991 kg/d. Mass out 3991 kg/d. Electrical duty 0.0000 kW. In: IA-EW-02 3991 kg/d (EW overflow). Out: IA-EW-03 3935 kg/d (EW overflow); IA-EW-MET-3 22.48 kg/d (plated sheet); IA-EW3-CL2 33.16 kg/d (anode Cl2 (+ O2 side) to leach oxidation); IA-EW3-H2B 0.1437 kg/d (cathode H2 to the H2 pool).

2. Size.
- AQS-DUTY-051: bounding 790 A (308.7 A at the element basis); 8 cathodes, 9 anodes at 196 A/m²; tank 970 × 720 × 760 mm, 0.446 m³ liquor, 169 min; DC 1.98 kW. The 600 × 420 × 650 mm envelope is the plate; layout re-placement held (unit task 14).
- Sheet 22.48 kg/d. As copper, 0.02844 kg/d per A. Current 22.48/0.02844 = 790 A. At 200 A/m², area 790/200 = 3.95 m². Plate 0.60×0.42 m, both sides 0.504 m², 8 plates. Pitch 50 mm.
- At 2.5 V that current is 1.98 kW. The node books 0.0000 kW.
- Liquor 4164.2 kg/d. Thirty-minute holdup V = (4164.2/1000)×(0.5/24) = 0.0868 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode titanium Grade 2, 3 mm. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coated (AQS-STD-002 section 9). Tank and racks PVC/FRP; 316L frame withdrawn (AQS-STD-002 M3). Corrosion allowance 0 mm on the titanium; hydride check per AQS-STD-002 section 9. Pit rate is not measured. Cathode annealed, no cold forming after anneal; anode protected from reverse current (AQS-REV-H2-001). Cell-to-cell transfer by free-fall launder with air break; floating DC; protection current on trip (AQS-STD-002 section 11).

4. Nozzles. Origin 9500, 5400, -6000 mm. Size 970 × 720 × 760 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EW-02, inlet, -Y face center, 9985, 5400, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EW-03, outlet, +Y face center, 9985, 6120, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-EW-MET-3, outlet, +Y face center, 9985, 6120, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_3.stl` is the plate rack. Nothing inside it is modelled yet.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. Kilowatts at 2.5 V do not match the node.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001; AQS-DUTY-051 Rev B). Current efficiency 0.85 and cell voltage 2.12 V (USBM_CL_EW chloride EW). Bounding current 930 A; 10 cathodes / 11 anodes at 184 A/m²; tank 1170 × 720 × 760 mm; cell DC 1.97 kW; channel DC on IA-DC-EW_3 2.25 kW with 0.3 V bus drop. Figures above at 2.5 V and current efficiency 1.0 are superseded.
