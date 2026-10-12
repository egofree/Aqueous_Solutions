# Power module

Document number: AQS-PWR-001
Revision: B
Date: 2026-10-11
Not a PE stamp.

1. Basis. Feed every bay at 48 V DC. EW-1 is 2105 A at cell voltage, not at 48 V. The bay connector is the control and the small-load feed. The cell current is a separate rectifier.

2. Size. One bay connector is 48 V, 100 A, 4.8 kW. The shop rail is 20 kW, 417 A, five connectors. Lathe 1.1 kW, mill 1.1 kW, welder 5.0 kW, furnace 10 kW, sum 17.2 kW. The farm LEDs are 20 to 40 kW and do not fit this rail. They are a second rail, 40 kW, 833 A, bar 833/200 = 4.2 cm². EW-1 at 2.5 V and 2105 A is 5.3 kW from its own rectifier, not from either rail. Fault on the shop rail is the inverter limit, 1.25 × 417 = 521 A. Each SB350 fuse is 100 A. The 10 kA figure is the 480 V array bus only.

3. Material. Shop bar 417/200 = 2.1 cm² copper. Farm bar 4.2 cm². Enclosure is the dry frame, A500, 800 × 600 × 800. Two bars, not one.

4. Nozzles. Input from the 60 kW inverter, two conductors. Output is a row of SB350 on the +X face. EW rectifier output is a separate pair of bus bars, not an SB350.

5. Instruments. Bus voltage, bus current. Overcurrent opens the contactor. Each connector has a fuse.

6. Relief. None. Not a pressure vessel.

7. Code. Shop. Not stamped.

8. Open items. None on the fault. The 10 kA figure in ONE_LINE.md is the 480 V array bus. It is not this rail.

