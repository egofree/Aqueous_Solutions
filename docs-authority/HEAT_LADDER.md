# Dual heat ladder

Document: AQS-HEAT-LADDER-001
Date: 2026-10-02
Not a PE stamp. Replaces the ghost edges that dumped Q1/Q2/Q3 onto Q4_BUS.

## Tiers

Heat moves down only. A valve is not a heat pump.

| Tier | Band | Fluid | Lands on |
|---|---|---|---|
| Q1 | flue, afterburner | thermal oil or ceramic | Q1 battery. Never hab air. Never Q4_BUS. |
| Q2 | glass burnout, pyro jacket | thermal oil | Q2 battery |
| Q3 | HX-8 EW residual | water or oil, <120 °C | Q3 battery |
| Q4 | life / farm | water, <80 °C | Q4_BUS |

Q3 source is HX-8 on the EW aisle. CONTINUOUS_RECYCLE is not a heat source and is not this ladder. C29_RECYCLE is the C29 cut pipe to the pyrolyzer inlet.

GEO_HP is the only lift. It feeds Q4 and the farm. It does not push heat back up the ladder.

## Two ladders

Ladder A, west of the core. Ladder B, east of the core. Same four tiers. Either ladder carries the plant while the other is isolated.

Each tier has:

- a heat battery (sensible store)
- a source exchanger into that battery
- a downhill heat pipe to the next tier
- a cross-tie to the same tier on the other ladder

Q1 battery is not a water tank. Q4 battery is water and is the only tier that may feed Q4_BUS.

## Diode rule

Deadband 5 K. No uphill valve.

Down valve A (same on B) opens only if

\[
T_{A,n} > T_{A,n+1} + 5\,\mathrm{K}
\]

Cross-tie opens only from the hotter ladder:

\[
T_{A,n} > T_{B,n} + 5\,\mathrm{K} \Rightarrow A \to B
\]

\[
T_{B,n} > T_{A,n} + 5\,\mathrm{K} \Rightarrow B \to A
\]

If the two batteries are inside the deadband, the cross-tie stays shut. A failed sensor fails the valve shut.

The heat pipe is the hardware diode: evaporator on the upper battery, condenser on the lower, check on the liquid return. The valve is the isolation and the cross-tie, not the thing that creates the temperature rise.

## Names

Q1_A, Q1_B, Q2_A, Q2_B, Q3_A, Q3_B, Q4_A, Q4_B are the batteries. Q4_BUS is the Q4 water header. No other unit is renamed onto this ladder.
