# Heat-ladder edge duties

Document number: AQS-DUTY-008
Revision: A
Date: 2026-10-07
Authority: AQS-HEAT-LADDER-001 (`HEAT_LADDER.md`), AQS-FLOW-GRAPH-001 Rev I. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First-principles duties for the 20 HL-* edges and S67B; closes the presence "study" edges | 2026-10-07 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This note gives each of the 21 edges that carried presence "study" through graph Rev H a defined duty, medium, supply and return temperature, flow, and line size. The values are written to each edge's `rate` and `params` in `flow_graph/plant_flow_graph.json`. The calculation is `docs-authority/_hl_edges_study.py`, which reproduces every number below.

In scope are the 20 HL-* heat edges (two source exchangers per ladder, three downhill steps per ladder, two Q4 bus feeds, and eight cross-ties) and S67B, the CO₂-rich cut from FLUE_KO to CRYO_CO2. HX-8 (Q3) and the Q4 exchangers on Q4_BUS outside the ladder are not in scope. They are discussed only where the balance needs them.

## 2. Inputs

| Input | Value | Source |
|---|---|---|
| Plant rate | 150 kg/d wet feed, mixed WEEE | ELECTRICAL.md; AQS-AUD-001 |
| Afterburner CO₂ | 15.0 kg/d (study) | Graph S18; AQS-AUD-001 mid of 12–22.5 kg/d |
| Burnout cullet | 30 kg/d silicate + grit | Graph S08G; AQS-AUD-001 §4.1 |
| Burnout electric duty | 1.0 kW, issued | GLASS_BURNOUT params |
| Burnout bed | 450–550 °C | COMPLETION_DUTIES.md (AQS-DUTY-007) |
| Stores | Q1/Q2 oil 0.30 m³ at 250/150 °C; Q3 water 0.40 m³ at 100 °C; Q4 water 0.60 m³ at 70 °C; 800 × 800 × 1200 mm; 1/2 in thermal relief at 10 % above design | Graph Q*_A/B params; MVS_EQUIPMENT.md |
| Q4 header | Water, < 80 °C | HEAT_LADDER.md; Q4_BUS notes |
| Diode rule | 5 K deadband; no uphill valve; failed sensor fails shut | HEAT_LADDER.md |
| ORC | 0 kW_e when Q4 takes the heat | GEO_ORC params; HANDOFF_2026-10-02 |

## 3. Method

Pumped single-phase loops (the source exchangers and the Q4 bus feeds) use

\[
\dot Q = \dot m\,c_p\,\Delta T .
\]

Loop thermosyphons (the downhill steps and the cross-ties) move latent heat. A vapor riser runs from the evaporator in the source store to the condenser in the sink store, and the condensate returns through a check valve:

\[
\dot Q = \dot m\,h_{fg} .
\]

This is the two-phase form of the same energy equation. With 5 K of condensate subcooling, the sensible term adds less than 1 % and is neglected.

Store standing loss is

\[
\dot Q_{loss} = U\,\bar A\,(T_{store}-T_{amb}), \qquad U = \left(\frac{t}{k}+\frac{1}{h_o}\right)^{-1},
\]

where \(\bar A\) is the mean of the inner and outer insulated areas, \(h_o\) = 10 W/m²·K, and \(T_{amb}\) = 25 °C.

Rated duty is the governing single-ladder throughput (one ladder isolated, all source heat on the other) multiplied by 1.25. Normal duty is the steady value with both ladders on line and the sources split 50/50. Each edge's `rate.value` carries the rated duty.

Line sizes are chosen as follows:

- Pumped liquid: velocity at or below 1.0 m/s. DN15 is the mechanical minimum and governs every pumped line here.
- Vapor: velocity at or below 10 m/s, plus a pressure-drop check. Darcy vapor and condensate losses over the equivalent length must stay below half of the static head \(\rho_l g H\) at H = 0.8 m of rise.
- Equivalent length: 6 m for a downhill step and 25 m for a cross-tie across the core.

## 4. Sources

### 4.1 Afterburner (Q1, through HX-2)

The non-condensable gas is taken as the polyolefin pyrolysis class, by mass:

| Species | CH₄ | C₂H₄ | C₂H₆ | C₃H₆ | C₃H₈ |
|---|---:|---:|---:|---:|---:|
| Mass fraction | 0.25 | 0.25 | 0.10 | 0.25 | 0.15 |

This mix gives:

- LHV = 47.5 MJ/kg;
- 3.00 kg CO₂ per kg of fuel;
- therefore 15.8 MJ released per kg of CO₂.

At the S18 basis:

\[
\dot Q_{rel} = 15.0\ \tfrac{kg}{d}\times 15.8\ \tfrac{MJ}{kg} = 2.74\ \mathrm{kW}, \qquad \dot m_{fuel} = 5.0\ \mathrm{kg/d}.
\]

This agrees with the pyrolyzer. Plastics at 15–30 % of 150 kg/d, with a 10–15 % NCG yield, give 2.2–6.8 kg/d of NCG.

The casing loses 5 %. The flue leaves the oxidizer at 850 °C (the 2 s class) with \(c_p\) = 1.13 kJ/kg·K, so \(\dot m_{flue}\) = 10.1 kg/h, an excess-air ratio of about 3. The flue train is:

| Step | Range °C | kW |
|---|---|---:|
| Casing loss | — | 0.137 |
| HX-7 burnout jacket (process heat to GLASS_BURNOUT) | 850 → 650 | 0.632 |
| HX-2 Q1 exchanger (HL-AFTERBURNER-Q1-A/B) | 650 → 300 | 1.106 |
| Flue to FLUE_KO (S67), rejected at the knockout | 300 → 25 | 0.869 |
| Sum / release | | 2.744 / 2.744 |

The 300 °C flue exit keeps a 50 K gas-side approach to the 250 °C Q1 store. The 180 m³/h NCG figure in AQS-GAS-003 is a header draft basis, not the fuel rate.

### 4.2 Glass burnout (Q2)

Heating the cullet from 25 to 500 °C takes 0.157 kW (30 kg/d, \(c_p\) = 0.95 kJ/kg·K).

Q2 recovers heat in two ways:

| Recovery | Basis | kW |
|---|---|---:|
| Oil recovery jacket behind 50 mm of mineral wool on the rotary | k = 0.08 W/m·K, 1.10 m², 500 → 140 °C | 0.634 |
| Cullet cooler | 500 → 170 °C | 0.109 |
| Total to Q2 | | 0.742 |

The burnout balance is:

- In: 0.632 kW of HX-7 flue plus 0.238 kW of electric trim, 0.870 kW in total.
- Out: 0.870 kW in total, made up of 0.157 kW cullet heat-up, 0.634 kW to the jacket, 0.03 kW off-gas sensible heat to the oil-vapor header, and 0.05 kW of end losses.

The trim is within the issued 1.0 kW.

## 5. Stores

| Store | Shape inside, m | Insulation | U W/m²·K | Loss kW |
|---|---|---|---:|---:|
| Q1_A/B | Ø0.62 × 1.00 (0.302 m³) | 90 mm microporous, k 0.025 | 0.27 | 0.200 |
| Q2_A/B | Ø0.62 × 1.00 (0.302 m³) | 90 mm microporous, k 0.025 | 0.27 | 0.111 |
| Q3_A/B | 0.68 × 0.68 × 0.88 (0.407 m³) | 60 mm mineral wool, k 0.035 | 0.55 | 0.174 |
| Q4_A/B | 0.74 × 0.74 × 1.10 (0.602 m³) | 30 mm PIR, k 0.025 | 0.77 | 0.164 |

All four fit the issued 800 × 800 × 1200 mm envelope. Q4 leaves only 30 mm for insulation, so it is envelope-limited.

## 6. Energy balance

Per ladder, the balance is:

\[
\dot Q_{in,n} = \dot Q_{src,n} + (1-\lambda)\,\dot Q_{down,n-1}, \qquad \dot Q_{down,n} = \dot Q_{in,n} - \dot Q_{loss,n},
\]

with a line loss of λ = 0.03 on each thermosyphon. HX-8 contributes 0 kW (see §9). There is no Q3 process draw on the ladder.

The tolerance is ±1 % of source heat (±0.018 kW).

### 6.1 Normal (both ladders, per ladder)

| Tier | Source in | From tier above | Line loss | Store loss | Down / to bus |
|---|---:|---:|---:|---:|---:|
| Q1 | 0.553 | 0.000 | 0.000 | 0.200 | 0.353 |
| Q2 | 0.371 | 0.342 | 0.011 | 0.111 | 0.603 |
| Q3 | 0.000 | 0.585 | 0.018 | 0.174 | 0.411 |
| Q4 | 0.000 | 0.398 | 0.012 | 0.164 | 0.234 |

Plant total:

- Sources: 1.106 + 0.742 = 1.848 kW.
- Sinks: 0.468 kW to Q4_BUS, 1.298 kW of store losses and 0.082 kW of line losses, also 1.848 kW in total.
- Residual: 0.000 kW.

### 6.2 Single ladder (B isolated; sizing case)

| Tier | Source in | From tier above | Line loss | Store loss | Down / to bus |
|---|---:|---:|---:|---:|---:|
| Q1 | 1.106 | 0.000 | 0.000 | 0.200 | 0.906 |
| Q2 | 0.742 | 0.879 | 0.027 | 0.111 | 1.510 |
| Q3 | 0.000 | 1.465 | 0.045 | 0.174 | 1.291 |
| Q4 | 0.000 | 1.252 | 0.039 | 0.164 | 1.088 |

Plant total:

- Sources: 1.848 kW.
- Sinks: 1.088 kW to Q4_BUS, 0.649 kW of store losses and 0.111 kW of line losses, also 1.848 kW in total.
- Residual: 0.000 kW.

The isolated ladder's standing loss is drawn from its own inventory and is not a steady term.

Running one ladder delivers 1.09 kW to Q4_BUS against 0.47 kW with both on line, because store losses are halved. Lead/standby operation is recommended. It is not locked.

The ladder never exceeds the 3.0 kW_th Q4 life priority, so Q_surplus after Q4 is 0 and GEO_ORC stays at 0 kW_e.

## 7. Edge register

| Edge | Source → sink | Rated kW | Normal kW | Medium | Supply / return °C | Flow | Line |
|---|---|---:|---:|---|---|---|---|
| HL-AFTERBURNER-Q1-A | AFTERBURNER → Q1_A | 1.38 | 0.55 | thermal oil (pumped) | 220 / 250 | 72.1 kg/h (1.38 L/min) | DN15, 0.117 m/s |
| HL-AFTERBURNER-Q1-B | AFTERBURNER → Q1_B | 1.38 | 0.55 | thermal oil (pumped) | 220 / 250 | 72.1 kg/h (1.38 L/min) | DN15, 0.117 m/s |
| HL-GLASS_BURNOUT-Q2-A | GLASS_BURNOUT → Q2_A | 0.93 | 0.37 | thermal oil (pumped) | 120 / 150 | 55.7 kg/h (1.0 L/min) | DN15, 0.085 m/s |
| HL-GLASS_BURNOUT-Q2-B | GLASS_BURNOUT → Q2_B | 0.93 | 0.37 | thermal oil (pumped) | 120 / 150 | 55.7 kg/h (1.0 L/min) | DN15, 0.085 m/s |
| HL-Q1-A-DOWN | Q1_A → Q2_A | 1.13 | 0.35 | DPO/biphenyl eutectic (two-phase) | 200 / 195 | 13.15 kg/h (12.468 m³/h vapor) | DN25, 6.21 m/s; return DN15 |
| HL-Q1-B-DOWN | Q1_B → Q2_B | 1.13 | 0.35 | DPO/biphenyl eutectic (two-phase) | 200 / 195 | 13.15 kg/h (12.468 m³/h vapor) | DN25, 6.21 m/s; return DN15 |
| HL-Q2-A-DOWN | Q2_A → Q3_A | 1.89 | 0.60 | water (two-phase, steel) | 125 / 120 | 3.11 kg/h (2.462 m³/h vapor) | DN15, 3.49 m/s; return DN15 |
| HL-Q2-B-DOWN | Q2_B → Q3_B | 1.89 | 0.60 | water (two-phase, steel) | 125 / 120 | 3.11 kg/h (2.462 m³/h vapor) | DN15, 3.49 m/s; return DN15 |
| HL-Q3-A-DOWN | Q3_A → Q4_A | 1.61 | 0.41 | water (two-phase, copper) | 85 / 80 | 2.53 kg/h (7.242 m³/h vapor) | DN20, 5.85 m/s; return DN15 |
| HL-Q3-B-DOWN | Q3_B → Q4_B | 1.61 | 0.41 | water (two-phase, copper) | 85 / 80 | 2.53 kg/h (7.242 m³/h vapor) | DN20, 5.85 m/s; return DN15 |
| HL-Q4-A-BUS | Q4_A → Q4_BUS | 1.36 | 0.23 | water (pumped) | 65 / 45 | 58.6 kg/h (0.99 L/min) | DN15, 0.084 m/s |
| HL-Q4-B-BUS | Q4_B → Q4_BUS | 1.36 | 0.23 | water (pumped) | 65 / 45 | 58.6 kg/h (0.99 L/min) | DN15, 0.084 m/s |
| HL-Q1-X | Q1_A → Q1_B | 1.38 | 0.00 | DPO/biphenyl eutectic (two-phase) | 245 / 240 | 17.16 kg/h (5.71 m³/h vapor) | DN20, 4.61 m/s; return DN15 |
| HL-Q1-X-BA | Q1_B → Q1_A | 1.38 | 0.00 | DPO/biphenyl eutectic (two-phase) | 245 / 240 | 17.16 kg/h (5.71 m³/h vapor) | DN20, 4.61 m/s; return DN15 |
| HL-Q2-X | Q2_A → Q2_B | 2.03 | 0.00 | water (two-phase, steel) | 145 / 140 | 3.42 kg/h (1.592 m³/h vapor) | DN15, 2.26 m/s; return DN15 |
| HL-Q2-X-BA | Q2_B → Q2_A | 2.03 | 0.00 | water (two-phase, steel) | 145 / 140 | 3.42 kg/h (1.592 m³/h vapor) | DN15, 2.26 m/s; return DN15 |
| HL-Q3-X | Q3_A → Q3_B | 1.83 | 0.00 | water (two-phase, copper) | 95 / 90 | 2.91 kg/h (5.845 m³/h vapor) | DN15, 8.28 m/s; return DN15 |
| HL-Q3-X-BA | Q3_B → Q3_A | 1.83 | 0.00 | water (two-phase, copper) | 95 / 90 | 2.91 kg/h (5.845 m³/h vapor) | DN15, 8.28 m/s; return DN15 |
| HL-Q4-X | Q4_A → Q4_B | 1.56 | 0.00 | water (two-phase, copper) | 65 / 60 | 2.40 kg/h (15.008 m³/h vapor) | DN25, 7.48 m/s; return DN15 |
| HL-Q4-X-BA | Q4_B → Q4_A | 1.56 | 0.00 | water (two-phase, copper) | 65 / 60 | 2.40 kg/h (15.008 m³/h vapor) | DN25, 7.48 m/s; return DN15 |
| S67B | FLUE_KO → CRYO_CO2 | 0.048 (cold-box load) | — | dry CO₂-rich cut, ≥ 90 mol % | 30 at 1.3 bar a | 12.75 kg/d CO₂, 13.68 kg/d total (0.3007 Nm³/h) | DN15 316L, 0.368 m/s |

Rated duty is the single-ladder value × 1.25. Cross-ties are rated for the full single-ladder input to their tier. Their normal duty is 0, because the 5 K deadband keeps them shut when the two ladders track each other.

Media:

- Source loops: synthetic thermal oil, hydrogenated-terphenyl class, in welded carbon steel.
- Q1 thermosyphons: biphenyl/diphenyl-oxide eutectic (Dowtherm A class). It runs sub-atmospheric at 0.25–0.78 bar a, which avoids the 15–40 bar of water at Q1 temperature.
- Q2 thermosyphons: deaerated water in steel.
- Q3/Q4 thermosyphons: deaerated water in copper.

## 8. Checks

Thermosyphon pressure drop. Vapor plus condensate loss is 69–993 Pa against 6.8–7.7 kPa of head at 0.8 m rise, so every loop is below half the head. The condenser coil shall sit at least 0.8 m above the evaporator coil: evaporator low in the source store, condenser high in the sink store.

Sealed-loop design pressure is the saturation pressure at the source store's relief temperature (nominal + 10 %):

| Loop | Relief temperature | Design pressure, bar a |
|---|---|---:|
| Q1 eutectic | 275 °C | 1.45 |
| Q2 water | 165 °C | 7.0 |
| Q3 water | 110 °C | 1.43 |
| Q4 water | 77 °C | 0.42 |

All loops shall also be rated for full vacuum.

Thermal relief. Blocked-in expansion at rated duty, \(\beta\dot Q/(\rho c_p)\), is 2.1 L/h on the Q1 loop, 1.4 L/h on Q2 and 0.6 L/h on the Q4 bus feed. The existing 1/2 in thermal relief covers this by a wide margin.

## 9. S67B

FLUE_KO does the following:

1. Quenches and knocks out the 300 °C flue to 30 °C. Condensate leaves as S68.
2. Pre-dries the gas on an alumina layer.
3. Separates the CO₂-rich cut on a two-bed VSA on zeolite 13X, at 0.85 recovery and at least 90 mol % CO₂.

N₂, O₂ and NOx are rejected at FLUE_KO.

The cut:

- 15.0 × 0.85 = 12.75 kg/d CO₂, 13.7 kg/d total, 0.30 Nm³/h;
- 30 °C, 1.3 bar a, dew point −40 °C or lower;
- in 1/2 in (DN15) 316L tube, at 0.37 m/s against a 10 m/s basis.

The sink duty on CRYO_CO2 is the cooling from 30 to −20 °C plus condensation at about 20 bar (282 kJ/kg): 0.048 kW. 2.25 kg/d of CO₂ leaves with the reject.

## 10. Locks

Every lock is respected:

- Heat moves only on HL-* edges.
- Q4_BUS receives water from Q4_A/Q4_B only.
- Cross-ties open only above 5 K, from the hotter store.
- CONTINUOUS_RECYCLE is not on the ladder.
- No unit was renamed. The source exchangers are HX-2 and HX-7 as named in the glossary.
- ORC is 0 kW_e.

## 11. Decisions

The following design choices were made in this study:

1. Rated duty is single-ladder × 1.25. `rate.value` carries the rated duty.
2. Downhill steps and cross-ties are loop thermosyphons, with the media named in §7.
3. HL-* edges move to the thermal layer (EFD layer B).
4. FLUE_KO separates the CO₂-rich cut by VSA on 13X at 0.85 recovery.
5. Presence stays `present` | `placeholder`. "study" is not a permanent class: every one of the 21 edges closes with a defined duty, source, sink and size.

## 12. Findings for decision

1. **HX-8 cannot charge Q3.** EW liquor and anode-hood gas run at 40–60 °C (FAN_STACK.md). The Q3 store runs at 80–120 °C, so HX-8 gives 0 kW to Q3 under the no-lift rule. HX-8 belongs on Q4 unless the EW aisle runs hot. This conflicts with the glossary "Heat rule".
2. **S18 and S67B are the same carbon.** S18 (AFTERBURNER → CRYO_CO2, 15 kg/d) predates the Rev E flue split. Counting both double-claims CO₂ at CRYO_CO2. S67B carries the gap flag `same_carbon_as_S18`.
3. **Q3 process draws are not graph edges.** HX-4 (dryer), HX-5 (leach) and HX-6 (digest) draw on Q3. Any such draw reduces Q3 → Q4 one-for-one. The rated duties cover the zero-draw case.
4. **Cross-tie coils are large at a 5 K approach.** At 5 K per coil they need 0.8–2.7 m² each, with the largest in the oil stores. The ladders still have no placement rows.
