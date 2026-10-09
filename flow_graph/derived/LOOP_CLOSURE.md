Graph Q. Closure is the cut around each Tarjan component.
A component passes when every unit balances and the cut balances, per rate unit.

## mass: 174 edges, 1 loops
- 54 units. Circuits listed: 20 (cap 20).
  AFTERBURNER, AFTERBURNER_FLUE, ANIMAL_PEN, BMED_ACID, BMED_BASE, BMED_UPW_POLISH, BOARD_MILL, C29_RECYCLE, CATCH_TANK, COMPOST, CONTINUOUS_RECYCLE, CRYO_AHU, CRYO_CO2, CRYO_H2 ...
  one circuit: S18 -> S04 -> S11
  kg/d: nodes off 0, cut in 1037.55 out 1037.55 pass

## thermal: 48 edges, 4 loops
- 2 units. Circuits listed: 1 (cap 20).
  Q4_A, Q4_B
  one circuit: HL-Q4-X -> HL-Q4-X-BA
  kW: nodes off 0, cut in 11.02 out 11.02 pass
- 2 units. Circuits listed: 1 (cap 20).
  Q3_A, Q3_B
  one circuit: HL-Q3-X -> HL-Q3-X-BA
  kW: nodes off 0, cut in 23.87 out 23.87 pass
- 2 units. Circuits listed: 1 (cap 20).
  Q2_A, Q2_B
  one circuit: HL-Q2-X -> HL-Q2-X-BA
  kW: nodes off 0, cut in 4.12 out 4.12 pass
- 2 units. Circuits listed: 1 (cap 20).
  Q1_A, Q1_B
  one circuit: HL-Q1-X -> HL-Q1-X-BA
  kW: nodes off 0, cut in 2.77 out 2.77 pass

## elec: 11 edges, 1 loops
- 2 units. Circuits listed: 1 (cap 20).
  SOL_ARK_60K, ZNBR2
  one circuit: IA-ESS-ZNBR2-CHG -> IA-ESS-ZNBR2-DIS
  kW: nodes off 0, cut in 34.63 out 34.64 pass

## ess: 10 edges, 2 loops
- 2 units. Circuits listed: 4 (cap 20).
  CATCH_TANK, ROOF_TANK
  one circuit: IA-ESS-HYDRO-CHG -> IA-ESS-HYDRO-DIS
  kW: nodes off 0, cut in 0.00 out 0.00 pass
  kg/d: nodes off 0, cut in 0.00 out 0.00 pass
- 2 units. Circuits listed: 1 (cap 20).
  SOL_ARK_60K, ZNBR2
  one circuit: IA-ESS-ZNBR2-CHG -> IA-ESS-ZNBR2-DIS
  kW: nodes off 1, cut in 0.79 out 1.67 fail

loops_closed: false
