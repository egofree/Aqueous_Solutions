# Build log - BSFL_BIN

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BSFL_BIN.md`; envelope per `models/mfg/BSFL_BIN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BSFL_BIN/bsfl_bin.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) fills the node box exactly: measured 2500.0 x 900.0 x 700.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/BSFL_BIN.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The size_basis machine is drawn: centre divider (the "2 x 5 kg/d-class bins in one frame" split, even split study choice), one PP self-harvest ramp per bin (duty section 3; foot laps 2 mm into the floor, top laps 1 mm into the wall - the volumetric-overlap idiom that keeps the export manifold), SS316 mesh top screens whose open area is the ventilation path (mesh mass ~0.15 of the drawn plate solid)
- Substrate not drawn: no depth is named on the node - larvae and substrate are process inventory, not BOM parts (the STOCK_OUT idiom; hold, W12)
- Route-class hold named: `bsfl_bin` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 12 rows of `docs-authority/nozzles/BSFL_BIN.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces; N9 vent drawn at the envelope top (schedule z 800 predates the 700 box, stale datum, hold W12); atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/BSFL_BIN/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the SS316 screens are the buy rows); `fasteners.csv` completed (screen clamps A4-70 polymer supplier rule, base anchors 8.8 CS per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/BSFL_BIN/bsfl_bin.py`
- `models/mfg/BSFL_BIN/export/bsfl_bin.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
