# Protection and coordination

Document number: AQS-ELEC-006
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-07; one-line AQS-ELEC-002 Rev C. Script `docs-authority/_protection.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-057 to A-M-059).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Inverter-limited fault, device types and settings, selectivity, DC channels, IEEE 80 check. | 2026-10-15 |
| B | X-RSZ-02: three inverters (180 kW). Fault 433 A; main 300 A; GPR 494 V; bare-soil touch fails, crushed rock required everywhere on the grid. | 2026-10-15 |

## 1. Available fault current

All AC sources sit behind SOL_ARK_60K, 4 × 60 kW (X-PAR-07, was 3 × 60 kW under X-RSZ-02). Rated 288.7 A at 480 V; fault contribution 2 × rated = 577 A (study; AQS-ELEC-002 Rev B method). No utility service is on the graph. If one is added, this study is redone.

## 2. Device rule

A thermal-magnetic breaker clears instantly only if its magnetic pickup is below the available fault. With 5× low-instantaneous trip units, every feeder up to 25 A meets that (pickup ≤ 0.8 × 433 A = 346 A; every feeder to 60 A qualifies). Larger feeders use electronic trip units with short-time pickup 1.5 × rating and 0.1 s delay:

| Bus | Load | Breaker A | Fault A | Device | Pickup |
| --- | --- | --- | --- | --- | --- |
| MCC-1 480 V | CRYO_ASU | 40 | 144 | electronic trip, short-time pickup 1.5×, 0.1 s | 60 A |
| MCC-1 480 V | MFG_SHOP | 25 | 144 | electronic trip, short-time pickup 1.5×, 0.1 s | 38 A |
| SOL_ARK 480 V | RECT-EW (EW_1–EW_9) | 70 | 144 | electronic trip, short-time pickup 1.5×, 0.1 s | 105 A |
| SOL_ARK 480 V | RECTIFIER | 40 | 144 | electronic trip, short-time pickup 1.5×, 0.1 s | 60 A |

Bus main (100 A frame at the inverter output): electronic trip, long-time 100 A, short-time pickup 125 A, 0.3 s. Selective over the 0.1 s feeders by time. T-1 (30 kVA): primary 50 A, secondary 100 A per NEC 450.3(B).

## 3. DC

RECT-EW channels: rectifier current limit at 1.05 × channel rating as primary protection; DC fuses on both poles at 1.25 × channel rating (ungrounded DC, AQS-ELEC-005); insulation monitor alarms on first ground fault. 48 V rails per AQS-PWR-001 (SB350 100 A fuses). ZnBr₂ DC bus: fuse per string, rating from the X-ELS-05 storage sizing.

## 4. Earth fault, touch and step (closes the AQS-ELEC-005 hold)

Earth-fault current is bounded by the inverters, 433 A. Grid 1.14 Ω gives ground potential rise 494 V. Taking touch voltage ≤ GPR (conservative), clearing time 0.5 s (feeders clear in ≤ 0.1 s; margin), 50 kg body, IEEE 80-2013 equations 32 and 29:

| Surface | Tolerable touch V | Tolerable step V | GPR V | Result |
| --- | --- | --- | --- | --- |
| bare soil | 176 | 213 | 494 | fails |
| crushed rock 0.1 m, 3000 ohm m | 677 | 2216 | 494 | safe |

Crushed rock 0.1 m, ≥ 3000 Ω·m, is required (not margin) on every outdoor surface over the grid: yard, ZNBR2, MeOH train and the PV field. Indoors, slab rebar is bonded to the grid as an equipotential mat (AQS-ELEC-005). Main breaker 300 A (1.25 × 216.5 A).

## 5. Held

Inverter fault data from the vendor; device time-current curves of the chosen brand; re-run when X-ELS-05 changes the sources.
