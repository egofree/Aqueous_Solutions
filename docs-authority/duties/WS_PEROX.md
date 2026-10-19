# WS_PEROX

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 3 kg/d. Mass out 3 kg/d. Electrical duty 0.0308 kW. In: IA-H2O2-SRC 0.176 kg/d (oxygen to peroxide); IA-PEROX-H2O 2.824 kg/d (peroxide dilution water). Out: S32 3 kg/d (H₂O₂).

2. Size.
- Storage (X-SAF-09): 1 d holdup at 2.94 L/d = 2.9 L net; tank 5 L nominal; own bund 6 L (≥110 %). Holdup days are an assumption: unstabilised peroxide decomposes; product_spec holdup_max_d 1.0.
- The largest edge is gas. This class is not a scrubber. No tower diameter is calculated from 1.5 m/s.

3. Material. HDPE tank (cross-linked, unpigmented, UV stabilized), PVDF piping, pump, and valves, PTFE or FKM seals. No metal wetted part (M3). Cell electrodes under M6. 5 wt% nominal, 6 wt% maximum, no stabilizer (graph product_spec). AQS-DSN-OX-001 section 2.

4. Nozzles. Origin 15200, 8200, 0 mm. Size 800 × 800 × 1100 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-H2O2-SRC, inlet, -Y face center, 15600, 8200, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N2, S32, outlet, +Y face center, 15600, 9000, 550 mm. Height 550 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Level with high-high trip on the cell. Temperature high trip 30 °C, which closes the cell feed and drains to the bund. Concentration alarm above 6 wt%. Vent flow or tank pressure alarm.

6. Relief. Atmospheric. Continuous filtered vent and a free-lifting manway cover as the emergency relief for decomposition. Ball and plug valves have vented cavities; no trapped volume. Not to a closed header.
7. Code. Shop. Not stamped. The envelope is `cad/stl/WS_PEROX.stl`.

8. Open items. Cell sized at 12.31 A, 246 cm², 30.8 W (AQS-DSN-OX-001 2.1, assumptions); anode held. IA-H2O2-SRC 3.0 kg/d against 0.176 kg/d O₂ needed: water source edge missing, owner decision. Tank volume (X-SAF-09). Segregation per AQS-DSN-OX-001 section 3.
