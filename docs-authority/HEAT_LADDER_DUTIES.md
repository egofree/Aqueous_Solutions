# Heat-ladder edge duties

Document number: AQS-DUTY-008
Revision: C
Date: 2026-10-07
Authority: AQS-HEAT-LADDER-001 (`HEAT_LADDER.md`), AQS-FLOW-GRAPH-001 Rev K. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First-principles duties for the 20 HL-* edges and S67B; closes the presence "study" edges | 2026-10-07 |
| B | §2, §4.1, §6, §7, §12, §13 | Graph Rev J: HX-8 to Q4, Q3 draws HX-4/5/6 with electric trim, S18 credit retired, re-rated Q3/Q4, ladder placement Rev G | 2026-10-07 |
| C | §3, §8, §11, §13.3, §13.8, §14 | Graph Rev K: thermosyphon rise checked; downhill steps gravity on stepped stores, cross-ties pumped loops; HDR_CO2 consumer (AQS-DUTY-009) | 2026-10-07 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This note gives each of the 21 edges that carried presence "study" through graph Rev H a defined duty, medium, supply and return temperature, flow, and line size. The values are written to each edge's `rate` and `params` in `flow_graph/plant_flow_graph.json`. The calculation is `docs-authority/_hl_edges_study.py`, which reproduces every number below.

Rev B (§13) adds HX-8 on Q4, the Q3 process draws, the S18/S67B carbon fix and the ladder placement. In scope for Rev A are the 20 HL-* heat edges (two source exchangers per ladder, three downhill steps per ladder, two Q4 bus feeds, and eight cross-ties) and S67B, the CO₂-rich cut from FLUE_KO to CRYO_CO2. HX-8 (Q3) and the Q4 exchangers on Q4_BUS outside the ladder are not in scope. They are discussed only where the balance needs them.

## 2. Inputs

| Input | Value | Source |
|---|---|---|
| Plant rate | 150 kg/d wet feed, mixed WEEE | ELECTRICAL.md; AQS-AUD-001 |
| Afterburner CO₂ | 15.0 kg/d (study) | Graph S67 (S18 until Rev J); AQS-AUD-001 mid of 12–22.5 kg/d |
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
- Vapor: velocity at or below 10 m/s, plus a pressure-drop check. Darcy vapor and condensate losses over the equivalent length must stay below half of the static head \(\rho_l g H\) at H = 0.8 m of rise. Rev C: H is the actual rise on the stepped stores (§14.2); cross-ties are pumped (§14.3).
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

At the flue CO₂ basis (S67; S18 until Rev J):

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

with a line loss of λ = 0.03 on each thermosyphon. §6.1–6.2 are the idle case (EW, HX-8 and the Q3 draws off); they govern the Q1–Q3 step ratings. The running case with HX-8 on Q4 and the Q3 draws is §13.4.

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
| HL-Q4-A-BUS | Q4_A → Q4_BUS | 5.51 (Rev B; was 1.36) | 2.12 (running) | water (pumped) | 65 / 45 | 237.3 kg/h (4.01 L/min) | DN15, 0.341 m/s |
| HL-Q4-B-BUS | Q4_B → Q4_BUS | 5.51 (Rev B; was 1.36) | 2.12 (running) | water (pumped) | 65 / 45 | 237.3 kg/h (4.01 L/min) | DN15, 0.341 m/s |
| HL-Q1-X | Q1_A → Q1_B | 1.38 | 0.00 | DPO/biphenyl eutectic (two-phase) | 245 / 240 | 17.16 kg/h (5.71 m³/h vapor) | DN20, 4.61 m/s; return DN15 |
| HL-Q1-X-BA | Q1_B → Q1_A | 1.38 | 0.00 | DPO/biphenyl eutectic (two-phase) | 245 / 240 | 17.16 kg/h (5.71 m³/h vapor) | DN20, 4.61 m/s; return DN15 |
| HL-Q2-X | Q2_A → Q2_B | 2.03 | 0.00 | water (two-phase, steel) | 145 / 140 | 3.42 kg/h (1.592 m³/h vapor) | DN15, 2.26 m/s; return DN15 |
| HL-Q2-X-BA | Q2_B → Q2_A | 2.03 | 0.00 | water (two-phase, steel) | 145 / 140 | 3.42 kg/h (1.592 m³/h vapor) | DN15, 2.26 m/s; return DN15 |
| HL-Q3-X | Q3_A → Q3_B | 1.83 | 0.00 | water (two-phase, copper) | 95 / 90 | 2.91 kg/h (5.845 m³/h vapor) | DN15, 8.28 m/s; return DN15 |
| HL-Q3-X-BA | Q3_B → Q3_A | 1.83 | 0.00 | water (two-phase, copper) | 95 / 90 | 2.91 kg/h (5.845 m³/h vapor) | DN15, 8.28 m/s; return DN15 |
| HL-Q4-X | Q4_A → Q4_B | 1.56 | 0.00 | water (two-phase, copper) | 65 / 60 | 2.40 kg/h (15.008 m³/h vapor) | DN25, 7.48 m/s; return DN15 |
| HL-Q4-X-BA | Q4_B → Q4_A | 1.56 | 0.00 | water (two-phase, copper) | 65 / 60 | 2.40 kg/h (15.008 m³/h vapor) | DN25, 7.48 m/s; return DN15 |
| S67B | FLUE_KO → CRYO_CO2 | 0.048 (cold-box load) | — | dry CO₂-rich cut, ≥ 90 mol % | 30 at 1.3 bar a | 12.75 kg/d CO₂, 13.68 kg/d total (0.3007 Nm³/h) | DN15 316L, 0.368 m/s |

HL-Q3-*-DOWN normal is 0.41 kW idle and 0 with the Q3 draws running. Rev B adds HL-HX8-Q4-A/B and HL-Q3-*-HX4/HX5/HX6 (§13.5).

Rated duty is the single-ladder value × 1.25. Cross-ties are rated for the full single-ladder input to their tier. Their normal duty is 0, because the 5 K deadband keeps them shut when the two ladders track each other.

Media:

- Source loops: synthetic thermal oil, hydrogenated-terphenyl class, in welded carbon steel.
- Q1 thermosyphons: biphenyl/diphenyl-oxide eutectic (Dowtherm A class). It runs sub-atmospheric at 0.25–0.78 bar a, which avoids the 15–40 bar of water at Q1 temperature.
- Q2 thermosyphons: deaerated water in steel.
- Q3/Q4 thermosyphons: deaerated water in copper.

## 8. Checks

Thermosyphon pressure drop. Vapor plus condensate loss is 69–993 Pa against 6.8–7.7 kPa of head at 0.8 m rise, so every loop is below half the head. The condenser coil shall sit at least 0.8 m above the evaporator coil: evaporator low in the source store, condenser high in the sink store. Superseded in Rev C (§14): that layout gives 0.54–0.60 m on level stores and draws the cold bottom of the hot store. The downhill steps use stratification-correct coils on stepped stores; the cross-ties are pumped.

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

The sink duty on CRYO_CO2 is the cooling from 30 to −20 °C plus condensation at about 20 bar (282 kJ/kg): 0.048 kW. 2.25 kg/d of CO₂ leaves with the reject. Since Rev B, S67B is the only CRYO_CO2 credit for afterburner carbon; S18 carries 0 kg/d (§13.3).

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
2. Downhill steps and cross-ties are loop thermosyphons, with the media named in §7. Rev C (§14): downhill steps stay gravity thermosyphons on stepped stores; cross-ties are pumped single-phase loops XL-Q1..Q4.
3. HL-* edges move to the thermal layer (EFD layer B).
4. FLUE_KO separates the CO₂-rich cut by VSA on 13X at 0.85 recovery.
5. Presence stays `present` | `placeholder`. "study" is not a permanent class: every one of the 21 edges closes with a defined duty, source, sink and size.

## 12. Findings for decision

All four were applied in Rev B (§13).

1. **HX-8 cannot charge Q3.** EW liquor and anode-hood gas run at 40–60 °C (FAN_STACK.md). The Q3 store runs at 80–120 °C, so HX-8 gives 0 kW to Q3 under the no-lift rule. HX-8 belongs on Q4 unless the EW aisle runs hot. This conflicts with the glossary "Heat rule".
2. **S18 and S67B are the same carbon.** S18 (AFTERBURNER → CRYO_CO2, 15 kg/d) predates the Rev E flue split. Counting both double-claims CO₂ at CRYO_CO2. S67B carries the gap flag `same_carbon_as_S18`.
3. **Q3 process draws are not graph edges.** HX-4 (dryer), HX-5 (leach) and HX-6 (digest) draw on Q3. Any such draw reduces Q3 → Q4 one-for-one. The rated duties cover the zero-draw case.
4. **Cross-tie coils are large at a 5 K approach.** At 5 K per coil they need 0.8–2.7 m² each, with the largest in the oil stores. Rev F already had study rows for the ladders; they collided on the placed copy and are reissued in Rev G (§13.6).

## 13. Rev B (graph Rev J)

Rev B applies the four §12 findings. Every number below is reproduced by `python3 docs-authority/_hl_edges_study.py --rev-j`.

### 13.1 HX-8 moves to Q4

The EW aisle runs at 40–60 °C (FAN_STACK.md). HX-8 cannot lift that heat into Q3 (80–120 °C). It now preheats the Q4 return.

The duty is the net heat the EW cells must reject to hold the liquor at 55 °C. Inputs are EW_1 (6.0 kW, RECT-EW class share), the ELECTRICAL.md cell table and the mixed-WEEE EW energy split (Fe 790, Cu 137, other 80 kWh/t; "other" is taken at Zn).

Ohmic heat. The anode makes Cl₂ for the CRU, so the thermoneutral voltage is for MCl₂ → M + Cl₂. Current lost to H₂ (1 − CE) is charged at 2HCl → H₂ + Cl₂, which is 1.733 V:

\[
V_{tn} = \frac{-\left(\Delta H_f(\mathrm{M^{2+}}) + 2\,\Delta H_f(\mathrm{Cl^-})\right)}{2F}, \qquad
\dot Q_{ohm} = P\left(1 - \frac{CE\,V_{tn} + (1-CE)\,1.733}{V_{cell}}\right).
\]

| Metal | V_cell | CE | V_tn | Heat fraction | Share kW | Heat kW |
|---|---:|---:|---:|---:|---:|---:|
| Fe | 3.1 | 0.80 | 2.195 | 0.322 | 4.707 | 1.515 |
| Cu | 2.2 | 0.85 | 1.397 | 0.342 | 0.816 | 0.279 |
| Zn (other) | 3.4 | 0.80 | 2.530 | 0.303 | 0.477 | 0.144 |
| Total | | | | | 6.000 | 1.938 |

Cell balance at 55 °C:

| Term | Basis | kW |
|---|---|---:|
| Ohmic heat | above | +1.938 |
| Concentrate sensible | 0.17 m³/h × 1050 kg/m³ × 3.7 kJ/kg·K = 0.1835 kW/K, from the 77.5 °C leach to 55 °C | +4.128 |
| Cell walls | 9 cells, 14.2 m², 12 mm CPVC + 25 mm closed-cell lagging, U = 1.25 W/m²·K, 30 K | −0.533 |
| Surface evaporation | 2.27 m² open liquor, (25 + 19v)·A·Δx at 0.3 m/s hood air: 7.3 kg/h bare (4.81 kW), cut 80 % by a PP ball blanket | −0.962 |
| HX-8 duty | | **4.572** |

HX-8 is a titanium plate exchanger:

- Liquor side: 55 → 51 °C, 1112 kg/h.
- Water side: Q4 return 45 → 49 °C, 984 kg/h. The bus return flow (237 kg/h rated) is too small on its own, so the HX-8 loop also takes the Q4 store bottom at 45 °C.
- Approach: 6 K at both ends, LMTD 6.0 K. The area is 0.51 m² at U = 1500 W/m²·K.

Edges: HL-HX8-Q3-A/B are replaced by HL-HX8-Q4-A/B (HX8 → Q4_A/Q4_B, thermal layer, IA). They are rated at 4.572 × 1.25 = 5.715 kW, because in single-ladder service one edge takes all of it. The line is DN25 at 0.62 m/s rated.

The heat lands in the Q4 batteries, not on Q4_BUS. Q4_BUS stays the Q4 water header fed only from Q4_A/Q4_B. IA-HX8 (EW_1 → HX8) moves to the thermal layer and carries 4.572 kW.

Sensitivity: 0.18 kW of HX-8 duty per kelvin of concentrate temperature.

### 13.2 Q3 process draws

| Exchanger | Sink | Basis | Duty kW |
|---|---|---|---:|
| HX-4 | OIL_DRYER | ELECTRICAL.md: 0.70–0.85 kWh/kg water; 150 kg/d × 5 % moisture = 7.5 kg/d × 0.775 kWh/kg (38.7 kWh/t, table 40) | 0.242 |
| HX-6 | GLASS_DIGEST | Derived, see below (GLASS_DIGEST study class 1.5 kW) | 1.663 |
| HX-5 | LEACH_CSTR_1 | Derived, see below (no duty in the repo) | 6.353 |
| Total | | | 8.258 |

HX-6, NaOH digest at 85 °C (mid of 80–90 °C):

- Caustic: 30 kg/d cullet, 72 % SiO₂ and 13 % Na₂O. Na₂SiO₃ needs 593 mol/d NaOH net (23.7 kg/d). At 2 M BMED caustic that is 297 L/d, heated 35 → 85 °C: 0.704 kW.
- Glass heat-up from 25 °C after the dry mill: 0.018 kW.
- Shell: 1.4 × 0.9 × 1.6 m with 50 mm mineral wool, 9.88 m²: 0.388 kW.
- Lid purge to HDR_CAUSTIC: 5 m³/h leaving saturated at 60 °C, 20.3 kg/d water: 0.554 kW.
- Dissolution heat is neglected (conservative).

HX-5, leach CSTR at 77.5 °C (mid of 70–85 °C):

| Term | Basis | kW |
|---|---|---:|
| REGEN LEACH return | 0.17 m³/h back from BMED at 35 °C (bipolar membranes held at or below 40 °C), reheated to 77.5 °C | +7.797 |
| Shell | 2.0 × 1.2 × 1.4 m, 13.76 m², 50 mm mineral wool, U = 0.65 | +0.473 |
| Shred heat-up | 150 kg/d, c_p 1.0, 25 → 77.5 °C | +0.091 |
| Lid purge (N3) | 5 m³/h leaving saturated at 60 °C, 20.3 kg/d water | +0.554 |
| Dissolution exotherm | Lowest credit: Fe, Zn and Al by H⁺ (−89.1, −153.9 and −531.0 kJ/mol), Cu by ClO₃⁻ (−242.1 kJ/mol); 85–90 % leach of the ELECTRICAL.md assay | −2.562 |
| HX-5 duty | | **6.353** |

The conservative basis is H⁺ as the oxidant for Fe, Zn and Al. Taking chlorate as the oxidant for all metals roughly doubles the exotherm.

Edges: HL-Q3-A/B-HX4, -HX5 and -HX6 (Q3_A/Q3_B → OIL_DRYER, LEACH_CSTR_1, GLASS_DIGEST). They are pumped, pressurized-water jacket loops:

| Edge set | Supply / return °C | Rated kW (duty × 1.25) | Line |
|---|---|---:|---|
| HL-Q3-*-HX4 | 95 / 85 | 0.302 | DN15 |
| HL-Q3-*-HX5 | 95 / 85 | 7.941 | DN20 |
| HL-Q3-*-HX6 | 95 / 90 | 2.079 | DN15 |

CONTINUOUS_RECYCLE stays off the ladder.

### 13.3 S18 and S67B

S18 (AFTERBURNER → CRYO_CO2) carried the same flue carbon as S67 → FLUE_KO → S67B.

The register describes S18 as "captured CO₂ / air feed". The air part is the cold-box air (AIR_INTAKE → MOL_SIEVE → HEPA_BANK), which does not come from the afterburner and is not this edge. On the graph S18 ends on CRYO_CO2, so the flue CO₂ is the only thing it carries.

S18 is not deleted, because `scale_down_map` (OIL), `pfd_bridge`, the C2 nozzle and the PFD labels name it.

The changes are:

- **S18**: rate 0.0 kg/d, claim retired, kept as the OIL → CRYO claim id.
- **S67**: carries the 15.0 kg/d CO₂ basis, with the flue at 241.7 kg/d (10.07 kg/h).
- **S67B**: 12.75 kg/d remains the only credit. The `same_carbon_as_S18` flag is dropped.
- **Scale-down map**: the OIL scale-down set now includes S67 and S67B.

CRYO_CO2 balance, kg/d:

| In | | Out | |
|---|---:|---|---:|
| S67B flue cut | 12.75 | S73 → MEOH_SYNTH | 6.90 |
| S82 MeOH FC return (S76 5.0 × 1.375) | 6.875 | S04 → GROW_BED (4.2 kg/d food × 0.08 DM / 0.5 HI × 0.45 C × 44/12) | 1.109 |
| | | S85 → HDR_CO2 (remainder) | 11.616 |
| Total | 19.625 | Total | 19.625 |

HDR_CO2 has no consumer edge, so 11.6 kg/d accumulates there. See §13.8. Rev C: closed by S89 HDR_CO2 → GROW_BED (AQS-DUTY-009, `CO2_HEADER_DUTY.md`).

### 13.4 Re-rated ladder balance (running: HX-8 on, Q3 draws on)

Q3 serves its draws in the order dryer, digest, leach. Whatever it cannot serve is electric trim at the process. HX-8 enters Q4.

Normal (both ladders, per ladder), kW:

| Tier | Source in | From above | Line loss | Store loss | Draws served | Down / to bus |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 0.553 | 0.000 | 0.000 | 0.200 | — | 0.353 |
| Q2 | 0.371 | 0.342 | 0.011 | 0.111 | — | 0.603 |
| Q3 | 0.000 | 0.585 | 0.018 | 0.174 | 0.411 (HX-4 0.121, HX-6 0.290) | 0.000 |
| Q4 | 2.286 (HX-8) | 0.000 | 0.000 | 0.164 | — | 2.122 |

Single ladder (B isolated), kW:

| Tier | Source in | From above | Line loss | Store loss | Draws served | Down / to bus |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 1.106 | 0.000 | 0.000 | 0.200 | — | 0.906 |
| Q2 | 0.742 | 0.879 | 0.027 | 0.111 | — | 1.510 |
| Q3 | 0.000 | 1.465 | 0.045 | 0.174 | 1.291 (HX-4 0.242, HX-6 1.049) | 0.000 |
| Q4 | 4.572 (HX-8) | 0.000 | 0.000 | 0.164 | — | 4.408 |

Closure (tolerance ±1 %):

| Case | Sources (Q1 + Q2 + HX-8) | Sinks (bus + store + line + draws served) | Residual |
|---|---:|---:|---:|
| Normal | 6.421 | 6.421 | 0.000 |
| Single | 6.421 | 6.421 | 0.000 |

Process balance: draws 8.258 kW = Q3 served + electric trim.

| Case | Q3 served | HX-4 trim | HX-6 trim | HX-5 trim | Total trim |
|---|---:|---:|---:|---:|---:|
| Normal (both ladders) | 0.822 | 0.000 | 1.084 | 6.353 | 7.437 |
| Single ladder | 1.291 | 0.000 | 0.614 | 6.353 | 6.967 |

Trim against issued ratings:

- GLASS_BURNOUT 1.0 kW is the only issued heater rating in the graph.
- The digest trim (≤ 1.084 kW) fits inside the GLASS_DIGEST 1.5 kW study class, but that class is not issued.
- No electric heater rating exists for OIL_DRYER or LEACH_CSTR_1. The 6.353 kW leach trim therefore has no issued rating. A leach heater rating must be issued, or the shortfall reduced (§13.7).

With the draws running, the Q4 bus receives 4.244 kW (normal) or 4.408 kW (single). This is above the 3.0 kW_th Q4 life priority by 1.24–1.41 kW. GEO_HP backfill drops to 0. GEO_ORC stays at 0 kW_e: its heat source on the graph is GEO_GHEX, and there is no Q4 → ORC edge. The ladder balance closes without it.

### 13.5 Re-rated edges

Ratings take the larger of the idle case (§6.2, draws and EW off) and the running case (§13.4), × 1.25.

| Edge | Rated kW | Normal kW | Governing case | Line |
|---|---:|---:|---|---|
| HL-Q3-A/B-DOWN | 1.614 (unchanged) | 0.000 running; 0.411 idle | idle | DN20 thermosyphon |
| HL-Q4-A/B-BUS | 5.510 (was 1.36) | 2.122 | running, single | DN15, 237 kg/h, 0.34 m/s |
| HL-HX8-Q4-A/B | 5.715 | 2.286 | running, single | DN25, 1231 kg/h, 0.62 m/s |
| HL-Q3-A/B-HX4 | 0.302 | 0.121 | duty | DN15 |
| HL-Q3-A/B-HX5 | 7.941 | 0.000 | duty | DN20, 679 kg/h |
| HL-Q3-A/B-HX6 | 2.079 | 0.290 | duty | DN15 |
| HL-Q4-X, -X-BA | 1.565 (unchanged) | 0 | idle | DN25 thermosyphon |

HX-8 has its own edge to each Q4 battery, so the Q4 cross-tie never carries HX-8 heat and keeps the ladder rating. Q1, Q2, Q3 cross-ties and all source and upper-step edges are unchanged.

Cross-tie coils (area = rated / (U × 5 K); U = 150 W/m²·K in oil, 400 W/m²·K in water). Each store holds two of them: the evaporator low and the condenser high. Each must fit in 0.45 of the inner height.

| Store | Rated kW | Area each, m² | Coil | Height each | Fits |
|---|---:|---:|---|---:|---|
| Q1 | 1.383 | 1.84 | DN25 bare, 17.4 m, 3 concentric rows (Ø0.47/0.33/0.20 m) | 0.38 m of 1.00 | yes |
| Q2 | 2.027 | 2.70 | DN25 integral low-fin (2.5 × area, η 0.9), 11.3 m, 2 rows | 0.31 m of 1.00 | yes |
| Q3 | 1.831 | 0.92 | DN25 bare, 8.6 m, 1 row | 0.35 m of 0.88 | yes |
| Q4 | 1.565 | 0.78 | DN25 bare, 7.4 m, 1 row | 0.27 m of 1.10 | yes |

Bare tube does not fit two 2.70 m² coils in the Q2 store, so Q2 uses low-fin tube.

### 13.6 Placement (AQS-PLACE-SEED-001 Rev G)

Rev F already had study rows for Q1_A..Q4_B (ladder A at x 6000, B at x 12000). Rev A §12 was wrong to say there were none. On the placed copy those origins collided with LEACH_CSTR_1, BMED_REGEN, SALT_FEED, HVAC_Q4 and the process core.

Rev G reissues all eight rows at the 800 × 800 × 1200 mm issued envelope, L-1, z −6000, 1500 mm pitch, plate-world (PROCESS_DX/DY not applied):

| Ladder | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| A, west of the core along the west wall | (1200, 9000) | (2700, 9000) | (4200, 9000) | (5700, 9000) |
| B, east of the core in the north-east bay | (15000, 15000) | (16500, 15000) | (18000, 15000) | (19500, 15000) |

Checks against every solid on the placed copy and every seed box:

- No intersections.
- At least 700 mm to equipment on the same level, and 1200 mm (A) or 2200 mm (B) to the envelope walls.
- At least 700 mm to corridors.
- CATCH_TANK on L-2 is 500 mm below ladder A, through the 300 mm L-1 slab. That is a cross-level vertical gap, not an access clearance.

The seed all-pairs check is 65 boxes, 2080 pairs, 0 intersections. The GEO_ORC pad is empty.

The copy `plant_placed_2026-10-07_revJ.FCStd` is built with `flow_to_cad.py --create-issued-only Q1_A,…,Q4_B`. The new option limits envelope creation to rows that have been reconciled. plant.FCStd is not opened or modified.

### 13.7 Lever (sensitivity, not adopted)

A liquor recuperator R-1 between the concentrate (77.5 °C, leach → EW-1) and the REGEN LEACH return (35 °C) would do the following, if sized so the EW cells are self-balanced:

- Duty 4.572 kW.
- EW feed at 52.6 °C.
- Return preheated to 59.9 °C, with a 17.6 K approach.
- HX-5 falls from 6.353 to 1.781 kW.
- HX-8 falls to 0, so Q4 would lose the 4.57 kW.

It is new equipment and needs a decision.

### 13.8 Decisions and open items

Decisions in Rev B:

- EW liquor at 55 °C, with 25 mm cell lagging and a ball blanket.
- Leach at 77.5 °C, with the REGEN return at 35 °C.
- Digest at 85 °C on 2 M caustic.
- 50 mm lagging on the CSTR and digest. This is outside the issued envelope, so the 600 mm clearance shrinks to 550 mm on those two vessels.
- Lid purge of 5 m³/h, saturated at 60 °C.
- Lowest exotherm credit.
- Q3 draw priority: dryer, digest, leach.
- HX-8 into Q4_A/Q4_B through its own loop.
- The Q4 cross-tie keeps the ladder rating.
- Low-fin tube for the Q2 coils.

Open items:

1. A leach heater rating (6.35 kW of trim) must be issued, or R-1 adopted.
2. The GLASS_DIGEST 1.5 kW class should be issued as the digest heater rating.
3. ~~HDR_CO2 needs a consumer or an export decision for 11.6 kg/d.~~ Closed in Rev C: S89 to GROW_BED, AQS-DUTY-009.
4. Q4 bus surplus over the life priority is 1.24 kW. Input it to ST-ORC-01; ORC stays at 0.
5. ~~The 0.8 m thermosyphon rise between stores on the same floor still needs stands or a level offset.~~ Closed in Rev C §14: stepped stores (gravity downhill steps), pumped cross-ties.

## 14. Rev C (graph Rev K): thermosyphon rise and cross-tie drive

Run: `python3 _hl_edges_study.py --rev-k --json out.json` (`main_k()`). Rev A/Rev B outputs are unchanged.

### 14.1 Check at the Rev G elevations

Both ladders were placed at z −6000 (one floor, all stores level). The store inner height and the coil heights fix where each coil can sit. Inner base above the store origin is (1.2 − h)/2; coils keep 0.06 m from the inner top and bottom.

| Step | Rev B layout (evaporator low, condenser high), rise at equal elevation | Required by Rev B | Stratification-correct layout at equal elevation |
|---|---:|---:|---:|
| Q1 → Q2 (HL-Q1-*-DOWN) | 0.542 m (4.8 kPa head) | 0.8 m | −0.542 m (no head) |
| Q2 → Q3 (HL-Q2-*-DOWN) | 0.597 m (5.5 kPa head) | 0.8 m | −0.597 m (no head) |
| Q3 → Q4 (HL-Q3-*-DOWN) | 0.575 m (5.5 kPa head) | 0.8 m | −0.575 m (no head) |

So the §8 requirement (0.8 m) is not met at the same elevation. Hydraulically the Rev B layout would still pass Δp < 0.5 × head at 0.54–0.60 m (4.8–5.5 kPa against at most 0.6 kPa with the check valve); it fails the 0.8 m rule as written and it fails thermally. The Rev B layout also has a thermal flaw: an evaporator at the bottom of the hotter store sits in the coldest layer of that store, and the fluid it cools stays at the bottom, so the step starves. A condenser at the top of the colder store heats only the top layer. A gravity loop between level stores cannot be both hydraulically and thermally right.

### 14.2 Decision for the downhill steps: gravity, on stepped stores

Each downhill step stays a gravity loop thermosyphon. The coils are stratification-correct: the evaporator sits high in the hotter store (it draws the hottest layer and the cooled fluid sinks away from it), and the condenser sits low in the colder store (it heats from the bottom and drives mixing). The colder store is raised so the condensate leg still falls to the evaporator:

\[ \Delta z_{store} = (z_{evap} - z_{cond}) + H_{req}, \qquad H_{req} = \max\left(\frac{2(\Delta p_v + \Delta p_l + \Delta p_{check})}{\rho_l g},\ 0.30\ \text{m}\right) \]

rounded up to 50 mm. Δp_check = 500 Pa (low-cracking swing check on the condensate return). The 0.30 m floor covers level swing in the condenser and drain-down of the return. Equivalent length: 6 m, or the routed length (in-store legs, level change, 1.5 m pitch, four long-radius elbows) if longer.

| Edge | Medium, line | Evaporator centre above source origin | Condenser centre above sink origin | Δp vapor + liquid + check, Pa | H_req | Store step | Actual rise | Head, Pa | Δp/head |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HL-Q1-A/B-DOWN | biphenyl/diphenyl-oxide eutectic, DN25 | 0.848 m | 0.306 m | 126.2 + 7.09 + 500 = 633 | 0.30 m | 0.85 m | 0.308 m | 2746 | 0.23 |
| HL-Q2-A/B-DOWN | water, DN15 | 0.898 m | 0.301 m | 107.7 + 0.79 + 500 = 608 | 0.30 m | 0.90 m | 0.303 m | 2787 | 0.22 |
| HL-Q3-A/B-DOWN | water, DN20 | 0.825 m | 0.249 m | 69.3 + 0.94 + 500 = 570 | 0.30 m | 0.90 m | 0.325 m | 3085 | 0.18 |

Every step passes Δp < 0.5 × head with margin (0.18–0.23). The check valve dominates the loss.

Store elevations (both ladders, plan positions unchanged):

| Store | Origin z, mm | Stand, mm |
|---|---:|---:|
| Q1_A, Q1_B | −6000 | 0 |
| Q2_A, Q2_B | −5150 | 850 |
| Q3_A, Q3_B | −4250 | 1750 |
| Q4_A, Q4_B | −3350 | 2650 |

Q4 top is at z −2150, 1850 mm below the L0 slab soffit (−300), so there is at least the 600 mm maintenance clearance overhead. The stand is a steel frame under the 800 × 800 store footprint; it does not widen the envelope. Store envelope, volumes and insulation are unchanged.

Coil packs (top to bottom; tallest bare coil switched to integral low-fin until the stack is ≤ 0.9 × inner height):

| Store | Coils | Stack / inner height |
|---|---|---:|
| Q1 | cross_tie (mid) 1.84 m² bare 3 row 0.376 m; down_evaporator (high) 1.51 m² bare 2 row 0.384 m | 0.760 / 1.00 m |
| Q2 | down_condenser (low) 1.51 m² integral low-fin 1 row 0.292 m; cross_tie (mid) 2.70 m² integral low-fin 2 row 0.305 m; down_evaporator (high) 2.52 m² integral low-fin 2 row 0.284 m | 0.881 / 1.00 m |
| Q3 | down_condenser (low) 0.94 m² integral low-fin 1 row 0.162 m; cross_tie (mid) 0.92 m² integral low-fin 1 row 0.157 m; down_evaporator (high) 0.81 m² bare 1 row 0.311 m | 0.630 / 0.88 m |
| Q4 | down_condenser (low) 0.81 m² bare 1 row 0.279 m; cross_tie (mid) 0.78 m² bare 1 row 0.270 m | 0.549 / 1.10 m |

### 14.3 Decision for the cross-ties: pumped single-phase loops

HL-Q*-X and HL-Q*-X-BA connect same-tier stores on the two ladders. Those stores are at the same elevation, the tie must carry heat in either direction, and the run is 25 m each way across the core. A gravity loop has a fixed hot end and would need ladder B a full step above ladder A for one direction only. Each tier therefore gets one pumped single-phase loop (XL-Q1..XL-Q4) through one coil in each store. The X and X-BA edges share it. The pump runs only when |T_A − T_B| > 5 K; heat then flows hotter to colder whatever the flow direction. Normal duty is 0, so the pumps are normally off.

Loop pressure drop is Darcy over 50 m (supply and return), two coils (× 1.3 for the helix) and ΣK = 12 of fittings. Pump electric power at 15 % wire-to-water.

| Loop | Medium | Supply/return °C | Flow, L/min | Line | Velocity, m/s | Loop Δp, kPa | Pump head, m | Hydraulic, W | Electric, W | Loop pressure |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---|
| XL-Q1 | synthetic thermal oil, hydrogenated terphenyl class | 245/240 | 7.78 | DN15 | 0.66 | 20.55 | 2.44 | 2.66 | 17.8 | 1.0 bar a, T_max 275 °C |
| XL-Q2 | synthetic thermal oil, hydrogenated terphenyl class | 145/140 | 13.08 | DN20 | 0.63 | 19.80 | 2.17 | 4.32 | 28.8 | 1.0 bar a, T_max 165 °C |
| XL-Q3 | treated water | 95/90 | 5.43 | DN15 | 0.46 | 9.64 | 1.02 | 0.87 | 5.8 | 2.5 bar a, T_max 110 °C |
| XL-Q4 | treated water | 65/60 | 4.58 | DN15 | 0.39 | 7.95 | 0.83 | 0.61 | 4.0 | 1.0 bar a, T_max 77 °C |

At the rated duty the store-to-store difference is 15 K (5 K loop ΔT plus two 5 K coil approaches). XL-Q1 and XL-Q2 use synthetic hydrogenated-terphenyl oil (no pressurisation at 275/165 °C). XL-Q3 water is held at 2.5 bar a (above 1.43 bar a saturation at 110 °C). The pumps are canned or magnetic-drive circulators; the computed electric power is below the smallest motor class, so the real draw is set by the motor (tens of watts), and only while a tie runs.

### 14.4 What changed in the graph and the seed

- HL-Q1/Q2/Q3-A/B-DOWN `params`: layout, rise, store step, Δp terms, head, Δp/head, same-elevation check.
- HL-Q*-X and -X-BA `params`: `kind` pumped single-phase loop, loop id, medium, flow, DN, Δp, pump head and power, control rule. The two-phase keys are removed.
- Q*_A/B node `params`: origin z, stand height, coil pack.
- AQS-PLACE-SEED-001 Rev H: Q2 −5150, Q3 −4250, Q4 −3350 on both ladders. All-pairs 0 intersections; ≥ 600 mm within a level.

§3 (H = 0.8 m), §8 (0.8 m rule, evaporator low and condenser high) and §11 item 2 (cross-ties as thermosyphons) are superseded by this section.

### 14.5 Items closed and open

Closed: §13.8 item 3 (HDR_CO2 consumer: S89 to GROW_BED, AQS-DUTY-009) and item 5 (rise: stepped stores).

Open:

1. Stand and access-platform design for Q2–Q4 (up to 2.65 m), and the Q4 coil and relief access from a platform.
2. Pump selection for XL-Q1..Q4 (high-temperature magnetic drive for the oil loops).
3. §13.8 items 1, 2 and 4 are unchanged.
