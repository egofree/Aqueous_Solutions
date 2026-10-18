# Dual heat ladder

Document: AQS-HEAT-LADDER-001
Date: 2026-10-02 (duty and tier notes updated 2026-10-07, graph Rev K; heater ratings and Q4 sinks 2026-10-08, graph Rev M)
Not a PE stamp. Replaces the ghost edges that dumped Q1/Q2/Q3 onto Q4_BUS.

Checked against graph Rev BH on 2026-10-12. HL-HX8-Q4-A and HL-HX8-Q4-B are present, HX8 to Q4_A and Q4_B, 2.286 kW each. HL-Q3-A/B-HX4, HX5, and HX6 are present. No present edge from Q1, Q2, or Q3 lands on Q4_BUS. The date line records the Rev K text. `HEAT_LADDER_DUTIES.md` is still the Rev C note for graph Rev K. It was not re-issued. Edge duties are the graph. No rate change.

## Tiers

Heat moves down only. A valve is not a heat pump.

| Tier | Band | Fluid | Lands on |
|---|---|---|---|
| Q1 | flue, afterburner | thermal oil or ceramic | Q1 battery. Never hab air. Never Q4_BUS. |
| Q2 | glass burnout, pyro jacket | thermal oil | Q2 battery |
| Q3 | downhill from Q2 only | water, <120 °C | Q3 battery; draws HX-4 dryer, HX-6 digest, HX-5 leach |
| Q4 | life / farm; HX-8 EW reject (Q4 return preheat) | water, <80 °C | Q4 battery, then Q4_BUS |

Q3 has no source of its own. HX-8 on the EW aisle (40–60 °C) cannot lift into Q3; since graph Rev J it preheats the Q4 return into Q4_A/Q4_B (HL-HX8-Q4-A/B). The Q3 process draws are HL-Q3-*-HX4/HX5/HX6. CONTINUOUS_RECYCLE is not a heat source and is not this ladder. C29_RECYCLE is the C29 cut pipe to the pyrolyzer inlet.

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

## Duties

Edge duties, media, supply and return temperatures, flows, and line sizes are in AQS-DUTY-008 (`HEAT_LADDER_DUTIES.md`, Rev C for graph Rev K), written to each HL-* edge in the graph. With the Q3 draws running, Q3 is fully drawn and the Q3 → Q4 step carries 0; the shortfall is electric trim at the process (AQS-DUTY-008 §13). Each downhill step is a gravity loop thermosyphon: evaporator high in the hotter store, condenser low in the colder store, and the colder store raised so the condensate leg rises at least 0.30 m (Q1 z −6000, Q2 −5150, Q3 −4250, Q4 −3350 mm; AQS-DUTY-008 §14.2). Each cross-tie is a pumped single-phase loop (XL-Q1..Q4), normally off, run only when the two ladders differ by more than 5 K (§14.3).

Graph Rev M (AQS-DUTY-011, AQS-DUTY-008 Rev D §15): the electric trim heaters are rated HX-5 leach 6.0 kW and HX-6 digest 2.5 kW. Q4_BUS, the Q4 water header, now has three sinks besides the life load: HX-9 leach make-up preheat (S100), HX-10 digest caustic preheat (S101) and borefield recharge to GEO_GHEX (S102). These are Q4_BUS branches; the HL-* edges still own the ladder path. The ORC pad stays reserved at 0 kW.

## Placement

The eight batteries have seed rows in `flow_graph/placement_seed.json` (AQS-PLACE-SEED-001 Rev H; unchanged in Rev I), 800 × 800 × 1200 mm issued envelope, 1500 mm pitch in a row at L-1, colder tiers on steel stands (0 / 850 / 1750 / 2650 mm). Ladder A sits west of the core along the west wall, ladder B east of the core in the north-east bay. Plan origins are listed in AQS-DUTY-008 §13.6; elevations in §14.2.
