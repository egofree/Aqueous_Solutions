# Build log - BIOFILTER

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named (carried); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BIOFILTER.md`; envelope per `models/mfg/BIOFILTER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BIOFILTER/biofilter.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) fills the node box exactly: measured 1100.0 x 900.0 x 1000.0 mm, flush on all six faces. The Oct-31 section-7-reported overshoot (bbox z 1012.1) does not survive the flush rebuild - the stale report CLEARS from section 7, nothing resized. `cad/stl/BIOFILTER.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- Media internal drawn: the node size_basis names "K1 media 0.2 m3" - the moving-bed carrier envelope is drawn as a solid at 0.2 m3 over the vessel floor (214.8 mm); the charge is a buy row (plan rule 6); the 0.55 m3 moving-bed volume stays a duty figure, not a model claim. The Oct-31 `stubs_mm` pair (two +X studs at z 20, not schedule rows) is superseded by the drawn schedule rows and leaves the params file
- Route-class hold named (carried from the Oct-31 wave): `biofilter` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 12 rows of `docs-authority/nozzles/BIOFILTER.csv` drawn at tag, face, height and bore as DN15/DN50 HDPE tube stubs flush at the envelope faces; N8 vent drawn at the envelope top (schedule z 1200 predates the 1000 box, stale datum, hold W12); atmospheric joints, no flange (W4 110 percent rule); schedule rating column carried verbatim
- Duty section 7 repair: the sheet's "The unit is retired from the graph" sentence predates the node's return to `present`; the line is brought back to the generator's present-unit wording
- BOM `models/mfg/BIOFILTER/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the K1 charge is the buy row); `fasteners.csv` completed (lid hold-downs A4-70 polymer supplier rule, base anchors 8.8 CS per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/BIOFILTER/biofilter.py`
- `models/mfg/BIOFILTER/export/biofilter.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; the section-7 overshoot report cleared on the flush rebuild; route-class hold named (carried) in WORK_ORDER W12.
