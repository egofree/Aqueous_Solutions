# Dual heat ladder

Document number: AQS-HEAT-LADDER-001
Revision: A
Date: 2026-10-25
Authority: plant flow graph Rev AC. Edge duties are held in the graph. Not a PE stamp.

| Rev | Description | Date |
|---|---|---|
| A | First issue under the documentation style guide (AQS-DOC-002). It consolidates the text dated 2026-10-02, with tier notes updated for graph Rev K on 2026-10-07, heater ratings and Q4 sinks for graph Rev M on 2026-10-08, and checks against graph Rev BH on 2026-10-12 and graph Rev AC on 2026-10-24. The earlier text is in the git history. No rate change. | 2026-10-25 |

## 1. Purpose and scope

The plant recovers waste heat from its hot processes and reuses it in cooler ones. The heat ladder is the system that does this. It has four temperature tiers, Q1 (hottest) to Q4 (coolest). Each tier has a heat battery, which is an insulated store that holds heat as a rise in the temperature of its fluid. Heat passes only from a hotter tier to the next cooler one. The plant has two identical ladders, so that either one can carry the plant while the other is isolated.

This page sets the tiers, the rule that keeps heat moving down the ladder, the names of the batteries, and where the duties and the placement are recorded. The duty of each heat-ladder edge (the `HL-*` and `XL-*` streams) is held in the plant flow graph and calculated in AQS-DUTY-008 (`HEAT_LADDER_DUTIES.md`). This page does not restate those duties.

The ladder replaces an earlier arrangement in which heat from Q1, Q2 and Q3 was sent straight to the Q4 water header, Q4_BUS, by edges with no equipment behind them.

## 2. Tiers

Table 2.1 lists the four tiers, the heat sources in each band, the fluid in each battery, and where the heat goes.

Table 2.1. Heat ladder tiers

| Tier | Sources | Fluid | Heat goes to |
|---|---|---|---|
| Q1 | Flue gas and the afterburner | Thermal oil or a ceramic store | The Q1 battery. Never to habitation air and never to Q4_BUS. |
| Q2 | Glass burnout and the pyrolyzer jacket | Thermal oil | The Q2 battery |
| Q3 | Only the downhill step from Q2 | Water, below 120 °C | The Q3 battery, which supplies the dryer exchanger HX-4, the digester exchanger HX-6 and the leach exchanger HX-5 |
| Q4 | Life support and the farm; heat rejected by electrowinning (EW) through HX-8, which preheats the Q4 return water | Water, below 80 °C | The Q4 battery, then Q4_BUS |

Q3 has no heat source of its own. The exchanger HX-8 in the electrowinning aisle works at 40 °C to 60 °C, which is too cool to put heat into Q3. Since graph Rev J it preheats the water returning to Q4_A and Q4_B, on edges HL-HX8-Q4-A and HL-HX8-Q4-B. The Q3 process draws are the edges HL-Q3-A-HX4, HL-Q3-A-HX5 and HL-Q3-A-HX6 and the matching edges on ladder B. The edges HL-HX8-Q3-A and HL-HX8-Q3-B, which once carried HX-8 heat to Q3, are retired.

Two units have names that suggest heat recovery but are not part of the ladder. CONTINUOUS_RECYCLE is not a heat source. C29_RECYCLE is the pipe that returns the C29 oil cut to the pyrolyzer inlet.

The ground-source heat pump GEO_HP is the only unit that raises heat to a higher temperature. It supplies Q4 and the farm and does not push heat up the ladder. Heat from metal melting is recovered at Q4 through MET_HX_Q4 (stream S63 to Q4_BUS); it is not raised into a hotter tier (`notes/LOAD_ROLLUP.md`).

The test `test_heat_ladder_moves_heat_down_only` in `flow_graph/test_doc_consistency.py` checks the graph against these rules. It fails if a present edge carries heat up the ladder, if an edge from Q1, Q2 or Q3 lands on Q4_BUS, if HX-8 feeds Q3, or if GEO_HP feeds any tier other than Q4.

## 3. Two ladders

Ladder A is west of the building core and ladder B is east of it. Both have the same four tiers. Either ladder can carry the plant while the other is isolated.

Each tier on each ladder has:

- a heat battery that stores sensible heat;
- a source exchanger that puts heat into the battery;
- a downhill heat pipe to the next cooler tier;
- a cross-tie to the same tier on the other ladder.

The Q1 battery is not a water tank. The Q4 battery holds water and is the only tier that may feed Q4_BUS.

## 4. Rule that keeps heat moving down

No valve on the ladder can move heat to a higher temperature; only a heat pump can do that. The control rule below therefore only opens a path from a hotter store to a cooler one. Each comparison uses a deadband of 5 K, and there is no valve in the uphill direction.

The downhill valve from tier n to tier n + 1 on ladder A (and in the same way on ladder B) opens only if

\[
T_{A,n} > T_{A,n+1} + 5\,\mathrm{K}
\]

where \(T_{A,n}\) is the temperature of the tier n battery on ladder A.

The cross-tie between the two ladders opens only in the direction from the hotter ladder:

\[
T_{A,n} > T_{B,n} + 5\,\mathrm{K} \Rightarrow A \to B
\]

\[
T_{B,n} > T_{A,n} + 5\,\mathrm{K} \Rightarrow B \to A
\]

If the two batteries are within the 5 K deadband, the cross-tie stays shut. A failed temperature sensor closes its valve.

The heat pipe is the hardware that allows flow in one direction only. Its evaporator is in the upper, hotter battery, its condenser is in the lower, cooler battery, and a check valve is fitted on the liquid return. The valves isolate the heat pipe and open the cross-tie; they do not create the temperature difference.

## 5. Names

The batteries are Q1_A, Q1_B, Q2_A, Q2_B, Q3_A, Q3_B, Q4_A and Q4_B. Q4_BUS is the Q4 water header. No other unit is given a name on this ladder.

## 6. Duties

The duty, medium, supply and return temperatures, flow and line size of every heat-ladder edge are in AQS-DUTY-008 (`HEAT_LADDER_DUTIES.md`, Rev C, for graph Rev K) and are written to each `HL-*` edge in the graph. When the Q3 process draws are running, Q3 is fully used and the step from Q3 to Q4 carries 0 kW. The shortfall is met by electric trim heaters at the process (AQS-DUTY-008 section 13).

Each downhill step is a gravity-loop thermosyphon. The evaporator is high in the hotter store and the condenser is low in the cooler store. The cooler store is raised so that the condensate leg rises at least 0.30 m. The base elevations are Q1 at −6000 mm, Q2 at −5150 mm, Q3 at −4250 mm and Q4 at −3350 mm (AQS-DUTY-008 section 14.2). Each cross-tie is a pumped single-phase loop, XL-Q1 to XL-Q4. It is normally off and runs only when the two ladders differ by more than 5 K (AQS-DUTY-008 section 14.3).

The electric trim heaters were rated at graph Rev M (AQS-DUTY-011; AQS-DUTY-008 Rev D section 15): 6.0 kW for the leach exchanger HX-5 and 2.5 kW for the digester exchanger HX-6. Besides the life-support load, Q4_BUS has three sinks: HX-9, which preheats the leach make-up water (S100); HX-10, which preheats the digester caustic (S101); and the recharge of the borefield GEO_GHEX (S102). These are branches of Q4_BUS; the `HL-*` edges still carry the ladder path. The pad for an organic Rankine cycle (ORC) unit is reserved at 0 kW.

## 7. Placement

The eight batteries have rows in `flow_graph/placement_seed.json` (AQS-PLACE-SEED-001 Rev H, unchanged in Rev I). Each has an issued envelope of 800 mm × 800 mm × 1200 mm. They stand in a row at level L-1 at a pitch of 1500 mm, with the cooler tiers on steel stands of 0 mm, 850 mm, 1750 mm and 2650 mm. Ladder A is west of the core along the west wall. Ladder B is east of the core in the north-east bay. The plan origins are listed in AQS-DUTY-008 section 13.6 and the elevations in section 14.2.

## 8. Related documents

- AQS-DUTY-008 (`HEAT_LADDER_DUTIES.md`): edge duties of the heat ladder. Its current text is Rev C, written for graph Rev K, and it has not been reissued since.
- `flow_graph/plant_flow_graph.json`: the `HL-*` and `XL-*` edges and their duties.
- `flow_graph/test_doc_consistency.py`: the test that enforces the tier rules.
