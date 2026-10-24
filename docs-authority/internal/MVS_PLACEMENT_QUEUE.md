# MVS placement queue

Date: 2026-10-02
Source: placement_report.json after datum lock from models/freecad/params.py SCALE_M=1.0
Do not run apply_placement.py on plant.FCStd. Block origins are not machine pitches.

## Closed this pass

Datums (mm FFL, slab not added): L0=0, L-1=-6000, L-2=-10500, L1=6000, L2=10800.
Moves 31 → 44. Datum gaps 7 → 0. Scrubber block and life-header spine added as block origins only.

## Still open — no machine pitch (32)

| Group | Units | What is locked | What is not |
|---|---|---|---|
| Yard power | ZNBR2, BACKUP_GEN, FUEL_CELL, RECTIFIER, SOL_ARK_60K, PV_ARRAY | Outdoor, west of north dock, YARD_WALL_CLEAR=500 mm. Counts from params. | X/Y pitch of each skid |
| Geothermal | GEO_HP, GEO_GHEX, GEO_HP_CLOSED_LOOP | Grade / yard family | Bore field and skid origin |
| MeOH | MEOH_FC, MEOH_FERM, MEOH_SYNTH, MEOH_TANK | Massing boxes exist. DMFC deferred. | Train order and bay |
| Metal shop internals | MET_AHU, MET_HX_Q4, MET_SCRUB | Inside MFG envelope 12000,0 L0 | Intra-shop pitch |
| Fab wet | WS_AMMONIA, WS_DOPE, WS_HF_ED, WS_KOH, WS_NITRIC, WS_PEROX, WS_SLURRY, WS_SOLV, FAB_UPW_TANK | Inside FAB envelope 12000,8000 L0. Tote class = P_TANK / TOTE. | Bench order. HF/perox separation not drawn |
| Water life | BLACK_DIGEST, GREY_TREAT, S13_CLASS_TREAT, BMED_UPW_POLISH | TBD massing, not nameplates | Which floor, which wall |
| Cryo internals | CRYO_AHU_COND_CONDENSABLE, CRYO_HX_Q4 | Inside CRYO 15000,6000 L-1 | Cold-box nozzle order |
| Terrace | TERRACE_IRRIG | South header exists | Not a machine |

## Skipped — study machines, not layout bugs (15)

Placeholders, no solid until the machine exists: BLOW_MOLD, ELECTRODE_COAT, LITHO_STUB, SOLAR_PV_CELL, VCD_TRAIN, REMIN, CONTINUOUS_RECYCLE.
Massing opted in but graph still placeholder: C29_RECYCLE, GEO_ORC, GLASS_BURNOUT, GLASS_MILL, GLASS_RINSE.
Logical, no solid: BOUNDARY_EXPORT, LOAD_AGG, Q4_BUS.

## Order

1. Yard pitch (power + PV + ZnBr2) — outdoor, no process header.
2. Fab wet bench order — hazard separation before coordinates.
3. MeOH train — still deferred; do not invent a bay.
4. Study machines — litho, electrode, blow mold, VCD, solar cell, remineralizer. Those are the MVS holes.
