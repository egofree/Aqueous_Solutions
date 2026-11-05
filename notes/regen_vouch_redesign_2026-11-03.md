# Full-regen cascade root cause: one flaky view render un-vouched the whole tree (2026-11-03)

## Answer first

The staleness gate rejected the tree a full regeneration produced (rc 1, 959 gated-stale
files) because of a three-layer failure, not an output-glob bookkeeping gap:

1. **Trigger.** Graphviz `dot` 2.42.4 intermittently renders two different layouts for
   byte-identical input (`views/mfd.dot`, the "trouble in init_rank" flake already recorded in
   `notes/fab_fabtools_m3_2026-11-02.md`). `flow_graph/render_layer_views.py` re-ran `dot` on
   every regeneration pass even when the generated `.dot` was byte-identical, so the doc phase
   of `python3 -m flow_graph.param.regen` could oscillate `views/mfd.svg` pass after pass and
   hit the convergence cap: `failed: ["(doc-convergence)"]`. Reproduced live on
   `qc/batch-1-farm-design-tool-placement` at `8e3cc8f5`: a full regen changed `mfd.svg` while
   `mfd.dot` was byte-identical to HEAD, and the parked cascade (a stash made at `10121b5b`;
   since 2026-11-04 kept locally as `refs/review-backup/stash-2026-11-03-full-regen-cascade`) carries the full failure state: receipt `converged: false`, board
   "1773 derived files, 959 stale".
2. **Amplifier.** `_rev_stamp.py` trusted the regen receipt's `vouched_patterns` only when the
   receipt said `converged: true`, and `regen.py` set `converged = not failed` globally. One
   oscillating SVG therefore un-vouched all 476 patterns in one step, and every derived file
   committed before the last graph commit went stale at once: 959 false stale files.
3. **Latent drift.** The per-unit commit lane (batch-1 farm design tool) committed new
   `models/mfg/*/fasteners.csv` and BOM sources with targeted generator runs, so the
   cross-unit aggregates behind them (`flow_graph/inventory/other_family_ids.json` +4 fastener
   families OF-133..136, `inventory/PLANT_BOM.csv` ±93, `inventory/SELF_COPY_RECON.csv` ±61,
   EOL/cost/spares cascades) were not a regeneration fixed point. The gate cannot see this
   class of drift (it compares file commits against graph commits and receipt vouches, and the
   aggregates were vouched), so the committed tree stayed green while a full regen produced a
   24-file diff. This drift is real work the pipeline should surface and commit; it was never
   the reason the gate went red — layer 2 turned it into a cascade, and the stash proves the
   red board was the flake, not the drift (the drift diff is 24 files; the stale list was 959).

## Changes

- `flow_graph/render_layer_views.py` — render determinism at the generator: when the
  generated `.dot` equals the on-disk `.dot` and the SVG exists, keep the SVG (skip path); a
  render that is needed repeats until two consecutive renders agree (bounded), so committed
  bytes do not depend on which layout one invocation produced. Repeated regen passes are now
  byte-stable by construction and can no longer oscillate on a view.
- `flow_graph/param/regen.py` — the receipt vouches per-stage verification, not run success:
  `vouched_patterns` for stages that ran ok and whose outputs+amends the final doc pass
  verified hash-stable; `vouched_files` for the individually stable files of a partly unstable
  stage; receipt `stages` entries carry `stable`. The monotonic carry-over of prior vouches is
  removed: a vouch is a verification made by the run that writes it, never inherited. A
  doc-phase failure now names the unstable stages in the log.
- `docs-authority/_rev_stamp.py` — the gate trusts the receipt on a graph-sha match alone
  (`receipt_vouched`); `converged` stays in the receipt as run-health reporting and still
  gates the regen exit code. One unstable stage now costs exactly that stage's own outputs,
  never the tree.
- `flow_graph/param/regen_manifest.json` — dated note for this correction; regen_derived
  stage note states the render determinism contract.
- Tests (house rule: invariants get a check, not a sentence): `flow_graph/test_render_views.py`
  (to_dot purity, skip-path byte-stability, end-to-end double render), `test_vouches_only_verified_stages`
  and `test_receipt_vouches_map_to_ok_stable_stages` in `flow_graph/param/test_regen.py`,
  `test_receipt_vouch_trust_is_sha_only` in `flow_graph/param/test_governance.py`.

## Semantics after the fix

A vouched pattern/file means: this regen run re-derived it at the receipt's graph sha and
observed it byte-stable. The gate clears a derived file when it matches a vouched pattern/file
at the current graph sha, or its last commit postdates the last graph commit. A committed
receipt is honest only if its run's output tree was committed with it; the pre-push check
(`scripts/check_all.sh --full`, `flow_graph/check_regen_idempotent.py`) remains the check for
that, and per-unit commits that change non-graph sources must re-run the aggregate stages they
feed (`inventory_other`, `doc_plant_bom` and its downstream) before committing.

## Evidence

- Full regen at HEAD before the fix: 24 changed files, gate green only because the run
  converged; `mfd.svg` changed with a byte-identical `mfd.dot` (flake captured in the act).
- The same stash (made at `10121b5b`): receipt `converged: false`, `failed:
  ["(doc-convergence)"]`, board "959 stale" — the reported failure, in the receipt's own bytes.
- After the fix: full regen → full regen is byte-identical, `scripts/check_all.sh` green.
