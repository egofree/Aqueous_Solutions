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

## MET_SCRUB (metal-aisle scrubber, tier 4) — commit 6

- `models/mfg/MET_SCRUB/met_scrub.py` on the shared lib. Same column family as
  NOX_SCRUB at the node design D 800: PVC-U shell (wall 6, study, hold; the graph
  gives no gas temperature — above 60 °C it would be CPVC, held), skirt + plinth,
  A-COL internals as envelope solids (support grid, 2303 mm packing in two beds with
  a redistribution disc, distributor, PP mesh demister). All 9 schedule rows drawn
  at tag, face, height and bore; N9 DN300 air return (z 600) drawn as a plain stub
  at the house OD series 323.9 — outside the lib DN15..DN50 hardware table (hold);
  N7's 2000 datum predates the sized column (hold). bbox 1200.0 × 1200.0 × 4103.0
  mm exact, one closed manifold solid; no holdup or stage/HTU count claimed (A-COL).
- Deliverables: exports, generated BOM, fasteners.csv, check.json, WORK_ORDER.md
  (W1–W12), the seven-sheet drawing set (stale GA.md superseded). `cad/stl` replaced.
- Holds named in W12: study wall; missing gas temperature; node PP-H vs duty PVC-U;
  layout bed elevations; no stage/HTU count; the DN300 lib-table gap; the clamped
  N7 datum; Class 150 rating column; fastener lengths.

## HX8 (EW reject / Q4 preheat exchanger, tier 4) — commit 7

- `models/mfg/HX8/hx8.py` on the shared lib. Vertical PVC-U shell OD 340 (wall 6,
  study, hold) on a plinth inside a four-post hold-down frame, filling the study
  registry envelope 600 × 400 × 600 exactly. The bundle is real hardware: 46 PVDF
  tubes OD 10 × 360 between two tube sheets, 0.5202 m² of tube area from the model
  against the 0.51 m² duty figure (A-HX; the duty carries the heat rate 4.59 kW at
  U 1500, LMTD 6 K, so the area is duty-sized and reported, nothing resized; the
  0.0102 m² whole-tube surplus is named).
- All 7 schedule rows drawn at tag, face, height and bore; the z 600 outlet datums
  clamped below the barb radius, the 800 vent datum flush at the top head (holds).
- Data repair in the lane: two hand-era rows of `docs-authority/nozzles/HX8.csv`
  (N2/N3) carried an unquoted comma that shifted their face and height fields
  (face read " Q4 return preheat", height None); repaired to the quoting of the
  identical N6/N7 rows. The generator only appends and preserves hand rows verbatim,
  so the fix is a source-data repair, recorded in the WORK_ORDER and this note.
- Deliverables: exports, generated BOM, fasteners.csv, check.json, WORK_ORDER.md
  (W1–W12), the seven-sheet drawing set (stale GA.md superseded). `cad/stl` replaced.
- Holds named in W12: study registry envelope; study shell and tube walls; the
  whole-tube area surplus; clamped outlet datums; the vent datum; the Class 150
  rating column; the schedule-row quoting repair; fastener patterns.

## MET_HX_Q4 (Q4 loop straight-tube exchanger, tier 4) — commit 8

- `models/mfg/MET_HX_Q4/met_hx_q4.py` on the shared lib. Vertical 316L shell OD 540
  (wall 3, study, hold) on a plinth inside a four-post hold-down frame, filling the
  study registry envelope 1000 × 600 × 800 exactly. The bundle is drawn hardware:
  198 tubes OD 12 × 525 (wall 1.5, study, hold) between two tube sheets at z 120/660,
  3.9188 m² of tube area REPORTED AS DRAWN, not called calculated - the node carries
  no heat rate (A-HX; duty sections 2 and 8), and no duty area figure exists to be
  over or under (unlike HX8, whose duty carried 4.59 kW and 0.51 m²).
- All 3 schedule rows drawn at tag, face, height and bore as atmospheric hose barbs
  (duty section 4): N1 DN15 heat out on +Y at z 600 (fits the 800 box), N2 drain
  boss on the base head to its 50 datum, N3 vent flush at the top head - the 800
  datum IS the envelope top, drawn exact.
- Material conditional: drawn 316L per duty section 3's wet branch ("316L if the
  stream is wet or chloride"); the carbon-steel alternative (dry hydrocarbon or dry
  gas stream) is a named hold. The schedule rating column (Class 150) carried
  verbatim as text; no flange drawn (W4 110 % rule).
- Deliverables: exports (STEP assembly + closed STL), generated BOM, fasteners.csv
  (4 M10 wedge anchors, 8 M12 A4-70 at the top-head service joint; study patterns),
  check.json, WORK_ORDER.md (W1-W12), and the seven-sheet drawing set (stale
  envelope GA.md superseded). `cad/stl/MET_HX_Q4.stl` replaced from the build.
  `python3 models/mfg/tracker.py --check MET_HX_Q4` green.
- Sheet repair in the lane: ga_front and nozzle_orient never had PDFs because their
  notes bands carried a raw `<` (from "heat < 80 C"), which made the SVGs
  not-well-formed XML. The defect is in the shared `lib/sheets.add_notes` (note text
  injected unescaped); it now XML-escapes the band text, the two sheets were
  regenerated through the sanctioned draw/stamp/PDF sequence, and all seven sheets
  parse and carry PDFs. The same raw-token class (`P&ID`, `heat < 80 C`) also breaks
  139 other units' style_builders-era sheets repo-wide (M2-era, pre-existing, with
  missing ga_front/ga_side/iso01 PDFs); reported here, out of this lane's scope.
- Duty sheet section 4 still carries the unit-task-04 placeholder "Size
  600 × 400 × 600 mm" against the node registry envelope 1000 × 600 × 800 the build
  fills; the sheet line is generator-authored and is not rewritten in the update
  path, the node governs, and the line-list origins sidecar reads the sheet line -
  reported in WORK_ORDER W12, nothing hand-edited, nothing resized.
- Build note: the interrupted overnight session's full regen had left the receipt at
  `converged: false` (`doc-convergence`) with the drawing PDF pass unfinished. This
  commit carries the completed regen (all doc layers refreshed, drawing PDFs
  exported). Operational note for the lane: `models/mfg/tracker.py` takes the design
  lock itself for its write phase - wrapping it (or a regen whose tracker stage runs
  inside) in a second `flock` deadlocks the stage; run both bare, as the tracker
  header states.



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

## CATCH_TANK (pumped-hydro catch tank, tier 4) — commit 9

- `models/mfg/CATCH_TANK/catch_tank.py` on the shared lib. Vertical PVC-U tank
  (shell OD 460, wall 10 per the study fab page - hold) on a plinth with heads,
  filling the node registry envelope 649 × 520 × 748 exactly; one closed manifold
  solid. Internals per the AQS-MFG-001 study page (`docs-authority/fab/
  CATCH_TANK.md`): dip pipe OD 60 inside a stilling well OD 110, concentric, feed
  down the dip pipe and the well damping the inlet jet for the level instruments
  (dims study, holds; node internals row none).
- All 6 schedule rows drawn at tag, face, height and bore as atmospheric hose
  barbs; N5 drain boss to its 50 datum; N6 vent flush at the top head (its 800
  datum predates the 748 box - hold). Duty sheet section 4 still carries the
  unit-task-04 reservoir line 12000 × 8000 × 4000 against the node box, and the
  fab study page a generic 1000 × 600 × 800: the node governs, both named (W12).
  PVC-U-or-HDPE conditional held (duty section 3 rule M1). Holdup 0.0893 m3
  reported, no residence derived (A-VES; the duty two-minute figure is not a
  designed volume).
- Deliverables: exports (STEP + closed STL), generated BOM, fasteners.csv,
  check.json, WORK_ORDER.md (W1-W12), the seven-sheet drawing set (stale
  style_builders-era GA.md and the three invalid-XML M2-era SVGs regenerated
  through the draw/stamp/PDF sequence). `cad/stl/CATCH_TANK.stl` replaced from
  the build. `tracker --check CATCH_TANK` green.
