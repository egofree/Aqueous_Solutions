# Closure lane record, 2026-10-19

Document number: AQS-PLAN-007 note (no new AQS number; working record). Companion to `notes/2026-10-19-evidence-pass.md`.
Scope: the reopened honesty tasks that are evidence/docs work (X-SAF-01 actions, X-MFG-34/36 bench procedures,
X-END-02 BOM classing). No graph, drivers.json or models writes; no commits.

## Finding first: the committed HAZOP CSV was stale

The committed `hazop_actions.csv` (147 actions, 99 open) predates the Rev AC graph. Regenerated at the committed
graph (rev AC, 178 nodes), the study has 190 actions. The "5 temp-indication actions with no closure path" of the
stale CSV were 14 temperature + 4 level indication actions in reality, plus 16 relief actions on units without duty
sheets. Everything below works from the regenerated state.

## X-SAF-01 - HAZOP action disposition

`_hazop.py` now gives every action a disposition at generation time; `_sif.py` then closes the trip actions as
before. Result (hazop_actions.csv, 190 actions):

- 89 closed at issue: relief-case actions on units whose duty sheet section 6 names the case or atmospheric
  statement (the same artifact the unit task 07 check reads; X-SAF-03 C7).
- 67 closed by the SIF pass: `closed by SIF-nnn (AQS-CTL-003)` (AQS-CTL-003 regenerated, 135 SIFs).
- 34 `open - tracked HA-nn (AQS-SAF-008)`: new register `HAZOP_ACTION_REGISTER.md` (AQS-SAF-008) with the owner
  task in AQS-PLAN-007 terms (unit task 07 for relief, 08 for indication) on 17 units: ADS_CHILL, AIR_RECEIVER,
  CAST_LINE, CONT_CAST, DRY_COOLER, EVAP_ACID_VS, FOOD_STORE, IND_MELT, MAU_HX, METAL_STORE, PELLET, POLY_OLEFIN,
  POLY_STOCK, RF_HEAT, ROLL, STOCK_OUT, VAC_IND.

Zero bare `open` rows outside the SIF pass. Status: **study complete and honestly dispositioned; 34 engineering
actions remain open and tracked - not closed.** X-SAF-01 renders PARTIAL (see TASK_PLAN).

Handoffs (this lane cannot write these):

1. TE/LT loops for the 14+4 indication actions belong to X-CTL-01 (`flow_graph/inventory/other.py` writes the
   instrument rows; `docs-authority/_instr_index.py` tags them). When indexed, `_hazop.py` closes those rows
   automatically - the disposition rule already checks AQS-CTL-001.
2. The 16 relief actions close when the units' duty sheets issue section 6 (unit tasks 01/02 then 07); rerun
   `_hazop.py` + `_sif.py` after.
3. `INSTRUMENT_INDEX.csv` was regenerated (31 rows of range text drifted vs the Rev AC graph; no tag-set change);
   AQS-CTL-001 owners should be aware their committed index was one regen behind.

## X-MFG-34 / X-MFG-36 - bench test procedures

- `BENCH_TEST_UPW_POLISH.md` (AQS-TST-004): RO permeance/rejection + EDI CE/resistivity bench test per A-M-176
  against AQS-DUTY-070. Preconditions, instrumentation table, 8-step procedure, acceptance bands from the A-M-176
  bases (A >= 2.4 of 3 LMH/bar; rejection >= 0.98 at 95.5 % recovery; CE >= 0.08 of 0.10; pump eta >= 0.35 of 0.40),
  five data sheets, safety.
- `BENCH_TEST_H2_COMPRESSOR.md` (AQS-TST-005): first-article 5-stage run per A-M-169 against AQS-DUTY-067 Rev B.
  N2 phases A-C then H2 phase D, ESD test, teardown; acceptance bands (specific work <= 2.2 vs 1.97 kWh/kg design;
  stage discharge <= 135 C API 618; volumetric eta >= 0.75 of 0.80; zero interlayer leak).
- Both state the honest frame on their face: procedure ISSUED, run HARDWARE-GATED, A-M entry stays
  needs_verification until the data sheets are signed and the assumptions lane substitutes the values.
- TASK_PLAN renders both as PARTIAL with that status.

Register observation (not fixed here - assumptions lane): `assumptions_manual.json` entries A-M-169 and A-M-176 have
collided fields - `task`/`value`/`files` carry the X-INV-02C motor-model text while `title`/`statement`/`replace_when`
still carry the compressor and UPW bases. The procedures cite the surviving statement fields plus the AQS-DUTY docs;
the entries themselves need re-splitting by whoever owns the register.

## X-END-02 - BOM classing

`_eol.py` Rev B. Delta (AQS-END-002, 1020 lines):

| | Rev A | Rev B |
|---|---|---|
| unassigned | 113 | 89 |
| metal_plateable | 407 | 430 |
| organic | 394 | 395 |
| held (all reasons) | 192 | 199 |

Classified: 14 envelope lines from 8 electrical units via their duty sheet section 3 ("No wetted alloy. Conductors
are copper." -> Cu/steel WEEE route); 7 instrument building-block lines (electronics rule, `instrument` keyword);
1 gearmotor (LEACH_CSTR_1, steel rule); 1 MF-21 coil (`class H wire`/`bobbin` -> Cu rule). OF-34 (PFA-lined flow
meter) moved to the fluoropolymer HF hold (`pfa` keyword) - it was unassigned before, which understated the Q-011
hold. New `class_basis` column records keyword vs duty-sheet-3 vs held for every line.

Held, not silently unassigned: 88 envelope lines on units with no duty sheet yet (`held - material pending: no duty
sheet yet; assigned at unit task 09 under AQS-STD-002`) and 1 roll-up pointer line (OF-13 fabricated part set,
classed line-by-line in the unit BOMs). The `held - vendor TBD` pattern is defined for alloy choices genuinely open
at order time; no line needs it today, and the doc says so explicitly.

Status: **classing advanced and every remaining gap named; 88 lines still wait on unit task 09 - not closed.**
X-END-02 renders PARTIAL.

## TASK_PLAN

`_task_plan_gen.py`: new `PARTIAL:<path>|<status>` override kind (box open, `Start from <path>` + status note);
EVIDENCE_PASS/REOPEN_WHY updated for the four tasks. TASK_PLAN.md regenerated once at the end of the pass.

## Registers touched

DOC_REGISTER: +AQS-SAF-008, +AQS-TST-004, +AQS-TST-005, AQS-END-002 A->B. Observation (X-GOV-04 lane, not fixed
here): AQS-STD-002 is registered twice - line 168 `MATERIALS_STD.md` and line 243 `AQS-STD-002_CODE_BASIS.md`.
OPEN_QUESTIONS Q-011 fluoropolymer count synced 58 -> 51 (PFA-lined meters now inside the hold).

## Verification record

- Generator chain idempotent: second run of `_hazop.py` + `_sif.py` + `_eol.py` + `_task_plan_gen.py` leaves every
  output byte-identical (md5 checked).
- Suite 43/43 green at 13:28 with this lane's write-set in place and the tree otherwise clean.
- `_rev_stamp.py --check-only`: 876 derived files, 0 stale, gated stale [].
- Side effects, kept and disclosed: `inventory/INSTRUMENT_INDEX.csv` + `INSTRUMENT_INDEX.md` regenerated by
  `_instr_index.py` during verification (31 rows of range text had drifted vs the Rev AC graph; no tag-set change);
  `DERIVED_REVISIONS.md` rewritten by `test_regen`'s `--quick` run (rows move from "working tree" to b41e0c4; 0 stale).
- After 13:32 a sibling lane began editing `flow_graph/param/drivers.json` and `refs.py` in this working tree; the
  suite then went red on the solver/balance/misfit/regen tests (7 failures, all reading the sibling's mid-edit
  drivers state). None of the failures touch this lane's artifacts (`test_no_vendor_basis`, `test_governance`,
  HAZOP/EOL/TASK_PLAN all unaffected). This lane wrote nothing under flow_graph/, models/, cad/, design_tool/.
