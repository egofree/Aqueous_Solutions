# TERRACE_IRRIG

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 40.00 kg/d. Mass out 40.00 kg/d. Electrical duty 0.0000 kW. In: S40 40.00 kg/d (clean overflow). Out: IA-TERR-VAP 40.00 kg/d (greenhouse transpiration).

2. Size.
- In 40.00 kg/d, out 40.00 kg/d. No holdup claimed.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Line list. Origin 0, -3000, 0 mm. Seed size 24000 × 400 mm has no height, so no face center is written. Atmospheric lines are hose. DN is copied from the edge and is not recalculated.

| Tag | Stream | From | To | End | Face | xyz mm | Height mm | Size | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | S40 | ROOF_TANK | TERRACE_IRRIG | inlet | — | — | — | bore not calculated | hose, atmospheric |
| L2 | IA-TERR-VAP | TERRACE_IRRIG | CRYO_AHU | outlet | — | — | — | bore not calculated | hose, atmospheric |
| L3 | S41 | TERRACE_IRRIG | CATCH_TANK | outlet | — | — | — | bore not calculated | hose, atmospheric |
| L4 | S42 | TERRACE_IRRIG | GREY_TREAT | outlet | — | — | — | bore not calculated | hose, atmospheric |
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/TERRACE_IRRIG.stl` is the box, not the internal. FreeCAD is not in this session.

8. Open items. No holdup basis for this class.
