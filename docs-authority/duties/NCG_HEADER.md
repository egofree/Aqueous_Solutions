# NCG_HEADER

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 5 kg/d. Mass out 5 kg/d. Electrical duty 0.0000 kW. In: IA-OIL-03 5 kg/d (NCG only). Out: NCG_TO_AB 5 kg/d (NCG).

2. Size.
- Duct at 10 m/s. Gas 0.1736 m³/h. Bore 2 mm, DN15. Not a packed tower.

3. Material. Carbon steel. Hydrocarbon. No aqueous chloride in this vessel. Corrosion allowance 1.5 mm. Pit rate is not measured.

4. Nozzles. Line list. Origin 5200, 12200, -6000 mm. Size 80 × 80 × 800 mm. Atmospheric lines are hose. DN is copied from the edge and is not recalculated.

| Tag | Stream | From | To | End | Face | xyz mm | Height mm | Size | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | IA-OIL-03 | OIL_FRAC | NCG_HEADER | inlet | -Y | 5240, 12200, -5600 | 400 | bore not calculated | hose, atmospheric |
| L2 | NCG_TO_AB | NCG_HEADER | AFTERBURNER | outlet | +Y | 5240, 12280, -5600 | 400 | bore not calculated | hose, atmospheric |
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/NCG_HEADER.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. Gas volume uses 1.2 kg/m³ because the edge has no m³/h. Duct bore uses 1.2 kg/m³.
