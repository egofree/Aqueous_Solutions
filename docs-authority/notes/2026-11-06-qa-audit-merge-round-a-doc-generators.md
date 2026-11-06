# 2026-11-06 qa-audit strategic merge, round A: six subsystem pages became generated

This record states what the round merged from `origin/qa-audit` and why. Owner ruling
(2026-11-05): merge the best engineering content by strategic review, not a mechanical
replay; no force-push. The regeneration ran in a scratch worktree and its result was
committed; the main working tree was never the regenerator's write target.

## What was merged

The audit branch rewrote six subsystem pages from hand-kept files into generator outputs at
newer revisions, each regenerated from the plant graph. The generators, the wiring and the
sizing addition came over; the pages then regenerated from the current graph, so every rate
in them is the branch's own:

| Page | Revision here -> now | Generator |
| --- | --- | --- |
| POWER_SIZING (AQS-ELEC-007) | F -> J | `docs-authority/_power_sizing_doc.py` |
| WATER_PURIFICATION (AQS-WTR-001) | B -> C | `docs-authority/_water_purification.py` |
| LIFE_MEP (AQS-MEP-001) | A -> B | `docs-authority/_life_mep.py` |
| MEOH_TRAIN (AQS-MeOH-001) | A -> B | `docs-authority/_meoh_train_doc.py` |
| VENT_CLOSURE (AQS-VENT-001) | C -> D | `docs-authority/_vent_closure.py` |
| sizing/SANITATION (AQS-DUTY-063) | B -> C | `flow_graph/param/sanitation.py --write` |

- `flow_graph/param/sizing/power.py` gains `rectifier_trims(g)` (A-M-415): the electric trim
  heaters fed from the RECTIFIER node, counted at rated load in the plant bus demand. The
  file is otherwise untouched between the branches.
- The manifest carries the six stages (143 -> 149), placed before `code_basis` so the
  X-STD-01 code-basis block lands on the freshly written pages; `test_regen` validates the
  topological order.
- POWER_SIZING Rev J reads this branch's figures: bus demand 191.0 kW in four parts
  (extension hall 88.0, rectifier input 7.5 at the bounding electrowinning current, trim
  heaters 23.26 over four streams, the rest the continuous loads), and the standby rating
  20 kW with the rule check agreeing.

## Re-based at Q-040

`_power_sizing_doc.py` came from a state that still read the removed driver
`backup_gen_rated_kW`; here it reads the live rating from
`flow_graph/param/backup_fuel.py` rating_kw (owner ruling Q-040, 2026-11-05) and states the
method that way. The page's rule check reports the stamped rating and the rule agree.

## Deferred, with reasons

- `_wafer_fab_equipment.py` needs the audit branch's wafer-route family (a wafer-route sizing
  module and its stages, absent here); the current plant has its own solar-cell line. Belongs
  to the route-family review.
- `_mfg_equipment.py` expects the audit branch's MFG tool-list JSON shape; the current
  `doc_mfg_tools` output differs. Belongs to the MFG-equipment family review.

Both stay in the qa-audit tree; the citation scan confirms nothing on this branch references
their qa-audit-only paths.

## Checks

`pytest flow_graph/` passes (237 passed, 1 skipped, 1 xfailed). `scripts/check_all.sh --full`
passes on the committed tip (tests, staleness, authority contract, citations, style, and the
scratch regeneration that changes nothing twice).
