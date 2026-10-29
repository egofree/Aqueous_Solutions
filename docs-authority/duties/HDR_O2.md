# HDR_O2

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 33.17 kg/d. Mass out 33.17 kg/d. Electrical duty 0.0000 kW. In: S83 33.17 kg/d (O2 product); IA-O2-MAKE 0 kg/d (oxygen makeup). Out: IA-FC-AIR 9.407 kg/d (cell air); IA-H2O2-SRC 0.176 kg/d (oxygen to peroxide); IA-GEN-O2 0.1722 kg/d (combustion O2, 10 % excess); IA-AB-O2 0.5283 kg/d (combustion O2, 10 % excess); 2 more.

2. Size.
- Duct at 10 m/s. Gas 1.67 m³/h. Bore 8 mm, DN15. Not a packed tower.

3. Material. 316L tube, oxygen-clean per ASTM_G93, socketless (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Gas duct DN15 at 10 m/s. Bore from 1.67 m³/h is 8 mm. Drain DN15. No flange class. Atmospheric. Vent DN15 into the suction of this loop, not the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/HDR_O2.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. Gas volume uses 1.2 kg/m³ because the edge has no m³/h. Duct bore uses 1.2 kg/m³.
9. Balance (AQS-PAR-003 Rev B). O2 product S83 44.906 kg/d equals the header draw; IA-O2-RET 0 (T3).
