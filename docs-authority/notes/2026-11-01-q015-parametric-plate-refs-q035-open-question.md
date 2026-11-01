# 2026-11-01 — Q-015 follow-through: plate-size mentions made parametric; Q-035 opened

## What changed

**Q-015 follow-through (AQS-BLD-001 Rev H, AQS-SCALE-001 Rev E)**: the owner
ruling of 2026-10-30 (open question Q-015, recorded in OPEN_QUESTIONS.md) made
the module plate parametric: sized from the drivers (`base_bays_x`,
`base_bays_y`, `bay_mm` in `flow_graph/param/drivers.json`) by need, with no
fixed plate size in any document. BUILDING_STACK.md already carried the ruling
in the opening paragraph of its levels section; this change removes the
remaining literal plate sizes that contradicted it:

- BUILDING_STACK.md section 7: "Scale is set by `SCALE_M` (1 = ...)" now names
  the baseline bay grid (`base_bays_x` × `base_bays_y` bays from
  `flow_graph/param/drivers.json`) instead of a fixed size.
- BUILDING_STACK.md Table 7.1: the ARRAY_ROOF row reads "plate-projected
  (driver-sized)" instead of a fixed projected size.
- BUILDING_STACK.md section 8 lead: "The plate carries the `SCALE_M = 1`
  baseline bay grid unchanged", dropping the literal size.
- SCALE_MODEL.md Table 4.1 (`SCALE_M` driver row): "1 = baseline plate
  (`base_bays_x` × `base_bays_y` × `bay_mm` from `drivers.json`)".

The factual build record in SCALE_MODEL.md (section 11, the saved
`plant.FCStd` entry) is left as written: it records what was built and cites
Q-015. `models/freecad/params.py` is not touched; it already matches the
drivers. No plant rebuild.

**Q-035 added (OPEN_QUESTIONS.md Rev C)**: locale design passes. The 16
placeholder locale-promotion units carry registered design bases
(A-M-396 to A-M-411) and defer sizing to "the locale design pass", but no task
commissions those passes. Question: commission them, and in what order, or do
the profiles stay at study completeness until a site design is ordered?
Default: defer; profiles stay study-complete. GEO_ORC remains separately ruled
(D-GEO_ORC). Task anchor: X-LOC-05 (closed), as with the other locale owner
questions. Next free Q number verified: Q-034 was the last row.

## Verification

`bash scripts/check_all.sh` passed (tests, 1 % misfit gate, staleness gates,
authority contract, citation check, documentation style check) before the
commit. The two pages carry rev-table rows for this change.
