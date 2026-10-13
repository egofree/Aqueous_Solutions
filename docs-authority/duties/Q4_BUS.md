# Q4_BUS

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0.0000 kg/d. Mass out 0.0000 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- No mass throughput. No volume is invented.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Line list. Origin 12000, 0, 0 mm. Size 10000 × 80 × 80 mm. Atmospheric lines are hose. DN is copied from the edge and is not recalculated.

| Tag | Stream | From | To | End | Face | xyz mm | Height mm | Size | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | HL-Q4-A-BUS | Q4_A | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | DN15 | hose, atmospheric |
| L2 | HL-Q4-B-BUS | Q4_B | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | DN15 | hose, atmospheric |
| L3 | IA-ZNBR-HEAT | ZNBR2 | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L4 | S44 | GEO_HP | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L5 | S53 | FUEL_CELL | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L6 | S54 | CRYO_HX_Q4 | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L7 | S63 | MET_HX_Q4 | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L8 | S80 | MEOH_FC | Q4_BUS | inlet | -Y | 17000, 0, 40 | 40 | bore not calculated | hose, atmospheric |
| L9 | HL-Q4-REJ | Q4_BUS | GEO_ORC | outlet | +Y | 17000, 80, 40 | 40 | bore not calculated | hose, atmospheric |
| L10 | IA-Q4-LIFE | Q4_BUS | HABITATION | outlet | +Y | 17000, 80, 40 | 40 | bore not calculated | hose, atmospheric |
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. No valve. Open to the process, not the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.

7. Code. Shop. Not stamped.

8. Open items. No mass edge. Bore was not calculated where the edge has no density and no line size.
