# 2026-10-30 — DONE_X comma injury repaired; X-LOC-01/02 return to done; the loader clause verified

## What changed

**Task-plan registry injury repaired**: the `DONE_X` set literal in
`docs-authority/_task_plan_gen.py` carried `"X-LOC-01""X-LOC-02"` — two adjacent
string literals with the separating comma lost, which Python implicitly
concatenates into the single member `X-LOC-01X-LOC-02`. X-LOC-01 and X-LOC-02
were therefore silently OUT of the done set and rendered as open tasks with
"Start from ... (partial)" markers, although both belong there: the 2026-10-19
evidence pass audited them into `DONE_X`, and their evidence stands
(AQS-PLAN-011 Rev J for X-LOC-01; `flow_graph/param/test_site_profile.py`, 11
passing tests, for X-LOC-02). The comma is restored. A scan of the whole set
literal found no other concatenation; the remaining duplicate members
(X-THM-03, X-RED-01..09, X-GOV-20, X-MFG-32, X-STD-01, X-PAR-10, X-MAT-07) are
harmless set-literal repeats from the historical append style.

**X-LOC-02's loader clause verified rather than assumed**: every consumer of
`drivers.json` goes through the loader (`DR.load()` / `DR.val()`); the only
path-level uses are legitimate file-level operations (the regen receipt hash in
`_ps_cache.py`, the design tool's drivers-sha256 provenance endpoint, and the
design tool's existence check before it loads through the loader). The dead
path constant `_D` in `flow_graph/param/water_tower.py` (superseded by its own
`_drivers()` loader call) is removed.

## Verification

`python3 docs-authority/_task_plan_gen.py` regenerates the plan with X-LOC-01
and X-LOC-02 done and cited; `pytest flow_graph/` 204 passed / 1 skipped
(including the site-profile identity gate). `scripts/check_all.sh --full`
idempotent.
