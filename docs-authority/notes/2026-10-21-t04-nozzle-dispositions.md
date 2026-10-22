# T04 nozzle-schedule dispositions — 20 desk-P2 items closed

Date: 2026-10-21. Items: the 20 unticked unit-task-04 (nozzle schedule) rows at desk P2.

## Basis

The `_nozzle_sched.py` nozzle rule (`_noz_edges`) counts a unit's schedulable connections as:
mass edges at kg/d, plus HL-/thermal kW edges that are not electrical. Electrical, cable and
kW_c energy rows are not nozzles (they belong to the cable schedule, X-ELS-06).

Two coverage classes close the whole batch:

1. **File exists** (13 units: LI_RECOVER, P_CA, LITHO_ALIGN, CRYO_HX_Q4, GREASE_CA, GREASE_LI,
   MET_HX_Q4, LOAD_AGG, PV_ARRAY, RECTIFIER, SOL_ARK_60K, GEO_HP, HYDRO_SET): the schedule file
   is current in `docs-authority/nozzles/`; zero piped kg/d process connections under the rule —
   the files carry the AQS-STD-001 section 4 drain/vent rows plus rows kept from earlier rule
   states (e.g. RECTIFIER DC/leach-trim, MET_HX_Q4 coil note). Status: schedule current, n/a
   connections.
2. **No file, by design** (7 units: FORGE, RES_HEAT, RF_HEAT, SI_REDUCE, ADS_CHILL, MAU_HX,
   EXT_HALL): machines and a building with nothing piped (`_nozzle_sched.py`: "machines with no
   piped process connection get no file — nothing to schedule, nothing invented"). SI_REDUCE
   additionally notes CHAR_TO_SI, a solids conveyor edge unrated since Rev AC — when the param
   pass rates it, the generator self-adds the row.

## Verification

- Per-unit closure text in `DONE_U` (`docs-authority/_task_plan_gen.py`), board regenerated:
  all 20 tick, desk P2 open count 29 → 9.
- `pytest -q` 43/43 (includes the plan-consistency test).
- `regen --check` 920 files 0 stale (unchanged this lane; no graph writes).

## Not closed here

The 9 remaining desk-P2 plant-level items: X-FIR-01 (fire tank/pump drivers; reopened pending
owners hall programme), X-MFG-31 (feed-blocked reactors), X-CTL-04/05, X-MAT-03 (gasket detail),
X-PRO-02, X-ASM-01/02, X-END-02.
