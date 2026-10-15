# One line

Document number: AQS-ELEC-002
Renumbered 2026-10-15 from AQS-ELEC-001 to clear a duplicate (AQS-REG-001).
Revision: B
Date: 2026-10-12
Not a PE stamp.

Checked against graph Rev BH on 2026-10-12. IA-PV-01 is 27.88 kW, PV_ARRAY to SOL_ARK_60K. The 60 kW, 72 A, and 2 AWG figures are this page. They are not edges. No rate change.

1. Basis. The inverter is SOL_ARK_60K. The array average into it is 27.88 kW (IA-PV-01). The node nameplate is 70 kW. The 400 kW figure is retired.

2. Size. 60 kW at 480 V three-phase is 60000 / (√3 × 480) = 72 A. Conductor is sized at 125%, 90 A. That is 2 AWG copper, not 500 kcmil. Fault current is the inverter limit, about 2 × 72 = 144 A. A 10 kA bus is not this machine.

3. Material. 2 AWG copper from the inverter to the 480 V breaker. The 48 V rails are in POWER.md.

4. Nozzles. Inverter AC out, one breaker, then the shop rectifier and the farm feed. No other tap on this page.

5. Instruments. AC current. Overcurrent opens the breaker.

6. Relief. None. Not a pressure part.

7. Code. Shop. Not stamped.

8. Open items. None on the current. The 400 kW conductor is withdrawn.
