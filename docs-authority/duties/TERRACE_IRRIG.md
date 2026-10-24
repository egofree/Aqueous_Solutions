# TERRACE_IRRIG

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 37.18 kg/d. Mass out 37.18 kg/d. Electrical duty 0.0000 kW. In: S40 37.18 kg/d (clean overflow). Out: S41 0 kg/d (rain + S40 return); S42 0 kg/d (dilute nutrient drain); IA-TERR-VAP 37.18 kg/d (greenhouse transpiration).

2. Size.
- In 37.18 kg/d, out 37.18 kg/d. Transpiration = irrigation - drains (AQS-PAR-003 Rev B T1; TAIZ2015). No CO2 supply and no harvest edge, so net photosynthetic fixation on this node is zero. No holdup claimed.

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
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/TERRACE_IRRIG.stl` is the outer envelope only; nothing inside it is modelled yet.

8. Open items. No holdup basis for this class.
