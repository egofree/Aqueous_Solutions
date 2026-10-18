# Rev AC recovery state — 2026-10-17

Document number: AQS-NOTE-REVAC-RECOVERY (working note; not a plan page).
Authority: graph Rev AC (`flow_graph/plant_flow_graph.json`). Owner-session handoff record.

## What happened

Commit `6e25619` ("Update to graph Rev AC") pushed a scope pivot (farm/bio out,
foundry/polymers in: 212 -> 165 units) **without running any check**: the projection,
derived registers, param pipeline and task plan were all left at Rev BH state, and the
consolidation dropped graph data that the closed-balance stack depends on.

## Recovered this session (commits through this note)

1. **Rate keys**: 159 of 247 edges lost their `rate` key entirely. 70 restored verbatim
   from Rev BH (`fa1b4db`) on identical topology; 89 new Rev AC edges given explicit
   null-rate objects (`status: null`, note names them "unrated pending param pass").
2. **Rate values**: 42 edges kept the key but had `value: null` on identical topology;
   BH values restored with provenance notes. 7 deliberate typed nulls
   (`null_rate_kind=...`) left null.
3. **Dropped edges**: 185 BH edges absent from AC whose both endpoint units survived
   restored verbatim (EW harvest/Cl2/H2 families, HL cross-ties, S-numbers). 544 BH
   edges touch retired units and stay retired. Edge count now 432.
4. **Pipeline adaptation**: `_one_line.py` and `_power_sizing.py` tolerate null rates,
   absent PV `nameplate_kw` (Rev AC stores `module_kw x count`), and gate critical
   loads on node presence (CRYO_ASU, GROW_BED). `ess_tf.tf()` gates the farm loop,
   galley, compost toilet, heat sink and VEG_BED blocks on node presence.
5. `solver/stub.py` PV double-count fixed; graph `mvs.revision` aligned to AC;
   `flow_graph/models.py` + design_tool `models.py` widened for Rev AC data shapes.

## Still failing (the missing facts, per X-GOV loop step 6)

`pytest flow_graph/` = 10 failed / 17 passed:

- `param/test_balance.py` (3), `param/test_param_misfit.py` (3), `param/test_envelopes.py`
  (1), `test_heat_ladder.py::test_heat_ladder_stores_close` — blocked at
  `o2_close.py` (`KeyError: IA-NOX-N2`) then `balance.physics()`'s inline farm/terrace
  references (S04/S87/GROW_BED/COMPOST/IA-TERR-*/`_unit_resid(g,'CRYO_ASU')`).
  Dead units referenced by the surviving stack: `FORM`, `H2O_ELYZ`, `EVAP_ACID`,
  `CRYO_ASU`, `COMPOST`, `HEAT_SINK`, `NFT`, `MISTER`, `DUAL_ROOT`, `VEG_BED`, `BSFL`,
  `FISH_SUMP`, `HAB_GALLEY`, `COMPOST_TOILET`, farm units. Decisions needed: gate,
  remap (e.g. RECT_EW -> RECTIFIER exists), or re-basis.
- `param/test_governance.py::test_gated_derived_files_not_stale` — gated files
  `BALANCE_RECONCILIATION.md` and `sizing/REACTOR_DESIGN.md` need the balance/power
  pipeline green before regeneration.
- **GROW_BED is alive while its whole closure neighbourhood (DUAL_ROOT, BSFL, COMPOST,
  VEG_BED) is retired** — its water/carbon/lighting TFs are skipped by the farm gate;
  it will not close until re-based or retired. This is the largest single open item.
- 88 new Rev AC edges (fluoride chemistry, Ti/Mo cells, HL-HX8-Q3 cross-ties,
  foundry) are unrated; `test_param_misfit` numeric closure over them is open X-PAR
  work, not recoverable from BH.

## QA pass 2026-10-17 (full-repo audit, three independent lanes + hygiene)

- **Regression found and fixed**: the edge-restore rule keyed on topology only and
  re-added 10 BH routes whose `stream_id` Rev AC had deliberately re-routed
  (S02/S03/S50 to CRYO_* sources, IA-BMED-03/04 to CRU feed, S12, S08G, S20 reverse,
  IA-POL-02, DOCK_EXPORT_TBD) — double-booked flows. All 10 restored duplicates
  removed; AC-native routes kept; graph now 422 edges, 0 duplicate stream_ids
  (the authority checker's "422 streams" = unique ids). Tests unchanged 10F/17P.
- Corrections to this note: `test_param_misfit` failures are **4**, not 3
  (`test_roof_carries_pv` shares the `solver.py KeyError 'IA-ACID-01'` root cause).
- **Newly recorded gaps**:
  - `_task_plan_gen.py` cannot regenerate TASK_PLAN: (1) hardcoded
    `os.chdir('/tmp/aqs.dFW2/Aqueous_Solutions')`, (2) 53 present nodes carry
    sector_ids unmapped in its `sysof()` (DIGESTER 23, FOUNDRY 20, POLYMERS 10).
    Committed TASK_PLAN.md still names Rev BH / 212 nodes.
  - `_assumptions_register.py` exit 1: 18 stale keys (LEACH_CSTR_1 hx5/liquor_T,
    EW_1..9 params.sizing, WS_NITRIC, WS_PEROX).
  - `pytest` rewrites tracked `docs-authority/DERIVED_REVISIONS.md` as a side
    effect (governance test re-stamps it).
  - `schema/plant_flow_graph.schema.json` drifted: 421 errors vs the live graph
    (enums predate Rev AC, vestigial `rate_kg_d`/`rate_status` on 247 BH-surviving
    edges, bare-string modules, `notes_rev_H..AC` case) — unused by any test.
  - S34/S34B missing `layers`+`namespace`; 10 `presence:'study'` HL-* semantics.
  - Known open security: `pack_name` traversal in export (live-confirmed escape
    from `exports/`); non-atomic sandbox mirror writes (`store._mirror`).
- Verified green: authority contract, export round-trip byte-stable, recovery
  provenance (full-population verbatim BH match, 0 invented rates), API smoke
  (PV dedup 77.5 kW live), web build, canonical-vs-working-copy parity (zero
  drift), git hygiene (fsck clean, remote == main).

## Owner decisions 2026-10-17

- R8 acid loop: restore EVAP_ACID/EVAP_BASE from Rev BH (books still size them).
- Sector ontology (owner correction): the plant is organized into SECTORS, not
  task-plan groupings. DIGESTER is the renamed WET line; FOUNDRY, MFG, FAB, FARM,
  HAB, POLYMERS are each their own sector. A DIGESTER->MET task-plan mapping was
  applied and REVERTED same day (owner stopped it); the task-plan system structure
  is pending the sector-hierarchy review — do not fold sectors into other systems
  without an owner decision.


Wave 1 — independent, parallelizable (small, verifiable):
- R1 `pack_name` validation in `export/pack.py` (reject `/`, `\`, `..`; assert
  resolve-containment under `EXPORTS_DIR`) + endpoint error mapping (ValueError→400,
  FileNotFoundError→404). Accept: traversal attempt returns 400 and nothing is
  written outside `exports/`; normal export 200.
- R2 atomic `store._mirror` (tmp + `os.replace`), corrupt-mirror `get()`→KeyError
  (404), `threading.Lock` on mutations. Accept: truncation test yields 404, not 500.
- R3 `_task_plan_gen.py`: drop hardcoded `/tmp/aqs.dFW2` chdir, resolve root from
  `__file__`. Accept: runs from repo root.
- R4 `_rev_stamp.py`: split check() from write; governance test uses check-only.
  Accept: pytest leaves the working tree clean.
- R5 S34/S34B `layers`+`namespace` added (mass/S) with provenance note; delete
  working-copy `sys` artifact. Accept: pydantic+schema clean on those ids.

Wave 2 — decisions then regeneration:
- R6 `_task_plan_gen.py` sector mapping for DIGESTER/FOUNDRY/POLYMERS (proposal:
  DIGESTER→BIO, FOUNDRY→MET, POLYMERS→MFG; owner to confirm; assumption entry
  required per AGENTS.md). Accept: TASK_PLAN.md regenerates at Rev AC / 164 nodes.
- R7 Regenerate `schema/plant_flow_graph.schema.json` from the pydantic models
  (or delete it if unmaintained). Accept: 0 jsonschema errors on the live graph.

Wave 3 — param pipeline (multi-session, ordered):
- R8 Unblock: gate/remap dead refs in `solver.py` (IA-ACID-01 / EVAP_ACID decision),
  `o2_close.py` (IA-NOX-N2, FORM, H2O_ELYZ), `balance.physics()` farm tail.
  Accept: `balance.reconcile()` runs to completion.
- R9 Reconcile `_assumptions_register.py` 18 stale keys with R8's outcome.
  Accept: exit 0, AQS-REG-002 regenerates.
- R10 Rate the 88 new Rev AC edges per system (FOUNDRY 31 gaps first), re-basis or
  retire GROW_BED, close residuals. Accept: 10 failing tests → 0.
- R11 Regenerate gated docs (BALANCE_RECONCILIATION, sizing/REACTOR_DESIGN) and
  sweep the 656 stale derived files. Accept: `_rev_stamp --check` exit 0.

## State when this note was written

- Authority contract: PASS (projection regenerated, revision AC).
- `_rev_stamp`: 656/676 derived files stale (truthful; regen needs the pipeline green).
- No invented rates: every restored number is verbatim BH with a provenance note;
  everything unknown is an explicit null.
