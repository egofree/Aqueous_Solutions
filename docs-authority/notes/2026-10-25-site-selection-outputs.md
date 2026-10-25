# Site selection and per-site output folders

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev G, AQS-PLAN-007 (X-LOC-04 done).

## Change

- `python3 -m flow_graph.param.regen --site <site_id>` regenerates a locale in a temporary git worktree of the current commit and copies the outputs that differ from the baseline to `sites/<site_id>/`, with `SITE_OUTPUTS.json` listing them and the profile hash. `--all-sites` runs the baseline in place and then every locale. With `--check`, a locale is regenerated and compared with its folder; nothing is written.
- Copied documents keep their base number with the site code as a suffix.
- Regeneration in this working tree refuses a locale selected through `AQS_SITE`, so a locale run cannot overwrite a baseline file. The copy step refuses any path outside `sites/<site_id>/`.
- The plan's earlier intent to stamp the site id and profile hash in every generated header is replaced by the manifest, which keeps every generator script unchanged.

## End-to-end check

A trial profile, committed only in a scratch worktree, with a different cooling design dry bulb was regenerated with `--site`, then checked with `--site --check`, which reported it current. The scratch worktree showed no change outside `sites/`. The trial showed that the cooling design dry bulb reaches only the driver listing: `docs-authority/_hot_draw_coolers.py`, which reads it, is not a regeneration stage. That is recorded for the first hot locale (X-LOC-07).

## Check

`scripts/check_all.sh --full` passes.
