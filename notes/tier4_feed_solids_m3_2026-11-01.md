# Tier 4 feed and solids path to M3 — 2026-11-01

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7; per-unit
recipe pattern in `models/mfg/EW_1/WORK_ORDER.md`. Graph Rev AC. One commit per unit
(plan rule 4); this note gains a section per accepted unit.

## HOPPER (receiving hopper, tier 4) — commit 2

- `models/mfg/HOPPER/hopper.py` rebuilt on the shared lib. All 10 rows of the issued
  schedule `docs-authority/nozzles/HOPPER.csv` drawn at tag, face, height and bore as
  atmospheric hose barbs (duty section 4: no flange class), the rating column carried
  verbatim as text: inlets −Y at z 160 with roots set in the frustum wall (the slope
  stands off the envelope face), outlets +Y clamped below the barb radius at the
  envelope top, N7 drain boss to its 50 datum beside the 190 mm discharge opening, N8
  vent on the +Y rim bar (schedule datum 800 predates the 600 box).
- Envelope: node `size_mm` 600 × 600 × 600 (AQS-DUTY-064); the duty sheet section 2
  carries no size line (hold). Build bbox 600.0 × 600.0 × 600.0 mm, one closed manifold
  solid; holdup 0.1424 m³ (bin + frustum + outlet) reported, no residence derived
  (A-VES; the duty claims no holdup).
- Deliverables: exports (STEP assembly + closed STL), generated `bom.csv` with mass and
  make-or-buy, `fasteners.csv` (4 M10 wedge anchors, grade 8.8 on carbon steel),
  `check.json`, `WORK_ORDER.md` (W1–W12), and the seven-sheet drawing set (GA front/side,
  nozzle orientation, body, base plate + rim frame, aux, iso; stamped per AQS-DWG-002;
  the stale envelope `drawings/GA.md` superseded). `cad/stl/HOPPER.stl` replaced from
  the build. `python3 models/mfg/tracker.py --check HOPPER` green.
- Holds named in WORK_ORDER W12: study wall thickness (no authority states one); no
  holdup basis (A-VES volume report only); the missing duty size line; the Class 150
  rating column against the atmospheric duty; the clamped outlet datums; the vent datum
  above the box; the frustum-wall set-in roots; fastener lengths.
- Build note for the lane: the per-unit reads its bounding box back from the exported
  STL (the measure the tracker gate reads), because the OCC Bnd_Box of the lofted barb
  faces is loose by tens of millimetres; the mesh itself fills the envelope exactly.

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
