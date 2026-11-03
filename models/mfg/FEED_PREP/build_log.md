# Build log - FEED_PREP

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; A-MACH practice on the purchased drives; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FEED_PREP.md`; envelope per `models/mfg/FEED_PREP/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/FEED_PREP/feed_prep.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 cabinet at the node box: measured 1300.0 x 900.0 x 1700.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/FEED_PREP.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The size_basis machine is drawn: mixer trough and HP drier stack (the Oct-31 hollow-box housings, confirmed) plus the grinder housing the size_basis names (SS304 hollow box between them; study layout, hold W12). The drives are the purchased items - named with the node rating (0.6 kW duty class, A-M-426; drier on the storage draw only) and drawn as their housings per plan rule 6 (A-MACH practice)
- Route-class hold named: `feed_prep` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 13 rows of `docs-authority/nozzles/FEED_PREP.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces; N10 vent drawn at the envelope top (schedule z 800 predates the 1700 box, stale datum, hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/FEED_PREP/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the drive set and drier unit are the buy rows with the node rating); `fasteners.csv` completed (base anchors 8.8 CS, drive-plate bolts A4-70 per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/FEED_PREP/feed_prep.py`
- `models/mfg/FEED_PREP/export/feed_prep.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; A-MACH practice recorded on the purchased drives; route-class hold named in WORK_ORDER W12.
