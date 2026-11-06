# 2026-11-06 qa-audit merge: the route-family program, classified and ordered

This note is the working classification for the remaining qa-audit merge content. Rounds A
to C (2026-11-06) merged the doc-generator conversions, the sizing-stage doc rewrites and
the portable exporter fixes. What remains is the route program: the audit branch's
recovery-first re-booking of the plant's material routes. It is recorded here so the next
rounds execute it in dependency order instead of piecemeal.

## The dependency web

1. The recovery-first gate (A-M-423, owner decision t61u): a checker module plus
   `test_recovery_first.py`. The checker is not a writer - it reads `params.recovery` records
   that the transfer functions stamp and flags dock ore that no record covers. Its test
   fails until the stamping transfer functions are ported, so it lands with them, not
   alone.
2. `standby_routes.py` (A-M-433), `solvent.py`, `sulfuric.py` (new unit ACID_PLANT),
   `caustic.py` - the rated/retired route sets and the on-site acid and caustic coverage.
   The audit's route bookkeeping writes `base_kg_d` onto edges (`params` on the edge), a
   convention this graph does not carry yet; the stage modules read it.
3. `grease.py` (A-M-429) - shop grease sized from the maintenance plan; invoked by
   `fluoro_train.py apply()` after the acid plant is rated, and its calcium route slakes the
   ACID_PLANT cake residue. Depends on family 2.
4. `si_refine.py`, `fab_silicon.py`, `fab_resist.py`, `pv_wafer.py` and the `pv_cell_line.py`
   delta (A-M-436/437) - the silicon and wafer route. This plant has its own solar-cell line
   and wafer fab, so the audit's route shape does not transfer one-to-one; the family review
   decides what carries.
5. The exporter and drawing deltas that encode these routes (deferred in rounds A to C with
   reasons) follow their families.

Each family lands as its own commit series with the scratch-worktree regeneration, every
generated-figure change explained, and `scripts/check_all.sh --full` green before the next.

## What does not come over

- The audit branch's dated notes: they cite that branch's commit ids, which do not exist in
  this history; the citation check rejects them. The content comes over in the family
  commits, the diary stays on the audit branch.
- The generated trees of either branch: they regenerate from the graph.

## Adopted this round

`scripts/check_all.sh` takes the audit's commit-identity gate: a placeholder or unset
`git user.email` fails the gate before a commit reaches history. The audit branch's other
changes to the script are the same gate's help text.

## Checks

`scripts/check_all.sh` (now including the identity gate) and the full variant pass on the
committed tip.
