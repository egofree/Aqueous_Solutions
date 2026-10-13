# CRYO_AHU

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 135.7 kg/d. Mass out 135.7 kg/d. Electrical duty 0.0000 kW. In: IA-AHU-AIR 79.04 kg/d (outdoor air moisture); IA-TERR-VAP 40.00 kg/d (greenhouse transpiration); IA-BED-VAP 16.70 kg/d (bed transpiration). Out: S68 78.99 kg/d (flue condensate); IA-HVAC-COND 56.70 kg/d (AHU condensate to the water cycle); IA-AHU-POT 0.0521 kg/d (condensable slip).

2. Size.
- Duct at 10 m/s. Gas 4.71 m³/h. Bore 13 mm, DN15. Not a packed tower.

3. Material. 316L. Condensation. No carbon steel. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Gas duct DN15 at 10 m/s. Bore from 4.71 m³/h is 13 mm. Drain DN15. No flange class. Atmospheric. Vent DN15 into the suction of this loop, not the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. The vents are S56 to RELIEF_CRYO and S86 to RELIEF_CRYO. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/CRYO_AHU.stl`.

8. Open items. Gas volume uses 1.2 kg/m³ because the edge has no m³/h. Duct bore uses 1.2 kg/m³.
