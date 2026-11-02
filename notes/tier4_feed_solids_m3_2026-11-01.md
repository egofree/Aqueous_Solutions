# Tier 4 feed and solids path to M3 — 2026-11-01

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7; per-unit
recipe pattern in `models/mfg/EW_1/WORK_ORDER.md`. Graph Rev AC. One commit per unit
(plan rule 4); this note gains a section per accepted unit.

## Pipeline repair ahead of the batch — housekeeping commit

- `models/mfg/style_builders.py`: the per-unit-script skip of the cold-box batch repair
  (f07280e2) referenced an `MFG` constant it never defined, so the `style_builders`
  regen stage crashed (`NameError`) whenever it ran argless, every doc stage after it
  was skipped, and the regen receipt converged false. The missing constant is defined;
  the stage passes again (82 built, 0 failed, 0 resized; the per-unit-script skip works
  as the repair intended).
- Consequence flushed: since that commit every full regen had died before the doc
  stages, so the doc layers had trailed the graph. This commit carries the regen
  refresh of those layers (cable schedule, control docs, motor and wire inventories,
  PLC-OIL, spares, task plan counts, derived-revision stamps) — generator output, no
  hand edits.
- Build note for the lane: per-unit bounding boxes are read back from the exported STL
  (the measure the tracker gate reads), because the OCC `Bnd_Box` of lofted barb faces
  is loose by tens of millimetres; the mesh fills the envelope exactly. STEP text also
  carries the OCC translator's in-process export counter, so a rebuilt style STEP can
  differ from the committed one by that one digit alone; such counter-only diffs are
  restored, not committed.
