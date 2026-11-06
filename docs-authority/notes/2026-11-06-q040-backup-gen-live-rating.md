# 2026-11-06 Q-040 lane: the standby generator rating derived from the live critical list

Owner ruling Q-040 (2026-11-05): the standby generator rating is parametric from the live
critical-load list under AQS-ELEC-007 / AQS-RED-001 (125 percent, rounded up in 5 kW steps),
not a hard-coded nameplate in the driver file. The pumped-hydro store keeps its own Q-009
basis (the issued 32 kW list), unchanged.

## What changed

- The hard-coded driver `backup_gen_rated_kW` (40 kW, frozen from a stale 32 kW issued list)
  is removed. New drivers `ELEC.generation-train.BACKUP_GEN.crit_margin` (1.25) and
  `ELEC.generation-train.BACKUP_GEN.rating_step_kw` (5.0) carry the rule's constants.
- `flow_graph/param/backup_fuel.py` gains `rating_kw(gc, d)`: the single computation of the
  rating from the live critical list (HABITATION 3.00, CRYO_H2 compressor peak 2.83,
  CRYO_ASU duty 1.75, GROW_BED 5.00, controls and instruments 2.00 = 14.58 kW; 125 % =
  18.23 kW; rounded up in the 5 kW step).
- The rating moves **40 -> 20 kW**. Consumers re-derive: `write_graph power()` stamps
  `rated_kW` and the basis text on the graph node; `docs-authority/_power_sizing.py` takes
  `gen_kW` from the same function; `o2_close.py` reads the stamped value (computing it itself
  only if the stamp is absent) and its exercise-fuel chain re-solves: the NFPA 110 8.4.2
  monthly-exercise average halves to 0.0041 kW, with the hydrogen exercise fuel and the
  C5-C10 fallback reserve following.
- `flow_graph/param/test_system_tree.py` no longer pins the exercise average to the retired
  40 kW basis; it checks the exercise average against the rated kW the graph carries at the
  NFPA 110 basis.

## Checks

`pytest flow_graph/` passes (237 passed, 1 skipped, 1 xfailed). `scripts/check_all.sh --full`
passes on the committed tip, including the staleness gates and the scratch regeneration that
changes nothing. The regeneration ran in a scratch worktree and its result was committed; the
main working tree was never the regenerator's write target.
