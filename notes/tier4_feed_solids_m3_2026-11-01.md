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

## FLOAT_SINK (float/sink separator, tier 4) — commit 3

- `models/mfg/FLOAT_SINK/float_sink.py` on the shared lib. All 6 rows of the issued
  schedule drawn at tag, face, height and bore as atmospheric hose barbs (duty
  section 4: no flange class), the rating column carried verbatim as text: N1 DN50
  sink solids in on −Y at z 160; N2/N3 outlets and the N6 solids port (DN15, bore not
  calculated) on +Y at z 600; N4 drain boss to its 50 datum in the sink zone floor;
  N5 vent on the +Y rim bar flush at the 800 top.
- Internals: CPVC weir plate x 690..700 to z 700 (sink zone x 0..690 / float zone
  x 700..990) and the float launder at the +X wall (lip overflow z 700, channel floor
  z 640) — layout solids from the duty section 1 separation duty; the node internals
  row is none, so the tracker records no internal solid (hold). Weir laps the floor,
  launder laps the wall and the lip laps the channel floor: every union fused.
- Envelope: node `size_mm` 1000 × 600 × 800, recorded on the node as the study
  registry box; no design sizing exists on the node or the duty (hold). Build bbox
  1000.0 × 600.0 × 800.0 mm, one closed manifold solid; holdup 0.399 m³ at the
  720 mm working level net of internals, reported (A-VES; no residence claimed).
- Deliverables: exports, generated BOM with mass and make-or-buy, `fasteners.csv`
  (4 M10 wedge anchors, A4-70 on the polymer joint), `check.json`, `WORK_ORDER.md`
  (W1–W12), the seven-sheet drawing set (via the new shared `lib/sheets.py` driver;
  stale envelope `GA.md` superseded). `cad/stl/FLOAT_SINK.stl` replaced from the
  build. `tracker --check FLOAT_SINK` green.
- Holds named in WORK_ORDER W12: study registry envelope with no design sizing;
  study wall thickness; no holdup basis; unsized separation duty behind the weir and
  launder layout; the Class 150 rating column; the +Y outlet row packing versus the
  weir zoning; fastener lengths.

## NOX_SCRUB (NOx scrubber, tier 4) — commit 5

- `models/mfg/NOX_SCRUB/nox_scrub.py` on the shared lib. A-COL internals as envelope
  solids at recorded layout elevations: packing support grid (z 700), the 2303 mm
  packing (node design) in two beds with a redistribution disc (z 715..1866.5 /
  1881.5..3033), liquid distributor (z 3060), PP mesh demister (z 4043). CPVC shell
  OD 200, wall 6 (study, hold), skirt and plinth; the vent riser on the top head
  closes the 4103 envelope. All 15 schedule rows drawn at tag, face, height and bore
  as atmospheric hose barbs flush at the envelope faces on extension spools that
  cross the air gap and the shell wall (ray-set lengths); N11/N12 (no schedule
  datum) drawn at z 3400 in the gas space; N10's 2000 datum predates the sized
  column (hold). The z 400 row packs the full DN 200 chord - outer nozzles
  near-tangent, named hold.
- Envelope: node 600 × 600 × 4103 (X-PAR-03). Build bbox exact, one closed manifold
  solid; no holdup or stage/HTU count claimed (A-COL).
- Deliverables: exports, generated BOM, fasteners.csv, check.json, WORK_ORDER.md
  (W1–W12), the seven-sheet drawing set (stale GA.md superseded). `cad/stl` replaced.
- Holds named in W12: study wall; node PP-H vs duty CPVC (duty section 3 governs);
  layout bed elevations; no stage/HTU count; duty prose vs 15-row CSV; blank N11/N12
  datums; the clamped N10 datum; the tangent-row packing; Class 150 rating column;
  fastener patterns.

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
