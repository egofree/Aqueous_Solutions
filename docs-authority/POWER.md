# Power module

Document number: AQS-PWR-001
Revision: C
Date: 2026-10-15
Not a PE stamp.

Checked against graph Rev BH on 2026-10-15. Current for the EW-1 current. The graph node EW_1 `continuous_kw` is 5.263 kW, study: 2105 A at 2.5 V. That is the one authoritative figure. This page and `duties/EW_1.md` copy it. Rev C replaced the 6.0 kW RECT-EW class share, which had no arithmetic behind it. The shop rail, the farm rail, and the lathe, mill, welder, and furnace loads are this page. They are not edges. No rate was changed.

1. Basis. Feed every bay at 48 V DC. EW-1 is 2105 A at cell voltage, not at 48 V. The bay connector is the control and the small-load feed. The cell current is a separate rectifier.

2. Size. One bay connector is 48 V, 100 A, 4.8 kW. The shop rail is 20 kW, 417 A, five connectors. Lathe 1.1 kW, mill 1.1 kW, welder 5.0 kW, furnace 10 kW, sum 17.2 kW. The farm LEDs are 20 to 40 kW and do not fit this rail. They are a second rail, 40 kW, 833 A, bar 833/200 = 4.2 cm². EW-1 at 2.5 V and 2105 A is 5.263 kW from its own rectifier, not from either rail. Basis: IA-EW-MET-1, 59.87 kg/d, taken as copper at 0.02844 kg/d per A, 59.87 / 0.02844 = 2105 A. Current efficiency 1.0 is assumed. The 2.5 V is the duty cell voltage, not a measurement. EW rectifier output bar at the shop rule of 200 A/cm²: 2105 / 200 = 10.5 cm² copper per pole, two poles. Fault current on that bar is not calculated; the rectifier limit is not on the node. Fault on the shop rail is the inverter limit, 1.25 × 417 = 521 A. Each SB350 fuse is 100 A. The 10 kA figure is the 480 V array bus only.

3. Material. Shop bar 417/200 = 2.1 cm² copper. Farm bar 4.2 cm². Enclosure is the dry frame, A500, 800 × 600 × 800. Two bars, not one.

4. Nozzles. Input from the 60 kW inverter, two conductors. Output is a row of SB350 on the +X face. EW rectifier output is a separate pair of bus bars, not an SB350.

5. Instruments. Bus voltage, bus current. Overcurrent opens the contactor. Each connector has a fuse.

6. Relief. None. Not a pressure vessel.

7. Code. Shop. Not stamped.

8. Open items. None on the fault. The 10 kA figure in ONE_LINE.md is the 480 V array bus. It is not this rail. IA-E-RECT, the energy edge into EW_1, stays 4.57 kW and does not equal the 5.263 kW node. The edge rate was not changed. The RECT-EW row in `ELECTRICAL.md`, 0–250 A, does not cover 2105 A. Rectifier selection waits on that.
