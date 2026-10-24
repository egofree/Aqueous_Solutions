# Duty sheets and nozzle schedules: residual authoring, 2026-10-20

Document number: AQS-PLAN-007 note (working record; no new AQS number).
Authority: AQS-PLAN-007 unit tasks 01 and 04. Companion to `docs-authority/notes/2026-10-20-evidence-audit.md`,
which named these residuals. Graph state: Rev AC (`flow_graph/plant_flow_graph.json`), HEAD 845e9a7,
suite 43/43 before and after, `regen --check` green (875 files 0 stale) before and after.
Scope: task-plan residuals part 1 — the 51 missing duty sheets, the 286 missing nozzle rows in
existing csvs, and the 55 absent nozzle csvs. No commits; the parent lane does the final
TASK_PLAN regeneration. Sibling lanes (instrument index, sizing modules) worked concurrently;
their write sets (INSTRUMENT_INDEX*, CAUSE_EFFECT, HAZOP*, sif_list) were not touched.

## 1. Duty sheets (unit task 01) — 51 authored, T01 124/175 → 175/175

Root cause of the gap: `_duty_basis.py` line 20 did `if not os.path.exists(p): continue` — the
generator only ever REFRESHED existing sheets; no code path authored a missing one. The 51 units
(FOUNDRY 27, POLYMERS 10, CRYO 4, DIGESTER 3, HEAT 3, OIL 2, GLASS 1, FARM 1) were made present by
the placeholders-to-real program (55d1033) and the CAD program (5f75bdb/845e9a7) without a
duty-sheet pass following.

Fix: the generator now AUTHORES a sheet when a present unit has none (`author()` in
`docs-authority/_duty_basis.py`). House AQS-STD-001 8-section standard; graph facts quoted, gaps
stated as pending:

- §1 from the graph closure (same line the refresh writes, so T01 detection reads it and future
  refreshes keep it live). All 51 close: T01 124/175 → 175/175 (universe includes the 2 boundary
  rows, which already carried sheets).
- §2 quotes what the node carries: `envelope` (size + basis, with the hold-up-hours sentence in
  the exact refresh-regex format), `design_storage` (AQS-DUTY-064), `sizing` (AQS-DUTY-072/073),
  `design` (AQS-PAR-001), flat node params with their study `basis` strings (e.g. ADS_CHILL,
  MAU_HX, DRY_COOLER quote AQS-HEAT-STUDY-002 A-M-239/241/244), node notes and internals.
  Units with none of these (GREASE_CA, GREASE_LI, P_CA, SI_REDUCE) say
  "Sizing calculation pending (unit task 02)".
- §3 material only where the node carries one (design.material / design_storage.material, e.g.
  POLY_F Hastelloy C-276, HF_GEN carbon steel/Monel); otherwise pending (task 09).
- §4 points at `nozzles/<UNIT>.csv` (see §2 below) with the AQS-PIP-003 basis sentence;
  units without piped connections say so plainly.
- §5 loops read live from AQS-CTL-001 (H2O_ELYZ carries 4 loops; the other 50 state
  "No instrument loop ... yet (unit task 08)").
- §6 quotes node relief data where it exists (H2O_ELYZ blocked-outlet case, A-M-196, bore 3.3 mm,
  design 990 kPa g), names vent edges where the graph has them (CR_CELL, MO_CELL, SHELL_BURNOUT),
  else "Relief case study pending (unit task 07)".
- §7 shop/not-stamped + `cad/stl/<UNIT>.stl` pointer where the envelope exists.
- §8 open items name every pending task explicitly, including the un-rated edges
  (GREASE_CA/LI, P_CA, SI_RECOVER mass edges carry no kg/d rate yet — §1 honestly reads zero
  flow until the parametric model rates them).

Side effect, expected: T07 (relief case = §6 heading) ticks 122 → 173, since every new sheet
carries an honest §6. T02/T03/T05/T06/T08/T09/T10/T12/T13 counts are unchanged. The 5 D-DOCK
stores (FOOD_STORE, METAL_STORE, AIR_RECEIVER, PROD_O2, PROD_MEOH) already tick T02 via
AQS-DUTY-064 STORAGE_HOLDUP.

## 2. Nozzle schedules (unit task 04) — generator issued, T04 28/173 → 153/173

The audit had found "no generator in the tree" — the csvs were hand-issued static artifacts.
Issued `docs-authority/_nozzle_sched.py` (new; the generator the mission asked to find did not
exist). Rules:

- Coverage rule = the T04 check in `_task_plan_gen.py` verbatim: one row per present process
  connection (mass kg/d edges plus HL-/thermal kW edges; cables are not nozzles), matched by
  service text == edge `carries` (the `_pid_sheets.py` match rule). Existing hand rows are
  preserved verbatim; only missing rows are appended.
- size: the AQS-PIP-004 line DN of the edge. AQS-PIP-003 basis: the piped bore is the nozzle
  bore basis; bores are NOT recalculated (no duty-sheet study value is needed). Non-piped
  transfers carry the line-list classification verbatim (`solids` — conveyor, bin or hand
  transfer), e.g. AL_POT Al-metal outlet.
- rating Class 150 (house schedule class, 1089 of 1093 issued rows); face inlet/outlet from the
  edge direction; height = the house placeholder elevations already used across the issued
  schedules (inlet 160 / outlet 600 / drain 50 / vent 800 mm) — stated on the sheet §4 and here
  as placeholders pending vessel design (tasks 02/06), not designed elevations.
- New files (absent csvs): one row per connection + the drain and vent utilities
  (AQS-STD-001 §4). Vessels with no piped connection (GREASE_CA, GREASE_LI, LI_RECOVER, P_CA)
  get the utilities-only file so the T04 status note reads truthfully. Machines with no piped
  process connection (RF_HEAT, RES_HEAT, FORGE, SI_REDUCE, ADS_CHILL, MAU_HX) get NO file:
  nothing to schedule, nothing invented.
- Idempotent: second run appends nothing (one-time settle: 2 sheets' hold-up hours converged to
  the legacy refresh fixpoint; §1 untouched).

Result: 48 csvs created (55 absent − 6 machines with nothing piped − EXT_HALL), 592 rows appended
total: 177 process rows in the created csvs (+ 96 drain/vent utility rows) and 319 rows across the
82 existing csvs the check finds short. The audit's 286 was counted at the 55d1033 tree; the graph
moved to 845e9a7 underneath (Cl2 offtake edges et al.), and the same-carries counting rule counts
parallel connections per row (e.g. LEACH_CSTR_1's three "anode Cl2 (+ O2 side)" lines).

T04 after: 153 ticked / 20 open. Every open box is a unit with ZERO piped process connections:
13 utilities-only csvs (CRYO_HX_Q4, GEO_HP, HYDRO_SET, LOAD_AGG, MET_HX_Q4, PV_ARRAY, RECTIFIER,
SOL_ARK_60K, LITHO_ALIGN + the 4 new vessel files) rendering "no piped process connections;
nozzle schedule n/a", and 7 units with no csv and nothing piped (the 6 machines above + EXT_HALL,
a hall). No csv anywhere is short of its unit's connections (verified with the exact check logic:
0 deficits plant-wide).

## 3. Verification

- T01 detection rerun: 175/175 tick (was 124).
- T04 detection rerun: 153/173 tick, 0 rows missing anywhere (was 28/173, 286+177 rows missing).
- `_task_plan_gen.py` rerun into the tree and reverted: 2887 tasks, 1089 → 1316 done
  (+51 T01, +125 T04, +51 T07 side effect). TASK_PLAN.md restored — parent does the final regen.
- `python3 -m pytest -q`: 43 passed.
- `python3 -m flow_graph.param.regen --check`: rc=0, 875 files 0 stale (before and after;
  note the check itself rewrites DERIVED_REVISIONS.md's "last graph commit" line 55d1033 → 845e9a7
  — restored, it is not this lane's write).
- Write set of this lane: `docs-authority/_duty_basis.py` (authoring branch),
  `docs-authority/_nozzle_sched.py` (new), `docs-authority/duties/*.md` (51 new) +
  `duties/_generated.json` (manifest; graph sha unchanged), `docs-authority/nozzles/*.csv`
  (48 new, 82 appended), this note. No commits.

## 4. Residual gaps

- 7 present units have no nozzle csv because the graph gives them no piped process connection
  (RF_HEAT, RES_HEAT, FORGE, SI_REDUCE, ADS_CHILL, MAU_HX, EXT_HALL). Their T04 boxes stay open
  with no note; the first piped edge that appears gives them a schedule. Nothing here is
  unsizable.
- GREASE_CA / GREASE_LI / P_CA / SI_RECOVER mass edges (WAX_TO_GREASE_CA, PCA_TO_GREASE,
  GREASE_CA_TO_MFG, CHAR_TO_SI, POLISH_TO_LI, LI_TO_GREASE) carry no kg/d rate; their §1 reads
  zero flow and their csvs are utilities-only until the parametric model rates those edges.
- Nozzle heights everywhere are the house placeholders; real elevations land with unit tasks
  02/06 (vessel design).
- §5 loop membership was read at authoring time; the instrument-index sibling lane was writing
  AQS-CTL-001 concurrently (only H2O_ELYZ had loops among these 51 at read time). If that lane
  adds FOUNDRY/POLYMERS loops, the new sheets' §5 pending sentences lag until the next
  `_duty_basis.py` pass re-authors nothing (sheets exist) — re-word by hand or note on T08.
