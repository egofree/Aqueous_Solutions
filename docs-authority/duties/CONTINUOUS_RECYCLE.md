# CONTINUOUS_RECYCLE

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 3753.7 kg/d. Mass out 3753.7 kg/d. Electrical duty 0.0000 kW. In: IA-POL-02 3753.7 kg/d (raffinate (EW tail after polish) to continuous recycle). Out: IA-REC-01 3753.7 kg/d (continuous recycle liquor).

2. Size.
- Envelope 1500×60×60 mm, 0.0054 m³. That box over this flow would be 0.0345 h if it were full. It is not a residence time.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. Line list. Origin 5000, 4600, -2700 mm. Size 1500 × 60 × 60 mm. Atmospheric lines are hose. DN is copied from the edge and is not recalculated.

| Tag | Stream | From | To | End | Face | xyz mm | Height mm | Size | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | IA-POL-02 | POLISH_BANK | CONTINUOUS_RECYCLE | inlet | -Y | 5750, 4600, -2670 | 30 | bore not calculated | hose, atmospheric |
| L2 | IA-REC-01 | CONTINUOUS_RECYCLE | LEACH_CSTR_1 | outlet | +Y | 5750, 4660, -2670 | 30 | bore not calculated | hose, atmospheric |
5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped.

8. Open items. Envelope volume over flow is not a residence time. Bore was not calculated where the edge has no density and no line size.
