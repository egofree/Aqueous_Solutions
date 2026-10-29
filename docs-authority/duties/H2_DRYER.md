# H2_DRYER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1.975 kg/d. Mass out 1.975 kg/d. Electrical duty 0.0205 kW. In: IA-HDR-H2-02 1.975 kg/d (process H2). Out: S24 0 kg/d (H2 relief contingency); S64 1.975 kg/d (H2 normal path); IA-H2-IN 0 kg/d (dried hydrogen); IA-H2-AIR 0 kg/d (sweep air from the hydrogen hood); 1 more.

2. Size.
- The largest edge is gas. This class is not a scrubber. No tower diameter is calculated from 1.5 m/s.

3. Material. Inlet knock-out PVC-U (wet). Dryer vessel and dry outlet 316L, annealed (M6, dry H₂). Regeneration conditions held. AQS-REV-H2-001.

4. Nozzles. No duct bore. Density is not on the edge, and 1.2 kg/m³ is not used. No flange class. The vent stays on the gas edge, not the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. The vent is S24 to RELIEF_H2. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/H2_DRYER.stl`.

8. Open items. No vessel diameter.
