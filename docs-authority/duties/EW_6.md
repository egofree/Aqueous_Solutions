# EW_6

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 3910 kg/d. Mass out 3910 kg/d. Electrical duty 0.0000 kW. In: IA-EW-05 3910 kg/d (EW overflow). Out: IA-EW-06 3896 kg/d (EW overflow); IA-EW-MET-6 5.47 kg/d (plated sheet); IA-EW6-CL2 8.07 kg/d (anode Cl2 (+ O2 side) to leach oxidation); IA-EW6-H2B 0.03496 kg/d (cathode H2 to the H2 pool).

2. Size.
- AQS-DUTY-051: bounding 192 A (27.1 A at the element basis); 2 cathodes, 3 anodes at 191 A/m²; tank 370 × 720 × 760 mm, 0.164 m³ liquor, 63 min; DC 0.48 kW. The 600 × 420 × 650 mm envelope is the plate; layout re-placement held (unit task 14).
- Sheet 5.47 kg/d. As copper, 0.02844 kg/d per A. Current 5.47/0.02844 = 192 A. At 200 A/m², area 192/200 = 0.96 m². Plate 0.60×0.42 m, both sides 0.504 m², 2 plates. Pitch 50 mm.
- At 2.5 V that current is 0.48 kW. The node books 0.0000 kW.
- Liquor 4128.1 kg/d. Thirty-minute holdup V = (4128.1/1000)×(0.5/24) = 0.0860 m³.
- Envelope 600×420×650 mm is one plate station, not the rack.

3. Material. Cathode titanium Grade 2, 3 mm. Anode titanium mesh, 1.5 mm, mixed-metal-oxide coated (AQS-STD-002 section 9). Tank and racks PVC/FRP; 316L frame withdrawn (AQS-STD-002 M3). Corrosion allowance 0 mm on the titanium; hydride check per AQS-STD-002 section 9. Pit rate is not measured. Cathode annealed, no cold forming after anneal; anode protected from reverse current (AQS-REV-H2-001). Cell-to-cell transfer by free-fall launder with air break; floating DC; protection current on trip (AQS-STD-002 section 11).

4. Nozzles. Origin 10000, 6800, -6000 mm. Size 370 × 720 × 760 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-EW-05, inlet, -Y face center, 10185, 6800, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-EW-06, outlet, +Y face center, 10185, 7520, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-EW-MET-6, outlet, +Y face center, 10185, 7520, -5620 mm. Height 380 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Cell voltage, current, liquor temperature. High temperature or low flow trips the rectifier.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. Rack `cad/stl/EW_6.stl` is the plate rack. Nothing inside it is modelled yet.

8. Open items. The sheet mass is undifferentiated plated metal. It is not an assay. The copper equivalent is the sizing rule, not a metal identification. Kilowatts at 2.5 V do not match the node.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001; AQS-DUTY-051 Rev B). Current efficiency 0.85 and cell voltage 2.12 V (USBM_CL_EW chloride EW). Bounding current 226 A; 3 cathodes / 4 anodes at 150 A/m²; tank 470 × 720 × 760 mm; cell DC 0.48 kW; channel DC on IA-DC-EW_6 0.55 kW with 0.3 V bus drop. Figures above at 2.5 V and current efficiency 1.0 are superseded.
