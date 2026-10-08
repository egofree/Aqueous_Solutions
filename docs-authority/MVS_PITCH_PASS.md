# Pitch pass — yard through water stubs

Document: AQS-PLACE-SEED-001 Rev B; origins updated to seed Rev F
Date: 2026-10-02; updated 2026-10-07
Not a PE stamp. Study envelopes where params.py has no article size.

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

Outdoor west yard, south of geothermal: FERM → SYNTH → TANK → FC.
Not the PEM fuel cell. Not under L1. Tank is NFPA 30 diked.

Rev F origins (SW corner, mm): MEOH_FERM −4700, 3100; MEOH_SYNTH −4848, 1600; MEOH_TANK −2048, 1600; MEOH_FC −4848, 200; MEOH_COND −2448, 200. 600 mm between every pair; FERM 700 mm from the ORC pad.

## 4. Nozzle order

Metal: MET_AHU → MET_SCRUB → returns S71–S72. MET_HX_Q4 is water after scrub, <80 °C.
Cryo: CRYO_AHU → CRYO_AHU_COND (S70) → cold box. CRYO_HX_Q4 is warm residual water (S54), not CRYO_DED_COOL.

## 5. Water stubs

BLACK_DIGEST then GREY_TREAT at hab SW. S13_CLASS_TREAT on L-1, not life. BMED_UPW_POLISH beside BMED, upstream of FAB_UPW_TANK.

Do not apply apply_placement.py to plant.FCStd until the wet cassette nudge is reconciled. These origins are plate-world, not L-1-local.
