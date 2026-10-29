# HDR_CO2

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 4.021 kg/d. Mass out 4.021 kg/d. Electrical duty 0.0000 kW. In: S85 0 kg/d (CO2 product after FLUE_KO); S90 4.021 kg/d (metabolic CO2 (desorbed from the HAB CO2 sorbent bed)). Out: CO2_TO_FARM 0 kg/d (CO2 enrichment); S89 0.8824 kg/d (CO2 enrichment dose (FARM AHU supply)); IA-HCO2-MEOH 3.139 kg/d (CO2 not taken by the bed).

2. Size.
- Duct at 10 m/s. Gas 0.5927 m³/h. Bore 5 mm, DN15. Not a packed tower.

3. Material. 316L tube (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Gas duct DN15 at 10 m/s. Bore from 0.5927 m³/h is 5 mm. Drain DN15. No flange class. Atmospheric. Vent DN15 into the suction of this loop, not the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/HDR_CO2.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. Gas volume uses 1.2 kg/m³ because the edge has no m³/h. Duct bore uses 1.2 kg/m³.
