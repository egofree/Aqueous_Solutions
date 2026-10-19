# Unit-task evidence audit (T01/T04/T05/T08/T10), 2026-10-20

Document number: AQS-PLAN-007 note (no new AQS number; this is a working record).
Authority: AQS-PLAN-007 section 1 rule — "A task is checked only where a file in the repo proves it; the file
is cited. … Partial evidence is written as a status note and the box stays open."
Scope: the five unit tasks whose evidence detection read a graph-side stand-in or a mere file-existence
test while the real plant-wide artifacts sat unread: 01 (closure duty §1), 04 (nozzle csv), 05 (line list
bores), 08 (instrument loop membership), 10 (mfg model). Detection now lives in
`docs-authority/_task_plan_gen.py` and reads the per-unit artifact itself on every regeneration.
Graph state: Rev AC (`flow_graph/plant_flow_graph.json`), HEAD 23d849f, suite 43/43 before and after.

## Method

For each task: the Done-when was read from the generator's task table, and the per-unit artifact was read
for all 175 present units (173 full-task units + 2 boundary units that carry task 01 only):
`duties/<UNIT>.md` §1, `nozzles/<UNIT>.csv`, the `LINE_LIST.md` row set (AQS-PIP-004), the
`inventory/INSTRUMENT_INDEX.csv` unit column (AQS-CTL-001), and `models/mfg/<UNIT>/bom.csv`. A unit ticks
only where the artifact content satisfies the Done-when; existing-but-short artifacts render as an open
box with a `Status:` note naming the gap. Nothing was ticked that was not read.

## Before / after (unit tasks, non-boundary unless noted)

| Task | Before | After | Change |
| --- | --- | --- | --- |
| 01 closure duty §1 (175 rows incl. boundary) | 4/175 | 124/175 | +120 |
| 04 nozzle schedule | 118/173 | 28/173 | −90 |
| 05 line list and bores | 0/173 | 173/173 | +173 |
| 08 instruments and control | 2/173 | 112/173 | +110 |
| 10 CAD model accepted (M3) | 0/173 | 0/173 | 0 (notes made truthful) |

Plan total 776/2887 → 1089/2887 done (+313 = +120 −90 +173 +110). Tasks 02/03/06/07/09/11/12/13/14/15
detection untouched (33/173/1/122/0/0/45/121/0/0 unchanged).

## T01 — duty sheet section 1 closure

Old check: the node's `params.duty` string matched `In X kg/d, out Y kg/d` with X = Y. That string is a
legacy graph param refreshed in memory only since the R11 Rev AC regen (`_duty_basis.py` line 19), so it
is stale for almost every unit — 4 ticks (CRYO_ASU, EVAP_ACID, EVAP_BASE, EXT_HALL).
New check: the section 1 line `_duty_basis.py` actually writes when it regenerates a sheet —
`1. Basis. Mass in X kg/d. Mass out Y kg/d. Electrical duty Z kW.` — read from `duties/<UNIT>.md`,
ticked when present with X = Y (within the 4-significant-figure rounding of the sheet text, 0.1 %).
Result: 124 ticked (96 with flow, 28 zero-flow), 51 open.

Honest residual:

- 51 units have no duty sheet at all (authoring work, task 01 → 02 chain): FOUNDRY 27 (AL_POT,
  CAST_LINE, CA_POT, COMB_HEAT, CONT_CAST, CR_CELL, DRAW, EXTRUDE, FLUX_PREP, FORGE, IND_MELT, INV_CAST,
  METAL_STORE, MG_POT, MO_CELL, RES_HEAT, RF_HEAT, ROLL, SHELL_BREAK, SHELL_BUILD, SHELL_BURNOUT,
  SINTER, STOCK_OUT, TI_CELL, VAC_CAST, VAC_IND, WAX_PATTERN), POLYMERS 10 (FILM_CAST, HF_GEN, PELLET,
  POLY_COND, POLY_F, POLY_OLEFIN, POLY_STOCK, POWDER_RESIN, TFE_SYN, VDF_SYN), CRYO 4 (AIR_RECEIVER,
  H2O_ELYZ, PROD_MEOH, PROD_O2), DIGESTER 3 (F_RECOVER, LI_RECOVER, P_CA), HEAT 3 (ADS_CHILL,
  DRY_COOLER, MAU_HX), OIL 2 (GREASE_CA, GREASE_LI), GLASS 1 (SI_REDUCE), FARM 1 (FOOD_STORE).
- 28 of the 124 ticks are zero-flow closures (no kg/d edges by design): BOUNDARY_EXPORT, CATCH_TANK,
  CRYO_DED_COOL, CRYO_HX_Q4, EXT_HALL, GEO_GHEX, GEO_HP, GEO_HP_CLOSED_LOOP, HX8, HYDRO_SET,
  LITHO_ALIGN, LOAD_AGG, MET_HX_Q4, PV_ARRAY, Q1_A..Q4_B, Q4_BUS, RECTIFIER, RELIEF_CRYO, RELIEF_H2,
  SALT_FEED, SOL_ARK_60K. §1 reads "Mass in 0 kg/d. Mass out 0 kg/d." — the literal Done-when
  (in = out, kW from the graph) is met and the zeros are visible in the evidence line, but these carry
  no process-basis content; their substance lands with task 02.

## T04 — nozzle schedule

Old check: `nozzles/<UNIT>.csv` exists → tick "(bores not calculated)". Existence said nothing about
coverage: the csvs are hand-issued static artifacts (commit fc93bc9, 2026-10-10; no generator in the
tree) and most list a subset of the unit's connections plus drain/vent utilities.
New check: every process connection of the unit — present kg/d mass edges plus HL-/thermal kW edges
(cables are not nozzles) — must have a row, counting a row for an edge where its service text equals
the edge `carries` (the same match rule `_pid_sheets.py` uses). Utility rows (drain, vent) match no
edge and are allowed extras. Bore recalculation is not claimed anywhere.
Result: 28 ticked — AFTERBURNER_FLUE, BMED_UPW_POLISH, C29_RECYCLE, CATCH_TANK, COLD_MILL,
CRYO_AHU_COND_CONDENSABLE, CRYO_DED_COOL, FAB_UPW_TANK, FLUE_KO, HDR_UPW, NCG_HEADER, OIL_DRYER,
OIL_PYRO, PROD_C29, WS_AMMONIA, WS_KOH, WS_SLURRY, WS_PHOS, ZNBR2, ZNBR2_BR2_REGEN, GLASS_RINSE,
GLASS_BURNOUT, Q1_A, Q2_A, Q3_A, Q1_B, Q2_B, Q3_B.

Honest residual:

- 81 csvs exist but do not cover their unit: 286 edge rows missing in total (e.g. LEACH_CSTR_1
  50 of 58 connections without a row). Rendered as `Status: partial: N of M process connections
  without a row`.
- 55 units have no csv (FOUNDRY 27, POLYMERS 10, CRYO 4, DIGESTER 6, HEAT 3, OIL 2, GLASS 1, ELEC 1,
  FARM 1).
- 9 csvs belong to units with no piped process connections at all (CRYO_HX_Q4, GEO_HP, HYDRO_SET,
  LOAD_AGG, MET_HX_Q4, PV_ARRAY, RECTIFIER, SOL_ARK_60K, LITHO_ALIGN — electrical/thermal-bus only):
  the Done-when is vacuous there, so the box stays open with `Status: no piped process connections;
  nozzle schedule n/a` rather than ticking an empty condition.

## T05 — line list and bores

Old check: none (0/173 while the plant line list has existed since AQS-PIP-004).
New check: every present edge of the unit has a row in `docs-authority/LINE_LIST.md`, and every piped
row carries DN + class; solids and cable rows are the line list's own "not piped" classification.
Schedule, rating and material resolve per class in AQS-PIP-003 (`PIPING_CLASSES.md`: e.g. P1 PVC-U
Sch 80 ASTM D1785, rating per D1785 × temperature factor), which is how the Done-when's four properties
are carried; the DN basis (velocity sizing vs `edge line_DN`) stays stated per row in the line list.
Result: 173/173 ticked — every present unit's every present edge is in the line list with DN + class.
Residual: none at unit level. Plant-level caveats remain as already recorded in the line list header
(rows without a length where a unit position is missing) and in X-MAT-20 for condensate classing.

## T08 — instruments and control

Old check: the unit's name appears anywhere in `INSTRUMENT_LOOPS.md` (AQS-INST-001 Rev B — the partial
assay/digester/farm study-loop page; 2 ticks: FLOAT_SINK, OIL_DRYER).
New check: the unit owns ≥ 1 instrument loop in the plant-wide index — `inventory/INSTRUMENT_INDEX.csv`
via `INSTRUMENT_INDEX.md` (AQS-CTL-001, 599 tags, every row carries tag/range/signal/loop/PLC).
Result: 112/173 ticked, each citing its loop count.
Naming note, recorded here because the Done-when text predates the index: the Done-when says "loop
listed in AQS-INST-001", which today holds only the three study loops (X-CTL-05 partial). Loop
membership plant-wide is proven by AQS-CTL-001; SIF trips and setpoints are carried in AQS-CTL-003
(CAUSE_EFFECT). Per-unit setpoint lists remain open with X-CTL-05.

Honest residual: 62 units own no instrument loop yet (61 non-boundary + BOUNDARY_EXPORT) — FOUNDRY 27,
POLYMERS 10, CRYO 4, HEAT 4, DIGESTER 4, GAS 3, OIL 3, HAB 2, one each in DOCK, WTR, GLASS, ELEC, FARM:
ADS_CHILL, AIR_RECEIVER, AL_POT, BOUNDARY_EXPORT, CAST_LINE, CA_POT, COMB_HEAT, CONT_CAST, CR_CELL,
DRAW, DRY_COOLER, EVAP_ACID_VS, EXTRUDE, EXT_HALL, FILM_CAST, FLUX_PREP, FOOD_STORE, FORGE, F_RECOVER,
GREASE_CA, GREASE_LI, HDR_CO2, HDR_H2, HDR_N2, HDR_O2, HDR_UPW, HF_GEN, IND_MELT, INV_CAST, LI_RECOVER,
MAU_HX, METAL_STORE, MG_POT, MO_CELL, NCG_HEADER, PELLET, POLY_COND, POLY_F, POLY_OLEFIN, POLY_STOCK,
POWDER_RESIN, PROD_MEOH, PROD_O2, P_CA, Q4_BUS, RELIEF_CRYO, RELIEF_H2, RES_HEAT, RF_HEAT, ROLL,
SHELL_BREAK, SHELL_BUILD, SHELL_BURNOUT, SINTER, SI_REDUCE, STOCK_OUT, TFE_SYN, TI_CELL, VAC_CAST,
VAC_IND, VDF_SYN, WAX_PATTERN. In short: no instrument loops exist for the FOUNDRY and POLYMERS trains
yet, nor for the gas headers, EVAP_ACID_VS, EXT_HALL, the relief nodes, the product/stores groups and
the standalone heat machines. This is authoring work in X-CTL-01's per-unit extension, not a detection
gap.

## T10 — CAD model accepted (AQS-PLAN-006 M3)

Old check: none for the box; the note claimed "partial: M2 at `models/mfg/<UNIT>/`" for any unit with a
directory — overstating units that hold only an envelope + PLACEHOLDER BOM.
New check (detection): `models/mfg/<UNIT>/bom.csv` is read and classified — a real BOM (any
non-placeholder row; "placeholder bore not calculated" notes inside a real BOM do not count) vs a
standby envelope stub (every row `PLACEHOLDER (standby, envelope-only)`).
The box stays open for every unit: the Done-when is acceptance M3 per AQS-PLAN-006 section 5, and no
unit passes section 5 (criterion 8 requires the drawing set; the MFG_MODEL_PLAN tracker records none at
M3 — every entry says "No drawings"). Ticking on a BOM file would claim acceptance that does not exist.

Honest residual at the final regeneration of this pass (the working tree, mid-CAD-lane — see the
concurrency flag below): 35 units carry a real M2 mfg BOM (BLACK_DIGEST, GLASS_DIGEST, LEACH_CSTR_1,
MEOH_FERM, MEOH_SYNTH, OIL_PYRO, EVAP_ACID, EVAP_BASE, EVAP_ACID_VS, HF_GEN, VDF_SYN, TFE_SYN, POLY_F,
CR_CELL, TI_CELL, MO_CELL, IND_MELT, CAST_LINE, ROLL, FLUX_PREP, STOCK_OUT, CONT_CAST, AL_POT, MG_POT,
CA_POT, WAX_PATTERN, SHELL_BUILD, SHELL_BURNOUT, INV_CAST, SHELL_BREAK, POLY_OLEFIN, PELLET,
POWDER_RESIN, FILM_CAST, POLY_STOCK) — note `Status: partial: M2 … (real BOM), not accepted per
AQS-PLAN-006 section 5 (no drawings)`; 10 units are standby envelope stubs (RF_HEAT, RES_HEAT,
COMB_HEAT, VAC_IND, VAC_CAST, EXTRUDE, DRAW, FORGE, SINTER, POLY_COND) — `envelope + PLACEHOLDER BOM
(standby style, machine design not started)`; the remaining ~130 units have no mfg model at all
(envelope `cad/stl/<UNIT>.stl` where it exists).

- Authoring work to first ticks: for each modelled unit, the section 5 set — drawings (X-DWG), fastener
  rows, duty §7 pointer, manifold STL replacing `cad/stl` — then acceptance per AQS-PLAN-006.
- Concurrency flag: the CAD lane was actively converting standby PLACEHOLDER BOMs to real machine BOMs
  in `models/mfg/**` during this audit (uncommitted working-tree edits; the real-BOM count moved
  17 → 35 between the first audit read and the final regeneration, and may move again). The T10 status
  notes in TASK_PLAN reflect the tree at the final regeneration of this pass; rerun
  `python3 docs-authority/_task_plan_gen.py` after the CAD lane lands to refresh the wording. Tick
  counts are unaffected (T10 stays 0 — acceptance content still does not exist; T12 counts bom.csv
  presence and stayed 45/173).

## Verification

- `python3 -m pytest -q`: 43 passed (before the change and after the final regeneration).
- TASK_PLAN totals self-consistent: 2887 tasks / 1089 done; counts table sums per task.
- Write set of this lane: `docs-authority/_task_plan_gen.py` (evidence detection only — no task
  definition, triage, or prose changed), `docs-authority/TASK_PLAN.md` (regenerated),
  `docs-authority/notes/2026-10-20-evidence-audit.md` (this record). No other docs were edited by this
  pass; duty sheets, LINE_LIST, INSTRUMENT_INDEX and mfg exports were read, not written. No commits.
