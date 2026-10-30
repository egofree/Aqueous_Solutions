Graph Rev AC. Closure is the cut around each Tarjan component.
A component passes when every unit balances and the cut balances, per rate unit, within 1%.
Pass is on the present edges in this file. It is not on-site evidence.
This result is not the MVS flag. mvs.mvs_criteria.loops_closed is not set here.

## mass: 439 edges, 1 loops
- 143 units. Circuits listed: 20 (cap 20).
  ACID_PLANT, ACID_POLISH_SCRUB, AFTERBURNER, AFTERBURNER_FLUE, AIR_RECEIVER, ALK_SCRUBBER, AL_POT, ATMOS, BACKUP_GEN, BAGHOUSE, BLACK_DIGEST, BLOW_MOLD, BMED_ACID, BMED_BASE ...
  one circuit: IA-ACID-CO2 -> IA-SI-HOOD-O2 -> IA-SI-FUME -> IA-BMED-03 -> IA-BMED-01 -> S34 -> S38 -> CUT-1
  kg/d: nodes off 2, cut in 11.40 out 0.00 fail

## thermal: 40 edges, 0 loops

## elec: 92 edges, 1 loops
- 2 units. Circuits listed: 1 (cap 20).
  SOL_ARK_60K, ZNBR2
  one circuit: IA-ESS-ZNBR2-CHG -> IA-ESS-ZNBR2-DIS
  kW: nodes off 1, cut in 356.86 out 160.86 fail

## ess: 10 edges, 2 loops
- 2 units. Circuits listed: 4 (cap 20).
  CATCH_TANK, ROOF_TANK
  one circuit: IA-ESS-HYDRO-CHG -> IA-ESS-HYDRO-DIS
  kg/d: nodes off 0, cut in 0.00 out 0.00 pass
- 2 units. Circuits listed: 1 (cap 20).
  SOL_ARK_60K, ZNBR2
  one circuit: IA-ESS-ZNBR2-CHG -> IA-ESS-ZNBR2-DIS
  kW: nodes off 1, cut in 2.67 out 1.67 fail

loops_closed: false
This result is the cut test. It is not the MVS flag.
