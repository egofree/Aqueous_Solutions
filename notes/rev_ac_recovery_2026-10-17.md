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

## State when this note was written

- Authority contract: PASS (projection regenerated, revision AC).
- `_rev_stamp`: 656/676 derived files stale (truthful; regen needs the pipeline green).
- No invented rates: every restored number is verbatim BH with a provenance note;
  everything unknown is an explicit null.
