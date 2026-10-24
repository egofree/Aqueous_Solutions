# NOX_SCRUB

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 459.9 kg/d. Mass out 459.9 kg/d. Electrical duty 0.0385 kW. In: S46 0.268 kg/d (exhaust condensate / NOx); IA-FLUE-EXH 263.6 kg/d (flue to the NOx scrubber); IA-FC-EXH 0 kg/d (cell exhaust); IA-LEACH-NOX 195 kg/d (leach offgas); 3 more. Out: IA-NOX-H2O 221.5 kg/d (scrubber condensate); IA-NOX-N 20.05 kg/d (nitrate liquor); IA-NOX-CO2 21.75 kg/d (scrubbed CO2 to the cold box); IA-NOX-N2 196.7 kg/d (scrubbed flue nitrogen to the cold box).

2. Size.
- Envelope 600×400×1200 mm, 0.2880 m³. That box over this flow would be 15.0 h if it were full. It is not a residence time.

3. Material. CPVC shell, sump, and packing support, per AQS-STD-002 rules M1 and M2. Packing is polymer. No metal wetted part. IA-LEACH-NOX and IA-CLOSE-1 arrive from LEACH_CSTR_1 at up to 85 °C (X-MAT-09). Inlet section and sump CPVC per M5; the packed section above the quench may stay PVC-U once the gas temperature there is calculated (held). Corrosion allowance does not apply to the polymer.

4. Nozzles. Origin -3500, 5800, 0 mm. Size 600 × 400 × 1200 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-CLOSE-1, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, IA-FC-EXH, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N3, IA-FC-FIX, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, IA-FLUE-EXH, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-GLX-NOX, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N6, IA-LEACH-NOX, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N7, S46, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N13, IA-NIT-VENT, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N14, IA-HNO3-VENT, inlet, -Y face center, -3200, 5800, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N8, IA-NOX-BOARD, outlet, +Y face center, -3200, 6200, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N9, IA-NOX-CO2, outlet, +Y face center, -3200, 6200, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N10, IA-NOX-H2O, outlet, +Y face center, -3200, 6200, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N11, IA-NOX-N, outlet, +Y face center, -3200, 6200, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N12, IA-NOX-N2, outlet, +Y face center, -3200, 6200, 600 mm. Height 600 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Differential pressure across the packing, and pH if there is a liquor loop. High differential pressure trips the fan.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/NOX_SCRUB.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. None.
