# Pitch pass: yard through water stubs

Document number: AQS-PLACE-SEED-001  
Revision: B  
Date: 2026-10-29  
Authority: placement seed revision F of 2026-10-07. Superseded for placement by `flow_graph/placement_seed.json` and the site unit placements AQS-SITE-013. This is a record, not a stamped design.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: placement of the yard, fab wet rooms, methanol train and water stubs, with origins at placement seed revision B. | 2026-10-02 |
| — | Origins updated to placement seed revision F; no revision letter was given. | 2026-10-07 |
| B | Identity lines, record of revisions and purpose added to the documentation style guide (AQS-DOC-002); arrows written as sentences. The record is otherwise unchanged. | 2026-10-29 |

## Purpose and scope

This page records the placement pass of early October 2026: where the yard units, the fab wet rooms, the methanol train and the water stubs were put, and the clearance rule behind each. It is kept as the record of those rules. The coordinates below are those of placement seed revision F and are no longer current; the current origins are in `flow_graph/placement_seed.json`, and the site placements in AQS-SITE-013. Some units named here (for example the phosphate fork, which was not then on the graph) have changed since.

## 1. Yard (west of X=0, Y aligned to dock at 10000)

| Unit | SW corner (mm) | Rule |
|---|---|---|
| ZNBR2 | −4848, 10000 | 10 ft from openings. Own Br2 tower. Not CRU. |
| SOL_ARK_60K | −1500, 14800 | NEC 110.26, 1100 mm. Outside ESS Class I. |
| RECTIFIER | −1900, 12800 | Same ordinary row. |
| BACKUP_GEN | −3500, 7700 | Outdoor H2. Issued 2000×1000×1600. 1100 mm all faces. Rev F. |
| FUEL_CELL | −4800, 16400 | H2 anode. O2 face south, 7700 mm from GEN (rule 7620 mm or 1 h wall). 1100 mm all faces. Rev F. |
| PV_ARRAY | −11000, 10000 | One module. Tilt +33° about +X. Not on the tank. 600 mm to ZNBR2_BR2_REGEN. Rev F. |
| GEO_HP / GHEX / loop | −7000 / −8600, 5200; loop −8600, 4000 | West of the MeOH train. |
| NOX_SCRUB | −3500, 5800 | Gen exhaust. Rev F, 1500 mm south of GEN. |

M1 counts from params.py are 1 / 1 / 1 for PV, ZnBr2, rectifier.

## 2. Fab wet (inside 12000, 8000)

1 h partition at X=15000. 25 ft does not fit in the bay.

| Room | Units |
|---|---|
| Acid, west | WS_HF_ED, WS_NITRIC. Separate bunds. |
| Oxidizer, east of partition | WS_PEROX |
| Alkaline | WS_AMMONIA, WS_KOH |
| CMP | WS_SLURRY |
| Flammable, north wall | WS_SOLV |
| Tool east wall | WS_DOPE cabinets |
| East of benches | FAB_UPW_TANK (roof water, not Salria) |

WS_PHOS is in the reagent note and not a graph node. No solid this pass.

## 3. MeOH (deferred chemistry, fixed order)

Outdoor west yard, south of geothermal: MEOH_FERM, then MEOH_SYNTH, MEOH_TANK and MEOH_FC.
Not the PEM fuel cell. Not under L1. Tank is NFPA 30 diked.

Rev F origins (SW corner, mm): MEOH_FERM −4700, 3100; MEOH_SYNTH −4848, 1600; MEOH_TANK −2048, 1600; MEOH_FC −4848, 200; MEOH_COND −2448, 200. 600 mm between every pair; FERM 700 mm from the ORC pad.

## 4. Nozzle order

Metal: MET_AHU feeds MET_SCRUB, which returns on S71 and S72. MET_HX_Q4 is water after scrub, <80 °C.
Cryo: CRYO_AHU feeds CRYO_AHU_COND, which returns on S70 to the cold box. CRYO_HX_Q4 is warm residual water (S54), not CRYO_DED_COOL.

## 5. Water stubs

BLACK_DIGEST then GREY_TREAT at hab SW. S13_CLASS_TREAT on L-1, not life. BMED_UPW_POLISH beside BMED, upstream of FAB_UPW_TANK.

Do not apply apply_placement.py to plant.FCStd until the wet cassette nudge is reconciled. These origins are plate-world, not L-1-local.
