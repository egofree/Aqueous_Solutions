# BLACK_DIGEST

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 22.72 kg/d. Mass out 22.72 kg/d. Electrical duty 0.1052 kW. In: IA-BLK-01 19.64 kg/d (vacuum-toilet blackwater); IA-URINE 1.42 kg/d (urine to the blackwater barrier train); IA-FEC-01 0.13 kg/d (fecal solids to the blackwater barrier train); IA-GAL 1.18 kg/d (galley food waste to the blackwater barrier train); 1 more. Out: DIGEST_TO_POLY 0 kg/d (digester organics); IA-BLK-GAS 0.0986 kg/d (digester biogas, flared in the afterburner); IA-BLK-CAKE 0.67 kg/d (dewatered digestate cake to incineration (barrier 2)); IA-BLK-NUT 0.9 kg/d (released digest-liquor nutrient split); 1 more.

2. Size.
- No mass throughput. No volume is invented.
- No flush blackwater. 16.48 kg/d was an off-graph term and is removed. Habitation already balances. Toilet solids and urine are the black stream.

3. Material. PVC-U wetted, per AQS-STD-002 rules M1 and M2. No metal wetted part. The graph gives no temperature for this unit; above 60 °C the thermoplastic is CPVC, never metal. Corrosion allowance does not apply to the polymer.

4. Nozzles. Origin 200, 200, 6000 mm. Size 1400 × 900 × 1600 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-DIG-BLK, inlet, -Y face center, 900, 200, 6800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Temperature and pressure. High pressure trips the feed. Gas stays on the gas edge, not the room.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/BLACK_DIGEST.stl` is the box, not the internal. FreeCAD is not in this session.

8. Open items. None.

## X-SAN-01 (2026-10-15)

Superseded for sizing by AQS-DUTY-063 (`docs-authority/sizing/SANITATION.md`): thermophilic anaerobic digester, barrier 1 of the multi-barrier train. Values on the graph and in that document govern.
