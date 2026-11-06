# 2026-11-06 qa-audit merge round C: the matplotlib exporter audit, the portable part

Owner ruling (2026-11-05): merge the best engineering content by strategic review, not a
mechanical replay; no force-push.

## What was merged

The audit branch's X-RTE-LEGACY-PFD round rewrote the matplotlib exporter folder's README as
a numbered annex of AQS-FLOW-GRAPH-001 (purpose and scope; what the regeneration runs; where
on-demand images go) and fixed stale labels and paths in individual exporters. The portable
part came over:

- `flow_graph/exporters/matplotlib/README.md` - AQS-FLOW-GRAPH-001 annex, Rev B, with one
  deliberate adaptation: the audit branch's section 2 stated that the regeneration runs
  seven PFD exporters; on this branch `flow_graph/regen_derived.py` regenerates the layer
  views only, the matplotlib renders having been retired from the pipeline on 2026-10-27
  (AQS-UI-001 Rev D). The section states this branch's behavior.
- `backup_gen_pfd.py`, `geothermal_pfd.py` - the sheet-attribution lines drop the reference
  to `POWER/Power_System_overview.md`, a path outside the repository that does not exist
  here.
- `building_stack_pfds.py`, `campus_life_hazard_pfds.py` - the FreeCAD parameter loader
  gains the model-tree candidate path (`models/freecad/params.py`), so the sheets read live
  geometry when run from the repository.
- `wet_line_factory_pfd.py` - the sheet is numbered (AQS-PFD-WET-001).

The doc register's parts table now lists the annex (36 parts); `test_doc_numbers` passes.

## Deferred, with reasons

- `cryo_pfd.py` and `solar_cell_pfd.py` - their deltas encode the audit branch's route set:
  a dropped stream register entry (S18, retired there) and the wafer-route edges
  (IA-PV-WAFER/IA-PV-CELL) that this graph does not carry. Belong to the route-family
  review.
- `fab_upw_pfd.py` - its fix re-points a label at the audit branch's wafer-fab layer view,
  which this branch does not generate. Belongs to the fab-family review.
- The deleted exporters (`wafer_fab_pfd.py`, `fab_reagent_forks_pfd.py`,
  `metal_forming_pfd.py`, `mfg_shop_pfd.py`) - the audit branch retired those routes; this
  plant keeps the units. A plant-scope decision that belongs to the route-family review, not
  a merge item.

## Checks

`pytest flow_graph/` passes (237 passed, 1 skipped, 1 xfailed). `scripts/check_all.sh --full`
passes on the committed tip.
