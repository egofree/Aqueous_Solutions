Graph Rev AC. Closure is the cut around each Tarjan component.
A component passes when every unit balances and the cut balances, per rate unit, within 1%.
Pass is on the present edges in this file. It is not on-site evidence.
This result is not the MVS flag. mvs.mvs_criteria.loops_closed is not set here.

## mass: 368 edges, 2 loops
- 123 units. Circuits listed: 20 (cap 20).
  ACID_POLISH_SCRUB, AFTERBURNER, AFTERBURNER_FLUE, AIR_RECEIVER, ALK_SCRUBBER, BACKUP_GEN, BAGHOUSE, BLACK_DIGEST, BLOW_MOLD, BMED_ACID, BMED_BASE, BMED_UPW_POLISH, C29_RECYCLE, CAST_LINE ...
  one circuit: S66 -> CRU_TO_VDF -> VDF_TO_POLY_F -> POLYF_TO_PELLET -> PELLET_TO_STOCK -> POLY_TO_MFG -> S16 -> IA-BMED-03
  kg/d: nodes off 0, cut in 0.00 out 0.00 pass
- 3 units. Circuits listed: 1 (cap 20).
  SHELL_BUILD, SHELL_BURNOUT, WAX_PATTERN
  one circuit: SHELL_TO_BURNOUT -> WAX_RECLAIM_TO_PATTERN -> WAX_TO_SHELL
  kg/d: nodes off 0, cut in 0.00 out 0.00 pass

## thermal: 40 edges, 0 loops

## elec: 55 edges, 1 loops
- 2 units. Circuits listed: 1 (cap 20).
  SOL_ARK_60K, ZNBR2
  one circuit: IA-ESS-ZNBR2-CHG -> IA-ESS-ZNBR2-DIS
  kW: nodes off 1, cut in 410.50 out 214.36 fail

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
